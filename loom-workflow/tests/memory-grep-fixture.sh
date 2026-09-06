#!/usr/bin/env bash
# memory-grep-fixture.sh — deterministic fixture repo for memory-grep golden
# tests (W1-01, docs/loom/2026-09-06-memory-grep-single-pass).
#
# Sourced, never executed directly. Defines one function:
#
#   build_memory_grep_fixture <target-dir>
#
# which git-inits a repo at <target-dir> and populates it with a fixed
# sequence of commits — fixed author/committer name+email, fixed per-commit
# GIT_AUTHOR_DATE == GIT_COMMITTER_DATE (ISO 8601, +0000), fixed
# core.abbrev=7 — so every short SHA the fixture produces is the same on
# every machine and every run. Callers MUST pass --since=2026-01-01 (or
# later) to memory-grep.sh; the fixture's dates are chosen to sit inside
# that window except the one commit deliberately dated before it.
#
# Every commit below is annotated with the Acceptance-3 case (from
# docs/loom/2026-09-06-memory-grep-single-pass/plan.md, task W1-01) it
# exists to cover; the equivalence suite names each one in its PASS output.
#
# Usage (from another test script):
#   source ".../memory-grep-fixture.sh"
#   build_memory_grep_fixture "$TMP_REPO"

build_memory_grep_fixture() {
  local dir="$1"

  git -C "$dir" init -q
  git -C "$dir" symbolic-ref HEAD refs/heads/main
  git -C "$dir" config user.name "Fixture Bot"
  git -C "$dir" config user.email "fixture@example.com"
  git -C "$dir" config core.autocrlf false
  git -C "$dir" config commit.gpgsign false
  git -C "$dir" config core.abbrev 7

  export GIT_AUTHOR_NAME="Fixture Bot"
  export GIT_AUTHOR_EMAIL="fixture@example.com"
  export GIT_COMMITTER_NAME="Fixture Bot"
  export GIT_COMMITTER_EMAIL="fixture@example.com"

  _mgf_commit() { # <date> <subject> [trailer-paragraph]
    local date="$1" subject="$2" body="${3:-}"
    export GIT_AUTHOR_DATE="${date}T00:00:00+0000"
    export GIT_COMMITTER_DATE="${date}T00:00:00+0000"
    if [ -n "$body" ]; then
      git -C "$dir" commit -q -m "$subject" -m "$body"
    else
      git -C "$dir" commit -q -m "$subject"
    fi
  }

  # Case: a memory commit OUTSIDE --since (dated before the fixed window).
  echo old > "$dir/old.txt"; git -C "$dir" add old.txt
  _mgf_commit "2025-06-01" "feat: old decision before window (#1)" \
    "Decision: old decision before window"

  # Base commit, no trailer — establishes the tracked files later commits
  # edit (so --path can distinguish them). Not memory-worthy itself.
  echo base > "$dir/parser.txt"; git -C "$dir" add parser.txt
  echo base > "$dir/cache.txt";  git -C "$dir" add cache.txt
  echo base > "$dir/README";     git -C "$dir" add README
  _mgf_commit "2026-01-02" "chore: init tracked files (#2)"

  # Case: subject ends "(#N)" — true of every commit in this fixture;
  # verified structurally rather than singled out.

  # Branch + merge, for the merge-commit-with-trailer case below.
  git -C "$dir" checkout -q -b feature
  echo feature > "$dir/feature.txt"; git -C "$dir" add feature.txt
  _mgf_commit "2026-01-03" "feat: side feature (#3)" \
    "Decision: side feature decision"
  git -C "$dir" checkout -q main
  export GIT_AUTHOR_DATE="2026-01-04T00:00:00+0000"
  export GIT_COMMITTER_DATE="2026-01-04T00:00:00+0000"
  git -C "$dir" merge -q --no-ff -m "merge: combine feature (#4)" \
    -m "Decision: merged decision that must be excluded by --no-merges" \
    feature
  git -C "$dir" branch -q -d feature

  # Case: lowercase "decision:" key — must NOT be picked up (case-sensitive
  # grep on the old path; the W1-02 risk this pins for the new path too).
  echo lower > "$dir/lower.txt"; git -C "$dir" add lower.txt
  _mgf_commit "2026-01-05" "chore: lowercase key check (#5)" \
    "decision: this should not match (lowercase key)"

  # Case: a Related:-only commit (no Decision/Learning/Gotcha).
  echo related > "$dir/related.txt"; git -C "$dir" add related.txt
  _mgf_commit "2026-01-06" "docs: note related context (#6)" \
    "Related: something to note"

  # Case: trailer value with |, :, #, CJK, and a folded continuation line
  # (git interpret-trailers --unfold joins the indented line into the one
  # above it into a single value).
  echo special > "$dir/special.txt"; git -C "$dir" add special.txt
  _mgf_commit "2026-01-07" "feat: special chars trailer (#7)" \
    "$(printf 'Decision: contains pipe | colon: and hash #9 中文你好\n continuation folded in')"

  # Case: Supersedes: by PR number — approach A (target) then approach B
  # (superseder), both touching parser.txt (also the --path fixture).
  echo approach-a > "$dir/parser.txt"; git -C "$dir" add parser.txt
  _mgf_commit "2026-01-08" "feat: approach A for parser (#8)" \
    "Decision: use approach A for parser.txt"
  echo approach-b > "$dir/parser.txt"; git -C "$dir" add parser.txt
  _mgf_commit "2026-01-09" "feat: switch to approach B for parser (#9)" \
    "$(printf 'Decision: use approach B for parser.txt\nSupersedes: PR #8')"

  # Case: Supersedes: by SHA — cache v1 (target) then a revert (superseder)
  # naming it by full SHA, both touching cache.txt.
  echo cache-v1 > "$dir/cache.txt"; git -C "$dir" add cache.txt
  _mgf_commit "2026-01-10" "feat: cache layer v1 (#10)" \
    "Learning: cache layer v1 gotcha"
  local sha_cache_v1
  sha_cache_v1="$(git -C "$dir" rev-parse HEAD)"
  echo cache-v2 > "$dir/cache.txt"; git -C "$dir" add cache.txt
  _mgf_commit "2026-01-11" "revert: drop cache layer v1 (#11)" \
    "$(printf 'Gotcha: cache layer v1 was wrong\nSupersedes: %s' "$sha_cache_v1")"

  # Case: a commit touching a distinct path (README), for --path scoping.
  echo readme-note > "$dir/README"; git -C "$dir" add README
  _mgf_commit "2026-01-12" "docs: readme note (#12)" \
    "Gotcha: parser edge case in docs"

  # Case: a trailer block followed by a non-trailer line — parses to
  # nothing under `git interpret-trailers --parse` (the #575 case). The
  # commit is skipped entirely by extract_commits_ndjson.
  echo weird > "$dir/weird.txt"; git -C "$dir" add weird.txt
  _mgf_commit "2026-01-13" "fix: weird trailer parse (#13)" \
    "$(printf 'Decision: this looks like a trailer\nbut a non-trailer line follows immediately')"

  unset -f _mgf_commit
}
