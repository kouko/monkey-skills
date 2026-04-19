#!/usr/bin/env bash
# setup.sh — investing-toolkit MCP environment bootstrap (v1.14.0+)
#
# Runs once on first plugin activation (spawned by mcp_bootstrap.sh when
# the readiness marker is missing or the plugin version has changed).
#
# Steps:
#   1. Install uv if absent.
#        tier 1: Homebrew (preferred; easier to upgrade)
#        tier 2: official curl installer (https://astral.sh/uv/install.sh)
#   2. Pre-warm uv cache by running `mcp_server.py --self-check` — this
#      forces dep resolution + Python 3.11 download + wheel install so
#      that the FAST PATH in mcp_bootstrap.sh completes inside the 60 s
#      MCP handshake window.
#   3. Write the readiness marker ($CLAUDE_PLUGIN_DATA/.mcp_ready)
#      containing the plugin version. mcp_bootstrap.sh compares this to
#      $PLUGIN_ROOT/.claude-plugin/plugin.json on subsequent starts.
#
# Logs go to $CLAUDE_PLUGIN_DATA/setup.log (redirected by the caller).
# Errors are surfaced via the absence of the marker + a [status] entry
# at the tail of setup.log, which mcp_wrapper.py reads and reports.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$HERE")}"
DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.cache/investing-toolkit}"
MARKER_FILE="$DATA_DIR/.mcp_ready"

PLUGIN_JSON="$PLUGIN_ROOT/.claude-plugin/plugin.json"
CURRENT_VERSION=""
if [ -f "$PLUGIN_JSON" ]; then
    CURRENT_VERSION=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$PLUGIN_JSON" | head -n 1)
fi
[ -z "$CURRENT_VERSION" ] && CURRENT_VERSION="unknown"

say() { printf '[setup %s] %s\n' "$(date '+%H:%M:%S')" "$*"; }

mkdir -p "$DATA_DIR"

say "investing-toolkit setup starting (version $CURRENT_VERSION)"
say "plugin_root=$PLUGIN_ROOT data_dir=$DATA_DIR"

# ── Step 1: ensure uv is installed ──────────────────────────────────────────
UV_BIN=""
for cand in \
    "$(command -v uv 2>/dev/null || true)" \
    "$HOME/.local/bin/uv" \
    "/opt/homebrew/bin/uv" \
    "/usr/local/bin/uv"
do
    if [ -n "$cand" ] && [ -x "$cand" ]; then
        UV_BIN="$cand"
        break
    fi
done

if [ -z "$UV_BIN" ]; then
    if command -v brew >/dev/null 2>&1; then
        say "Homebrew detected → brew install uv"
        if ! brew install uv; then
            say "[status] FAILED: brew install uv exit code $?"
            exit 1
        fi
    else
        say "Homebrew not available → curl installer"
        if ! curl -LsSf https://astral.sh/uv/install.sh | sh; then
            say "[status] FAILED: curl installer exit code $?"
            exit 1
        fi
    fi

    for cand in \
        "$HOME/.local/bin/uv" \
        "/opt/homebrew/bin/uv" \
        "/usr/local/bin/uv" \
        "$(command -v uv 2>/dev/null || true)"
    do
        if [ -n "$cand" ] && [ -x "$cand" ]; then
            UV_BIN="$cand"
            break
        fi
    done
fi

if [ -z "$UV_BIN" ]; then
    say "[status] FAILED: uv not found after install attempts"
    exit 1
fi

say "uv ready: $UV_BIN ($($UV_BIN --version 2>&1 || echo unknown))"

# ── Step 2: pre-warm dep cache ──────────────────────────────────────────────
say "pre-warming dep cache via --self-check (resolves mcp/yfinance/akshare/pandas/…)"
export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"
if ! "$UV_BIN" run --script "$HERE/mcp_server.py" --self-check; then
    say "[status] FAILED: --self-check exit code $?"
    exit 1
fi

# ── Step 3: write readiness marker ──────────────────────────────────────────
printf '%s' "$CURRENT_VERSION" > "$MARKER_FILE"
say "[status] OK: marker written → $MARKER_FILE ($CURRENT_VERSION)"
say "Restart Claude Desktop (Cmd+Q then reopen) to activate MCP tools."
exit 0
