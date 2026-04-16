#!/usr/bin/env sh
# sync-check.sh — Verify all skill-local script copies match source of truth
#
# Usage: sh investing-toolkit/scripts/sync-check.sh
# Exit 0 = all in sync. Exit 1 = drift detected.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS="$SCRIPT_DIR/../skills"
ERRORS=0

echo "Checking script sync..."

for skill_script in "$SKILLS"/*/scripts/*.py; do
  [ -f "$skill_script" ] || continue
  filename="$(basename "$skill_script")"
  source="$SCRIPT_DIR/$filename"

  if [ ! -f "$source" ]; then
    echo "WARN: $skill_script has no source-of-truth at $source"
    continue
  fi

  if ! diff -q "$source" "$skill_script" > /dev/null 2>&1; then
    echo "DRIFT: $skill_script differs from $source"
    ERRORS=$((ERRORS + 1))
  fi
done

if [ "$ERRORS" -gt 0 ]; then
  echo ""
  echo "FAIL: $ERRORS file(s) out of sync."
  echo "Run: sh investing-toolkit/scripts/sync-scripts.sh"
  exit 1
fi

echo "OK: All skill scripts match source of truth."
