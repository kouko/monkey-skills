#!/usr/bin/env bash
set -uo pipefail

# =============================================================================
# reset-local.sh — wipe local gws-toolkit state to re-test fresh-machine flow
# -----------------------------------------------------------------------------
# Removes everything auto-setup.sh would create on the user's machine, while
# preserving GCP-side state (project, OAuth Client, Test User config, API
# enables). After running this, `auto-setup.sh` should:
#   - skip steps 1-4 (gcloud installed + authed, project exists, APIs enabled)
#   - on step 5 either prompt for a fresh client_secret download OR
#     auto-resume if the user keeps a backup in ~/Downloads
#   - run steps 6-8 fresh (credential install, bootstrap, gws auth login)
#
# Use this to validate that the auto-setup fixes (bootstrap step,
# JSON-aware verify, credential-check rewrite) hold up across re-runs
# without paying the 15-min full-Console-walkthrough cost.
#
# Targets removed:
#   ~/.cache/gws-toolkit/bin/         entire dir (gws + jq + .version)
#   ~/.config/gws/client_secret.json     downloaded OAuth client
#   ~/.config/gws/env.sh                 BYO-OAuth-client env vars
#   ~/.config/gws/credentials.enc        encrypted refresh token
#   ~/.config/gws/keyring-file.json      file-backend fallback (if any)
#   macOS Keychain entry: service=gws-cli, account=$USER
#                                        the AES-256-GCM key that decrypts
#                                        credentials.enc; orphaned without
#                                        credentials.enc but cleaner to
#                                        remove
#
# NOT removed:
#   GCP project (e.g. gws-toolkit-260504)
#   OAuth consent screen + Test User config
#   OAuth Client (Desktop app) on GCP
#   Enabled APIs (slides + drive + docs + sheets)
#   gcloud install
#   gcloud's own auth state (`gcloud auth list`)
#
# To also reset GCP-side state, see "Manual full-reset" at bottom of this
# script's source.
#
# Usage:
#   bash gws-toolkit/scripts/dev/reset-local.sh             # interactive confirm
#   bash gws-toolkit/scripts/dev/reset-local.sh --yes       # skip confirm
#   bash gws-toolkit/scripts/dev/reset-local.sh --dry-run   # show plan only
# =============================================================================

readonly CACHE_BIN="${HOME}/.cache/gws-toolkit/bin"
readonly GWS_CONFIG="${HOME}/.config/gws"
readonly KEYCHAIN_SERVICE="gws-cli"

YES=0
DRY=0
for arg in "$@"; do
  case "${arg}" in
    --yes|-y) YES=1 ;;
    --dry-run) DRY=1 ;;
    -h|--help)
      sed -n '7,40p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) printf 'reset-local: unknown arg: %s\n' "${arg}" >&2; exit 1 ;;
  esac
done

run() {
  if (( DRY == 1 )); then
    printf '[dry-run] %s\n' "$*" >&2
  else
    eval "$@"
  fi
}

list_target() {
  local label="$1" path="$2"
  if [[ -e "${path}" ]]; then
    printf '  ✓ %-30s %s\n' "${label}" "${path}" >&2
  fi
}

printf '\n=== reset-local.sh — local state wipe ===\n\n' >&2
printf 'Targets present:\n' >&2
list_target "binary cache dir"     "${CACHE_BIN}"
list_target "OAuth client_secret"  "${GWS_CONFIG}/client_secret.json"
list_target "BYO-client env.sh"    "${GWS_CONFIG}/env.sh"
list_target "encrypted creds"      "${GWS_CONFIG}/credentials.enc"
list_target "file-backend creds"   "${GWS_CONFIG}/keyring-file.json"
if security find-generic-password -s "${KEYCHAIN_SERVICE}" -a "${USER}" >/dev/null 2>&1; then
  printf '  ✓ %-30s service=%s account=%s\n' "macOS Keychain entry" "${KEYCHAIN_SERVICE}" "${USER}" >&2
fi

if (( YES == 0 )) && (( DRY == 0 )); then
  printf '\nWipe these and proceed? (y/N): ' >&2
  read -r ans
  case "${ans}" in
    y|Y|yes|YES) ;;
    *) echo "aborted" >&2; exit 1 ;;
  esac
fi

printf '\n--- removing ---\n' >&2

# 1. Binary cache dir
if [[ -d "${CACHE_BIN}" ]]; then
  run "rm -rf '${CACHE_BIN}'"
  printf '  removed %s\n' "${CACHE_BIN}" >&2
fi

# 2. Config dir contents (client_secret, env.sh, credentials.enc, keyring-file.json)
for f in client_secret.json env.sh credentials.enc keyring-file.json; do
  if [[ -e "${GWS_CONFIG}/${f}" ]]; then
    run "rm -f '${GWS_CONFIG}/${f}'"
    printf '  removed %s\n' "${GWS_CONFIG}/${f}" >&2
  fi
done

# 3. macOS Keychain entry (the AES-256-GCM key)
if security find-generic-password -s "${KEYCHAIN_SERVICE}" -a "${USER}" >/dev/null 2>&1; then
  run "security delete-generic-password -s '${KEYCHAIN_SERVICE}' -a '${USER}' >/dev/null 2>&1"
  printf '  removed Keychain entry: service=%s account=%s\n' "${KEYCHAIN_SERVICE}" "${USER}" >&2
fi

printf '\n=== done ===\n' >&2
printf 'Re-run setup with:\n' >&2
printf '  GWS_TOOLKIT_PROJECT_ID="<your-project-id>" \\\n    bash gws-toolkit/scripts/gws/auto-setup.sh\n\n' >&2
printf 'Steps 1-4 will idempotent-skip (project + APIs already on GCP).\n' >&2
printf 'Step 5 will need either an existing client_secret_*.json freshly\n' >&2
printf 'placed in ~/Downloads, OR a fresh OAuth Client created via the\n' >&2
printf 'Console URLs (re-uses the same Test User).\n' >&2

# =============================================================================
# Manual full-reset (also wipes GCP-side state):
# -----------------------------------------------------------------------------
# Run this script first, then:
#
#   PROJECT_ID="gws-toolkit-260504"   # or whatever your project is
#
#   # 1. Disable APIs (optional — saves quota; not required)
#   gcloud services disable slides.googleapis.com drive.googleapis.com \
#     docs.googleapis.com sheets.googleapis.com --project=${PROJECT_ID}
#
#   # 2. Delete the OAuth Client + Test User config requires manual UI:
#   #    https://console.cloud.google.com/auth/clients?project=${PROJECT_ID}
#   #    https://console.cloud.google.com/auth/audience?project=${PROJECT_ID}
#
#   # 3. Delete the project itself (30-day soft-delete window in GCP)
#   gcloud projects delete ${PROJECT_ID}
#
# After that, auto-setup.sh starts truly from zero: project create,
# Console walkthrough, OAuth Client, the works (~15 min).
# =============================================================================
