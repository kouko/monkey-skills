#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# auto-setup.sh — slides-toolkit end-to-end GCP / OAuth setup automation
# -----------------------------------------------------------------------------
# Codifies the live-E2E-verified Google Slides backend bootstrap as an
# idempotent script. Steps:
#   1. Detect / install gcloud CLI (brew cask or the official installer).
#   2. gcloud auth login (skipped if already signed in).
#   3. Create the GCP project and enable the 4 Workspace APIs (Slides +
#      Drive + Docs + Sheets) — must match the OAuth scope set requested
#      in step 8 below.
#   4. Guide through 3 sub-steps (5a Branding → 5b Test User → 5c OAuth
#      Client). Each opens a single Console URL, prints inline
#      instructions, waits for the user's ENTER (read from /dev/tty so
#      Claude background invocations still prompt the human directly).
#      5c additionally polls ~/Downloads/ for the client_secret_*.json
#      and validates it is a Desktop app (rejects Web app early — the
#      most common silent footgun).
#   5. Move the JSON to ~/.config/gws/client_secret.json (chmod 600) and
#      write env.sh.
#   6. (handled jointly with 5 — install credentials + env.sh).
#   7. Bootstrap the gws + jq binaries via bootstrap.sh
#      (`~/.cache/slides-toolkit/bin/`).
#   8. `gws auth login --scopes=presentations,drive,documents,spreadsheets`
#      (4 scopes covering Slides + Drive + Docs + Sheets API operations
#      surfaced by the 5 vendored upstream skills; correct scope syntax —
#      `--scopes=` with full URLs, not `-s`). Verify `gws auth status`
#      reports oauth2.
#
# Idempotent: each function probes the current state and skips with an
# "already done" stderr line when the step is complete. --force-reinstall
# forces the auth step to re-run.
#
# Design principles:
#   - Automate what can be reliably automated. UI actions (clicking in the
#     Console, adding a test user, downloading the JSON) remain manual;
#     the script only opens the browser and waits for the file to appear.
#   - The main flow does not run a smoke test (no test-deck creation) to
#     avoid leaving stray resources behind.
#   - The Gmail account is detected dynamically — never hardcoded.
#   - Secrets (ASVS V14): client_secret.json and env.sh are chmod 600,
#     inside a 0700 directory.
#
# Upstream refs:
#   - TECH-SPEC v0.3 §4.2 Exit code table
#   - TECH-SPEC §4.8 Credential flow (ASVS V14 secrets-at-rest)
#   - TECH-SPEC §7.3 Dry-run mode
#
# Args:
#   --dry-run                 Print the plan only; no gcloud/gws commands
#                             or filesystem changes.
#   --force-reinstall         Re-run gws auth login even if gws is already
#                             authed.
#   -h|--help                 Print usage.
#
# Env:
#   SLIDES_TOOLKIT_PROJECT_ID  Optional; defaults to slides-toolkit-<YYMMDD>.
#
# Stdin: none
# Stdout: JSON
#   {"status":"success","project_id":"...","account":"...",
#    "scopes":["presentations","drive","documents","spreadsheets"],
#    "elapsed_sec":N}
# Stderr: human-readable `[auto-setup] step N/7: ...` progress +
#         structured error JSON on failure.
#
# Exit codes (per TECH-SPEC v0.3 §4.2):
#   0   success
#   1   generic error (usage / platform / unknown state)
#   10  auth error (gcloud/gws login failed; user declined consent;
#       timeout; etc.)
#   12  API error (enable services / create project failed)
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
readonly DRIVE_SCOPE="https://www.googleapis.com/auth/drive"
readonly DOCS_SCOPE="https://www.googleapis.com/auth/documents"
readonly SHEETS_SCOPE="https://www.googleapis.com/auth/spreadsheets"

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
  SLIDES_TOOLKIT_PROJECT_ID    GCP project id (default: slides-toolkit-<YYMMDD>)

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
    step 1 8 "gcloud already installed, skip"
    return
  fi

  step 1 8 "gcloud not found; install via brew or official installer"

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
    step 2 8 "gcloud already authed as ${ACCOUNT}, skip"
    return
  fi

  step 2 8 "gcloud auth login (will open browser)"

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
  step 3 8 "ensure project ${PROJECT_ID}"

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

# --- step 4：enable Slides + Drive + Docs + Sheets APIs ---------------------
# `gcloud services list --enabled` 比對；4 個全在 → skip。Workspace API
# enablement is independent of OAuth scope grant — both gates must pass for
# any API call to succeed (see PRODUCT-SPEC v1.0 §6.3).
ensure_apis() {
  step 4 8 "enable slides + drive + docs + sheets APIs on ${PROJECT_ID}"

  if (( DRY_RUN == 1 )); then
    dry_echo "gcloud services enable slides.googleapis.com drive.googleapis.com docs.googleapis.com sheets.googleapis.com --project=${PROJECT_ID}"
    return
  fi

  local enabled
  enabled="$(gcloud services list \
    --enabled \
    --project="${PROJECT_ID}" \
    --format='value(config.name)' 2>/dev/null || printf '')"

  if printf '%s\n' "${enabled}" | grep -q '^slides\.googleapis\.com$' \
     && printf '%s\n' "${enabled}" | grep -q '^drive\.googleapis\.com$' \
     && printf '%s\n' "${enabled}" | grep -q '^docs\.googleapis\.com$' \
     && printf '%s\n' "${enabled}" | grep -q '^sheets\.googleapis\.com$'; then
    printf '[auto-setup] APIs already enabled, skip\n' >&2
    return
  fi

  if ! gcloud services enable \
      slides.googleapis.com \
      drive.googleapis.com \
      docs.googleapis.com \
      sheets.googleapis.com \
      --project="${PROJECT_ID}"; then
    die_json 12 "gcloud services enable failed"
  fi
}

# --- step 5：guided 3 sub-steps（5a Branding / 5b Test User / 5c OAuth Client）
# UI 操作（OAuth consent / Audience test user / Clients create）不可自動化；
# 改成 sub-step 引導 + 每步 wait-for-confirm + 5c 對下載 JSON 做 Desktop-app
# shape 驗證攔早期錯誤（避免使用者誤建 Web client 在 step 8 才 401）。
#
# 互動模式：always 從 /dev/tty 讀按鍵，所以 Claude Bash 背景跑也能 prompt。
# 真 headless（無 /dev/tty）→ fallback 一次性開 3 URL + 純 poll。
# /dev/tty existence-check via [[ -r ]] is unreliable on macOS — the file
# exists but the device isn't "configured" when no controlling terminal
# is attached. Detect by actually attempting to open it.
have_working_tty() {
  if [[ -r /dev/tty && -w /dev/tty ]]; then
    if (printf '' >/dev/tty) 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

prompt_continue() {
  local message="$1"
  if have_working_tty; then
    printf '\n%s\n→ Press ENTER when done (or Ctrl-C to abort): ' "${message}" >/dev/tty 2>/dev/null
    read -r _ </dev/tty 2>/dev/null || true
  else
    printf '[auto-setup] (no /dev/tty; proceeding without prompt) %s\n' "${message}" >&2
  fi
}

step_5a_branding() {
  step 5 8 "5a — OAuth Consent Screen / Branding"
  local url="https://console.cloud.google.com/auth/overview?project=${PROJECT_ID}"

  cat >&2 <<EOF

  📋 5a — Branding
     URL: ${url}

     In the browser:
       1. Open the "Branding" tab (default landing)
       2. Fill:
          • App name (e.g. "gws-toolkit")
          • User support email = your Gmail
          • Developer contact = your Gmail
       3. Click Save → wait for "saved" confirmation
EOF
  if (( DRY_RUN == 1 )); then
    dry_echo "open ${url}"
    return
  fi
  open "${url}" >/dev/null 2>&1 || true
  prompt_continue "Done with 5a (Branding saved)?"
}

step_5b_test_user() {
  step 5 8 "5b — Test User"
  local url="https://console.cloud.google.com/auth/audience?project=${PROJECT_ID}"

  cat >&2 <<EOF

  📋 5b — Audience / Test User
     URL: ${url}

     In the browser:
       1. Scroll to "Test users" section
       2. Click "+ ADD USERS"
       3. Enter your Gmail (${ACCOUNT:-your@gmail.com})
       4. Click Save
       5. Confirm the email appears in the Test users list

     ⚠ Skipping this = step 8 fails with 403 access_denied.
EOF
  if (( DRY_RUN == 1 )); then
    dry_echo "open ${url}"
    return
  fi
  open "${url}" >/dev/null 2>&1 || true
  prompt_continue "Done with 5b (Test User added & saved)?"
}

step_5c_oauth_client() {
  step 5 8 "5c — OAuth Client (Desktop app) + Download"
  local url="https://console.cloud.google.com/auth/clients?project=${PROJECT_ID}"

  cat >&2 <<EOF

  📋 5c — OAuth Client
     URL: ${url}

     In the browser:
       1. Click "+ CREATE CLIENT"
       2. Application type = "Desktop app"
          ⚠ NOT "Web application" — Desktop is required for the
          localhost callback gws uses. Picking Web silently breaks
          step 8.
       3. Name (e.g. "gws-toolkit-cli")
       4. Click Create
       5. Click DOWNLOAD JSON
       6. Save to ${DOWNLOADS_DIR}/  (keep default filename)

     Polling ${DOWNLOADS_DIR}/ for fresh client_secret_*.json
     (timeout ${WAIT_CLIENT_SECRET_TIMEOUT_SEC}s)...
EOF
  if (( DRY_RUN == 1 )); then
    dry_echo "open ${url}"
    dry_echo "poll ${DOWNLOADS_DIR}/client_secret_*.json"
    return
  fi
  open "${url}" >/dev/null 2>&1 || true

  # 既有 install 已就位 → skip
  if [[ -f "${CLIENT_SECRET_DEST}" ]] && (( FORCE_REINSTALL == 0 )); then
    printf '[auto-setup] %s already installed, skip wait\n' "${CLIENT_SECRET_DEST}" >&2
    return
  fi

  # Poll + Desktop-app shape validation
  local jq_bin
  jq_bin="$(command -v jq || printf '%s/jq' "${CACHE_BIN_DIR}")"
  [[ -x "${jq_bin}" ]] \
    || die_json 1 "jq not found (expected system jq or ${CACHE_BIN_DIR}/jq); cannot validate downloaded client_secret"

  local deadline now candidate mtime age_sec
  deadline=$(( $(date +%s) + WAIT_CLIENT_SECRET_TIMEOUT_SEC ))

  while :; do
    now=$(date +%s)
    if (( now > deadline )); then
      die_json 10 "timeout waiting for client_secret_*.json in ${DOWNLOADS_DIR}"
    fi

    candidate="$(ls -t "${DOWNLOADS_DIR}"/client_secret_*.json 2>/dev/null \
      | head -1 || printf '')"
    if [[ -n "${candidate}" && -f "${candidate}" ]]; then
      mtime="$(stat -f '%m' "${candidate}" 2>/dev/null || printf '0')"
      age_sec=$(( now - mtime ))
      if (( age_sec <= CLIENT_SECRET_FRESHNESS_SEC )); then
        # Validate Desktop app shape (.installed.client_id present)
        if "${jq_bin}" -e '.installed.client_id // empty | length > 0' "${candidate}" >/dev/null 2>&1; then
          printf '[auto-setup] found fresh Desktop OAuth client: %s (age %ds)\n' \
            "${candidate}" "${age_sec}" >&2
          return
        fi
        # Web app instead — actionable error
        if "${jq_bin}" -e '.web.client_id // empty | length > 0' "${candidate}" >/dev/null 2>&1; then
          printf '\n[auto-setup] ⚠ %s is a Web OAuth client, not Desktop.\n' "${candidate}" >&2
          printf '[auto-setup]   gws requires Desktop app type for the localhost callback.\n' >&2
          printf '[auto-setup]   Re-run 5c: delete this Web client + create a Desktop one.\n' >&2
          die_json 1 "downloaded client_secret has .web.* (Web app) — must be Desktop app"
        fi
        printf '[auto-setup] ⚠ %s has neither .installed nor .web sections; format unknown\n' "${candidate}" >&2
        die_json 1 "client_secret JSON shape unrecognised"
      fi
    fi

    sleep "${WAIT_CLIENT_SECRET_INTERVAL_SEC}"
  done
}

# --- step 6：搬 JSON + chmod + 寫 env.sh ------------------------------------
# ASVS V14：secrets-at-rest 一律 0600，parent dir 0700。
# 讀 client_id / client_secret 用 jq（優先 .installed.*；fallback .web.*）。
install_credentials() {
  step 6 8 "install client_secret.json + write env.sh"

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

# --- step 7：bootstrap gws + jq binaries -----------------------------------
# Idempotent — bootstrap.sh detects cached binary + TTL itself; this wrapper
# only handles dry-run and absolute-path resolution.
ensure_binaries() {
  step 7 8 "bootstrap gws + jq binaries"

  local bootstrap="${SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}/bootstrap.sh"
  [[ -x "${bootstrap}" ]] \
    || die_json 1 "bootstrap.sh not executable at ${bootstrap}"

  if (( DRY_RUN == 1 )); then
    dry_echo "bash ${bootstrap}"
    return
  fi

  if ! bash "${bootstrap}" >/dev/null; then
    die_json 1 "bootstrap.sh failed"
  fi
  printf '[auto-setup] gws + jq binaries installed under ~/.cache/slides-toolkit/bin/\n' >&2
}

# --- step 8a：gws auth login（正確 --scopes=URL,URL 語法） -----------------
# 實測：gws 的 `-s` 是 service filter，不是 scope；要用 `--scopes=<URL>,<URL>`
# --force-reinstall 時強制重跑，否則 gws auth status 已 oauth2 → skip。
ensure_gws_auth() {
  step 8 8 "gws auth login with presentations + drive + documents + spreadsheets scopes"

  local gws_bin
  gws_bin="$(command -v gws || printf '%s/gws' "${CACHE_BIN_DIR}")"
  [[ -x "${gws_bin}" ]] \
    || die_json 1 "gws binary not found (expected system gws or ${CACHE_BIN_DIR}/gws); run bootstrap.sh first"

  # 已 authed 偵測：status 的 JSON 中 .auth_method == "oauth2" → skip
  # （除非 --force-reinstall）
  # gws v0.22.5 起 `auth status` 輸出為 JSON（含 1-2 行 stderr-style header
  # 在 stdout），用 sed 截 JSON 部分後 jq parse。
  if (( FORCE_REINSTALL == 0 )); then
    local jq_bin
    jq_bin="$(command -v jq || printf '%s/jq' "${CACHE_BIN_DIR}")"
    if [[ -x "${jq_bin}" ]] && "${gws_bin}" auth status 2>/dev/null \
        | sed -n '/^{/,$p' \
        | "${jq_bin}" -er '.auth_method == "oauth2"' >/dev/null 2>&1; then
      printf '[auto-setup] gws already authed (oauth2), skip\n' >&2
      return
    fi
  fi

  if (( DRY_RUN == 1 )); then
    dry_echo "source ${ENV_FILE}"
    dry_echo "${gws_bin} auth login --scopes=${SLIDES_SCOPE},${DRIVE_SCOPE},${DOCS_SCOPE},${SHEETS_SCOPE}"
    return
  fi

  # 載入 env.sh 到 subshell 再跑 gws，避免污染主 script 環境
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  export GOOGLE_WORKSPACE_CLI_CLIENT_ID GOOGLE_WORKSPACE_CLI_CLIENT_SECRET

  if ! "${gws_bin}" auth login \
      --scopes="${SLIDES_SCOPE},${DRIVE_SCOPE},${DOCS_SCOPE},${SHEETS_SCOPE}"; then
    die_json 10 "gws auth login failed"
  fi
}

# --- step 8b：驗證 gws auth status -----------------------------------------
# 失敗 exit 10（auth）— 不是 generic 1，讓 caller 能區分 retry 策略。
# gws v0.22.5 `auth status` 輸出 JSON（前面可能有 1-2 行 "Using keyring..."
# header 跑到 stdout），用 sed 截 JSON 部分後 jq parse `.auth_method`。
verify() {
  if (( DRY_RUN == 1 )); then
    dry_echo 'gws auth status | sed -n "/^{/,$p" | jq -e ".auth_method == \"oauth2\""'
    return
  fi

  local gws_bin jq_bin
  gws_bin="$(command -v gws || printf '%s/gws' "${CACHE_BIN_DIR}")"
  jq_bin="$(command -v jq || printf '%s/jq' "${CACHE_BIN_DIR}")"
  [[ -x "${jq_bin}" ]] || die_json 1 "jq not found (expected system jq or ${CACHE_BIN_DIR}/jq)"

  if ! "${gws_bin}" auth status 2>/dev/null \
      | sed -n '/^{/,$p' \
      | "${jq_bin}" -er '.auth_method == "oauth2"' >/dev/null 2>&1; then
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
       scopes: ["presentations", "drive", "documents", "spreadsheets"],
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
  step_5a_branding               # step 5a
  step_5b_test_user              # step 5b
  step_5c_oauth_client           # step 5c
  install_credentials            # step 6
  ensure_binaries                # step 7
  ensure_gws_auth                # step 8a
  verify                         # step 8b

  emit_result
}

main "$@"
