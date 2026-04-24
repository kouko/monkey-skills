#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# bootstrap.sh — slides-toolkit google-slides backend binary bootstrapper
# -----------------------------------------------------------------------------
# 用途：
#   偵測 macOS 平台 → 從 GitHub release 以 HTTPS + `curl -fLSs` 下載
#   gws / jq binary 到 ~/.cache/slides-toolkit/bin/ → chmod +x → 寫 .version。
#   Idempotent：binary 存在且未超過 TTL 則 skip（除非 --force）。
#   Auto-refresh：若 .version 的 installed_at 超過 TTL（預設 30 天），自
#   動重抓 latest；失敗則保留 cached binary 並 exit 0（不阻斷日常使用）。
#
# v0.3.1: latest-URL resolution + auto-refresh after TTL
#   - URL 改用 GitHub /releases/latest/download/ redirect（零 version pin）
#   - `.version` 多記 installed_at + resolved tag（透過 GitHub API）
#   - `GWS_VERSION` env 可 override 停用 auto-refresh（stability pin）
#
# v0.3: SHA-256 verification removed; see TECH-SPEC v0.3 §2.3 for
#       HTTPS-only integrity model.
#
# Upstream refs:
#   - TECH-SPEC v0.3 §2.3 Binary distribution strategy
#   - TECH-SPEC v0.3 §4.2 `scripts/google-slides/bootstrap.sh` contract
#   - TECH-SPEC §7.3 Dry-run 模式
#
# Args:
#   --force                         忽略 cache + TTL，強制重下載
#   --dry-run                       只印計畫，不連網、不寫 cache dir
#   --platform <darwin-arm64|darwin-x86_64>
#                                   override auto-detect (CI / 跨機器測試用)
#
# Env:
#   GWS_VERSION                     pin 某 tag（e.g. v0.23.0）→ 停用 auto-refresh
#   JQ_VERSION                      pin jq version（預設 jq-1.7.1）
#   SLIDES_TOOLKIT_BINARY_TTL_DAYS  auto-refresh 門檻（預設 30）
#
# Stdin: none
# Stdout: JSON `{"gws":"<path>","jq":"<path>","version":{"gws":"...","jq":"..."},"cache_dir":"...","dry_run":bool}`
# Stderr: 人讀 progress（含錯誤 JSON on failure）
#
# Exit codes (per TECH-SPEC v0.3 §4.2)：
#   0  success
#   1  generic error（unknown platform / network on initial install / usage）
#
# 注：auto-refresh 失敗不 die；保留 cached binary 並 exit 0（見 install_one）。
# =============================================================================

# --- UTF-8 locale（§8.5；best-effort，若系統無此 locale 則保持預設） ---
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

# --- 版本 pin / TTL --------------------------------------------------------
# 預設空字串 = auto-resolve latest；若使用者 export GWS_VERSION=v0.X.Y 則
# 停用 auto-refresh，固守該版。jq 預設 pin 1.7.1（jq release 極穩定，
# 不需 latest）。
GWS_VERSION="${GWS_VERSION:-}"
JQ_VERSION="${JQ_VERSION:-jq-1.7.1}"
TTL_DAYS="${SLIDES_TOOLKIT_BINARY_TTL_DAYS:-30}"

# --- 常數 -------------------------------------------------------------------
readonly CACHE_DIR="${HOME}/.cache/slides-toolkit/bin"
readonly VERSION_FILE="${CACHE_DIR}/.version"
readonly GWS_RELEASE_BASE="https://github.com/googleworkspace/cli/releases/download"
readonly GWS_LATEST_BASE="https://github.com/googleworkspace/cli/releases/latest/download"
readonly GWS_API_LATEST="https://api.github.com/repos/googleworkspace/cli/releases/latest"
readonly JQ_RELEASE_BASE="https://github.com/jqlang/jq/releases/download"

# --- 臨時目錄 + 清理 trap ---------------------------------------------------
TMP="$(mktemp -d -t slides-toolkit-bootstrap.XXXXXX)"
trap 'rm -rf "${TMP}"' EXIT

# --- 旗標 -------------------------------------------------------------------
FORCE=0
DRY_RUN=0
PLATFORM_OVERRIDE=""
# 是否為 auto-refresh（由 needs_install 推斷）— 影響 download 失敗語意
AUTO_REFRESH=0
# Resolved tag（auto-resolve 後填入；用於 .version 紀錄）
RESOLVED_GWS_TAG=""

# --- helper：stderr 印 JSON error 後 exit ------------------------------------
die_json() {
  local code="$1"
  local msg="$2"
  local encoded_msg
  encoded_msg="$(printf '%s' "${msg}" | jq -R -s '.' 2>/dev/null || printf '"%s"' "${msg//\"/\\\"}")"
  printf '{"error":true,"exit_code":%s,"message":%s}\n' "${code}" "${encoded_msg}" >&2
  exit "${code}"
}

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    printf '{"error":true,"exit_code":1,"message":"required command not found: %s"}\n' "${cmd}" >&2
    exit 1
  fi
}

# --- 解析 args --------------------------------------------------------------
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

Env:
  GWS_VERSION=v0.23.0                 pin a specific tag (disables auto-refresh)
  JQ_VERSION=jq-1.7.1                 pin jq version (default)
  SLIDES_TOOLKIT_BINARY_TTL_DAYS=30   auto-refresh threshold in days
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

# --- 從 GitHub API 解析 gws latest tag（best-effort；失敗則 fallback） ------
# 成功：印 tag（e.g. "v0.23.0"）到 stdout
# 失敗：印空字串，caller 視為無法 resolve
resolve_latest_gws_tag() {
  curl -sfL "${GWS_API_LATEST}" 2>/dev/null \
    | jq -r '.tag_name // ""' 2>/dev/null \
    || printf ''
}

# --- 構造 download URL ------------------------------------------------------
# gws：若 GWS_VERSION 有值 → 用 /releases/download/<tag>/；否則用 /releases/latest/download/
# jq ：用 JQ_VERSION pin
url_for() {
  local tool="$1"
  local platform="$2"
  case "${tool}" in
    gws)
      if [[ -n "${GWS_VERSION}" ]]; then
        printf '%s/%s/gws-%s' "${GWS_RELEASE_BASE}" "${GWS_VERSION}" "${platform}"
      else
        printf '%s/gws-%s' "${GWS_LATEST_BASE}" "${platform}"
      fi
      ;;
    jq)
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

# --- 下載 + 安裝單一 binary --------------------------------------------------
# Dry-run contract：完全不連網、不 curl、不寫磁碟
# Integrity model：HTTPS + `curl -f` + URL pin
# Auto-refresh 安全網：若 AUTO_REFRESH=1 且 download 失敗，保留既有 binary
#   並印 stderr warning（不 die），讓 skill 日常使用不被網路問題阻斷。
install_one() {
  local tool="$1"
  local platform="$2"
  local url tmp_file dest
  url="$(url_for "${tool}" "${platform}")"
  tmp_file="${TMP}/${tool}"
  dest="${CACHE_DIR}/${tool}"

  if (( DRY_RUN == 1 )); then
    printf '[bootstrap] --dry-run plan for %s:\n' "${tool}" >&2
    printf '              url: %s\n' "${url}" >&2
    printf '             dest: %s\n' "${dest}" >&2
    return
  fi

  printf '[bootstrap] fetching %s from %s\n' "${tool}" "${url}" >&2

  if ! curl -fLSs -o "${tmp_file}" "${url}"; then
    if (( AUTO_REFRESH == 1 )) && [[ -x "${dest}" ]]; then
      printf '[bootstrap] WARN: auto-refresh of %s failed (keeping existing binary at %s)\n' \
        "${tool}" "${dest}" >&2
      return
    fi
    die_json 1 "download failed: ${url}"
  fi

  mkdir -p "${CACHE_DIR}"
  mv "${tmp_file}" "${dest}"
  chmod +x "${dest}"
  printf '[bootstrap] installed %s → %s\n' "${tool}" "${dest}" >&2
}

# --- .version 判讀：計算 installed_at 距今幾天 -------------------------------
# 回傳整數到 stdout；若無法計算回 -1。macOS `date -j -f`；不支援 GNU 的
# `date -d`。
cached_age_days() {
  [[ -f "${VERSION_FILE}" ]] || { printf -- '-1'; return; }
  local installed_at
  installed_at="$(jq -r '.installed_at // ""' "${VERSION_FILE}" 2>/dev/null || printf '')"
  [[ -n "${installed_at}" ]] || { printf -- '-1'; return; }
  local installed_epoch now_epoch
  installed_epoch="$(date -j -u -f '%Y-%m-%dT%H:%M:%SZ' "${installed_at}" '+%s' 2>/dev/null || printf '0')"
  if [[ "${installed_epoch}" == "0" ]]; then
    printf -- '-1'; return
  fi
  now_epoch="$(date -u +%s)"
  printf '%d' $(( (now_epoch - installed_epoch) / 86400 ))
}

# --- idempotence check + TTL 自動更新 ---------------------------------------
# 回傳 0 = 需下載（初次 or auto-refresh）；1 = 可 skip。
# 若決定 auto-refresh（因 age > TTL），設 AUTO_REFRESH=1 讓 install_one
# 失敗時走安全網而非 die。
needs_install() {
  (( FORCE == 1 )) && return 0
  [[ -f "${VERSION_FILE}" ]] || return 0
  [[ -x "${CACHE_DIR}/gws" ]] || return 0
  [[ -x "${CACHE_DIR}/jq" ]]  || return 0

  # pin override：若 GWS_VERSION 明示設 env，比對 cached tag
  if [[ -n "${GWS_VERSION}" ]]; then
    local cached_gws
    cached_gws="$(jq -r '.gws_tag // .gws // ""' "${VERSION_FILE}" 2>/dev/null || printf '')"
    if [[ "${cached_gws}" != "${GWS_VERSION}" ]]; then
      return 0
    fi
    # Pin 模式：跳過 age check（使用者明示控版）
    return 1
  fi

  # Auto-refresh 模式：看 installed_at 年齡
  local age
  age="$(cached_age_days)"
  if [[ "${age}" -ge 0 && "${age}" -gt "${TTL_DAYS}" ]]; then
    printf '[bootstrap] cache age %d days > TTL %d; auto-refresh\n' \
      "${age}" "${TTL_DAYS}" >&2
    AUTO_REFRESH=1
    return 0
  fi
  return 1
}

# --- 寫 .version file（版本 metadata + installed_at） -----------------------
# 優先順序決定 gws_tag 欄位：
#   1. GWS_VERSION env（pin 模式）
#   2. RESOLVED_GWS_TAG（從 GitHub API 取到 tag）
#   3. 空字串 "unknown"（API 失敗但 download 成功）
write_version_file() {
  (( DRY_RUN == 1 )) && return
  local gws_tag source
  if [[ -n "${GWS_VERSION}" ]]; then
    gws_tag="${GWS_VERSION}"
    source="env-pinned"
  elif [[ -n "${RESOLVED_GWS_TAG}" ]]; then
    gws_tag="${RESOLVED_GWS_TAG}"
    source="auto-resolved"
  else
    gws_tag="unknown"
    source="auto-resolve-failed"
  fi
  jq -n \
    --arg gws "${gws_tag}" \
    --arg jq_v "${JQ_VERSION}" \
    --arg src "${source}" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{gws_tag: $gws, jq_tag: $jq_v, source: $src, installed_at: $ts}' \
    > "${VERSION_FILE}"
}

# --- 印最終 stdout JSON ------------------------------------------------------
emit_result() {
  local gws_path jq_path gws_display
  gws_path="${CACHE_DIR}/gws"
  jq_path="${CACHE_DIR}/jq"
  if [[ -n "${GWS_VERSION}" ]]; then
    gws_display="${GWS_VERSION}"
  elif [[ -n "${RESOLVED_GWS_TAG}" ]]; then
    gws_display="${RESOLVED_GWS_TAG}"
  else
    gws_display="latest"
  fi
  jq -n \
    --arg gws "${gws_path}" \
    --arg jqp "${jq_path}" \
    --arg gws_v "${gws_display}" \
    --arg jq_v "${JQ_VERSION}" \
    --arg cache "${CACHE_DIR}" \
    --argjson dry_run "$([[ ${DRY_RUN} -eq 1 ]] && printf 'true' || printf 'false')" \
    '{gws: $gws, jq: $jqp, version: {gws: $gws_v, jq: $jq_v}, cache_dir: $cache, dry_run: $dry_run}'
}

# --- main -------------------------------------------------------------------
main() {
  parse_args "$@"
  require_cmd curl
  require_cmd uname
  require_cmd date
  require_cmd jq

  local platform
  platform="$(detect_platform)"
  printf '[bootstrap] platform=%s force=%d dry_run=%d ttl_days=%d\n' \
    "${platform}" "${FORCE}" "${DRY_RUN}" "${TTL_DAYS}" >&2

  if needs_install; then
    # 若非 pin 模式（無 GWS_VERSION）且 non-dry-run，嘗試解析 latest tag
    # 供 .version 紀錄用；失敗不阻斷（URL 仍用 /latest/download/ redirect）。
    if [[ -z "${GWS_VERSION}" ]] && (( DRY_RUN == 0 )); then
      RESOLVED_GWS_TAG="$(resolve_latest_gws_tag)"
      if [[ -n "${RESOLVED_GWS_TAG}" ]]; then
        printf '[bootstrap] resolved latest gws tag: %s\n' "${RESOLVED_GWS_TAG}" >&2
      else
        printf '[bootstrap] WARN: could not resolve latest tag via GitHub API; proceeding with /latest/download/ redirect\n' >&2
      fi
    fi

    install_one "gws" "${platform}"
    install_one "jq"  "${platform}"
    write_version_file
  else
    printf '[bootstrap] cache hit: %s (within TTL); skip\n' "${CACHE_DIR}" >&2
  fi

  emit_result
}

main "$@"
