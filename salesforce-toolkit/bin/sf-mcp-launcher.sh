#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# sf-mcp-launcher.sh — brew→npx dynamic dispatcher for Salesforce DX MCP
# -----------------------------------------------------------------------------
# Resolves the Salesforce MCP entrypoint at launch time so that the static
# .mcp.json remains valid regardless of whether the user has run
# /salesforce-toolkit:sf-setup yet:
#
#   1. sf-mcp-server on PATH (brew install salesforce-mcp ships binary
#      `sf-mcp-server`, NOT `salesforce-mcp` — verified dogfood 2026-05-20)
#      → exec it.
#   2. else npx on PATH → exec `npx -y @salesforce/mcp` (npm package name
#      is `@salesforce/mcp`; its package.json bin field exposes the
#      `sf-mcp-server` command). Cold-start fallback, no brew required.
#   3. else → emit a clear stderr pointer to /salesforce-toolkit:sf-setup
#      and exit 127.
#
# All user-supplied args (e.g. --orgs / --toolsets) are forwarded verbatim
# via "$@".
#
# Refs:
#   - PRODUCT-SPEC / brief Decision Q1 Path D (shim launcher)
#   - PRODUCT-SPEC / brief Decision Q7 (brew-absent fallback to npx)
# =============================================================================

if command -v sf-mcp-server >/dev/null 2>&1; then
  exec sf-mcp-server "$@"
fi

if command -v npx >/dev/null 2>&1; then
  exec npx -y @salesforce/mcp "$@"
fi

printf 'sf-mcp-launcher: neither sf-mcp-server nor npx found on PATH.\n' >&2
printf 'Run /salesforce-toolkit:sf-setup first to install the Salesforce DX MCP stack.\n' >&2
exit 127
