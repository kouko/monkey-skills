#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# refresh-auth.sh — salesforce-toolkit standalone re-auth helper
# -----------------------------------------------------------------------------
# Direct `sf org login web --alias=<X> --set-default` invocation without the
# 6-step orchestrator overhead. Use this when the OAuth token has expired and
# the user just wants to re-authenticate the SAME org alias (no install, no
# alias inference, no MCP check).
#
# Relationship to auto-setup.sh:
#   - auto-setup.sh is for first-time install + first login (idempotent
#     6-step from clean macOS state).
#   - refresh-auth.sh is for "I'm already set up; my token expired" —
#     a single sf-CLI re-auth call wrapped in the same TTY guard +
#     argument-parsing + JSON-result contract the rest of the toolkit
#     follows.
#
# Default behavior:
#   - --alias is resolved from `sf config get target-org` when not passed
#     explicitly. If neither is available, abort with a usage error rather
#     than guessing — calling `sf org login web` without --alias would
#     authenticate but not bind to any alias.
#   - --set-default is always appended so the freshly re-authed org becomes
#     the current default (matches user intent: "I just want to log back in
#     to the org I was using").
#
# Args:
#   --alias=<name>   Explicit alias override. Falls back to
#                    `sf config get target-org` when omitted.
#   --dry-run        Print the plan only; do NOT invoke `sf`. Bats covers
#                    this path; the user dogfoods the real path manually.
#   -h|--help        Print usage.
#
# Stdin: none (interactive — controlling TTY required unless --dry-run).
# Stdout: final JSON contract on real re-auth path:
#   {
#     "status":       "ok",
#     "alias":        "<string>",
#     "instance_url": "<string>" | null,
#     "expiry":       "<string>" | null
#   }
# Stderr: human-readable `[refresh-auth] ...` progress + dry-run plan
#         lines + structured error JSON on failure.
#
# Exit codes:
#   0   success (re-auth complete)
#   1   generic error (unknown flag, --alias resolution failed)
#   10  auth / interaction error (no TTY, sf login failed)
#   12  install error (sf CLI missing — user should run auto-setup.sh first)
# =============================================================================

# --- UTF-8 locale -----------------------------------------------------------
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

# --- sf-CLI telemetry consent bypass ----------------------------------------
# Cf. auto-setup.sh header: SF_DISABLE_TELEMETRY=true skips first-run sf
# consent prompt that would otherwise hang in non-TTY contexts. Dogfood-
# verified 2026-05-20. Override the env var before invocation to opt in.
export SF_DISABLE_TELEMETRY="${SF_DISABLE_TELEMETRY:-true}"

# --- Resolve script dir + source helpers ------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

# Dynamic source path — static lint cannot resolve, but bash does at runtime
# (covered by bats). Disable SC1091 explicitly so the lint stays clean.
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/../common/tty-guard.sh"

# --- Flags (defaults) -------------------------------------------------------
DRY_RUN=0
USER_ALIAS=""

# --- die_json: structured error → stderr, then exit -------------------------
die_json() {
  local code="$1"
  local msg="$2"
  local encoded
  if command -v jq >/dev/null 2>&1; then
    encoded="$(printf '%s' "${msg}" | jq -R -s '.')"
  else
    # Fallback: naive escape of embedded quotes.
    encoded="\"${msg//\"/\\\"}\""
  fi
  printf '{"error":true,"exit_code":%s,"message":%s}\n' "${code}" "${encoded}" >&2
  exit "${code}"
}

# --- dry_echo: print a planned command line to stderr -----------------------
dry_echo() {
  printf '[refresh-auth] [dry-run] would run: %s\n' "$*" >&2
}

# --- parse_args -------------------------------------------------------------
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run)    DRY_RUN=1; shift ;;
      --alias=*)    USER_ALIAS="${1#--alias=}"; shift ;;
      --alias)
        if [[ $# -lt 2 ]]; then
          die_json 1 "--alias requires a value"
        fi
        USER_ALIAS="$2"; shift 2 ;;
      -h|--help)
        cat <<'USAGE' >&2
Usage: refresh-auth.sh [--alias=NAME] [--dry-run]

Standalone Salesforce re-auth helper. Wraps `sf org login web` so an
already-set-up user can refresh their OAuth token without re-running the
full 6-step auto-setup.sh.

Options:
  --alias=NAME   Org alias to re-authenticate. Defaults to the result of
                 `sf config get target-org` when omitted.
  --dry-run      Print the plan only; do NOT invoke `sf`.
  -h, --help     Print this usage.

Exit codes:
  0   success
  1   generic / usage error (--alias resolution failed)
  10  auth / interaction error (no TTY, sf login failed)
  12  install error (sf CLI missing — run auto-setup.sh first)
USAGE
        exit 0 ;;
      *)
        die_json 1 "unknown arg: $1" ;;
    esac
  done
}

# --- resolve_alias: explicit > `sf config get target-org` -------------------
# Sets FINAL_ALIAS. In --dry-run we still try to honour an explicit
# --alias=X but skip the `sf config get` call (sf may not be installed).
FINAL_ALIAS=""
resolve_alias() {
  if [[ -n "${USER_ALIAS}" ]]; then
    FINAL_ALIAS="${USER_ALIAS}"
    return
  fi

  if (( DRY_RUN == 1 )); then
    # In dry-run with no explicit alias, leave empty — the planned command
    # will simply show no `--alias=` token, which is the honest plan.
    FINAL_ALIAS=""
    return
  fi

  if ! command -v sf >/dev/null 2>&1; then
    die_json 12 "sf CLI not found in PATH — run auto-setup.sh first"
  fi

  # `sf config get target-org --json` returns:
  #   {"status":0,"result":[{"name":"target-org","value":"foo",...}], ...}
  # When no default is set, .result[0].value is null/missing.
  local raw
  raw="$(sf config get target-org --json 2>/dev/null || printf '')"
  if [[ -z "${raw}" ]]; then
    die_json 1 "could not read default target-org from sf config; pass --alias=NAME explicitly"
  fi

  if command -v jq >/dev/null 2>&1; then
    FINAL_ALIAS="$(printf '%s' "${raw}" | jq -r '.result[0].value // empty' 2>/dev/null || printf '')"
  fi

  if [[ -z "${FINAL_ALIAS}" ]]; then
    die_json 1 "no default target-org configured; pass --alias=NAME explicitly"
  fi
}

# --- do_login: invoke sf org login web (or print plan) ----------------------
do_login() {
  if (( DRY_RUN == 1 )); then
    local plan_alias_part=""
    if [[ -n "${FINAL_ALIAS}" ]]; then
      plan_alias_part=" --alias=${FINAL_ALIAS} --set-default"
    fi
    dry_echo "sf org login web${plan_alias_part}"
    return
  fi

  if ! command -v sf >/dev/null 2>&1; then
    die_json 12 "sf CLI not found in PATH — run auto-setup.sh first"
  fi

  printf '[refresh-auth] initiating sf org login web for alias: %s\n' "${FINAL_ALIAS}" >&2
  printf '[refresh-auth] browser will open; complete consent to refresh OAuth token\n' >&2

  if ! sf org login web --alias="${FINAL_ALIAS}" --set-default; then
    die_json 10 "sf org login web failed"
  fi
}

# --- verify_and_emit: sf org display --json → stdout JSON contract ----------
verify_and_emit() {
  if (( DRY_RUN == 1 )); then
    # Dry-run prints no stdout JSON: only the plan went to stderr. Mirrors
    # auto-setup.sh's convention that --dry-run plans live on stderr and
    # the stdout JSON is reserved for real-result emission. Bats does not
    # assert on stdout for dry-run here — only on the plan content.
    return
  fi

  local raw
  raw="$(sf org display --target-org="${FINAL_ALIAS}" --json 2>/dev/null || printf '')"
  if [[ -z "${raw}" ]]; then
    die_json 10 "sf org display returned empty payload after login"
  fi

  local instance_url=""
  local expiry=""
  if command -v jq >/dev/null 2>&1; then
    instance_url="$(printf '%s' "${raw}" | jq -r '.result.instanceUrl // empty' 2>/dev/null || printf '')"
    expiry="$(printf '%s' "${raw}" | jq -r '.result.accessTokenExpirationDate // empty' 2>/dev/null || printf '')"
  fi

  if command -v jq >/dev/null 2>&1; then
    jq -n \
      --arg status       "ok" \
      --arg alias        "${FINAL_ALIAS}" \
      --arg instance_url "${instance_url}" \
      --arg expiry       "${expiry}" \
      '{
         status:       $status,
         alias:        $alias,
         instance_url: (if $instance_url == "" then null else $instance_url end),
         expiry:       (if $expiry       == "" then null else $expiry       end)
       }'
    return
  fi

  # jq-missing fallback — minimal JSON by hand.
  printf '{"status":"ok","alias":"%s","instance_url":null,"expiry":null}\n' \
    "${FINAL_ALIAS}"
}

# --- main -------------------------------------------------------------------
main() {
  parse_args "$@"

  printf '[refresh-auth] dry_run=%d alias=%s\n' \
    "${DRY_RUN}" "${USER_ALIAS:-<auto>}" >&2

  # TTY guard ONLY on real path; dry-run is bats / CI-friendly.
  if (( DRY_RUN == 0 )); then
    require_tty
  fi

  resolve_alias
  do_login
  verify_and_emit
}

main "$@"
