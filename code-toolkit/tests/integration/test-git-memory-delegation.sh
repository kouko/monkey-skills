#!/usr/bin/env bash
# test-git-memory-delegation.sh
#
# Verify code-toolkit's finishing-a-development-branch skill invokes
# dev-workflow:git-memory at Step 3 per ROADMAP P3-D MANDATORY.
#
# Usage:
#   bash code-toolkit/tests/integration/test-git-memory-delegation.sh

set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
FINISH_SKILL="${REPO_ROOT}/code-toolkit/skills/finishing-a-development-branch/SKILL.md"
GIT_MEMORY_SKILL="${REPO_ROOT}/dev-workflow/skills/git-memory/SKILL.md"

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }
skip() { echo "SKIP — $1"; SKIP_COUNT=$((SKIP_COUNT + 1)); }

# -------------------------------------------------------------------------
# Check 1 — offline: finishing-a-development-branch references git-memory

if [ ! -f "${FINISH_SKILL}" ]; then
  fail "finishing-a-development-branch SKILL.md not found"
  exit 1
fi

if grep -q "dev-workflow:git-memory" "${FINISH_SKILL}"; then
  pass "finishing-a-development-branch references dev-workflow:git-memory"
else
  fail "finishing-a-development-branch does NOT reference dev-workflow:git-memory"
fi

# -------------------------------------------------------------------------
# Check 2 — offline: P3-D mandatory framing present

if grep -qE "P3-D|MANDATORY|mandatory" "${FINISH_SKILL}"; then
  pass "P3-D MANDATORY framing present in finishing-a-development-branch"
else
  fail "P3-D MANDATORY framing missing — git-memory delegation is supposed to be non-optional per ROADMAP §Phase 3 Q-lock"
fi

# -------------------------------------------------------------------------
# Check 3 — offline: Step 3 in 7-step flow is git-memory

if grep -E "Step 3.*git-memory|git-memory.*Step 3" "${FINISH_SKILL}" >/dev/null; then
  pass "Step 3 of the 7-step flow names git-memory"
else
  fail "Step 3 of the 7-step flow does NOT explicitly name git-memory"
fi

# -------------------------------------------------------------------------
# Check 4 — prerequisite: dev-workflow:git-memory installed

if [ -f "${GIT_MEMORY_SKILL}" ]; then
  pass "git-memory skill exists in dev-workflow plugin"
else
  fail "git-memory SKILL.md not found at ${GIT_MEMORY_SKILL}"
fi

if command -v claude >/dev/null 2>&1; then
  # `claude plugin list` is multi-line per plugin; use -A 3 to capture Status
  if claude plugin list 2>&1 | grep -A 3 "[❯>] dev-workflow" | grep -q "Status: ✔ enabled"; then
    pass "dev-workflow plugin enabled (git-memory dispatchable)"
  else
    fail "dev-workflow plugin not enabled — Step 3 delegation will fail"
  fi
else
  skip "claude CLI not found"
fi

# -------------------------------------------------------------------------
# Summary + manual verification handoff

echo ""
echo "================================================================"
echo "Offline check summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL / ${SKIP_COUNT} SKIP"
echo "================================================================"

if [ ${FAIL_COUNT} -gt 0 ]; then
  echo "Offline checks FAILED — fix before live verification."
  exit 1
fi

cat <<'EOF'

Offline checks PASSED. Live verification (manual, in fresh Claude session):

  1. cd to a repo with a non-trivial branch ready to close (e.g. this
     very repo's feat/code-toolkit-design branch — it has 20+ commits
     that would warrant memory trailers)
  2. claude
  3. Prompt: "finish this branch"
  4. Expected agent behavior:
     - Skill(code-toolkit:finishing-a-development-branch) auto-loads
     - Steps 1 + 2 run (requesting-code-review + verification-before-
       completion)
     - Step 3 EXPLICITLY invokes dev-workflow:git-memory (transcript
       should show "Skill(dev-workflow:git-memory) → Successfully
       loaded skill" before commit message draft)
     - Step 4 commit message includes git-memory's trailer decisions
       (Decision: / Learning: / Gotcha: as warranted)

  5. PASS if transcript shows Step 3 git-memory invocation BEFORE the
     commit subject is finalized. FAIL if commit message is drafted
     without git-memory dispatch.
EOF
exit 0
