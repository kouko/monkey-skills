#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# docs-confirm-append.sh — L1 safety wrapper for Google Docs writes
# -----------------------------------------------------------------------------
# Wraps `gws docs documents batchUpdate` (insertText + replaceAllText) behind
# a single-tier (L1) dry-run gate. Designed for Claude orchestration: Claude
# calls with no --confirm to get a preview JSON, shows it to the user, and
# only re-runs with --confirm after explicit user assent.
#
# Why L1-only (no L2):
# Google Docs maintains automatic version history (File > Version history
# in the Docs UI). Any text inserted or replaced by this wrapper can be
# rolled back from that UI without operator intervention — equivalent
# reversibility to Drive Trash for files. PRODUCT-SPEC §6.3 therefore
# specifies L1 dry-run only for Docs writes, with one extra safeguard for
# broad-stroke `replaceAllText` (where a careless `--find` string can
# mutate dozens of unrelated passages).
#
# Broad-stroke warning:
# When --action replace and the document contains > 5 matches for --find,
# the dry-run surfaces a warning in the output JSON. Claude must show this
# warning to the user before requesting --confirm. The match count is
# derived from a preview `gws docs documents get` call and counting
# occurrences of --find in the body, OR (for testing) supplied via
# --mock-match-count <N> which bypasses the preview call.
#
# Usage:
#   docs-confirm-append.sh --document <ID> --action append --text "..."
#       # L1 append, dry-run
#   docs-confirm-append.sh --document <ID> --action append --text "..." --confirm
#       # L1 append, execute
#   docs-confirm-append.sh --document <ID> --action replace \
#                          --find "..." --replace "..."
#       # L1 replace, dry-run
#   docs-confirm-append.sh --document <ID> --action replace \
#                          --find "..." --replace "..." --confirm
#       # L1 replace, execute
#   docs-confirm-append.sh --document <ID> --action replace \
#                          --find "..." --replace "..." \
#                          --mock-match-count 6
#       # dry-run with synthetic match count (for testing / preview override)
#
# Stdout: JSON
#   dry-run:   {action:"append"|"replace", dry_run:true,
#              metadata:{document, range, text_preview,
#                        replace_count (replace only)},
#              warnings:[...], next:"<re-run cmd>"}
#   executed:  {action:"appended"|"replaced", dry_run:false,
#              document, replies (replace only with count)}
# Stderr: human-readable progress + warnings.
#
# Exit codes (mirror safe-delete.sh):
#   0   success (dry-run preview, or executed action)
#   1   usage / pre-flight error
#   2   document not found / 404
#   3   confirmation gate failed (reserved; L1 has no typed-name gate)
#   10  auth / scope error (passed through from gws-wrap)
#   11  rate limit
#   12  generic API error
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly GWS_WRAP="${SCRIPT_DIR}/gws-wrap.sh"
readonly BROAD_STROKE_THRESHOLD=5
readonly TEXT_PREVIEW_MAX=80

die() { printf 'docs-confirm-append: %s\n' "$*" >&2; exit "${2:-1}"; }
usage() {
  sed -n '5,68p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 1
}

# --- arg parse -------------------------------------------------------------
DOCUMENT_ID=""
ACTION=""
TEXT=""
FIND=""
REPLACE=""
CONFIRM=0
MOCK_MATCH_COUNT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --document) DOCUMENT_ID="${2:-}"; shift 2 ;;
    --document=*) DOCUMENT_ID="${1#*=}"; shift ;;
    --action) ACTION="${2:-}"; shift 2 ;;
    --action=*) ACTION="${1#*=}"; shift ;;
    --text) TEXT="${2:-}"; shift 2 ;;
    --text=*) TEXT="${1#*=}"; shift ;;
    --find) FIND="${2:-}"; shift 2 ;;
    --find=*) FIND="${1#*=}"; shift ;;
    --replace) REPLACE="${2:-}"; shift 2 ;;
    --replace=*) REPLACE="${1#*=}"; shift ;;
    --mock-match-count) MOCK_MATCH_COUNT="${2:-}"; shift 2 ;;
    --mock-match-count=*) MOCK_MATCH_COUNT="${1#*=}"; shift ;;
    --confirm) CONFIRM=1; shift ;;
    -h|--help) usage ;;
    -*) die "unknown flag: $1" ;;
    *) die "unexpected positional: $1" ;;
  esac
done

[[ -n "${DOCUMENT_ID}" ]] || die "missing --document <ID>"
[[ -n "${ACTION}" ]] || die "missing --action <append|replace>"
[[ -x "${GWS_WRAP}" ]] || die "gws-wrap.sh not executable at ${GWS_WRAP}"
command -v jq >/dev/null 2>&1 || die "jq not found"

case "${ACTION}" in
  append)
    [[ -n "${TEXT}" ]] || die "--action append requires --text <TEXT>"
    ;;
  replace)
    [[ -n "${FIND}" ]] || die "--action replace requires --find <STRING>"
    # --replace may legitimately be empty (delete-all), so do not require
    # non-empty REPLACE here. The caller's intent for empty replace is
    # explicit if they passed --replace.
    ;;
  *)
    die "invalid --action: ${ACTION} (must be append|replace)"
    ;;
esac

# --- helpers ---------------------------------------------------------------
preview_text() {
  # Truncate to TEXT_PREVIEW_MAX chars; preserve full text in stderr only.
  local s="$1"
  if (( ${#s} > TEXT_PREVIEW_MAX )); then
    printf '%s…' "${s:0:TEXT_PREVIEW_MAX}"
  else
    printf '%s' "${s}"
  fi
}

# Count occurrences of FIND in the document body via `docs documents get`.
# Returns integer on stdout. Returns 0 on fetch error (caller should handle).
fetch_match_count() {
  local doc_id="$1"
  local needle="$2"
  local body_json
  body_json="$(
    "${GWS_WRAP}" docs documents get \
      --params "$(jq -nc --arg id "${doc_id}" '{documentId: $id}')" 2>/dev/null
  )" || return 1
  [[ -n "${body_json}" ]] || return 1
  # Concatenate all textRun.content fields, then count needle occurrences.
  # jq path: .body.content[].paragraph.elements[].textRun.content
  printf '%s' "${body_json}" | jq -r --arg needle "${needle}" '
    [.. | objects | .textRun? | .content? | select(. != null)]
    | join("")
    | [splits($needle)]
    | length - 1
  '
}

# --- dry-run path ----------------------------------------------------------
if [[ "${CONFIRM}" == "0" ]]; then
  warnings_json="[]"

  if [[ "${ACTION}" == "append" ]]; then
    text_preview="$(preview_text "${TEXT}")"
    metadata_json="$(jq -nc \
      --arg doc "${DOCUMENT_ID}" \
      --arg preview "${text_preview}" \
      '{
        document: $doc,
        range: "endOfSegmentLocation",
        text_preview: $preview
      }')"
    next_cmd="bash docs-confirm-append.sh --document ${DOCUMENT_ID} --action append --text \"<your text>\" --confirm"

  else
    # action == replace
    text_preview="$(preview_text "${REPLACE}")"
    find_preview="$(preview_text "${FIND}")"

    if [[ -n "${MOCK_MATCH_COUNT}" ]]; then
      match_count="${MOCK_MATCH_COUNT}"
    else
      match_count="$(fetch_match_count "${DOCUMENT_ID}" "${FIND}")" || {
        die "failed to fetch document body for match-count preview (id=${DOCUMENT_ID}); use --mock-match-count to bypass" 2
      }
      # Empty / non-numeric guard
      [[ "${match_count}" =~ ^[0-9]+$ ]] || match_count=0
    fi

    if (( match_count > BROAD_STROKE_THRESHOLD )); then
      warnings_json="$(jq -nc \
        --argjson n "${match_count}" \
        --argjson t "${BROAD_STROKE_THRESHOLD}" \
        '["broad-stroke replace: match-count \($n) exceeds threshold \($t)"]')"
    fi

    metadata_json="$(jq -nc \
      --arg doc "${DOCUMENT_ID}" \
      --arg find "${find_preview}" \
      --arg preview "${text_preview}" \
      --argjson n "${match_count}" \
      '{
        document: $doc,
        range: ("replaceAllText: \"" + $find + "\""),
        text_preview: $preview,
        replace_count: $n
      }')"
    next_cmd="bash docs-confirm-append.sh --document ${DOCUMENT_ID} --action replace --find \"<find>\" --replace \"<replace>\" --confirm"
  fi

  jq -nc \
    --arg action "${ACTION}" \
    --argjson metadata "${metadata_json}" \
    --argjson warnings "${warnings_json}" \
    --arg next "${next_cmd}" \
    '{
      action: $action,
      dry_run: true,
      tier: "L1",
      metadata: $metadata,
      warnings: $warnings,
      next: $next
    }'
  exit 0
fi

# --- execute ---------------------------------------------------------------
if [[ "${ACTION}" == "append" ]]; then
  printf '[docs-confirm-append] append: document=%s text_len=%d\n' \
    "${DOCUMENT_ID}" "${#TEXT}" >&2
  requests_json="$(jq -nc --arg t "${TEXT}" '{
    requests: [
      {
        insertText: {
          text: $t,
          endOfSegmentLocation: {}
        }
      }
    ]
  }')"
  "${GWS_WRAP}" docs documents batchUpdate \
    --params "$(jq -nc --arg id "${DOCUMENT_ID}" '{documentId: $id}')" \
    --json "${requests_json}" >/dev/null
  jq -nc --arg id "${DOCUMENT_ID}" \
    '{action:"appended", dry_run:false, document:$id}'
else
  # action == replace
  printf '[docs-confirm-append] replace: document=%s find_len=%d replace_len=%d\n' \
    "${DOCUMENT_ID}" "${#FIND}" "${#REPLACE}" >&2
  requests_json="$(jq -nc --arg f "${FIND}" --arg r "${REPLACE}" '{
    requests: [
      {
        replaceAllText: {
          containsText: {
            text: $f,
            matchCase: true
          },
          replaceText: $r
        }
      }
    ]
  }')"
  "${GWS_WRAP}" docs documents batchUpdate \
    --params "$(jq -nc --arg id "${DOCUMENT_ID}" '{documentId: $id}')" \
    --json "${requests_json}" >/dev/null
  jq -nc --arg id "${DOCUMENT_ID}" \
    '{action:"replaced", dry_run:false, document:$id}'
fi
