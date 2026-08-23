#!/usr/bin/env bash
# test-bba-description.sh
#
# Pins the brief-before-asking SKILL.md frontmatter `description:` block:
# it must keep summarizing all FIVE reactive signals, not just the three
# named originally (question / explanation / stakes). #599 added two more
# body-level signals — the check-question guard (body ~:81-92) and the
# repeated-confusion meta-trigger (body ~:79) — but the description never
# picked them up, so they were undiscoverable from the one-line summary
# skill-routing reads. This is a description-summary gap fix, not a new
# mechanism: the existing "lost on the question, the explanation, or the
# stakes" clause must survive verbatim alongside the addition.
#
# Usage:
#   bash loom-workflow/tests/test-bba-description.sh

set -u

SKILL="$(cd "$(dirname "$0")/.." && pwd)/skills/brief-before-asking/SKILL.md"

PASS_COUNT=0
FAIL_COUNT=0
pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

if [ ! -f "$SKILL" ]; then
  echo "FAIL — SKILL.md not found at $SKILL"
  exit 1
fi

# Extract the YAML frontmatter block (between the first two '---' lines),
# which contains the `description: |` block scalar.
FRONTMATTER="$(awk '/^---$/{c++; next} c==1{print}' "$SKILL")"

has()  { printf '%s' "$1" | grep -qi "$2"; }

# ── existing reactive-clause wording must survive verbatim ─────────
has "$FRONTMATTER" "lost on the question, the explanation, or the stakes" \
  && pass "original reactive clause (question/explanation/stakes) preserved" \
  || fail "original reactive clause must not be dropped"

# ── new: check-question guard summarized ───────────────────────────
has "$FRONTMATTER" "check-question" \
  && pass "description summarizes the check-question guard" \
  || fail "description should mention the check-question guard"

# ── new: repeated-confusion meta-trigger summarized ─────────────────
has "$FRONTMATTER" "repeated-confusion\|repeated confusion" \
  && pass "description summarizes the repeated-confusion meta-trigger" \
  || fail "description should mention the repeated-confusion meta-trigger"

echo ""
echo "================================================================"
echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
echo "================================================================"
[ "${FAIL_COUNT}" -gt 0 ] && exit 1
exit 0
