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
# Fixture: two more commits for the #578 suspicious-empty-body case.

# Commit D — title-only body AND the title matches the squash-of-PR
# signature "(#N)" — the #578 live incident: the merge dialog emptied
# the entire body, so no heading logic ever runs. This must be caught
# BEFORE the heading check, exit 4.
echo "d" > "$TMP_REPO/d.txt"
git -C "$TMP_REPO" add d.txt
git -C "$TMP_REPO" commit -q -m "feat(git-memory): harden verify-merged (#578)"
SHA_D="$(git -C "$TMP_REPO" rev-parse HEAD)"

# Commit E — title-only body WITHOUT a "(#N)" suffix: a routine direct
# commit (not a squash-of-PR shape at all) — NOT suspicious, exit 0.
echo "e" > "$TMP_REPO/e.txt"
git -C "$TMP_REPO" add e.txt
git -C "$TMP_REPO" commit -q -m "chore: bump version string"
SHA_E="$(git -C "$TMP_REPO" rev-parse HEAD)"

# Commit F — multi-line body, no `## Memory` heading: still exit 0
# (existing heading-absent path, unaffected by the new check).
echo "f" > "$TMP_REPO/f.txt"
git -C "$TMP_REPO" add f.txt
git -C "$TMP_REPO" commit -q -m "feat: add f" -m "First body line.
Second body line, still no heading."
SHA_F="$(git -C "$TMP_REPO" rev-parse HEAD)"

# -------------------------------------------------------------------------
# Check 6 — title-only body + "(#N)" suffix: suspicious squash-shaped
# commit whose PR body never reached the squash message (#578 case).
# Exit 4.

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged "$SHA_D"
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 4 ]; then
  pass "--verify-merged on title-only squash-shaped commit D exits 4 (#578 case)"
else
  fail "--verify-merged on title-only squash-shaped commit D should exit 4 (got $rc)"
fi

# -------------------------------------------------------------------------
# Check 7 — title-only body WITHOUT "(#N)" suffix: routine direct
# commit, not suspicious. Exit 0.

if bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged "$SHA_E"; then
  pass "--verify-merged on title-only non-squash commit E exits 0"
else
  fail "--verify-merged on title-only non-squash commit E should exit 0 (got $?)"
fi

# -------------------------------------------------------------------------
# Check 8 — multi-line body without `## Memory` heading: still exit 0.

if bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged "$SHA_F"; then
  pass "--verify-merged on multi-line heading-absent commit F exits 0"
else
  fail "--verify-merged on multi-line heading-absent commit F should exit 0 (got $?)"
fi

# -------------------------------------------------------------------------
# Fixture: commit G — title-only body (title + a WHITESPACE-ONLY second
# line) whose title matches the squash-of-PR "(#N)" signature. A regular
# `git commit -m ... -m ...` invocation would strip a trailing
# whitespace-only line (cleanup=strip default), so this shape is built via
# `git commit-tree -F` directly, which bypasses that cleanup and preserves
# the whitespace-only line verbatim — reproducing what the GitHub merge
# dialog / API can actually compose.

MSG_G="$TMP_REPO/msg-g.txt"
printf 'feat(git-memory): whitespace-title bug (#888)\n   \n' > "$MSG_G"
echo "g" > "$TMP_REPO/g.txt"
git -C "$TMP_REPO" add g.txt
TREE_G="$(git -C "$TMP_REPO" write-tree)"
PARENT_G="$(git -C "$TMP_REPO" rev-parse HEAD)"
SHA_G="$(git -C "$TMP_REPO" commit-tree "$TREE_G" -p "$PARENT_G" -F "$MSG_G")"

# -------------------------------------------------------------------------
# Check 9 — title + "(#N)" line followed by a WHITESPACE-ONLY line: the
# body is still title-only in substance (no real second line of content),
# so this must be caught by the same #578 suspicious-empty-body check as
# commit D. A naive `grep -c .` non-empty-line count would (wrongly) count
# the whitespace-only line as content and miss this. Exit 4.

set +e
bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged "$SHA_G"
rc=$?
set -e 2>/dev/null || true
if [ "$rc" -eq 4 ]; then
  pass "--verify-merged on title+(#N)+whitespace-only-line commit G exits 4"
else
  fail "--verify-merged on title+(#N)+whitespace-only-line commit G should exit 4 (got $rc)"
fi

# -------------------------------------------------------------------------
# Fixture: commit H — a heading that STARTS WITH but is not exactly
# `## Memory` (here "## Memory management"), and NO Decision/Learning/
# Gotcha key anywhere in the body. A prefix-only heading regex would
# wrongly treat this as the memory-worthy heading and then fail it (exit
# 4) for lacking a key. The heading match must be exact-line, so this
# should read as "no `## Memory` heading at all" — exit 0.

echo "h" > "$TMP_REPO/h.txt"
git -C "$TMP_REPO" add h.txt
git -C "$TMP_REPO" commit -q -m "feat: add h" -m "## Memory management

Some notes about managing memory allocation, no trailer keys here."
SHA_H="$(git -C "$TMP_REPO" rev-parse HEAD)"

# -------------------------------------------------------------------------
# Check 10 — "## Memory management" heading (not the exact `## Memory`
# heading) with no memory key: exit 0 (not memory-worthy).

if bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged "$SHA_H"; then
  pass "--verify-merged on non-exact '## Memory management' heading commit H exits 0"
else
  fail "--verify-merged on non-exact '## Memory management' heading commit H should exit 0 (got $?)"
fi

# -------------------------------------------------------------------------
# Check 11 — exact `## Memory` heading + key still detected (regression
# guard for the exact-line-anchor tightening): reuses commit B.

if bash "$SCRIPT" --repo="$TMP_REPO" --verify-merged "$SHA_B"; then
  pass "--verify-merged still detects exact '## Memory' heading + key on commit B"
else
  fail "--verify-merged should still detect exact '## Memory' heading + key on commit B (got $?)"
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
