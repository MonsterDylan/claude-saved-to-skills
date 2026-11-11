"""Tiny shared helpers: find API keys without making the user export anything.

Keys are looked up in the process environment first, then in a few dotenv
files. Each key is only ever sent to its own provider.
"""
from __future__ import annotations

import os
from pathlib import Path

ENV_FILES = [
    Path.home() / ".config" / "saved-to-skills" / ".env",
    Path.home() / ".config" / "watch" / ".env",
    Path.home() / ".claude" / ".env",
    Path.cwd() / ".env",
]


def get_key(name: str) -> str | None:
    val = os.environ.get(name)
    if val:
        return val.strip()
    for f in ENV_FILES:
        try:
            for line in f.read_text().splitlines():
                line = line.strip()
                if line.startswith(f"{name}="):
                    v = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
        except OSError:
            continue
    return None


def shortcode_of(url: str) -> str | None:
    import re

    m = re.search(r"/(?:reel|reels|p|tv)/([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None
