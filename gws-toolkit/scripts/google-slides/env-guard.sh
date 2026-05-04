#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# env-guard.sh — gws issue #119 detection + workaround apply (ISP split)
# -----------------------------------------------------------------------------
# Two subcommands with separate responsibilities (Interface Segregation):
#   - `check`: Detect whether the issue #119 workaround is needed (missing
#     GOOGLE_WORKSPACE_CLI_CLIENT_ID / CLIENT_SECRET env vars, or gws auth
#     returning invalid_scope / invalid_client). Emits JSON
#     `{"workaround_needed": bool, "reason": "..."}`. Exits 16 when the
#     workaround is needed but not applied; exits 0 otherwise.
#   - `apply`: Read client ID / secret from
#     `~/.config/gws/client_secret.json` and emit shell-eval lines (KISS:
#     the caller's env is not mutated directly — the caller must `eval` or
#     `source` the output, avoiding side-effect leakage).
#
# ISP (TECH-SPEC §6.1): the setup caller runs check + apply; the builder
# caller only runs check — different subcommands, different responsibilities.
#
# Upstream refs:
#   - TECH-SPEC §4.2 `scripts/google-slides/env-guard.sh` contract
#   - TECH-SPEC §6.1 gws issue #119 workaround
#   - TECH-SPEC §8.1 settings.json deny rule (credential-at-rest guard)
#
# Args:
#   check              Detect whether the workaround is needed.
#   apply              Emit `export ...` shell lines for the caller to eval.
#                      The only plaintext secret appears on stdout (the
#                      export lines themselves); the stderr progress log is
#                      masked to "***".
#
# Stdin:  none
# Stdout: JSON (check) or shell-eval lines (apply; no plaintext log).
# Stderr: human-readable messages, no plaintext secrets.
#
# Exit codes (per TECH-SPEC §4.2):
#   0   success / workaround not required
#   1   generic error (usage / client_secret.json not found)
#   16  workaround required but not applied (check subcommand)
# =============================================================================

export LC_ALL="${LC_ALL:-en_US.UTF-8}"

readonly GWS_CONFIG_DIR="${HOME}/.config/gws"
readonly CLIENT_SECRET_FILE="${GWS_CONFIG_DIR}/client_secret.json"
readonly ENV_FILE="${GWS_CONFIG_DIR}/env.sh"
readonly BIN_DIR="${BIN_DIR:-${HOME}/.cache/slides-toolkit/bin}"
readonly GWS="${BIN_DIR}/gws"

TMP="$(mktemp -d -t env-guard.XXXXXX)"
trap 'rm -rf "${TMP}"' EXIT

# --- helper：safe JSON error to stderr + exit -------------------------------
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

# --- 輸出 check JSON（ASVS V1 output encoding）------------------------------
emit_check() {
  local needed="$1"  # "true" | "false"
  local reason="$2"
  jq -n \
    --argjson needed "${needed}" \
    --arg reason "${reason}" \
    '{workaround_needed: $needed, reason: $reason}'
}

# --- subcommand: check ------------------------------------------------------
# 邏輯：
#   1. 若 GOOGLE_WORKSPACE_CLI_CLIENT_ID / CLIENT_SECRET 已 set（非空）
#      → 無需 workaround（env 已注入）。
#   2. 若 env var 缺但 env.sh 存在（user 已跑過 apply）→ 視為不需 re-apply
#      （builder 會自己 source）。
#   3. 否則跑一次 `gws auth status`（lightweight ping），stderr 若含
#      invalid_scope / invalid_client → 需 workaround → exit 16。
#   4. 若 gws 不存在（尚未 bootstrap）→ 無從判斷；保守回 false（讓 setup
#      流程先跑 bootstrap）。
cmd_check() {
  # case 1: env 已注入
  if [[ -n "${GOOGLE_WORKSPACE_CLI_CLIENT_ID:-}" && -n "${GOOGLE_WORKSPACE_CLI_CLIENT_SECRET:-}" ]]; then
    emit_check "false" "env vars already set"
    exit 0
  fi

  # case 2: env.sh 存在（可 lazy load）
  if [[ -f "${ENV_FILE}" ]]; then
    emit_check "false" "env.sh present; caller should source before calling gws"
    exit 0
  fi

  # case 4: gws 尚未 bootstrap
  if [[ ! -x "${GWS}" ]]; then
    emit_check "false" "gws binary not present; run bootstrap.sh first"
    exit 0
  fi

  # case 3: 跑一次 dry auth ping（gws auth status 為 lightweight）
  local auth_stderr="${TMP}/auth.stderr"
  set +e
  "${GWS}" auth status >/dev/null 2>"${auth_stderr}"
  local rc=$?
  set -e

  if (( rc == 0 )); then
    emit_check "false" "gws auth status OK"
    exit 0
  fi

  if grep -qiE 'invalid_scope|invalid_client' "${auth_stderr}"; then
    emit_check "true" "gws returned invalid_scope / invalid_client (issue #119)"
    # exit 16：需 workaround 但未套用
    exit 16
  fi

  # 其他 auth 錯誤不是 #119；不在本 script 責任範圍（ISP）
  emit_check "false" "gws auth error is not #119-related; see stderr"
  exit 0
}

# --- subcommand: apply ------------------------------------------------------
# 讀 ~/.config/gws/client_secret.json（標準 GCP OAuth Client 下載檔格式：
#   { "installed": { "client_id": "...", "client_secret": "..." } }
# 或 { "web": {...} }），印出 export 指令到 stdout 供 caller eval。
# **安全**：
#   - 不 echo 明文 secret 到 stderr（progress 只印 "applied" 不含值）
#   - 不修改 user env 直接（KISS：caller 控制 scope）
cmd_apply() {
  if [[ ! -f "${CLIENT_SECRET_FILE}" ]]; then
    die_json 1 "client_secret.json not found at ${CLIENT_SECRET_FILE}; download from GCP Console first"
  fi

  # 檢查檔案權限（ASVS V14 secrets-at-rest）
  local perms
  perms="$(stat -f '%Lp' "${CLIENT_SECRET_FILE}" 2>/dev/null || printf '000')"
  if [[ "${perms}" != "600" ]]; then
    printf '[env-guard] warning: %s perms=%s; recommend chmod 600\n' \
      "${CLIENT_SECRET_FILE}" "${perms}" >&2
  fi

  # 解析 client_id / client_secret（兼容 "installed" / "web" 兩種）
  local cid csec
  cid="$(jq -r '(.installed // .web // {}) | .client_id // empty' "${CLIENT_SECRET_FILE}")"
  csec="$(jq -r '(.installed // .web // {}) | .client_secret // empty' "${CLIENT_SECRET_FILE}")"

  if [[ -z "${cid}" || -z "${csec}" ]]; then
    die_json 1 "client_id or client_secret missing in ${CLIENT_SECRET_FILE}"
  fi

  # 印出 shell-eval 指令到 stdout（caller: `eval "$(env-guard.sh apply)"`）
  # 注意：此為 stdout 唯一會出現 secret 的地方；caller 應在受控 scope 內 eval
  # 而不 pipe 到 log。progress 訊息（stderr）只印 "applied"，masked。
  # 值用 printf %q 做 shell-quote（防 injection；ASVS V1）。
  printf 'export GOOGLE_WORKSPACE_CLI_CLIENT_ID=%q\n' "${cid}"
  printf 'export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=%q\n' "${csec}"

  # stderr：只印 masked log（ASVS V13 secrets-not-logged / V16 log hygiene）
  printf '[env-guard] applied GOOGLE_WORKSPACE_CLI_CLIENT_ID=*** CLIENT_SECRET=***\n' >&2
}

# --- main -------------------------------------------------------------------
main() {
  require_cmd jq
  if [[ $# -eq 0 ]]; then
    die_json 1 "usage: env-guard.sh {check|apply}"
  fi
  case "$1" in
    check) shift; cmd_check "$@" ;;
    apply) shift; cmd_apply "$@" ;;
    -h|--help)
      cat <<'USAGE' >&2
Usage: env-guard.sh {check|apply}
  check    Detect whether issue #119 workaround is needed; exit 16 if yes
  apply    Emit `export ...` shell lines for caller to `eval` (no mutation)
USAGE
      exit 0
      ;;
    *) die_json 1 "unknown subcommand: $1 (expected: check|apply)" ;;
  esac
}

main "$@"
