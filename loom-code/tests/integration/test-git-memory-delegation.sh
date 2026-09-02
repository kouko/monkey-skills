#!/usr/bin/env bash
# test-git-memory-delegation.sh
#
# Verify loom-code's ship station invokes loom-workflow:git-memory and
# carries the memory in both carriers (commit trailer + PR body).
#
# Repointed at loom-code 1.0: the subject moved from
# finishing-a-development-branch to skills/ship. The checks tied to the old
# document's shape (the ROADMAP P3-D Q-lock, the numbered "Step 6", the
# compose-pr.md pointer) are dropped with that shape; the delegation, the
# verify gate and the two carriers are what survived and are checked here.
#
# Usage:
#   bash loom-code/tests/integration/test-git-memory-delegation.sh

set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SHIP_SKILL="${REPO_ROOT}/loom-code/skills/ship/SKILL.md"
GIT_MEMORY_SKILL="${REPO_ROOT}/loom-workflow/skills/git-memory/SKILL.md"

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }
skip() { echo "SKIP — $1"; SKIP_COUNT=$((SKIP_COUNT + 1)); }

# -------------------------------------------------------------------------
# Check 1 — offline: the ship station references git-memory

if [ ! -f "${SHIP_SKILL}" ]; then
  fail "ship/SKILL.md not found"
  exit 1
fi

if grep -q "loom-workflow:git-memory" "${SHIP_SKILL}"; then
  pass "ship references loom-workflow:git-memory"
else
  fail "ship does NOT reference loom-workflow:git-memory"
fi

# -------------------------------------------------------------------------
# Check 3b — offline: F4 commit-carrier verify gate present
# After the close-out commit, finishing must run memory-grep.sh --verify HEAD
# and STOP a memory-worthy branch whose commit carrier is empty (exit 4).

if grep -- '--verify' "${SHIP_SKILL}" >/dev/null; then
  pass "ship names the --verify commit-carrier gate (F4)"
else
  fail "ship does NOT name the --verify commit-carrier gate — memory-worthy branch can ship with an empty commit carrier (#445 leak)"
fi

# The station may NOT reach into loom-workflow's file tree (the plugins
# install independently), so it carries its own post-merge carrier check
# and names the sibling skill for installs that have it.
if grep -qE "git log -1 --format=%B[^|]*\\| *grep -E '\\^\\(Decision" "${SHIP_SKILL}"; then
  pass "ship carries its own inline post-merge carrier grep"
else
  fail "ship has NO inline carrier check — a loom-code-only install would verify nothing"
fi

# -------------------------------------------------------------------------
# Check 3c — offline: F4 PR-carrier check present
# At PR creation, finishing must confirm the PR body carries a ## Memory section
# for a memory-worthy branch.

if grep -- '## Memory' "${SHIP_SKILL}" >/dev/null; then
  pass "ship names the PR ## Memory carrier check (F4)"
else
  fail "ship does NOT name the PR ## Memory carrier check — PR-carrier half of both-carrier policy missing"
fi

# -------------------------------------------------------------------------
# Check 3d — offline: the PR body carries BOTH carriers, not just `## Memory`.
# A PR can pass the `## Memory`-only check while dropping the raw trailer
# footer that the post-merge grep actually reads (the #575 failure class).

if grep -qi 'raw trailer footer' "${SHIP_SKILL}"; then
  pass "ship names the raw trailer footer as the PR body's last block"
else
  fail "ship does NOT name the raw trailer footer — a PR can pass with ## Memory present but the footer missing/broken (the #575 failure class)"
fi

# -------------------------------------------------------------------------
# Check 3e — offline: F4 PR-carrier check gives an inline discriminator for
# what a raw trailer block LOOKS like, so a context-blind executor can judge
# without opening another file. A context-blind haiku run rejected a valid
# single-line `Decision: …` last block as "prose" because Step 11's text
# never states the shape (the #576 finding). "single such line qualifies"
# is the minimal pinned phrase for the fix.

if grep -qi 'single such line qualifies' "${SHIP_SKILL}"; then
  pass "PR-carrier check names the inline raw-trailer-block discriminator"
else
  fail "PR-carrier check does NOT define what a raw trailer block looks like inline — a context-blind executor must guess (the #576 failure class)"
fi

# -------------------------------------------------------------------------
# Check 4 — prerequisite: loom-workflow:git-memory installed

if [ -f "${GIT_MEMORY_SKILL}" ]; then
  pass "git-memory skill exists in loom-workflow plugin"
else
  fail "git-memory SKILL.md not found at ${GIT_MEMORY_SKILL}"
fi

if command -v claude >/dev/null 2>&1; then
  # `claude plugin list` is multi-line per plugin; use -A 3 to capture Status
  if claude plugin list 2>&1 | grep -A 3 "[❯>] loom-workflow" | grep -q "Status: ✔ enabled"; then
    pass "loom-workflow plugin enabled (git-memory dispatchable)"
  else
    fail "loom-workflow plugin not enabled — git-memory delegation will fail"
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

  1. cd to a repo with a non-trivial branch whose branch-end checkpoint
     has returned PASS and whose blind-run report exists — it should
     have enough commits to warrant memory trailers
  2. claude
  3. Prompt: "finish this branch"
  4. Expected agent behavior:
     - Skill(loom-code:ship) auto-loads
     - Step 1 recomputes the preconditions and step 2 presents the
       blind-run report for acceptance
     - Step 3 EXPLICITLY invokes loom-workflow:git-memory (transcript
       should show "Skill(loom-workflow:git-memory) → Successfully
       loaded skill" before the trailers are drafted)
     - The amended review-only commit carries git-memory's trailers
       (Decision: / Learning: / Gotcha: as warranted)

  5. PASS if the transcript shows the step-3 git-memory invocation BEFORE
     the trailers are finalized. FAIL if they are drafted without it.
EOF
exit 0
