#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# refresh-auth.sh — slides-toolkit gws refresh-token re-auth helper
# -----------------------------------------------------------------------------
# One-shot helper to re-obtain a gws refresh token from Google (used when
# the 7-day Testing-mode expiry hits). Wraps the full scope URLs and the
# issue #119 env-var exports so the user does not need to memorize the
# long command.
#
# Usage scenarios:
#   1. Run proactively every 7 days (alias: `gws-relogin`).
#   2. Auto-invoked by gws-wrap.sh or slides-builder when exit 10
#      is detected.
#   3. Manual `bash refresh-auth.sh` for debugging.
#
# Preconditions:
#   - `gws-setup` has completed the first-time setup.
#   - `~/.config/gws/client_secret.json` exists.
#   - `~/.config/gws/env.sh` exists (issue #119 workaround env vars).
#   - `~/.cache/slides-toolkit/bin/gws` exists.
#
# Args: none (flags via env).
#
# Env:
#   SLIDES_TOOLKIT_SCOPES  Override the scope clamp.
#                          Default: presentations,drive.file (as full URLs,
#                          comma-separated).
#
# Stdin: none
# Stdout: gws auth login stdout (consent URL + success message).
# Stderr: human-readable progress.
#
# Exit codes:
#   0  success (re-auth complete; credentials.enc refreshed)
#   1  generic error (missing client_secret / env.sh / gws binary)
#   10 gws auth login failed (user cancelled browser consent, scope
#      mismatch, etc.)
# =============================================================================

export LC_ALL="${LC_ALL:-en_US.UTF-8}"

readonly GWS_CONFIG_DIR="${HOME}/.config/gws"
readonly CLIENT_SECRET="${GWS_CONFIG_DIR}/client_secret.json"
readonly ENV_FILE="${GWS_CONFIG_DIR}/env.sh"
readonly GWS_BIN="${HOME}/.cache/slides-toolkit/bin/gws"

# Default scope set for slides-toolkit MVP (least-privilege per ASVS V1)
readonly DEFAULT_SCOPES="https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive.file"
SCOPES="${SLIDES_TOOLKIT_SCOPES:-${DEFAULT_SCOPES}}"

die() {
  printf '[refresh-auth] ERROR: %s\n' "$1" >&2
  exit "${2:-1}"
}

# Pre-flight：確認所有必要檔案在位
[[ -f "${CLIENT_SECRET}" ]] || die "client_secret.json not found at ${CLIENT_SECRET}. Run gws-setup first."
[[ -f "${ENV_FILE}" ]]      || die "env.sh not found at ${ENV_FILE}. Run gws-setup first."
[[ -x "${GWS_BIN}" ]]       || die "gws binary not found at ${GWS_BIN}. Run bootstrap.sh first."

# 載 issue #119 env vars
# shellcheck disable=SC1090
source "${ENV_FILE}"
export GOOGLE_WORKSPACE_CLI_CLIENT_ID GOOGLE_WORKSPACE_CLI_CLIENT_SECRET

[[ -n "${GOOGLE_WORKSPACE_CLI_CLIENT_ID:-}" ]]     || die "GOOGLE_WORKSPACE_CLI_CLIENT_ID not set after sourcing env.sh"
[[ -n "${GOOGLE_WORKSPACE_CLI_CLIENT_SECRET:-}" ]] || die "GOOGLE_WORKSPACE_CLI_CLIENT_SECRET not set after sourcing env.sh"

printf '[refresh-auth] initiating gws auth login with scopes: %s\n' "${SCOPES}" >&2
printf '[refresh-auth] browser will open; click "Allow" to complete re-auth (~10 sec)\n' >&2

# Delegate to gws auth login；成功 exit 0、失敗 gws 自己會印錯誤
if "${GWS_BIN}" auth login --scopes="${SCOPES}"; then
  printf '[refresh-auth] ✓ re-auth successful; refresh token valid for another ~7 days (Testing mode)\n' >&2
  exit 0
else
  exit 10
fi
