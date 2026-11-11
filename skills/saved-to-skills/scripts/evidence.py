#!/usr/bin/env python3
"""evidence.py - write the evidence file for one skill from the scoreboard.

A skill's rules are only as good as the evidence behind them, and that evidence
should travel with the skill. This pulls the chosen scoreboard rows into a
markdown table with every source reel linked.

Usage: python3 evidence.py <workspace> <out.md> <move-id> [<move-id> ...]
       python3 evidence.py <workspace> <out.md> --types hook,cta
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    ws, out = Path(sys.argv[1]), Path(sys.argv[2])
    sb = json.loads((ws / "scoreboard.json").read_text())
    mfile = ws / "metrics.json"
    if mfile.exists():
        metrics = {r["shortcode"]: r for r in json.loads(mfile.read_text())["reels"]}
    else:  # no Apify run: take the creator and link from the teardown cards
        metrics = {}
        for card_file in (ws / "reels").glob("*/card.json"):
            card = json.loads(card_file.read_text())
            code = card_file.parent.name
            metrics[code] = {"url": card.get("url") or f"https://www.instagram.com/reel/{code}/",
                             "creator": (card.get("creator") or "unknown").lstrip("@")}
    args = sys.argv[3:]
    if args and args[0] == "--types":
        want = set(args[1].split(","))
        rows = [r for r in sb["moves"] if r["type"] in want]
    else:
        rows = [r for i in args for r in sb["moves"] if r["id"] == i]
    order = {"lift": 0, "promising": 1, "table-stakes": 2, "drag": 3, "anecdote": 4}
    rows.sort(key=lambda r: (order.get(r["verdict"], 9), -(r["lift"] or 0)))
    seg = ", ".join(f"{k}: {n} reels, median {sb['segment_medians'][k]:.0f}" for k, n in sb["segment_sizes"].items())
    lines = ["# Evidence", "",
             f"From {sb['collection_reels']} reels ({seg}). Score is 0 to 100 inside this collection, blending reach "
             "past the creator's own followers, save and share rate, and raw plays. Lift is points above or below "
             "the median of comparable reels. This is correlation inside a hand-picked collection, not proof.", ""]
    for r in rows:
        lift = f"{r['lift']:+.0f}" if r["lift"] is not None else "n/a"
        lines += [f"## {r['name']}", "",
                  f"`{r['id']}` · {r['type']} · **{r['verdict']}** · lift {lift} · "
                  f"{r['n_creators']} creators, {r['n_reels']} reels", "", r["how"], ""]
        for c in sorted(r["reels"], key=lambda c: -(metrics.get(c, {}).get("score") or 0)):
            m = metrics.get(c) or {"url": f"https://www.instagram.com/reel/{c}/", "creator": "unknown"}
            plays = f"{m['plays']:,}" if m.get("plays") else "n/a"
            lines.append(f"- [{c}]({m['url']}) @{m['creator']} · score {m.get('score')} · {plays} plays · "
                         f"reach {m.get('reach_x')}x" if m.get("plays") else f"- [{c}]({m['url']}) @{m['creator']}")
        lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print(f"{len(rows)} techniques -> {out}")


if __name__ == "__main__":
    main()
