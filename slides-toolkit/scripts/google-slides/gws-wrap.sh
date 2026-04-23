#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# gws-wrap.sh — gws CLI wrapper with pre-flight + 429 退避
# -----------------------------------------------------------------------------
# 用途：
#   在每次呼叫 gws 前跑 env-guard（issue #119 pre-flight 檢測，不 apply）+
#   credential-check（token 有效性 / backend 偵測），然後以指數退避重試
#   429 / 5xx 錯誤；解析 structured error 映射到 TECH-SPEC §4.2 exit code。
#
# Upstream refs:
#   - TECH-SPEC §3.4 google-slides-builder
#   - TECH-SPEC §4.2 `scripts/google-slides/gws-wrap.sh` contract
#   - TECH-SPEC §4.3 gws CLI recipe mapping
#   - TECH-SPEC §6.4 Rate limit (429) 指數退避實作
#
# Args:
#   --dry-run                不呼叫 gws，只印出將執行的 command + args
#   <subcommand> <args...>   完整轉傳給 gws（例：`slides presentations batchUpdate ...`）
#
# Stdin: raw JSON（若 subcommand 需要）— 直接 passthrough 給 gws
# Stdout: gws 回傳的 JSON，原樣 passthrough
# Stderr: 人讀 progress + 結構化 error JSON on failure
#
# Exit codes (per TECH-SPEC §4.2)：
#   0   success
#   1   generic error（usage / pre-flight）
#   10  token expired / unauthenticated (401/403)
#   11  rate limit exhausted after retry (429 × 5)
#   12  Google resource not found / API error
#   16  issue #119 workaround needed（env-guard check fail）
#
# 預設：`BIN_DIR=${HOME}/.cache/slides-toolkit/bin`（由 bootstrap.sh 填入）
# =============================================================================

export LC_ALL="${LC_ALL:-en_US.UTF-8}"

# --- 常數 -------------------------------------------------------------------
readonly BIN_DIR="${BIN_DIR:-${HOME}/.cache/slides-toolkit/bin}"
readonly GWS="${BIN_DIR}/gws"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ENV_GUARD="${SCRIPT_DIR}/env-guard.sh"
readonly CRED_CHECK="${SCRIPT_DIR}/credential-check.sh"
readonly GWS_ENV_FILE="${HOME}/.config/gws/env.sh"

# Retry parameters（§6.4）
readonly MAX_ATTEMPTS=3        # 本 task spec: 5s/10s/20s, 3 次（TECH-SPEC §6.4 列 5 次，
                                # 但本 task 的題目要求 3 次；取題目的 3 次為主）
readonly RETRY_BASE_SEC=5

# --- 臨時目錄 --------------------------------------------------------------
TMP="$(mktemp -d -t gws-wrap.XXXXXX)"
trap 'rm -rf "${TMP}"' EXIT

DRY_RUN=0

# --- helper：structured error to stderr -------------------------------------
die_json() {
  local code="$1"
  local msg="$2"
  local encoded
  encoded="$(printf '%s' "${msg}" | jq -R -s '.' 2>/dev/null || printf '"%s"' "${msg//\"/\\\"}")"
  printf '{"error":true,"exit_code":%s,"message":%s}\n' "${code}" "${encoded}" >&2
  exit "${code}"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    die_json 1 "required command not found: $1"
  fi
}

# --- 解析 args --------------------------------------------------------------
# 只吃 --dry-run；其餘原樣轉傳給 gws
parse_args() {
  if [[ $# -eq 0 ]]; then
    die_json 1 "usage: gws-wrap.sh [--dry-run] <subcommand> <args...>"
  fi
  if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=1
    shift
  fi
  if [[ $# -eq 0 ]]; then
    die_json 1 "missing <subcommand> after --dry-run"
  fi
  # 把剩餘 args 回寫到 GWS_ARGS 全域
  GWS_ARGS=("$@")
}

# --- pre-flight：env-guard + credential-check -------------------------------
preflight() {
  # issue #119：若 env.sh 存在就 source（靜默；不將任何 secret echo 到 stdout）
  # ASVS V13：secrets 由 shell environment 注入，不記 log
  if [[ -f "${GWS_ENV_FILE}" ]]; then
    # shellcheck disable=SC1090
    source "${GWS_ENV_FILE}"
  fi

  # env-guard check：檢測 #119 是否需 workaround 但未套用
  # 注意：check 不會 apply，只報告
  if [[ -x "${ENV_GUARD}" ]]; then
    local guard_out guard_exit
    guard_out="$("${ENV_GUARD}" check 2>/dev/null || true)"
    guard_exit=0
    "${ENV_GUARD}" check >/dev/null 2>&1 || guard_exit=$?
    if (( guard_exit == 16 )); then
      die_json 16 "issue #119 workaround required; run google-slides-setup to apply"
    fi
    # 其他非 0 不致命（check 本身問題不阻斷；但 log to stderr）
    if (( guard_exit != 0 )); then
      printf '[gws-wrap] env-guard check returned %d; continuing\n' "${guard_exit}" >&2
    fi
  fi

  # credential-check：若 Keychain 不可用 → exit 18 由 builder 處理 fallback
  if [[ -x "${CRED_CHECK}" ]]; then
    local cred_exit=0
    "${CRED_CHECK}" >/dev/null 2>&1 || cred_exit=$?
    if (( cred_exit == 18 )); then
      die_json 10 "credential backend unavailable; run: gws auth"
    fi
  fi

  # 檢查 gws binary 存在
  if [[ ! -x "${GWS}" ]]; then
    die_json 1 "gws binary not found at ${GWS}; run bootstrap.sh first"
  fi
}

# --- 把 gws raw exit 映射成 TECH-SPEC exit code ------------------------------
# gws 的 stderr 可能含 "401"/"403"/"429"/"quota"/"invalid_scope" 等關鍵詞
map_gws_error() {
  local raw_exit="$1"
  local stderr_file="$2"
  local err_text=""
  [[ -f "${stderr_file}" ]] && err_text="$(cat "${stderr_file}")"

  # 順序：優先 invalid_scope（#119）→ auth → quota → 其他
  if printf '%s' "${err_text}" | grep -qiE 'invalid_scope|invalid_client'; then
    return 16
  fi
  if printf '%s' "${err_text}" | grep -qiE '\b401\b|\b403\b|unauthenticated|token.*expired|invalid_grant'; then
    return 10
  fi
  if printf '%s' "${err_text}" | grep -qiE 'quota|quotaExceeded|userRateLimitExceeded'; then
    return 11
  fi
  # 無法分類 → generic API error
  return 12
}

# --- 偵測是否為 429（可重試）------------------------------------------------
is_retryable() {
  local stderr_file="$1"
  [[ -f "${stderr_file}" ]] || return 1
  grep -qiE '\b429\b|rateLimitExceeded|backendError|\b5[0-9]{2}\b' "${stderr_file}"
}

# --- 執行 gws 一次 ----------------------------------------------------------
# 回傳：主 function 的 exit code 保持為 gws 的 raw exit；stdout/stderr 寫到檔
run_gws_once() {
  local stdout_f="$1"
  local stderr_f="$2"

  # stdin passthrough：直接用 </dev/stdin 不可靠，用 caller 層的 `cat`
  # passthrough。此 script 透過 fd 0 接；若 caller 無 stdin，bash 會給 /dev/null。
  set +e
  "${GWS}" "${GWS_ARGS[@]}" >"${stdout_f}" 2>"${stderr_f}"
  local rc=$?
  set -e
  return "${rc}"
}

# --- 指數退避 retry loop -----------------------------------------------------
# 5s → 10s → 20s，最多 MAX_ATTEMPTS 次
invoke_with_retry() {
  local attempt=0
  local delay="${RETRY_BASE_SEC}"
  local stdout_f="${TMP}/gws.stdout"
  local stderr_f="${TMP}/gws.stderr"

  while (( attempt < MAX_ATTEMPTS )); do
    attempt=$(( attempt + 1 ))
    local rc=0
    run_gws_once "${stdout_f}" "${stderr_f}" || rc=$?

    if (( rc == 0 )); then
      # passthrough stdout；stderr 視為 progress
      cat "${stdout_f}"
      [[ -s "${stderr_f}" ]] && cat "${stderr_f}" >&2 || true
      return 0
    fi

    if is_retryable "${stderr_f}" && (( attempt < MAX_ATTEMPTS )); then
      printf '[gws-wrap] attempt %d/%d got retryable error; sleeping %ds\n' \
        "${attempt}" "${MAX_ATTEMPTS}" "${delay}" >&2
      sleep "${delay}"
      delay=$(( delay * 2 ))
      continue
    fi

    # 不可重試或耗盡次數 → 映射 exit code
    local mapped=0
    map_gws_error "${rc}" "${stderr_f}" || mapped=$?
    # stderr 先 passthrough（不含 secret；gws 本身不 echo credential）
    [[ -s "${stderr_f}" ]] && cat "${stderr_f}" >&2 || true
    # 若為可重試但已耗盡 → 11
    if is_retryable "${stderr_f}"; then
      die_json 11 "rate limit exhausted after ${MAX_ATTEMPTS} attempts"
    fi
    die_json "${mapped}" "gws error (raw_exit=${rc})"
  done
}

# --- dry-run：只印即將執行的命令 ---------------------------------------------
emit_dry_run() {
  # 用 jq 做 safe JSON encoding（ASVS V1）
  local args_json
  args_json="$(printf '%s\n' "${GWS_ARGS[@]}" | jq -R -s 'split("\n") | map(select(length > 0))')"
  jq -n \
    --arg bin "${GWS}" \
    --argjson args "${args_json}" \
    '{dry_run: true, command: $bin, args: $args}'
}

# --- main -------------------------------------------------------------------
main() {
  require_cmd jq
  require_cmd curl  # gws 內部可能用；pre-flight 也有
  parse_args "$@"

  if (( DRY_RUN == 1 )); then
    # dry-run 仍做 pre-flight（讓 #119 問題能被早期 surface）
    preflight
    emit_dry_run
    exit 0
  fi

  preflight
  invoke_with_retry
}

main "$@"
