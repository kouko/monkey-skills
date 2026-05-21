#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# sheets-confirm-write.sh — op-aware two-tier confirmation wrapper for
#                          Google Sheets values writes
# -----------------------------------------------------------------------------
# Wraps `gws sheets values <op>` behind an op-aware tiered confirmation gate.
# Modeled on safe-delete.sh (3-tier confirm pattern); op-aware tier dispatch:
#
#   --op append           → L1. Appends rows below existing data. Non-
#                                destructive — does not overwrite. Requires
#                                --confirm to execute.
#   --op clear            → L2. Removes values in the given range. The
#   --op update                  range is recoverable ONLY via the
#                                spreadsheet's version history within the
#                                last 30 days (Drive retention default).
#                                Requires --confirm AND
#                                --confirm-recovery="version_history_only".
#                                The second flag is a typed acknowledgment
#                                that the operator understands the
#                                recovery boundary — see safe-delete.sh
#                                §L3 rationale for confirmation-fatigue
#                                defense.
#
# Default mode is dry-run: every invocation without --confirm prints a
# JSON preview and exits 0 without calling the gws API. The caller must
# re-run with the required flags to execute.
#
# Usage:
#   sheets-confirm-write.sh --op append --spreadsheet <ID> --range <A1> \
#                           --values '<JSON-2D-array>'
#   sheets-confirm-write.sh --op append ... --confirm
#   sheets-confirm-write.sh --op clear --spreadsheet <ID> --range <A1>
#   sheets-confirm-write.sh --op clear ... --confirm \
#                           --confirm-recovery="version_history_only"
#   sheets-confirm-write.sh --op update --spreadsheet <ID> --range <A1> \
#                           --values '<JSON-2D-array>' --confirm \
#                           --confirm-recovery="version_history_only"
#
# Stdout: JSON
#   dry-run:
#     {action:"append"|"clear"|"update", dry_run:true,
#      metadata:{spreadsheet, sheet, range, values_preview, affected_cells},
#      warnings:[...] (L2 only — empty list for L1),
#      next:"<re-run cmd>"}
#   executed:
#     {action:"appended"|"cleared"|"updated", dry_run:false,
#      spreadsheet, range, affected_cells}
# Stderr: human-readable progress + warnings.
#
# Exit codes (mirror safe-delete.sh):
#   0   success (dry-run preview, or executed action)
#   1   usage / pre-flight error
#   2   resource not found / 404 (reserved; gws-wrap maps 404 to 12 currently)
#   3   confirmation gate failed (missing --confirm-recovery on L2)
#   10  auth / scope error (passed through from gws-wrap)
#   11  rate limit (passed through from gws-wrap)
#   12  generic API error (passed through from gws-wrap)
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly GWS_WRAP="${SCRIPT_DIR}/gws-wrap.sh"

readonly L2_WARNING="L2: clear/overwrite is recoverable only via version history within 30 days"
readonly REQUIRED_RECOVERY_TOKEN="version_history_only"

die() { printf 'sheets-confirm-write: %s\n' "$*" >&2; exit "${2:-1}"; }
usage() {
  sed -n '8,60p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 1
}

# --- arg parse -------------------------------------------------------------
OP=""
SPREADSHEET=""
SHEET=""
RANGE=""
VALUES_JSON=""
CONFIRM=0
CONFIRM_RECOVERY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --op) OP="${2:-}"; shift 2 ;;
    --op=*) OP="${1#*=}"; shift ;;
    --spreadsheet) SPREADSHEET="${2:-}"; shift 2 ;;
    --spreadsheet=*) SPREADSHEET="${1#*=}"; shift ;;
    --sheet) SHEET="${2:-}"; shift 2 ;;
    --sheet=*) SHEET="${1#*=}"; shift ;;
    --range) RANGE="${2:-}"; shift 2 ;;
    --range=*) RANGE="${1#*=}"; shift ;;
    --values) VALUES_JSON="${2:-}"; shift 2 ;;
    --values=*) VALUES_JSON="${1#*=}"; shift ;;
    --confirm) CONFIRM=1; shift ;;
    --confirm-recovery) CONFIRM_RECOVERY="${2:-}"; shift 2 ;;
    --confirm-recovery=*) CONFIRM_RECOVERY="${1#*=}"; shift ;;
    -h|--help) usage ;;
    -*) die "unknown flag: $1" ;;
    *) die "unexpected positional: $1" ;;
  esac
done

# --- validate --------------------------------------------------------------
case "${OP}" in
  append|clear|update) ;;
  "") die "missing --op (one of: append, clear, update)" ;;
  *) die "invalid --op: ${OP} (must be one of: append, clear, update)" ;;
esac

[[ -n "${SPREADSHEET}" ]] || die "missing --spreadsheet <ID>"
[[ -n "${RANGE}" ]] || die "missing --range <A1-notation>"
command -v jq >/dev/null 2>&1 || die "jq not found"

# `clear` doesn't need --values; `append` and `update` do
if [[ "${OP}" == "append" || "${OP}" == "update" ]]; then
  [[ -n "${VALUES_JSON}" ]] || die "--values <JSON-2D-array> required for --op ${OP}"
  # Validate JSON parses as an array (2D array shape not strictly enforced;
  # caller responsible for matching gws API contract).
  if ! printf '%s' "${VALUES_JSON}" | jq -e 'type == "array"' >/dev/null 2>&1; then
    die "--values must be a JSON array, got: ${VALUES_JSON}"
  fi
fi

# --- compute tier + affected_cells ----------------------------------------
# Tier rules:
#   append → L1 (recoverable: just delete the appended rows; non-destructive)
#   clear  → L2 (destructive: needs version-history recovery acknowledgment)
#   update → L2 (overwrites existing values; same recovery boundary as clear)
if [[ "${OP}" == "append" ]]; then
  TIER="L1"
else
  TIER="L2"
fi

# affected_cells:
#   For append/update: count cells in the values array (rows × cols of row[0]).
#   For clear: parse range A1:B2 → 2 rows × 2 cols = 4 cells.
compute_affected_cells_from_values() {
  # Input: VALUES_JSON (a 2D JSON array). Output: int on stdout.
  printf '%s' "${VALUES_JSON}" | jq '
    if (type == "array") then
      if (length == 0) then 0
      elif (.[0] | type == "array") then (length * (.[0] | length))
      else length  # 1D array → row of N cells
      end
    else 0 end
  '
}

compute_affected_cells_from_range() {
  # Parse A1-notation range like "A1:B2", "Sheet1!A1:C3", "A1".
  # Strip optional "Sheet!" prefix; on single-cell ranges return 1.
  local r="${RANGE#*!}"  # strip sheet prefix if present
  if [[ "${r}" != *:* ]]; then
    printf '1'
    return
  fi
  local start="${r%:*}"
  local end="${r#*:}"
  # Extract column letters and row numbers using bash regex.
  # Pattern: ^([A-Z]+)([0-9]+)$ on each endpoint.
  local re='^([A-Za-z]+)([0-9]+)$'
  if [[ "${start}" =~ ${re} ]]; then
    local sc="${BASH_REMATCH[1]}" sr="${BASH_REMATCH[2]}"
  else
    printf '0'
    return
  fi
  if [[ "${end}" =~ ${re} ]]; then
    local ec="${BASH_REMATCH[1]}" er="${BASH_REMATCH[2]}"
  else
    printf '0'
    return
  fi
  # Convert column letters → numbers (A=1, B=2, ..., Z=26, AA=27, ...).
  col_to_num() {
    local letters="${1^^}"  # uppercase
    local n=0 i ch code
    for (( i=0; i<${#letters}; i++ )); do
      ch="${letters:$i:1}"
      code=$(( $(printf '%d' "'${ch}") - 64 ))
      n=$(( n * 26 + code ))
    done
    printf '%d' "${n}"
  }
  local sc_n ec_n
  sc_n="$(col_to_num "${sc}")"
  ec_n="$(col_to_num "${ec}")"
  local cols=$(( ec_n - sc_n + 1 ))
  local rows=$(( er - sr + 1 ))
  (( cols < 0 )) && cols=0
  (( rows < 0 )) && rows=0
  printf '%d' $(( rows * cols ))
}

if [[ "${OP}" == "clear" ]]; then
  AFFECTED_CELLS="$(compute_affected_cells_from_range)"
else
  AFFECTED_CELLS="$(compute_affected_cells_from_values)"
fi

# values_preview: first row (or scalar 0 sentinel) — keep small; never leak full payload
if [[ -n "${VALUES_JSON}" ]]; then
  VALUES_PREVIEW_JSON="$(printf '%s' "${VALUES_JSON}" | jq -c 'if length == 0 then [] else (.[0:1]) end')"
else
  VALUES_PREVIEW_JSON="null"
fi

# --- compose warnings ------------------------------------------------------
if [[ "${TIER}" == "L2" ]]; then
  WARNINGS_JSON="$(jq -nc --arg w "${L2_WARNING}" '[$w]')"
else
  WARNINGS_JSON="[]"
fi

# --- metadata --------------------------------------------------------------
METADATA_JSON="$(
  jq -nc \
    --arg spreadsheet "${SPREADSHEET}" \
    --arg sheet "${SHEET}" \
    --arg range "${RANGE}" \
    --argjson values_preview "${VALUES_PREVIEW_JSON}" \
    --argjson affected_cells "${AFFECTED_CELLS}" \
    '{spreadsheet:$spreadsheet, sheet:$sheet, range:$range, values_preview:$values_preview, affected_cells:$affected_cells}'
)"

# --- dry-run path ----------------------------------------------------------
build_next_cmd() {
  local base="bash sheets-confirm-write.sh --op ${OP} --spreadsheet ${SPREADSHEET} --range \"${RANGE}\""
  if [[ "${OP}" == "append" || "${OP}" == "update" ]]; then
    base="${base} --values '${VALUES_JSON}'"
  fi
  if [[ "${TIER}" == "L2" ]]; then
    printf '%s --confirm --confirm-recovery="%s"' "${base}" "${REQUIRED_RECOVERY_TOKEN}"
  else
    printf '%s --confirm' "${base}"
  fi
}

if [[ "${CONFIRM}" == "0" ]]; then
  next_cmd="$(build_next_cmd)"
  jq -nc \
    --arg action "${OP}" \
    --arg tier "${TIER}" \
    --argjson metadata "${METADATA_JSON}" \
    --argjson warnings "${WARNINGS_JSON}" \
    --arg next "${next_cmd}" \
    '{
      action: $action,
      dry_run: true,
      tier: $tier,
      metadata: $metadata,
      warnings: $warnings,
      next: $next
    }'
  exit 0
fi

# --- L2 confirmation gate --------------------------------------------------
if [[ "${TIER}" == "L2" ]]; then
  if [[ "${CONFIRM_RECOVERY}" != "${REQUIRED_RECOVERY_TOKEN}" ]]; then
    die "L2 confirmation required: pass --confirm-recovery=\"${REQUIRED_RECOVERY_TOKEN}\" (operation is recoverable only via version history within 30 days)" 3
  fi
fi

# --- execute ---------------------------------------------------------------
[[ -x "${GWS_WRAP}" ]] || die "gws-wrap.sh not executable at ${GWS_WRAP}" 1

# Build the JSON body for gws sheets values <op>.
# gws contract:
#   values append: --params '{spreadsheetId, range, valueInputOption}' --json '{values: [[...]]}'
#   values update: same shape
#   values clear:  --params '{spreadsheetId, range}' --json '{}'
PARAMS_JSON="$(jq -nc \
  --arg id "${SPREADSHEET}" \
  --arg range "${RANGE}" \
  '{spreadsheetId:$id, range:$range, valueInputOption:"USER_ENTERED"}')"

case "${OP}" in
  append)
    BODY_JSON="$(jq -nc --argjson v "${VALUES_JSON}" '{values:$v}')"
    printf '[sheets-confirm-write] appending %s cells to %s!%s\n' \
      "${AFFECTED_CELLS}" "${SPREADSHEET}" "${RANGE}" >&2
    "${GWS_WRAP}" sheets values append \
      --params "${PARAMS_JSON}" \
      --json "${BODY_JSON}" >/dev/null
    jq -nc \
      --arg id "${SPREADSHEET}" --arg range "${RANGE}" --argjson cells "${AFFECTED_CELLS}" \
      '{action:"appended", dry_run:false, spreadsheet:$id, range:$range, affected_cells:$cells}'
    ;;
  update)
    BODY_JSON="$(jq -nc --argjson v "${VALUES_JSON}" '{values:$v}')"
    printf '[sheets-confirm-write] updating %s cells in %s!%s (L2 — recoverable via version history within 30 days)\n' \
      "${AFFECTED_CELLS}" "${SPREADSHEET}" "${RANGE}" >&2
    "${GWS_WRAP}" sheets values update \
      --params "${PARAMS_JSON}" \
      --json "${BODY_JSON}" >/dev/null
    jq -nc \
      --arg id "${SPREADSHEET}" --arg range "${RANGE}" --argjson cells "${AFFECTED_CELLS}" \
      '{action:"updated", dry_run:false, spreadsheet:$id, range:$range, affected_cells:$cells}'
    ;;
  clear)
    # clear takes no values body, just spreadsheetId + range
    CLEAR_PARAMS_JSON="$(jq -nc --arg id "${SPREADSHEET}" --arg range "${RANGE}" \
      '{spreadsheetId:$id, range:$range}')"
    printf '[sheets-confirm-write] clearing %s cells in %s!%s (L2 — recoverable via version history within 30 days)\n' \
      "${AFFECTED_CELLS}" "${SPREADSHEET}" "${RANGE}" >&2
    "${GWS_WRAP}" sheets values clear \
      --params "${CLEAR_PARAMS_JSON}" \
      --json '{}' >/dev/null
    jq -nc \
      --arg id "${SPREADSHEET}" --arg range "${RANGE}" --argjson cells "${AFFECTED_CELLS}" \
      '{action:"cleared", dry_run:false, spreadsheet:$id, range:$range, affected_cells:$cells}'
    ;;
esac
