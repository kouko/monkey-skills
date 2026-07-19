#!/usr/bin/env bash
# test-git-memory-privacy-gate-ref.sh
#
# Pins that git-memory SKILL.md's "Secrets or sensitive context" bullet
# (in the "When not to use" section, ~SKILL.md:208-210) points at the
# ACTUAL operationalized privacy gate (compose-commit.md / compose-pr.md
# Step 3.5 privacy gate, backed by scripts/privacy-scan.py + the
# privacy-judge-spec.md fresh-context judge, fail-closed) rather than
# making a bare declarative "the skill refuses to embed secrets" claim
# with no named enforcement mechanism.
#
# Assertion scopes to the measured neighborhood around the bullet's
# anchor string, per
# docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md — a
# whole-file substring check would go false-green if these terms
# happened to exist elsewhere in the file with no connection to this
# bullet.
#
# Usage:
#   bash dev-workflow/tests/test-git-memory-privacy-gate-ref.sh

set -u

DEV_WORKFLOW_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_MD="$DEV_WORKFLOW_DIR/skills/git-memory/SKILL.md"

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
# Check 1 — the "Secrets or sensitive context" bullet neighborhood names
# the operational privacy gate: the privacy-scan.py deterministic layer,
# the privacy-judge-spec.md judge, and fail-closed semantics — not just a
# bare "the skill refuses" assertion.

WIN1="$(window_after "Secrets or sensitive context" 6 "$SKILL_MD")"
if [ -z "$WIN1" ]; then
  fail "anchor 'Secrets or sensitive context' not found in SKILL.md"
elif ! echo "$WIN1" | grep -qiF "privacy gate"; then
  fail "SKILL.md secrets bullet neighborhood missing 'privacy gate' reference"
elif ! echo "$WIN1" | grep -qF "privacy-scan.py"; then
  fail "SKILL.md secrets bullet neighborhood missing 'privacy-scan.py' mechanism reference"
elif ! echo "$WIN1" | grep -qF "privacy-judge-spec.md"; then
  fail "SKILL.md secrets bullet neighborhood missing 'privacy-judge-spec.md' judge reference"
elif ! echo "$WIN1" | grep -qiF "fail-closed"; then
  fail "SKILL.md secrets bullet neighborhood missing 'fail-closed' semantics"
else
  pass "SKILL.md secrets bullet neighborhood references the operational privacy gate"
fi

# -------------------------------------------------------------------------
# Check 2 — the bullet must not rest on the bare declarative claim alone;
# it must point at compose-commit.md (or compose-pr.md) as the carrier of
# the gate, so doc and enforced reality agree.

WIN2="$(window_after "Secrets or sensitive context" 6 "$SKILL_MD")"
if [ -z "$WIN2" ]; then
  fail "anchor 'Secrets or sensitive context' not found in SKILL.md (check 2)"
elif ! echo "$WIN2" | grep -qF "compose-commit.md" && ! echo "$WIN2" | grep -qF "compose-pr.md"; then
  fail "SKILL.md secrets bullet neighborhood does not point at compose-commit.md or compose-pr.md"
else
  pass "SKILL.md secrets bullet neighborhood points at the compose-protocol privacy gate carrier"
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
