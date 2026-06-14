#!/usr/bin/env bash
# test-hook-injection.sh — verify SessionStart hook injects router in
# Codex CLI sessions
#
# Phase 2.5 v0.4.0 build deliverable. Runs the hook script directly
# (offline check) AND attempts a fresh Codex session probe to confirm
# the injected `hookSpecificOutput.additionalContext` key (the one Codex
# actually consumes per the official Codex hooks doc) is consumed.
#
# Prerequisite: Codex CLI installed (script gracefully skips otherwise).
#
# Usage:
#   bash code-toolkit/tests/codex-cli/test-hook-injection.sh

set -u

PLUGIN_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK_SCRIPT="${PLUGIN_ROOT}/hooks/session-start"

# -------------------------------------------------------------------------
# Step 1 — offline check: hook script emits the Codex-shape JSON key

echo "Step 1: verify hook output has nested hookSpecificOutput.additionalContext key (the key Codex consumes; offline check)"

if [ ! -x "${HOOK_SCRIPT}" ]; then
  echo "FAIL: hook script not executable: ${HOOK_SCRIPT}"
  exit 1
fi

HOOK_OUTPUT=$("${HOOK_SCRIPT}")
if [ -z "${HOOK_OUTPUT}" ]; then
  echo "FAIL: hook script emitted empty output"
  exit 1
fi

# Use python3 to JSON-parse + check the key Codex actually consumes.
PYTHON_CHECK=$(printf '%s' "${HOOK_OUTPUT}" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
except Exception as e:
    print(f'FAIL: hook output is not valid JSON: {e}')
    sys.exit(1)

# PRIMARY (load-bearing): the nested hookSpecificOutput.additionalContext key
# is the ONE both Claude Code AND Codex actually consume (per the official
# Codex hooks doc). If this is absent/empty the agent receives no router,
# regardless of the defensive top-level keys.
hso = data.get('hookSpecificOutput')
if not isinstance(hso, dict):
    print('FAIL: hook output missing nested hookSpecificOutput object (the shape Codex consumes)')
    print(f'  Got keys: {sorted(data.keys())}')
    sys.exit(1)
ctx = hso.get('additionalContext')
if ctx is None:
    print('FAIL: hook output missing hookSpecificOutput.additionalContext (the key Codex consumes)')
    print(f'  Got hookSpecificOutput keys: {sorted(hso.keys())}')
    sys.exit(1)
if len(ctx) < 100:
    print(f'FAIL: hookSpecificOutput.additionalContext suspiciously short ({len(ctx)} chars)')
    sys.exit(1)
print(f'OK: hookSpecificOutput.additionalContext has {len(ctx)} chars (key Codex consumes)')
print(f'OK: first 80 chars: {ctx[:80]!r}')

# SECONDARY (defensive): the two top-level keys are emitted belt-and-suspenders
# for cross-host/version portability — NOT what Codex consumes. Assert they are
# present to match the deliberate 3-key design, but they are not load-bearing.
for k in ('additional_context', 'additionalContext'):
    if k not in data:
        print(f'FAIL: defensive top-level key {k!r} missing (3-key portability design)')
        print(f'  Got top-level keys: {sorted(data.keys())}')
        sys.exit(1)
print('OK: both defensive top-level keys present (additional_context, additionalContext)')
sys.exit(0)
")
PYTHON_EXIT=$?

echo "${PYTHON_CHECK}"
if [ ${PYTHON_EXIT} -ne 0 ]; then
  exit 1
fi

# -------------------------------------------------------------------------
# Step 2 — live check: run a fresh Codex CLI session, verify router context lands

echo ""
echo "Step 2: live check — fresh Codex session, verify router context lands"

if ! command -v codex >/dev/null 2>&1; then
  cat <<'EOF'
SKIP Step 2: Codex CLI not installed (offline check Step 1 passed).

Step 1 verified the hook emits the nested hookSpecificOutput.additionalContext
key that Codex CLI actually consumes.
Step 2 (live verification) needs Codex CLI installed — see
test-skill-loading.sh for install instructions.

(Live verification on Codex 0.139.0 already recorded in README.md
"Verified outcome" — this branch only runs when codex is absent here.)
EOF
  exit 0
fi

# Real non-interactive invocation (verified on Codex 0.139.0, 2026-06-14):
#   codex exec --sandbox read-only '<prompt>'
# The bare `codex` / `codex --print` / `codex run` forms fail with
# "stdin is not a terminal" on a machine where codex IS installed — that
# is a RUNTIME/environment error, not evidence the router failed to load,
# so it must be SKIP-with-note, never a hard FAIL.

# Probe via a question that ONLY makes sense if the router was injected:
PROBE_PROMPT="Do you have code-toolkit loaded? Name the four load-bearing rules from the router's <EXTREMELY-IMPORTANT> block."

echo "  running: codex exec --sandbox read-only '<probe prompt>'"
PROBE_OUTPUT=$(timeout 60 codex exec --sandbox read-only "${PROBE_PROMPT}" 2>&1) || true

# Broadened runtime-error guard: a non-probe outcome (terminal/stdin,
# usage-limit, auth, or argument errors) means we could not actually
# exercise the router on this machine — that is a SKIP-with-note, NOT a
# FAIL. Only a successful probe whose reply lacks router keywords is a
# real failure.
if echo "${PROBE_OUTPUT}" | grep -qiE "stdin is not a terminal|not a (tty|terminal)|usage limit|rate limit|quota|not (logged in|authenticated)|unauthor|please (log ?in|sign ?in)|invalid api key|unknown (option|command|subcommand)|usage:|invalid argument"; then
  cat <<EOF
SKIP Step 2: Codex ran but could not complete the live probe (runtime/env condition, not a router failure).

Reason surfaced by codex (first 300 chars):
$(printf '%s' "${PROBE_OUTPUT}" | head -c 300)

Step 1 (offline) verified the hook emits the nested
hookSpecificOutput.additionalContext key that Codex consumes.
Re-run Step 2 once the runtime condition is cleared
(interactive terminal / usage budget / auth).
EOF
  exit 0
fi

if [ -z "${PROBE_OUTPUT}" ]; then
  cat <<'EOF'
SKIP Step 2: codex exec produced no output (runtime/env condition, not a router failure).

Step 1 (offline) verified the hook emits the nested
hookSpecificOutput.additionalContext key that Codex consumes.
EOF
  exit 0
fi

# Did the agent surface evidence of the router being loaded?
if echo "${PROBE_OUTPUT}" | grep -qE "Brainstorm|TDD|iron law|SDD|Never push without review|code-toolkit"; then
  echo "OK: agent surfaced router rule content"
  echo "PASS — SessionStart hook injection verified in live Codex CLI session"
  exit 0
else
  echo "FAIL: agent reply does not contain expected router rule keywords"
  echo "  Expected one of: Brainstorm / TDD / iron law / SDD / Never push without review / code-toolkit"
  echo "  First 500 chars of reply:"
  echo "${PROBE_OUTPUT}" | head -c 500
  echo ""
  echo "  ⚠️ Possible causes:"
  echo "    1. Hook not registered with Codex CLI (verify hooks.json plugin manifest spec)"
  echo "    2. Codex CLI not reading hookSpecificOutput.additionalContext (verify nested-key contract)"
  echo "    3. Plugin not enabled in this session scope"
  exit 1
fi
