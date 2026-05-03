#!/usr/bin/env bash
# sync-clients.sh — Synchronize cross-skill duplicated clients within
# investing-toolkit.
#
# Post-ADR-0008 (2026-05-03): MCP server removed. The
# `investing-toolkit/scripts/` canonical-vs-skill-copy duality is gone;
# only true cross-skill duplications remain. Two groups are tracked:
#
#   - yfinance_client.py: data-us is the reference; data-jp / data-tw /
#                         data-kr / data-cn must equal data-us byte-for-byte.
#   - fred_client.py:     data-us is the reference; data-cn must equal it.
#
# All other clients (nbs, akshare, dgbas, ndc, cbc, statgov, fdr,
# boj, ecb, estat, sec_edgar, mops, edinet, finmind, twse_openapi,
# tdnet, ta) are single-skill — no cross-skill copies, no sync needed.
#
# Modes:
#   bash investing-toolkit/scripts/sync-clients.sh           # copy reference → all targets
#   bash investing-toolkit/scripts/sync-clients.sh --check   # report drift, exit 1 on any
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

# Per-file targets — data-us is the reference for both groups (US is the
# canonical reference skill across the toolkit).
YF_REFERENCE="$SKILLS_DIR/data-us/scripts/yfinance_client.py"
YF_TARGETS=(
  "data-jp"
  "data-tw"
  "data-kr"
  "data-cn"
)

FRED_REFERENCE="$SKILLS_DIR/data-us/scripts/fred_client.py"
FRED_TARGETS=(
  "data-cn"
)

SYNCED=0
UNCHANGED=0
DRIFT=0
MISSING_REFERENCE=0
SKIPPED_TARGET=0

process_one() {
  local reference="$1"
  local target_skill="$2"
  local filename
  filename="$(basename "$reference")"
  local target_dir="$SKILLS_DIR/$target_skill/scripts"
  local target="$target_dir/$filename"

  if [ ! -f "$reference" ]; then
    echo "[miss] reference not found: $reference"
    MISSING_REFERENCE=$((MISSING_REFERENCE + 1))
    return 0
  fi

  if [ ! -d "$target_dir" ]; then
    echo "[skip] target skill not present: $target_skill (no scripts/ dir)"
    SKIPPED_TARGET=$((SKIPPED_TARGET + 1))
    return 0
  fi

  if [ ! -f "$target" ]; then
    if [ "$CHECK_ONLY" -eq 1 ]; then
      echo "[DRIFT] missing copy: $target"
      DRIFT=$((DRIFT + 1))
    else
      cp "$reference" "$target"
      echo "[copy] $reference → $target (new)"
      SYNCED=$((SYNCED + 1))
    fi
    return 0
  fi

  local h_reference h_target
  h_reference="$(md5_of "$reference")"
  h_target="$(md5_of "$target")"

  if [ "$h_reference" = "$h_target" ]; then
    UNCHANGED=$((UNCHANGED + 1))
    return 0
  fi

  if [ "$CHECK_ONLY" -eq 1 ]; then
    echo "[DRIFT] $target"
    echo "        reference md5 = $h_reference"
    echo "        target    md5 = $h_target"
    DRIFT=$((DRIFT + 1))
  else
    cp "$reference" "$target"
    echo "[sync] $reference → $target"
    SYNCED=$((SYNCED + 1))
  fi
}

if [ "$CHECK_ONLY" -eq 1 ]; then
  echo "Checking client sync (data-us reference → cross-skill copies)..."
else
  echo "Syncing clients (data-us reference → cross-skill copies)..."
fi
echo

echo "== yfinance_client.py =="
for skill in "${YF_TARGETS[@]}"; do
  process_one "$YF_REFERENCE" "$skill"
done
echo

echo "== fred_client.py =="
for skill in "${FRED_TARGETS[@]}"; do
  process_one "$FRED_REFERENCE" "$skill"
done
echo

echo "Summary:"
if [ "$CHECK_ONLY" -eq 1 ]; then
  echo "  Drift: $DRIFT"
  echo "  Unchanged: $UNCHANGED"
  echo "  Skipped (target dir missing): $SKIPPED_TARGET"
  echo "  Missing reference: $MISSING_REFERENCE"
  if [ "$DRIFT" -gt 0 ]; then
    echo
    echo "FAIL: drift detected. Run without --check to fix:"
    echo "  bash investing-toolkit/scripts/sync-clients.sh"
    exit 1
  fi
  echo
  echo "OK: all in sync."
else
  echo "  Synced $SYNCED files; $UNCHANGED unchanged; skipped $SKIPPED_TARGET (no target dir); missing reference: $MISSING_REFERENCE"
fi
