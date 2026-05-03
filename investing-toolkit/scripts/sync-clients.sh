#!/usr/bin/env bash
# sync-clients.sh — Synchronize duplicated clients across investing-toolkit skills.
#
# v2.0.0 sole sync mechanism. Replaced the legacy v1.x pair
# (sync-check.sh + sync-scripts.sh), which were deleted in the v2.0.0
# three-layer refactor — they hardcoded v1.x skill names (us-macro,
# us-stock-snapshot, etc.) that no longer exist. All skill targets here
# are v2.0.0 data-{country} skills, matching ADR-0001's acceptable-
# duplication table.
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
#   - dgbas_client.py:    investing-toolkit/scripts/dgbas_client.py
#       → data-tw (1 skill)  [added 2026-05-03]
#   - ndc_client.py:      investing-toolkit/scripts/ndc_client.py
#       → data-tw (1 skill)  [added 2026-05-03]
#   - cbc_client.py:      investing-toolkit/scripts/cbc_client.py
#       → data-tw (1 skill)  [added 2026-05-03]
#   - statgov_client.py:  investing-toolkit/scripts/statgov_client.py
#       → data-tw (1 skill)  [added 2026-05-03]
#   - fdr_client.py:      investing-toolkit/scripts/fdr_client.py
#       → data-kr (1 skill)  [added 2026-05-03]
#
# The 5 *-client groups added 2026-05-03 share the same canonical-vs-copy
# duality: investing-toolkit/scripts/<name>.py is imported by servers/
# mcp_server.py via sys.path; the skill copy is invoked as `uv run` script
# via PEP 723 inline metadata. See "MCP vs CLI parallel mechanisms" in
# investing-toolkit/docs/architecture.md (or grep `mcp_server.py` for
# `_import_clients`).
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

# Added 2026-05-03 — TW/KR clients with canonical-vs-skill-copy duality
# for MCP server (investing-toolkit/scripts/) vs CLI / pack.py (skill copy).
DGBAS_CANONICAL="$TOOLKIT_DIR/scripts/dgbas_client.py"
DGBAS_TARGETS=(
  "data-tw"
)

NDC_CANONICAL="$TOOLKIT_DIR/scripts/ndc_client.py"
NDC_TARGETS=(
  "data-tw"
)

CBC_CANONICAL="$TOOLKIT_DIR/scripts/cbc_client.py"
CBC_TARGETS=(
  "data-tw"
)

STATGOV_CANONICAL="$TOOLKIT_DIR/scripts/statgov_client.py"
STATGOV_TARGETS=(
  "data-tw"
)

FDR_CANONICAL="$TOOLKIT_DIR/scripts/fdr_client.py"
FDR_TARGETS=(
  "data-kr"
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

echo "== dgbas_client.py =="
for skill in "${DGBAS_TARGETS[@]}"; do
  process_one "$DGBAS_CANONICAL" "$skill"
done
echo

echo "== ndc_client.py =="
for skill in "${NDC_TARGETS[@]}"; do
  process_one "$NDC_CANONICAL" "$skill"
done
echo

echo "== cbc_client.py =="
for skill in "${CBC_TARGETS[@]}"; do
  process_one "$CBC_CANONICAL" "$skill"
done
echo

echo "== statgov_client.py =="
for skill in "${STATGOV_TARGETS[@]}"; do
  process_one "$STATGOV_CANONICAL" "$skill"
done
echo

echo "== fdr_client.py =="
for skill in "${FDR_TARGETS[@]}"; do
  process_one "$FDR_CANONICAL" "$skill"
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
