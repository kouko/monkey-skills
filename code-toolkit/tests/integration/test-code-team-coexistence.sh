#!/usr/bin/env bash
# test-code-team-coexistence.sh
#
# Verify code-toolkit + domain-teams:code-team coexist without conflict.
# Per PRODUCT-SPEC §Q2 (passive code-team retained) + §4.3 (parallel use).
#
# Usage:
#   bash code-toolkit/tests/integration/test-code-team-coexistence.sh

set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
CODE_TOOLKIT_SKILLS="${REPO_ROOT}/code-toolkit/skills"
CODE_TEAM_SKILL="${REPO_ROOT}/domain-teams/skills/code-team/SKILL.md"

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }
skip() { echo "SKIP — $1"; SKIP_COUNT=$((SKIP_COUNT + 1)); }

# -------------------------------------------------------------------------
# Check 1 — both plugins exist

if [ -f "${CODE_TEAM_SKILL}" ]; then
  pass "code-team SKILL.md exists in domain-teams plugin"
else
  fail "code-team SKILL.md not found at ${CODE_TEAM_SKILL}"
fi

if [ -d "${CODE_TOOLKIT_SKILLS}" ]; then
  pass "code-toolkit/skills/ directory exists"
else
  fail "code-toolkit/skills/ not found"
  exit 1
fi

# -------------------------------------------------------------------------
# Check 2 — no skill-name collisions between code-toolkit and code-team

CT_SKILLS=$(ls -d "${CODE_TOOLKIT_SKILLS}"/*/ 2>/dev/null | xargs -n1 basename | sort)
CODE_TEAM_NAME="code-team"

collision=0
for ct_skill in ${CT_SKILLS}; do
  if [ "${ct_skill}" = "${CODE_TEAM_NAME}" ]; then
    fail "skill-name collision: ${ct_skill} exists in both plugins"
    collision=1
  fi
done

if [ ${collision} -eq 0 ]; then
  pass "no skill-name collision between code-toolkit and code-team"
fi

# -------------------------------------------------------------------------
# Check 3 — SSOT-and-functional-copy mechanism intact

if [ -f "${REPO_ROOT}/code-toolkit/scripts/verify-drift.py" ]; then
  # Python script; executable bit not required (invoked via python3)
  if python3 "${REPO_ROOT}/code-toolkit/scripts/verify-drift.py" >/dev/null 2>&1; then
    pass "verify-drift.py: all functional copies byte-identical to canonical"
  else
    fail "verify-drift.py reports drift between code-toolkit functional copies and code-team canonical"
  fi
else
  skip "verify-drift.py not found"
fi

# -------------------------------------------------------------------------
# Check 4 — coexistence framing in code-toolkit SKILL.md files

USING_SKILL="${CODE_TOOLKIT_SKILLS}/using-code-toolkit/SKILL.md"
if grep -q "code-team" "${USING_SKILL}" && grep -qi "coexist\|並存\|passive gate" "${USING_SKILL}"; then
  pass "using-code-toolkit/SKILL.md surfaces code-team coexistence framing"
else
  fail "using-code-toolkit/SKILL.md missing code-team coexistence framing"
fi

# -------------------------------------------------------------------------
# Check 5 — both plugins discoverable in Claude CLI

if command -v claude >/dev/null 2>&1; then
  # `claude plugin list` is multi-line per plugin; use -A 3 to capture Status
  if claude plugin list 2>&1 | grep -A 3 "[❯>] domain-teams" | grep -q "Status: ✔ enabled"; then
    pass "domain-teams plugin enabled in Claude CLI"
  else
    fail "domain-teams plugin not enabled — passive-gate use case unavailable"
  fi
  if claude plugin list 2>&1 | grep -A 3 "[❯>] code-toolkit" | grep -q "Status: ✔ enabled"; then
    pass "code-toolkit plugin enabled in Claude CLI"
  else
    skip "code-toolkit not enabled in user-level CLI (may be local-scope only)"
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

  1. claude   # fresh session with both plugins enabled
  2. Verify both skill families surface in router list:
     - Skill(code-toolkit:tdd-iron-law) — should load successfully
     - Skill(domain-teams:code-team) — should load successfully
  3. Run a hybrid prompt that exercises BOTH:

     ---
     I have an existing src/services/payment_processor.py (200 LOC,
     no tests). Use domain-teams:code-team to audit it for compliance,
     then if PASS, use code-toolkit's tdd-iron-law to add test coverage
     under Feathers (2004) characterization-test approach.
     ---

  4. Expected behavior:
     - Agent loads domain-teams:code-team for the audit (passive gate)
     - On code-team PASS, agent routes to code-toolkit's tdd-iron-law
       (active construction)
     - Both skills used in same session without conflict
     - Per PRODUCT-SPEC §Q2: "code-team 並存 — code-toolkit 主動建構
       入口，code-team 被動 gate 入口"

  5. PASS if both skills load + execute their respective roles without
     deadlock / collision / contradiction.
EOF
exit 0
