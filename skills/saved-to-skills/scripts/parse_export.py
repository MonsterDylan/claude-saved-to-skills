#!/usr/bin/env python3
"""parse_export.py - pull saved-collection links out of an Instagram data export.

Instagram's "Download your information" export (JSON format) includes your
saved posts and collections. Meta changes the exact file layout from time to
time, so this does not depend on one schema: it walks every JSON file under a
"saved" folder, picks up each post or reel URL, and labels it with the nearest
collection title it has seen.

NOTE: written against the documented export layout but not yet verified on a
fresh 2026 export. If it finds nothing, open the export's saved/ folder and
check the file names, then pass that file directly.

Usage:
  python3 parse_export.py <export-folder-or-json>              list collections and counts
  python3 parse_export.py <export-folder-or-json> "<name>" out/links.txt
"""
from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

URL = re.compile(r"https?://(?:www\.)?instagram\.com/(?:reel|reels|p|tv)/[A-Za-z0-9_-]+")


def walk(node, state, out):
    if isinstance(node, dict):
        title = node.get("title")
        if isinstance(title, str) and title.strip():
            state["collection"] = title.strip()
        name = node.get("string_map_data", {}).get("Name", {}) if isinstance(node.get("string_map_data"), dict) else {}
        if isinstance(name, dict) and name.get("value") and not name.get("href") and title == "Collection":
            state["collection"] = name["value"]
        for v in node.values():
            walk(v, state, out)
    elif isinstance(node, list):
        for v in node:
            walk(v, state, out)
    elif isinstance(node, str):
        m = URL.search(node)
        if m:
            out.setdefault(state["collection"], OrderedDict())[m.group(0).rstrip("/") + "/"] = True


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = Path(sys.argv[1])
    files = [src] if src.is_file() else sorted(p for p in src.rglob("*.json") if "saved" in str(p).lower())
    if not files:
        raise SystemExit("No saved*.json files found. Was the export requested in JSON format?")
    out: dict[str, OrderedDict] = {}
    for f in files:
        state = {"collection": "All saved" if "collection" not in f.name else "Unsorted"}
        try:
            walk(json.loads(f.read_text()), state, out)
        except (json.JSONDecodeError, OSError) as e:
            print(f"skipped {f}: {e}", file=sys.stderr)
    if len(sys.argv) < 4:
        for name, links in out.items():
            print(f"{len(links):>4}  {name}")
        return
    want, dest = sys.argv[2].lower(), Path(sys.argv[3])
    match = [n for n in out if n.lower() == want] or [n for n in out if want in n.lower()]
    if not match:
        raise SystemExit(f"No collection matching '{sys.argv[2]}'. Run without a name to list them.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(f"# Collection: {match[0]} (from Instagram export)\n" + "\n".join(out[match[0]]) + "\n")
    print(f"{len(out[match[0]])} links -> {dest}")


if __name__ == "__main__":
    main()
