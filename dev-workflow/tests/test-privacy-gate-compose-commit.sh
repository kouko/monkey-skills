#!/usr/bin/env bash
# test-privacy-gate-compose-commit.sh
#
# Pins that compose-commit.md wires the close-out privacy gate into the
# commit-message carrier (loom-code plan Task 3, docs/loom/specs/
# 2026-07-19-closeout-privacy-gate.md). The layer-2 judge SSOT
# (privacy-judge-spec.md) states both compose-commit.md and compose-pr.md
# point at it; this test pins the compose-commit.md half of that claim.
#
# Requires, in one neighborhood after the composed-message steps:
#   1. layer-1 deterministic scan invocation (scripts/privacy-scan.py)
#   2. layer-2 fresh-context judge pointing at protocols/privacy-judge-spec.md
#   3. an explicit fail-closed -> BLOCK branch (not an emergent default)
#   4. the compose-commit-only quality_note advisory (non-blocking)
#
# Assertions scope to a measured neighborhood around the gate's anchor
# string, per docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md
# — a whole-file substring check goes false-green when a generic phrase
# pre-exists elsewhere in the file.
#
# Usage:
#   bash dev-workflow/tests/test-privacy-gate-compose-commit.sh

set -u

DEV_WORKFLOW_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_COMMIT_MD="$DEV_WORKFLOW_DIR/skills/git-memory/protocols/compose-commit.md"

PASS_COUNT=0
FAIL_COUNT=0
pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# Extract N lines starting at the line matching anchor $1 (fixed-string),
# joined into one space-separated string so a markdown line-wrap can't
# split a phrase in a way that hides it from a substring check.
window_after() {
  local anchor="$1" n="$2" file="$3"
  local start
  start="$(grep -Fn "$anchor" "$file" | head -1 | cut -d: -f1)"
  if [ -z "$start" ]; then
    echo ""
    return
  fi
  sed -n "${start},$((start + n))p" "$file" | tr '\n' ' '
}

# -------------------------------------------------------------------------
# Check 0 — the file exists at all.

if [ ! -f "$COMPOSE_COMMIT_MD" ]; then
  fail "compose-commit.md does not exist at $COMPOSE_COMMIT_MD"
  echo ""
  echo "================================================================"
  echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
  echo "================================================================"
  exit 1
else
  pass "compose-commit.md exists"
fi

# -------------------------------------------------------------------------
# Check 1 — the privacy gate neighborhood exists and runs the layer-1
# deterministic scan (scripts/privacy-scan.py) as the first check.

WIN="$(window_after "Privacy gate (fail-closed)" 30 "$COMPOSE_COMMIT_MD")"
if [ -z "$WIN" ]; then
  fail "anchor 'Privacy gate (fail-closed)' not found in compose-commit.md"
elif ! echo "$WIN" | grep -qF "privacy-scan.py"; then
  fail "Privacy gate neighborhood missing the layer-1 'privacy-scan.py' invocation"
else
  pass "Privacy gate neighborhood present and runs layer-1 privacy-scan.py"
fi

# -------------------------------------------------------------------------
# Check 2 — the layer-2 fresh-context judge is dispatched and points at
# the SSOT spec file rather than duplicating its rubric.

if [ -z "$WIN" ]; then
  fail "cannot check layer-2 judge — neighborhood window empty"
elif ! echo "$WIN" | grep -qiF "fresh-context"; then
  fail "Privacy gate neighborhood missing the layer-2 'fresh-context' judge dispatch"
elif ! echo "$WIN" | grep -qF "privacy-judge-spec.md"; then
  fail "Privacy gate neighborhood missing the pointer to protocols/privacy-judge-spec.md"
else
  pass "Privacy gate neighborhood dispatches the layer-2 fresh-context judge via privacy-judge-spec.md"
fi

# -------------------------------------------------------------------------
# Check 3 — an explicit fail-closed -> BLOCK branch (not an emergent
# default): a script error, dispatch failure, or non-conforming output
# must all map to BLOCK.

if [ -z "$WIN" ]; then
  fail "cannot check fail-closed branch — neighborhood window empty"
elif ! echo "$WIN" | grep -qF "BLOCK"; then
  fail "Privacy gate neighborhood missing the 'BLOCK' verdict outcome"
elif ! echo "$WIN" | grep -qiF "explicit"; then
  fail "Privacy gate neighborhood missing the explicit-not-emergent framing"
elif ! echo "$WIN" | grep -qiF "fail-closed"; then
  fail "Privacy gate neighborhood missing the 'fail-closed' label on the branch"
else
  pass "Privacy gate neighborhood states an explicit fail-closed -> BLOCK branch"
fi

# -------------------------------------------------------------------------
# Check 4 — the compose-commit-ONLY quality_note advisory: non-blocking,
# never escalates, points at the same SSOT spec.

WIN_Q="$(window_after "Quality advisory" 15 "$COMPOSE_COMMIT_MD")"
if [ -z "$WIN_Q" ]; then
  fail "anchor 'Quality advisory' not found in compose-commit.md"
elif ! echo "$WIN_Q" | grep -qiF "quality_note"; then
  fail "Quality advisory neighborhood missing the 'quality_note' field name"
elif ! echo "$WIN_Q" | grep -qiF "non-blocking" && ! echo "$WIN_Q" | grep -qiF "never blocks"; then
  fail "Quality advisory neighborhood missing the non-blocking guarantee"
elif ! echo "$WIN_Q" | grep -qF "privacy-judge-spec.md"; then
  fail "Quality advisory neighborhood missing the pointer to protocols/privacy-judge-spec.md"
else
  pass "Quality advisory neighborhood present (quality_note, non-blocking, points at privacy-judge-spec.md)"
fi

# -------------------------------------------------------------------------
# Summary

echo ""
echo "================================================================"
echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
echo "================================================================"

if [ "${FAIL_COUNT}" -gt 0 ]; then
  exit 1
fi
exit 0
