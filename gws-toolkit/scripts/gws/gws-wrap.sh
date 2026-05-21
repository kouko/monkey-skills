#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# gws-wrap.sh — gws CLI wrapper with pre-flight + 429 backoff
# -----------------------------------------------------------------------------
# Before each gws invocation, the wrapper runs env-guard (BYO-client
# env-var pre-flight check, no apply) and credential-check (token
# validity and backend detection), then retries 429 / 5xx errors with
# exponential
# backoff. Structured errors are parsed and mapped to the TECH-SPEC §4.2
# exit-code table.
#
# Upstream refs:
#   - TECH-SPEC §3.4 slides-builder
#   - TECH-SPEC §4.2 `scripts/gws/gws-wrap.sh` contract
#   - TECH-SPEC §4.3 gws CLI recipe mapping
#   - TECH-SPEC §6.4 Rate-limit (429) exponential-backoff implementation
#
# Args:
#   --dry-run                Do not call gws; print the command + args that
#                            would run.
#   <subcommand> <args...>   Forwarded verbatim to gws
#                            (e.g. `slides presentations batchUpdate ...`).
#
# Stdin: raw JSON (if the subcommand needs it) — passed through to gws.
# Stdout: gws response JSON, passed through unchanged.
# Stderr: human-readable progress + structured error JSON on failure.
#
# Exit codes (per TECH-SPEC §4.2):
#   0   success
#   1   generic error (usage / pre-flight)
#   10  token expired / unauthenticated (401/403)
#   11  rate limit exhausted after retry (429 × 5)
#   12  Google resource not found / API error
#   16  BYO-client env vars missing (env-guard check failed; historical
#       name "issue #119 workaround")
#
# Default: `BIN_DIR=${HOME}/.cache/gws-toolkit/bin` (populated by
# bootstrap.sh).
# =============================================================================

export LC_ALL="${LC_ALL:-en_US.UTF-8}"

# --- 常數 -------------------------------------------------------------------
readonly BIN_DIR="${BIN_DIR:-${HOME}/.cache/gws-toolkit/bin}"
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

# --- pre-flight report（dry-run 專用；collect status，不 exit on issue） ----
# Stdout: 結構化 pre-flight 狀態 JSON
preflight_report() {
  local issue_119="false"
  local cred_backend="unknown"
  local cred_token_valid="false"
  local gws_present="false"

  if [[ -f "${GWS_ENV_FILE}" ]]; then
    # shellcheck disable=SC1090
    source "${GWS_ENV_FILE}"
  fi

  if [[ -x "${ENV_GUARD}" ]]; then
    local guard_exit=0
    "${ENV_GUARD}" check >/dev/null 2>&1 || guard_exit=$?
    if (( guard_exit == 16 )); then
      issue_119="true"
    fi
  fi

  if [[ -x "${CRED_CHECK}" ]]; then
    local cred_out
    cred_out="$("${CRED_CHECK}" 2>/dev/null || true)"
    if [[ -n "${cred_out}" ]]; then
      cred_backend="$(printf '%s' "${cred_out}" | jq -r '.backend // "unknown"' 2>/dev/null || printf 'unknown')"
      cred_token_valid="$(printf '%s' "${cred_out}" | jq -r '.token_valid // false' 2>/dev/null || printf 'false')"
    fi
  fi

  [[ -x "${GWS}" ]] && gws_present="true"

  jq -n \
    --argjson issue_119 "${issue_119}" \
    --arg cred_backend "${cred_backend}" \
    --argjson cred_valid "${cred_token_valid}" \
    --argjson gws_present "${gws_present}" \
    '{issue_119_workaround_needed: $issue_119, credential_backend: $cred_backend, token_valid: $cred_valid, gws_binary_present: $gws_present}'
}

# --- pre-flight（real-run 專用；exit on blocking issue） --------------------
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
      die_json 16 "issue #119 workaround required; run gws-setup to apply"
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

# --- dry-run：印將執行命令 + pre-flight 狀態（不 enforce）---------------------
# 契約：dry-run 永遠 exit 0（只要 args 合法）；pre-flight 問題以狀態欄位回報，
# 不 block dry-run。真正執行才由 preflight() enforce。
emit_dry_run() {
  local args_json preflight_json
  args_json="$(printf '%s\n' "${GWS_ARGS[@]}" | jq -R -s 'split("\n") | map(select(length > 0))')"
  preflight_json="$(preflight_report)"
  jq -n \
    --arg bin "${GWS}" \
    --argjson args "${args_json}" \
    --argjson preflight "${preflight_json}" \
    '{dry_run: true, command: $bin, args: $args, preflight: $preflight}'
}

# --- main -------------------------------------------------------------------
main() {
  require_cmd jq
  require_cmd curl  # gws 內部可能用；pre-flight 也有
  parse_args "$@"

  if (( DRY_RUN == 1 )); then
    # dry-run：emit_dry_run 內部會做 preflight_report（non-enforcing）
    emit_dry_run
    exit 0
  fi

  preflight
  invoke_with_retry
}

main "$@"
