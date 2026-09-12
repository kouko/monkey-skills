#!/usr/bin/env bash
# test-memory-grep-perf.sh
#
# Speed contract for memory-grep.sh (W1-02,
# docs/loom/2026-09-06-memory-grep-single-pass/plan.md). The rewrite
# replaces per-commit subprocess loops with one git pass, so this suite
# asserts two things a byte-diff equivalence oracle cannot:
#
#   (a) wall-clock: `--no-pr` on a 2,000-commit fixture (300
#       memory-worthy, 20 with Supersedes:) finishes within a bound
#       measured with a monotonic SUB-second clock (wave-end:1-05:
#       `date +%s` whole-second timestamps cannot enforce a 2-second
#       bound — a ~2.9s run can report "2s" elapsed and pass a broken
#       gate. `python3 -c 'import time; print(time.monotonic())'` is
#       already a dependency of this repo's Python test suite, so no
#       new tool is added; bash 3.2 has no $EPOCHREALTIME of its own).
#       The intent's local bound is 2.0s; CI's tolerance is looser and
#       stated separately at the assertion itself, since a loaded
#       runner failing only the time bound (not the git/jq-call-count
#       gates, which are deterministic) should be read as load, not a
#       regression.
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
#
# The history is imported with `git fast-import` (W1-01) instead of one
# `git commit` process per commit: the 2,000-commit fixture cost 66s of
# this suite's 72s wall clock that way. TWO import passes are needed,
# because the last `supersede_count` memory commits cite the SHA of one
# of the earliest ones in a `Supersedes:` trailer and a SHA is only
# known once its commit exists — pass 1 writes every commit up to the
# first superseding one and exports its marks, pass 2 resolves the
# cited SHAs from that marks file and writes the rest. Messages,
# identities and per-index dates are byte-identical to what the
# previous `git commit -m` loop produced for the same index.
build_perf_repo() {
  local dir="$1" n="$2" memory_count="$3" supersede_count="$4"
  mkdir -p "$dir"
  git -C "$dir" init -q
  git -C "$dir" symbolic-ref HEAD refs/heads/main
  git -C "$dir" config user.email "fixture@example.com"
  git -C "$dir" config user.name "Fixture Bot"
  git -C "$dir" config commit.gpgsign false

  # python3 is already a dependency of this script (the monotonic clock
  # below), so emitting the stream from it adds no new tool and no new
  # file. Parameters travel in the environment: the heredoc is quoted,
  # so nothing in the program below is shell-expanded.
  FIXTURE_DIR="$dir" FIXTURE_N="$n" FIXTURE_MEMORY="$memory_count" \
    FIXTURE_SUPERSEDE="$supersede_count" python3 - <<'PY'
import os
import subprocess
from datetime import datetime, timezone

d = os.environ["FIXTURE_DIR"]
N = int(os.environ["FIXTURE_N"])
MEM = int(os.environ["FIXTURE_MEMORY"])
SUP = int(os.environ["FIXTURE_SUPERSEDE"])


def ident(i):
    # The same per-index date the shell loop derived, in the raw
    # "<epoch> +0000" form fast-import wants. The old loop handed
    # "<date>T00:00:00+0000" to GIT_{AUTHOR,COMMITTER}_DATE, so the
    # epoch is computed in UTC — a local-time conversion here would
    # shift every commit date by the runner's offset.
    year = 2015 + i // 336
    month = (i // 28) % 12 + 1
    day = i % 28 + 1
    ts = int(datetime(year, month, day, tzinfo=timezone.utc).timestamp())
    return "Fixture Bot <fixture@example.com> %d +0000" % ts


def message(i, supersedes):
    if i >= MEM:
        return "chore: commit %d (#%d)\n" % (i, i + 1000)
    if supersedes:
        return ("fix: superseding decision %d (#%d)\n\n"
                "Gotcha: superseding decision %d\n"
                "Supersedes: %s\n" % (i, i + 1000, i, supersedes))
    return ("feat: memory decision %d (#%d)\n\n"
            "Decision: memory decision number %d\n" % (i, i + 1000, i))


def stream(lo, hi, cited):
    out = []
    for i in range(lo, hi):
        supersedes = ""
        if SUP > 0 and MEM - SUP <= i < MEM:
            # Pair the last `SUP` memory commits with the earliest
            # `SUP` memory SHAs, exactly as the shell loop did.
            supersedes = cited[i - (MEM - SUP)]
        body = message(i, supersedes).encode()
        who = ident(i).encode()
        out.append(b"commit refs/heads/main\nmark :%d\nauthor %s\n"
                   b"committer %s\ndata %d\n" % (i + 1, who, who, len(body)))
        out.append(body)
        if i == lo and lo > 0:
            # A fresh fast-import process needs the branch's existing
            # tip named explicitly as this commit's parent.
            out.append(b"from refs/heads/main^0\n")
        blob = ("content at commit %d\n" % i).encode()
        out.append(b"M 100644 inline content.txt\ndata %d\n" % len(blob))
        out.append(blob)
        out.append(b"\n")
    return b"".join(out)


def fast_import(payload, export_marks=None):
    cmd = ["git", "-C", d, "fast-import", "--quiet"]
    if export_marks:
        cmd.append("--export-marks=" + export_marks)
    subprocess.run(cmd, input=payload, check=True)


split = MEM - SUP if SUP > 0 else N
marks_path = os.path.join(d, "fixture-marks")
fast_import(stream(0, min(split, N), []), export_marks=marks_path)
if split < N:
    marks = {}
    with open(marks_path) as fh:
        for line in fh:
            mark, sha = line.split()
            marks[int(mark[1:])] = sha
    fast_import(stream(split, N, [marks[i + 1] for i in range(SUP)]))
os.remove(marks_path)
# fast-import only moves the ref; give the repo a populated index and
# worktree, as the `git commit` loop left behind.
subprocess.run(["git", "-C", d, "reset", "-q", "--hard", "refs/heads/main"],
               check=True)
PY
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

# ── fixture verification (wave-end:1-04): assert record counts BEFORE
# using the fixture for timing/subprocess-count assertions. Every
# assertion below this point discards stdout (>/dev/null) or only
# counts subprocess invocations, so the fixture could silently regress
# to zero live records (the exact class of bug W1-03 found and fixed)
# while every count/timing assertion stayed green. Verify shape via
# --format=json --history first: 300 total commit records, exactly 20
# marked superseded, and the default (live-only) run's 280 = 300 - 20.
large_json_history="$(bash "$SCRIPT" --repo="$LARGE_REPO" --no-pr --since=2010-01-01 --format=json --history)"
large_total_records="$(printf '%s' "$large_json_history" | jq '.commits | length')"
large_superseded_records="$(printf '%s' "$large_json_history" | jq '[.commits[] | select(.superseded == true)] | length')"
large_json_default="$(bash "$SCRIPT" --repo="$LARGE_REPO" --no-pr --since=2010-01-01 --format=json)"
large_live_records="$(printf '%s' "$large_json_default" | jq '.commits | length')"

if [ "$large_total_records" -eq 300 ]; then
  pass "the 2,000-commit fixture yields exactly 300 commit records (--format=json --history)"
else
  fail "the 2,000-commit fixture yields $large_total_records commit records, expected 300"
fi

if [ "$large_superseded_records" -eq 20 ]; then
  pass "the 2,000-commit fixture marks exactly 20 records superseded"
else
  fail "the 2,000-commit fixture marks $large_superseded_records records superseded, expected 20"
fi

if [ "$large_live_records" -eq 280 ]; then
  pass "the 2,000-commit fixture's default (live-only) run yields exactly 280 commit records (300 - 20 superseded)"
else
  fail "the 2,000-commit fixture's default run yields $large_live_records commit records, expected 280 (300 - 20 superseded)"
fi

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
# wave-end:1-05: a monotonic SUB-second clock, not `date +%s` — whole
# seconds cannot enforce a 2-second bound (a run taking 2.9s can
# report an elapsed of "2"). python3's time.monotonic() is already a
# dependency of this repo's Python test suite; no new tool is added.
start_ts="$(python3 -c 'import time; print(time.monotonic())')"
bash "$SCRIPT" --repo="$LARGE_REPO" --no-pr --since=2010-01-01 >/dev/null
run_exit=$?
end_ts="$(python3 -c 'import time; print(time.monotonic())')"
elapsed="$(python3 -c "print(f'{${end_ts} - ${start_ts}:.3f}')")"

if [ "$run_exit" -eq 0 ]; then
  pass "--no-pr on the 2,000-commit repo exits 0"
else
  fail "--no-pr on the 2,000-commit repo exited $run_exit (expected 0)"
fi

# The subprocess-count assertions above are the deterministic gate;
# this timing assertion is secondary and load-sensitive. Two bounds,
# stated separately: the intent's LOCAL bound is 2.0s (asserted below
# as a distinct pass line so it stays visible); CI's TOLERANCE is a
# looser 5.0s, because a loaded CI runner can miss 2.0s for reasons
# unrelated to the code under test — only a breach of the 5.0s
# tolerance is scored FAIL.
if python3 -c "import sys; sys.exit(0 if ${elapsed} <= 5.0 else 1)"; then
  if python3 -c "import sys; sys.exit(0 if ${elapsed} <= 2.0 else 1)"; then
    pass "--no-pr on the 2,000-commit repo finishes within the intent's 2.0s local bound (${elapsed}s, monotonic sub-second clock)"
  else
    pass "--no-pr on the 2,000-commit repo finishes within the 5.0s CI tolerance (${elapsed}s) but not the intent's 2.0s local bound — read as runner load, not a regression"
  fi
else
  fail "--no-pr on the 2,000-commit repo took ${elapsed}s (expected <=5.0s CI tolerance; intent's local bound is 2.0s) — a red run here on an otherwise-passing git-call-count assertion may be machine load (plan.md Risk 1), not a regression"
fi

echo ""
echo "================================================================"
echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
echo "================================================================"
[ "${FAIL_COUNT}" -gt 0 ] && exit 1
exit 0
