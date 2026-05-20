#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# sf-mcp-launcher.sh — brew→npx dynamic dispatcher for Salesforce DX MCP
# -----------------------------------------------------------------------------
# Resolves the Salesforce MCP entrypoint at launch time so that the static
# .mcp.json remains valid regardless of whether the user has run
# /salesforce-toolkit:sf-setup yet:
#
#   1. salesforce-mcp on PATH (brew install salesforce-mcp) → exec it.
#   2. else npx on PATH                                     → exec
#      `npx -y @salesforce/mcp` (cold-start fallback, no brew required).
#   3. else                                                 → emit a clear
#      stderr pointer to /salesforce-toolkit:sf-setup and exit 127.
#
# All user-supplied args (e.g. --orgs / --toolsets) are forwarded verbatim
# via "$@".
#
# Refs:
#   - PRODUCT-SPEC / brief Decision Q1 Path D (shim launcher)
#   - PRODUCT-SPEC / brief Decision Q7 (brew-absent fallback to npx)
# =============================================================================

if command -v salesforce-mcp >/dev/null 2>&1; then
  exec salesforce-mcp "$@"
fi

if command -v npx >/dev/null 2>&1; then
  exec npx -y @salesforce/mcp "$@"
fi

printf 'sf-mcp-launcher: neither salesforce-mcp nor npx found on PATH.\n' >&2
printf 'Run /salesforce-toolkit:sf-setup first to install the Salesforce DX MCP stack.\n' >&2
exit 127
