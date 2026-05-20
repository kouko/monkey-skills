#!/usr/bin/env bash
# =============================================================================
# alias-infer.sh — 3-layer Salesforce org alias inference for salesforce-toolkit
# -----------------------------------------------------------------------------
# Provides `infer_alias`, a pure shell function other scripts source to derive
# a clean `sf` CLI alias from (1) an explicit user override, (2) the org's
# instance URL subdomain, or (3) the well-known login/test endpoint name.
# Source of truth: spec Decision Q3 in
#   docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md.
#
# Why this guard exists:
#   The auto-setup.sh flow needs to suggest a sensible default alias at the
#   `sf org login web` step. Hard-coding `ichef` was rejected (Brief §Decisions)
#   because (a) it leaks a specific tenant name into a generic toolkit and
#   (b) multi-org users get the same alias for every login, masking later orgs.
#   Three-layer inference covers the common cases (My-Domain URL, well-known
#   endpoint, explicit user override) while leaving an `empty` escape hatch so
#   `sf` falls back to its own username-derived default when none apply.
#
# Contract:
#   - Designed to be `source`d:
#       source "${CLAUDE_PLUGIN_ROOT}/scripts/sf/alias-infer.sh"
#   - Exposes one public function: `infer_alias INSTANCE_URL USER_ALIAS`
#   - Both arguments are required (use `""` for absent). Function echoes the
#     inferred alias to stdout (may be empty string) and returns 0.
#   - No side effects: no globals written, no commands executed beyond
#     `tr` (used to lowercase the captured subdomain — `${var,,}` is bash 4+
#     only and macOS default bash is 3.2).
#
# Layering (per Decision Q3):
#   Layer 1 — explicit override:  USER_ALIAS non-empty wins unconditionally.
#   Layer 2 — subdomain parse:    INSTANCE_URL matches
#                                   ^https?://<sub>.my.salesforce.com
#                                   ^https?://<sub>.lightning.force.com
#                                   ^https?://<sub>.sandbox.my.salesforce.com
#                                 → lowercase <sub>, collapse `--` → `-`,
#                                   strip leading/trailing `-`.
#   Layer 3 — endpoint fallback:  login.salesforce.com / empty URL → `prod`;
#                                 test.salesforce.com → `sandbox`;
#                                 anything else → empty string (caller lets
#                                 `sf` derive an alias from the username).
#
# Bash 3.2 compatibility (macOS default):
#   - No associative arrays.
#   - No `${var,,}` lowercase — uses `tr '[:upper:]' '[:lower:]'`.
#   - Regex match via `[[ ... =~ ... ]]` + BASH_REMATCH (3.2+ supports both).
#
# Not done in this helper (intentional):
#   - No URL validation beyond the regex — caller is responsible for ensuring
#     the URL is well-formed; this is purely a string parser.
#   - No interactive prompt — auto-setup.sh layers Enter-to-accept on top.
# =============================================================================

# Public: infer Salesforce CLI alias from instance URL and optional user
# override. Echoes the alias to stdout (may be empty); always returns 0.
#
# Arguments:
#   $1  INSTANCE_URL  e.g. "https://acme.my.salesforce.com" or ""
#   $2  USER_ALIAS    explicit override, or "" to defer to inference
infer_alias() {
  local instance_url="${1:-}"
  local user_alias="${2:-}"
  local sub

  # Layer 1 — explicit override wins.
  if [ -n "$user_alias" ]; then
    printf '%s\n' "$user_alias"
    return 0
  fi

  # Layer 2 — parse subdomain from *.my.salesforce.com /
  # *.lightning.force.com / *.sandbox.my.salesforce.com. Order in the
  # alternation matters for correctness only when the subdomain itself
  # could end in one of the suffixes; the character class `[a-zA-Z0-9_-]+`
  # excludes `.` so each capture is bounded at the first dot after the
  # scheme, making the alternation order irrelevant in practice.
  if [[ "$instance_url" =~ ^https?://([a-zA-Z0-9_-]+)\.(my\.salesforce\.com|lightning\.force\.com|sandbox\.my\.salesforce\.com) ]]; then
    sub="${BASH_REMATCH[1]}"
    # Lowercase via tr (bash 3.2 has no ${var,,}).
    sub="$(printf '%s' "$sub" | tr '[:upper:]' '[:lower:]')"
    # Collapse runs of `-` (e.g. `--`, `----`) into a single `-`. One pass
    # of ${var//--/-} only halves doubled runs; loop until no `--` remains.
    while [[ "$sub" == *--* ]]; do
      sub="${sub//--/-}"
    done
    # Strip leading / trailing `-` (defensive — regex char class allows them
    # but DNS-legal subdomains do not start/end with a hyphen).
    sub="${sub#-}"
    sub="${sub%-}"
    printf '%s\n' "$sub"
    return 0
  fi

  # Layer 3 — well-known endpoint fallback.
  case "$instance_url" in
    'https://login.salesforce.com'|'http://login.salesforce.com'|'')
      printf '%s\n' "prod"
      ;;
    'https://test.salesforce.com'|'http://test.salesforce.com')
      printf '%s\n' "sandbox"
      ;;
    *)
      # Unknown host — emit empty string so caller lets `sf` use its own
      # username-derived alias.
      printf '%s\n' ""
      ;;
  esac
  return 0
}

# Direct-invocation entry point. When this script is executed (not sourced),
# `bash alias-infer.sh <instance_url> [<user_alias>]` prints the resolved
# alias to stdout. When sourced via `source alias-infer.sh`, this block is
# skipped (BASH_SOURCE[0] != $0) and only the function is defined.
#
# Used by Claude-orchestrated `/sf-setup` so the slash command's procedure
# can call alias-infer.sh via a single Bash tool invocation without writing
# a `bash -c 'source ...; infer_alias ...'` wrapper.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  infer_alias "${1:-}" "${2:-}"
fi
