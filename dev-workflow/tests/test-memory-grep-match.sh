#!/usr/bin/env bash
# test-memory-grep-match.sh
#
# Verify memory-grep.sh's pull-retrieval surface: --match (topic filter),
# --path (pathspec scope), --top (display cap with drop-logging). The
# load-bearing invariant: liveness is computed over the FULL history, so
# --match / --path narrow only the DISPLAY, never the supersession index.
# A record superseded by a commit that does NOT match the query must still
# be hidden by default.
#
# Usage:
#   bash dev-workflow/tests/test-memory-grep-match.sh

set -u

SCRIPT="$(cd "$(dirname "$0")/../skills/git-memory/scripts" && pwd)/memory-grep.sh"

PASS_COUNT=0
FAIL_COUNT=0
pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

TMP="$(mktemp -d)"
cleanup() { [ -n "${TMP:-}" ] && find "$TMP" -mindepth 0 -delete 2>/dev/null; }
trap cleanup EXIT

git -C "$TMP" init -q
git -C "$TMP" config user.email "test@example.com"
git -C "$TMP" config user.name "Test Harness"

commit() { # <file> <subject> <trailer-paragraph>
  echo "$RANDOM" > "$TMP/$1"; git -C "$TMP" add "$1"
  git -C "$TMP" commit -q -m "$2" -m "$3"
}

# C1 parser (superseded by C3) ; C2 cache (superseded by C5, out-of-topic
# & out-of-path superseder) ; C3 parser+supersedes ; C4 parser only in a
# trailer, path README ; C5 supersedes C2 but mentions neither cache nor
# touches cache.txt.
commit parser.txt "feat: parser core (#40)" "Decision: two-pass parser"
commit cache.txt  "feat: cache layer (#41)" "Learning: cache ttl gotcha"
commit parser.txt "perf: single-pass (#42)" "$(printf 'Decision: single-pass parser\nSupersedes: PR #40')"
commit README     "docs: readme (#43)"      "Gotcha: parser edge in docs"
commit misc.txt   "chore: cleanup (#44)"    "$(printf 'Decision: consolidate config\nSupersedes: PR #41')"

has()  { printf '%s' "$1" | grep -q "$2"; }
nhas() { ! printf '%s' "$1" | grep -q "$2"; }
run()  { bash "$SCRIPT" --repo="$TMP" --no-pr "$@"; }

# ── A. --match text filter + liveness (default = live) ─────────────
A="$(run --match=parser)"
has  "$A" "single-pass parser"   && pass "match: shows live C3 (subject/trailer parser)"   || fail "match: should show C3"
has  "$A" "parser edge in docs"  && pass "match: matches trailer VALUE not just subject"    || fail "match: should match trailer value (C4)"
nhas "$A" "cache ttl"            && pass "match: excludes non-matching C2"                  || fail "match: should exclude C2"
nhas "$A" "two-pass parser"      && pass "match: hides superseded C1 by default"            || fail "match: should hide superseded C1"

# ── B. --match + --history reveals superseded match ────────────────
B="$(run --match=parser --history)"
has "$B" "two-pass parser" && pass "match+history: shows superseded C1" || fail "match+history: should show C1"

# ── C. KEY: liveness over FULL set — C2 superseded by C5 which does
#     NOT match 'cache' and lives elsewhere; still hidden. ───────────
C="$(run --match=cache)"
nhas "$C" "cache ttl gotcha" && pass "match: C2 hidden though its superseder doesn't match query" || fail "match: C2 should be hidden (liveness over full set)"
CH="$(run --match=cache --history)"
has "$CH" "cache ttl gotcha" && pass "match+history: superseded C2 reappears" || fail "match+history: C2 should reappear"

# ── D. --top cap + drop note ───────────────────────────────────────
D="$(run --match=parser --top=1)"
[ "$(printf '%s' "$D" | grep -c '^### ')" = "1" ] && pass "top=1 caps to one record" || fail "top=1 should cap to one record"
has "$D" "suppressed" && pass "top logs suppressed count (no silent truncation)" || fail "top should log suppressed count"

# ── E. --path scope (distinct from text match) ─────────────────────
E="$(run --path=parser.txt)"
has  "$E" "single-pass parser"  && pass "path: shows live commit touching parser.txt (C3)" || fail "path: should show C3"
nhas "$E" "cache ttl"           && pass "path: excludes C2 (touches cache.txt)"            || fail "path: should exclude C2"
nhas "$E" "parser edge in docs" && pass "path: excludes C4 (touches README, not path)"     || fail "path: should exclude C4"

# ── F. KEY: --path liveness over FULL history — C2's superseder C5 is
#     out-of-path (misc.txt), yet C2 still retired. ─────────────────
F="$(run --path=cache.txt)"
nhas "$F" "cache ttl gotcha" && pass "path: C2 hidden though out-of-path superseder retired it" || fail "path: C2 should be hidden (index over full history)"
FH="$(run --path=cache.txt --history)"
has "$FH" "cache ttl gotcha" && pass "path+history: superseded C2 reappears, tagged" || fail "path+history: C2 should reappear"
has "$FH" "SUPERSEDED"       && pass "path+history: tag present"                     || fail "path+history: should tag superseded"

# ── G. empty match → clear message, exit 0 ─────────────────────────
set +e; G="$(run --match=zzznomatch)"; rc=$?; set -e 2>/dev/null || true
[ "$rc" = "0" ] && pass "empty match exits 0" || fail "empty match should exit 0 (got $rc)"
has "$G" "no memory matches" && pass "empty match prints clear message" || fail "empty match should print a clear message"
[ "$(printf '%s' "$G" | grep -c '^### ')" = "0" ] && pass "empty match shows no records" || fail "empty match should show no records"

# ── H. malformed --match regex fails loud+clean (exit 1, not jq's 5) ─
set +e; HERR="$(run --match='p(' 2>&1)"; rc=$?; set -e 2>/dev/null || true
[ "$rc" = "1" ] && pass "malformed regex exits 1 (not undocumented jq abort)" || fail "malformed regex should exit 1 (got $rc)"
has "$HERR" "Invalid --match regex" && pass "malformed regex prints one clean message" || fail "malformed regex should print a clean message"

# ── I. --top larger than result count → all shown, no suppressed note ─
TT="$(run --match=parser --top=99)"
nhas "$TT" "suppressed" && pass "--top > result count reports nothing suppressed" || fail "--top > count should not claim suppression"

echo ""
echo "================================================================"
echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
echo "================================================================"
[ "${FAIL_COUNT}" -gt 0 ] && exit 1
exit 0
