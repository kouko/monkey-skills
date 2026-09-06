#!/usr/bin/env bash
# test-memory-grep-perf.sh
#
# Speed contract for memory-grep.sh (W1-02,
# docs/loom/2026-09-06-memory-grep-single-pass/plan.md). The rewrite
# replaces per-commit subprocess loops with one git pass, so this suite
# asserts two things a byte-diff equivalence oracle cannot:
#
#   (a) wall-clock: `--no-pr` on a 2,000-commit fixture (300
#       memory-worthy, 20 with Supersedes:) finishes within 2 whole
#       seconds (`date +%s` before/after — bash 3.2 has no
#       $EPOCHREALTIME, so sub-second precision is unavailable and the
#       bound is deliberately whole-second).
#   (b) git-call count: with a PATH shim that logs every `git`
#       invocation, the number of calls memory-grep.sh makes is a SMALL
#       CONSTANT — the same count on a 20-commit repo and the
#       2,000-commit repo — bounded at <=4 for `--no-pr` and <=6 with
#       `--path=<file>` (plan.md W1-02 Risk).
#
# RED today (before W1-02): (a) takes on the order of 100s; (b) counts
# on the order of 6,000 git calls, and the count is NOT constant across
# repo sizes (it scales with commit count).
#
# Usage:
#   bash loom-workflow/tests/test-memory-grep-perf.sh

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$(cd "$HERE/../skills/git-memory/scripts" && pwd)/memory-grep.sh"

PASS_COUNT=0
FAIL_COUNT=0
pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

TMP_ROOT="$(mktemp -d)"
cleanup() { [ -n "${TMP_ROOT:-}" ] && find "$TMP_ROOT" -mindepth 0 -delete 2>/dev/null; }
trap cleanup EXIT

# ── fixture builder ─────────────────────────────────────────────────
# $1 — target dir, $2 — total commit count, $3 — memory-worthy count,
# $4 — how many of those memory-worthy commits also carry Supersedes:
# (pointing at an earlier memory commit). Every commit touches the same
# tracked file so a --path pathspec matches all of them.
build_perf_repo() {
  local dir="$1" n="$2" memory_count="$3" supersede_count="$4"
  mkdir -p "$dir"
  git -C "$dir" init -q
  git -C "$dir" symbolic-ref HEAD refs/heads/main
  git -C "$dir" config user.email "fixture@example.com"
  git -C "$dir" config user.name "Fixture Bot"
  git -C "$dir" config commit.gpgsign false

  local i=0 memory_shas="" msha_count=0
  while [ "$i" -lt "$n" ]; do
    local year=$((2015 + i / 336))
    local month=$(( (i / 28) % 12 + 1 ))
    local day=$(( i % 28 + 1 ))
    local date
    date="$(printf '%04d-%02d-%02d' "$year" "$month" "$day")"
    echo "content at commit $i" > "$dir/content.txt"
    git -C "$dir" add content.txt

    local msg="chore: commit $i (#$((i + 1000)))"
    if [ "$i" -lt "$memory_count" ]; then
      local supersede_target=""
      if [ "$i" -ge "$((memory_count - supersede_count))" ]; then
        # Pair up the last `supersede_count` memory commits with the
        # earliest `supersede_count` memory shas recorded so far.
        local idx=$((i - (memory_count - supersede_count)))
        supersede_target="$(printf '%s\n' "$memory_shas" | sed -n "$((idx + 1))p")"
      fi
      if [ -n "$supersede_target" ]; then
        msg="fix: superseding decision $i (#$((i + 1000)))

Gotcha: superseding decision $i
Supersedes: $supersede_target"
      else
        msg="feat: memory decision $i (#$((i + 1000)))

Decision: memory decision number $i"
      fi
    fi

    GIT_AUTHOR_DATE="${date}T00:00:00+0000" \
      GIT_COMMITTER_DATE="${date}T00:00:00+0000" \
      git -C "$dir" commit -q -m "$msg"

    if [ "$i" -lt "$memory_count" ]; then
      local sha
      sha="$(git -C "$dir" rev-parse HEAD)"
      memory_shas="$memory_shas
$sha"
      msha_count=$((msha_count + 1))
    fi
    i=$((i + 1))
  done
}

# ── git-call-count shim: a PATH-prepended dir with one `git` shim that
# logs its args (one line per invocation) then execs the real binary ──
make_git_shim() {
  local shim_dir="$1" log="$2"
  local real
  real="$(command -v git)"
  mkdir -p "$shim_dir"
  cat > "$shim_dir/git" <<SHIM
#!/bin/sh
echo "\$@" >> "$log"
exec "$real" "\$@"
SHIM
  chmod +x "$shim_dir/git"
}

count_git_calls() {
  # $1 — repo, rest — memory-grep.sh args
  local repo="$1"; shift
  local shim_dir="$TMP_ROOT/shim-$$-$RANDOM"
  local log="$TMP_ROOT/git-calls-$$-$RANDOM.log"
  : > "$log"
  make_git_shim "$shim_dir" "$log"
  ( PATH="$shim_dir:$PATH" bash "$SCRIPT" --repo="$repo" "$@" >/dev/null 2>/dev/null )
  wc -l < "$log" | tr -d ' '
}

# ── jq-call-count shim (W1-03): a PATH-prepended dir with one `jq` shim
# that logs exactly ONE marker line per invocation (never the args
# themselves — unlike git's single-line args, a jq filter program is
# typically a multi-line string, so `echo "$@" >> log` would log
# several newlines per single invocation and overcount) then execs the
# real binary. Renderers must read the NDJSON once — a small constant
# number of jq invocations, not one (or more) per record. ───────────
make_jq_shim() {
  local shim_dir="$1" log="$2"
  local real
  real="$(command -v jq)"
  mkdir -p "$shim_dir"
  cat > "$shim_dir/jq" <<SHIM
#!/bin/sh
echo call >> "$log"
exec "$real" "\$@"
SHIM
  chmod +x "$shim_dir/jq"
}

count_jq_calls() {
  # $1 — repo, rest — memory-grep.sh args
  local repo="$1"; shift
  local shim_dir="$TMP_ROOT/jq-shim-$$-$RANDOM"
  local log="$TMP_ROOT/jq-calls-$$-$RANDOM.log"
  : > "$log"
  make_jq_shim "$shim_dir" "$log"
  ( PATH="$shim_dir:$PATH" bash "$SCRIPT" --repo="$repo" "$@" >/dev/null 2>/dev/null )
  wc -l < "$log" | tr -d ' '
}

# ── build a small (20-commit) and a large (2,000-commit) fixture ───
SMALL_REPO="$TMP_ROOT/small"
LARGE_REPO="$TMP_ROOT/large"
build_perf_repo "$SMALL_REPO" 20 5 1
build_perf_repo "$LARGE_REPO" 2000 300 20

# ── (b) git-call count: constant across repo sizes ─────────────────
small_count_no_path="$(count_git_calls "$SMALL_REPO" --no-pr --since=2010-01-01)"
large_count_no_path="$(count_git_calls "$LARGE_REPO" --no-pr --since=2010-01-01)"
small_count_path="$(count_git_calls "$SMALL_REPO" --no-pr --since=2010-01-01 --path=content.txt)"
large_count_path="$(count_git_calls "$LARGE_REPO" --no-pr --since=2010-01-01 --path=content.txt)"

if [ "$small_count_no_path" -le 4 ] && [ "$large_count_no_path" -le 4 ]; then
  pass "git-call count for --no-pr is <=4 on both a 20-commit repo ($small_count_no_path) and a 2,000-commit repo ($large_count_no_path)"
else
  fail "git-call count for --no-pr exceeds 4: small=$small_count_no_path large=$large_count_no_path"
fi

if [ "$small_count_path" -le 6 ] && [ "$large_count_path" -le 6 ]; then
  pass "git-call count for --no-pr --path is <=6 on both a 20-commit repo ($small_count_path) and a 2,000-commit repo ($large_count_path)"
else
  fail "git-call count for --no-pr --path exceeds 6: small=$small_count_path large=$large_count_path"
fi

if [ "$small_count_no_path" = "$large_count_no_path" ]; then
  pass "git-call count for --no-pr is the same constant regardless of repo size ($small_count_no_path)"
else
  fail "git-call count for --no-pr varies with repo size: small=$small_count_no_path large=$large_count_no_path (not a constant)"
fi

# ── (c) jq-call count: small constant, both formats, both repo sizes ──
plain_small_jq="$(count_jq_calls "$SMALL_REPO" --no-pr --since=2010-01-01)"
plain_large_jq="$(count_jq_calls "$LARGE_REPO" --no-pr --since=2010-01-01)"
json_small_jq="$(count_jq_calls "$SMALL_REPO" --no-pr --since=2010-01-01 --format=json)"
json_large_jq="$(count_jq_calls "$LARGE_REPO" --no-pr --since=2010-01-01 --format=json)"

if [ "$plain_small_jq" -le 6 ] && [ "$plain_large_jq" -le 6 ]; then
  pass "jq-call count for plain format is <=6 on both a 20-commit repo ($plain_small_jq) and a 2,000-commit repo ($plain_large_jq)"
else
  fail "jq-call count for plain format exceeds 6: small=$plain_small_jq large=$plain_large_jq"
fi

if [ "$json_small_jq" -le 6 ] && [ "$json_large_jq" -le 6 ]; then
  pass "jq-call count for json format is <=6 on both a 20-commit repo ($json_small_jq) and a 2,000-commit repo ($json_large_jq)"
else
  fail "jq-call count for json format exceeds 6: small=$json_small_jq large=$json_large_jq"
fi

if [ "$plain_small_jq" = "$plain_large_jq" ]; then
  pass "jq-call count for plain format is the same constant regardless of repo size ($plain_small_jq)"
else
  fail "jq-call count for plain format varies with repo size: small=$plain_small_jq large=$plain_large_jq (not a constant)"
fi

if [ "$json_small_jq" = "$json_large_jq" ]; then
  pass "jq-call count for json format is the same constant regardless of repo size ($json_small_jq)"
else
  fail "jq-call count for json format varies with repo size: small=$json_small_jq large=$json_large_jq (not a constant)"
fi

# ── (a) wall-clock bound on the 2,000-commit repo ──────────────────
start_ts="$(date +%s)"
bash "$SCRIPT" --repo="$LARGE_REPO" --no-pr --since=2010-01-01 >/dev/null
run_exit=$?
end_ts="$(date +%s)"
elapsed=$((end_ts - start_ts))

if [ "$run_exit" -eq 0 ]; then
  pass "--no-pr on the 2,000-commit repo exits 0"
else
  fail "--no-pr on the 2,000-commit repo exited $run_exit (expected 0)"
fi

if [ "$elapsed" -le 2 ]; then
  pass "--no-pr on the 2,000-commit repo finishes within 2s wall-clock (${elapsed}s)"
else
  fail "--no-pr on the 2,000-commit repo took ${elapsed}s (expected <=2s) — a red run here on an otherwise-passing git-call-count assertion may be machine load (plan.md Risk 1), not a regression"
fi

echo ""
echo "================================================================"
echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
echo "================================================================"
[ "${FAIL_COUNT}" -gt 0 ] && exit 1
exit 0
