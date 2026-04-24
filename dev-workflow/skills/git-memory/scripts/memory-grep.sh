#!/usr/bin/env bash
#
# memory-grep.sh — retrieval primitive for git-memory skill.
#
# Dumps all memory trailers from git log plus all `## Memory` sections
# from merged PR bodies, producing a plain-text digest that any tool
# (Claude Code, Cursor, Codex, aider, a human) can ingest.
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
# Exit codes:
#   0  success
#   1  usage error
#   2  not a git repo
#   3  external dependency missing (gh / jq when required)

set -euo pipefail

# Render a trailer group as one or more indented lines.
#   $1 — label (e.g. "Decision")
#   $2 — raw value from git log with %x1F separators between entries
# Single entry:   "  Decision: <text>"
# Multiple:       "  Decision (1/N): <text>" one per line
render_group() {
  [ -z "${2:-}" ] && return 0
  local entries
  entries=$(printf '%s' "$2" | tr $'\x1F' '\n' | sed '/^$/d')
  [ -z "$entries" ] && return 0
  local n
  n=$(printf '%s\n' "$entries" | wc -l | tr -d ' ')
  if [ "$n" -eq 1 ]; then
    printf '  %s: %s\n' "$1" "$entries"
  else
    printf '%s\n' "$entries" \
      | awk -v L="$1" -v N="$n" '{printf "  %s (%d/%d): %s\n", L, NR, N, $0}'
  fi
}

SINCE='3 months ago'
LIMIT=50
REPO='.'
FORMAT='plain'
INCLUDE_PR=1
INCLUDE_COMMIT=1

usage() {
  cat <<'EOF'
memory-grep.sh — retrieve git-memory entries from a repo

Usage:
  memory-grep.sh [--since=<period>] [--limit=<n>] [--repo=<path>]
                 [--format=plain|json] [--no-pr] [--no-commit]

Options:
  --since=<period>   git log --since value (default: "3 months ago")
  --limit=<n>        max PRs to inspect (default: 50)
  --repo=<path>      working tree path (default: current dir)
  --format=<f>       output format: plain | json (default: plain)
  --no-pr            skip PR body extraction
  --no-commit        skip commit trailer extraction

Examples:
  memory-grep.sh --since='6 months ago' --limit=100
  memory-grep.sh --no-pr              # commit trailers only
  memory-grep.sh --format=json | jq '.commits[]'
EOF
}

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

if [ "$FORMAT" = 'json' ] && ! command -v jq >/dev/null 2>&1; then
  echo "--format=json requires jq" >&2
  exit 3
fi

# ─── commit trailer extraction ─────────────────────────────────────

commit_records=''
if [ "$INCLUDE_COMMIT" = 1 ]; then
  # For each commit in the range, emit a pipe-delimited record:
  #   <short-sha>|<subject>|<iso-date>|<Decision trailer>|<Learning trailer>|<Gotcha trailer>|<Related trailer>
  # Missing trailers come back as empty strings.
  commit_records=$(
    git -C "$REPO" log \
      --since="$SINCE" \
      --no-merges \
      --pretty=format:'%h|%s|%ad|%(trailers:key=Decision,valueonly,separator=%x1F)|%(trailers:key=Learning,valueonly,separator=%x1F)|%(trailers:key=Gotcha,valueonly,separator=%x1F)|%(trailers:key=Related,valueonly,separator=%x1F)' \
      --date=short \
      2>/dev/null \
      | awk -F'|' 'NF>=7 && ($4!="" || $5!="" || $6!="")' || true
  )
fi

# ─── PR body Memory-section extraction ─────────────────────────────

pr_records=''
if [ "$INCLUDE_PR" = 1 ]; then
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    # Fetch recent merged PRs, filter down to those containing `## Memory`.
    # Output one JSON object per line (jq -c): {number, title, mergedAt, memory}
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
    if [ -n "$commit_records" ]; then
      echo "## Commit trailers"
      echo
      # Render each record as a human-readable block.
      echo "$commit_records" | while IFS='|' read -r sha subject date decision learning gotcha related; do
        [ -z "$sha" ] && continue
        echo "### $sha  $date  $subject"
        render_group "Decision" "$decision"
        render_group "Learning" "$learning"
        render_group "Gotcha"   "$gotcha"
        render_group "Related"  "$related"
        echo
      done
    else
      echo "## Commit trailers"
      echo "(none in range)"
      echo
    fi

    if [ -n "$pr_records" ]; then
      echo "## PR Memory sections"
      echo
      echo "$pr_records" | jq -r '
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
    # Build a single JSON object: {commits: [...], prs: [...]}
    jq -n \
      --arg since "$SINCE" \
      --arg repo "$REPO" \
      --argjson commits "$(
        if [ -z "$commit_records" ]; then
          echo '[]'
        else
          echo "$commit_records" | jq -R -s 'split("\n") | map(select(length > 0)) | map(
            split("|") as $f |
            {
              sha:      $f[0],
              subject:  $f[1],
              date:     $f[2],
              decision: ($f[3] | split("") | map(select(length > 0))),
              learning: ($f[4] | split("") | map(select(length > 0))),
              gotcha:   ($f[5] | split("") | map(select(length > 0))),
              related:  ($f[6] | split("") | map(select(length > 0)))
            }
          )'
        fi
      )" \
      --argjson prs "$(
        if [ -z "$pr_records" ]; then
          echo '[]'
        else
          echo "$pr_records" | jq -s '.'
        fi
      )" \
      '{repo: $repo, since: $since, commits: $commits, prs: $prs}'
    ;;
esac
