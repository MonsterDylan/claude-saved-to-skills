#!/usr/bin/env python3
"""scoreboard.py - rank techniques by evidence, not by how good they sound.

Input (all inside the workspace folder):
  metrics.json          from metrics.py
  reels/*/card.json     one teardown card per reel
  moves.json            the cluster map you wrote after reading every card:
    {"moves": [{"id": "number-hook", "type": "hook",
                "name": "Open on a number that proves demand",
                "how": "one or two sentences on doing it well",
                "reels": ["Dd9DCEZh3In", "..."],
                "best_example": "Dd9DCEZh3In"}],
     "segments": {"share": ["shortcodes of skits, memes, pure showcases"]}}

  "segments" is optional. Reels not listed fall in the default segment, "teach".
  Use it when a collection mixes kinds of reel that are not comparable. A 13
  second meme and a 60 second tutorial play different games, and without
  segments every tutorial technique looks like a loser next to the memes.

Output:
  scoreboard.json and scoreboard.md, techniques ranked by:
    1. creators   how many separate creators use it (independent confirmation)
    2. lift       how far reels using it sit above or below the median of
                  their own segment (median of score minus segment median)
    3. top        the best-performing reel that uses it

Verdicts (MARGIN is 8 points):
  lift          3+ creators, and reels using it sit 8+ points above their segment
  table-stakes  3+ creators, no clear difference either way
  drag          3+ creators, and reels using it sit 8+ points below
  promising     under 3 creators but 8+ points above; unproven
  anecdote      everything else
  common        (only when there is no metrics.json) 3+ creators use it; no lift is known

Usage: python3 scoreboard.py <workspace>
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path


MARGIN = 8  # points of score, on a 0 to 100 scale


def fmt(n):
    if n is None:
        return "n/a"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)


def load_metrics(ws: Path, cards: dict) -> tuple[dict, bool]:
    """Numbers per reel. Without metrics.json (no Apify token) fall back to the cards,
    so the run still works: techniques are then ranked by creator count only."""
    f = ws / "metrics.json"
    if f.exists():
        return {r["shortcode"]: r for r in json.loads(f.read_text())["reels"]}, True
    return {c: {"shortcode": c, "creator": (card.get("creator") or "").lstrip("@"),
                "url": card.get("url") or f"https://www.instagram.com/reel/{c}/",
                "plays": None, "score": None, "reach_x": None}
            for c, card in cards.items()}, False


def main() -> None:
    ws = Path(sys.argv[1])
    cards = {}
    for p in sorted((ws / "reels").glob("*/card.json")):
        try:
            cards[p.parent.name] = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            print(f"[scoreboard] bad card {p}: {e}", file=sys.stderr)
    metrics, has_numbers = load_metrics(ws, cards)
    spec = json.loads((ws / "moves.json").read_text())
    moves = spec["moves"]
    seg_of = {c: seg for seg, codes in (spec.get("segments") or {}).items() for c in codes}

    scored = [m["score"] for c, m in metrics.items() if c in cards and m.get("score") is not None]
    base = statistics.median(scored) if scored else 0
    by_seg: dict[str, list] = {}
    for c, m in metrics.items():
        if c in cards and m.get("score") is not None:
            by_seg.setdefault(seg_of.get(c, "teach"), []).append(m["score"])
    seg_median = {seg: statistics.median(v) for seg, v in by_seg.items()}
    rows = []
    for mv in moves:
        reels = [c for c in dict.fromkeys(mv.get("reels", [])) if c in metrics]
        if not reels:
            continue
        ms = [metrics[c] for c in reels]
        scores = [m["score"] for m in ms if m.get("score") is not None]
        adjusted = [m["score"] - seg_median[seg_of.get(m["shortcode"], "teach")]
                    for m in ms if m.get("score") is not None]
        top = max(ms, key=lambda m: m.get("plays") or 0)
        creators = sorted({m["creator"] for m in ms if m.get("creator")})
        med = statistics.median(scores) if scores else None
        lift = round(statistics.median(adjusted), 1) if adjusted else None
        segs = sorted({seg_of.get(c, "teach") for c in reels})
        rows.append({
            "id": mv["id"], "type": mv.get("type"), "name": mv["name"], "how": mv.get("how", ""),
            "reels": reels, "n_reels": len(reels), "creators": creators, "n_creators": len(creators),
            "median_score": med, "lift": lift, "segments": segs,
            "share_of_collection": round(100 * len(reels) / max(1, len(cards))),
            "top_reel": {"shortcode": top["shortcode"], "creator": top["creator"], "plays": top["plays"],
                         "url": top["url"]},
            "best_example": mv.get("best_example") or top["shortcode"],
            # keep = confirmed by 3+ creators and not below the collection median
            # With a handful of reels per technique, a few points of lift is noise.
            # Only call it a lift or a drag when it clears a real margin.
            "verdict": (("common" if len(creators) >= 3 else "anecdote") if not has_numbers
                        else "lift" if len(creators) >= 3 and (lift or 0) >= MARGIN
                        else "drag" if len(creators) >= 3 and (lift or 0) <= -MARGIN
                        else "table-stakes" if len(creators) >= 3
                        else "promising" if (lift or 0) >= MARGIN
                        else "anecdote"),
        })
    rows.sort(key=lambda r: (-r["n_creators"], -(r["lift"] or -999)))

    out = {"collection_reels": len(cards), "collection_median_score": base,
           "segment_medians": seg_median, "segment_sizes": {k: len(v) for k, v in by_seg.items()},
           "moves": rows}
    (ws / "scoreboard.json").write_text(json.dumps(out, indent=1))

    lines = [f"# Scoreboard", "",
             f"{len(cards)} reels watched. Collection median score: {base:.0f}. Segments: "
             + ", ".join(f"{k} ({len(v)} reels, median {seg_median[k]:.0f})" for k, v in by_seg.items()) + ".",
             "",
             "Lift = how far the reels using a technique sit above or below the median of their own segment. "
             "It is a correlation inside a hand-picked collection, not proof of cause.", ""]
    if not has_numbers:
        lines[2:] = [f"{len(cards)} reels watched. No metrics.json was found, so there are no view counts and "
                     "no lift. Techniques are ranked only by how many separate creators use them. "
                     "Add an APIFY_TOKEN and run metrics.py to get a real ranking.", ""]
    for kind in ("hook", "structure", "edit", "cta", "trust", "teaching"):
        sub = [r for r in rows if r["type"] == kind]
        if not sub:
            continue
        lines += [f"## {kind.title()}", "",
                  "| Technique | Creators | Reels | Lift | Seen in | Top reel | Verdict |", "|---|---|---|---|---|---|---|"]
        for r in sub:
            t = r["top_reel"]
            lift = f"{r['lift']:+.0f}" if r["lift"] is not None else "n/a"
            lines.append(f"| {r['name']} | {r['n_creators']} | {r['n_reels']} | {lift} | {'+'.join(r['segments'])} | "
                         f"[@{t['creator']} {fmt(t['plays'])}]({t['url']}) | {r['verdict']} |")
        lines.append("")
    (ws / "scoreboard.md").write_text("\n".join(lines))
    tally = {v: sum(r["verdict"] == v for r in rows)
             for v in ("lift", "table-stakes", "drag", "promising", "common", "anecdote")}
    tally = {v: n for v, n in tally.items() if n}
    print(f"[scoreboard] {len(rows)} techniques ranked: " + ", ".join(f"{n} {v}" for v, n in tally.items())
          + f" -> {ws/'scoreboard.md'}")


if __name__ == "__main__":
    main()
