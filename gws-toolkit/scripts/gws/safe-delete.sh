#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# safe-delete.sh — three-tier delete protection for Google Drive files
# -----------------------------------------------------------------------------
# Wraps `gws drive files update {trashed:true}` (soft / recoverable) and
# `gws drive files delete` (permanent / irreversible) behind a tiered
# confirmation gate. Designed for Claude orchestration: Claude calls with
# no confirm flag to get a preview JSON, shows it to the user, and only
# re-runs with --confirm after explicit user assent.
#
# Why this exists:
# Granting full `drive` OAuth scope (gws-toolkit v0.4 default) replaces
# the implicit "app can only touch files it created" guarantee that the
# narrower drive.file scope previously provided. Application-layer delete
# safety must therefore enforce equivalent (or stronger) protection.
# The three tiers (PRODUCT-SPEC v1.0 §6.3.x):
#   L1 — Trash (default). Recoverable in 30 days from drive.google.com
#        Trash. Equivalent to drag-to-trash in the Drive web UI.
#   L2 — Permanent (--permanent). Irreversible. Requires --confirm + an
#        explicit metadata preview Claude must surface to the user.
#   L3 — Permanent + non-provenance. The target file lacks the
#        appProperties.created_by tag set by tag-create.sh. Requires
#        --i-confirm-name=<exact-name> to typed-match against the file's
#        actual name field. Defends against confirmation fatigue.
#
# Default mode is dry-run: every invocation without --confirm prints the
# metadata + planned action and exits 0 without calling the destructive
# API. Claude must explicitly re-run with --confirm to execute.
#
# Usage:
#   safe-delete.sh <file_id>                          # L1 trash, dry-run
#   safe-delete.sh <file_id> --confirm                # L1 trash, execute
#   safe-delete.sh <file_id> --permanent              # L2 permanent, dry-run
#   safe-delete.sh <file_id> --permanent --confirm    # L2 permanent, execute (provenance present)
#   safe-delete.sh <file_id> --permanent \
#                  --i-confirm-name="<exact-name>"    # L3 permanent, execute (no provenance)
#
# Stdout: JSON
#   dry-run:   {action:"trash"|"permanent", dry_run:true, metadata:{...},
#              provenance_tag:bool, warnings:[...], next:"<re-run cmd>"}
#   executed:  {action:"trashed"|"permanent_deleted", dry_run:false,
#              file_id, file_name}
# Stderr: human-readable progress + warnings.
#
# Exit codes:
#   0   success (dry-run preview, or executed action)
#   1   usage / pre-flight error
#   2   file not found / 404
#   3   confirmation gate failed (e.g. typed name mismatch on L3)
#   10  auth / scope error (passed through from gws-wrap)
#   11  rate limit
#   12  generic API error
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly GWS_WRAP="${SCRIPT_DIR}/gws-wrap.sh"

PROVENANCE_KEY="created_by"
PROVENANCE_VALUE="gws-toolkit"

die() { printf 'safe-delete: %s\n' "$*" >&2; exit "${2:-1}"; }
usage() {
  sed -n '8,50p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 1
}

# --- arg parse -------------------------------------------------------------
FILE_ID=""
PERMANENT=0
CONFIRM=0
TYPED_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --permanent) PERMANENT=1; shift ;;
    --confirm) CONFIRM=1; shift ;;
    --i-confirm-name=*) TYPED_NAME="${1#*=}"; CONFIRM=1; shift ;;
    --i-confirm-name) TYPED_NAME="${2:-}"; CONFIRM=1; shift 2 ;;
    -h|--help) usage ;;
    -*) die "unknown flag: $1" ;;
    *) [[ -z "${FILE_ID}" ]] && FILE_ID="$1" || die "unexpected positional: $1" ; shift ;;
  esac
done

[[ -n "${FILE_ID}" ]] || die "missing <file_id>"
[[ -x "${GWS_WRAP}" ]] || die "gws-wrap.sh not executable at ${GWS_WRAP}"
command -v jq >/dev/null 2>&1 || die "jq not found"

# --- fetch metadata --------------------------------------------------------
# fields request includes appProperties + name + size + mimeType + owners +
# parents + modifiedTime + trashed. If the file is already trashed, we still
# show metadata but flip "next" guidance.
metadata_json="$(
  "${GWS_WRAP}" drive files get \
    --params "$(jq -nc --arg id "${FILE_ID}" '{
      fileId: $id,
      fields: "id,name,mimeType,size,modifiedTime,owners(emailAddress,displayName),parents,trashed,appProperties"
    }')" 2>/dev/null
)" || {
  rc=$?
  case "${rc}" in
    10) die "auth / scope error fetching metadata; run gws-setup" 10 ;;
    *) die "file not found or fetch failed (rc=${rc})" 2 ;;
  esac
}

[[ -n "${metadata_json}" ]] || die "empty metadata response" 2

file_name="$(printf '%s' "${metadata_json}" | jq -r '.name // empty')"
[[ -n "${file_name}" ]] || die "metadata missing name field" 2

# Provenance check: is appProperties.<PROVENANCE_KEY> == <PROVENANCE_VALUE>?
provenance_tag="$(printf '%s' "${metadata_json}" | jq -r --arg k "${PROVENANCE_KEY}" --arg v "${PROVENANCE_VALUE}" '
  (.appProperties // {}) | (.[$k] // "") | (. == $v)
')"
[[ "${provenance_tag}" == "true" ]] || provenance_tag="false"

# --- compose warnings ------------------------------------------------------
warnings_json="[]"
if [[ "${PERMANENT}" == "1" && "${provenance_tag}" == "false" ]]; then
  warnings_json="$(jq -nc '["L3: target lacks gws-toolkit provenance tag (appProperties.created_by). Permanent deletion requires --i-confirm-name=<exact-name>"]')"
elif [[ "${PERMANENT}" == "1" ]]; then
  warnings_json="$(jq -nc '["L2: permanent deletion is irreversible (no Drive Trash recovery)"]')"
fi

# --- dry-run path ----------------------------------------------------------
if [[ "${CONFIRM}" == "0" ]]; then
  if [[ "${PERMANENT}" == "1" ]]; then
    if [[ "${provenance_tag}" == "false" ]]; then
      next_cmd="bash safe-delete.sh ${FILE_ID} --permanent --i-confirm-name=\"${file_name}\""
      action="permanent"
    else
      next_cmd="bash safe-delete.sh ${FILE_ID} --permanent --confirm"
      action="permanent"
    fi
  else
    next_cmd="bash safe-delete.sh ${FILE_ID} --confirm"
    action="trash"
  fi

  jq -nc \
    --arg action "${action}" \
    --argjson metadata "${metadata_json}" \
    --argjson provenance "${provenance_tag}" \
    --argjson warnings "${warnings_json}" \
    --arg next "${next_cmd}" \
    '{
      action: $action,
      dry_run: true,
      provenance_tag: $provenance,
      metadata: $metadata,
      warnings: $warnings,
      next: $next
    }'
  exit 0
fi

# --- L3 typed-name confirmation gate ---------------------------------------
if [[ "${PERMANENT}" == "1" && "${provenance_tag}" == "false" ]]; then
  if [[ -z "${TYPED_NAME}" ]]; then
    die "L3 confirmation required: pass --i-confirm-name=\"${file_name}\" (file lacks gws-toolkit provenance)" 3
  fi
  if [[ "${TYPED_NAME}" != "${file_name}" ]]; then
    die "L3 typed-name mismatch: --i-confirm-name=\"${TYPED_NAME}\" does not match file name \"${file_name}\"" 3
  fi
fi

# --- execute ---------------------------------------------------------------
if [[ "${PERMANENT}" == "1" ]]; then
  printf '[safe-delete] PERMANENT delete: %s (id=%s)\n' "${file_name}" "${FILE_ID}" >&2
  "${GWS_WRAP}" drive files delete \
    --params "$(jq -nc --arg id "${FILE_ID}" '{fileId: $id}')"
  jq -nc --arg id "${FILE_ID}" --arg name "${file_name}" \
    '{action:"permanent_deleted", dry_run:false, file_id:$id, file_name:$name}'
else
  printf '[safe-delete] trashing: %s (id=%s)\n' "${file_name}" "${FILE_ID}" >&2
  "${GWS_WRAP}" drive files update \
    --params "$(jq -nc --arg id "${FILE_ID}" '{fileId: $id}')" \
    --json '{"trashed":true}' >/dev/null
  jq -nc --arg id "${FILE_ID}" --arg name "${file_name}" \
    '{action:"trashed", dry_run:false, file_id:$id, file_name:$name}'
fi
