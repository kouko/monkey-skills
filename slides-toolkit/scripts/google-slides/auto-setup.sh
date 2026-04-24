#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# auto-setup.sh — slides-toolkit 端到端 GCP/OAuth 自動化 setup
# -----------------------------------------------------------------------------
# 用途：
#   把 live E2E 驗證過的 Google Slides backend 自動化 bootstrap codify 成
#   idempotent script。涵蓋：
#     1. gcloud CLI 偵測 / 安裝（brew cask 或官方 installer）
#     2. gcloud auth login（已登入則 skip）
#     3. GCP project 建立 + Slides/Drive API enable
#     4. 印出 Console 手動步驟 URL（OAuth consent / Audience / Clients）並
#        `open` 瀏覽器；等使用者下載 client_secret_*.json 到 ~/Downloads
#     5. 搬 JSON → ~/.config/gws/client_secret.json（chmod 600）+ 寫 env.sh
#     6. `gws auth login --scopes=presentations,drive.file`（正確 scope 語法）
#     7. 驗證 `gws auth status` 為 oauth2
#
#   Idempotent：每個 function 偵測當前 state；已完成則 skip + stderr 印
#   "already done"。--force-reinstall 可強制重跑 auth step。
#
# 設計原則：
#   - 「自動化可以可靠自動化的部分」：UI 操作（Console 點按鈕 / add test user
#     / download JSON）由使用者完成；script 只開瀏覽器 + 等檔案出現
#   - 不跑 smoke test（建 test deck）於主流程，避免產生垃圾資源
#   - 全部動態偵測 gmail 帳號，不 hardcode
#   - Secrets ASVS V14：client_secret.json / env.sh 均 chmod 600，0700 dir
#
# Upstream refs:
#   - TECH-SPEC v0.3 §4.2 Exit code table
#   - TECH-SPEC §4.8 Credential flow（ASVS V14 secrets-at-rest）
#   - TECH-SPEC §7.3 Dry-run 模式
#
# Args:
#   --dry-run                 只印計畫，不執行任何 gcloud/gws 命令或檔案操作
#   --force-reinstall         即使 gws 已 authed，仍重跑 gws auth login
#   -h|--help                 印使用說明
#
# Env:
#   SLIDES_TOOLKIT_PROJECT_ID  optional；預設 slides-toolkit-<YYMMDD>
#
# Stdin: none
# Stdout: JSON
#   {"status":"success","project_id":"...","account":"...",
#    "scopes":["presentations","drive.file"],"elapsed_sec":N}
# Stderr: 人讀 `[auto-setup] step N/7: ...` progress + 結構化 error JSON
#
# Exit codes (per TECH-SPEC v0.3 §4.2)：
#   0   success
#   1   generic error（usage / platform / unknown state）
#   10  auth error（gcloud/gws login 失敗；使用者拒絕授權；timeout 等 JSON）
#   12  API error（enable services / create project 失敗）
# =============================================================================

# --- UTF-8 locale ---
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

# --- 常數 -------------------------------------------------------------------
readonly GWS_CONFIG_DIR="${HOME}/.config/gws"
readonly CLIENT_SECRET_DEST="${GWS_CONFIG_DIR}/client_secret.json"
readonly ENV_FILE="${GWS_CONFIG_DIR}/env.sh"
readonly DOWNLOADS_DIR="${HOME}/Downloads"
readonly CACHE_BIN_DIR="${HOME}/.cache/slides-toolkit/bin"
readonly SLIDES_SCOPE="https://www.googleapis.com/auth/presentations"
readonly DRIVE_SCOPE="https://www.googleapis.com/auth/drive.file"

# 等待 client_secret JSON 出現的 timeout（秒）與輪詢週期
readonly WAIT_CLIENT_SECRET_TIMEOUT_SEC=600
readonly WAIT_CLIENT_SECRET_INTERVAL_SEC=5
# 視為「剛下載」的 mtime 新鮮度門檻（秒）
readonly CLIENT_SECRET_FRESHNESS_SEC=300

# --- 旗標 -------------------------------------------------------------------
DRY_RUN=0
FORCE_REINSTALL=0

# 內部 state（由 detect / ensure functions 填入，供 emit_result 使用）
PROJECT_ID=""
ACCOUNT=""
START_EPOCH=0

# --- helper：結構化 error 輸出後 exit ----------------------------------------
# Errors out-of-band 原則：error JSON 走 stderr，非 stdout（stdout 保留成功
# contract）。
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
  command -v "$1" >/dev/null 2>&1 \
    || die_json 1 "required command not found: $1"
}

# 印 step progress header（stderr）
step() {
  local n="$1"
  local total="$2"
  shift 2
  printf '[auto-setup] step %s/%s: %s\n' "${n}" "${total}" "$*" >&2
}

# 印 dry-run 計畫（stderr）—— 模擬一條命令
dry_echo() {
  printf '[auto-setup] [dry-run] would run: %s\n' "$*" >&2
}

# --- 解析 args --------------------------------------------------------------
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run)          DRY_RUN=1; shift ;;
      --force-reinstall)  FORCE_REINSTALL=1; shift ;;
      -h|--help)
        cat <<'USAGE' >&2
Usage: auto-setup.sh [--dry-run] [--force-reinstall]

Env:
  SLIDES_TOOLKIT_PROJECT_ID    GCP project id（預設 slides-toolkit-<YYMMDD>）

Exit codes:
  0  success
  1  generic error
  10 auth error
  12 API error
USAGE
        exit 0
        ;;
      *)
        die_json 1 "unknown arg: $1"
        ;;
    esac
  done
}

# --- platform 偵測（MVP: macOS-only；與 bootstrap.sh 一致） -----------------
detect_platform() {
  local os
  os="$(uname -s)"
  if [[ "${os}" != "Darwin" ]]; then
    die_json 1 "unsupported OS: ${os} (MVP supports macOS only)"
  fi
}

# --- step 1：偵測 + 安裝 gcloud ---------------------------------------------
# 若 PATH 已有 gcloud → skip；否則優先 brew cask；再退到官方 installer。
# 安裝完印 `gcloud --version` 驗證。
ensure_gcloud() {
  if command -v gcloud >/dev/null 2>&1; then
    step 1 7 "gcloud already installed, skip"
    return
  fi

  step 1 7 "gcloud not found; install via brew or official installer"

  if (( DRY_RUN == 1 )); then
    dry_echo 'brew install --cask google-cloud-sdk  # if brew exists'
    dry_echo 'curl https://sdk.cloud.google.com | bash --disable-prompts --install-dir=$HOME  # fallback'
    return
  fi

  if command -v brew >/dev/null 2>&1; then
    if ! brew install --cask google-cloud-sdk; then
      die_json 1 "brew install google-cloud-sdk failed"
    fi
  else
    # 官方 installer：--disable-prompts 非互動，--install-dir 放在 $HOME
    if ! curl -fsSL https://sdk.cloud.google.com \
        | bash -s -- --disable-prompts --install-dir="${HOME}"; then
      die_json 1 "official gcloud installer failed"
    fi
    # 把 bin 加進目前 shell PATH（使用者需自行加到 rc）
    export PATH="${HOME}/google-cloud-sdk/bin:${PATH}"
  fi

  if ! command -v gcloud >/dev/null 2>&1; then
    die_json 1 "gcloud still not in PATH after install"
  fi
  gcloud --version >&2 || die_json 1 "gcloud --version failed post-install"
}

# --- step 2：gcloud auth login ---------------------------------------------
# 偵測 active account；無則跑 `gcloud auth login --quiet`（會開瀏覽器）。
# 偵測到的 account 填入全域 ACCOUNT 供最終 JSON 用。
ensure_gcloud_auth() {
  local active
  active="$(gcloud auth list \
    --filter=status:ACTIVE \
    --format='value(account)' 2>/dev/null || printf '')"

  if [[ -n "${active}" ]]; then
    ACCOUNT="${active}"
    step 2 7 "gcloud already authed as ${ACCOUNT}, skip"
    return
  fi

  step 2 7 "gcloud auth login (will open browser)"

  if (( DRY_RUN == 1 )); then
    dry_echo 'gcloud auth login --quiet'
    ACCOUNT="<dry-run-account>"
    return
  fi

  if ! gcloud auth login --quiet; then
    die_json 10 "gcloud auth login failed"
  fi

  ACCOUNT="$(gcloud auth list \
    --filter=status:ACTIVE \
    --format='value(account)' 2>/dev/null || printf '')"
  [[ -n "${ACCOUNT}" ]] \
    || die_json 10 "no active account after gcloud auth login"
}

# --- step 3a：決定 project id -----------------------------------------------
# 優先 env SLIDES_TOOLKIT_PROJECT_ID；否則產 slides-toolkit-<YYMMDD>
resolve_project_id() {
  if [[ -n "${SLIDES_TOOLKIT_PROJECT_ID:-}" ]]; then
    PROJECT_ID="${SLIDES_TOOLKIT_PROJECT_ID}"
  else
    PROJECT_ID="slides-toolkit-$(date +%y%m%d)"
  fi
}

# --- step 3b：建 GCP project（已存在則 skip） -------------------------------
# `gcloud projects describe` 成功 → 存在；否則 `projects create`。
# 最後 `gcloud config set project`。
ensure_project() {
  step 3 7 "ensure project ${PROJECT_ID}"

  if (( DRY_RUN == 1 )); then
    dry_echo "gcloud projects describe ${PROJECT_ID} || gcloud projects create ${PROJECT_ID} --name=slides-toolkit"
    dry_echo "gcloud config set project ${PROJECT_ID}"
    return
  fi

  if gcloud projects describe "${PROJECT_ID}" >/dev/null 2>&1; then
    printf '[auto-setup] project %s already exists, skip create\n' \
      "${PROJECT_ID}" >&2
  else
    if ! gcloud projects create "${PROJECT_ID}" --name="slides-toolkit"; then
      die_json 12 "gcloud projects create failed for ${PROJECT_ID}"
    fi
  fi

  if ! gcloud config set project "${PROJECT_ID}" >/dev/null 2>&1; then
    die_json 12 "gcloud config set project failed"
  fi
}

# --- step 4：enable Slides + Drive APIs -------------------------------------
# `gcloud services list --enabled` 比對；兩者已在 → skip。
ensure_apis() {
  step 4 7 "enable slides + drive APIs on ${PROJECT_ID}"

  if (( DRY_RUN == 1 )); then
    dry_echo "gcloud services enable slides.googleapis.com drive.googleapis.com --project=${PROJECT_ID}"
    return
  fi

  local enabled
  enabled="$(gcloud services list \
    --enabled \
    --project="${PROJECT_ID}" \
    --format='value(config.name)' 2>/dev/null || printf '')"

  if printf '%s\n' "${enabled}" | grep -q '^slides\.googleapis\.com$' \
     && printf '%s\n' "${enabled}" | grep -q '^drive\.googleapis\.com$'; then
    printf '[auto-setup] APIs already enabled, skip\n' >&2
    return
  fi

  if ! gcloud services enable \
      slides.googleapis.com \
      drive.googleapis.com \
      --project="${PROJECT_ID}"; then
    die_json 12 "gcloud services enable failed"
  fi
}

# --- step 5a：印 Console 手動步驟 URL 並 `open` -----------------------------
# UI 操作（OAuth consent / Audience test user / Clients create）不可靠自動化；
# script 僅提供最短 navigation path：依序開 3 個 URL。
open_console_urls() {
  step 5 7 "open Console URLs for manual OAuth consent + test user + OAuth client"

  local consent_url audience_url clients_url
  consent_url="https://console.cloud.google.com/auth/overview?project=${PROJECT_ID}"
  audience_url="https://console.cloud.google.com/auth/audience?project=${PROJECT_ID}"
  clients_url="https://console.cloud.google.com/auth/clients?project=${PROJECT_ID}"

  printf '[auto-setup]   1) Consent screen: %s\n'   "${consent_url}" >&2
  printf '[auto-setup]   2) Add test users: %s\n'   "${audience_url}" >&2
  printf '[auto-setup]   3) Create OAuth client: %s\n' "${clients_url}" >&2
  printf '[auto-setup]   → After creating Desktop OAuth client, download JSON to %s\n' \
    "${DOWNLOADS_DIR}" >&2

  if (( DRY_RUN == 1 )); then
    dry_echo "open ${consent_url}"
    dry_echo "open ${audience_url}"
    dry_echo "open ${clients_url}"
    return
  fi

  # `open` 失敗不致命（SSH / headless 環境使用者可複製 URL）
  open "${consent_url}"  >/dev/null 2>&1 || true
  open "${audience_url}" >/dev/null 2>&1 || true
  open "${clients_url}"  >/dev/null 2>&1 || true
}

# --- step 5b：輪詢 ~/Downloads/client_secret_*.json -------------------------
# 條件：檔案存在 **且** mtime 在 CLIENT_SECRET_FRESHNESS_SEC 秒內 → 視為
# 剛下載的新檔（避免挑到舊檔）。Timeout 10 min → exit 10。
wait_for_client_secret() {
  if [[ -f "${CLIENT_SECRET_DEST}" ]] && (( FORCE_REINSTALL == 0 )); then
    printf '[auto-setup] %s already installed, skip wait\n' \
      "${CLIENT_SECRET_DEST}" >&2
    return
  fi

  printf '[auto-setup] waiting for client_secret_*.json in %s (timeout %ds)...\n' \
    "${DOWNLOADS_DIR}" "${WAIT_CLIENT_SECRET_TIMEOUT_SEC}" >&2

  if (( DRY_RUN == 1 )); then
    dry_echo "poll ${DOWNLOADS_DIR}/client_secret_*.json (mtime < ${CLIENT_SECRET_FRESHNESS_SEC}s old)"
    return
  fi

  local deadline now candidate mtime age_sec
  deadline=$(( $(date +%s) + WAIT_CLIENT_SECRET_TIMEOUT_SEC ))

  while :; do
    now=$(date +%s)
    if (( now > deadline )); then
      die_json 10 "timeout waiting for client_secret_*.json in ${DOWNLOADS_DIR}"
    fi

    # ls -t 依 mtime 新→舊；挑最新一個候選
    candidate="$(ls -t "${DOWNLOADS_DIR}"/client_secret_*.json 2>/dev/null \
      | head -1 || printf '')"
    if [[ -n "${candidate}" && -f "${candidate}" ]]; then
      mtime="$(stat -f '%m' "${candidate}" 2>/dev/null || printf '0')"
      age_sec=$(( now - mtime ))
      if (( age_sec <= CLIENT_SECRET_FRESHNESS_SEC )); then
        printf '[auto-setup] found fresh %s (age %ds)\n' \
          "${candidate}" "${age_sec}" >&2
        return
      fi
    fi

    sleep "${WAIT_CLIENT_SECRET_INTERVAL_SEC}"
  done
}

# --- step 6：搬 JSON + chmod + 寫 env.sh ------------------------------------
# ASVS V14：secrets-at-rest 一律 0600，parent dir 0700。
# 讀 client_id / client_secret 用 jq（優先 .installed.*；fallback .web.*）。
install_credentials() {
  step 6 7 "install client_secret.json + write env.sh"

  if [[ -f "${CLIENT_SECRET_DEST}" ]] \
     && [[ -f "${ENV_FILE}" ]] \
     && (( FORCE_REINSTALL == 0 )); then
    printf '[auto-setup] credentials already installed, skip\n' >&2
    return
  fi

  if (( DRY_RUN == 1 )); then
    dry_echo "mv ~/Downloads/client_secret_*.json ${CLIENT_SECRET_DEST}"
    dry_echo "chmod 700 ${GWS_CONFIG_DIR} && chmod 600 ${CLIENT_SECRET_DEST}"
    dry_echo "write ${ENV_FILE} with GOOGLE_WORKSPACE_CLI_CLIENT_{ID,SECRET} (chmod 600)"
    return
  fi

  local src
  src="$(ls -t "${DOWNLOADS_DIR}"/client_secret_*.json 2>/dev/null \
    | head -1 || printf '')"
  [[ -n "${src}" && -f "${src}" ]] \
    || die_json 1 "no client_secret_*.json found in ${DOWNLOADS_DIR}"

  mkdir -p "${GWS_CONFIG_DIR}"
  chmod 700 "${GWS_CONFIG_DIR}"

  mv "${src}" "${CLIENT_SECRET_DEST}"
  chmod 600 "${CLIENT_SECRET_DEST}"

  # jq：優先系統 jq；否則 cache bin 的 jq（bootstrap.sh 管安裝）
  local jq_bin
  jq_bin="$(command -v jq || printf '%s/jq' "${CACHE_BIN_DIR}")"
  [[ -x "${jq_bin}" ]] \
    || die_json 1 "jq not found (expected system jq or ${CACHE_BIN_DIR}/jq)"

  local client_id client_secret
  client_id="$("${jq_bin}" -r \
    '.installed.client_id // .web.client_id // ""' \
    "${CLIENT_SECRET_DEST}")"
  client_secret="$("${jq_bin}" -r \
    '.installed.client_secret // .web.client_secret // ""' \
    "${CLIENT_SECRET_DEST}")"

  [[ -n "${client_id}" ]]     || die_json 1 "client_id missing in ${CLIENT_SECRET_DEST}"
  [[ -n "${client_secret}" ]] || die_json 1 "client_secret missing in ${CLIENT_SECRET_DEST}"

  # env.sh：用 single-quote heredoc 避免 shell 展開 client_secret 的
  # 特殊字符（ASVS V1 encoding）。先寫到 .tmp，chmod 後 rename（atomic）。
  local tmp_env="${ENV_FILE}.tmp"
  {
    printf '#!/usr/bin/env bash\n'
    printf "export GOOGLE_WORKSPACE_CLI_CLIENT_ID='%s'\n"     "${client_id}"
    printf "export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET='%s'\n" "${client_secret}"
  } > "${tmp_env}"
  chmod 600 "${tmp_env}"
  mv "${tmp_env}" "${ENV_FILE}"

  printf '[auto-setup] wrote %s (chmod 600)\n' "${ENV_FILE}" >&2
}

# --- step 7a：gws auth login（正確 --scopes=URL,URL 語法） -----------------
# 實測：gws 的 `-s` 是 service filter，不是 scope；要用 `--scopes=<URL>,<URL>`
# --force-reinstall 時強制重跑，否則 gws auth status 已 oauth2 → skip。
ensure_gws_auth() {
  step 7 7 "gws auth login with slides + drive.file scopes"

  local gws_bin
  gws_bin="$(command -v gws || printf '%s/gws' "${CACHE_BIN_DIR}")"
  [[ -x "${gws_bin}" ]] \
    || die_json 1 "gws binary not found (expected system gws or ${CACHE_BIN_DIR}/gws); run bootstrap.sh first"

  # 已 authed 偵測：status 含 oauth2 → skip（除非 --force-reinstall）
  if (( FORCE_REINSTALL == 0 )); then
    if "${gws_bin}" auth status 2>/dev/null \
        | grep -qE 'auth_method:[[:space:]]*oauth2'; then
      printf '[auto-setup] gws already authed (oauth2), skip\n' >&2
      return
    fi
  fi

  if (( DRY_RUN == 1 )); then
    dry_echo "source ${ENV_FILE}"
    dry_echo "${gws_bin} auth login --scopes=${SLIDES_SCOPE},${DRIVE_SCOPE}"
    return
  fi

  # 載入 env.sh 到 subshell 再跑 gws，避免污染主 script 環境
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  export GOOGLE_WORKSPACE_CLI_CLIENT_ID GOOGLE_WORKSPACE_CLI_CLIENT_SECRET

  if ! "${gws_bin}" auth login \
      --scopes="${SLIDES_SCOPE},${DRIVE_SCOPE}"; then
    die_json 10 "gws auth login failed"
  fi
}

# --- step 7b：驗證 gws auth status -----------------------------------------
# 失敗 exit 10（auth）— 不是 generic 1，讓 caller 能區分 retry 策略。
verify() {
  if (( DRY_RUN == 1 )); then
    dry_echo "gws auth status | grep 'auth_method: oauth2'"
    return
  fi

  local gws_bin
  gws_bin="$(command -v gws || printf '%s/gws' "${CACHE_BIN_DIR}")"

  if ! "${gws_bin}" auth status 2>/dev/null \
      | grep -qE 'auth_method:[[:space:]]*oauth2'; then
    die_json 10 "gws auth status did not report oauth2"
  fi
  printf '[auto-setup] verify OK: gws auth_method=oauth2\n' >&2
}

# --- 最終成功 JSON（stdout contract） ---------------------------------------
emit_result() {
  local elapsed
  elapsed=$(( $(date +%s) - START_EPOCH ))

  # 若 dry-run 且 ACCOUNT 為 placeholder，用 "<dry-run>" 表示
  local account_out="${ACCOUNT}"
  [[ -z "${account_out}" ]] && account_out="<unknown>"

  jq -n \
    --arg status "success" \
    --arg project_id "${PROJECT_ID}" \
    --arg account "${account_out}" \
    --argjson elapsed "${elapsed}" \
    --argjson dry_run "$([[ ${DRY_RUN} -eq 1 ]] && printf 'true' || printf 'false')" \
    '{
       status: $status,
       project_id: $project_id,
       account: $account,
       scopes: ["presentations", "drive.file"],
       elapsed_sec: $elapsed,
       dry_run: $dry_run
     }'
}

# --- main -------------------------------------------------------------------
# Step-down rule (Clean Code Ch.3)：main 只做 top-level flow；每個 ensure_*
# function 自己處理 idempotence + dry-run + 錯誤分類。
main() {
  parse_args "$@"
  require_cmd jq
  require_cmd curl
  require_cmd date
  require_cmd uname
  require_cmd stat

  detect_platform
  START_EPOCH="$(date +%s)"

  printf '[auto-setup] dry_run=%d force_reinstall=%d\n' \
    "${DRY_RUN}" "${FORCE_REINSTALL}" >&2

  ensure_gcloud                  # step 1
  ensure_gcloud_auth             # step 2
  resolve_project_id
  ensure_project                 # step 3
  ensure_apis                    # step 4
  open_console_urls              # step 5a
  wait_for_client_secret         # step 5b
  install_credentials            # step 6
  ensure_gws_auth                # step 7a
  verify                         # step 7b

  emit_result
}

main "$@"
