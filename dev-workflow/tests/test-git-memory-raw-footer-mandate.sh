#!/usr/bin/env bash
# test-git-memory-raw-footer-mandate.sh
#
# Pins the O2 raw-trailer-footer mandate: a memory-worthy PR body MUST end
# with a blank-line-separated raw trailer block (Decision:/Learning:/
# Gotcha:, unbolded) as the ABSOLUTE LAST block — placed after even the
# "🤖 Generated with" footer. Live-found in #575: any non-trailer line
# after the block empties `%(trailers)` under this repo's squash mode
# (squash_merge_commit_message = PR_BODY, so the PR body becomes the
# squash commit message verbatim).
#
# Also pins that git-memory SKILL.md's former "opt-in escape hatch"
# framing (SKILL.md:135-142) now points at the compose-pr.md mandate
# instead of calling `git log --grep` "the supported path" — a phrase
# that contradicts the O4 carrier-hierarchy doctrine (Task 1).
#
# Assertions scope to measured neighborhoods around each claim's anchor
# string, per docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md
# — a whole-file substring presence check goes false-green when a generic
# phrase pre-exists elsewhere in the file. Check 3 below is a deliberate
# WHOLE-FILE exception: the phrase "is the supported path" must be
# eradicated everywhere in SKILL.md, not just near the hatch.
#
# Usage:
#   bash dev-workflow/tests/test-git-memory-raw-footer-mandate.sh

set -u

DEV_WORKFLOW_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_PR_MD="$DEV_WORKFLOW_DIR/skills/git-memory/protocols/compose-pr.md"
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
# Check 1 — compose-pr.md's placement-rule neighborhood (Step 4, around
# compose-pr.md:90-101) requires the raw trailer footer as the absolute
# last block, after even the 🤖 footer, blank-line-separated.

WIN1="$(window_after "## Step 4" 60 "$COMPOSE_PR_MD")"
if [ -z "$WIN1" ]; then
  fail "anchor '## Step 4' not found in compose-pr.md"
elif ! echo "$WIN1" | grep -qF "raw trailer block"; then
  fail "compose-pr.md Step 4 neighborhood missing 'raw trailer block'"
elif ! echo "$WIN1" | grep -qF "absolute last block"; then
  fail "compose-pr.md Step 4 neighborhood missing 'absolute last block'"
elif ! echo "$WIN1" | grep -qF "after even the"; then
  fail "compose-pr.md Step 4 neighborhood missing 'after even the' (footer ordering)"
elif ! echo "$WIN1" | grep -qF "blank-line-separated"; then
  fail "compose-pr.md Step 4 neighborhood missing 'blank-line-separated'"
elif ! echo "$WIN1" | grep -qF "%(trailers)"; then
  fail "compose-pr.md Step 4 neighborhood missing '%(trailers)' mechanism reference"
else
  pass "compose-pr.md Step 4 neighborhood pins the raw-trailer-footer mandate"
fi

# -------------------------------------------------------------------------
# Check 2 — compose-pr.md includes a worked before/after example showing
# a non-trailer line after the block emptying %(trailers) vs. the correct
# absolute-last-block form.

WIN2="$(window_after "## Step 4" 90 "$COMPOSE_PR_MD")"
if [ -z "$WIN2" ]; then
  fail "anchor '## Step 4' not found in compose-pr.md (check 2)"
elif ! echo "$WIN2" | grep -qiF "Worked example"; then
  fail "compose-pr.md Step 4 neighborhood missing a 'Worked example' heading"
elif ! echo "$WIN2" | grep -qiF "parses empty"; then
  fail "compose-pr.md Step 4 neighborhood missing the 'parses empty' broken-case label"
elif ! echo "$WIN2" | grep -qiF "true last block"; then
  fail "compose-pr.md Step 4 neighborhood missing the 'true last block' correct-case label"
else
  pass "compose-pr.md Step 4 neighborhood includes a worked before/after example"
fi

# -------------------------------------------------------------------------
# Check 3 — git-memory SKILL.md's former opt-in-hatch neighborhood now
# points at the compose-pr.md mandate instead of framing git log --grep
# as the supported path. Anchor on stable prose immediately BEFORE the
# hatch paragraph (untouched by this task) so the window reliably spans
# into the rewritten paragraph.

WIN3="$(window_after "This verification is **enforced as an executable gate by" 20 "$SKILL_MD")"
if [ -z "$WIN3" ]; then
  fail "anchor 'This verification is **enforced as an executable gate by' not found in SKILL.md"
elif ! echo "$WIN3" | grep -qF "protocols/compose-pr.md"; then
  fail "SKILL.md hatch neighborhood does not point at protocols/compose-pr.md"
elif ! echo "$WIN3" | grep -qiF "mandate"; then
  fail "SKILL.md hatch neighborhood does not frame the footer as a mandate"
else
  pass "SKILL.md hatch neighborhood points at the compose-pr.md mandate"
fi

# -------------------------------------------------------------------------
# Check 4 — WHOLE-FILE absence assertion: "is the supported path" must be
# eradicated everywhere in SKILL.md (🔴 finding from Task 1's
# code-quality-reviewer verdict — it contradicts the O4 top-of-file
# carrier-hierarchy doctrine). The phrase can wrap across a markdown line
# break, so join the whole file into one space-separated string before
# the substring check (a raw per-line grep misses the wrapped case).

SKILL_JOINED="$(tr '\n' ' ' < "$SKILL_MD")"
if echo "$SKILL_JOINED" | grep -qF "is the supported path"; then
  fail "'is the supported path' still present somewhere in SKILL.md"
else
  pass "'is the supported path' absent from the whole of SKILL.md"
fi

# -------------------------------------------------------------------------
# Check 5 — the "Squash-merge caveat" neighborhood (SKILL.md:95-112, caveat
# paragraph + capture-location table) must point at the O2 mandate as the
# escape from the caveat, not just assert '%(trailers) is unreliable' in
# isolation — a top-to-bottom reader would otherwise form the wrong model
# before reaching the mandate paragraph at :135-146. Window scoped after
# the "Squash-merge caveat" anchor so it spans both the caveat blockquote
# and the table below it.

WIN5="$(window_after "Squash-merge caveat" 20 "$SKILL_MD")"
if [ -z "$WIN5" ]; then
  fail "anchor 'Squash-merge caveat' not found in SKILL.md"
elif ! echo "$WIN5" | grep -qF "mandated escape"; then
  fail "SKILL.md caveat neighborhood missing 'mandated escape' pointer to the O2 mandate"
elif ! echo "$WIN5" | grep -qF "parses correctly even on squash"; then
  fail "SKILL.md caveat neighborhood missing the squash-main parse-works escape clause"
elif ! echo "$WIN5" | grep -qF "once the PR body ends with the mandated raw trailer footer"; then
  fail "SKILL.md capture-location table missing the mandate pointer in the squash-merge row"
else
  pass "SKILL.md caveat + table neighborhood points at the O2 mandate as the escape"
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
