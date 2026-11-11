#!/usr/bin/env python3
"""effects_catalog.py - turn graphics cards into a catalog of effects worth building.

Input (inside the workspace folder):
  effects.json                  the cluster map written after reading every graphics card
                                (shape is in references/graphics-mode.md)
  reels/*/graphics.json         the graphics cards, for creator names
  metrics.json                  optional; adds how the reels using each effect performed

Output:
  effects-catalog.md and effects-catalog.json. Effects the person does not have yet
  come first, then the ones they already have, each with its build spec and links
  to the burst strips that show it moving.
  style-sheets.md: one style sheet per creator, from the "system" block of each card.

Usage: python3 effects_catalog.py <workspace>
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path


def main() -> None:
    ws = Path(sys.argv[1])
    spec = json.loads((ws / "effects.json").read_text())
    cards = {}
    for p in sorted((ws / "reels").glob("*/graphics.json")):
        try:
            cards[p.parent.name] = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            print(f"[catalog] bad card {p}: {e}", file=sys.stderr)
    mfile = ws / "metrics.json"
    metrics = {r["shortcode"]: r for r in json.loads(mfile.read_text())["reels"]} if mfile.exists() else {}
    scored = [m["score"] for c, m in metrics.items() if c in cards and m.get("score") is not None]
    # Under 15 scored reels a median means nothing, so no lift is shown.
    base = statistics.median(scored) if len(scored) >= 15 else None

    def creator(code: str) -> str:
        return ((metrics.get(code) or {}).get("creator") or (cards.get(code) or {}).get("creator") or "unknown").lstrip("@")

    rows = []
    for fx in spec["effects"]:
        examples = [e for e in fx.get("examples", []) if e.get("reel")]
        reels = list(dict.fromkeys(e["reel"] for e in examples))
        creators = sorted({creator(c) for c in reels})
        scores = [metrics[c]["score"] for c in reels if c in metrics and metrics[c].get("score") is not None]
        lift = round(statistics.median(scores) - base, 1) if scores and base is not None else None
        rows.append({**fx, "examples": examples, "n_reels": len(reels), "creators": creators,
                     "n_creators": len(creators), "lift": lift,
                     "new": not str(fx.get("have_already", "")).strip()})
    rows.sort(key=lambda r: (not r["new"], -r["n_creators"], -(r["lift"] or -999)))
    (ws / "effects-catalog.json").write_text(json.dumps({"reels": len(cards), "effects": rows}, indent=1))

    lines = ["# Effects catalog", "",
             f"{len(rows)} effects from {len(cards)} reels. "
             + ("Lift is how reels using the effect scored against the rest of this collection. "
                "It is correlation in a small set, not proof." if base is not None
                else "No performance ranking: too few reels with metrics."), "",
             "Rebuild the technique in your own palette and type. Do not copy anyone's artwork.", ""]

    def block(r: dict) -> list[str]:
        head = f"### {r['name']}"
        meta = [r.get("kind", "effect"), f"{r['n_creators']} creator" + ("s" if r["n_creators"] != 1 else "")]
        if r["lift"] is not None:
            meta.append(f"lift {r['lift']:+.0f}")
        if not r["new"]:
            meta.append(f"you have: {r['have_already']}")
        elif r.get("closest"):
            meta.append(f"closest you have: {r['closest']}")
        out = [head, "", " · ".join(meta), ""]
        for label, key in (("What", "what"), ("How it moves", "moves"), ("Build", "build"),
                           ("Use it for", "use_for"), ("Watch out", "caution")):
            if r.get(key):
                out.append(f"- **{label}:** {r[key]}")
        if r["examples"]:
            out.append("- **See it:** " + ", ".join(
                f"[@{creator(e['reel'])} at {float(e.get('t', 0)):.0f}s](reels/{e['reel']}/graphics/{e['burst']})"
                if e.get("burst") else f"@{creator(e['reel'])} at {float(e.get('t', 0)):.0f}s"
                for e in r["examples"]))
        return out + [""]

    new = [r for r in rows if r["new"]]
    have = [r for r in rows if not r["new"]]
    if new:
        lines += ["## New to you", ""] if have else ["## Effects", ""]
        for r in new:
            lines += block(r)
    if have:
        lines += ["## You already have these", ""]
        for r in have:
            lines += block(r)
    (ws / "effects-catalog.md").write_text("\n".join(lines))

    # One style sheet per creator, straight from the "system" block of each card.
    sheets = ["# Style sheets", "",
              "How each creator's videos are put together. Use these for the discipline (zones, rhythm, "
              "restraint), and build in your own palette and type.", ""]
    labels = [("canvas", "Canvas"), ("zones", "Zones"), ("type", "Type"), ("captions", "Captions"),
              ("rhythm", "Rhythm"), ("default_transition", "Default transition"), ("restraint", "Restraint")]
    for code, card in cards.items():
        system = card.get("system") or {}
        sheets += [f"## @{creator(code)}", "", f"[{code}]({card.get('url') or 'https://www.instagram.com/reel/' + code + '/'})", ""]
        for key, label in labels:
            if system.get(key):
                sheets.append(f"- **{label}:** {system[key]}")
        palette = system.get("palette") or []
        if palette:
            sheets.append("- **Palette, by role:** " + "; ".join(
                f"{c.get('role')}: {c.get('color')}" if isinstance(c, dict) else str(c) for c in palette))
        if card.get("do_not_copy"):
            sheets.append("- **Theirs, do not copy:** " + "; ".join(card["do_not_copy"]))
        sheets.append("")
    (ws / "style-sheets.md").write_text("\n".join(sheets))
    print(f"[catalog] {len(rows)} effects ({len(new)} new, {len(have)} already owned) -> {ws/'effects-catalog.md'}")


if __name__ == "__main__":
    main()
