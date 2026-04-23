#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# bootstrap.sh — slides-toolkit google-slides backend binary bootstrapper
# -----------------------------------------------------------------------------
# 用途：
#   偵測 macOS 平台 → 從 GitHub release 下載 pin 過的 gws / jq binary 到
#   ~/.cache/slides-toolkit/bin/ → SHA-256 verify → chmod +x → 寫 .version。
#   Idempotent：若 .version 已匹配則跳過（除非 --force）。
#
# Upstream refs:
#   - TECH-SPEC §2.3 Binary distribution strategy
#   - TECH-SPEC §4.2 `scripts/google-slides/bootstrap.sh` contract
#   - TECH-SPEC §7.3 Dry-run 模式
#   - TECH-SPEC §8.6 ASVS V13 supply-chain integrity
#
# Args:
#   --force                         忽略 .version 比對，強制重下載
#   --dry-run                       只 fetch + SHA-256 check，不寫 cache dir
#   --platform <darwin-arm64|darwin-x86_64>
#                                   override auto-detect (CI / 跨機器測試用)
#
# Stdin: none
# Stdout: JSON `{"gws":"<path>","jq":"<path>","version":{"gws":"...","jq":"..."},"cache_dir":"..."}`
# Stderr: 人讀 progress（含錯誤 JSON on failure）
#
# Exit codes (per TECH-SPEC §4.2)：
#   0  success
#   1  generic error（unknown platform / network / usage）
#   17 SHA-256 mismatch on binary fetch
# =============================================================================

# --- UTF-8 locale（§8.5；best-effort，若系統無此 locale 則保持預設） ---
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

# --- 版本 pin（TODO: 首次 C3 commit 時 fill actual latest stable） ------------
# NOTE: 以下常數於發 release 前由維護者更新；目前為 placeholder。
# gws：googleworkspace/cli release tag (e.g. "v0.1.0")
GWS_VERSION="${GWS_VERSION:-v0.0.0-TODO}"
JQ_VERSION="${JQ_VERSION:-jq-1.7.1}"

# SHA-256 pin（TODO: 首次 C3 commit 時填入實際 shasum；以下為 placeholder）
# 來源：`shasum -a 256` 對下載的 release binary 跑一次後貼入。
GWS_SHA256_DARWIN_ARM64="${GWS_SHA256_DARWIN_ARM64:-TODO_FILL_REAL_SHA256_64HEX}"
GWS_SHA256_DARWIN_X86_64="${GWS_SHA256_DARWIN_X86_64:-TODO_FILL_REAL_SHA256_64HEX}"
JQ_SHA256_DARWIN_ARM64="${JQ_SHA256_DARWIN_ARM64:-TODO_FILL_REAL_SHA256_64HEX}"
JQ_SHA256_DARWIN_X86_64="${JQ_SHA256_DARWIN_X86_64:-TODO_FILL_REAL_SHA256_64HEX}"

# --- 常數 -------------------------------------------------------------------
readonly CACHE_DIR="${HOME}/.cache/slides-toolkit/bin"
readonly VERSION_FILE="${CACHE_DIR}/.version"
readonly GWS_RELEASE_BASE="https://github.com/googleworkspace/cli/releases/download"
readonly JQ_RELEASE_BASE="https://github.com/jqlang/jq/releases/download"

# --- 臨時目錄 + 清理 trap ---------------------------------------------------
TMP="$(mktemp -d -t slides-toolkit-bootstrap.XXXXXX)"
trap 'rm -rf "${TMP}"' EXIT

# --- 旗標 -------------------------------------------------------------------
FORCE=0
DRY_RUN=0
PLATFORM_OVERRIDE=""

# --- helper：stderr 印 JSON error 後 exit ------------------------------------
# 所有對 stderr 的 JSON 使用者資料皆過 jq -R（ASVS V1 output encoding）。
die_json() {
  local code="$1"
  local msg="$2"
  # jq -R 把任意字串安全編碼為 JSON string
  local encoded_msg
  encoded_msg="$(printf '%s' "${msg}" | jq -R -s '.' 2>/dev/null || printf '"%s"' "${msg//\"/\\\"}")"
  printf '{"error":true,"exit_code":%s,"message":%s}\n' "${code}" "${encoded_msg}" >&2
  exit "${code}"
}

# --- helper：check 相依命令 --------------------------------------------------
require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    # 注意：在 jq 尚未 bootstrap 之前，die_json 可能無 jq；fallback 純文字
    printf '{"error":true,"exit_code":1,"message":"required command not found: %s"}\n' "${cmd}" >&2
    exit 1
  fi
}

# --- 解析 args（do-one-thing；SOLID SRP） ------------------------------------
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --force)     FORCE=1; shift ;;
      --dry-run)   DRY_RUN=1; shift ;;
      --platform)
        [[ $# -ge 2 ]] || die_json 1 "--platform requires a value"
        PLATFORM_OVERRIDE="$2"
        shift 2
        ;;
      -h|--help)
        cat <<'USAGE' >&2
Usage: bootstrap.sh [--force] [--dry-run] [--platform darwin-arm64|darwin-x86_64]
USAGE
        exit 0
        ;;
      *)
        die_json 1 "unknown arg: $1"
        ;;
    esac
  done
}

# --- 偵測平台 ---------------------------------------------------------------
detect_platform() {
  if [[ -n "${PLATFORM_OVERRIDE}" ]]; then
    printf '%s' "${PLATFORM_OVERRIDE}"
    return
  fi
  local os arch
  os="$(uname -s)"
  arch="$(uname -m)"
  if [[ "${os}" != "Darwin" ]]; then
    die_json 1 "unsupported OS: ${os} (MVP supports macOS only)"
  fi
  case "${arch}" in
    arm64)         printf 'darwin-arm64' ;;
    x86_64)        printf 'darwin-x86_64' ;;
    *)             die_json 1 "unsupported arch: ${arch}" ;;
  esac
}

# --- 取得 expected SHA-256 -------------------------------------------------
# 用 case 映射，避免 eval。
expected_sha_for() {
  local tool="$1"
  local platform="$2"
  case "${tool}:${platform}" in
    gws:darwin-arm64)  printf '%s' "${GWS_SHA256_DARWIN_ARM64}" ;;
    gws:darwin-x86_64) printf '%s' "${GWS_SHA256_DARWIN_X86_64}" ;;
    jq:darwin-arm64)   printf '%s' "${JQ_SHA256_DARWIN_ARM64}" ;;
    jq:darwin-x86_64)  printf '%s' "${JQ_SHA256_DARWIN_X86_64}" ;;
    *)                 die_json 1 "no SHA pin for ${tool}:${platform}" ;;
  esac
}

# --- 構造 download URL ------------------------------------------------------
url_for() {
  local tool="$1"
  local platform="$2"
  case "${tool}" in
    gws)
      # e.g. https://github.com/googleworkspace/cli/releases/download/v0.1.0/gws-darwin-arm64
      printf '%s/%s/gws-%s' "${GWS_RELEASE_BASE}" "${GWS_VERSION}" "${platform}"
      ;;
    jq)
      # jq 的 macOS release artifact 命名（1.7.1 起）：jq-macos-arm64 / jq-macos-amd64
      # 為避免 drift，這裡用 platform 作 naming pivot；實際 artifact 名稱在
      # C3 commit 時由維護者校對（TODO）。
      local jq_suffix
      case "${platform}" in
        darwin-arm64)  jq_suffix="macos-arm64" ;;
        darwin-x86_64) jq_suffix="macos-amd64" ;;
        *)             die_json 1 "no jq artifact for ${platform}" ;;
      esac
      printf '%s/%s/jq-%s' "${JQ_RELEASE_BASE}" "${JQ_VERSION}" "${jq_suffix}"
      ;;
    *)
      die_json 1 "unknown tool: ${tool}"
      ;;
  esac
}

# --- SHA-256 verify（security-critical；TECH-SPEC §7.1） ---------------------
verify_sha256() {
  local file="$1"
  local expected="$2"
  local actual
  actual="$(shasum -a 256 "${file}" | awk '{print $1}')"
  if [[ "${actual}" != "${expected}" ]]; then
    # 清理可能的暫檔由 trap 處理
    die_json 17 "SHA-256 mismatch for ${file}: expected=${expected} actual=${actual}"
  fi
}

# --- 下載 + 驗 + 安裝單一 binary --------------------------------------------
install_one() {
  local tool="$1"
  local platform="$2"
  local url expected tmp_file dest
  url="$(url_for "${tool}" "${platform}")"
  expected="$(expected_sha_for "${tool}" "${platform}")"
  tmp_file="${TMP}/${tool}"
  dest="${CACHE_DIR}/${tool}"

  printf '[bootstrap] fetching %s from %s\n' "${tool}" "${url}" >&2

  # curl: -f fail on HTTP error, -L follow redirect, -S show err on silent,
  # -s silent progress, -o output file
  if ! curl -fLSs -o "${tmp_file}" "${url}"; then
    die_json 1 "download failed: ${url}"
  fi

  verify_sha256 "${tmp_file}" "${expected}"

  if (( DRY_RUN == 1 )); then
    printf '[bootstrap] --dry-run: SHA OK for %s; not installing\n' "${tool}" >&2
    return
  fi

  mkdir -p "${CACHE_DIR}"
  mv "${tmp_file}" "${dest}"
  chmod +x "${dest}"
  printf '[bootstrap] installed %s → %s\n' "${tool}" "${dest}" >&2
}

# --- idempotence check：比對 .version 看是否需重下載 -------------------------
# 回傳 0 = 需重下載；1 = 可 skip
needs_install() {
  (( FORCE == 1 )) && return 0
  [[ -f "${VERSION_FILE}" ]] || return 0
  [[ -x "${CACHE_DIR}/gws" ]] || return 0
  [[ -x "${CACHE_DIR}/jq" ]]  || return 0

  # 讀 .version，比對 pinned 版本
  local cached_gws cached_jq
  cached_gws="$(jq -r '.gws // ""' "${VERSION_FILE}" 2>/dev/null || printf '')"
  cached_jq="$(jq -r '.jq // ""'  "${VERSION_FILE}" 2>/dev/null || printf '')"
  if [[ "${cached_gws}" == "${GWS_VERSION}" && "${cached_jq}" == "${JQ_VERSION}" ]]; then
    return 1
  fi
  return 0
}

# --- 寫 .version file（版本 metadata；非 secret） ----------------------------
write_version_file() {
  (( DRY_RUN == 1 )) && return
  # 用 jq 產生 JSON（ASVS V1 encoding）
  jq -n \
    --arg gws "${GWS_VERSION}" \
    --arg jq_v "${JQ_VERSION}" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{gws: $gws, jq: $jq_v, written_at: $ts}' \
    > "${VERSION_FILE}"
}

# --- 印最終 stdout JSON ------------------------------------------------------
emit_result() {
  local gws_path jq_path
  gws_path="${CACHE_DIR}/gws"
  jq_path="${CACHE_DIR}/jq"
  jq -n \
    --arg gws "${gws_path}" \
    --arg jqp "${jq_path}" \
    --arg gws_v "${GWS_VERSION}" \
    --arg jq_v "${JQ_VERSION}" \
    --arg cache "${CACHE_DIR}" \
    --argjson dry_run "$([[ ${DRY_RUN} -eq 1 ]] && printf 'true' || printf 'false')" \
    '{gws: $gws, jq: $jqp, version: {gws: $gws_v, jq: $jq_v}, cache_dir: $cache, dry_run: $dry_run}'
}

# --- main -------------------------------------------------------------------
main() {
  parse_args "$@"
  # curl + shasum + jq + awk 為必備；jq 第一次 bootstrap 時可能還沒裝，
  # 但我們要求使用者系統已有 jq（jq 本身也是 bootstrap target；此 contract
  # 允許 system-wide jq 先存在用於 JSON encoding，稍後會把 pinned jq 放入
  # cache）。這是 step-down rule 的 main 層次：僅檢查先決條件。
  require_cmd curl
  require_cmd shasum
  require_cmd awk
  require_cmd uname
  require_cmd jq  # system-wide jq 供 bootstrap 自身用；pinned jq 供下游 script 用

  local platform
  platform="$(detect_platform)"
  printf '[bootstrap] platform=%s force=%d dry_run=%d\n' "${platform}" "${FORCE}" "${DRY_RUN}" >&2

  if needs_install; then
    install_one "gws" "${platform}"
    install_one "jq"  "${platform}"
    write_version_file
  else
    printf '[bootstrap] cache hit: %s already at pinned versions; skip\n' "${CACHE_DIR}" >&2
  fi

  emit_result
}

main "$@"
