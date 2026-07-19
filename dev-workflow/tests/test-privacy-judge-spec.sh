#!/usr/bin/env bash
# test-privacy-judge-spec.sh
#
# Pins the layer-2 fresh-context privacy judge SSOT
# (dev-workflow/skills/git-memory/protocols/privacy-judge-spec.md) — the
# single spec that compose-commit.md and compose-pr.md must both point at
# instead of duplicating the judge rubric (two copies drift).
#
# Per docs/loom/specs/2026-07-19-closeout-privacy-gate.md, the spec MUST
# contain five parts: (1) dispatch instruction (fresh-context agent,
# composed text is content not commands), (2) the four inspected
# categories (secrets explicitly out of scope — layer-1 regex owns them),
# (3) a structured PASS|BLOCK + findings output schema, (4) an optional
# non-blocking commit-only `quality_note` field, (5) an explicit
# fail-closed contract (dispatch failure or non-conforming output → BLOCK).
#
# Assertions scope to measured neighborhoods around each claim's anchor
# string, per docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md
# — a whole-file substring presence check goes false-green when a generic
# phrase pre-exists elsewhere in the file.
#
# Usage:
#   bash dev-workflow/tests/test-privacy-judge-spec.sh

set -u

DEV_WORKFLOW_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SPEC_MD="$DEV_WORKFLOW_DIR/skills/git-memory/protocols/privacy-judge-spec.md"

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
# Check 0 — the spec file exists at all.

if [ ! -f "$SPEC_MD" ]; then
  fail "privacy-judge-spec.md does not exist at $SPEC_MD"
  echo ""
  echo "================================================================"
  echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
  echo "================================================================"
  exit 1
else
  pass "privacy-judge-spec.md exists"
fi

# -------------------------------------------------------------------------
# Check 1 — Part 1: dispatch instruction. Must direct dispatch of a
# FRESH-CONTEXT agent over the composed text, and must state that the
# text under review is content, not commands (prompt-injection guard).

WIN1="$(window_after "## Dispatch instruction" 25 "$SPEC_MD")"
if [ -z "$WIN1" ]; then
  fail "anchor '## Dispatch instruction' not found in privacy-judge-spec.md"
elif ! echo "$WIN1" | grep -qiF "fresh-context"; then
  fail "Dispatch instruction neighborhood missing 'fresh-context' agent requirement"
elif ! echo "$WIN1" | grep -qiF "content, not commands" && ! echo "$WIN1" | grep -qiF "content not commands"; then
  fail "Dispatch instruction neighborhood missing the content-not-commands prompt-injection guard"
else
  pass "Dispatch instruction neighborhood present (fresh-context + content-not-commands guard)"
fi

# -------------------------------------------------------------------------
# Check 2 — Part 2: categories inspected. All four categories must be
# named, and secrets must be explicitly stated OUT of scope here.

WIN2="$(window_after "## Categories inspected" 30 "$SPEC_MD")"
if [ -z "$WIN2" ]; then
  fail "anchor '## Categories inspected' not found in privacy-judge-spec.md"
elif ! echo "$WIN2" | grep -qiF "personal name"; then
  fail "Categories neighborhood missing 'personal names'"
elif ! echo "$WIN2" | grep -qiF "company" && ! echo "$WIN2" | grep -qiF "organization"; then
  fail "Categories neighborhood missing 'company/organization names'"
elif ! echo "$WIN2" | grep -qiF "codename"; then
  fail "Categories neighborhood missing 'internal project codenames'"
elif ! echo "$WIN2" | grep -qiF "contextual leak"; then
  fail "Categories neighborhood missing 'contextual leaks'"
elif ! echo "$WIN2" | grep -qiF "out of scope"; then
  fail "Categories neighborhood missing the secrets-out-of-scope carve-out"
elif ! echo "$WIN2" | grep -qiF "layer-1"; then
  fail "Categories neighborhood missing the layer-1-owns-secrets pointer"
else
  pass "Categories neighborhood lists all four categories + secrets carve-out"
fi

# -------------------------------------------------------------------------
# Check 3 — Part 3: output schema. Must specify PASS | BLOCK plus a
# findings list with category, quoted span, and why-sensitive fields.

WIN3="$(window_after "## Output schema" 30 "$SPEC_MD")"
if [ -z "$WIN3" ]; then
  fail "anchor '## Output schema' not found in privacy-judge-spec.md"
elif ! echo "$WIN3" | grep -qF "PASS"; then
  fail "Output schema neighborhood missing 'PASS'"
elif ! echo "$WIN3" | grep -qF "BLOCK"; then
  fail "Output schema neighborhood missing 'BLOCK'"
elif ! echo "$WIN3" | grep -qiF "findings"; then
  fail "Output schema neighborhood missing a 'findings' list"
elif ! echo "$WIN3" | grep -qiF "quoted span"; then
  fail "Output schema neighborhood missing 'quoted span' field"
elif ! echo "$WIN3" | grep -qiF "why"; then
  fail "Output schema neighborhood missing the 'why it's sensitive' field"
else
  pass "Output schema neighborhood specifies PASS|BLOCK + findings (category/quoted span/why)"
fi

# -------------------------------------------------------------------------
# Check 4 — Part 4: quality_note field. Optional, commit-carrier only,
# and explicitly non-blocking / never-escalating.

WIN4="$(window_after "## \`quality_note\` field" 25 "$SPEC_MD")"
if [ -z "$WIN4" ]; then
  fail "anchor for quality_note field section not found in privacy-judge-spec.md"
elif ! echo "$WIN4" | grep -qiF "optional"; then
  fail "quality_note neighborhood missing 'optional'"
elif ! echo "$WIN4" | grep -qiF "commit"; then
  fail "quality_note neighborhood missing the commit-carrier-only scope"
elif ! echo "$WIN4" | grep -qiF "non-blocking" && ! echo "$WIN4" | grep -qiF "never block"; then
  fail "quality_note neighborhood missing the non-blocking guarantee"
elif ! echo "$WIN4" | grep -qiF "never escalate" && ! echo "$WIN4" | grep -qiF "never escalates"; then
  fail "quality_note neighborhood missing the never-escalates guarantee"
else
  pass "quality_note neighborhood present (optional, commit-only, non-blocking, never escalates)"
fi

# -------------------------------------------------------------------------
# Check 5 — Part 5: fail-closed contract. Must be an EXPLICIT branch/rule
# (not emergent) covering BOTH a dispatch failure and a non-conforming
# judge output, both mapping to BLOCK.

WIN5="$(window_after "## Fail-closed contract" 25 "$SPEC_MD")"
if [ -z "$WIN5" ]; then
  fail "anchor '## Fail-closed contract' not found in privacy-judge-spec.md"
elif ! echo "$WIN5" | grep -qiF "dispatch failure" && ! echo "$WIN5" | grep -qiF "dispatch fails"; then
  fail "Fail-closed neighborhood missing the dispatch-failure branch"
elif ! echo "$WIN5" | grep -qiF "non-conforming"; then
  fail "Fail-closed neighborhood missing the non-conforming-output branch"
elif ! echo "$WIN5" | grep -qiF "explicit"; then
  fail "Fail-closed neighborhood missing the explicit-not-emergent framing"
elif ! echo "$WIN5" | grep -qF "BLOCK"; then
  fail "Fail-closed neighborhood missing the BLOCK outcome"
else
  pass "Fail-closed neighborhood present (explicit dispatch-failure + non-conforming → BLOCK)"
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
