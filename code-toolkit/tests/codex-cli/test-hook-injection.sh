#!/usr/bin/env bash
# test-hook-injection.sh — verify SessionStart hook injects router in
# Codex CLI sessions
#
# Phase 2.5 v0.4.0 build deliverable. Runs the hook script directly
# (offline check) AND attempts a fresh Codex session probe to confirm
# the injected `additional_context` key is actually consumed.
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

echo "Step 1: verify hook output has 'additional_context' top-level key (offline check)"

if [ ! -x "${HOOK_SCRIPT}" ]; then
  echo "FAIL: hook script not executable: ${HOOK_SCRIPT}"
  exit 1
fi

HOOK_OUTPUT=$("${HOOK_SCRIPT}")
if [ -z "${HOOK_OUTPUT}" ]; then
  echo "FAIL: hook script emitted empty output"
  exit 1
fi

# Use python3 to JSON-parse + check for the Codex-shape key
PYTHON_CHECK=$(printf '%s' "${HOOK_OUTPUT}" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
except Exception as e:
    print(f'FAIL: hook output is not valid JSON: {e}')
    sys.exit(1)

# Codex CLI consumes the top-level 'additional_context' key
ctx = data.get('additional_context')
if ctx is None:
    print('FAIL: hook output missing top-level additional_context key (Codex CLI shape)')
    print(f'  Got keys: {sorted(data.keys())}')
    sys.exit(1)
if len(ctx) < 100:
    print(f'FAIL: additional_context suspiciously short ({len(ctx)} chars)')
    sys.exit(1)
print(f'OK: additional_context has {len(ctx)} chars')
print(f'OK: first 80 chars: {ctx[:80]!r}')
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

Step 1 verified the hook script emits the right JSON shape for Codex CLI.
Step 2 (live verification) needs Codex CLI installed — see
test-skill-loading.sh for install instructions.

Phase 2.5 BUILD complete; live verification ritual deferred.
EOF
  exit 0
fi

# ⚠️ TBD verify exact Codex CLI invocation for "non-interactive prompt".
# The Claude Code analogue is `claude --print --max-turns 1`. Codex CLI's
# equivalent might be `codex --print`, `codex run`, `codex exec`, etc.

# Attempt to probe via a question that ONLY makes sense if router was injected:
PROBE_PROMPT="Do you have code-toolkit loaded? Name the four load-bearing rules from the router's <EXTREMELY-IMPORTANT> block."

# Try common Codex CLI invocation patterns
PROBE_OUTPUT=""
for codex_cmd in "codex --print --max-turns 1" "codex run" "codex"; do
  echo "  trying: ${codex_cmd}"
  result=$(printf '%s\n' "${PROBE_PROMPT}" | timeout 30 ${codex_cmd} 2>&1) || true
  if [ -n "${result}" ] && ! echo "${result}" | grep -qi "unknown\|usage\|invalid"; then
    PROBE_OUTPUT="${result}"
    break
  fi
done

if [ -z "${PROBE_OUTPUT}" ]; then
  echo "FAIL: could not find a working Codex CLI invocation for non-interactive prompt"
  echo "  ⚠️ verify Codex CLI's --print equivalent + update this script"
  exit 1
fi

# Did the agent surface evidence of the router being loaded?
if echo "${PROBE_OUTPUT}" | grep -qE "Brainstorm|TDD|iron law|SDD|Never push without review"; then
  echo "OK: agent surfaced router rule content"
  echo "PASS — SessionStart hook injection verified in live Codex CLI session"
  exit 0
else
  echo "FAIL: agent reply does not contain expected router rule keywords"
  echo "  Expected one of: Brainstorm / TDD / iron law / SDD / Never push without review"
  echo "  First 500 chars of reply:"
  echo "${PROBE_OUTPUT}" | head -c 500
  echo ""
  echo "  ⚠️ Possible causes:"
  echo "    1. Hook not registered with Codex CLI (verify hooks.json plugin manifest spec)"
  echo "    2. Codex CLI ignores 'additional_context' key (use different key name?)"
  echo "    3. Plugin not enabled in this session scope"
  exit 1
fi
