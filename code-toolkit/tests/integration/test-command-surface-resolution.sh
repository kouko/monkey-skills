#!/usr/bin/env bash
# test-command-surface-resolution.sh
#
# Assertion harness for the Command Surface v1 prose-edit feature.
# Greps five edit targets for canonical rule phrases introduced by Tasks 2-6.
#
# Contract: each CHECK group is independent. On failure it prints
#   MISSING: <check-id>  <reason>
# and increments FAILURES. Exits 1 if any failures, else exits 0.
#
# This is READ-ONLY — no mutations, no trap/restore needed.
#
# Usage:
#   bash code-toolkit/tests/integration/test-command-surface-resolution.sh

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

# -------------------------------------------------------------------------
# Preflight: target files we probe must exist (except the pressure prompt
# which is what CHECK-PRESSURE tests for existence of).

VBC_REF="${REPO_ROOT}/code-toolkit/skills/verification-before-completion/references/test-invocation-by-stack.md"
VBC_SKILL="${REPO_ROOT}/code-toolkit/skills/verification-before-completion/SKILL.md"
SDD_SKILL="${REPO_ROOT}/code-toolkit/skills/subagent-driven-development/SKILL.md"
IMPLEMENTER="${REPO_ROOT}/code-toolkit/agents/implementer.md"
PRESSURE_PROMPT="${REPO_ROOT}/code-toolkit/tests/verification-before-completion-pressure/prompts/declared-surface-vs-detection.txt"
PRESSURE_INDEX="${REPO_ROOT}/code-toolkit/tests/verification-before-completion-pressure/prompts/index.md"

[ -f "${VBC_REF}" ]    || die "VBC reference file not found: ${VBC_REF}"
[ -f "${VBC_SKILL}" ]  || die "VBC SKILL.md not found: ${VBC_SKILL}"
[ -f "${SDD_SKILL}" ]  || die "SDD SKILL.md not found: ${SDD_SKILL}"
[ -f "${IMPLEMENTER}" ] || die "implementer.md not found: ${IMPLEMENTER}"

# -------------------------------------------------------------------------
# CHECK-① — test-invocation-by-stack.md must contain BOTH phrases.

if ! grep -qF 'consult the project-declared surface first' "${VBC_REF}"; then
  missing "CHECK-①" "phrase 'consult the project-declared surface first' absent from test-invocation-by-stack.md"
elif ! grep -qF 'only if it runs and emits a test count' "${VBC_REF}"; then
  missing "CHECK-①" "phrase 'only if it runs and emits a test count' absent from test-invocation-by-stack.md"
else
  ok "CHECK-①  both phrases present in test-invocation-by-stack.md"
fi

# -------------------------------------------------------------------------
# CHECK-② — verification-before-completion/SKILL.md must contain BOTH phrases.

if ! grep -qF 'Resolve the test command' "${VBC_SKILL}"; then
  missing "CHECK-②" "phrase 'Resolve the test command' absent from verification-before-completion/SKILL.md"
elif ! grep -qF 'declared-first' "${VBC_SKILL}"; then
  missing "CHECK-②" "phrase 'declared-first' absent from verification-before-completion/SKILL.md"
else
  ok "CHECK-②  both phrases present in verification-before-completion/SKILL.md"
fi

# -------------------------------------------------------------------------
# CHECK-③a — subagent-driven-development/SKILL.md must contain BOTH phrases.

if ! grep -qF 'Resolved test command' "${SDD_SKILL}"; then
  missing "CHECK-③a" "phrase 'Resolved test command' absent from subagent-driven-development/SKILL.md"
elif ! grep -qF 'session-scoped' "${SDD_SKILL}"; then
  missing "CHECK-③a" "phrase 'session-scoped' absent from subagent-driven-development/SKILL.md"
else
  ok "CHECK-③a  both phrases present in subagent-driven-development/SKILL.md"
fi

# -------------------------------------------------------------------------
# CHECK-③b — agents/implementer.md must contain the phrase.

if ! grep -qF 'Resolved test command' "${IMPLEMENTER}"; then
  missing "CHECK-③b" "phrase 'Resolved test command' absent from agents/implementer.md"
else
  ok "CHECK-③b  phrase present in agents/implementer.md"
fi

# -------------------------------------------------------------------------
# CHECK-PRESSURE — pressure prompt file must exist AND index.md must reference it.

if ! test -f "${PRESSURE_PROMPT}"; then
  missing "CHECK-PRESSURE" "file declared-surface-vs-detection.txt does not exist"
elif ! test -f "${PRESSURE_INDEX}"; then
  missing "CHECK-PRESSURE" "index.md does not exist in pressure prompts dir"
elif ! grep -qF 'declared-surface-vs-detection' "${PRESSURE_INDEX}"; then
  missing "CHECK-PRESSURE" "phrase 'declared-surface-vs-detection' absent from pressure prompts index.md"
else
  ok "CHECK-PRESSURE  pressure prompt file exists and index.md references it"
fi

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
