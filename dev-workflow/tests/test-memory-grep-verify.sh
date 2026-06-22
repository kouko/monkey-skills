#!/usr/bin/env bash
# test-memory-grep-verify.sh
#
# Verify memory-grep.sh's `--verify <ref>` mode: it must detect whether
# a given commit carries git-memory in its FULL message body (a text
# match on `^(Decision|Learning|Gotcha):`, which is what survives a
# squash merge mid-body under COMMIT_MESSAGES), and exit with a distinct
# code so an orchestrator can detect a silently-empty memory substrate.
#
#   exit 0  — memory-worthy trailer present in the ref's body
#   exit 4  — memory check requested but NO memory found
#   exit 2  — <ref> does not resolve
#   exit 1  — usage error (no ref given)
#
# Usage:
#   bash dev-workflow/tests/test-memory-grep-verify.sh

set -u

SCRIPT="$(cd "$(dirname "$0")/../skills/git-memory/scripts" && pwd)/memory-grep.sh"

PASS_COUNT=0
FAIL_COUNT=0

pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# -------------------------------------------------------------------------
# Fixture: a throwaway git repo with one memory-worthy commit (A) and one
# bare-subject commit (B). Lives under $TMPDIR; cleaned up at the end.

TMP_REPO="$(mktemp -d)"
cleanup() { [ -n "${TMP_REPO:-}" ] && find "$TMP_REPO" -mindepth 0 -delete 2>/dev/null; }
trap cleanup EXIT

git -C "$TMP_REPO" init -q
git -C "$TMP_REPO" config user.email "test@example.com"
git -C "$TMP_REPO" config user.name "Test Harness"

# Commit A — memory-worthy: a Decision trailer in the body.
echo "a" > "$TMP_REPO/a.txt"
git -C "$TMP_REPO" add a.txt
git -C "$TMP_REPO" commit -q -m "feat: add a" -m "Decision: chose X over Y"
SHA_A="$(git -C "$TMP_REPO" rev-parse HEAD)"

# Commit B — bare subject, no trailer.
echo "b" > "$TMP_REPO/b.txt"
git -C "$TMP_REPO" add b.txt
git -C "$TMP_REPO" commit -q -m "chore: add b"
SHA_B="$(git -C "$TMP_REPO" rev-parse HEAD)"

# Commit C — ONLY a Related: trailer, no Decision/Learning/Gotcha. The
# verify predicate is the three memory-worthy keys, NOT the 4-key
# extraction set — so a Related-only commit is NOT memory-worthy and
# must exit 4 (regression guard against verify over-matching Related).
echo "c" > "$TMP_REPO/c.txt"
git -C "$TMP_REPO" add c.txt
git -C "$TMP_REPO" commit -q -m "chore: add c" -m "Related: #123"
SHA_C="$(git -C "$TMP_REPO" rev-parse HEAD)"

# -------------------------------------------------------------------------
# Check 1 — memory-worthy ref exits 0

if bash "$SCRIPT" --repo="$TMP_REPO" --verify "$SHA_A"; then
  pass "--verify on memory-worthy commit A exits 0"
else
  fail "--verify on memory-worthy commit A should exit 0 (got $?)"
fi

# -------------------------------------------------------------------------
# Check 2 — bare-subject ref exits 4

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify "$SHA_B"
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 4 ]; then
  pass "--verify on bare-subject commit B exits 4"
else
  fail "--verify on bare-subject commit B should exit 4 (got $rc)"
fi

# -------------------------------------------------------------------------
# Check 3 — missing ref is a usage error (exit 1)

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 1 ]; then
  pass "--verify with no ref exits 1 (usage error)"
else
  fail "--verify with no ref should exit 1 (got $rc)"
fi

# -------------------------------------------------------------------------
# Check 4 — unresolvable ref exits 2

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 2 ]; then
  pass "--verify on unresolvable ref exits 2"
else
  fail "--verify on unresolvable ref should exit 2 (got $rc)"
fi

# -------------------------------------------------------------------------
# Check 5 — Related-only commit exits 4 (verify must NOT match Related)

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify "$SHA_C"
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 4 ]; then
  pass "--verify on Related-only commit C exits 4"
else
  fail "--verify on Related-only commit C should exit 4 (got $rc)"
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
