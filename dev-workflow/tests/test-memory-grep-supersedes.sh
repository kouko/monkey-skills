#!/usr/bin/env bash
# test-memory-grep-supersedes.sh
#
# Verify memory-grep.sh's supersession/liveness behavior. A `Supersedes:`
# trailer on a LATER commit marks an EARLIER decision as no longer live
# (append-only substrate: the old commit can't be edited, so the pointer
# lives on the replacement and points backward — by PR #N or by SHA).
#
# Liveness is COMPUTED, not stored: a record is superseded iff some later
# commit's `Supersedes:` names it. Default recall shows LIVE records only;
# `--history` includes superseded ones, tagged.
#
# Usage:
#   bash dev-workflow/tests/test-memory-grep-supersedes.sh

set -u

SCRIPT="$(cd "$(dirname "$0")/../skills/git-memory/scripts" && pwd)/memory-grep.sh"

PASS_COUNT=0
FAIL_COUNT=0

pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# -------------------------------------------------------------------------
# Fixture: A superseded-by-PR#, B supersedes A, C superseded-by-SHA, D
# supersedes C. Trailers of the SAME commit share one paragraph so
# `git interpret-trailers` parses them as one footer block.

TMP_REPO="$(mktemp -d)"
cleanup() { [ -n "${TMP_REPO:-}" ] && find "$TMP_REPO" -mindepth 0 -delete 2>/dev/null; }
trap cleanup EXIT

git -C "$TMP_REPO" init -q
git -C "$TMP_REPO" config user.email "test@example.com"
git -C "$TMP_REPO" config user.name "Test Harness"

# A — the original decision, PR #10.
echo a > "$TMP_REPO/a.txt"; git -C "$TMP_REPO" add a.txt
git -C "$TMP_REPO" commit -q -m "feat: add approach X (#10)" \
  -m "Decision: use approach X for the parser"

# B — supersedes A by PR number, PR #11.
echo b > "$TMP_REPO/b.txt"; git -C "$TMP_REPO" add b.txt
git -C "$TMP_REPO" commit -q -m "feat: switch to Z (#11)" \
  -m "$(printf 'Decision: switch to approach Z\nSupersedes: PR #10')"

# C — an independent learning, PR #12.
echo c > "$TMP_REPO/c.txt"; git -C "$TMP_REPO" add c.txt
git -C "$TMP_REPO" commit -q -m "feat: add C (#12)" \
  -m "Learning: C insight about caching"
SHA_C="$(git -C "$TMP_REPO" rev-parse HEAD)"

# D — supersedes C by full SHA, PR #13.
echo d > "$TMP_REPO/d.txt"; git -C "$TMP_REPO" add d.txt
git -C "$TMP_REPO" commit -q -m "revert: drop C (#13)" \
  -m "$(printf 'Gotcha: C caching was wrong\nSupersedes: %s' "$SHA_C")"

run_plain()   { bash "$SCRIPT" --repo="$TMP_REPO" --no-pr "$@"; }
run_json()    { bash "$SCRIPT" --repo="$TMP_REPO" --no-pr --format=json "$@"; }

# -------------------------------------------------------------------------
# Default (live-only) plain output
OUT="$(run_plain)"

if ! printf '%s' "$OUT" | grep -q "use approach X"; then
  pass "default hides A (superseded by PR #10)"
else
  fail "default should hide superseded A"
fi

if printf '%s' "$OUT" | grep -q "switch to approach Z"; then
  pass "default shows B (live)"
else
  fail "default should show live B"
fi

if ! printf '%s' "$OUT" | grep -q "C insight about caching"; then
  pass "default hides C (superseded by SHA)"
else
  fail "default should hide superseded C"
fi

if printf '%s' "$OUT" | grep -q "C caching was wrong"; then
  pass "default shows D (live)"
else
  fail "default should show live D"
fi

# -------------------------------------------------------------------------
# --history includes superseded, tagged
HOUT="$(run_plain --history)"

if printf '%s' "$HOUT" | grep -q "use approach X"; then
  pass "--history shows superseded A"
else
  fail "--history should show superseded A"
fi

if printf '%s' "$HOUT" | grep -qi "superseded"; then
  pass "--history tags superseded records"
else
  fail "--history should tag superseded records"
fi

# -------------------------------------------------------------------------
# JSON default: only live records (B, D)
JOUT="$(run_json)"
N="$(printf '%s' "$JOUT" | jq '.commits | length')"
if [ "$N" = "2" ]; then
  pass "json default returns 2 live commits"
else
  fail "json default should return 2 live commits (got $N)"
fi

if ! printf '%s' "$JOUT" | jq -e '.commits[] | select(.subject | test("approach X"))' >/dev/null; then
  pass "json default excludes superseded A"
else
  fail "json default should exclude superseded A"
fi

# -------------------------------------------------------------------------
# JSON --history: superseded flagged
JHOUT="$(run_json --history)"
NS="$(printf '%s' "$JHOUT" | jq '[.commits[] | select(.superseded == true)] | length')"
if [ "$NS" = "2" ]; then
  pass "json --history flags 2 superseded (A, C)"
else
  fail "json --history should flag 2 superseded (got $NS)"
fi

# -------------------------------------------------------------------------
# Edge fixtures (separate repo): supersedes-only commit, reverse-prefix
# SHA match, and malformed-value graceful drop. core.abbrev=12 so a
# 7-char abbrev on the superseding side is strictly SHORTER than the
# target's %h, exercising the reverse-prefix branch (index(s, tok)==1).

TMP2="$(mktemp -d)"
cleanup2() { [ -n "${TMP2:-}" ] && find "$TMP2" -mindepth 0 -delete 2>/dev/null; }
trap 'cleanup; cleanup2' EXIT

git -C "$TMP2" init -q
git -C "$TMP2" config user.email "test@example.com"
git -C "$TMP2" config user.name "Test Harness"
git -C "$TMP2" config core.abbrev 12

# M1 superseded by M2, where M2 is a pure revert with NO Decision/Learning/
# Gotcha — only a Supersedes:. Exercises "supersedes-only commit registers".
echo m1 > "$TMP2/m1"; git -C "$TMP2" add m1
git -C "$TMP2" commit -q -m "feat: revertable (#30)" -m "Decision: keep M1"
echo m2 > "$TMP2/m2"; git -C "$TMP2" add m2
git -C "$TMP2" commit -q -m "revert: kill M1" -m "Supersedes: PR #30"

# M3 superseded by M4 via a 7-char abbrev (< 12-char %h) → reverse-prefix.
echo m3 > "$TMP2/m3"; git -C "$TMP2" add m3
git -C "$TMP2" commit -q -m "feat: sha-target (#31)" -m "Decision: keep M3"
SHORT7="$(git -C "$TMP2" rev-parse --short=7 HEAD)"
echo m4 > "$TMP2/m4"; git -C "$TMP2" add m4
git -C "$TMP2" commit -q -m "revert: kill M3" \
  -m "$(printf 'Decision: m4 replaces M3\nSupersedes: %s' "$SHORT7")"

# M5 with a malformed Supersedes on M6 → M5 must stay live (safe direction).
echo m5 > "$TMP2/m5"; git -C "$TMP2" add m5
git -C "$TMP2" commit -q -m "feat: malformed target (#32)" -m "Decision: keep M5"
echo m6 > "$TMP2/m6"; git -C "$TMP2" add m6
git -C "$TMP2" commit -q -m "chore: bad ptr" \
  -m "$(printf 'Decision: m6\nSupersedes: not-a-ref')"

E="$(bash "$SCRIPT" --repo="$TMP2" --no-pr)"

if ! printf '%s' "$E" | grep -q "keep M1"; then
  pass "supersedes-only commit (no D/L/G) still retires its target"
else
  fail "supersedes-only commit should retire M1"
fi

if ! printf '%s' "$E" | grep -q "keep M3"; then
  pass "reverse-prefix SHA (7-char abbrev < 12-char %h) matches"
else
  fail "reverse-prefix SHA abbrev should retire M3"
fi

if printf '%s' "$E" | grep -q "keep M5"; then
  pass "malformed Supersedes leaves target live (safe direction)"
else
  fail "malformed Supersedes should NOT retire M5"
fi

# -------------------------------------------------------------------------
echo ""
echo "================================================================"
echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
echo "================================================================"
[ "${FAIL_COUNT}" -gt 0 ] && exit 1
exit 0
