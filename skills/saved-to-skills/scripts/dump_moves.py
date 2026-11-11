#!/usr/bin/env python3
"""dump_moves.py - print every card's moves in one compact list for clustering.

Reading 60 card.json files one at a time to cluster their moves burns context
on fields the clustering step does not need. This prints only what it does
need, grouped by move type, with each reel's score beside it.

Usage: python3 dump_moves.py <workspace> [--type hook|structure|edit|cta|teaching|trust]
       python3 dump_moves.py <workspace> --overview    one line per reel instead
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    ws = Path(sys.argv[1])
    only = sys.argv[sys.argv.index("--type") + 1] if "--type" in sys.argv else None
    mfile = ws / "metrics.json"
    metrics = {r["shortcode"]: r for r in json.loads(mfile.read_text())["reels"]} if mfile.exists() else {}
    cards = []
    for p in sorted((ws / "reels").glob("*/card.json")):
        try:
            cards.append(json.loads(p.read_text()))
        except json.JSONDecodeError as e:
            print(f"BAD CARD {p}: {e}", file=sys.stderr)

    if "--overview" in sys.argv:
        for c in sorted(cards, key=lambda c: -(metrics.get(c.get("shortcode"), {}).get("score") or 0)):
            m = metrics.get(c.get("shortcode"), {})
            hook = (c.get("does") or {}).get("hook") or {}
            cta = (c.get("does") or {}).get("cta") or {}
            print(f"{m.get('score')!s:>3} {c.get('shortcode')} @{c.get('creator')} "
                  f"plays={m.get('plays')} reach_x={m.get('reach_x')} len={c.get('length_s')}s "
                  f"| {c.get('format')} | hook:{hook.get('type')} | cta:{cta.get('type')}/{cta.get('keyword')} "
                  f"| {c.get('topic')}")
        return

    by_type: dict[str, list[str]] = {}
    for c in cards:
        code = c.get("shortcode")
        score = metrics.get(code, {}).get("score")
        for mv in c.get("moves") or []:
            t = (mv.get("type") or "other").split("|")[0].strip()
            if only and t != only:
                continue
            by_type.setdefault(t, []).append(f"{code} s{score} | {mv.get('move')}  [{mv.get('evidence')}]")
    for t, rows in by_type.items():
        print(f"\n## {t} ({len(rows)})")
        print("\n".join(rows))
    print(f"\n{len(cards)} cards, {sum(len(v) for v in by_type.values())} moves", file=sys.stderr)


if __name__ == "__main__":
    main()
