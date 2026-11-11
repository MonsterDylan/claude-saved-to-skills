#!/usr/bin/env python3
"""metrics.py - pull the real numbers for every saved reel, then score them.

Why: "keep the version that works" is a guess unless you can see what
performed. This asks Apify for plays, likes, comments, shares, saves and the
creator's follower count for each link, then computes a reach multiple
(plays / followers) and engagement rates so techniques can be ranked by
evidence instead of by how confident the creator sounded.

Usage:
  python3 metrics.py <links.txt> <out-dir> [--actor data-slayer/instagram-post-details]

Needs APIFY_TOKEN (environment, or one of the dotenv files in _env.py).
Cost is about $0.002 per link.

Writes:
  <out-dir>/metrics.raw.json   the untouched actor output
  <out-dir>/metrics.json       one normalized row per link, sorted by score
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _env import get_key, shortcode_of  # noqa: E402

API = "https://api.apify.com/v2"


def _call(method: str, url: str, token: str, body: dict | None = None) -> dict | list:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def run_actor(actor: str, payload: dict, token: str) -> list:
    actor_id = actor.replace("/", "~")
    run = _call("POST", f"{API}/acts/{actor_id}/runs", token, payload)["data"]
    run_id, dataset = run["id"], run["defaultDatasetId"]
    print(f"[metrics] run {run_id} started", file=sys.stderr)
    while True:
        status = _call("GET", f"{API}/actor-runs/{run_id}", token)["data"]["status"]
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
        time.sleep(4)
    if status != "SUCCEEDED":
        raise SystemExit(f"[metrics] actor run ended with status {status}")
    return _call("GET", f"{API}/datasets/{dataset}/items?clean=true&format=json", token)


def dig(obj, *paths, default=None):
    """Return the first non-empty value found at any dotted path."""
    for path in paths:
        cur = obj
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                cur = None
                break
        if cur not in (None, "", [], {}):
            return cur
    return default


def num(v):
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def normalize(item: dict) -> dict:
    code = dig(item, "code", "shortcode", "short_code", "shortCode")
    plays = num(dig(item, "metrics.play_count", "metrics.ig_play_count", "play_count",
                    "metrics.view_count", "videoPlayCount", "video_play_count"))
    likes = num(dig(item, "metrics.like_count", "like_count", "likesCount"))
    comments = num(dig(item, "metrics.comment_count", "comment_count", "commentsCount"))
    shares = num(dig(item, "metrics.share_count", "share_count", "reshare_count"))
    saves = num(dig(item, "metrics.save_count", "save_count"))
    followers = num(dig(item, "metrics.user_follower_count", "user.follower_count",
                        "owner.follower_count", "ownerFollowersCount"))
    row = {
        "shortcode": code,
        "url": f"https://www.instagram.com/reel/{code}/" if code else dig(item, "url", "inputUrl"),
        "creator": dig(item, "user.username", "owner.username", "ownerUsername"),
        "creator_name": dig(item, "user.full_name", "owner.full_name", "ownerFullName"),
        "followers": followers,
        "posted": dig(item, "taken_at_date", "taken_at", "timestamp"),
        "duration_s": dig(item, "video_duration", "videoDuration"),
        "is_video": bool(dig(item, "video_url", "videoUrl", "video_versions")),
        "caption": dig(item, "caption.text", "caption", default=""),
        "video_url": dig(item, "video_url", "videoUrl"),
        "thumbnail_url": dig(item, "thumbnail_url", "displayUrl", "image_versions2.candidates.0.url"),
        "plays": plays, "likes": likes, "comments": comments, "shares": shares, "saves": saves,
    }
    if isinstance(row["caption"], dict):
        row["caption"] = row["caption"].get("text", "")

    def rate(n):
        return round(100 * n / plays, 2) if n is not None and plays else None

    row["like_rate"] = rate(likes)
    row["comment_rate"] = rate(comments)
    row["share_rate"] = rate(shares)
    row["save_rate"] = rate(saves)
    # Reach multiple: how far past the creator's own audience this one travelled.
    row["reach_x"] = round(plays / followers, 2) if plays and followers else None
    row["creator_median_plays"] = None
    row["outlier_x"] = None
    ts = num(dig(item, "taken_at_ts", "taken_at"))
    row["age_days"] = round((time.time() - ts) / 86400, 1) if ts else None
    # A reel under 3 days old has not finished collecting views; treat its score as a floor.
    row["still_climbing"] = bool(row["age_days"] is not None and row["age_days"] < 3)
    return row


def add_creator_context(rows: list[dict], token: str, out: Path, actor: str) -> None:
    """Fill follower counts and each creator's normal view count.

    The post actor does not return followers, so one extra call fetches every
    unique creator's profile. If the profile lists recent posts with view
    counts, their median becomes the creator's baseline, which gives a true
    outlier multiple (this reel / what this creator usually gets).
    """
    names = sorted({r["creator"] for r in rows if r.get("creator")})
    if not names:
        return
    cache = out / "creators.raw.json"
    if cache.exists():
        profiles = json.loads(cache.read_text())
    else:
        profiles = run_actor(actor, {"usernames": names}, token)
        cache.write_text(json.dumps(profiles, indent=1))
    by_name = {}
    for p in profiles:
        if not isinstance(p, dict):
            continue
        views = [num(dig(x, "videoViewCount", "videoPlayCount", "playCount"))
                 for x in (p.get("latestPosts") or []) if isinstance(x, dict)]
        views = [v for v in views if v]
        by_name[(p.get("username") or "").lower()] = {
            "followers": num(dig(p, "followersCount", "followers")),
            "median": int(statistics.median(views)) if len(views) >= 4 else None,
        }
    for r in rows:
        ctx = by_name.get((r.get("creator") or "").lower())
        if not ctx:
            continue
        r["followers"] = r["followers"] or ctx["followers"]
        r["creator_median_plays"] = ctx["median"]
        if r["plays"] and r["followers"]:
            r["reach_x"] = round(r["plays"] / r["followers"], 2)
        if r["plays"] and ctx["median"]:
            r["outlier_x"] = round(r["plays"] / ctx["median"], 2)


def add_scores(rows: list[dict]) -> None:
    """score = percentile inside this collection, blending reach and intent.

    Reach multiple says the algorithm pushed it. Save + share rate says people
    wanted to keep it or pass it on. Percentiles keep one giant account from
    drowning everything else out.
    """
    def pct_rank(key):
        vals = sorted(r[key] for r in rows if r.get(key) is not None)
        out = {}
        for r in rows:
            v = r.get(key)
            if v is None or not vals:
                out[id(r)] = None
            else:
                out[id(r)] = sum(1 for x in vals if x <= v) / len(vals)
        return out

    for r in rows:
        s, sh = r.get("save_rate"), r.get("share_rate")
        r["intent_rate"] = round((s or 0) + (sh or 0), 2) if (s is not None or sh is not None) else None
    reach, intent, raw, outl = (pct_rank("reach_x"), pct_rank("intent_rate"),
                                pct_rank("plays"), pct_rank("outlier_x"))
    for r in rows:
        parts = [p for p in (reach[id(r)], intent[id(r)], raw[id(r)], outl[id(r)]) if p is not None]
        r["score"] = round(100 * statistics.mean(parts)) if parts else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("links")
    ap.add_argument("out_dir")
    ap.add_argument("--actor", default="data-slayer/instagram-post-details")
    ap.add_argument("--profile-actor", default="apify/instagram-profile-scraper")
    ap.add_argument("--no-creators", action="store_true",
                    help="skip the creator profile lookup (no follower counts, no outlier multiple)")
    ap.add_argument("--from-raw", action="store_true",
                    help="skip the Apify call and re-normalize an existing metrics.raw.json")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    links = [l.strip() for l in Path(args.links).read_text().splitlines() if l.strip() and not l.startswith("#")]
    raw_path = out / "metrics.raw.json"

    token = get_key("APIFY_TOKEN")
    if args.from_raw:
        items = json.loads(raw_path.read_text())
    else:
        if not token:
            raise SystemExit("APIFY_TOKEN not found. Add it to ~/.config/saved-to-skills/.env "
                             "or run with --from-raw after exporting metrics another way.")
        items = run_actor(args.actor, {"postUrls": links}, token)
        raw_path.write_text(json.dumps(items, indent=1))

    rows = [normalize(i) for i in items if isinstance(i, dict)]
    rows = [r for r in rows if r["shortcode"]]
    got = {r["shortcode"] for r in rows}
    missing = [l for l in links if shortcode_of(l) not in got]
    if token and not args.no_creators:
        try:
            add_creator_context(rows, token, out, args.profile_actor)
        except Exception as e:  # noqa: BLE001 - scores still work without creator context
            print(f"[metrics] creator lookup failed, continuing without it: {e}", file=sys.stderr)
    add_scores(rows)
    rows.sort(key=lambda r: (r["score"] is None, -(r["score"] or 0)))
    (out / "metrics.json").write_text(json.dumps({"count": len(rows), "missing": missing, "reels": rows}, indent=1))
    print(f"[metrics] {len(rows)} scored, {len(missing)} missing -> {out/'metrics.json'}")
    for r in rows[:5]:
        print(f"  {r['score']:>3}  @{r['creator']}  plays={r['plays']}  reach_x={r['reach_x']}  "
              f"outlier_x={r['outlier_x']}  save%={r['save_rate']}  {r['url']}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"[metrics] HTTP {e.code}: {e.read().decode()[:300]}")
