#!/usr/bin/env bash
# test-command-surface-accretion.sh
#
# Assertion harness for the Command Surface v2 (accretion) prose-edit feature.
# Greps four edit targets for canonical rule phrases introduced by Tasks 2-5.
#
# Contract: each CHECK group is independent. On failure it prints
#   MISSING: <check-id>  <reason>
# and increments FAILURES. Exits 1 if any failures, else exits 0.
#
# This is READ-ONLY — no mutations, no trap/restore needed.
#
# Usage:
#   bash code-toolkit/tests/integration/test-command-surface-accretion.sh

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
# Preflight: stable anchor files that must already exist.

SDD_SKILL="${REPO_ROOT}/code-toolkit/skills/subagent-driven-development/SKILL.md"
IMPLEMENTER="${REPO_ROOT}/code-toolkit/agents/implementer.md"
PLAN_SKILL="${REPO_ROOT}/code-toolkit/skills/writing-plans/SKILL.md"
PRESSURE_INDEX="${REPO_ROOT}/code-toolkit/tests/verification-before-completion-pressure/prompts/index.md"

[ -f "${SDD_SKILL}" ]    || die "SDD SKILL.md not found: ${SDD_SKILL}"
[ -f "${IMPLEMENTER}" ]  || die "implementer.md not found: ${IMPLEMENTER}"
[ -f "${PLAN_SKILL}" ]   || die "writing-plans SKILL.md not found: ${PLAN_SKILL}"

# -------------------------------------------------------------------------
# CHECK-ACCRETE-SDD — subagent-driven-development/SKILL.md must contain BOTH phrases.

if ! grep -qF 'new runnable capability' "${SDD_SKILL}"; then
  missing "CHECK-ACCRETE-SDD" "phrase 'new runnable capability' absent from subagent-driven-development/SKILL.md"
elif ! grep -qF 'accretion' "${SDD_SKILL}"; then
  missing "CHECK-ACCRETE-SDD" "phrase 'accretion' absent from subagent-driven-development/SKILL.md"
else
  ok "CHECK-ACCRETE-SDD  both phrases present in subagent-driven-development/SKILL.md"
fi

# -------------------------------------------------------------------------
# CHECK-ACCRETE-IMPL — agents/implementer.md must contain BOTH phrases.

if ! grep -qF 'verify-before-declare' "${IMPLEMENTER}"; then
  missing "CHECK-ACCRETE-IMPL" "phrase 'verify-before-declare' absent from agents/implementer.md"
elif ! grep -qF 'BEGIN command-surface (managed)' "${IMPLEMENTER}"; then
  missing "CHECK-ACCRETE-IMPL" "phrase 'BEGIN command-surface (managed)' absent from agents/implementer.md"
else
  ok "CHECK-ACCRETE-IMPL  both phrases present in agents/implementer.md"
fi

# -------------------------------------------------------------------------
# CHECK-ACCRETE-PLAN — writing-plans/SKILL.md must contain the phrase.

if ! grep -qF 'runnable capability' "${PLAN_SKILL}"; then
  missing "CHECK-ACCRETE-PLAN" "phrase 'runnable capability' absent from writing-plans/SKILL.md"
else
  ok "CHECK-ACCRETE-PLAN  phrase present in writing-plans/SKILL.md"
fi

# -------------------------------------------------------------------------
# CHECK-ACCRETE-PRESSURE — pressure prompt file must exist AND index.md must reference it.

PRESSURE_PROMPT="${REPO_ROOT}/code-toolkit/tests/verification-before-completion-pressure/prompts/accretion-declare-new-verb.txt"

if ! test -f "${PRESSURE_PROMPT}"; then
  missing "CHECK-ACCRETE-PRESSURE" "file accretion-declare-new-verb.txt does not exist"
elif ! test -f "${PRESSURE_INDEX}"; then
  missing "CHECK-ACCRETE-PRESSURE" "index.md does not exist in pressure prompts dir"
elif ! grep -qF 'accretion-declare-new-verb' "${PRESSURE_INDEX}"; then
  missing "CHECK-ACCRETE-PRESSURE" "phrase 'accretion-declare-new-verb' absent from pressure prompts index.md"
else
  ok "CHECK-ACCRETE-PRESSURE  pressure prompt file exists and index.md references it"
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
