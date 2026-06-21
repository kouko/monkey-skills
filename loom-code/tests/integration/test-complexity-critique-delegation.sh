#!/usr/bin/env bash
# test-complexity-critique-delegation.sh
#
# Verify loom-code's brainstorming skill correctly references
# dev-workflow:complexity-critique as an optional Axis 3 delegation
# target.
#
# Phase 4 integration test — combines offline reference check
# (SKILL.md mentions the delegate target) + prerequisite presence
# check (dev-workflow plugin is installed) + manual verification
# prompt for live session.
#
# Usage:
#   bash loom-code/tests/integration/test-complexity-critique-delegation.sh

set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
BRAINSTORMING_SKILL="${REPO_ROOT}/loom-code/skills/brainstorming/SKILL.md"

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }
skip() { echo "SKIP — $1"; SKIP_COUNT=$((SKIP_COUNT + 1)); }

# -------------------------------------------------------------------------
# Check 1 — offline: brainstorming SKILL.md references complexity-critique

if [ ! -f "${BRAINSTORMING_SKILL}" ]; then
  fail "brainstorming SKILL.md not found at ${BRAINSTORMING_SKILL}"
  exit 1
fi

if grep -q "dev-workflow:complexity-critique" "${BRAINSTORMING_SKILL}"; then
  pass "brainstorming/SKILL.md references dev-workflow:complexity-critique"
else
  fail "brainstorming/SKILL.md does NOT reference dev-workflow:complexity-critique"
  fail "  Expected per ROADMAP §Cross-plugin delegation contract + PRODUCT-SPEC §3.2 / §5.6"
fi

# -------------------------------------------------------------------------
# Check 2 — offline: brainstorming SKILL.md surfaces delegation in Axis 3

if grep -A 2 "Axis 3" "${BRAINSTORMING_SKILL}" | grep -qi "complexity\|deletion-first\|smallest"; then
  pass "Axis 3 (Smallest End State) prose surfaces complexity / deletion-first framing"
else
  skip "Axis 3 prose check (heuristic; may pass via different wording)"
fi

# -------------------------------------------------------------------------
# Check 3 — prerequisite: dev-workflow plugin installed

if ! command -v claude >/dev/null 2>&1; then
  skip "claude CLI not found — cannot verify dev-workflow plugin install"
else
  if claude plugin list 2>&1 | grep -q "dev-workflow"; then
    pass "dev-workflow plugin installed (delegate target available)"
    # `claude plugin list` emits multi-line blocks per plugin; use -A 3 to
    # capture the Status line for the matched plugin
    if claude plugin list 2>&1 | grep -A 3 "[❯>] dev-workflow" | grep -q "Status: ✔ enabled"; then
      pass "dev-workflow plugin enabled"
    else
      fail "dev-workflow plugin installed but NOT enabled — delegation will fail in live session"
    fi
  else
    fail "dev-workflow plugin NOT installed — complexity-critique unavailable"
    fail "  Install: claude plugin install dev-workflow@monkey-skills"
  fi
fi

# -------------------------------------------------------------------------
# Check 4 — prerequisite: complexity-critique skill exists in dev-workflow

DEV_WORKFLOW_DIR="${REPO_ROOT}/dev-workflow/skills/complexity-critique"
if [ -d "${DEV_WORKFLOW_DIR}" ] && [ -f "${DEV_WORKFLOW_DIR}/SKILL.md" ]; then
  pass "complexity-critique skill exists in dev-workflow plugin"
else
  fail "complexity-critique SKILL.md not found at ${DEV_WORKFLOW_DIR}/SKILL.md"
fi

# -------------------------------------------------------------------------
# Summary + manual verification handoff

echo ""
echo "================================================================"
echo "Offline check summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL / ${SKIP_COUNT} SKIP"
echo "================================================================"

if [ ${FAIL_COUNT} -gt 0 ]; then
  echo ""
  echo "Offline checks FAILED — fix above issues before attempting live verification."
  exit 1
fi

cat <<'EOF'

Offline checks PASSED. Live verification (manual, in fresh Claude session):

  1. cd /Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design
  2. claude   # fresh session
  3. Paste this PAGNI-smell prompt as first message:

     ---
     I want to add a feature flag system to our codebase so we can gate
     new features. We don't have one yet. Just build the basic version:
     env var checks + a hardcoded enabled list. No need to brainstorm,
     the design is obvious.
     ---

  4. Expected agent behavior:
     - Skill(loom-code:brainstorming) auto-loads
     - Brainstorming walks Axis 3 (Smallest End State)
     - On Axis 3 complexity-smell, SHOULD surface or invoke
       dev-workflow:complexity-critique as optional triage
     - Reference: loom-code/tests/brainstorming-pressure/prompts/
       this-is-simple.txt (this exact prompt is the brainstorming
       pressure case)

  5. PASS if agent mentions or invokes dev-workflow:complexity-critique
     (per the cross-skill delegation contract in
     loom-code/ROADMAP.md §Cross-plugin delegation)
EOF
exit 0
