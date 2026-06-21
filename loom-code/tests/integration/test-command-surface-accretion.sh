#!/usr/bin/env bash
# test-command-surface-accretion.sh
#
# Assertion harness for the Command Surface v2 (accretion) prose-edit feature.
# Greps four edit targets for canonical rule phrases introduced by Tasks 2-5.
#
# Contract: each CHECK group is independent. On failure it prints
#   MISSING: <check-id>  <reason>
# for EVERY absent phrase (not just the first) and increments FAILURES.
# Exits 1 if any failures, else exits 0.
#
# This is READ-ONLY — no mutations, no trap/restore needed.
#
# Usage:
#   bash loom-code/tests/integration/test-command-surface-accretion.sh

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
# Reports a MISSING line if <phrase> is absent. Returns nonzero on absence
# so callers OR-accumulate a per-check result WITHOUT an if/elif short-circuit
# that would hide a second absent phrase in one run.
require_phrase() {
  local check_id="$1" phrase="$2" file="$3" label="$4"
  if ! grep -qF "${phrase}" "${file}"; then
    missing "${check_id}" "phrase '${phrase}' absent from ${label}"
    return 1
  fi
  return 0
}

# -------------------------------------------------------------------------
# Preflight: stable anchor files that must already exist.

SDD_SKILL="${REPO_ROOT}/loom-code/skills/subagent-driven-development/SKILL.md"
IMPLEMENTER="${REPO_ROOT}/loom-code/agents/implementer.md"
PLAN_SKILL="${REPO_ROOT}/loom-code/skills/writing-plans/SKILL.md"
PRESSURE_INDEX="${REPO_ROOT}/loom-code/tests/verification-before-completion-pressure/prompts/index.md"

[ -f "${SDD_SKILL}" ]    || die "SDD SKILL.md not found: ${SDD_SKILL}"
[ -f "${IMPLEMENTER}" ]  || die "implementer.md not found: ${IMPLEMENTER}"
[ -f "${PLAN_SKILL}" ]   || die "writing-plans SKILL.md not found: ${PLAN_SKILL}"

# -------------------------------------------------------------------------
# CHECK-ACCRETE-SDD — subagent-driven-development/SKILL.md must contain BOTH phrases.

c_sdd=0
require_phrase "CHECK-ACCRETE-SDD" 'new runnable capability' "${SDD_SKILL}" "subagent-driven-development/SKILL.md" || c_sdd=1
require_phrase "CHECK-ACCRETE-SDD" 'accretion' "${SDD_SKILL}" "subagent-driven-development/SKILL.md" || c_sdd=1
if [ "${c_sdd}" -eq 0 ]; then ok "CHECK-ACCRETE-SDD  both phrases present in subagent-driven-development/SKILL.md"; fi

# -------------------------------------------------------------------------
# CHECK-ACCRETE-IMPL — agents/implementer.md must contain BOTH phrases.

c_impl=0
require_phrase "CHECK-ACCRETE-IMPL" 'verify-before-declare' "${IMPLEMENTER}" "agents/implementer.md" || c_impl=1
require_phrase "CHECK-ACCRETE-IMPL" 'BEGIN command-surface (managed)' "${IMPLEMENTER}" "agents/implementer.md" || c_impl=1
if [ "${c_impl}" -eq 0 ]; then ok "CHECK-ACCRETE-IMPL  both phrases present in agents/implementer.md"; fi

# -------------------------------------------------------------------------
# CHECK-ACCRETE-PLAN — writing-plans/SKILL.md must contain the phrase.

c_plan=0
require_phrase "CHECK-ACCRETE-PLAN" 'runnable capability' "${PLAN_SKILL}" "writing-plans/SKILL.md" || c_plan=1
if [ "${c_plan}" -eq 0 ]; then ok "CHECK-ACCRETE-PLAN  phrase present in writing-plans/SKILL.md"; fi

# -------------------------------------------------------------------------
# CHECK-ACCRETE-PRESSURE — pressure prompt file must exist AND index.md must reference it.

PRESSURE_PROMPT="${REPO_ROOT}/loom-code/tests/verification-before-completion-pressure/prompts/accretion-declare-new-verb.txt"

cp=0
if ! test -f "${PRESSURE_PROMPT}"; then
  missing "CHECK-ACCRETE-PRESSURE" "file accretion-declare-new-verb.txt does not exist"; cp=1
fi
if ! test -f "${PRESSURE_INDEX}"; then
  missing "CHECK-ACCRETE-PRESSURE" "index.md does not exist in pressure prompts dir"; cp=1
elif ! grep -qF 'accretion-declare-new-verb' "${PRESSURE_INDEX}"; then
  missing "CHECK-ACCRETE-PRESSURE" "phrase 'accretion-declare-new-verb' absent from pressure prompts index.md"; cp=1
fi
if [ "${cp}" -eq 0 ]; then ok "CHECK-ACCRETE-PRESSURE  pressure prompt file exists and index.md references it"; fi

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
