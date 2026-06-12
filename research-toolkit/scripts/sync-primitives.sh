#!/usr/bin/env bash
# sync-primitives.sh — Place byte-identical copies of deep-deep-research's
# reusable primitives into one or more sibling research-toolkit skills.
#
# deep-deep-research is the SSOT (single source of truth) for four primitives:
#
#   - schemas.py  — shared dataclasses / typed structures
#   - rank.py     — source-ranking helper
#   - prompts.py  — prompt builders
#   - dedup.py    — result deduplication
#
# Sibling skills that reuse these (e.g. fact-check, cite-check) carry
# byte-identical copies under their own scripts/ dir. This script
# (re)creates those copies from the deep-deep-research SSOT.
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
SSOT_DIR="$SKILLS_DIR/deep-deep-research/scripts"

# All four SSOT primitives. Each sibling carries only the subset it actually
# uses (see primitives_for) — a skill must not carry code it never invokes.
ALL_PRIMITIVES=(
  "schemas.py"
  "rank.py"
  "prompts.py"
  "dedup.py"
)

# Per-skill primitive set. Default = all four (fact-check uses every one;
# cite-check uses extract/verify/dedup + rank.py for its opt-in quorum).
# deep-read only invokes schemas.py (EXTRACT_SCHEMA) + prompts.py (fetch_prompt)
# via CLI and rolls its own claim-text dedup — it needs neither rank.py nor
# dedup.py, so it carries only the two primitives it actually uses.
primitives_for() {
  case "$1" in
    deep-read) printf '%s\n' "schemas.py" "prompts.py" ;;
    *)         printf '%s\n' "${ALL_PRIMITIVES[@]}" ;;
  esac
}

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <skill-name> [<skill-name>...]" >&2
  exit 2
fi

# Fail loud if any SSOT primitive is missing.
for f in "${ALL_PRIMITIVES[@]}"; do
  if [ ! -f "$SSOT_DIR/$f" ]; then
    echo "ERROR: SSOT primitive not found: $SSOT_DIR/$f" >&2
    exit 3
  fi
done

COPIED=0
for skill in "$@"; do
  target_dir="$SKILLS_DIR/$skill/scripts"
  mkdir -p "$target_dir"
  while IFS= read -r f; do
    cp "$SSOT_DIR/$f" "$target_dir/$f"
    echo "[copy] $SSOT_DIR/$f -> $target_dir/$f"
    COPIED=$((COPIED + 1))
  done < <(primitives_for "$skill")
done

echo
echo "Copied $COPIED file(s) into $# skill(s): $*"
