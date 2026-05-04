#!/usr/bin/env bash
set -uo pipefail

# =============================================================================
# smoke-test-api-coverage.sh — exercise representative methods across all 4
# Workspace APIs (Drive / Docs / Slides / Sheets) and report pass/fail.
# -----------------------------------------------------------------------------
# Purpose: confirm gws-toolkit's OAuth scope set + GCP API enables + gws CLI
# dispatch all work end-to-end against real Google APIs, beyond the minimum
# methods exercised during initial smoke testing.
#
# Coverage (12-15 methods total):
#   Drive:  about.get, files.list, files.get, files.create (folder),
#           permissions.create
#   Docs:   documents.create, documents.get, documents.batchUpdate
#   Sheets: spreadsheets.create, spreadsheets.get,
#           spreadsheets.values.update, spreadsheets.values.get,
#           spreadsheets.batchUpdate
#   Slides: presentations.create, presentations.get,
#           presentations.batchUpdate
#
# Each method is invoked, response captured, pass/fail decided by exit code
# + minimum-payload sanity check (e.g. id field present).
#
# Cleanup: every Drive resource created (Doc / Sheet / Slide / folder) is
# trashed via safe-delete.sh --confirm at the end. Failed tests still trigger
# cleanup of whatever was created up to that point.
#
# Usage:
#   bash gws-toolkit/scripts/dev/smoke-test-api-coverage.sh
#   bash gws-toolkit/scripts/dev/smoke-test-api-coverage.sh --keep
#       (skip cleanup; leave resources in Drive — useful for manual inspection)
#
# Exit codes:
#   0   all methods passed
#   1   one or more methods failed (table shows which)
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TOOLKIT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly GWS="${HOME}/.cache/slides-toolkit/bin/gws"
readonly JQ="${HOME}/.cache/slides-toolkit/bin/jq"
readonly SAFE_DELETE="${TOOLKIT_ROOT}/gws/safe-delete.sh"

KEEP=0
[[ "${1:-}" == "--keep" ]] && KEEP=1

# resource ids created during the run (to be cleaned up)
declare -a CLEANUP_IDS=()

# results: each entry "API|method|status|note"
declare -a RESULTS=()

record() {
  local api="$1" method="$2" status="$3" note="${4:-}"
  RESULTS+=("${api}|${method}|${status}|${note}")
  printf '[smoke] %s %s %s %s\n' "${api}" "${method}" "${status}" "${note}" >&2
}

# wrap a gws call: capture stdout to file, mark pass/fail by jq predicate
# args: api method jq_predicate gws_args...
try() {
  local api="$1" method="$2" pred="$3"; shift 3
  local out_file
  out_file="$(mktemp -t smoke.XXXXXX)"
  if ! "${GWS}" "$@" >"${out_file}" 2>/dev/null; then
    record "${api}" "${method}" "FAIL" "gws non-zero exit"
    rm -f "${out_file}"
    return 1
  fi
  if ! sed -n '/^{/,$p' "${out_file}" | "${JQ}" -e "${pred}" >/dev/null 2>&1; then
    record "${api}" "${method}" "FAIL" "predicate mismatch: ${pred}"
    rm -f "${out_file}"
    return 1
  fi
  record "${api}" "${method}" "PASS"
  cat "${out_file}"
  rm -f "${out_file}"
  return 0
}

# ============== DRIVE ============================================
echo
echo "============== Drive ==============" >&2

try "Drive" "about.get" '.user.emailAddress | length > 0' \
  drive about get --params '{"fields":"user(emailAddress,displayName),storageQuota"}' \
  | "${JQ}" -c '{user: .user.emailAddress}' >&2 || true

try "Drive" "files.list (with q)" '.files | type == "array"' \
  drive files list --params '{"q":"trashed = false","pageSize":2,"fields":"files(id,name,mimeType)"}' \
  | "${JQ}" -c '{count: .files | length}' >&2 || true

# Create a folder for organising smoke test artefacts
folder_resp="$(mktemp)"
if "${GWS}" drive files create \
    --json "$(${JQ} -nc --arg n "smoke-test folder $(date -u +%Y%m%dT%H%M%SZ)" '{name:$n, mimeType:"application/vnd.google-apps.folder", appProperties:{created_by:"gws-toolkit"}}')" \
    >"${folder_resp}" 2>/dev/null; then
  FOLDER_ID="$(sed -n '/^{/,$p' "${folder_resp}" | "${JQ}" -r '.id // empty')"
  if [[ -n "${FOLDER_ID}" ]]; then
    record "Drive" "files.create (folder)" "PASS"
    CLEANUP_IDS+=("${FOLDER_ID}")
  else
    record "Drive" "files.create (folder)" "FAIL" "no id in response"
  fi
else
  record "Drive" "files.create (folder)" "FAIL" "gws non-zero exit"
fi
rm -f "${folder_resp}"

# files.get on the folder we just created
if [[ -n "${FOLDER_ID:-}" ]]; then
  try "Drive" "files.get" '.id | length > 0' \
    drive files get --params "$(${JQ} -nc --arg id "${FOLDER_ID}" '{fileId:$id, fields:"id,name,mimeType,appProperties"}')" \
    >/dev/null || true
fi

# permissions.create — share folder to anyoneWithLink (reader)
if [[ -n "${FOLDER_ID:-}" ]]; then
  try "Drive" "permissions.create" '.id | length > 0' \
    drive permissions create \
    --params "$(${JQ} -nc --arg id "${FOLDER_ID}" '{fileId:$id}')" \
    --json '{"role":"reader","type":"anyone"}' \
    >/dev/null || true
fi

# ============== DOCS =============================================
echo
echo "============== Docs ==============" >&2

doc_resp="$(mktemp)"
if "${GWS}" docs documents create \
    --json '{"title":"smoke test doc"}' \
    >"${doc_resp}" 2>/dev/null; then
  DOC_ID="$(sed -n '/^{/,$p' "${doc_resp}" | "${JQ}" -r '.documentId // empty')"
  if [[ -n "${DOC_ID}" ]]; then
    record "Docs" "documents.create" "PASS"
    CLEANUP_IDS+=("${DOC_ID}")
  fi
fi
rm -f "${doc_resp}"

if [[ -n "${DOC_ID:-}" ]]; then
  try "Docs" "documents.get" '.documentId | length > 0' \
    docs documents get --params "$(${JQ} -nc --arg id "${DOC_ID}" '{documentId:$id}')" \
    >/dev/null || true

  try "Docs" "documents.batchUpdate" '.replies | length > 0' \
    docs documents batchUpdate \
    --params "$(${JQ} -nc --arg id "${DOC_ID}" '{documentId:$id}')" \
    --json '{"requests":[{"insertText":{"location":{"index":1},"text":"smoke test body."}}]}' \
    >/dev/null || true
fi

# ============== SHEETS ===========================================
echo
echo "============== Sheets ==============" >&2

sheet_resp="$(mktemp)"
SHEET_TITLE=""
if "${GWS}" sheets spreadsheets create \
    --json '{"properties":{"title":"smoke test sheet"}}' \
    >"${sheet_resp}" 2>/dev/null; then
  SHEET_ID="$(sed -n '/^{/,$p' "${sheet_resp}" | "${JQ}" -r '.spreadsheetId // empty')"
  # Default first-sheet title is locale-specific (Sheet1 / 工作表1 / シート1 etc.)
  # Read it from the create response so subsequent range refs resolve.
  SHEET_TITLE="$(sed -n '/^{/,$p' "${sheet_resp}" | "${JQ}" -r '.sheets[0].properties.title // "Sheet1"')"
  if [[ -n "${SHEET_ID}" ]]; then
    record "Sheets" "spreadsheets.create" "PASS"
    CLEANUP_IDS+=("${SHEET_ID}")
  fi
fi
rm -f "${sheet_resp}"

if [[ -n "${SHEET_ID:-}" ]]; then
  try "Sheets" "spreadsheets.get" '.spreadsheetId | length > 0' \
    sheets spreadsheets get --params "$(${JQ} -nc --arg id "${SHEET_ID}" '{spreadsheetId:$id}')" \
    >/dev/null || true

  # values.update — write A1 (range uses the actual default sheet title)
  RANGE="${SHEET_TITLE}!A1"
  try "Sheets" "spreadsheets.values.update" '.updatedCells > 0' \
    sheets spreadsheets values update \
    --params "$(${JQ} -nc --arg id "${SHEET_ID}" --arg r "${RANGE}" '{spreadsheetId:$id, range:$r, valueInputOption:"USER_ENTERED"}')" \
    --json '{"values":[["hello smoke"]]}' \
    >/dev/null || true

  # values.get — read A1 back
  try "Sheets" "spreadsheets.values.get" '.values[0][0] == "hello smoke"' \
    sheets spreadsheets values get \
    --params "$(${JQ} -nc --arg id "${SHEET_ID}" --arg r "${RANGE}" '{spreadsheetId:$id, range:$r}')" \
    >/dev/null || true

  # batchUpdate — add a sheet
  try "Sheets" "spreadsheets.batchUpdate" '.replies | length > 0' \
    sheets spreadsheets batchUpdate \
    --params "$(${JQ} -nc --arg id "${SHEET_ID}" '{spreadsheetId:$id}')" \
    --json '{"requests":[{"addSheet":{"properties":{"title":"smoke-sheet-2"}}}]}' \
    >/dev/null || true
fi

# ============== SLIDES ===========================================
echo
echo "============== Slides ==============" >&2

slide_resp="$(mktemp)"
if "${GWS}" slides presentations create \
    --json '{"title":"smoke test deck"}' \
    >"${slide_resp}" 2>/dev/null; then
  PRES_ID="$(sed -n '/^{/,$p' "${slide_resp}" | "${JQ}" -r '.presentationId // empty')"
  if [[ -n "${PRES_ID}" ]]; then
    record "Slides" "presentations.create" "PASS"
    CLEANUP_IDS+=("${PRES_ID}")
  fi
fi
rm -f "${slide_resp}"

if [[ -n "${PRES_ID:-}" ]]; then
  try "Slides" "presentations.get" '.presentationId | length > 0' \
    slides presentations get --params "$(${JQ} -nc --arg id "${PRES_ID}" '{presentationId:$id, fields:"presentationId,slides(objectId)"}')" \
    >/dev/null || true

  try "Slides" "presentations.batchUpdate" '.replies | length > 0' \
    slides presentations batchUpdate \
    --params "$(${JQ} -nc --arg id "${PRES_ID}" '{presentationId:$id}')" \
    --json '{"requests":[{"createSlide":{"slideLayoutReference":{"predefinedLayout":"TITLE_AND_BODY"}}}]}' \
    >/dev/null || true
fi

# ============== Cleanup ==========================================
echo
echo "============== Cleanup ==============" >&2
if (( KEEP == 1 )); then
  echo "[smoke] --keep: skipping cleanup (resources remain in Drive)" >&2
else
  for id in "${CLEANUP_IDS[@]}"; do
    if bash "${SAFE_DELETE}" "${id}" --confirm >/dev/null 2>&1; then
      printf '[smoke] cleanup: trashed %s\n' "${id}" >&2
    else
      printf '[smoke] cleanup: FAILED to trash %s\n' "${id}" >&2
    fi
  done
fi

# ============== Results table ====================================
echo
echo "============== Results =============="
fail_count=0
printf '%-7s | %-32s | %-4s | %s\n' "API" "Method" "Stat" "Note"
printf '%-7s-+-%-32s-+-%-4s-+-%s\n' "-------" "--------------------------------" "----" "----"
for r in "${RESULTS[@]}"; do
  api="${r%%|*}"; rest="${r#*|}"
  method="${rest%%|*}"; rest="${rest#*|}"
  status="${rest%%|*}"; note="${rest#*|}"
  printf '%-7s | %-32s | %-4s | %s\n' "${api}" "${method}" "${status}" "${note}"
  [[ "${status}" == "FAIL" ]] && fail_count=$((fail_count + 1))
done
echo
if (( fail_count == 0 )); then
  echo "All ${#RESULTS[@]} methods passed."
  exit 0
else
  echo "${fail_count}/${#RESULTS[@]} methods failed."
  exit 1
fi
