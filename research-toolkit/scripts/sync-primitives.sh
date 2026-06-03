#!/usr/bin/env bash
# sync-primitives.sh — Place byte-identical copies of deep-research's
# reusable primitives into one or more sibling research-toolkit skills.
#
# deep-research is the SSOT (single source of truth) for four primitives:
#
#   - schemas.py  — shared dataclasses / typed structures
#   - rank.py     — source-ranking helper
#   - prompts.py  — prompt builders
#   - dedup.py    — result deduplication
#
# Sibling skills that reuse these (e.g. fact-check, cite-check) carry
# byte-identical copies under their own scripts/ dir. This script
# (re)creates those copies from the deep-research SSOT.
#
# Usage:
#   bash research-toolkit/scripts/sync-primitives.sh <skill-name> [<skill-name>...]
#   e.g. bash research-toolkit/scripts/sync-primitives.sh fact-check cite-check
#
# Idempotent: re-running overwrites copies with the current SSOT.
# Target skill scripts/ dirs are created with mkdir -p if absent.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOLKIT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$TOOLKIT_DIR/skills"
SSOT_DIR="$SKILLS_DIR/deep-research/scripts"

PRIMITIVES=(
  "schemas.py"
  "rank.py"
  "prompts.py"
  "dedup.py"
)

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <skill-name> [<skill-name>...]" >&2
  exit 2
fi

# Fail loud if any SSOT primitive is missing.
for f in "${PRIMITIVES[@]}"; do
  if [ ! -f "$SSOT_DIR/$f" ]; then
    echo "ERROR: SSOT primitive not found: $SSOT_DIR/$f" >&2
    exit 3
  fi
done

COPIED=0
for skill in "$@"; do
  target_dir="$SKILLS_DIR/$skill/scripts"
  mkdir -p "$target_dir"
  for f in "${PRIMITIVES[@]}"; do
    cp "$SSOT_DIR/$f" "$target_dir/$f"
    echo "[copy] $SSOT_DIR/$f -> $target_dir/$f"
    COPIED=$((COPIED + 1))
  done
done

echo
echo "Copied $COPIED file(s) into $# skill(s): $*"
