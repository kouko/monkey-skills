#!/usr/bin/env bash
# test-rule-sheet-drift.sh
#
# Verify the SSOT-and-functional-copy drift gate covers the rule-sheet
# injection block injected into routed agents (loom-code v0.9.0 inline
# rule-sheet feature).
#
# Contract under test:
#   - distribute.py writes the canonical rule-sheet between
#     <!-- BEGIN rule-sheet-v1 --> and <!-- END rule-sheet-v1 --> in every
#     routed agent file.
#   - verify-drift.py exits 0 when on-disk bytes match SSOT.
#   - verify-drift.py exits 1 with substring "INJECTION-DRIFT" + the
#     drifted agent's filename when the injected block is mutated.
#   - distribute.py is idempotent and restores canonical state.
#
# Usage:
#   bash loom-code/tests/integration/test-rule-sheet-drift.sh
#
# Leaves the working tree clean even if assertions fail (trap-based
# restore via distribute.py — SSOT regenerates canonical bytes).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DISTRIBUTE="${REPO_ROOT}/loom-code/scripts/distribute.py"
VERIFY_DRIFT="${REPO_ROOT}/loom-code/scripts/verify-drift.py"
TARGET_AGENT="${REPO_ROOT}/loom-code/agents/implementer.md"

# -------------------------------------------------------------------------
# Trap: always restore canonical state on exit (success or failure).
# distribute.py is the SSOT — running it regenerates the canonical block
# from loom-code/scripts/_rule-sheet.md, no backup file needed.

restore_canonical_state() {
  python3 "${DISTRIBUTE}" >/dev/null 2>&1 || true
}
trap restore_canonical_state EXIT

die() {
  echo "FAIL — $1" >&2
  exit 1
}

# -------------------------------------------------------------------------
# Preflight: required files present.

[ -f "${DISTRIBUTE}" ]   || die "distribute.py not found at ${DISTRIBUTE}"
[ -f "${VERIFY_DRIFT}" ] || die "verify-drift.py not found at ${VERIFY_DRIFT}"
[ -f "${TARGET_AGENT}" ] || die "implementer.md not found at ${TARGET_AGENT}"

# -------------------------------------------------------------------------
# Step 1 — distribute.py to ensure clean baseline.

python3 "${DISTRIBUTE}" >/dev/null 2>&1 \
  || die "distribute.py failed during baseline setup"

# Step 2 — verify-drift.py exits 0 on clean baseline.

if ! python3 "${VERIFY_DRIFT}" >/dev/null 2>&1; then
  die "verify-drift.py reports drift on clean baseline (precondition violated)"
fi
echo "PASS — clean baseline: distribute.py + verify-drift.py exit 0"

# -------------------------------------------------------------------------
# Step 3 — Corrupt the rule-sheet block in implementer.md.
# Replace everything between BEGIN rule-sheet-v1 / END rule-sheet-v1
# markers with a single CORRUPT sentinel line. Use Python so the regex
# is portable across GNU and BSD sed.

python3 - "${TARGET_AGENT}" <<'PY' \
  || die "failed to corrupt rule-sheet block"
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
pattern = re.compile(
    r"(<!-- BEGIN rule-sheet-v1[^>]*-->\n).*?(\n<!-- END rule-sheet-v1 -->)",
    re.DOTALL,
)
new_text, n = pattern.subn(r"\1CORRUPT\2", text)
if n != 1:
    print(f"expected exactly 1 rule-sheet block, found {n}", file=sys.stderr)
    sys.exit(1)
path.write_text(new_text, encoding="utf-8")
PY

# Sanity: corruption sentinel landed in the file.
grep -q "^CORRUPT$" "${TARGET_AGENT}" \
  || die "corruption sentinel not found in ${TARGET_AGENT} after mutation"

# -------------------------------------------------------------------------
# Step 4 — verify-drift.py must now exit 1 with INJECTION-DRIFT +
# implementer.md substrings.

set +e
drift_output="$(python3 "${VERIFY_DRIFT}" 2>&1)"
drift_exit=$?
set -e

if [ "${drift_exit}" -ne 1 ]; then
  echo "${drift_output}" >&2
  die "verify-drift.py exit=${drift_exit}, expected 1 after corruption"
fi

if ! echo "${drift_output}" | grep -q "INJECTION-DRIFT"; then
  echo "${drift_output}" >&2
  die "verify-drift.py output missing INJECTION-DRIFT substring"
fi

if ! echo "${drift_output}" | grep -q "implementer.md"; then
  echo "${drift_output}" >&2
  die "verify-drift.py output missing implementer.md filename"
fi
echo "PASS — corruption detected: exit=1, output names INJECTION-DRIFT + implementer.md"

# -------------------------------------------------------------------------
# Step 5 — distribute.py restores canonical content from SSOT.

python3 "${DISTRIBUTE}" >/dev/null 2>&1 \
  || die "distribute.py failed during restore step"

# Step 6 — verify-drift.py exits 0 again (restored).

if ! python3 "${VERIFY_DRIFT}" >/dev/null 2>&1; then
  die "verify-drift.py still reports drift after distribute.py restore"
fi

# Sanity: corruption sentinel is gone, canonical marker line present.
if grep -q "^CORRUPT$" "${TARGET_AGENT}"; then
  die "CORRUPT sentinel still present after restore"
fi
echo "PASS — restore: distribute.py recovers canonical state, verify-drift.py exits 0"

# -------------------------------------------------------------------------

echo ""
echo "OK: test-rule-sheet-drift PASS"
exit 0
