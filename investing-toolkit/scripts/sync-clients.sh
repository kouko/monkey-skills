#!/usr/bin/env bash
# sync-clients.sh — Synchronize duplicated clients across investing-toolkit skills.
#
# Supersedes investing-toolkit/scripts/sync-check.sh + sync-scripts.sh in v2.0.0.
# Legacy scripts retained until PR 3 cutover (deletion + CI required-flip happen
# in the same commit so branch protection and on-disk reality stay aligned).
#
# Modes:
#   bash investing-toolkit/scripts/sync-clients.sh           # copy canonical → all targets
#   bash investing-toolkit/scripts/sync-clients.sh --check   # report drift, exit 1 on any
#
# Canonical sources (per ADR-0001 §"Acceptable Duplications"):
#   - yfinance_client.py: investing-toolkit/scripts/yfinance_client.py
#       → data-us, data-jp, data-tw, data-kr, data-cn (5 skills)
#   - fred_client.py:     investing-toolkit/scripts/fred_client.py
#       → data-us, data-cn (2 skills)
#   - nbs_client.py:      investing-toolkit/scripts/nbs_client.py
#       → data-cn (1 skill)
#   - akshare_client.py:  investing-toolkit/scripts/akshare_client.py
#       → data-cn (1 skill)
#
# v2.0.0 has only one ta_client.py consumer (analysis-technical, the canonical
# owner). When other analysis skills consume TA primitives, add their dirs to a
# TA_TARGETS array here AND mirror in .github/workflows/check-script-sync.yml.
#
# Compatible with macOS (md5) and Linux (md5sum).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOLKIT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$TOOLKIT_DIR/skills"

CHECK_ONLY=0
case "${1:-}" in
  --check) CHECK_ONLY=1 ;;
  "" )    : ;;
  * )     echo "Unknown flag: $1" >&2; echo "Usage: $0 [--check]" >&2; exit 2 ;;
esac

# Cross-platform md5
md5_of() {
  local f="$1"
  if command -v md5sum >/dev/null 2>&1; then
    md5sum "$f" | awk '{print $1}'
  elif command -v md5 >/dev/null 2>&1; then
    md5 -q "$f"
  else
    echo "ERROR: neither md5sum nor md5 available" >&2
    exit 3
  fi
}

# Per-file targets
YF_CANONICAL="$TOOLKIT_DIR/scripts/yfinance_client.py"
YF_TARGETS=(
  "data-us"
  "data-jp"
  "data-tw"
  "data-kr"
  "data-cn"
)

FRED_CANONICAL="$TOOLKIT_DIR/scripts/fred_client.py"
FRED_TARGETS=(
  "data-us"
  "data-cn"
)

NBS_CANONICAL="$TOOLKIT_DIR/scripts/nbs_client.py"
NBS_TARGETS=(
  "data-cn"
)

AKSHARE_CANONICAL="$TOOLKIT_DIR/scripts/akshare_client.py"
AKSHARE_TARGETS=(
  "data-cn"
)

# ta_client.py: no second consumer in v2.0.0 (only analysis-technical, which IS
# the canonical owner). Section intentionally omitted — see header for when to
# re-introduce.

SYNCED=0
UNCHANGED=0
DRIFT=0
MISSING_CANONICAL=0
SKIPPED_TARGET=0

process_one() {
  local canonical="$1"
  local target_skill="$2"
  local filename
  filename="$(basename "$canonical")"
  local target_dir="$SKILLS_DIR/$target_skill/scripts"
  local target="$target_dir/$filename"

  if [ ! -f "$canonical" ]; then
    echo "[miss] canonical not found: $canonical"
    MISSING_CANONICAL=$((MISSING_CANONICAL + 1))
    return 0
  fi

  if [ ! -d "$target_dir" ]; then
    echo "[skip] target skill not present: $target_skill (no scripts/ dir)"
    SKIPPED_TARGET=$((SKIPPED_TARGET + 1))
    return 0
  fi

  # Same file — nothing to do (e.g. ta_client.py canonical IS analysis-technical's copy)
  if [ "$canonical" = "$target" ]; then
    return 0
  fi

  if [ ! -f "$target" ]; then
    if [ "$CHECK_ONLY" -eq 1 ]; then
      echo "[DRIFT] missing copy: $target"
      DRIFT=$((DRIFT + 1))
    else
      cp "$canonical" "$target"
      echo "[copy] $canonical → $target (new)"
      SYNCED=$((SYNCED + 1))
    fi
    return 0
  fi

  local h_canonical h_target
  h_canonical="$(md5_of "$canonical")"
  h_target="$(md5_of "$target")"

  if [ "$h_canonical" = "$h_target" ]; then
    UNCHANGED=$((UNCHANGED + 1))
    return 0
  fi

  if [ "$CHECK_ONLY" -eq 1 ]; then
    echo "[DRIFT] $target"
    echo "        canonical md5 = $h_canonical"
    echo "        target    md5 = $h_target"
    DRIFT=$((DRIFT + 1))
  else
    cp "$canonical" "$target"
    echo "[sync] $canonical → $target"
    SYNCED=$((SYNCED + 1))
  fi
}

if [ "$CHECK_ONLY" -eq 1 ]; then
  echo "Checking client sync (canonical → skill copies)..."
else
  echo "Syncing clients (canonical → skill copies)..."
fi
echo

echo "== yfinance_client.py =="
for skill in "${YF_TARGETS[@]}"; do
  process_one "$YF_CANONICAL" "$skill"
done
echo

echo "== fred_client.py =="
for skill in "${FRED_TARGETS[@]}"; do
  process_one "$FRED_CANONICAL" "$skill"
done
echo

echo "== nbs_client.py =="
for skill in "${NBS_TARGETS[@]}"; do
  process_one "$NBS_CANONICAL" "$skill"
done
echo

echo "== akshare_client.py =="
for skill in "${AKSHARE_TARGETS[@]}"; do
  process_one "$AKSHARE_CANONICAL" "$skill"
done
echo

# == ta_client.py == intentionally absent — see header.

echo "Summary:"
if [ "$CHECK_ONLY" -eq 1 ]; then
  echo "  Drift: $DRIFT"
  echo "  Unchanged: $UNCHANGED"
  echo "  Skipped (target dir missing): $SKIPPED_TARGET"
  echo "  Missing canonical: $MISSING_CANONICAL"
  if [ "$DRIFT" -gt 0 ]; then
    echo
    echo "FAIL: drift detected. Run without --check to fix:"
    echo "  bash investing-toolkit/scripts/sync-clients.sh"
    exit 1
  fi
  echo
  echo "OK: all in sync."
else
  echo "  Synced $SYNCED files; $UNCHANGED unchanged; skipped $SKIPPED_TARGET (no target dir); missing canonical: $MISSING_CANONICAL"
fi
