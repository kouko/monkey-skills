#!/usr/bin/env bash
# test-command-surface-resolution.sh
#
# Assertion harness for the Command Surface v1 prose-edit feature.
# Greps five edit targets for canonical rule phrases introduced by Tasks 2-6.
#
# Contract: each CHECK group is independent. On failure it prints
#   MISSING: <check-id>  <reason>
# for EVERY absent phrase (not just the first) and increments FAILURES.
# Exits 1 if any failures, else exits 0.
#
# This is READ-ONLY — no mutations, no trap/restore needed.
#
# Usage:
#   bash loom-code/tests/integration/test-command-surface-resolution.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

FAILURES=0

die() {
  echo "FAIL — $1" >&2
  exit 1
}

missing() {
  local check_id="$1"
  local reason="$2"
  echo "MISSING: ${check_id}  ${reason}"
  FAILURES=$(( FAILURES + 1 ))
}

ok() {
  echo "ok — $1"
}

# require_phrase <check-id> <phrase> <file> <file-label>
# Reports a MISSING line if <phrase> is absent from <file>. Returns nonzero
# on absence so callers can OR-accumulate a per-check result WITHOUT the
# if/elif short-circuit that would hide a second absent phrase in one run.
require_phrase() {
  local check_id="$1" phrase="$2" file="$3" label="$4"
  if ! grep -qF "${phrase}" "${file}"; then
    missing "${check_id}" "phrase '${phrase}' absent from ${label}"
    return 1
  fi
  return 0
}

# -------------------------------------------------------------------------
# Preflight: target files we probe must exist (except the pressure prompt
# which is what CHECK-PRESSURE tests for existence of).

VBC_REF="${REPO_ROOT}/loom-code/skills/verification-before-completion/references/test-invocation-by-stack.md"
VBC_SKILL="${REPO_ROOT}/loom-code/skills/verification-before-completion/SKILL.md"
SDD_SKILL="${REPO_ROOT}/loom-code/skills/subagent-driven-development/SKILL.md"
IMPLEMENTER="${REPO_ROOT}/loom-code/agents/implementer.md"
PRESSURE_PROMPT="${REPO_ROOT}/loom-code/tests/verification-before-completion-pressure/prompts/declared-surface-vs-detection.txt"
PRESSURE_INDEX="${REPO_ROOT}/loom-code/tests/verification-before-completion-pressure/prompts/index.md"

[ -f "${VBC_REF}" ]    || die "VBC reference file not found: ${VBC_REF}"
[ -f "${VBC_SKILL}" ]  || die "VBC SKILL.md not found: ${VBC_SKILL}"
[ -f "${SDD_SKILL}" ]  || die "SDD SKILL.md not found: ${SDD_SKILL}"
[ -f "${IMPLEMENTER}" ] || die "implementer.md not found: ${IMPLEMENTER}"

# -------------------------------------------------------------------------
# CHECK-① — test-invocation-by-stack.md must contain BOTH phrases.

c1=0
require_phrase "CHECK-①" 'consult the project-declared surface first' "${VBC_REF}" "test-invocation-by-stack.md" || c1=1
require_phrase "CHECK-①" 'only if it runs and emits a test count' "${VBC_REF}" "test-invocation-by-stack.md" || c1=1
if [ "${c1}" -eq 0 ]; then ok "CHECK-①  both phrases present in test-invocation-by-stack.md"; fi

# -------------------------------------------------------------------------
# CHECK-② — verification-before-completion/SKILL.md must contain BOTH phrases.

c2=0
require_phrase "CHECK-②" 'Resolve the test command' "${VBC_SKILL}" "verification-before-completion/SKILL.md" || c2=1
require_phrase "CHECK-②" 'declared-first' "${VBC_SKILL}" "verification-before-completion/SKILL.md" || c2=1
if [ "${c2}" -eq 0 ]; then ok "CHECK-②  both phrases present in verification-before-completion/SKILL.md"; fi

# -------------------------------------------------------------------------
# CHECK-③a — subagent-driven-development/SKILL.md must contain BOTH phrases.

c3a=0
require_phrase "CHECK-③a" 'Resolved test command' "${SDD_SKILL}" "subagent-driven-development/SKILL.md" || c3a=1
require_phrase "CHECK-③a" 'session-scoped' "${SDD_SKILL}" "subagent-driven-development/SKILL.md" || c3a=1
if [ "${c3a}" -eq 0 ]; then ok "CHECK-③a  both phrases present in subagent-driven-development/SKILL.md"; fi

# -------------------------------------------------------------------------
# CHECK-③b — agents/implementer.md must contain the phrase.

c3b=0
require_phrase "CHECK-③b" 'Resolved test command' "${IMPLEMENTER}" "agents/implementer.md" || c3b=1
if [ "${c3b}" -eq 0 ]; then ok "CHECK-③b  phrase present in agents/implementer.md"; fi

# -------------------------------------------------------------------------
# CHECK-PRESSURE — pressure prompt file must exist AND index.md must reference it.

cp=0
if ! test -f "${PRESSURE_PROMPT}"; then
  missing "CHECK-PRESSURE" "file declared-surface-vs-detection.txt does not exist"; cp=1
fi
if ! test -f "${PRESSURE_INDEX}"; then
  missing "CHECK-PRESSURE" "index.md does not exist in pressure prompts dir"; cp=1
elif ! grep -qF 'declared-surface-vs-detection' "${PRESSURE_INDEX}"; then
  missing "CHECK-PRESSURE" "phrase 'declared-surface-vs-detection' absent from pressure prompts index.md"; cp=1
fi
if [ "${cp}" -eq 0 ]; then ok "CHECK-PRESSURE  pressure prompt file exists and index.md references it"; fi

# -------------------------------------------------------------------------
# Summary

echo ""
if [ "${FAILURES}" -gt 0 ]; then
  echo "RESULT: ${FAILURES} check(s) MISSING — edit tasks must fill these gaps"
  exit 1
else
  echo "RESULT: all checks PASS"
  exit 0
fi
