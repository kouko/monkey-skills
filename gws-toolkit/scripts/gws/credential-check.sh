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

# Google OAuth External + Testing：refresh_token 7 天 lifetime（TECH-SPEC §6.3）
readonly TOKEN_LIFETIME_DAYS=7

# Keychain service 名稱（gws 預設）；TODO：確認 gws 實際 service name
readonly KEYCHAIN_SERVICE="gws"

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

# --- Keychain 可用性偵測（§6.2） --------------------------------------------
# 回傳：
#   0 = Keychain 中找到 gws 條目（可用）
#   1 = Keychain silent-fail 或條目不存在
check_keychain() {
  # macOS only；其他平台（未來 portability）視為無 keychain
  if [[ "$(uname -s)" != "Darwin" ]]; then
    return 1
  fi
  if ! command -v security >/dev/null 2>&1; then
    return 1
  fi
  # 合併 stderr→stdout，不讓 stderr 直接漏（可能含 path）
  local out
  out="$(security find-generic-password -s "${KEYCHAIN_SERVICE}" -a "${USER}" 2>&1 || true)"
  if printf '%s' "${out}" | grep -qiE 'could not be found|errSec'; then
    return 1
  fi
  # 若 exit 0 且輸出含 "keychain:"（security 標準輸出頭）→ OK
  if printf '%s' "${out}" | grep -q 'keychain:'; then
    return 0
  fi
  return 1
}

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

  local backend=""
  local backend_usable=1
  if check_keychain; then
    backend="keychain"
  elif check_file_backend; then
    backend="file"
    printf '[credential-check] keychain silent-fail or absent; using file backend\n' >&2
  else
    # 兩邊都不可用：stdout 仍回結構化狀態（backend=none），exit 18 表嚴重度
    backend="none"
    backend_usable=0
    printf '[credential-check] no backend usable; run: gws auth\n' >&2
  fi

  local remaining
  remaining="$(compute_expires_in_days)"

  # token_valid 的語意：有可用 backend **且** credentials file 在 7 天內
  local token_valid="false"
  if (( backend_usable == 1 )) && (( remaining > 0 )); then
    token_valid="true"
  fi

  emit_result "${backend}" "${token_valid}" "${remaining}"

  if (( backend_usable == 0 )); then
    exit 18
  fi
}

main "$@"
