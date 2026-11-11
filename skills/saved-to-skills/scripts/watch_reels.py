#!/usr/bin/env python3
"""watch_reels.py - turn each saved reel into something a model can actually watch.

For every reel it writes a small folder:
  sheets/sheet_00.jpg ...  contact sheets, 1 frame per second, 20 frames per sheet
                           (5 columns x 4 rows, read left to right, top to bottom;
                           sheet N covers seconds N*20 to N*20+19)
  transcript.txt           timestamped speech
  transcript.json          the same, as segments
  cuts.json                hard-cut timestamps, cuts per 10s, average shot length
  media.json               duration, size, where each piece came from
  meta.json                creator, caption and numbers for this reel (from metrics.json)
  graphics/                only with --graphics: burst strips (8 frames across ~1.4s) at each
                           moment something arrives on screen, plus events.json listing them

Contact sheets are the trick: 4 images cover a 75 second reel completely, so a
model sees every beat of the edit for the token cost of 4 pictures.

Usage:
  python3 watch_reels.py <metrics.json | links.txt> <out-dir> [--workers 4]
                         [--only SHORTCODE ...] [--keep-video] [--no-whisper] [--graphics [N]]

Needs ffmpeg, ffprobe, yt-dlp on PATH and GROQ_API_KEY or OPENAI_API_KEY for
speech. The video file is deleted after processing unless --keep-video is set.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _env import get_key, shortcode_of  # noqa: E402

SHEET_SECONDS = 20
# Speech APIs rate-limit hard. Downloads and frame work can fan out wide, but
# only two transcriptions run at once, and a 429 backs off and retries.
WHISPER_GATE = threading.Semaphore(2)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) saved-to-skills/1.0"


def sh(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def download(url: str, video_url: str | None, dest: Path) -> str:
    """Try the public page with yt-dlp, fall back to the direct CDN url."""
    r = sh(["yt-dlp", "-q", "--no-warnings", "--no-playlist",
            "-f", "bv*[height<=960]+ba/b[height<=960]/b",
            "--merge-output-format", "mp4", "-o", str(dest), url])
    if r.returncode == 0 and dest.exists() and dest.stat().st_size > 10_000:
        return "yt-dlp"
    if video_url:
        req = urllib.request.Request(video_url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
            shutil.copyfileobj(resp, f)
        if dest.stat().st_size > 10_000:
            return "direct"
    raise RuntimeError((r.stderr or "download failed").strip().splitlines()[-1][:200])


def duration_of(video: Path) -> float:
    r = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=nk=1:nw=1", str(video)])
    return float(r.stdout.strip() or 0)


def make_sheets(video: Path, out: Path, dur: float) -> int:
    out.mkdir(parents=True, exist_ok=True)
    n = max(1, math.ceil(dur / SHEET_SECONDS))
    for i in range(n):
        sh(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(i * SHEET_SECONDS),
            "-t", str(SHEET_SECONDS), "-i", str(video),
            "-vf", "fps=1,scale=300:-2,tile=5x4:padding=6:color=white",
            "-frames:v", "1", "-q:v", "4", str(out / f"sheet_{i:02d}.jpg")])
    return len(list(out.glob("sheet_*.jpg")))


def find_cuts(video: Path, dur: float) -> dict:
    r = sh(["ffmpeg", "-hide_banner", "-i", str(video), "-an",
            "-vf", "select='gt(scene,0.30)',showinfo", "-f", "null", "-"])
    times = sorted({round(float(t), 2) for t in re.findall(r"pts_time:([0-9.]+)", r.stderr)})
    buckets = [0] * max(1, math.ceil(dur / 10))
    for t in times:
        buckets[min(int(t // 10), len(buckets) - 1)] += 1
    return {
        "cut_count": len(times),
        "cut_timestamps": times,
        "cuts_per_10s": buckets,
        "avg_shot_seconds": round(dur / (len(times) + 1), 2) if dur else None,
        "note": "Hard cuts only (scene change > 0.30). Graphic pop-ins inside a shot are not counted; "
                "read those off the contact sheets.",
    }


def transcribe(video: Path, work: Path) -> dict:
    groq, openai = get_key("GROQ_API_KEY"), get_key("OPENAI_API_KEY")
    if not (groq or openai):
        return {"source": "none (no GROQ_API_KEY or OPENAI_API_KEY)", "segments": []}
    audio = work / "audio.mp3"
    sh(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-vn", "-ac", "1",
        "-ar", "16000", "-b:a", "48k", str(audio)])
    if not audio.exists() or audio.stat().st_size < 2000:
        return {"source": "none (no audio track)", "segments": []}
    if groq:
        url, key, model, src = ("https://api.groq.com/openai/v1/audio/transcriptions", groq,
                                "whisper-large-v3", "whisper (groq)")
    else:
        url, key, model, src = ("https://api.openai.com/v1/audio/transcriptions", openai,
                                "whisper-1", "whisper (openai)")
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in (("model", model), ("response_format", "verbose_json")):
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="audio.mp3"\r\n'
                 f"Content-Type: audio/mpeg\r\n\r\n".encode() + audio.read_bytes() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(url, data=b"".join(parts), method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("User-Agent", UA)
    data, err = None, None
    try:
        for attempt in range(6):
            try:
                with WHISPER_GATE, urllib.request.urlopen(req, timeout=180) as r:
                    data = json.loads(r.read().decode())
                break
            except urllib.error.HTTPError as e:
                err = e
                if e.code not in (429, 500, 502, 503):
                    break
                wait = float(e.headers.get("Retry-After") or 0) or min(60, 6 * 2 ** attempt)
                time.sleep(wait)
            except Exception as e:  # noqa: BLE001 - a failed transcript should not kill the batch
                err = e
                break
    finally:
        audio.unlink(missing_ok=True)
    if data is None:
        return {"source": f"failed ({type(err).__name__}: {str(err)[:120]})", "segments": []}
    segs = [{"start": round(s.get("start", 0), 2), "end": round(s.get("end", 0), 2),
             "text": s.get("text", "").strip()} for s in data.get("segments", [])]
    return {"source": src, "text": data.get("text", "").strip(), "segments": segs}


META_KEYS = ["shortcode", "url", "creator", "creator_name", "followers", "posted", "age_days",
             "still_climbing", "plays", "likes", "comments", "shares", "saves", "save_rate",
             "share_rate", "comment_rate", "reach_x", "score", "caption"]


def write_meta(reel: dict, out: Path, dur: float | None = None) -> None:
    """One small file per reel with its creator, caption and numbers.

    Whoever writes the teardown card reads this instead of the whole metrics file.
    """
    meta = {k: reel.get(k) for k in META_KEYS}
    if dur:
        meta["duration_s"] = round(dur, 1)
    (out / "meta.json").write_text(json.dumps(meta, indent=1))


BURST_FPS = 5          # frames per second inside a burst strip
BURST_FRAMES = 8       # 4 columns x 2 rows
BURST_LEAD = 0.3       # start this long before the change, so the "before" state is visible
CUT_SCORE = 0.30       # a change this large is a hard cut, not a graphic arriving


def change_scores(video: Path) -> list[tuple[float, float]]:
    """How much the picture changed at each tenth of a second, 0 to 1.

    A talking head sits around 0.005. A card popping in is 0.03 to 0.15. A hard
    cut is 0.3 and up. Sampling at 10 fps on a tiny copy keeps this fast.
    """
    r = sh(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video), "-an", "-vf",
            "fps=10,scale=160:-2,select='gte(scene,0)',metadata=print:file=-", "-f", "null", "-"], timeout=600)
    rows, t = [], None
    for line in r.stdout.splitlines():
        m = re.search(r"pts_time:([0-9.]+)", line)
        if m:
            t = float(m.group(1))
        m = re.search(r"scene_score=([0-9.]+)", line)
        if m and t is not None:
            rows.append((t, float(m.group(1))))
    return rows


def pick_events(rows: list[tuple[float, float]], limit: int) -> tuple[list[dict], float]:
    """Find the moments something new arrives on screen.

    The bar adapts to the reel: 5x its own median change, never below 0.03. That
    way a shaky handheld reel does not flag every frame, and a locked-off one
    still catches a small label fading in.
    """
    if not rows:
        return [], 0.0
    scores = sorted(s for _, s in rows)
    bar = max(0.03, 5 * scores[len(scores) // 2])
    events, cur = [], None
    for t, sc in rows:
        if sc >= bar:
            if cur and t - cur["last"] <= 0.5:
                cur["last"], cur["score"] = t, max(cur["score"], sc)
            else:
                cur = {"t": t, "last": t, "score": sc}
                events.append(cur)
    if len(events) > limit:
        # Too many. Two things matter more than raw size: cover the whole reel, and
        # prefer something arriving inside a shot over a hard cut. Cuts score highest,
        # so picking by size alone keeps only cuts and loses the subtle graphics.
        span = (rows[-1][0] or 1) / limit
        best: dict[int, dict] = {}
        for e in events:
            slot = min(int(e["t"] / span), limit - 1)
            rank = (e["score"] < CUT_SCORE, e["score"])  # in-shot changes first, then by size
            if slot not in best or rank > best[slot]["rank"]:
                best[slot] = {**e, "rank": rank}
        events = [{k: v for k, v in e.items() if k != "rank"} for _, e in sorted(best.items())]
    return events, bar


def graphic_bursts(video: Path, out: Path, limit: int, segments: list[dict]) -> int:
    """Write one burst strip per on-screen change, so the motion can be read.

    The 1 fps contact sheets show what a graphic looks like once it has landed.
    They cannot show how it got there. A burst strip is 8 frames across about
    1.4 seconds around the change: read left to right, top row then bottom row.
    """
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("burst_*.jpg"):  # a redo may find fewer events than last time
        stale.unlink()
    events, bar = pick_events(change_scores(video), limit)
    listed = []
    for i, e in enumerate(events, 1):
        start = max(0.0, e["t"] - BURST_LEAD)
        name = f"burst_{i:02d}.jpg"
        sh(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{start:.2f}", "-t", f"{BURST_FRAMES / BURST_FPS:.2f}",
            "-i", str(video), "-vf", f"fps={BURST_FPS},scale=384:-2,tile=4x2:padding=6:color=white",
            "-frames:v", "1", "-q:v", "3", str(out / name)])
        if not (out / name).exists():
            continue
        end = start + (BURST_FRAMES - 1) / BURST_FPS
        said = " ".join(s["text"] for s in segments if s["end"] >= start - 0.3 and s["start"] <= end + 0.3)
        listed.append({"i": i, "t": round(e["t"], 1), "file": name,
                       "covers": f"{start:.1f}s to {end:.1f}s, one frame every {1 / BURST_FPS:.1f}s",
                       "kind": "cut" if e["score"] >= CUT_SCORE else "change",
                       "change_score": round(e["score"], 3), "said_around_it": said.strip()})
    (out / "events.json").write_text(json.dumps({
        "how_to_read": "Each burst strip is 8 frames, 4 columns by 2 rows, left to right then top to bottom. "
                       "The first frame is just before the change. 'kind: cut' is a hard cut to a new shot; "
                       "'kind: change' is something arriving or leaving inside the shot.",
        "threshold_used": round(bar, 3), "events": listed}, indent=1))
    return len(listed)


def process(reel: dict, out_root: Path, keep_video: bool, no_whisper: bool, graphics: int = 0,
            redo_graphics: bool = False) -> dict:
    code = reel["shortcode"]
    out = out_root / code
    prior = json.loads((out / "media.json").read_text()) if (out / "media.json").exists() else None
    # Work out what is still missing, so a second run only does that part.
    need_speech = prior is None or (not no_whisper
                                    and str(prior.get("transcript_source", "")).startswith("failed"))
    need_graphics = graphics > 0 and (redo_graphics or not (out / "graphics" / "events.json").exists())
    if prior and not need_speech and not need_graphics:
        write_meta(reel, out, prior.get("duration_s"))  # numbers may have been refreshed
        return {"shortcode": code, "status": "cached"}
    out.mkdir(parents=True, exist_ok=True)
    video = out / "video.mp4"
    try:
        how = download(reel["url"], reel.get("video_url"), video)
        dur = duration_of(video)
        if prior:
            sheets = prior["sheets"]
            cuts = json.loads((out / "cuts.json").read_text())
        else:
            sheets = make_sheets(video, out / "sheets", dur)
            cuts = find_cuts(video, dur)
            (out / "cuts.json").write_text(json.dumps(cuts, indent=1))
        if need_speech:
            tr = {"source": "skipped", "segments": []} if no_whisper else transcribe(video, out)
            (out / "transcript.json").write_text(json.dumps(tr, indent=1))
            lines = [f"[{int(s['start'])//60:02d}:{int(s['start'])%60:02d}] {s['text']}" for s in tr["segments"]]
            (out / "transcript.txt").write_text("\n".join(lines) or "(no speech found)")
        else:
            tr = json.loads((out / "transcript.json").read_text())
        media = {"shortcode": code, "url": reel["url"], "duration_s": round(dur, 1),
                 "download": how, "sheets": sheets, "sheet_seconds": SHEET_SECONDS,
                 "cut_count": cuts["cut_count"], "avg_shot_seconds": cuts["avg_shot_seconds"],
                 "transcript_source": tr["source"], "words": len(tr.get("text", "").split())}
        if need_graphics:
            media["graphic_bursts"] = graphic_bursts(video, out / "graphics", graphics, tr.get("segments", []))
        elif prior and "graphic_bursts" in prior:
            media["graphic_bursts"] = prior["graphic_bursts"]
        (out / "media.json").write_text(json.dumps(media, indent=1))
        write_meta(reel, out, dur)
        return {"shortcode": code, "status": "ok", **media}
    except Exception as e:  # noqa: BLE001
        if not prior:
            (out / "error.txt").write_text(str(e))
        return {"shortcode": code, "status": "failed", "error": str(e)[:200]}
    finally:
        if not keep_video:
            video.unlink(missing_ok=True)


def load_reels(src: Path) -> list[dict]:
    if src.suffix == ".json":
        data = json.loads(src.read_text())
        return [r for r in data["reels"] if r.get("is_video", True)]
    reels = []
    for line in src.read_text().splitlines():
        code = shortcode_of(line)
        if code and "/p/" not in line:
            reels.append({"shortcode": code, "url": line.strip()})
    return reels


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="metrics.json from metrics.py, or a links.txt")
    ap.add_argument("out_dir")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", nargs="*", help="only these shortcodes")
    ap.add_argument("--keep-video", action="store_true")
    ap.add_argument("--no-whisper", action="store_true")
    ap.add_argument("--graphics", nargs="?", const=10, type=int, default=0, metavar="N",
                    help="graphics mode: also write up to N burst strips per reel (default 10) "
                         "showing how each on-screen change animates in")
    ap.add_argument("--redo-graphics", action="store_true",
                    help="with --graphics: rebuild the burst strips even if they already exist")
    args = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe", "yt-dlp"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} not found on PATH. Install it first (brew install ffmpeg yt-dlp).")

    reels = load_reels(Path(args.source))
    if args.only:
        reels = [r for r in reels if r["shortcode"] in set(args.only)]
    out_root = Path(args.out_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(process, r, out_root, args.keep_video, args.no_whisper, args.graphics,
                            args.redo_graphics) for r in reels]
        for f in as_completed(futs):
            res = f.result()
            results.append(res)
            print(f"[watch] {res['shortcode']}: {res['status']}"
                  + (f" ({res.get('duration_s')}s, {res.get('cut_count')} cuts"
                     + (f", {res['graphic_bursts']} bursts" if "graphic_bursts" in res else "") + ")"
                     if res["status"] == "ok" else "")
                  + (f" {res.get('error')}" if res["status"] == "failed" else ""), flush=True)
    ok = sum(r["status"] in ("ok", "cached") for r in results)
    (out_root / "_watch_log.json").write_text(json.dumps(results, indent=1))
    no_speech = [r["shortcode"] for r in results
                 if str(r.get("transcript_source", "")).startswith("failed")]
    print(f"[watch] done: {ok}/{len(results)} watched, {len(results)-ok} failed"
          + (f", {len(no_speech)} transcripts failed (run again to retry just those)" if no_speech else ""))


if __name__ == "__main__":
    main()
