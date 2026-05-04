#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# gws-login.sh — user-facing OAuth login (with --switch for account swap)
# -----------------------------------------------------------------------------
# Wraps `gws auth login --scopes=...` (4-API scope set) with two
# additions over a raw gws call:
#   1. Idempotent — if already authed (`gws auth status` reports
#      auth_method=oauth2 + token_valid=true), exits 0 without
#      re-prompting unless --switch is given.
#   2. --switch — invokes gws-logout.sh first to clear local creds,
#      then runs OAuth. Google's account picker appears in the
#      browser (provided multiple Google accounts are signed in to
#      the browser session); pick the new account.
#
# Relationship to refresh-auth.sh:
#   - refresh-auth.sh: 7-day Testing-mode token expired, same account
#   - gws-login.sh:    first-time login after auto-setup, OR
#                      account switch (--switch)
# Both ultimately call `gws auth login`; the split is intent + UX
# framing, not mechanism.
#
# Args:
#   --switch     Logout local creds first, then re-auth (account swap).
#   --dry-run    Print the plan; do not touch state.
#   -h|--help    Print usage.
#
# Env:
#   GWS_TOOLKIT_SCOPES    Override scope set (full URLs, comma-separated).
#                         Default: 4-API set (presentations + drive +
#                         documents + spreadsheets).
#
# Pre-flight:
#   - ~/.config/gws/client_secret.json must exist
#   - ~/.config/gws/env.sh must exist (issue #119 workaround env vars)
#   - gws binary in PATH or ~/.cache/slides-toolkit/bin/
#
# Stdin: none
# Stdout: JSON
#   {"status":"success","action":"login"|"already_authed"|"switched",
#    "user":"<email>"|null,
#    "scopes":["presentations","drive","documents","spreadsheets"],
#    "dry_run":bool}
# Stderr: human-readable progress.
#
# Exit codes (per TECH-SPEC v0.3 §4.2):
#   0   success
#   1   generic error (missing client_secret / env.sh / gws / arg)
#   10  OAuth flow failed (user cancelled, scope mismatch, etc.)
# =============================================================================

export LC_ALL="${LC_ALL:-en_US.UTF-8}"

readonly GWS_CONFIG_DIR="${HOME}/.config/gws"
readonly CLIENT_SECRET="${GWS_CONFIG_DIR}/client_secret.json"
readonly ENV_FILE="${GWS_CONFIG_DIR}/env.sh"
readonly CACHE_BIN_DIR="${HOME}/.cache/slides-toolkit/bin"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOGOUT_SCRIPT="${SCRIPT_DIR}/gws-logout.sh"

readonly SLIDES_SCOPE="https://www.googleapis.com/auth/presentations"
readonly DRIVE_SCOPE="https://www.googleapis.com/auth/drive"
readonly DOCS_SCOPE="https://www.googleapis.com/auth/documents"
readonly SHEETS_SCOPE="https://www.googleapis.com/auth/spreadsheets"
readonly DEFAULT_SCOPES="${SLIDES_SCOPE},${DRIVE_SCOPE},${DOCS_SCOPE},${SHEETS_SCOPE}"
SCOPES="${GWS_TOOLKIT_SCOPES:-${DEFAULT_SCOPES}}"

DRY_RUN=0
SWITCH=0

die_json() {
  local code="$1"
  local msg="$2"
  local encoded
  encoded="$(printf '%s' "${msg}" | jq -R -s '.' 2>/dev/null \
    || printf '"%s"' "${msg//\"/\\\"}")"
  printf '{"error":true,"exit_code":%s,"message":%s}\n' "${code}" "${encoded}" >&2
  exit "${code}"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die_json 1 "required command not found: $1"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --switch)   SWITCH=1; shift ;;
      --dry-run)  DRY_RUN=1; shift ;;
      -h|--help)
        cat <<'USAGE' >&2
Usage: gws-login.sh [--switch] [--dry-run]

OAuth login via `gws auth login` with the 4-API scope set
(presentations, drive, documents, spreadsheets). Idempotent — skips
the OAuth flow if already authed, unless --switch is given.

Args:
  --switch     Logout first, then re-auth. Google's account picker
               appears in the browser; pick the new account to swap.
               OAuth client config (client_secret.json, env.sh) is
               preserved — same GCP project, different end-user.
  --dry-run    Print the plan; do not touch state.
  -h|--help    Print this help.

Env:
  GWS_TOOLKIT_SCOPES   Override scopes (default: 4 APIs as full URLs,
                       comma-separated).

Exit codes:
  0   success
  1   generic error
  10  OAuth flow failed
USAGE
        exit 0
        ;;
      *) die_json 1 "unknown arg: $1" ;;
    esac
  done
}

# Returns the current authed user email via `gws auth status`,
# or empty string if not authed / unparseable.
current_user() {
  local gws_bin="$1"
  local jq_bin="$2"
  "${gws_bin}" auth status 2>/dev/null \
    | sed -n '/^{/,$p' \
    | "${jq_bin}" -r '
        select(.auth_method == "oauth2" and (.token_valid // false) == true)
        | .user // ""
      ' 2>/dev/null \
    || printf ''
}

emit_result() {
  local action="$1"
  local user="$2"
  local user_arg
  if [[ -n "${user}" ]]; then
    user_arg=( --arg user "${user}" )
    jq -n \
      --arg status "success" \
      --arg action "${action}" \
      "${user_arg[@]}" \
      --argjson dry "$([[ ${DRY_RUN} -eq 1 ]] && printf 'true' || printf 'false')" \
      '{
         status: $status,
         action: $action,
         user: $user,
         scopes: ["presentations", "drive", "documents", "spreadsheets"],
         dry_run: $dry
       }'
  else
    jq -n \
      --arg status "success" \
      --arg action "${action}" \
      --argjson dry "$([[ ${DRY_RUN} -eq 1 ]] && printf 'true' || printf 'false')" \
      '{
         status: $status,
         action: $action,
         user: null,
         scopes: ["presentations", "drive", "documents", "spreadsheets"],
         dry_run: $dry
       }'
  fi
}

main() {
  require_cmd jq
  parse_args "$@"

  local gws_bin jq_bin
  gws_bin="$(command -v gws || printf '%s/gws' "${CACHE_BIN_DIR}")"
  jq_bin="$(command -v jq)"

  # Pre-flight (skip in dry-run if files missing — show plan anyway)
  if (( DRY_RUN == 0 )); then
    [[ -f "${CLIENT_SECRET}" ]] \
      || die_json 1 "client_secret.json not found at ${CLIENT_SECRET}; run auto-setup.sh first"
    [[ -f "${ENV_FILE}" ]] \
      || die_json 1 "env.sh not found at ${ENV_FILE}; run auto-setup.sh first"
    [[ -x "${gws_bin}" ]] \
      || die_json 1 "gws binary not found at ${gws_bin}; run bootstrap.sh first"
  fi

  # --switch: clear creds first, then fall through to login below
  if (( SWITCH == 1 )); then
    if (( DRY_RUN == 1 )); then
      printf '[gws-login] [dry-run] --switch: would invoke gws-logout.sh\n' >&2
      printf '[gws-login] [dry-run] would run: %s auth login --scopes=%s\n' \
        "${gws_bin}" "${SCOPES}" >&2
      emit_result "switched" ""
      exit 0
    fi
    [[ -x "${LOGOUT_SCRIPT}" ]] \
      || die_json 1 "gws-logout.sh not executable at ${LOGOUT_SCRIPT}"
    printf '[gws-login] --switch: clearing local creds via gws-logout.sh\n' >&2
    if ! "${LOGOUT_SCRIPT}" >/dev/null; then
      die_json 1 "gws-logout.sh failed (cannot prepare clean state for switch)"
    fi
    # Fall through to OAuth flow below.
  else
    # Idempotent: skip if already authed
    local existing_user
    existing_user="$(current_user "${gws_bin}" "${jq_bin}")"
    if [[ -n "${existing_user}" ]]; then
      printf '[gws-login] already authed as %s; use --switch to swap account\n' \
        "${existing_user}" >&2
      if (( DRY_RUN == 1 )); then
        printf '[gws-login] [dry-run] would skip; already authed\n' >&2
      fi
      emit_result "already_authed" "${existing_user}"
      exit 0
    fi

    if (( DRY_RUN == 1 )); then
      printf '[gws-login] [dry-run] would run: %s auth login --scopes=%s\n' \
        "${gws_bin}" "${SCOPES}" >&2
      emit_result "login" ""
      exit 0
    fi
  fi

  # Execute OAuth flow
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  export GOOGLE_WORKSPACE_CLI_CLIENT_ID GOOGLE_WORKSPACE_CLI_CLIENT_SECRET
  [[ -n "${GOOGLE_WORKSPACE_CLI_CLIENT_ID:-}" ]] \
    || die_json 1 "GOOGLE_WORKSPACE_CLI_CLIENT_ID missing in ${ENV_FILE}"
  [[ -n "${GOOGLE_WORKSPACE_CLI_CLIENT_SECRET:-}" ]] \
    || die_json 1 "GOOGLE_WORKSPACE_CLI_CLIENT_SECRET missing in ${ENV_FILE}"

  printf '[gws-login] opening browser for OAuth (scopes: %s)\n' "${SCOPES}" >&2
  if ! "${gws_bin}" auth login --scopes="${SCOPES}"; then
    die_json 10 "gws auth login failed"
  fi

  local new_user
  new_user="$(current_user "${gws_bin}" "${jq_bin}")"
  if [[ -n "${new_user}" ]]; then
    printf '[gws-login] ✓ logged in as %s\n' "${new_user}" >&2
  else
    printf '[gws-login] ✓ login successful\n' >&2
  fi

  if (( SWITCH == 1 )); then
    emit_result "switched" "${new_user}"
  else
    emit_result "login" "${new_user}"
  fi
}

main "$@"
