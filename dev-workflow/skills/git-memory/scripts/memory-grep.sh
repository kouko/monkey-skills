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
#   2  not a git repo
#   3  external dependency missing (jq always required; gh required if PR path enabled)

set -euo pipefail

SINCE='3 months ago'
LIMIT=50
REPO='.'
FORMAT='plain'
INCLUDE_PR=1
INCLUDE_COMMIT=1

TRAILER_KEYS_REGEX='^(Decision|Learning|Gotcha|Related):'

usage() {
  cat <<'EOF'
memory-grep.sh — retrieve git-memory entries from a repo

Usage:
  memory-grep.sh [--since=<period>] [--limit=<n>] [--repo=<path>]
                 [--format=plain|json] [--no-pr] [--no-commit]

Options:
  --since=<period>   date filter for COMMITS (default: "3 months ago")
  --limit=<n>        cap on number of merged PRs fetched (default: 50)
  --repo=<path>      working tree path (default: current dir)
  --format=<f>       output format: plain | json (default: plain)
  --no-pr            skip PR body extraction
  --no-commit        skip commit trailer extraction

Note: --since filters commits by date; --limit caps PR count.
      PRs are not date-filtered (newest N are always taken).

Examples:
  memory-grep.sh --since='6 months ago' --limit=100
  memory-grep.sh --no-pr              # commit trailers only
  memory-grep.sh --format=json | jq '.commits[]'
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

for arg in "$@"; do
  case "$arg" in
    --since=*)   SINCE="${arg#*=}" ;;
    --limit=*)   LIMIT="${arg#*=}" ;;
    --repo=*)    REPO="${arg#*=}" ;;
    --format=*)  FORMAT="${arg#*=}" ;;
    --no-pr)     INCLUDE_PR=0 ;;
    --no-commit) INCLUDE_COMMIT=0 ;;
    -h|--help)   usage; exit 0 ;;
    *) echo "Unknown argument: $arg" >&2; usage; exit 1 ;;
  esac
done

case "$FORMAT" in
  plain|json) ;;
  *) echo "Invalid --format: $FORMAT (plain|json)" >&2; exit 1 ;;
esac

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

# ─── commit trailer extraction (Layer 2 — git's own parser) ────────
#
# Emits NDJSON (one object per line) for each memory-worthy commit:
#   {sha, date, subject, decision:[...], learning:[...], gotcha:[...], related:[...]}

extract_commits_ndjson() {
  git -C "$REPO" log \
    --since="$SINCE" \
    --no-merges \
    --format='%H' \
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

commit_records=''
if [ "$INCLUDE_COMMIT" = 1 ]; then
  commit_records=$(extract_commits_ndjson)
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

# ─── emit output ───────────────────────────────────────────────────

case "$FORMAT" in
  plain)
    echo "# git-memory digest — repo=$REPO since=\"$SINCE\""
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
          echo "### $sha  $date  $subject"
          for key_pair in 'decision Decision' 'learning Learning' 'gotcha Gotcha' 'related Related'; do
            k=${key_pair% *}
            label=${key_pair#* }
            entries=$(printf '%s' "$rec" | jq -r ".${k}[]" 2>/dev/null || true)
            render_group "$label" "$entries"
          done
          echo
        done
      else
        echo "(none in range)"
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
      '{repo: $repo, since: $since, commits: $commits, prs: $prs}'
    ;;
esac
