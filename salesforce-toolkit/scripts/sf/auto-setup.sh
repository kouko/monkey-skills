#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# auto-setup.sh — salesforce-toolkit 6-step idempotent installer
# -----------------------------------------------------------------------------
# Codifies the Salesforce DX MCP bootstrap from a clean macOS state to
# "Claude Code can talk to your Salesforce org" as a single rerun-safe
# script. Steps (PRODUCT-SPEC §Decision setup steps):
#
#   1. OS + TTY guard  — macOS only + tty -s (skipped in --dry-run).
#   2. Homebrew        — detect; if absent prompt + run the official
#                        install.sh curl pipe.
#   3. `sf` CLI        — `command -v sf` else `brew install sf`.
#   4. `sf-mcp-server` — `command -v sf-mcp-server` else `brew install
#                        salesforce-mcp` (brew formula name is
#                        `salesforce-mcp`; the binary it produces is
#                        `sf-mcp-server`). Skipped unless --skip-mcp-brew.
#   5. `sf org login web` — alias inferred via scripts/sf/alias-infer.sh
#                        (3-layer: explicit / instance-url subdomain /
#                        well-known endpoint). Enter-to-accept inferred
#                        alias unless --no-prompt. Skipped when an active
#                        default org already exists, unless --force-reauth.
#   6. Verify + JSON   — `sf org display --target-org=<alias> --json` to
#                        confirm; emit final stdout JSON contract.
#
# Idempotent: each step probes current state and emits an "already done:
# <step name>" stderr line when skipped.
#
# Design principles:
#   - --dry-run never touches brew/curl/sf; it only prints the plan and
#     the alias-resolution result, then emits a dry_run=true JSON.
#   - alias inference is delegated to scripts/sf/alias-infer.sh (Q3
#     3-layer); --no-alias forces alias omission so `sf` falls back to
#     its own username-derived alias.
#   - TTY check delegated to scripts/common/tty-guard.sh (sourced).
#   - Bash 3.2 compatible (macOS default): no associative arrays,
#     no `${var,,}`, no `mapfile`.
#
# Args:
#   --dry-run                Print the plan only; no brew/sf/curl. Bats
#                            exercises only this path.
#   --alias=<name>           Explicit alias override (Layer 1).
#   --no-alias               Force omit alias (sf uses username default).
#   --no-prompt              Skip Enter-to-accept prompt; use inferred
#                            (or empty) alias directly.
#   --force-reauth           Re-run `sf org login web` even when an
#                            active default org already exists.
#   --instance-url=<url>     Pass-through to `sf org login web
#                            --instance-url=<url>`; also fed into the
#                            Layer-2 alias-infer parser.
#   --skip-mcp-brew          Skip step 4 `brew install salesforce-mcp`
#                            (launcher shim falls back to npx at runtime).
#   -h|--help                Print usage.
#
# Stdin: none
# Stdout: final JSON contract (PRODUCT-SPEC §setup steps step 6):
#   {
#     "status":       "ok",
#     "sf_version":   "<string>" | null,
#     "mcp_version":  "<string>" | null,
#     "org_alias":    "<string>" | null,
#     "instance_url": "<string>" | null,
#     "oauth_expiry": "<string>" | null,
#     "elapsed_sec":  <number>,
#     "dry_run":      true | false
#   }
# Stderr: human-readable `[auto-setup] step N/6: ...` progress + dry-run
#         plan lines + structured error JSON on failure.
#
# Exit codes:
#   0   success
#   1   generic error (usage / unknown flag / unknown state)
#   10  auth / interaction error (TTY missing, sf login failed)
#   11  unsupported OS (non-Darwin)
#   12  install error (brew / sf / mcp install failed)
# =============================================================================

# --- UTF-8 locale -----------------------------------------------------------
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

# --- sf-CLI telemetry consent bypass ----------------------------------------
# First-run sf CLI shows an interactive y/N telemetry consent prompt that
# blocks in non-TTY contexts (verified dogfood 2026-05-20: sf hangs in CC
# Bash tool waiting for stdin). Setting SF_DISABLE_TELEMETRY=true skips
# the prompt + opts out of telemetry. Users who want to enable telemetry
# can override this env var explicitly before invoking the script.
export SF_DISABLE_TELEMETRY="${SF_DISABLE_TELEMETRY:-true}"

# --- Resolve script dir + source helpers ------------------------------------
# `readlink -f` is GNU; macOS uses `realpath` or BSD `readlink`. Fall back to
# a cd/pwd dance which is POSIX-portable.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

# Dynamic paths — shellcheck cannot statically resolve them at lint time
# from this script's location, but bash resolves them fine at runtime
# (verified by bats coverage). Disable SC1091 explicitly so the lint
# stays clean.
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/../common/tty-guard.sh"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/alias-infer.sh"

# --- Flags (defaults) -------------------------------------------------------
DRY_RUN=0
USER_ALIAS=""
NO_ALIAS=0
NO_PROMPT=0
FORCE_REAUTH=0
INSTANCE_URL=""
SKIP_MCP_BREW=0

# --- Internal state ---------------------------------------------------------
START_EPOCH=0
SF_VERSION=""
MCP_VERSION=""
FINAL_ALIAS=""
OAUTH_EXPIRY=""

# --- die_json: structured error → stderr, then exit -------------------------
die_json() {
  local code="$1"
  local msg="$2"
  local encoded
  if command -v jq >/dev/null 2>&1; then
    encoded="$(printf '%s' "${msg}" | jq -R -s '.')"
  else
    # Fallback: naive escape of embedded quotes/backslashes.
    encoded="\"${msg//\"/\\\"}\""
  fi
  printf '{"error":true,"exit_code":%s,"message":%s}\n' "${code}" "${encoded}" >&2
  exit "${code}"
}

# --- step: print [auto-setup] step N/6 header to stderr ---------------------
step() {
  local n="$1"
  shift
  printf '[auto-setup] step %s/6: %s\n' "${n}" "$*" >&2
}

# --- dry_echo: print a planned command line to stderr -----------------------
dry_echo() {
  printf '[auto-setup] [dry-run] would run: %s\n' "$*" >&2
}

# --- parse_args -------------------------------------------------------------
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run)         DRY_RUN=1; shift ;;
      --no-alias)        NO_ALIAS=1; shift ;;
      --no-prompt)       NO_PROMPT=1; shift ;;
      --force-reauth)    FORCE_REAUTH=1; shift ;;
      --skip-mcp-brew)   SKIP_MCP_BREW=1; shift ;;
      --alias=*)         USER_ALIAS="${1#--alias=}"; shift ;;
      --alias)
        if [[ $# -lt 2 ]]; then
          die_json 1 "--alias requires a value"
        fi
        USER_ALIAS="$2"; shift 2 ;;
      --instance-url=*)  INSTANCE_URL="${1#--instance-url=}"; shift ;;
      --instance-url)
        if [[ $# -lt 2 ]]; then
          die_json 1 "--instance-url requires a value"
        fi
        INSTANCE_URL="$2"; shift 2 ;;
      -h|--help)
        cat <<'USAGE' >&2
Usage: auto-setup.sh [--dry-run] [--alias=NAME] [--no-alias] [--no-prompt]
                     [--force-reauth] [--instance-url=URL] [--skip-mcp-brew]

Options:
  --dry-run               Print the plan; no brew/sf/curl invocations.
  --alias=NAME            Explicit alias (wins over inference).
  --no-alias              Omit alias (sf uses its username-derived default).
  --no-prompt             Skip Enter-to-accept prompt for inferred alias.
  --force-reauth          Re-run `sf org login web` even if already authed.
  --instance-url=URL      Pass to `sf org login web --instance-url=URL`;
                          also feeds the Layer-2 subdomain parse.
  --skip-mcp-brew         Skip `brew install salesforce-mcp`; rely on the
                          launcher shim's npx fallback at runtime.

Exit codes:
  0  success
  1  generic / usage error
  10 auth / interaction error (no TTY, sf login fail)
  11 unsupported OS (non-Darwin)
  12 install error (brew / sf / mcp install failed)
USAGE
        exit 0 ;;
      *)
        die_json 1 "unknown arg: $1" ;;
    esac
  done

  # --alias and --no-alias are mutually exclusive — surface early.
  if (( NO_ALIAS == 1 )) && [[ -n "${USER_ALIAS}" ]]; then
    die_json 1 "--no-alias and --alias=<name> are mutually exclusive"
  fi
}

# --- step 1: OS + TTY guard -------------------------------------------------
ensure_os_and_tty() {
  step 1 "OS + TTY guard"

  local os
  os="$(uname -s)"
  if [[ "${os}" != "Darwin" ]]; then
    die_json 11 "unsupported OS: ${os} (MVP supports macOS only)"
  fi

  if (( DRY_RUN == 1 )); then
    dry_echo "tty -s  # TTY guard skipped in --dry-run"
    return
  fi

  # require_tty exits 10 on failure — no need to check return value.
  require_tty
}

# --- step 2: Homebrew -------------------------------------------------------
ensure_brew() {
  step 2 "ensure Homebrew installed"

  if command -v brew >/dev/null 2>&1; then
    printf '[auto-setup] already done: Homebrew installed\n' >&2
    return
  fi

  if (( DRY_RUN == 1 )); then
    # The literal command we'd run — `$(...)` is part of the planned
    # invocation, not a shell expansion in this script.
    # shellcheck disable=SC2016
    dry_echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    return
  fi

  # Confirm with the user before pulling a remote script over curl.
  printf '\n[auto-setup] Homebrew not found. Install via the official script?\n' >&2
  printf '            (https://brew.sh) — y/N: ' >/dev/tty
  local reply
  read -r reply </dev/tty
  case "${reply}" in
    y|Y|yes|YES)
      if ! /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
        die_json 12 "Homebrew installer failed"
      fi
      ;;
    *)
      die_json 12 "Homebrew install declined; cannot proceed (re-run with brew installed)"
      ;;
  esac

  if ! command -v brew >/dev/null 2>&1; then
    die_json 12 "brew still not in PATH after install"
  fi
}

# --- step 3: sf CLI ---------------------------------------------------------
ensure_sf() {
  step 3 "ensure sf CLI installed"

  if command -v sf >/dev/null 2>&1; then
    printf '[auto-setup] already done: sf CLI installed\n' >&2
    SF_VERSION="$(sf --version 2>/dev/null | head -n 1 || printf '')"
    return
  fi

  if (( DRY_RUN == 1 )); then
    dry_echo 'brew install sf'
    return
  fi

  if ! brew install sf; then
    die_json 12 "brew install sf failed"
  fi
  SF_VERSION="$(sf --version 2>/dev/null | head -n 1 || printf '')"
}

# --- step 4: sf-mcp-server (from brew formula salesforce-mcp) ---------------
# Note: brew formula name is `salesforce-mcp`; the binary it installs is
# `sf-mcp-server` (verified dogfood 2026-05-20; cf. sf-mcp-launcher.sh
# header for the same caveat).
ensure_mcp() {
  step 4 "ensure sf-mcp-server installed (via brew formula salesforce-mcp)"

  if command -v sf-mcp-server >/dev/null 2>&1; then
    printf '[auto-setup] already done: sf-mcp-server installed\n' >&2
    MCP_VERSION="$(brew list --versions salesforce-mcp 2>/dev/null | awk '{print $2}' || printf '')"
    return
  fi

  if (( SKIP_MCP_BREW == 1 )); then
    printf '[auto-setup] --skip-mcp-brew: not installing salesforce-mcp via brew (launcher will fallback to npx)\n' >&2
    return
  fi

  if (( DRY_RUN == 1 )); then
    dry_echo 'brew install salesforce-mcp'
    return
  fi

  if ! brew install salesforce-mcp; then
    die_json 12 "brew install salesforce-mcp failed"
  fi
  MCP_VERSION="$(brew list --versions salesforce-mcp 2>/dev/null | awk '{print $2}' || printf '')"
}

# --- resolve_alias: 3-layer infer + Enter-to-accept prompt ------------------
# Sets FINAL_ALIAS. Honours --no-alias (forces empty regardless of layer
# results) and --no-prompt (skips the ENTER read).
resolve_alias() {
  if (( NO_ALIAS == 1 )); then
    FINAL_ALIAS=""
    printf '[auto-setup] --no-alias: omitting alias (sf will derive from username)\n' >&2
    return
  fi

  local inferred
  inferred="$(infer_alias "${INSTANCE_URL}" "${USER_ALIAS}")"

  # Non-interactive paths short-circuit before any /dev/tty read.
  if (( DRY_RUN == 1 )) || (( NO_PROMPT == 1 )); then
    FINAL_ALIAS="${inferred}"
    return
  fi

  # Explicit user override skips the prompt (Layer 1 dominates UX too —
  # asking "is `foo` ok?" when the user just passed --alias=foo is noise).
  if [[ -n "${USER_ALIAS}" ]]; then
    FINAL_ALIAS="${inferred}"
    return
  fi

  # Enter-to-accept: print inferred + read /dev/tty so this also works
  # when stdin is piped (Claude background invocations still hit the
  # user's terminal). Empty inferred → prompt asks for explicit name or
  # `-` to omit.
  if [[ -n "${inferred}" ]]; then
    printf '\n[auto-setup] Inferred alias: %s\n' "${inferred}" >&2
    # Literal backticks in the help text — no command substitution
    # intended by the single-quoted format string.
    # shellcheck disable=SC2016
    printf '            Press ENTER to accept, type a different name, or `-` to omit: ' >/dev/tty
  else
    printf '\n[auto-setup] No alias inferred from URL.\n' >&2
    # shellcheck disable=SC2016
    printf '            Type an alias, or `-` to omit (sf uses username): ' >/dev/tty
  fi
  local reply
  read -r reply </dev/tty
  case "${reply}" in
    '')
      FINAL_ALIAS="${inferred}" ;;
    '-')
      FINAL_ALIAS="" ;;
    *)
      FINAL_ALIAS="${reply}" ;;
  esac
}

# --- step 5: sf org login web -----------------------------------------------
ensure_org_login() {
  step 5 "sf org login web (alias inference + Enter-to-accept)"

  resolve_alias

  if (( DRY_RUN == 1 )); then
    local plan_alias_part=""
    if [[ -n "${FINAL_ALIAS}" ]]; then
      plan_alias_part=" --alias=${FINAL_ALIAS} --set-default"
    fi
    local plan_url_part=""
    if [[ -n "${INSTANCE_URL}" ]]; then
      plan_url_part=" --instance-url=${INSTANCE_URL}"
    fi
    dry_echo "sf org login web${plan_alias_part}${plan_url_part}"
    return
  fi

  # Skip if a default org is already active + not --force-reauth.
  if (( FORCE_REAUTH == 0 )) && command -v sf >/dev/null 2>&1; then
    if sf org display --json >/dev/null 2>&1; then
      printf '[auto-setup] already done: active default org detected, skipping login (use --force-reauth to re-run)\n' >&2
      return
    fi
  fi

  # Build args without an empty `--alias=` token (sf would treat empty as
  # an invalid alias rather than "no alias").
  local -a login_args
  login_args=(org login web)
  if [[ -n "${FINAL_ALIAS}" ]]; then
    login_args+=("--alias=${FINAL_ALIAS}" "--set-default")
  fi
  if [[ -n "${INSTANCE_URL}" ]]; then
    login_args+=("--instance-url=${INSTANCE_URL}")
  fi

  if ! sf "${login_args[@]}"; then
    die_json 10 "sf org login web failed"
  fi
}

# --- step 6: verify + populate OAUTH_EXPIRY ---------------------------------
verify_org() {
  step 6 "verify org via sf org display"

  if (( DRY_RUN == 1 )); then
    if [[ -n "${FINAL_ALIAS}" ]]; then
      dry_echo "sf org display --target-org=${FINAL_ALIAS} --json"
    else
      dry_echo "sf org display --json"
    fi
    return
  fi

  if ! command -v sf >/dev/null 2>&1; then
    die_json 12 "sf CLI missing at verify step (unexpected)"
  fi

  local raw
  if [[ -n "${FINAL_ALIAS}" ]]; then
    raw="$(sf org display --target-org="${FINAL_ALIAS}" --json 2>/dev/null || printf '')"
  else
    raw="$(sf org display --json 2>/dev/null || printf '')"
  fi
  if [[ -z "${raw}" ]]; then
    die_json 10 "sf org display returned empty payload"
  fi

  # Pull instance URL + token expiry for the final JSON; failures collapse
  # to empty (caller maps "" → null).
  if command -v jq >/dev/null 2>&1; then
    if [[ -z "${INSTANCE_URL}" ]]; then
      INSTANCE_URL="$(printf '%s' "${raw}" | jq -r '.result.instanceUrl // empty' 2>/dev/null || printf '')"
    fi
    OAUTH_EXPIRY="$(printf '%s' "${raw}" | jq -r '.result.accessTokenExpirationDate // .result.connectedStatus // empty' 2>/dev/null || printf '')"
  fi
}

# --- emit_result: stdout JSON contract --------------------------------------
emit_result() {
  local elapsed
  elapsed=$(( $(date +%s) - START_EPOCH ))

  local dry_run_lit
  if (( DRY_RUN == 1 )); then
    dry_run_lit=true
  else
    dry_run_lit=false
  fi

  if command -v jq >/dev/null 2>&1; then
    jq -n \
      --arg status       "ok" \
      --arg sf_version   "${SF_VERSION}" \
      --arg mcp_version  "${MCP_VERSION}" \
      --arg org_alias    "${FINAL_ALIAS}" \
      --arg instance_url "${INSTANCE_URL}" \
      --arg oauth_expiry "${OAUTH_EXPIRY}" \
      --argjson elapsed_sec "${elapsed}" \
      --argjson dry_run "${dry_run_lit}" \
      '{
         status:       $status,
         sf_version:   (if $sf_version   == "" then null else $sf_version   end),
         mcp_version:  (if $mcp_version  == "" then null else $mcp_version  end),
         org_alias:    (if $org_alias    == "" then null else $org_alias    end),
         instance_url: (if $instance_url == "" then null else $instance_url end),
         oauth_expiry: (if $oauth_expiry == "" then null else $oauth_expiry end),
         elapsed_sec:  $elapsed_sec,
         dry_run:      $dry_run
       }'
    return
  fi

  # jq missing fallback — emit minimal JSON by hand. This path is only
  # hit when `brew install` of jq has never happened on the host; we
  # still want a parseable JSON document so callers don't choke.
  printf '{"status":"ok","sf_version":null,"mcp_version":null,"org_alias":null,"instance_url":null,"oauth_expiry":null,"elapsed_sec":%s,"dry_run":%s}\n' \
    "${elapsed}" "${dry_run_lit}"
}

# --- main -------------------------------------------------------------------
main() {
  parse_args "$@"
  START_EPOCH="$(date +%s)"

  printf '[auto-setup] dry_run=%d alias=%s no_alias=%d no_prompt=%d force_reauth=%d skip_mcp_brew=%d\n' \
    "${DRY_RUN}" "${USER_ALIAS:-<none>}" "${NO_ALIAS}" "${NO_PROMPT}" "${FORCE_REAUTH}" "${SKIP_MCP_BREW}" >&2

  ensure_os_and_tty   # step 1
  ensure_brew         # step 2
  ensure_sf           # step 3
  ensure_mcp          # step 4
  ensure_org_login    # step 5
  verify_org          # step 6

  emit_result
}

main "$@"
