#!/usr/bin/env bash
# test-git-memory-carrier-doctrine.sh
#
# Pins the O4 carrier-hierarchy doctrine in dev-workflow/skills/git-memory/
# SKILL.md: the repo's committed memory store (docs/loom/memory/) is the
# authoritative durable carrier; commit trailers are commit-bound capture —
# best-effort, secondary, never the retrieval path a durable lesson depends
# on (PR #574 incident: pre-push --verify passed, squash landed the trailer
# un-retrievable; CommitDistill arXiv:2605.18284 measured git log --grep
# retrieval at 0.083 vs a distilled file layer at 0.750). Guards against
# regressing to the old framing that treated git artifacts themselves as
# the durable carrier, and "git log --grep is the supported [durable]
# path".
#
# Assertions scope to measured neighborhoods around each claim's anchor
# string, per docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md
# — a whole-file substring presence check goes false-green when a generic
# phrase pre-exists elsewhere in the file.
#
# Usage:
#   bash dev-workflow/tests/test-git-memory-carrier-doctrine.sh

set -u

SKILL_MD="$(cd "$(dirname "$0")/.." && pwd)/skills/git-memory/SKILL.md"
DEV_WORKFLOW_DIR="$(cd "$(dirname "$0")/.." && pwd)"

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
# Check 1 — pinned carrier-hierarchy sentence present near the top of the
# file (transcribed VERBATIM per the plan's ## Notes pinned wording).

TOP="$(head -20 "$SKILL_MD" | tr '\n' ' ')"
if echo "$TOP" | grep -qF "the authoritative carrier" \
  && echo "$TOP" | grep -qF "commit-bound capture: best-effort, secondary" \
  && echo "$TOP" | grep -qF "never the retrieval path"; then
  pass "pinned carrier-hierarchy sentence present near top of SKILL.md"
else
  fail "pinned carrier-hierarchy sentence missing near top of SKILL.md"
fi

# -------------------------------------------------------------------------
# Check 2 — "durable substrate" fully eradicated from SKILL.md

if grep -qi "durable substrate" "$SKILL_MD"; then
  fail "'durable substrate' still present in SKILL.md"
else
  pass "'durable substrate' absent from SKILL.md"
fi

# -------------------------------------------------------------------------
# Check 3 — "durable substrate" fully eradicated plugin-wide (the
# plugin-wide sweep acceptance from the plan). Excludes this test file
# itself, which legitimately carries the phrase as the string it asserts
# the absence of — that's the test, not a contradicting doctrine claim.

if grep -ril "durable substrate" "$DEV_WORKFLOW_DIR" 2>/dev/null \
  | grep -v "/tests/test-git-memory-carrier-doctrine.sh$" | grep -q .; then
  fail "'durable substrate' still present somewhere in dev-workflow/"
else
  pass "'durable substrate' absent from the whole dev-workflow plugin (excl. this test)"
fi

# -------------------------------------------------------------------------
# Check 4 — squash-caveat / retrieval-table neighborhood no longer frames
# git log --grep / trailers as the reliable or durable retrieval path

WIN4="$(window_after "Squash-merge caveat" 25 "$SKILL_MD")"
if [ -z "$WIN4" ]; then
  fail "anchor 'Squash-merge caveat' not found in SKILL.md"
elif echo "$WIN4" | grep -qF "Reliable retrieval"; then
  fail "retrieval-path table still labeled 'Reliable retrieval' (durable framing survives)"
elif echo "$WIN4" | grep -qF "durable carrier"; then
  fail "verification paragraph still calls commit-bound capture 'a durable carrier'"
else
  pass "squash-caveat/verification neighborhood no longer frames grep/trailers as durable"
fi

# -------------------------------------------------------------------------
# Check 5 — invocation-policy neighborhood no longer calls the two squash
# capture locations "durable carriers"

WIN5="$(window_after "last checkpoint before the" 10 "$SKILL_MD")"
if [ -z "$WIN5" ]; then
  fail "anchor 'last checkpoint before the' not found in SKILL.md"
elif echo "$WIN5" | grep -qF "durable carriers"; then
  fail "invocation-policy note still calls squash capture locations 'durable carriers'"
else
  pass "invocation-policy neighborhood no longer claims 'durable carriers'"
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
