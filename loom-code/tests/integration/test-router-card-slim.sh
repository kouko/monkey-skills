#!/usr/bin/env bash
# test-router-card-slim.sh
#
# Verify the SessionStart hook injects the slim router card
# (hooks/router-card.md), NOT the full using-loom-code SKILL.md body.
# The card must stay small (pre-invocation cost), keep every
# load-bearing token (mandate + five rules + SUBAGENT-STOP), and drop
# full-body-only sections (those load via the Skill tool on invocation).
#
# Per docs/loom/plans/2026-07-06-loom-code-router-card-slim.md.
#
# Usage:
#   bash loom-code/tests/integration/test-router-card-slim.sh

set -u

PLUGIN_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK_SCRIPT="${PLUGIN_ROOT}/hooks/session-start"

PASS_COUNT=0
FAIL_COUNT=0

pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# -------------------------------------------------------------------------
# Check 1 — hook script exists + executable

if [ -x "${HOOK_SCRIPT}" ]; then
  pass "hook script exists + executable"
else
  fail "hook script not executable or missing"
  exit 1
fi

# -------------------------------------------------------------------------
# Check 2 — injected context is slim: 1000 < len < 3500 chars

unset LOOM_CODE_MODE
CTX="$("${HOOK_SCRIPT}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
sys.stdout.write(d.get('hookSpecificOutput', {}).get('additionalContext', ''))
")"
CTX_LEN=${#CTX}

if [ "${CTX_LEN}" -gt 1000 ] && [ "${CTX_LEN}" -lt 3500 ]; then
  pass "injected context is slim (${CTX_LEN} chars, expected 1000-3500)"
else
  fail "injected context is ${CTX_LEN} chars (expected 1000-3500 per TECH-SPEC ~600-token budget — bloat or empty)"
fi

# -------------------------------------------------------------------------
# Check 3 — load-bearing tokens survive the cut

for token in \
  "SUBAGENT-STOP" \
  "Brainstorm before implementing" \
  "TDD is the iron law" \
  "subagent-driven-development" \
  "Never push without review" \
  "Research before asking" \
  "using-loom-code"
do
  if printf '%s' "${CTX}" | grep -qF "${token}"; then
    pass "load-bearing token present: ${token}"
  else
    fail "load-bearing token MISSING: ${token}"
  fi
done

# -------------------------------------------------------------------------
# Check 4 — full-body-only sections are NOT injected

for marker in \
  "Skill priority — decision order" \
  "## Continuous mode" \
  "## Red flags" \
  "## Coexistence"
do
  if printf '%s' "${CTX}" | grep -qF "${marker}"; then
    fail "full-body marker leaked into card: ${marker}"
  else
    pass "full-body marker absent: ${marker}"
  fi
done

# -------------------------------------------------------------------------
# Check 5 — 3-key emission shape preserved (canonical + 2 defensive)

KEYS_OK="$("${HOOK_SCRIPT}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
a = d.get('hookSpecificOutput', {}).get('additionalContext', '')
b = d.get('additional_context', '')
c = d.get('additionalContext', '')
print('ok' if (a and a == b == c) else 'bad')
")"

if [ "${KEYS_OK}" = "ok" ]; then
  pass "3-key shape preserved (canonical + additional_context + additionalContext, identical)"
else
  fail "3-key shape broken"
fi

# -------------------------------------------------------------------------
echo
echo "Results: ${PASS_COUNT} passed, ${FAIL_COUNT} failed"
[ "${FAIL_COUNT}" -eq 0 ] || exit 1
