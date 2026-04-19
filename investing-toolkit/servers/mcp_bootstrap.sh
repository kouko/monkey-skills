#!/usr/bin/env bash
# mcp_bootstrap.sh — investing-toolkit MCP entry router (v1.14.0+)
#
# Claude Code / Claude Cowork spawns this script (via .mcp.json) each
# time the investing-toolkit plugin activates an MCP session.
#
# Two paths:
#   FAST PATH  — if the environment is ready (uv installed + ../scripts/
#                deps pre-warmed + plugin version matches the last
#                successful setup), we exec directly into mcp_server.py.
#                This must complete + respond to `initialize` within
#                60 s (observed Claude Desktop handshake timeout).
#   BOOTSTRAP  — if anything is missing, we spawn setup.sh in the
#                background and exec the stdlib wrapper, which responds
#                to initialize immediately and exposes a single
#                `investing_toolkit_status` tool that Claude can poll.
#
# All paths write logs to $LOG_DIR/bootstrap.log for debugging.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$HERE")}"
DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.cache/investing-toolkit}"
mkdir -p "$DATA_DIR"
LOG_FILE="$DATA_DIR/bootstrap.log"
MARKER_FILE="$DATA_DIR/.mcp_ready"
SETUP_LOCK="$DATA_DIR/.setup.lock"

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*" >> "$LOG_FILE"; }

# ── Resolve plugin version ──────────────────────────────────────────────────
PLUGIN_JSON="$PLUGIN_ROOT/.claude-plugin/plugin.json"
CURRENT_VERSION=""
if [ -f "$PLUGIN_JSON" ]; then
    CURRENT_VERSION=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$PLUGIN_JSON" | head -n 1)
fi

# ── Resolve uv binary ───────────────────────────────────────────────────────
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

# ── Read marker ─────────────────────────────────────────────────────────────
MARKER_VERSION=""
[ -f "$MARKER_FILE" ] && MARKER_VERSION=$(tr -d '[:space:]' < "$MARKER_FILE")

log "bootstrap invoked: plugin_root=$PLUGIN_ROOT current_version=$CURRENT_VERSION marker_version=$MARKER_VERSION uv=$UV_BIN"

# ── FAST PATH ───────────────────────────────────────────────────────────────
if [ -n "$UV_BIN" ] && [ -n "$CURRENT_VERSION" ] && \
   [ "$MARKER_VERSION" = "$CURRENT_VERSION" ]; then
    log "fast path → exec $UV_BIN run --script $HERE/mcp_server.py"
    export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"
    export INVESTING_TOOLKIT_CACHE="${INVESTING_TOOLKIT_CACHE:-$DATA_DIR/cache}"
    exec "$UV_BIN" run --script "$HERE/mcp_server.py"
fi

# ── BOOTSTRAP PATH ──────────────────────────────────────────────────────────
log "bootstrap path: spawning setup.sh in background"

# Atomic lock: only one setup process at a time (mitigates concurrent Claude windows).
if ( set -o noclobber; : > "$SETUP_LOCK" ) 2>/dev/null; then
    (
        trap 'rm -f "$SETUP_LOCK"' EXIT
        bash "$HERE/setup.sh" >> "$DATA_DIR/setup.log" 2>&1
    ) &
    disown
    log "setup.sh spawned (pid $!)"
else
    log "setup already running (lock $SETUP_LOCK present) — skipping spawn"
fi

# Hand stdio off to the stdlib wrapper. This process must respond to
# `initialize` within <60 s — wrapper is pure stdlib and replies instantly.
export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"
export CLAUDE_PLUGIN_DATA="$DATA_DIR"
log "exec python3 $HERE/mcp_wrapper.py"
exec /usr/bin/python3 "$HERE/mcp_wrapper.py"
