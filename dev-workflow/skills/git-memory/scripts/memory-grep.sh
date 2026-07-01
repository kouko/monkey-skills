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
# Usage:
#   memory-grep.sh [--since=<period>] [--limit=<n>] [--repo=<path>]
#                  [--format=plain|json] [--no-pr] [--no-commit]
#   memory-grep.sh --verify <ref> [--repo=<path>]
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
#   3  external dependency missing (jq always required; gh required if PR path enabled)
#   4  --verify only: a memory check was requested but NO memory trailer
#      (^Decision:/^Learning:/^Gotcha:) was found in the ref's message body

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

# Extraction includes Related: (relationship context). Verify does NOT —
# the memory-worthy predicate is the three keys Decision/Learning/Gotcha
# only (a Related:-only commit captured no actual memory).
TRAILER_KEYS_REGEX='^(Decision|Learning|Gotcha|Related):'
VERIFY_KEYS_REGEX='^(Decision|Learning|Gotcha):'

usage() {
  cat <<'EOF'
memory-grep.sh — retrieve git-memory entries from a repo

Usage:
  memory-grep.sh [--since=<period>] [--limit=<n>] [--repo=<path>]
                 [--format=plain|json] [--no-pr] [--no-commit]
  memory-grep.sh --verify <ref> [--repo=<path>]

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
EOF
}

# ─── render helper (plain format) ──────────────────────────────────
#
# Render a trailer group as one or more indented lines.
#   $1 — label (e.g. "Decision")
#   $2 — newline-separated entries
# Single entry:   "  Decision: <text>"
# Multiple:       "  Decision (1/N): <text>" one per line
render_group() {
  [ -z "${2:-}" ] && return 0
  local entries="$2"
  local n
  n=$(printf '%s\n' "$entries" | wc -l | tr -d ' ')
  if [ "$n" -eq 1 ]; then
    printf '  %s: %s\n' "$1" "$entries"
  else
    printf '%s\n' "$entries" \
      | awk -v L="$1" -v N="$n" '{printf "  %s (%d/%d): %s\n", L, NR, N, $0}'
  fi
}

# ─── argument parsing ──────────────────────────────────────────────

# --verify takes the FOLLOWING token as its ref. The for-loop has no
# lookahead, so a one-shot flag (expect_ref) captures the next token.
expect_ref=0
for arg in "$@"; do
  if [ "$expect_ref" = 1 ]; then
    VERIFY_REF="$arg"
    expect_ref=0
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
    -h|--help)   usage; exit 0 ;;
    *) echo "Unknown argument: $arg" >&2; usage; exit 1 ;;
  esac
done

# ─── verify mode (memory-substrate check) ──────────────────────────
#
# Runs before the normal extraction path and exits. Needs neither jq,
# gh, nor the --since/--limit machinery — it grep's a single commit's
# full message body for a memory trailer (text match, so it survives a
# squash that pushes the trailer mid-body under COMMIT_MESSAGES).
if [ "$VERIFY_MODE" = 1 ]; then
  if [ -z "$VERIFY_REF" ]; then
    echo "--verify requires a <ref>" >&2
    usage
    exit 1
  fi
  if ! git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1; then
    echo "Not a git repository: $REPO" >&2
    exit 2
  fi
  if ! git -C "$REPO" rev-parse --verify --quiet "${VERIFY_REF}^{commit}" >/dev/null 2>&1; then
    echo "Unresolvable ref: $VERIFY_REF" >&2
    exit 2
  fi
  if git -C "$REPO" log -1 --format='%B' "$VERIFY_REF" \
       | grep -qE "$VERIFY_KEYS_REGEX"; then
    exit 0
  else
    echo "No memory trailer found in $VERIFY_REF" >&2
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

# ─── commit trailer extraction (Layer 2 — git's own parser) ────────
#
# Emits NDJSON (one object per line) for each memory-worthy commit:
#   {sha, date, subject, decision:[...], learning:[...], gotcha:[...], related:[...]}

extract_commits_ndjson() {
  # --path narrows which commits are DISPLAYED. It is intentionally NOT
  # applied to build_supersession_index (which scans full history), so a
  # superseding commit outside the pathspec still retires a shown record.
  # Collect SHAs first (bash-3.2 + set -u safe: no empty-array expansion).
  local shas
  if [ -n "$PATHSPEC" ]; then
    shas=$(git -C "$REPO" log --since="$SINCE" --no-merges --format='%H' -- "$PATHSPEC")
  else
    shas=$(git -C "$REPO" log --since="$SINCE" --no-merges --format='%H')
  fi
  printf '%s\n' "$shas" \
    | while read -r full_sha; do
        [ -z "$full_sha" ] && continue

        # Extract trailer lines via git's own parser, filtered to our keys.
        local trailer_lines
        trailer_lines=$(
          git -C "$REPO" log -1 --format='%B' "$full_sha" \
            | git interpret-trailers --parse --unfold 2>/dev/null \
            | grep -E "$TRAILER_KEYS_REGEX" \
            || true
        )

        # No memory trailers → skip this commit entirely.
        [ -z "$trailer_lines" ] && continue

        # Group trailer lines by key into {decision, learning, gotcha, related} arrays.
        local trailers_obj
        trailers_obj=$(
          printf '%s\n' "$trailer_lines" \
            | jq -R -n '
                [inputs | capture("^(?<k>[^:]+): (?<v>.*)$")
                        | {key: (.k | ascii_downcase), value: .v}]
                | group_by(.key)
                | map({(.[0].key): map(.value)})
                | add // {}
                | {decision: (.decision // []),
                   learning: (.learning // []),
                   gotcha:   (.gotcha   // []),
                   related:  (.related  // [])}
              '
        )

        # Metadata for header. Use %x1F as local separator — we control these fields
        # (short-sha is hex, date is YYYY-MM-DD, subject can contain any char
        # except 0x1F in practice).
        local meta sha_short date subject
        meta=$(git -C "$REPO" log -1 --format='%h%x1F%ad%x1F%s' --date=short "$full_sha")
        sha_short=${meta%%$'\x1F'*}
        meta=${meta#*$'\x1F'}
        date=${meta%%$'\x1F'*}
        subject=${meta#*$'\x1F'}

        jq -nc \
          --arg sha "$sha_short" \
          --arg date "$date" \
          --arg subject "$subject" \
          --argjson trailers "$trailers_obj" \
          '$trailers + {sha: $sha, date: $date, subject: $subject}'
      done
}

# ─── supersession index (Supersedes: trailer → liveness) ───────────
#
# Append-only substrate: an earlier decision can't be edited, so the
# replacement commit carries a backward-pointing `Supersedes:` trailer
# (by `PR #N` or by SHA). Liveness is COMPUTED, never stored — a record
# is superseded iff some later commit names it. bash-3.2-safe: no
# associative arrays; the map is a `token<TAB>by_label` text table.

# normalize_ref <value> → "pr:<N>" | "sha:<hex>" | "" (unrecognized)
normalize_ref() {
  local v="$1"
  if printf '%s' "$v" | grep -qE '#[0-9]+'; then
    printf 'pr:%s' "$(printf '%s' "$v" | sed -n 's/.*#\([0-9][0-9]*\).*/\1/p')"
  elif printf '%s' "$v" | grep -qiE '^[0-9a-f]{7,40}$'; then
    printf 'sha:%s' "$(printf '%s' "$v" | tr 'A-Z' 'a-z')"
  fi
}

# Emit one `token<TAB>by_label` line per Supersedes: target. Scans ALL
# commits in range (not just memory-worthy ones) so a Supersedes-only
# commit still registers. Note: a superseding commit OUTSIDE the --since
# window won't be seen — widen --since to resurface old supersessions.
# The map is order-free; "later-supersedes-earlier" is guaranteed by the
# backward-pointer authoring convention, not enforced here (a forward or
# self-referential Supersedes: would mis-hide a live record).
build_supersession_index() {
  git -C "$REPO" log --since="$SINCE" --no-merges --format='%H' \
    | while read -r sha; do
        [ -z "$sha" ] && continue
        local sup_lines
        sup_lines=$(
          git -C "$REPO" log -1 --format='%B' "$sha" \
            | git interpret-trailers --parse --unfold 2>/dev/null \
            | grep -E '^Supersedes:' || true
        )
        [ -z "$sup_lines" ] && continue
        local by_label by_pr
        by_label=$(git -C "$REPO" log -1 --format='%h' "$sha")
        by_pr=$(git -C "$REPO" log -1 --format='%s' "$sha" \
          | sed -n 's/.*(#\([0-9][0-9]*\)).*/\1/p')
        [ -n "$by_pr" ] && by_label="$by_label (PR #$by_pr)"
        printf '%s\n' "$sup_lines" | while IFS= read -r line; do
          local val token
          val=$(printf '%s' "${line#Supersedes:}" | sed 's/^ *//; s/ *$//')
          token=$(normalize_ref "$val")
          [ -n "$token" ] && printf '%s\t%s\n' "$token" "$by_label"
        done
      done
}

# lookup_superseded <short_sha> <subject> → by_label if superseded, else ""
# Matches by PR number (from the subject's "(#N)") or by SHA prefix.
lookup_superseded() {
  local short="$1" subject="$2" pr
  pr=$(printf '%s' "$subject" | sed -n 's/.*(#\([0-9][0-9]*\)).*/\1/p')
  if [ -n "$pr" ]; then
    local hit
    hit=$(printf '%s\n' "$SUPERSEDE_MAP" \
      | awk -F'\t' -v p="pr:$pr" '$1==p {print $2; exit}')
    [ -n "$hit" ] && { printf '%s' "$hit"; return; }
  fi
  printf '%s\n' "$SUPERSEDE_MAP" \
    | awk -F'\t' -v s="$short" '
        $1 ~ /^sha:/ {
          tok = substr($1, 5)
          if (index(tok, s) == 1 || index(s, tok) == 1) { print $2; exit }
        }'
}

# Annotate NDJSON commit records with {superseded, superseded_by} and,
# unless --history, drop the superseded ones. Single filtering point for
# both plain and json output.
annotate_commits() {
  while IFS= read -r rec; do
    [ -z "$rec" ] && continue
    local sha subject by
    sha=$(printf '%s' "$rec" | jq -r '.sha')
    subject=$(printf '%s' "$rec" | jq -r '.subject')
    by=$(lookup_superseded "$sha" "$subject")
    if [ -n "$by" ]; then
      [ "$INCLUDE_HISTORY" = 0 ] && continue
      printf '%s' "$rec" | jq -c --arg by "$by" \
        '. + {superseded: true, superseded_by: $by}'
    else
      printf '%s' "$rec" | jq -c '. + {superseded: false, superseded_by: null}'
    fi
  done
}

commit_records=''
COMMIT_DROPPED=0
if [ "$INCLUDE_COMMIT" = 1 ]; then
  SUPERSEDE_MAP=$(build_supersession_index)
  commit_records=$(extract_commits_ndjson)
  [ -n "$commit_records" ] && \
    commit_records=$(printf '%s\n' "$commit_records" | annotate_commits)

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
        printf '%s\n' "$commit_records" | while IFS= read -r rec; do
          [ -z "$rec" ] && continue
          sha=$(printf '%s' "$rec" | jq -r '.sha')
          date=$(printf '%s' "$rec" | jq -r '.date')
          subject=$(printf '%s' "$rec" | jq -r '.subject')
          superseded_by=$(printf '%s' "$rec" | jq -r '.superseded_by // ""')
          if [ -n "$superseded_by" ]; then
            echo "### $sha  $date  $subject  [SUPERSEDED by $superseded_by]"
          else
            echo "### $sha  $date  $subject"
          fi
          for key_pair in 'decision Decision' 'learning Learning' 'gotcha Gotcha' 'related Related'; do
            k=${key_pair% *}
            label=${key_pair#* }
            entries=$(printf '%s' "$rec" | jq -r ".${k}[]" 2>/dev/null || true)
            render_group "$label" "$entries"
          done
          echo
        done
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
          printf '%s\n' "$commit_records" | jq -s '.'
        fi
      )" \
      --argjson prs "$(
        if [ -z "$pr_records" ]; then
          echo '[]'
        else
          printf '%s\n' "$pr_records" | jq -s '.'
        fi
      )" \
      '{repo: $repo, since: $since,
        match: (if $match == "" then null else $match end),
        path:  (if $path  == "" then null else $path  end),
        commits_suppressed: $suppressed,
        commits: $commits, prs: $prs}'
    ;;
esac
