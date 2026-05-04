#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# credential-check.sh — Keychain / file backend detection + token-age metadata
# -----------------------------------------------------------------------------
# Responsibilities:
#   - Detect whether the macOS Keychain is usable for gws refresh_token
#     storage (the common silent-fail symptom is a non-zero exit with
#     "could not be found" on stderr — fall through to the file backend).
#   - Detect whether the file fallback
#     (~/.config/gws/keyring-file.json) exists.
#   - Read metadata (mtime) from ~/.config/gws/credentials.enc to estimate
#     token age. Contents are never read (ASVS V14 secrets-at-rest:
#     metadata-only).
#
# Security rules specific to this script:
#   - Never read credential-file contents; only stat metadata (existence +
#     mtime).
#   - Never echo env vars or credentials to stdout.
#   - Never pass through system error messages from stderr verbatim (they
#     may include paths).
#
# Upstream refs:
#   - TECH-SPEC §4.2 `scripts/gws/credential-check.sh` contract
#   - TECH-SPEC §4.8 Credential flow (ASVS V14)
#   - TECH-SPEC §6.2 Keychain silent-fail fallback
#   - TECH-SPEC §6.3 7-day token expiry UX
#
# Args: none
#
# Stdin: none
# Stdout: JSON `{"backend":"keychain"|"file"|"none","token_valid":bool,"expires_in_days":int}`
#        — always a structured status JSON; the no-backend case does NOT
#          degrade to an error JSON, so callers such as gws-wrap.sh can
#          parse uniformly. Severity is signalled via the exit code.
# Stderr: human-readable progress (no secrets).
#
# Exit codes (per TECH-SPEC §4.2):
#   0   success (backend usable; token_valid may be true or false)
#   1   generic error (missing required command, etc.)
#   18  Keychain unavailable AND file backend also unavailable
#       (run `gws auth`). Note: stdout still returns the structured
#       `{"backend":"none",...}` status; the exit code signals severity
#       (errors-out-of-band principle).
# =============================================================================

export LC_ALL="${LC_ALL:-en_US.UTF-8}"

readonly GWS_CONFIG_DIR="${HOME}/.config/gws"
readonly FILE_BACKEND="${GWS_CONFIG_DIR}/keyring-file.json"
readonly CREDENTIALS_FILE="${GWS_CONFIG_DIR}/credentials.enc"
readonly CACHE_BIN_DIR="${HOME}/.cache/slides-toolkit/bin"

# Google OAuth External + Testing：refresh_token 7 天 lifetime（TECH-SPEC §6.3）
readonly TOKEN_LIFETIME_DAYS=7

# --- helper -----------------------------------------------------------------
die_json() {
  local code="$1"
  local msg="$2"
  local encoded
  encoded="$(printf '%s' "${msg}" | jq -R -s '.' 2>/dev/null || printf '"%s"' "${msg//\"/\\\"}")"
  printf '{"error":true,"exit_code":%s,"message":%s}\n' "${code}" "${encoded}" >&2
  exit "${code}"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die_json 1 "required command not found: $1"
}

# --- gws auth status JSON probe（v0.22.5+）---------------------------------
# gws v0.22.5 起把 refresh token 存在 ~/.config/gws/credentials.enc（AES-
# 256-GCM 加密），加密 key 存於 OS keyring（service name 由 gws 內部管理，
# 不再固定為 "gws"）。直接用 `gws auth status` 自報 backend + token_valid，
# 比外部偵測 keychain entry 可靠：gws 自己最清楚自己的 storage layout。
#
# Echoes the captured JSON to stdout (single-line); empty on failure.
gws_auth_status_json() {
  local gws_bin
  gws_bin="$(command -v gws || printf '%s/gws' "${CACHE_BIN_DIR}")"
  [[ -x "${gws_bin}" ]] || { printf ''; return 1; }
  "${gws_bin}" auth status 2>/dev/null \
    | sed -n '/^{/,$p' \
    | jq -c '.' 2>/dev/null \
    || { printf ''; return 1; }
}

# --- file backend fallback（macOS Keychain 不可用時）------------------------
# gws auth status 的 .keyring_backend == "file" 時走此路徑（gws 自己已經 fallback
# 過）。我們不再自己嘗試 fallback；信任 gws 的 backend 判斷。

# --- file backend 可用性 ---------------------------------------------------
check_file_backend() {
  [[ -f "${FILE_BACKEND}" ]]
}

# --- 計算 token 年齡（metadata only；不讀檔內容）-----------------------------
# 回傳剩餘天數（stdout）；若找不到 credentials 檔則印 -1
compute_expires_in_days() {
  if [[ ! -e "${CREDENTIALS_FILE}" ]]; then
    printf -- '-1'
    return
  fi
  # macOS stat: -f %m = mtime (epoch)
  local mtime now age_sec age_days remaining
  mtime="$(stat -f '%m' "${CREDENTIALS_FILE}" 2>/dev/null || printf '0')"
  now="$(date +%s)"
  if [[ "${mtime}" -eq 0 ]]; then
    printf -- '-1'
    return
  fi
  age_sec=$(( now - mtime ))
  age_days=$(( age_sec / 86400 ))
  remaining=$(( TOKEN_LIFETIME_DAYS - age_days ))
  printf '%d' "${remaining}"
}

# --- 結果輸出（ASVS V1 output encoding） ------------------------------------
emit_result() {
  local backend="$1"       # "keychain" | "file"
  local token_valid="$2"   # "true" | "false"
  local expires_days="$3"  # int

  jq -n \
    --arg backend "${backend}" \
    --argjson valid "${token_valid}" \
    --argjson exp "${expires_days}" \
    '{backend: $backend, token_valid: $valid, expires_in_days: $exp}'
}

# --- main -------------------------------------------------------------------
main() {
  require_cmd jq
  require_cmd stat
  require_cmd date

  local status_json backend token_valid backend_usable
  status_json="$(gws_auth_status_json)"

  if [[ -z "${status_json}" ]]; then
    # gws 不存在或 auth status 解析失敗 → 沒有可用 backend
    backend="none"
    token_valid="false"
    backend_usable=0
    printf '[credential-check] gws auth status unavailable; run: gws auth\n' >&2
  else
    local raw_backend
    raw_backend="$(printf '%s' "${status_json}" | jq -r '.keyring_backend // "none"')"
    case "${raw_backend}" in
      keyring) backend="keychain" ;;
      file)    backend="file" ;;
      *)       backend="none" ;;
    esac
    token_valid="$(printf '%s' "${status_json}" | jq -r '.token_valid // false')"
    if [[ "${backend}" == "none" || "${token_valid}" != "true" ]]; then
      backend_usable=0
    else
      backend_usable=1
    fi
    if (( backend_usable == 0 )); then
      printf '[credential-check] gws reports backend=%s token_valid=%s; run: gws auth\n' \
        "${backend}" "${token_valid}" >&2
    fi
  fi

  local remaining
  remaining="$(compute_expires_in_days)"

  emit_result "${backend}" "${token_valid}" "${remaining}"

  if (( backend_usable == 0 )); then
    exit 18
  fi
}

main "$@"
