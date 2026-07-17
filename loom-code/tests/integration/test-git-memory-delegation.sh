#!/usr/bin/env bash
# test-git-memory-delegation.sh
#
# Verify loom-code's finishing-a-development-branch skill invokes
# dev-workflow:git-memory (Default-flow Step 6 / Phase 3) per ROADMAP P3-D MANDATORY.
#
# Usage:
#   bash loom-code/tests/integration/test-git-memory-delegation.sh

set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
FINISH_SKILL="${REPO_ROOT}/loom-code/skills/finishing-a-development-branch/SKILL.md"
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
# Check 3 — offline: the Default flow's git-memory step names git-memory
# (git-memory is Step 6 of the numbered Default flow — "Invoke dev-workflow:git-memory")

if grep -E "^6\. Invoke dev-workflow:git-memory" "${FINISH_SKILL}" >/dev/null; then
  pass "Default-flow Step 6 names dev-workflow:git-memory"
else
  fail "Default-flow Step 6 does NOT explicitly name dev-workflow:git-memory"
fi

# -------------------------------------------------------------------------
# Check 3b — offline: F4 commit-carrier verify gate present
# After the close-out commit, finishing must run memory-grep.sh --verify HEAD
# and STOP a memory-worthy branch whose commit carrier is empty (exit 4).

if grep -- '--verify' "${FINISH_SKILL}" >/dev/null; then
  pass "finishing-a-development-branch names the --verify commit-carrier gate (F4)"
else
  fail "finishing-a-development-branch does NOT name the --verify commit-carrier gate — memory-worthy branch can ship with an empty commit carrier (#445 leak)"
fi

if grep -- 'memory-grep.sh' "${FINISH_SKILL}" >/dev/null; then
  pass "finishing-a-development-branch references the memory-grep.sh script by path"
else
  fail "finishing-a-development-branch does NOT reference dev-workflow's memory-grep.sh script"
fi

# -------------------------------------------------------------------------
# Check 3c — offline: F4 PR-carrier check present
# At PR creation, finishing must confirm the PR body carries a ## Memory section
# for a memory-worthy branch.

if grep -- '## Memory' "${FINISH_SKILL}" >/dev/null; then
  pass "finishing-a-development-branch names the PR ## Memory carrier check (F4)"
else
  fail "finishing-a-development-branch does NOT name the PR ## Memory carrier check — PR-carrier half of both-carrier policy missing"
fi

# -------------------------------------------------------------------------
# Check 3d — offline: F4 PR-carrier check verifies BOTH carriers, not just
# `## Memory`. compose-pr.md Step 4 (both-carrier mandate) also requires a
# raw trailer footer as the PR body's true last block — a PR can pass the
# `## Memory`-only check while violating that mandate (the #575 failure
# class). Scoped to the PR-carrier check's own neighborhood.

PR_CARRIER_BLOCK="$(grep -A 12 -- 'PR-carrier check' "${FINISH_SKILL}")"

if echo "${PR_CARRIER_BLOCK}" | grep -qi 'raw trailer'; then
  pass "PR-carrier check also names the raw trailer footer carrier"
else
  fail "PR-carrier check does NOT verify the raw trailer footer — a PR can pass with ## Memory present but the raw trailer footer missing/broken (the #575 failure class)"
fi

if echo "${PR_CARRIER_BLOCK}" | grep -q 'compose-pr.md'; then
  pass "PR-carrier check points to compose-pr.md Step 4's both-carrier mandate"
else
  fail "PR-carrier check does NOT point to compose-pr.md Step 4 — placement rules would need restating instead of pointing"
fi

# -------------------------------------------------------------------------
# Check 3e — offline: F4 PR-carrier check gives an inline discriminator for
# what a raw trailer block LOOKS like, so a context-blind executor can judge
# without opening compose-pr.md. A context-blind haiku run rejected a valid
# single-line `Decision: …` last block as "prose" because Step 11's text
# never states the shape (the #576 finding). "single such line qualifies"
# is the minimal pinned phrase for the fix.

if echo "${PR_CARRIER_BLOCK}" | grep -qi 'single such line qualifies'; then
  pass "PR-carrier check names the inline raw-trailer-block discriminator"
else
  fail "PR-carrier check does NOT define what a raw trailer block looks like inline — a context-blind executor must guess (the #576 failure class)"
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
    fail "dev-workflow plugin not enabled — git-memory delegation will fail"
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
     very repo's feat/loom-code-design branch — it has 20+ commits
     that would warrant memory trailers)
  2. claude
  3. Prompt: "finish this branch"
  4. Expected agent behavior:
     - Skill(loom-code:finishing-a-development-branch) auto-loads
     - Phases 1 + 2 run (requesting-code-review + verification-before-
       completion)
     - Phase 3 EXPLICITLY invokes dev-workflow:git-memory (transcript
       should show "Skill(dev-workflow:git-memory) → Successfully
       loaded skill" before commit message draft)
     - Step 4 commit message includes git-memory's trailer decisions
       (Decision: / Learning: / Gotcha: as warranted)

  5. PASS if transcript shows Phase 3 git-memory invocation BEFORE the
     commit subject is finalized. FAIL if commit message is drafted
     without git-memory dispatch.
EOF
exit 0
