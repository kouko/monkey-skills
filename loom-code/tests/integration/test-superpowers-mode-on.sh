#!/usr/bin/env bash
# test-superpowers-mode-on.sh
#
# Verify loom-code + obra/superpowers coexistence when
# LOOM_CODE_MODE is unset or "on" — both plugins' SessionStart
# hooks fire; user picks which to use via slash command / Skill tool.
#
# Per PRODUCT-SPEC §5.6 obra/superpowers coexistence contract.
#
# Usage:
#   bash loom-code/tests/integration/test-superpowers-mode-on.sh

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
# Check 2 — with LOOM_CODE_MODE unset, hook injects router context

unset LOOM_CODE_MODE
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
  pass "LOOM_CODE_MODE unset → hook injects ${CTX_LEN} chars (router fires)"
else
  fail "LOOM_CODE_MODE unset → hook injected ${CTX_LEN} chars (expected >1000)"
fi

# -------------------------------------------------------------------------
# Check 3 — with LOOM_CODE_MODE=on, same behavior (alias for default)

CTX_LEN_ON=$(LOOM_CODE_MODE=on "${HOOK_SCRIPT}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(len(d.get('hookSpecificOutput', {}).get('additionalContext', '')))
")

if [ "${CTX_LEN_ON}" -eq "${CTX_LEN}" ]; then
  pass "LOOM_CODE_MODE=on emits same content as unset (${CTX_LEN_ON} chars)"
else
  fail "LOOM_CODE_MODE=on emits ${CTX_LEN_ON} chars but unset emits ${CTX_LEN} — inconsistency"
fi

# -------------------------------------------------------------------------
# Check 4 — prerequisite: obra/superpowers installed (optional)

if command -v claude >/dev/null 2>&1; then
  if claude plugin list 2>&1 | grep -q "superpowers"; then
    pass "obra/superpowers plugin installed"
    # P15-9 — distinguish installed vs enabled. Live coexistence test needs
    # superpowers ENABLED in the user's session scope, not just installed
    # at the marketplace level.
    if claude plugin list 2>&1 | grep -A 3 "[❯>] superpowers" | grep -q "Status: ✔ enabled"; then
      pass "obra/superpowers plugin enabled (live coexistence verification possible)"
    else
      skip "obra/superpowers installed but NOT enabled in user settings"
      skip "  → Live coexistence verification deferred until user runs:"
      skip "    claude plugin enable superpowers"
      skip "  → Until then, offline checks (above) establish the structural"
      skip "    coexistence contract but the active-session behavior remains"
      skip "    unverified. Not a loom-code defect — test prerequisite gap."
    fi
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
with BOTH loom-code + obra/superpowers installed):

  1. Ensure both plugins installed + enabled:
     claude plugin install loom-code@monkey-skills    # if not already
     claude plugin install superpowers                   # obra marketplace
     unset LOOM_CODE_MODE     # or set to "on"

  2. claude   # fresh session
  3. Inspect session-start output (look for hook error if any):
     - Expected: NO hook error
     - Expected: agent has BOTH loom-code router + superpowers content
       loaded (both injected via SessionStart)

  4. Test prompt: "what skills do you have?"
     - Expected: both loom-code (11 skills) + superpowers (~13 skills)
       discoverable
     - Skill-name collisions (brainstorming, writing-plans, etc.) — user
       must use plugin-scoped form: Skill(loom-code:brainstorming)
       vs Skill(superpowers:brainstorming)

  5. PASS if both plugins inject hook content without error + skill
     lists discoverable. Run test-superpowers-mode-off.sh for the
     escape-hatch verification.
EOF
exit 0
