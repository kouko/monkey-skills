#!/usr/bin/env bash
# test-privacy-gate-compose-pr.sh
#
# Pins the close-out privacy gate wired into compose-pr.md (dev-workflow
# git-memory, plan Task 4). The composed PR body is the CARRIER checked
# here. Per docs/loom/specs/2026-07-19-closeout-privacy-gate.md, this is
# the other half of making the layer-2 judge SSOT's claim ("both compose
# protocols point here") true — compose-commit.md (T3) carries the
# sibling half for the commit carrier.
#
# The gate step must transcribe the pinned wording verbatim:
#   1. Layer 1 — deterministic scan via scripts/privacy-scan.py
#   2. Layer 2 — fresh-context judge dispatched per
#      protocols/privacy-judge-spec.md (SSOT — rubric NOT inlined here)
#   3. Verdict — any layer-1 finding OR layer-2 BLOCK -> BLOCKED,
#      escalate to human
#   4. Fail-closed (explicit) — script error / dispatch failure /
#      non-conforming judge output -> BLOCK, never PASS
#
# No quality-advisory block here — quality_note is COMMIT-carrier only
# per privacy-judge-spec.md, so it must NOT appear in this PR-carrier step.
#
# Assertions scope to a measured neighborhood around the gate's own
# heading anchor, per
# docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md — a
# whole-file substring presence check goes false-green when a generic
# phrase pre-exists elsewhere in the file.
#
# Usage:
#   bash dev-workflow/tests/test-privacy-gate-compose-pr.sh

set -u

DEV_WORKFLOW_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_PR_MD="$DEV_WORKFLOW_DIR/skills/git-memory/protocols/compose-pr.md"

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

if [ ! -f "$COMPOSE_PR_MD" ]; then
  fail "compose-pr.md does not exist at $COMPOSE_PR_MD"
  echo ""
  echo "================================================================"
  echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
  echo "================================================================"
  exit 1
fi

# -------------------------------------------------------------------------
# Check 1 — the gate heading exists and its neighborhood carries the
# layer-1 script invocation and the layer-2 judge pointer to the SSOT
# spec file (rubric NOT inlined — just the pointer).

WIN1="$(window_after "Privacy gate (fail-closed)" 30 "$COMPOSE_PR_MD")"
if [ -z "$WIN1" ]; then
  fail "anchor 'Privacy gate (fail-closed)' not found in compose-pr.md"
elif ! echo "$WIN1" | grep -qF "scripts/privacy-scan.py"; then
  fail "Privacy gate neighborhood missing layer-1 'scripts/privacy-scan.py' invocation"
elif ! echo "$WIN1" | grep -qF "protocols/privacy-judge-spec.md"; then
  fail "Privacy gate neighborhood missing layer-2 pointer to 'protocols/privacy-judge-spec.md'"
elif ! echo "$WIN1" | grep -qF "fresh-context"; then
  fail "Privacy gate neighborhood missing the 'fresh-context' judge dispatch requirement"
else
  pass "Privacy gate neighborhood present (layer-1 script + layer-2 SSOT pointer)"
fi

# -------------------------------------------------------------------------
# Check 2 — the verdict branch: any layer-1 finding OR a layer-2 BLOCK
# blocks the PR body and escalates to the human.

WIN2="$(window_after "Privacy gate (fail-closed)" 30 "$COMPOSE_PR_MD")"
if [ -z "$WIN2" ]; then
  fail "anchor 'Privacy gate (fail-closed)' not found in compose-pr.md (check 2)"
elif ! echo "$WIN2" | grep -qF "BLOCKED"; then
  fail "Privacy gate neighborhood missing the BLOCKED verdict outcome"
elif ! echo "$WIN2" | grep -qiF "escalate to the" || ! echo "$WIN2" | grep -qiF "human"; then
  fail "Privacy gate neighborhood missing the escalate-to-human branch"
else
  pass "Privacy gate neighborhood specifies the BLOCKED + escalate-to-human verdict"
fi

# -------------------------------------------------------------------------
# Check 3 — the fail-closed branch is EXPLICIT (not emergent): a layer-1
# script error, a layer-2 dispatch failure, or a non-conforming judge
# output must all map to BLOCK, never PASS.

WIN3="$(window_after "Privacy gate (fail-closed)" 30 "$COMPOSE_PR_MD")"
if [ -z "$WIN3" ]; then
  fail "anchor 'Privacy gate (fail-closed)' not found in compose-pr.md (check 3)"
elif ! echo "$WIN3" | grep -qiF "script error"; then
  fail "Privacy gate neighborhood missing the layer-1 'script error' fail-closed branch"
elif ! echo "$WIN3" | grep -qiF "dispatch failure"; then
  fail "Privacy gate neighborhood missing the layer-2 'dispatch failure' fail-closed branch"
elif ! echo "$WIN3" | grep -qiF "non-conforming"; then
  fail "Privacy gate neighborhood missing the 'non-conforming' judge-output fail-closed branch"
elif ! echo "$WIN3" | grep -qiF "never as PASS" && ! echo "$WIN3" | grep -qiF "never PASS"; then
  fail "Privacy gate neighborhood missing the 'never as PASS' explicit framing"
elif ! echo "$WIN3" | grep -qiF "explicit branch"; then
  fail "Privacy gate neighborhood missing the 'explicit branch, not an emergent default' framing"
else
  pass "Privacy gate neighborhood pins the explicit fail-closed branch (script error / dispatch failure / non-conforming -> BLOCK)"
fi

# -------------------------------------------------------------------------
# Check 4 — no quality-advisory block here: quality_note is COMMIT-carrier
# only per privacy-judge-spec.md, so this PR-carrier step must not mention
# it.

WIN4="$(window_after "Privacy gate (fail-closed)" 30 "$COMPOSE_PR_MD")"
if [ -z "$WIN4" ]; then
  fail "anchor 'Privacy gate (fail-closed)' not found in compose-pr.md (check 4)"
elif echo "$WIN4" | grep -qiF "quality_note"; then
  fail "Privacy gate neighborhood must NOT mention 'quality_note' (COMMIT-carrier only, not PR-carrier)"
else
  pass "Privacy gate neighborhood correctly omits the commit-only quality_note block"
fi

# -------------------------------------------------------------------------
# Check 5 — placement: the gate step must land before the point where the
# PR body is handed to `gh pr create` (the Step 6 user-confirmation /
# `gh pr create` step must appear AFTER the gate heading in the file).

GATE_LINE="$(grep -Fn "Privacy gate (fail-closed)" "$COMPOSE_PR_MD" | head -1 | cut -d: -f1)"
CREATE_LINE="$(grep -Fn "gh pr create" "$COMPOSE_PR_MD" | tail -1 | cut -d: -f1)"
if [ -z "$GATE_LINE" ]; then
  fail "cannot check placement — gate heading not found"
elif [ -z "$CREATE_LINE" ]; then
  fail "cannot check placement — no 'gh pr create' reference found in compose-pr.md"
elif [ "$GATE_LINE" -ge "$CREATE_LINE" ]; then
  fail "Privacy gate heading (line $GATE_LINE) does not precede the last 'gh pr create' reference (line $CREATE_LINE)"
else
  pass "Privacy gate heading (line $GATE_LINE) precedes the 'gh pr create' hand-off (line $CREATE_LINE)"
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
