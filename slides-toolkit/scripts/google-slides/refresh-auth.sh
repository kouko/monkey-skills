#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# refresh-auth.sh — slides-toolkit gws refresh-token re-auth helper
# -----------------------------------------------------------------------------
# 用途：
#   一鍵重新向 Google 取得 gws refresh token（當 Testing mode 7 天過期時）。
#   包住完整 scope URL 和 issue #119 env vars export，免背長指令。
#
#   使用場景：
#     1. 每 7 天主動跑一次（alias: `gws-relogin`）
#     2. 被 gws-wrap.sh 或 google-slides-builder 在偵測 exit 10 時自動 invoke
#     3. 手動 `bash refresh-auth.sh` 當 debug 用
#
# 前置條件：
#   - `google-slides-setup` 已完成首次設定
#   - `~/.config/gws/client_secret.json` 存在
#   - `~/.config/gws/env.sh` 存在（issue #119 workaround env vars）
#   - `~/.cache/slides-toolkit/bin/gws` 存在
#
# Args: none（flag 走 env）
#
# Env:
#   SLIDES_TOOLKIT_SCOPES  override scope clamp
#                          default: presentations,drive.file
#                          為完整 URL 的 comma-separated list
#
# Stdin: none
# Stdout: gws auth login 的 stdout（含 URL + 成功訊息）
# Stderr: 人讀 progress
#
# Exit codes:
#   0  success（re-auth 完成，credentials.enc 已更新）
#   1  generic error（missing client_secret / env.sh / gws binary）
#   10 gws auth login fail（user 取消瀏覽器 consent / scope 錯等）
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
[[ -f "${CLIENT_SECRET}" ]] || die "client_secret.json not found at ${CLIENT_SECRET}. Run google-slides-setup first."
[[ -f "${ENV_FILE}" ]]      || die "env.sh not found at ${ENV_FILE}. Run google-slides-setup first."
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
