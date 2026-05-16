#!/usr/bin/env bash
# test-superpowers-mode-on.sh
#
# Verify code-toolkit + obra/superpowers coexistence when
# CODE_TOOLKIT_MODE is unset or "on" — both plugins' SessionStart
# hooks fire; user picks which to use via slash command / Skill tool.
#
# Per PRODUCT-SPEC §5.6 obra/superpowers coexistence contract.
#
# Usage:
#   bash code-toolkit/tests/integration/test-superpowers-mode-on.sh

set -u

PLUGIN_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK_SCRIPT="${PLUGIN_ROOT}/hooks/session-start"

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }
skip() { echo "SKIP — $1"; SKIP_COUNT=$((SKIP_COUNT + 1)); }

# -------------------------------------------------------------------------
# Check 1 — hook script exists + executable

if [ -x "${HOOK_SCRIPT}" ]; then
  pass "hook script exists + executable: ${HOOK_SCRIPT}"
else
  fail "hook script not executable or missing"
  exit 1
fi

# -------------------------------------------------------------------------
# Check 2 — with CODE_TOOLKIT_MODE unset, hook injects router context

unset CODE_TOOLKIT_MODE
HOOK_OUTPUT=$("${HOOK_SCRIPT}")

CTX_LEN=$(echo "${HOOK_OUTPUT}" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    ctx = d.get('hookSpecificOutput', {}).get('additionalContext', '')
    print(len(ctx))
except Exception as e:
    print(0)
")

if [ "${CTX_LEN}" -gt 1000 ]; then
  pass "CODE_TOOLKIT_MODE unset → hook injects ${CTX_LEN} chars (router fires)"
else
  fail "CODE_TOOLKIT_MODE unset → hook injected ${CTX_LEN} chars (expected >1000)"
fi

# -------------------------------------------------------------------------
# Check 3 — with CODE_TOOLKIT_MODE=on, same behavior (alias for default)

CTX_LEN_ON=$(CODE_TOOLKIT_MODE=on "${HOOK_SCRIPT}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(len(d.get('hookSpecificOutput', {}).get('additionalContext', '')))
")

if [ "${CTX_LEN_ON}" -eq "${CTX_LEN}" ]; then
  pass "CODE_TOOLKIT_MODE=on emits same content as unset (${CTX_LEN_ON} chars)"
else
  fail "CODE_TOOLKIT_MODE=on emits ${CTX_LEN_ON} chars but unset emits ${CTX_LEN} — inconsistency"
fi

# -------------------------------------------------------------------------
# Check 4 — prerequisite: obra/superpowers installed (optional)

if command -v claude >/dev/null 2>&1; then
  if claude plugin list 2>&1 | grep -q "superpowers"; then
    pass "obra/superpowers plugin installed"
  else
    skip "obra/superpowers not installed — coexistence test mostly offline-only"
    skip "  Install: claude plugin install superpowers (via obra marketplace)"
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

Offline checks PASSED. Live verification (manual, in fresh Claude session
with BOTH code-toolkit + obra/superpowers installed):

  1. Ensure both plugins installed + enabled:
     claude plugin install code-toolkit@monkey-skills    # if not already
     claude plugin install superpowers                   # obra marketplace
     unset CODE_TOOLKIT_MODE     # or set to "on"

  2. claude   # fresh session
  3. Inspect session-start output (look for hook error if any):
     - Expected: NO hook error
     - Expected: agent has BOTH code-toolkit router + superpowers content
       loaded (both injected via SessionStart)

  4. Test prompt: "what skills do you have?"
     - Expected: both code-toolkit (10 skills) + superpowers (~11 skills)
       discoverable
     - Skill-name collisions (brainstorming, writing-plans, etc.) — user
       must use plugin-scoped form: Skill(code-toolkit:brainstorming)
       vs Skill(superpowers:brainstorming)

  5. PASS if both plugins inject hook content without error + skill
     lists discoverable. Run test-superpowers-mode-off.sh for the
     escape-hatch verification.
EOF
exit 0
