#!/usr/bin/env bash
# test-loom-memory-charter-pins.sh
#
# Pins the O4b carrier-hierarchy doctrine in docs/loom/memory/README.md
# (the loom memory charter): anchored at the jurisdiction table, the charter
# must carry the same pinned hierarchy sentence as git-memory SKILL.md
# (dev-workflow/tests/test-git-memory-carrier-doctrine.sh) — the committed
# file store is the authoritative durable carrier; commit trailers
# ("Decision bound to a commit -> git-memory trailers" row) are commit-bound
# capture, best-effort/secondary, never the retrieval path a durable lesson
# depends on. Without this, the charter's jurisdiction row reads as if
# trailers were a durable home, contradicting git-memory's own doctrine.
#
# Assertions scope to the measured neighborhood around the jurisdiction
# table anchor, per
# docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md — a
# whole-file substring presence check goes false-green when a generic
# phrase pre-exists elsewhere in the file (e.g. this README's intro already
# says "this folder is the durable truth").
#
# Usage:
#   bash dev-workflow/tests/test-loom-memory-charter-pins.sh

set -u

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
README="${REPO_ROOT}/docs/loom/memory/README.md"

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
# Check 1 — pinned carrier-hierarchy sentence present in the neighborhood
# of the jurisdiction table (transcribed VERBATIM per the plan's ## Notes
# pinned wording — same pin git-memory SKILL.md carries).

WIN1="$(window_after "## Charter — jurisdiction" 20 "$README")"
if [ -z "$WIN1" ]; then
  fail "anchor '## Charter — jurisdiction' not found in README.md"
elif echo "$WIN1" | grep -qF "the authoritative carrier" \
  && echo "$WIN1" | grep -qF "commit-bound capture: best-effort, secondary" \
  && echo "$WIN1" | grep -qF "never the retrieval path"; then
  pass "pinned carrier-hierarchy sentence present near jurisdiction table"
else
  fail "pinned carrier-hierarchy sentence missing near jurisdiction table"
fi

# -------------------------------------------------------------------------
# Check 2 — pinned contradiction-check sentence present in the neighborhood
# of the "## When to record" section (transcribed VERBATIM per the plan's
# ## Notes pinned wording — same pin loom-memory SKILL.md record step 2
# carries).

WIN2="$(window_after "## When to record" 20 "$README")"
if [ -z "$WIN2" ]; then
  fail "anchor '## When to record' not found in README.md"
elif echo "$WIN2" | grep -qF "grep the store for entries the new fact contradicts" \
  && echo "$WIN2" | grep -qF "update or replace that entry" \
  && echo "$WIN2" | grep -qF "never add a contradicting sibling"; then
  pass "pinned contradiction-check sentence present near When-to-record section"
else
  fail "pinned contradiction-check sentence missing near When-to-record section"
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
