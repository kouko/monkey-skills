#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# tag-create.sh — wrapper for gws drive files create that injects toolkit
#                 provenance into appProperties
# -----------------------------------------------------------------------------
# Wraps `gws drive files create --upload <local>` with a JSON body that
# pre-fills `appProperties.created_by` (= "gws-toolkit"),
# `appProperties.created_by_version` (= toolkit semver), and
# `appProperties.created_at` (UTC ISO 8601). These tags drive the
# safe-delete.sh L1/L2/L3 tier decision: files we created are eligible
# for the lower-friction L2 confirmation; files we did NOT create
# require L3 typed-name confirmation.
#
# Usage:
#   tag-create.sh --name <filename> --upload <local-path> [--mime <type>]
#                 [--parent <folder-id>] [--extra-app-properties '<json>']
#                 [--extra-fields '<json>']
#
# Args:
#   --name <s>          Drive display name (required)
#   --upload <path>     Local file to upload (required)
#   --mime <s>          MIME type (optional; gws auto-detects when omitted)
#   --parent <id>       Parent folder Drive ID (optional)
#   --extra-app-properties <json>
#                       Merge additional appProperties (object); merged
#                       AFTER the toolkit-managed three keys, so caller
#                       cannot accidentally override created_by /
#                       created_by_version / created_at.
#   --extra-fields <json>
#                       Merge additional top-level fields into the create
#                       body (object). Cannot override
#                       `name`, `mimeType`, `appProperties`, or `parents`.
#
# Stdin: passed through to gws drive files create (typically empty; the
#        upload uses --upload binary path).
# Stdout: gws drive files create response JSON (file resource).
# Stderr: progress.
#
# Exit codes (passed through from gws-wrap):
#   0  success
#   1  usage / pre-flight
#   10 auth / scope error
#   11 rate limit
#   12 generic API error
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly GWS_WRAP="${SCRIPT_DIR}/gws-wrap.sh"
readonly PIN_FILE="$(cd "${SCRIPT_DIR}/../.." && pwd)/UPSTREAM_GWS_VERSION"

# Toolkit version: read from plugin.json (single source of truth) so the
# provenance tag tracks releases automatically. Fallback to "unknown" if
# plugin.json is unreadable.
TOOLKIT_VERSION="$(jq -r '.version // "unknown"' "$(cd "${SCRIPT_DIR}/../.." && pwd)/.claude-plugin/plugin.json" 2>/dev/null || printf 'unknown')"

die() { printf 'tag-create: %s\n' "$*" >&2; exit "${2:-1}"; }
usage() {
  sed -n '8,40p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 1
}

# --- arg parse -------------------------------------------------------------
NAME=""
UPLOAD=""
MIME=""
PARENT=""
EXTRA_APP=""
EXTRA_FIELDS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="${2:-}"; shift 2 ;;
    --upload) UPLOAD="${2:-}"; shift 2 ;;
    --mime) MIME="${2:-}"; shift 2 ;;
    --parent) PARENT="${2:-}"; shift 2 ;;
    --extra-app-properties) EXTRA_APP="${2:-}"; shift 2 ;;
    --extra-fields) EXTRA_FIELDS="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) die "unknown arg: $1" ;;
  esac
done

[[ -n "${NAME}" ]] || die "missing --name <filename>"
[[ -n "${UPLOAD}" ]] || die "missing --upload <local-path>"
[[ -f "${UPLOAD}" ]] || die "upload file not found: ${UPLOAD}"
[[ -x "${GWS_WRAP}" ]] || die "gws-wrap.sh not executable at ${GWS_WRAP}"
command -v jq >/dev/null 2>&1 || die "jq not found"

# --- compose body ----------------------------------------------------------
# Toolkit-managed appProperties (always present, cannot be overridden by caller)
managed_app="$(jq -nc \
  --arg created_by "gws-toolkit" \
  --arg version "${TOOLKIT_VERSION}" \
  --arg created_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{
    created_by: $created_by,
    created_by_version: $version,
    created_at: $created_at
  }')"

# Merge extras after managed (so managed wins on conflict)
if [[ -n "${EXTRA_APP}" ]]; then
  app_properties="$(jq -nc --argjson extra "${EXTRA_APP}" --argjson managed "${managed_app}" '$extra * $managed')" \
    || die "invalid --extra-app-properties JSON"
else
  app_properties="${managed_app}"
fi

# Top-level body: name + appProperties (+ optional mime + parents + extras)
body="$(jq -nc --arg name "${NAME}" --argjson app "${app_properties}" '{name: $name, appProperties: $app}')"

if [[ -n "${MIME}" ]]; then
  body="$(jq -nc --arg mime "${MIME}" --argjson b "${body}" '$b + {mimeType: $mime}')"
fi

if [[ -n "${PARENT}" ]]; then
  body="$(jq -nc --arg pid "${PARENT}" --argjson b "${body}" '$b + {parents: [$pid]}')"
fi

if [[ -n "${EXTRA_FIELDS}" ]]; then
  # Extras merged FIRST so toolkit-managed (name/mimeType/appProperties/parents) can override
  body="$(jq -nc --argjson extra "${EXTRA_FIELDS}" --argjson b "${body}" '$extra * $b')" \
    || die "invalid --extra-fields JSON"
fi

# --- invoke gws-wrap -------------------------------------------------------
printf '[tag-create] uploading %s as "%s" with provenance tag\n' "${UPLOAD}" "${NAME}" >&2

"${GWS_WRAP}" drive files create \
  --json "${body}" \
  --upload "${UPLOAD}"
