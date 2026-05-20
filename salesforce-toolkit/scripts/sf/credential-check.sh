#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# credential-check.sh — Salesforce-toolkit read-only diagnostic
# -----------------------------------------------------------------------------
# Responsibilities:
#   Probe the local environment for the components salesforce-toolkit needs
#   (Homebrew, `sf` CLI, `salesforce-mcp` server, Node.js) and the currently
#   configured Salesforce default org. Emit a single JSON object to stdout
#   summarising the result. Pure read-only: this script never installs,
#   uninstalls, logs in, or modifies state.
#
# Output JSON shape (TECH-SPEC §4.2 contract for setup Step 6 verify):
#   {
#     "brew":               "installed" | "missing",
#     "sf_cli":             "installed" | "missing",
#     "sf_version":         "<version-string>" | null,
#     "salesforce_mcp":     "installed" | "missing",
#     "mcp_version":        "<version-string>" | null,
#     "node":               "installed" | "missing",
#     "default_org":        "<alias>"   | null,
#     "default_org_status": "active" | "expired" | null
#   }
#
# Exit code: ALWAYS 0.
#   Rationale: this is the diagnostic auto-setup.sh consumes to decide which
#   install steps to skip. Errors-out-of-band would force auto-setup.sh to
#   treat a missing tool as a script failure rather than a state to remediate.
#
# Args: none (any args ignored; `--help` is not provided in v0.1.0).
# Stdin: none
# Stderr: silent on success path. (No progress chatter — auto-setup.sh
#         orchestrator owns user-facing messaging.)
#
# Security:
#   - No credential file is opened. We never read `~/.sfdx/` org JSON
#     directly; we ask `sf` for the alias + connectedStatus via the
#     officially-supported `--json` interface.
#   - No environment variable is echoed.
#
# Bash 3.2 compatible (macOS default).
# =============================================================================

export LC_ALL="${LC_ALL:-en_US.UTF-8}"

# ---------------------------------------------------------------------------
# Tool presence + version probes
# ---------------------------------------------------------------------------

# Returns 0 if cmd is on PATH, 1 otherwise. Pure wrapper around `command -v`
# for readability at the call sites.
have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

# Echo `sf --version` output (single line) or empty if sf is missing.
# `sf --version` may print to stdout *or* exit non-zero on a botched
# install; both paths funnel to empty string here.
probe_sf_version() {
  have_cmd sf || { printf ''; return 0; }
  sf --version 2>/dev/null | head -n 1 || printf ''
}

# Echo `salesforce-mcp --version` (or `npx -y @salesforce/mcp --version`
# fallback) or empty. We deliberately DO NOT shell out to npx in the
# fallback because (a) it would be a multi-second network probe in the
# common cold-cache case, and (b) a missing `salesforce-mcp` binary
# means the brew bottle is not installed regardless of whether npx
# could resolve the package. v0.1.0 keeps this brew-binary-only;
# auto-setup.sh covers the npx fallback narrative.
probe_mcp_version() {
  have_cmd salesforce-mcp || { printf ''; return 0; }
  salesforce-mcp --version 2>/dev/null | head -n 1 || printf ''
}

# ---------------------------------------------------------------------------
# Default org probe — alias + connectedStatus
# ---------------------------------------------------------------------------

# Echo the alias currently configured as `target-org` (sf config get
# target-org --json → .result[0].value) or empty string if unset/sf
# missing. Failures (sf command-not-found, jq parse failure, config
# unset) all collapse to empty: the caller maps empty → JSON null.
probe_default_org_alias() {
  have_cmd sf || { printf ''; return 0; }
  local raw value
  raw="$(sf config get target-org --json 2>/dev/null || printf '')"
  if [ -z "$raw" ]; then
    printf ''
    return 0
  fi
  # `.result[0].value` is the alias or username sf considers the
  # default; null/absent → empty.
  value="$(printf '%s' "$raw" | jq -r '.result[0].value // empty' 2>/dev/null || printf '')"
  printf '%s' "$value"
}

# Echo "active" | "expired" | "" for the given alias.
# Mapping rule (TECH-SPEC §4.2):
#   sf org display --target-org=<alias> --json → .result.connectedStatus
#     "Connected"                              → "active"
#     "RefreshTokenAuthError" / "Expired"      → "expired"
#     anything else                            → "" (unknown)
probe_default_org_status() {
  local alias="$1"
  if [ -z "$alias" ]; then
    printf ''
    return 0
  fi
  have_cmd sf || { printf ''; return 0; }
  local raw status
  raw="$(sf org display --target-org="$alias" --json 2>/dev/null || printf '')"
  if [ -z "$raw" ]; then
    printf ''
    return 0
  fi
  status="$(printf '%s' "$raw" | jq -r '.result.connectedStatus // empty' 2>/dev/null || printf '')"
  case "$status" in
    Connected)
      printf 'active'
      ;;
    RefreshTokenAuthError|Expired|*Expired*)
      printf 'expired'
      ;;
    *)
      printf ''
      ;;
  esac
}

# ---------------------------------------------------------------------------
# JSON emitter — single source of the output contract
# ---------------------------------------------------------------------------

# Map empty-string → JSON null, non-empty → JSON string. Centralised so
# the main() body reads as a flat field list rather than 8 ternaries.
# We rely on jq's `--arg` always producing a JSON string + a post-pass
# `if . == "" then null else . end` to project to null. This keeps the
# emitter safe against version strings containing quotes/backslashes
# (jq handles the escaping).
emit_json() {
  local brew_state="$1"
  local sf_state="$2"
  local sf_version="$3"
  local mcp_state="$4"
  local mcp_version="$5"
  local node_state="$6"
  local default_org="$7"
  local default_org_status="$8"

  jq -n \
    --arg brew                "$brew_state" \
    --arg sf_cli              "$sf_state" \
    --arg sf_version          "$sf_version" \
    --arg salesforce_mcp      "$mcp_state" \
    --arg mcp_version         "$mcp_version" \
    --arg node                "$node_state" \
    --arg default_org         "$default_org" \
    --arg default_org_status  "$default_org_status" \
    '{
       brew:               $brew,
       sf_cli:             $sf_cli,
       sf_version:         (if $sf_version         == "" then null else $sf_version         end),
       salesforce_mcp:     $salesforce_mcp,
       mcp_version:        (if $mcp_version        == "" then null else $mcp_version        end),
       node:               $node,
       default_org:        (if $default_org        == "" then null else $default_org        end),
       default_org_status: (if $default_org_status == "" then null else $default_org_status end)
     }'
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

main() {
  # jq is a hard runtime dep for the emitter. We could die_json here but
  # the script's contract is "always emit valid JSON + exit 0"; if jq is
  # genuinely missing we have nothing to emit with. Print a static
  # all-missing object via printf as a last-resort and still exit 0.
  if ! have_cmd jq; then
    printf '%s\n' '{"brew":"missing","sf_cli":"missing","sf_version":null,"salesforce_mcp":"missing","mcp_version":null,"node":"missing","default_org":null,"default_org_status":null}'
    exit 0
  fi

  local brew_state sf_state sf_version mcp_state mcp_version node_state
  local default_org default_org_status

  have_cmd brew           && brew_state="installed" || brew_state="missing"
  have_cmd sf             && sf_state="installed"   || sf_state="missing"
  have_cmd salesforce-mcp && mcp_state="installed"  || mcp_state="missing"
  have_cmd node           && node_state="installed" || node_state="missing"

  sf_version="$(probe_sf_version)"
  mcp_version="$(probe_mcp_version)"
  default_org="$(probe_default_org_alias)"
  default_org_status="$(probe_default_org_status "$default_org")"

  emit_json \
    "$brew_state" \
    "$sf_state" \
    "$sf_version" \
    "$mcp_state" \
    "$mcp_version" \
    "$node_state" \
    "$default_org" \
    "$default_org_status"

  exit 0
}

# Only invoke main when executed directly (not when sourced — preserves
# the option for callers to source the probe helpers for unit-testing).
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
