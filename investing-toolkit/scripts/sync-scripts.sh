#!/usr/bin/env sh
# sync-scripts.sh — Copy source-of-truth scripts to each skill that needs them
#
# Usage: sh investing-toolkit/scripts/sync-scripts.sh
# Run from repo root or investing-toolkit/ directory.

set -e

# Resolve base directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$SCRIPT_DIR/.."
SCRIPTS="$SCRIPT_DIR"
SKILLS="$BASE/skills"

echo "Source of truth: $SCRIPTS"
echo "Skills directory: $SKILLS"
echo ""

# ── Mapping: script → skill directories ─────────────────────────────────────

copy_to() {
  script="$1"
  shift
  for skill in "$@"; do
    dest="$SKILLS/$skill/scripts"
    mkdir -p "$dest"
    cp "$SCRIPTS/$script" "$dest/$script"
    echo "  $script → $skill/scripts/"
  done
}

echo "Syncing yfinance_client.py..."
copy_to yfinance_client.py \
  us-stock-snapshot \
  technical-snapshot \
  stock-screener \
  investment-memo-writer \
  invest-portfolio \
  china-macro

echo "Syncing fred_client.py..."
copy_to fred_client.py \
  macro-regime-snapshot \
  investment-memo-writer \
  dcf-valuation \
  us-macro \
  china-macro

echo "Syncing finmind_client.py..."
copy_to finmind_client.py \
  taiwan-stock-snapshot \
  investment-memo-writer \
  invest-portfolio

echo "Syncing boj_client.py..."
copy_to boj_client.py \
  japan-macro

echo "Syncing estat_client.py..."
copy_to estat_client.py \
  japan-macro

echo "Syncing cbc_client.py..."
copy_to cbc_client.py \
  taiwan-macro

echo "Syncing dgbas_client.py..."
copy_to dgbas_client.py \
  taiwan-macro

echo "Syncing ndc_client.py..."
copy_to ndc_client.py \
  taiwan-macro

echo "Syncing statgov_client.py..."
copy_to statgov_client.py \
  taiwan-macro

echo "Syncing fdr_client.py..."
copy_to fdr_client.py \
  korea-macro

echo "Syncing akshare_client.py..."
copy_to akshare_client.py \
  china-macro

echo "Syncing nbs_client.py..."
copy_to nbs_client.py \
  china-macro

echo "Syncing ta_client.py..."
copy_to ta_client.py \
  technical-snapshot \
  stock-screener

echo "Syncing setup.sh..."
copy_to setup.sh \
  us-stock-snapshot \
  technical-snapshot \
  stock-screener \
  investment-memo-writer \
  invest-portfolio \
  macro-regime-snapshot \
  dcf-valuation \
  taiwan-stock-snapshot \
  us-macro \
  japan-macro \
  taiwan-macro \
  korea-macro \
  china-macro

echo ""
echo "Sync complete."
