#!/usr/bin/env bash
# test-superpowers-mode-off.sh
#
# Verify LOOM_CODE_MODE=off escape hatch — loom-code's hook
# silently exits with empty context, so users running obra/superpowers
# can disable loom-code's injection without uninstalling.
#
# Per PRODUCT-SPEC §5.6 obra/superpowers coexistence contract +
# Phase 1.5 P15-1 (LOOM_CODE_MODE escape, shipped Phase 1 commit
# 9cba15c).
#
# Usage:
#   bash loom-code/tests/integration/test-superpowers-mode-off.sh

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
# Check 1 — hook script exists

if [ ! -x "${HOOK_SCRIPT}" ]; then
  fail "hook script not executable or missing"
  exit 1
fi

# -------------------------------------------------------------------------
# Check 2 — with LOOM_CODE_MODE=off, hook emits EMPTY additionalContext

OFF_OUTPUT=$(LOOM_CODE_MODE=off "${HOOK_SCRIPT}")

if [ -z "${OFF_OUTPUT}" ]; then
  fail "LOOM_CODE_MODE=off → hook emitted EMPTY output (should emit empty-context JSON, not empty)"
  exit 1
fi

OFF_CTX_LEN=$(echo "${OFF_OUTPUT}" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    ctx = d.get('hookSpecificOutput', {}).get('additionalContext', '')
    print(len(ctx))
except Exception as e:
    print(-1)
")

if [ "${OFF_CTX_LEN}" -eq 0 ]; then
  pass "LOOM_CODE_MODE=off → hook emits valid JSON with empty additionalContext"
elif [ "${OFF_CTX_LEN}" -eq -1 ]; then
  fail "LOOM_CODE_MODE=off → hook output not valid JSON"
else
  fail "LOOM_CODE_MODE=off → hook emitted ${OFF_CTX_LEN} chars (expected 0)"
fi

# -------------------------------------------------------------------------
# Check 3 — OFF mode also emits required hookEventName key (per Phase 1.5 fix)

OFF_HEN=$(echo "${OFF_OUTPUT}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('hookSpecificOutput', {}).get('hookEventName', '__missing__'))
")

if [ "${OFF_HEN}" = "SessionStart" ]; then
  pass "LOOM_CODE_MODE=off → hook output includes hookEventName=SessionStart (per v0.1.0 hook spec fix)"
else
  fail "LOOM_CODE_MODE=off → hookEventName missing or wrong: ${OFF_HEN}"
fi

# -------------------------------------------------------------------------
# Check 4 — OFF mode emits all 3 portable keys (Codex/legacy compat)

OFF_KEY_CHECK=$(echo "${OFF_OUTPUT}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
keys_present = []
if 'additional_context' in d:
    keys_present.append('additional_context')
if 'additionalContext' in d:
    keys_present.append('additionalContext')
if 'hookSpecificOutput' in d:
    keys_present.append('hookSpecificOutput.additionalContext')
print(','.join(sorted(keys_present)))
")

EXPECTED="additionalContext,additional_context,hookSpecificOutput.additionalContext"
if [ "${OFF_KEY_CHECK}" = "${EXPECTED}" ]; then
  pass "OFF mode emits all 3 portable keys (Claude Code + Codex + legacy)"
else
  fail "OFF mode missing portable keys. Got: ${OFF_KEY_CHECK}; Expected: ${EXPECTED}"
fi

# -------------------------------------------------------------------------
# Check 5 — verify with mode unset, hook DOES emit non-empty context (sanity)

unset LOOM_CODE_MODE
DEFAULT_CTX_LEN=$(echo "${HOOK_OUTPUT:-$("${HOOK_SCRIPT}")}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(len(d.get('hookSpecificOutput', {}).get('additionalContext', '')))
" 2>/dev/null || echo "0")
# Fallback if HOOK_OUTPUT not set
if [ -z "${DEFAULT_CTX_LEN}" ] || [ "${DEFAULT_CTX_LEN}" -eq 0 ]; then
  DEFAULT_CTX_LEN=$("${HOOK_SCRIPT}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(len(d.get('hookSpecificOutput', {}).get('additionalContext', '')))
")
fi

if [ "${DEFAULT_CTX_LEN}" -gt 1000 ]; then
  pass "Sanity: LOOM_CODE_MODE unset → ${DEFAULT_CTX_LEN} chars (escape hatch only fires when explicitly =off)"
else
  fail "Sanity check failed — default mode should emit >1000 chars"
fi

# -------------------------------------------------------------------------
# Check 6 — P15-9: superpowers enablement prereq for live verification

if command -v claude >/dev/null 2>&1; then
  if claude plugin list 2>&1 | grep -q "superpowers"; then
    if claude plugin list 2>&1 | grep -A 3 "[❯>] superpowers" | grep -q "Status: ✔ enabled"; then
      pass "obra/superpowers plugin enabled (live OFF-mode verification possible)"
    else
      skip "obra/superpowers installed but NOT enabled in user settings"
      skip "  → OFF-mode escape-hatch behavior verified OFFLINE (above) — "
      skip "    loom-code hook correctly emits empty context when var set."
      skip "  → Live verification (superpowers ALONE fires after LOOM_CODE_MODE=off)"
      skip "    deferred until user runs: claude plugin enable superpowers"
      skip "  → Not a loom-code defect — test prerequisite gap (P15-9)."
    fi
  else
    skip "obra/superpowers not installed — live OFF-mode verification N/A"
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

Offline checks PASSED. Live verification (manual, requires obra/
superpowers installed alongside loom-code):

  1. Open new shell + set escape var:
     export LOOM_CODE_MODE=off

  2. cd to a repo + claude   # fresh session
     - Look at session-start output
     - Expected: NO loom-code router injection (silent — no
       <EXTREMELY_IMPORTANT>loom-code</EXTREMELY_IMPORTANT> block)
     - Expected: obra/superpowers content STILL injects (only
       loom-code muted)

  3. Test prompt: "what skills are available?"
     - Expected: superpowers' 11 skills listed; loom-code's 10
       skills NOT listed (or marked as disabled in this session)

  4. Unset to restore:
     unset LOOM_CODE_MODE
     claude   # fresh session — both plugins fire again

  5. PASS if:
     - With LOOM_CODE_MODE=off: only superpowers active
     - With unset: both active
     - Toggle is reversible without uninstalling either plugin
EOF
exit 0
