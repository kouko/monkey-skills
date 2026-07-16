#!/usr/bin/env bash
# test-memory-grep-verify-merged.sh
#
# Verify memory-grep.sh's `--verify-merged <ref>` mode: the post-merge CI
# predicate for "a memory-worthy squash commit landed without its trailer
# carrier" (#574 incident class). Unlike `--verify` (which checks for a
# bare Decision/Learning/Gotcha trailer anywhere in the body), this mode
# gates on the squash-commit's `## Memory` heading:
#
#   no `## Memory` heading in body      → exit 0 (not memory-worthy at all)
#   `## Memory` heading + a verify key  → exit 0 (carrier present)
#   `## Memory` heading, NO verify key  → exit 4 (the #574 silent-drop case)
#   <ref> does not resolve              → exit 2
#   no ref given                        → exit 1 (usage error)
#
# Usage:
#   bash dev-workflow/tests/test-memory-grep-verify-merged.sh

set -u

SCRIPT="$(cd "$(dirname "$0")/../skills/git-memory/scripts" && pwd)/memory-grep.sh"

PASS_COUNT=0
FAIL_COUNT=0

pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# -------------------------------------------------------------------------
# Fixture: a throwaway git repo with three squash-shaped commits.

TMP_REPO="$(mktemp -d)"
cleanup() { [ -n "${TMP_REPO:-}" ] && find "$TMP_REPO" -mindepth 0 -delete 2>/dev/null; }
trap cleanup EXIT

git -C "$TMP_REPO" init -q
git -C "$TMP_REPO" config user.email "test@example.com"
git -C "$TMP_REPO" config user.name "Test Harness"

# Commit A — no `## Memory` heading at all: not memory-worthy, exit 0.
echo "a" > "$TMP_REPO/a.txt"
git -C "$TMP_REPO" add a.txt
git -C "$TMP_REPO" commit -q -m "feat: add a" -m "just a bare squash body, no heading"
SHA_A="$(git -C "$TMP_REPO" rev-parse HEAD)"

# Commit B — `## Memory` heading present, carrying a Decision: key: exit 0.
echo "b" > "$TMP_REPO/b.txt"
git -C "$TMP_REPO" add b.txt
git -C "$TMP_REPO" commit -q -m "feat: add b" -m "## Memory

Decision: chose X over Y"
SHA_B="$(git -C "$TMP_REPO" rev-parse HEAD)"

# Commit C — `## Memory` heading present but NO verify key survives (the
# #574 silent-drop case: heading present, trailer carrier lost): exit 4.
echo "c" > "$TMP_REPO/c.txt"
git -C "$TMP_REPO" add c.txt
git -C "$TMP_REPO" commit -q -m "feat: add c" -m "## Memory

Something was noted here but no trailer key survived the squash."
SHA_C="$(git -C "$TMP_REPO" rev-parse HEAD)"

# -------------------------------------------------------------------------
# Check 1 — no `## Memory` heading exits 0 (not memory-worthy)

if bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged "$SHA_A"; then
  pass "--verify-merged on heading-absent commit A exits 0"
else
  fail "--verify-merged on heading-absent commit A should exit 0 (got $?)"
fi

# -------------------------------------------------------------------------
# Check 2 — heading + verify key exits 0 (carrier present)

if bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged "$SHA_B"; then
  pass "--verify-merged on heading+key commit B exits 0"
else
  fail "--verify-merged on heading+key commit B should exit 0 (got $?)"
fi

# -------------------------------------------------------------------------
# Check 3 — heading present, no verify key: exit 4 (the #574 case)

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged "$SHA_C"
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 4 ]; then
  pass "--verify-merged on heading-only commit C exits 4"
else
  fail "--verify-merged on heading-only commit C should exit 4 (got $rc)"
fi

# -------------------------------------------------------------------------
# Check 4 — unresolvable ref exits 2

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 2 ]; then
  pass "--verify-merged on unresolvable ref exits 2"
else
  fail "--verify-merged on unresolvable ref should exit 2 (got $rc)"
fi

# -------------------------------------------------------------------------
# Check 5 — missing ref is a usage error (exit 1)

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 1 ]; then
  pass "--verify-merged with no ref exits 1 (usage error)"
else
  fail "--verify-merged with no ref should exit 1 (got $rc)"
fi

# -------------------------------------------------------------------------
# Summary

echo ""
echo "================================================================"
echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
echo "================================================================"

if [ "${FAIL_COUNT}" -gt 0 ]; then
  exit 1
fi
exit 0
