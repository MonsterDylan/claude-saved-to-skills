#!/bin/sh
# zips the skill folder (the zip holds the folder, SKILL.md inside it)
cd "$(dirname "$0")/.."
mkdir -p zips
for d in skills/*/; do
  n=$(basename "$d")
  rm -f "zips/$n.zip"
  (cd skills && zip -qr "../zips/$n.zip" "$n" -x '*.DS_Store' -x '*__pycache__*')
done
ls -la zips
