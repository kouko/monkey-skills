#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# gws-logout.sh — clear local gws credentials (account switch / cleanup helper)
# -----------------------------------------------------------------------------
# Wraps the upstream `gws auth logout` builtin with two additions:
#   1. Idempotent — exits 0 with action="already_logged_out" if no
#      credentials.enc / token_cache.json exist.
#   2. Surfaces https://myaccount.google.com/permissions as the
#      follow-up for users who want immediate server-side revocation.
#
# We do NOT auto-revoke server-side. Doing so would require decrypting
# credentials.enc to extract the refresh token, which breaks the
# metadata-only access pattern in credential-check.sh (ASVS V14
# secrets-at-rest). The 7-day Testing-mode token lifetime is the
# natural server-side expiry; users can revoke earlier by visiting the
# linked permissions page.
#
# Preserved across logout (intentionally): client_secret.json, env.sh
# — the OAuth client config is reusable across logins. Only the user's
# refresh token (credentials.enc + token_cache.json + Keychain entry)
# is cleared.
#
# Args:
#   --dry-run     Print the plan; do not touch state.
#   -h|--help     Print usage.
#
# Stdin: none
# Stdout: JSON
#   {"status":"success","action":"logout"|"already_logged_out",
#    "revoke_url":"https://myaccount.google.com/permissions",
#    "dry_run":bool}
# Stderr: human-readable progress.
#
# Exit codes (per TECH-SPEC v0.3 §4.2):
#   0   success (logged out, or already logged out)
#   1   generic error (missing dep, invalid arg)
#   10  logout failed (gws auth logout non-zero AND fallback rm could
#       not clean state)
# =============================================================================

export LC_ALL="${LC_ALL:-en_US.UTF-8}"

readonly GWS_CONFIG_DIR="${HOME}/.config/gws"
readonly CREDENTIALS_FILE="${GWS_CONFIG_DIR}/credentials.enc"
readonly TOKEN_CACHE="${GWS_CONFIG_DIR}/token_cache.json"
readonly CACHE_BIN_DIR="${HOME}/.cache/gws-toolkit/bin"
readonly REVOKE_URL="https://myaccount.google.com/permissions"

DRY_RUN=0

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
      --dry-run)  DRY_RUN=1; shift ;;
      -h|--help)
        cat <<'USAGE' >&2
Usage: gws-logout.sh [--dry-run]

Clear saved gws credentials (refresh token + token cache) so the next
login starts a fresh OAuth flow. Preserves OAuth client config
(client_secret.json, env.sh) — same GCP project across logins.

For immediate server-side revocation visit:
  https://myaccount.google.com/permissions

Args:
  --dry-run     Print the plan; do not touch state.
  -h|--help     Print this help.

Exit codes:
  0  success / already logged out
  1  generic error
  10 logout failed
USAGE
        exit 0
        ;;
      *) die_json 1 "unknown arg: $1" ;;
    esac
  done
}

emit_result() {
  local action="$1"
  jq -n \
    --arg status "success" \
    --arg action "${action}" \
    --arg url "${REVOKE_URL}" \
    --argjson dry "$([[ ${DRY_RUN} -eq 1 ]] && printf 'true' || printf 'false')" \
    '{
       status: $status,
       action: $action,
       revoke_url: $url,
       dry_run: $dry
     }'
}

main() {
  require_cmd jq
  parse_args "$@"

  local gws_bin
  gws_bin="$(command -v gws || printf '%s/gws' "${CACHE_BIN_DIR}")"

  # Already-logged-out detection (metadata only — never read content)
  if [[ ! -e "${CREDENTIALS_FILE}" && ! -e "${TOKEN_CACHE}" ]]; then
    printf '[gws-logout] already logged out (no credentials.enc / token_cache.json)\n' >&2
    if (( DRY_RUN == 1 )); then
      printf '[gws-logout] [dry-run] would skip; already clean\n' >&2
    fi
    emit_result "already_logged_out"
    exit 0
  fi

  if (( DRY_RUN == 1 )); then
    printf '[gws-logout] [dry-run] would run: %s auth logout\n' "${gws_bin}" >&2
    printf '[gws-logout] [dry-run]   (clears credentials.enc + token_cache.json + Keychain entry)\n' >&2
    printf '[gws-logout] [dry-run] server-side revoke (optional): %s\n' "${REVOKE_URL}" >&2
    emit_result "logout"
    exit 0
  fi

  [[ -x "${gws_bin}" ]] \
    || die_json 1 "gws binary not found at ${gws_bin}; run bootstrap.sh first"

  printf '[gws-logout] running: gws auth logout\n' >&2
  local rc=0
  "${gws_bin}" auth logout || rc=$?

  # Fallback: even if gws auth logout failed, try to rm leftover state.
  # Avoids a corrupt-but-non-empty credential file blocking next login.
  if (( rc != 0 )); then
    printf '[gws-logout] gws auth logout exited %d; attempting fallback cleanup\n' "${rc}" >&2
    rm -f "${CREDENTIALS_FILE}" "${TOKEN_CACHE}" || true
  fi

  if [[ -e "${CREDENTIALS_FILE}" || -e "${TOKEN_CACHE}" ]]; then
    die_json 10 "logout incomplete: leftover state at ${CREDENTIALS_FILE} or ${TOKEN_CACHE}"
  fi

  printf '[gws-logout] ✓ local credentials cleared\n' >&2
  printf '[gws-logout]   server-side revoke (optional): %s\n' "${REVOKE_URL}" >&2
  emit_result "logout"
}

main "$@"
