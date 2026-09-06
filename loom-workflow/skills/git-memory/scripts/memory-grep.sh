#!/usr/bin/env bash
#
# memory-grep.sh — retrieval primitive for git-memory skill.
#
# Dumps all memory trailers from git log plus all `## Memory` sections
# from merged PR bodies, producing a plain-text or JSON digest that
# any tool (Claude Code, Cursor, Codex, aider, a human) can ingest.
#
# Parsing strategy:
#   Commit trailers are parsed by `git interpret-trailers --parse`, not
#   by re-splitting a `--pretty=format:` field-delimited output. This
#   eliminates separator-collision bugs (e.g. a trailer value containing
#   `|` or any other ASCII character) — git's own parser is the source
#   of truth for what counts as a trailer.
#
# Minimum git version: this script's extraction pass requires the
# `%(trailers:key=…)` `--format` placeholder with the `key=` and
# `unfold` options (see the citation in extract_commits_ndjson below).
# Verified on this machine (git version 2.50.1, Apple Git-155): `git
# help log` / `man git-log` document `key=` and `unfold` as current
# `%(trailers:...)` options. This machine's man pages and locally
# installed docs do not state which git version FIRST introduced
# `key=` (no shipped release notes to check offline, and the network
# was not consulted) — assumed here, not verified, at git 2.22 (the
# floor this plan assumed going in). Confirm before relying on an
# older git.
#
# Capability check (branch-end fix, W1-02 finding): a git old enough to
# not understand the `key=` filter does not always reject it outright —
# some accept arbitrary `%(...)` placeholder syntax and echo the whole
# `%(trailers:key=…)` string back as LITERAL text instead of expanding
# it. Every commit's fourth field then reads as that literal string, no
# line matches `^Decision: `/`^Learning: `/`^Gotcha: `/`^Related: `, the
# memory-worthy filter drops every record, and the script used to exit
# 0 printing "(none in range)" — a repository full of real trailers
# silently reporting having none, indistinguishable from an empty
# history. extract_commits_ndjson now runs a one-time, cheap probe
# (one extra `git log -1`, no per-commit calls) before the real
# extraction pass: if the probe's own `%(trailers:key=…)` output
# contains the literal substring `%(trailers`, the pass falls back to
# the key-less `%(trailers:unfold)` placeholder (still ONE git-log call
# — no exit-code change) and lets the existing jq stage's case-sensitive
# key re-filter recover the real trailers, since that stage already
# re-filters every line by key regardless of whether git's own key=
# filter ran first. A git that instead REJECTS the placeholder outright
# (fatal, non-zero exit, no output) is left alone — the probe treats a
# failing probe as inconclusive and defers to the unchanged extraction
# git-log call, which fails loudly via its own PIPESTATUS re-exit
# exactly as before. Deliberate choice over `exit 3` (external
# dependency missing): the incompatibility is recoverable without
# degrading the user's result, so recovering silently outranks failing
# loudly for a capability this script can work around at no extra
# per-commit cost — `exit 3` remains the right call for a probe that
# reveals NO working extraction path at all.
#
# A THIRD case exists, since `%(trailers)` and its `unfold` option
# predate the `key=` filter: a git old enough to understand neither
# placeholder would echo the key-less fallback back as literal text
# too — the exact same silent-empty-digest failure mode, one band
# further down. So after selecting the fallback format, the script
# probes ONCE MORE (only on this already-incompatible path — the
# common key=-capable path never pays this second call): if that
# fallback probe ALSO comes back containing the literal `%(trailers`,
# there is no working extraction path at all, and THIS is the `exit 3`
# case — the same class as the missing-jq check — with a message
# naming the missing capability and telling the user to upgrade git to
# at least the version this header states as the assumed minimum.
#
# Usage:
#   memory-grep.sh [--since=<period>] [--limit=<n>] [--repo=<path>]
#                  [--format=plain|json] [--no-pr] [--no-commit]
#   memory-grep.sh --verify <ref> [--repo=<path>]
#   memory-grep.sh --verify-merged <ref> [--repo=<path>]
#   memory-grep.sh --verify-strict <ref> [--repo=<path>]
#
# Defaults:
#   --since='3 months ago'
#   --limit=50         (PR list cap)
#   --repo=.           (current working tree)
#   --format=plain
#
# Filtering semantics (intentional asymmetry):
#   --since  applies to COMMITS only. Uses git log --since under the hood.
#   --limit  applies to PRS only. Caps the number of merged PRs fetched
#            by `gh pr list` (newest first). PRs are not date-filtered
#            because `gh pr list` does not take a date argument without
#            falling back to a search query. If you need date-bounded
#            PRs, re-run with a tighter `--limit` or post-filter the
#            JSON output with jq on `.mergedAt`.
#
# Exit codes:
#   0  success
#   1  usage error
#   2  not a git repo (or, in --verify mode, an unresolvable ref)
#   3  external dependency missing (jq always required; gh required if PR path enabled);
#      also: this git supports neither the `%(trailers:key=...)` nor
#      the key-less `%(trailers:unfold)` --format placeholder that
#      commit-trailer extraction depends on (both capability probes in
#      extract_commits_ndjson came back with the literal placeholder
#      text unexpanded) — upgrade git to at least the version assumed
#      above
#   4  --verify only: a memory check was requested but NO memory trailer
#      (^Decision:/^Learning:/^Gotcha:) was found in the ref's message body
#   4  --verify-merged only: the ref's body has a `## Memory` heading AND
#      no Decision:/Learning:/Gotcha: key anywhere in the body (the #574
#      silent-drop case — a memory-worthy squash landed without its
#      trailer carrier), OR the ref's body is title-only (exactly one
#      non-empty line) AND the title matches the squash-of-PR signature
#      `(#N)` (the #578 case — the merge dialog dropped the entire PR
#      body, so the heading check never got a chance to run)
#   4  --verify-strict only: no Decision:/Learning:/Gotcha: key survives
#      `git interpret-trailers --parse --unfold` (the #575 refinement — a
#      trailer block followed by any non-trailer line stops being the
#      message's true footer, so the parser yields nothing even when a
#      plain text grep still matches the line mid-body)

set -euo pipefail

SINCE='3 months ago'
LIMIT=50
REPO='.'
FORMAT='plain'
INCLUDE_PR=1
INCLUDE_COMMIT=1
INCLUDE_HISTORY=0
MATCH=''
PATHSPEC=''
TOP=''
VERIFY_MODE=0
VERIFY_REF=''
VERIFY_MERGED_MODE=0
VERIFY_MERGED_REF=''
VERIFY_STRICT_MODE=0
VERIFY_STRICT_REF=''

# Extraction includes Related: (relationship context). Verify does NOT —
# the memory-worthy predicate is the three keys Decision/Learning/Gotcha
# only (a Related:-only commit captured no actual memory). Extraction's
# own key set lives in extract_commits_ndjson's jq pass, case-sensitive
# there too (matching the git format's key= case-insensitive match).
VERIFY_KEYS_REGEX='^(Decision|Learning|Gotcha):'
MEMORY_HEADING_REGEX='^## Memory[[:space:]]*$'

usage() {
  cat <<'EOF'
memory-grep.sh — retrieve git-memory entries from a repo

Usage:
  memory-grep.sh [--since=<period>] [--limit=<n>] [--repo=<path>]
                 [--format=plain|json] [--no-pr] [--no-commit]
  memory-grep.sh --verify <ref> [--repo=<path>]
  memory-grep.sh --verify-merged <ref> [--repo=<path>]
  memory-grep.sh --verify-strict <ref> [--repo=<path>]

Options:
  --since=<period>   date filter for COMMITS (default: "3 months ago")
  --limit=<n>        cap on number of merged PRs fetched (default: 50)
  --repo=<path>      working tree path (default: current dir)
  --format=<f>       output format: plain | json (default: plain)
  --no-pr            skip PR body extraction
  --no-commit        skip commit trailer extraction
  --match=<regex>    topic filter: keep only records whose text matches
                     (case-insensitive regex). Searches commit subject +
                     trailer values, and PR title + Memory section.
  --path=<pathspec>  keep only COMMITS touching <pathspec>. Commit-only —
                     PR sections cannot be path-scoped. Does NOT affect
                     liveness (the supersession scan stays full-history).
  --top=<n>          cap displayed commits to the newest <n>; the number
                     suppressed is reported (never silently truncated).
  --history          include superseded records (default: live only). A
                     record is superseded when a LATER commit carries a
                     `Supersedes:` trailer naming it (by PR #N or SHA).
                     Liveness is computed by forward-scan, never stored.
  --verify <ref>     check whether <ref>'s message body carries a memory
                     trailer (^Decision:/^Learning:/^Gotcha:). Exits 0 if
                     present, 4 if absent, 2 if <ref> does not resolve.
                     Text match on the full body — survives squash mid-body
                     under the COMMIT_MESSAGES setting; does not footer-parse.
  --verify-merged <ref>
                     post-merge predicate for a squash-shaped commit.
                     First checks for a suspicious empty body: a
                     title-only body (exactly one non-empty line) whose
                     title matches the squash-of-PR signature `(#N)`
                     exits 4 immediately (the #578 case — the merge
                     dialog dropped the entire PR body, so nothing below
                     can be checked). Otherwise, if the body has NO
                     `## Memory` heading, exits 0 (not memory-worthy —
                     nothing to check). If the heading IS present,
                     requires a Decision:/Learning:/Gotcha: key anywhere
                     in the body — exits 0 if found, 4 if not (the #574
                     silent-drop case: heading survived, trailer carrier
                     didn't). Exits 2 if <ref> does not resolve.
  --verify-strict <ref>
                     diagnostic, parser-strict variant of --verify: the
                     memory key must survive `git interpret-trailers
                     --parse --unfold` (a true trailing footer), not just
                     a text match anywhere in the body. Exits 0 on a
                     parse-level hit, 4 otherwise (the #575 case: a
                     trailer block followed by any non-trailer line
                     empties the parse even though --verify still passes
                     on a text match). Exits 2 if <ref> does not resolve.

Note: --since filters commits by date; --limit caps PR count.
      PRs are not date-filtered (newest N are always taken).

Examples:
  memory-grep.sh --since='6 months ago' --limit=100
  memory-grep.sh --no-pr              # commit trailers only
  memory-grep.sh --match='parser|latency'      # topic recall
  memory-grep.sh --path=src/parser --top=5     # decisions touching a path
  memory-grep.sh --history           # include superseded decisions
  memory-grep.sh --format=json | jq '.commits[]'
  memory-grep.sh --verify HEAD        # did this commit capture memory?
  memory-grep.sh --verify-merged HEAD # did a squash-merge drop its memory?
  memory-grep.sh --verify-strict HEAD # does the memory key survive a strict parse?
EOF
}

# ─── argument parsing ──────────────────────────────────────────────

# --verify / --verify-merged / --verify-strict each take the FOLLOWING
# token as their ref. The for-loop has no lookahead, so a one-shot flag
# per option (expect_ref / expect_merged_ref / expect_strict_ref) captures
# the next token.
expect_ref=0
expect_merged_ref=0
expect_strict_ref=0
for arg in "$@"; do
  if [ "$expect_ref" = 1 ]; then
    VERIFY_REF="$arg"
    expect_ref=0
    continue
  fi
  if [ "$expect_merged_ref" = 1 ]; then
    VERIFY_MERGED_REF="$arg"
    expect_merged_ref=0
    continue
  fi
  if [ "$expect_strict_ref" = 1 ]; then
    VERIFY_STRICT_REF="$arg"
    expect_strict_ref=0
    continue
  fi
  case "$arg" in
    --since=*)   SINCE="${arg#*=}" ;;
    --limit=*)   LIMIT="${arg#*=}" ;;
    --repo=*)    REPO="${arg#*=}" ;;
    --format=*)  FORMAT="${arg#*=}" ;;
    --no-pr)     INCLUDE_PR=0 ;;
    --no-commit) INCLUDE_COMMIT=0 ;;
    --history)   INCLUDE_HISTORY=1 ;;
    --match=*)   MATCH="${arg#*=}" ;;
    --path=*)    PATHSPEC="${arg#*=}" ;;
    --top=*)     TOP="${arg#*=}" ;;
    --verify)    VERIFY_MODE=1; expect_ref=1 ;;
    --verify-merged) VERIFY_MERGED_MODE=1; expect_merged_ref=1 ;;
    --verify-strict) VERIFY_STRICT_MODE=1; expect_strict_ref=1 ;;
    -h|--help)   usage; exit 0 ;;
    *) echo "Unknown argument: $arg" >&2; usage; exit 1 ;;
  esac
done

# ─── shared ref-resolution guard (--verify / --verify-merged / --verify-strict) ───
#
# All three verify modes need the same three checks before touching git
# log: a non-empty ref, a valid git repo, and a resolvable commit. Called
# as a bare statement (never inside an `if`/`while` test), so `exit`
# inside it terminates the whole script under `set -e` exactly like the
# inlined checks it replaces.
#   $1 — the ref string to resolve (may be empty)
#   $2 — the flag name, for the usage-error message (e.g. "--verify")
resolve_ref_or_die() {
  local ref="$1" flag="$2"
  if [ -z "$ref" ]; then
    echo "$flag requires a <ref>" >&2
    usage
    exit 1
  fi
  if ! git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1; then
    echo "Not a git repository: $REPO" >&2
    exit 2
  fi
  if ! git -C "$REPO" rev-parse --verify --quiet "${ref}^{commit}" >/dev/null 2>&1; then
    echo "Unresolvable ref: $ref" >&2
    exit 2
  fi
}

# ─── verify mode (memory-substrate check) ──────────────────────────
#
# Runs before the normal extraction path and exits. Needs neither jq,
# gh, nor the --since/--limit machinery — it grep's a single commit's
# full message body for a memory trailer (text match, so it survives a
# squash that pushes the trailer mid-body under COMMIT_MESSAGES).
if [ "$VERIFY_MODE" = 1 ]; then
  resolve_ref_or_die "$VERIFY_REF" "--verify"
  if git -C "$REPO" log -1 --format='%B' "$VERIFY_REF" \
       | grep -qE "$VERIFY_KEYS_REGEX"; then
    exit 0
  else
    echo "No memory trailer found in $VERIFY_REF" >&2
    exit 4
  fi
fi

# ─── verify-merged mode (post-merge squash-carrier check) ──────────
#
# Post-merge CI predicate for a squash-shaped commit body: no `## Memory`
# heading means the commit was never claimed to be memory-worthy, so
# there is nothing to check (exit 0). The `## Memory` heading present
# AND no Decision:/Learning:/Gotcha: key anywhere in the body is the
# #574 silent-drop case — the commit claimed memory but the trailer
# carrier was lost (exit 4).
if [ "$VERIFY_MERGED_MODE" = 1 ]; then
  resolve_ref_or_die "$VERIFY_MERGED_REF" "--verify-merged"
  merged_body=$(git -C "$REPO" log -1 --format='%B' "$VERIFY_MERGED_REF")

  # Suspicious-empty-body check (the #578 case), runs BEFORE the heading
  # logic: a squash-of-PR-shaped commit (title ends "(#N)") whose body is
  # title-only (exactly one non-empty line) means the merge dialog dropped
  # the entire PR body — the heading check below never even gets a chance
  # to see a missing/present `## Memory` heading, so it silently reads as
  # "not memory-worthy" (exit 0) when it is actually unknowable. A
  # title-only body WITHOUT a "(#N)" suffix is a routine direct commit,
  # not a squash-of-PR shape, so it is not suspicious.
  merged_body_nonempty_lines=$(printf '%s\n' "$merged_body" | grep -c '[^[:space:]]')
  merged_body_title=$(printf '%s\n' "$merged_body" | grep -m1 .)
  if [ "$merged_body_nonempty_lines" -eq 1 ] \
       && printf '%s' "$merged_body_title" | grep -qE '\(#[0-9]+\)$'; then
    echo "suspicious: squash-shaped commit (#N) with title-only body — the PR body did not reach the squash message" >&2
    exit 4
  fi

  if ! printf '%s\n' "$merged_body" | grep -qE "$MEMORY_HEADING_REGEX"; then
    exit 0
  fi
  if printf '%s\n' "$merged_body" | grep -qE "$VERIFY_KEYS_REGEX"; then
    exit 0
  else
    echo "## Memory heading present but no memory key found in $VERIFY_MERGED_REF" >&2
    exit 4
  fi
fi

# ─── verify-strict mode (parser-strict diagnostic check) ───────────
#
# Diagnostic variant of --verify: the #575 refinement. Plain --verify
# text-greps the full body, so it still finds a Decision:/Learning:/
# Gotcha: line even when a non-trailer line follows it — but
# `git interpret-trailers` only reads the message's true trailing
# footer, so that same commit parses to nothing structurally. This mode
# requires the parse-level hit, catching exactly that silent gap.
if [ "$VERIFY_STRICT_MODE" = 1 ]; then
  resolve_ref_or_die "$VERIFY_STRICT_REF" "--verify-strict"
  if git -C "$REPO" log -1 --format='%B' "$VERIFY_STRICT_REF" \
       | git interpret-trailers --parse --unfold 2>/dev/null \
       | grep -qE "$VERIFY_KEYS_REGEX"; then
    exit 0
  else
    echo "No memory trailer survives strict parse in $VERIFY_STRICT_REF" >&2
    exit 4
  fi
fi

case "$FORMAT" in
  plain|json) ;;
  *) echo "Invalid --format: $FORMAT (plain|json)" >&2; exit 1 ;;
esac

# --limit must be a positive integer. Without this guard a non-numeric
# value silently passes through to `gh pr list --limit abc`, which
# returns zero rows and produces the misleading message
# "(none found in last abc merged PRs)".
if ! [[ "$LIMIT" =~ ^[1-9][0-9]*$ ]]; then
  echo "Invalid --limit: $LIMIT (expected positive integer)" >&2
  exit 1
fi

if [ -n "$TOP" ] && ! [[ "$TOP" =~ ^[1-9][0-9]*$ ]]; then
  echo "Invalid --top: $TOP (expected positive integer)" >&2
  exit 1
fi

if ! git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1; then
  echo "Not a git repository: $REPO" >&2
  exit 2
fi

# jq is required for both formats now — the commit extractor builds NDJSON
# regardless of the output format.
if ! command -v jq >/dev/null 2>&1; then
  echo "memory-grep.sh requires jq" >&2
  exit 3
fi

# Validate --match ONCE up front. Otherwise jq's test() throws mid-filter
# under `set -euo pipefail`, aborting with an undocumented exit and one
# raw "Regex failure" line per commit. An agent composing --match from a
# free-text topic can easily pass an unbalanced ( or [ — fail loud and
# clean instead.
if [ -n "$MATCH" ] && ! jq -n --arg m "$MATCH" '"" | test($m; "i")' >/dev/null 2>&1; then
  echo "Invalid --match regex: $MATCH" >&2
  exit 1
fi

# ─── commit trailer extraction + supersession index (one git pass) ─
#
# One `git log` call (plus one more, for the allowed-SHA set, when
# --path narrows the display) replaces the old per-commit subprocess
# loops (one `git log -1` + one `git interpret-trailers` + one `grep`
# per commit, twice over — once for extraction, once for the
# supersession scan). git's own trailer parser is still the source of
# truth: `%(trailers:key=…,unfold)` is the same parser
# `git interpret-trailers --parse --unfold` used, exposed as a format
# placeholder instead of a second process per commit.
#
# wave-end:1-02 grounding (verified against `git --version` 2.50.1
# (Apple Git-155) on this machine, docs read via `man git-log` / `man
# git-interpret-trailers` — this build has no standalone
# gitformat-pretty(1) page; the same "PRETTY FORMATS" text lives
# inside git-log(1)):
#   - git-log(1), PRETTY FORMATS, the `%(trailers[:<option>,...])`
#     entry: "key=<key>: only show trailers with specified <key>.
#     Matching is done case-insensitively and trailing colon is
#     optional. … This option automatically enables the `only` option
#     so that non-trailer lines in the trailer block are hidden." —
#     this is the source for both (a) key= selecting by key
#     case-insensitively (why the jq re-filter below is still needed
#     to reproduce the old case-SENSITIVE match) and (c) the
#     placeholder emitting ONLY trailer lines, never other body text.
#   - Same entry, `unfold[=<bool>]`: "make it behave as if
#     interpret-trailer's --unfold option was given." — the source for
#     (b): `%(trailers:…,unfold)` is declared equivalent to
#     `git-interpret-trailers(1)`'s own `--unfold`, whose OPTIONS
#     section defines it as "If a trailer has a value that runs over
#     multiple lines (aka 'folded'), reformat the value into a single
#     line."
#   - This machine's man pages do not state which git version
#     introduced `key=` on `%(trailers:...)` (the man page documents
#     current behavior, not a changelog); not guessed here — the
#     script header (W2-01) states the minimum git version this
#     change requires, verified separately.
#
# Record separator: every FIELD is delimited by NUL, and git's `-z`
# terminates each commit's whole record with NUL too — so the raw
# stream is ONE flat sequence of NUL-delimited tokens (sha, date,
# subject, trailers, sha, date, subject, trailers, …), split on a
# single byte value and then chunked four tokens per record. NUL is
# the one byte a commit message provably cannot contain (git's own
# object model forbids it), so this encoding is injective for every
# OTHER byte a subject or trailer value might hold — 0x1F, 0x1E, CJK,
# an embedded newline, all round-trip untouched. (wave-end:1-01: an
# earlier revision of this file used `%x1F` between fields instead —
# a subject containing a raw 0x1F byte mis-split the record and
# silently dropped it, because %x1F is NOT provably absent from
# commit text the way NUL is. NUL has no such exposure, so this is
# the smallest change that makes the encoding injective for every
# non-NUL byte.) This file never spells out a raw NUL byte: jq builds
# it at runtime via `[0] | implode`, so it survives any editor/encoding.
#
# `%(trailers:key=…)` matches keys CASE-INSENSITIVELY (unlike the old
# `grep -E '^(Decision|…):'`), so the jq stage below re-filters each
# trailer line with the same case-sensitive key set the old code used
# — a `decision:`/`DECISION:` line stays excluded exactly as before.
#
# --path narrows which commits are DISPLAYED only. It does NOT narrow
# the supersession scan (full history, always), so a superseding commit
# outside the pathspec still retires a shown record.
#
# Emits NDJSON (one object per line), same shape as before:
#   {decision:[...], learning:[...], gotcha:[...], related:[...],
#    sha, date, subject, superseded, superseded_by}

extract_commits_ndjson() {
  local all_records path_shas sup_entries rc
  local trailers_keyfilter trailers_format probe_out probe_rc

  # ─── one-time capability probe (branch-end fix, W1-02) ────────────
  # Cheap: a single `git log -1` with no ref pinned, so it needs neither
  # the repo to have any commits nor any trailers to exist. A probe
  # that itself FAILS (empty repo, or a git that rejects the
  # placeholder outright) is inconclusive here, not a literal-echo
  # finding — it is left to the real extraction git-log call below,
  # which already fails loudly via its own PIPESTATUS re-exit in that
  # case. Only a probe that SUCCEEDS while echoing the placeholder back
  # as literal, UNEXPANDED text is the failure mode this guards: fall
  # back to the key-less `unfold` placeholder, still one single
  # git-log call, and let the jq stage's existing case-sensitive key
  # re-filter recover the real trailers.
  #
  # The check matches the EXACT placeholder text just attempted (not a
  # loose "%(trailers" substring): probing against the repo's real HEAD
  # means an actual trailer VALUE could legitimately contain "%(trailers"
  # as hostile-but-real content (e.g. a Decision: line quoting jq/git
  # syntax) — that must not be mistaken for a git that failed to expand
  # the placeholder. An exact match on the full attempted placeholder
  # string is what an unexpanded echo actually produces (git's `%%` ->
  # literal `%`, and the untouched `(...)` that follows is not itself a
  # placeholder token), so it stays specific to the real failure mode.
  trailers_keyfilter='key=Decision,key=Learning,key=Gotcha,key=Related,key=Supersedes,unfold'
  trailers_format="%(trailers:${trailers_keyfilter})"
  probe_rc=0
  probe_out=$(git -C "$REPO" log -1 --format="$trailers_format" 2>/dev/null) || probe_rc=$?
  if [ "$probe_rc" -eq 0 ] && printf '%s' "$probe_out" | grep -qF -- "$trailers_format"; then
    trailers_format='%(trailers:unfold)'

    # ─── second probe: does THIS git understand %(trailers:unfold) at
    # all? (`%(trailers)`/`unfold` predate `key=`, so a git that fails
    # the first probe usually understands the fallback — but a git old
    # enough to understand neither placeholder would echo the fallback
    # back as literal text too, one band further down the same silent-
    # empty-digest failure mode the finding named. One more `git log -1`
    # here, and ONLY on this already-incompatible path — the common
    # (key=-capable) path never pays this second call.
    probe_rc=0
    probe_out=$(git -C "$REPO" log -1 --format="$trailers_format" 2>/dev/null) || probe_rc=$?
    if [ "$probe_rc" -eq 0 ] && printf '%s' "$probe_out" | grep -qF -- "$trailers_format"; then
      echo "memory-grep.sh: this git does not support the %(trailers:...) --format placeholder (neither the key= filter nor plain unfold) that commit-trailer extraction depends on." >&2
      echo "Upgrade git to at least the version this script's header states as the assumed minimum (git 2.22+, unverified further) and retry." >&2
      exit 3
    fi
  fi

  # git's -z output is NUL-delimited; a bash `$(...)` command
  # substitution silently drops embedded NUL bytes (bash-3.2 and bash-5
  # both do this), so the raw stream is piped STRAIGHT into jq below —
  # never captured into a bash variable first.
  #
  # `all_records=$(git ... | jq ...)` is a nested command substitution
  # inside a function that is ITSELF invoked via command substitution
  # (`commit_records=$(extract_commits_ndjson)` below) — under that
  # nesting, bash's `set -e` does not propagate a failing FIRST command
  # of the pipe (git) when the LAST command (jq) succeeds, even with
  # `pipefail` (a bash quirk with function-in-command-substitution, not
  # present at top level). The old script's fatal-exit-128 behavior on a
  # zero-commit repo (git log fails; nothing captures it) must survive
  # byte-identically, so the subshell explicitly re-exits with git's own
  # PIPESTATUS on failure, and the caller checks $? right after.

  # One jq pass turns the raw -z/%x1F stream into one JSON array: every
  # commit in range, trailer lines grouped by key (still case-preserving
  # — the case-sensitive re-filter happens per key below).
  all_records=$(
    git -C "$REPO" log --since="$SINCE" --no-merges -z --date=short \
      --format="%h%x00%ad%x00%s%x00${trailers_format}" \
      | jq -R -s -c '
          ([0] | implode) as $NUL
          | ([10] | implode) as $LF
          | (split($NUL)) as $tok0
          | ($tok0 | if (length > 0 and .[-1] == "") then .[:-1] else . end) as $tok
          | [
              range(0; ($tok | length) / 4) as $i
              | $tok[$i * 4] as $sha
              | $tok[$i * 4 + 1] as $date
              | $tok[$i * 4 + 2] as $subject
              | ($tok[$i * 4 + 3] // "" | split($LF) | map(select(length > 0))) as $lines
              | {
                  sha: $sha, date: $date, subject: $subject,
                  decision: [ $lines[] | select(test("^Decision: ")) | sub("^Decision: ";"") ],
                  learning: [ $lines[] | select(test("^Learning: ")) | sub("^Learning: ";"") ],
                  gotcha: [ $lines[] | select(test("^Gotcha: ")) | sub("^Gotcha: ";"") ],
                  related: [ $lines[] | select(test("^Related: ")) | sub("^Related: ";"") ],
                  supersedes: [ $lines[] | select(test("^Supersedes: ")) | sub("^Supersedes: ";"") ]
                }
            ]
        '
    git_rc="${PIPESTATUS[0]}"
    [ "$git_rc" -ne 0 ] && exit "$git_rc"
    true
  )
  rc=$?
  [ "$rc" -ne 0 ] && exit "$rc"

  if [ -n "$PATHSPEC" ]; then
    path_shas=$(git -C "$REPO" log --since="$SINCE" --no-merges --format='%h' -- "$PATHSPEC")
  else
    path_shas=''
  fi

  # Supersession map: {token, by_label} per Supersedes: target, built
  # from the SAME unfiltered all_records (never path-narrowed) — a
  # forward-pointer authoring convention is trusted, not enforced, same
  # as the old code. token is "pr:<N>" or "sha:<hex>", normalize_ref's
  # old semantics (a bare "#N" anywhere -> pr; 7-40 hex chars -> sha).
  sup_entries=$(printf '%s' "$all_records" | jq -c '
      [
        .[] | . as $rec
        | ($rec.subject | if test("\\(#[0-9]+\\)") then capture("^.*\\(#(?<n>[0-9]+)\\).*$").n else null end) as $pr
        | ($rec.sha + (if $pr != null then " (PR #" + $pr + ")" else "" end)) as $by_label
        | $rec.supersedes[] as $val
        | (
            if ($val | test("#[0-9]+")) then "pr:" + ($val | capture("^.*#(?<n>[0-9]+).*$").n)
            elif ($val | test("^[0-9a-fA-F]{7,40}$")) then "sha:" + ($val | ascii_downcase)
            else null
            end
          ) as $token
        | select($token != null)
        | {token: $token, by_label: $by_label}
      ]
    ')

  # Final pass: memory-worthy filter (Decision/Learning/Gotcha/Related
  # non-empty; Supersedes-only is NOT memory-worthy, same as before),
  # optional --path narrowing, then liveness lookup (PR number from the
  # record's own "(#N)" subject first, else SHA-prefix match either
  # direction — same order lookup_superseded used, "first match" being
  # the first entry in sup_entries' array order, which is newest-first
  # like the old token<TAB>by_label table scan). Not --history and
  # superseded -> dropped; otherwise annotated. Field order matches the
  # old annotate_commits output exactly (decision/learning/gotcha/
  # related/sha/date/subject/superseded/superseded_by).
  # path_active distinguishes "no --path given" (null $pset, no
  # filtering) from "--path given but it matched zero commits" (an
  # empty $pset array, filtering everything out) — both leave
  # path_shas as an empty bash string, so the string alone can't tell
  # them apart.
  local path_active=0
  [ -n "$PATHSPEC" ] && path_active=1

  printf '%s' "$all_records" | jq -c \
    --argjson sup "$sup_entries" --arg pathset "$path_shas" \
    --argjson path_active "$path_active" --argjson history "$INCLUDE_HISTORY" '
      ([10] | implode) as $LF
      | . as $all
      | (if $path_active == 1 then ($pathset | split($LF) | map(select(length > 0))) else null end) as $pset
      | $all[]
      | select((.decision | length) > 0 or (.learning | length) > 0 or (.gotcha | length) > 0 or (.related | length) > 0)
      | . as $rec
      | select($pset == null or ($pset | index($rec.sha)) != null)
      | ($rec.subject | if test("\\(#[0-9]+\\)") then capture("^.*\\(#(?<n>[0-9]+)\\).*$").n else null end) as $subj_pr
      | (
          if $subj_pr != null then ($sup | map(select(.token == ("pr:" + $subj_pr))) | (.[0].by_label // null))
          else null
          end
        ) as $by_from_pr
      | (
          if $by_from_pr != null then $by_from_pr
          else (
            $sup
            | map(select(.token | startswith("sha:")))
            | map(select((.token[4:]) as $t | ($t | startswith($rec.sha)) or ($rec.sha | startswith($t))))
            | (.[0].by_label // null)
          )
          end
        ) as $by
      | if $by != null then
          (if ($history == 1) then
            { decision: $rec.decision, learning: $rec.learning, gotcha: $rec.gotcha, related: $rec.related,
              sha: $rec.sha, date: $rec.date, subject: $rec.subject,
              superseded: true, superseded_by: $by }
          else empty end)
        else
          { decision: $rec.decision, learning: $rec.learning, gotcha: $rec.gotcha, related: $rec.related,
            sha: $rec.sha, date: $rec.date, subject: $rec.subject,
            superseded: false, superseded_by: null }
        end
    '
}

commit_records=''
COMMIT_DROPPED=0
if [ "$INCLUDE_COMMIT" = 1 ]; then
  commit_records=$(extract_commits_ndjson)

  # --match topic filter, applied AFTER liveness annotation so it narrows
  # the view only. Searchable text = subject + all trailer values.
  if [ -n "$MATCH" ] && [ -n "$commit_records" ]; then
    commit_records=$(printf '%s\n' "$commit_records" | jq -c --arg m "$MATCH" \
      'select((([.subject] + .decision + .learning + .gotcha + .related)
                | join(" ")) | test($m; "i"))')
  fi

  # --top cap. Records are already reverse-chronological (newest first),
  # so head keeps the newest N. Suppressed count is reported, never
  # silently dropped.
  if [ -n "$TOP" ] && [ -n "$commit_records" ]; then
    _n=$(printf '%s\n' "$commit_records" | grep -c .)
    if [ "$_n" -gt "$TOP" ]; then
      COMMIT_DROPPED=$((_n - TOP))
      commit_records=$(printf '%s\n' "$commit_records" | head -n "$TOP")
    fi
  fi
fi

# ─── PR body Memory-section extraction ─────────────────────────────

pr_records=''
if [ "$INCLUDE_PR" = 1 ]; then
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    pr_records=$(
      gh pr list \
        --repo "$(git -C "$REPO" config --get remote.origin.url 2>/dev/null || echo '')" \
        --state merged \
        --limit "$LIMIT" \
        --json number,title,mergedAt,body \
        2>/dev/null \
        | jq -c '
            .[]
            | select(.body | test("(?m)^## Memory"))
            | {
                number,
                title,
                mergedAt,
                memory: (
                  .body
                  | capture("(?s)^(?:.*?)\n## Memory\\s*\n(?<m>.*?)(?:\n## |\n🤖|$)"; "m")
                  | .m
                  // ""
                  | sub("\\s+$"; "")
                )
              }
          ' 2>/dev/null || true
    )
  fi
fi

# --match filters PRs by title + Memory-section text. (--path is
# commit-only: gh pr list cannot filter by pathspec, so PR sections are
# never path-scoped — see usage.)
if [ -n "$MATCH" ] && [ -n "$pr_records" ]; then
  pr_records=$(printf '%s\n' "$pr_records" | jq -c --arg m "$MATCH" \
    'select(((.title // "") + " " + (.memory // "")) | test($m; "i"))')
fi

# ─── emit output ───────────────────────────────────────────────────

case "$FORMAT" in
  plain)
    hdr="# git-memory digest — repo=$REPO since=\"$SINCE\""
    [ -n "$MATCH" ]    && hdr="$hdr match=\"$MATCH\""
    [ -n "$PATHSPEC" ] && hdr="$hdr path=\"$PATHSPEC\""
    echo "$hdr"
    echo
    if [ "$INCLUDE_COMMIT" = 1 ]; then
      echo "## Commit trailers"
      if [ -n "$commit_records" ]; then
        echo
        # One jq -r pass over the whole NDJSON stream renders every
        # record's header line, its trailer groups (render_group's old
        # single-entry vs "(i/N)" multi-entry layout), and the blank
        # line after it — replacing the old per-record loop that spawned
        # one `jq` per field plus one per trailer key (up to 8 per
        # record). jq itself still only ever sees each record's fields
        # as opaque JSON string VALUES here (never re-parsed as jq
        # syntax or shell), so a hostile trailer value survives verbatim.
        printf '%s\n' "$commit_records" | jq -r '
            def render_group(lbl; entries):
              (entries | length) as $n
              | if $n == 0 then empty
                elif $n == 1 then "  " + lbl + ": " + entries[0]
                else (
                  range(0; $n) as $i
                  | "  " + lbl + " (" + (($i + 1) | tostring) + "/" + ($n | tostring) + "): " + entries[$i]
                )
                end;
            (
              (if ((.superseded_by // "") != "") then
                "### " + .sha + "  " + .date + "  " + .subject + "  [SUPERSEDED by " + .superseded_by + "]"
              else
                "### " + .sha + "  " + .date + "  " + .subject
              end),
              render_group("Decision"; .decision),
              render_group("Learning"; .learning),
              render_group("Gotcha"; .gotcha),
              render_group("Related"; .related),
              ""
            )
          '
        [ "$COMMIT_DROPPED" -gt 0 ] && \
          echo "(… $COMMIT_DROPPED more matches suppressed; raise --top or narrow --match/--path)" && echo
      else
        if [ -n "$MATCH" ]; then
          echo "(no memory matches \"$MATCH\")"
        elif [ -n "$PATHSPEC" ]; then
          echo "(no memory touched \"$PATHSPEC\")"
        else
          echo "(none in range)"
        fi
        echo
      fi
    fi

    if [ -n "$pr_records" ]; then
      echo "## PR Memory sections"
      echo
      printf '%s\n' "$pr_records" | jq -r '
        "### PR #" + (.number|tostring) + "  " + (.mergedAt[:10]) + "  " + .title + "\n" +
        (.memory | split("\n") | map("  " + .) | join("\n")) + "\n"
      '
    elif [ "$INCLUDE_PR" = 1 ]; then
      echo "## PR Memory sections"
      if ! command -v gh >/dev/null 2>&1; then
        echo "(gh CLI not installed — skipped)"
      elif ! gh auth status >/dev/null 2>&1; then
        echo "(gh CLI not authenticated — skipped)"
      else
        echo "(none found in last $LIMIT merged PRs)"
      fi
      echo
    fi
    ;;

  json)
    jq -n \
      --arg since "$SINCE" \
      --arg repo "$REPO" \
      --arg match "$MATCH" \
      --arg path "$PATHSPEC" \
      --argjson suppressed "$COMMIT_DROPPED" \
      --argjson commits "$(
        if [ -z "$commit_records" ]; then
          echo '[]'
        else
          printf '%s\n' "$commit_records" | jq -sc '.'
        fi
      )" \
      --argjson prs "$(
        if [ -z "$pr_records" ]; then
          echo '[]'
        else
          printf '%s\n' "$pr_records" | jq -sc '.'
        fi
      )" \
      '{repo: $repo, since: $since, match: (if $match == "" then null else $match end), path: (if $path == "" then null else $path end), commits_suppressed: $suppressed, commits: $commits, prs: $prs}'
    ;;
esac
