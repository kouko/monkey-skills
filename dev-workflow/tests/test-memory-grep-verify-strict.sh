#!/usr/bin/env bash
# test-memory-grep-verify-strict.sh
#
# Verify memory-grep.sh's `--verify-strict <ref>` mode: unlike `--verify`
# (a text match anywhere in the body), strict mode requires the memory key
# to survive `git interpret-trailers --parse --unfold` — the #575
# refinement. A trailer block followed by ANY non-trailer line stops being
# the message's true footer, so git's own parser yields nothing even
# though a plain text grep still finds the `Decision:`/etc. line mid-body.
#
#   parse-level hit (key survives interpret-trailers)  → exit 0
#   parse-level miss (text may or may not match)        → exit 4
#   <ref> does not resolve                               → exit 2
#   no ref given                                          → exit 1 (usage error)
#
# Usage:
#   bash dev-workflow/tests/test-memory-grep-verify-strict.sh

set -u

SCRIPT="$(cd "$(dirname "$0")/../skills/git-memory/scripts" && pwd)/memory-grep.sh"

PASS_COUNT=0
FAIL_COUNT=0

pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# -------------------------------------------------------------------------
# Fixture: a throwaway git repo with four commits.

TMP_REPO="$(mktemp -d)"
cleanup() { [ -n "${TMP_REPO:-}" ] && find "$TMP_REPO" -mindepth 0 -delete 2>/dev/null; }
trap cleanup EXIT

git -C "$TMP_REPO" init -q
git -C "$TMP_REPO" config user.email "test@example.com"
git -C "$TMP_REPO" config user.name "Test Harness"

# Commit A — the #575-shaped case: a `Decision:` line mid-body, but the
# block is followed by a non-trailer prose line. Plain `--verify` (text
# grep on the full body) exits 0. `git interpret-trailers` only reads the
# message's trailing paragraph as a footer — since a non-trailer line
# comes AFTER the Decision: line here, nothing survives the parse, so
# `--verify-strict` must exit 4.
echo "a" > "$TMP_REPO/a.txt"
git -C "$TMP_REPO" add a.txt
git -C "$TMP_REPO" commit -q -m "feat: add a" -m "Decision: chose X over Y

This trailing prose line breaks trailer-footer detection."
SHA_A="$(git -C "$TMP_REPO" rev-parse HEAD)"

# Commit B — proper footer: the Decision: trailer IS the message's true
# last block, nothing follows it. Both --verify and --verify-strict exit 0.
echo "b" > "$TMP_REPO/b.txt"
git -C "$TMP_REPO" add b.txt
git -C "$TMP_REPO" commit -q -m "feat: add b" -m "Some prose explaining the change.

Decision: chose X over Y"
SHA_B="$(git -C "$TMP_REPO" rev-parse HEAD)"

# Commit C — no memory key anywhere: both --verify and --verify-strict
# exit 4.
echo "c" > "$TMP_REPO/c.txt"
git -C "$TMP_REPO" add c.txt
git -C "$TMP_REPO" commit -q -m "chore: add c"
SHA_C="$(git -C "$TMP_REPO" rev-parse HEAD)"

# -------------------------------------------------------------------------
# Check 1 — #575 case: plain --verify exits 0 on commit A (text match)

if bash "$SCRIPT" --repo="$TMP_REPO" --verify "$SHA_A"; then
  pass "plain --verify on commit A (mid-body Decision + trailing prose) exits 0"
else
  fail "plain --verify on commit A should exit 0 (got $?)"
fi

# -------------------------------------------------------------------------
# Check 2 — #575 case: --verify-strict exits 4 on commit A (parse-level miss)

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify-strict "$SHA_A"
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 4 ]; then
  pass "--verify-strict on commit A (trailing prose after trailer) exits 4"
else
  fail "--verify-strict on commit A should exit 4 (got $rc)"
fi

# -------------------------------------------------------------------------
# Check 3 — proper-footer commit B: --verify-strict exits 0

if bash "$SCRIPT" --repo="$TMP_REPO" --verify-strict "$SHA_B"; then
  pass "--verify-strict on commit B (proper trailer footer) exits 0"
else
  fail "--verify-strict on commit B should exit 0 (got $?)"
fi

# -------------------------------------------------------------------------
# Check 4 — no-key commit C: --verify-strict exits 4

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify-strict "$SHA_C"
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 4 ]; then
  pass "--verify-strict on no-key commit C exits 4"
else
  fail "--verify-strict on no-key commit C should exit 4 (got $rc)"
fi

# -------------------------------------------------------------------------
# Check 5 — unresolvable ref exits 2

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify-strict "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 2 ]; then
  pass "--verify-strict on unresolvable ref exits 2"
else
  fail "--verify-strict on unresolvable ref should exit 2 (got $rc)"
fi

# -------------------------------------------------------------------------
# Check 6 — missing ref is a usage error (exit 1)

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify-strict
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 1 ]; then
  pass "--verify-strict with no ref exits 1 (usage error)"
else
  fail "--verify-strict with no ref should exit 1 (got $rc)"
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
