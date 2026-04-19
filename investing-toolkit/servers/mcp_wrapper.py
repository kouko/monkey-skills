#!/usr/bin/env python3
"""mcp_wrapper.py — stdlib JSON-RPC wrapper for investing-toolkit
bootstrap path (v1.14.0+).

Runs during the window when investing-toolkit's MCP environment is not
yet provisioned (uv missing, deps not resolved, or plugin version
bumped).  mcp_bootstrap.sh spawns setup.sh in the background and execs
this wrapper to handle the current MCP session — Claude's `initialize`
must be answered within 60 s, and stdlib alone is fast enough.

The wrapper exposes one tool, `investing_toolkit_status`, that reports
whether background setup finished. When it's done, it asks the user to
restart Claude Desktop so mcp_bootstrap.sh can take the FAST PATH into
the real MCP server.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parents[1])
DATA_DIR = Path(
    os.environ.get("CLAUDE_PLUGIN_DATA")
    or (Path.home() / ".cache" / "investing-toolkit")
)
MARKER_FILE = DATA_DIR / ".mcp_ready"
SETUP_LOG = DATA_DIR / "setup.log"
PLUGIN_JSON = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"

_START_TS = datetime.now(tz=timezone.utc)


def _plugin_version() -> str:
    try:
        doc = json.loads(PLUGIN_JSON.read_text())
        return doc.get("version", "unknown")
    except Exception:
        return "unknown"


def _tail(path: Path, n: int = 30) -> str:
    try:
        lines = path.read_text(errors="replace").splitlines()
        return "\n".join(lines[-n:])
    except Exception:
        return ""


def _elapsed_seconds() -> int:
    return int((datetime.now(tz=timezone.utc) - _START_TS).total_seconds())


def _status_message() -> str:
    current = _plugin_version()
    if MARKER_FILE.exists():
        marker = MARKER_FILE.read_text().strip()
        if marker == current:
            return (
                f"✅ investing-toolkit MCP environment is ready "
                f"(version {current}).\n\n"
                "The background setup finished. **Please quit Claude "
                "Desktop (Cmd+Q on macOS) and reopen it** — on the next "
                "launch, the MCP bootstrap will take the fast path and "
                "expose the full set of 13 investing-toolkit tools "
                "(yfinance, FRED, SEC EDGAR, MOPS, TWSE OpenAPI, "
                "FinMind, NBS, akshare).\n\n"
                "No further action required after the restart."
            )
        return (
            f"⚠️ A setup marker exists but it records a different "
            f"version ({marker}) than the current plugin ({current}). "
            "Background setup is rebuilding the environment for the "
            "new version; check back shortly."
        )

    log_tail = _tail(SETUP_LOG, 20)
    if log_tail and "[status] FAILED" in log_tail:
        return (
            "❌ investing-toolkit environment setup FAILED. "
            "Tail of setup log:\n\n"
            f"```\n{log_tail}\n```\n\n"
            "Check network access, Homebrew / curl availability, and "
            f"disk space. Log file: {SETUP_LOG}"
        )

    elapsed = _elapsed_seconds()
    return (
        f"⏳ investing-toolkit environment is still provisioning "
        f"(elapsed in this session: ~{elapsed} s; typical total "
        "60–120 s on first install).\n\n"
        "uv install + Python 3.11 download + 66 wheel installs run in "
        "the background. Ask me again in a minute, or keep working and "
        "I'll re-check on the next turn. You don't need to do anything "
        "manually.\n\n"
        f"(Setup log: `{SETUP_LOG}` — tail if curious.)"
    )


# ---------------------------------------------------------------------------
# Minimal JSON-RPC stdio loop (stdlib only; no mcp SDK required here)
# ---------------------------------------------------------------------------


def _send(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _tool_schema() -> list[dict]:
    return [{
        "name": "investing_toolkit_status",
        "description": (
            "Check the provisioning status of investing-toolkit's MCP "
            "environment. On first plugin install, uv + Python 3.11 + "
            "Python dependencies are installed in the background "
            "(~1–2 min). This tool reports: whether setup is still "
            "running, whether it succeeded (ask user to restart Claude "
            "Desktop), or whether it failed (returns log tail). Call "
            "this if other investing-toolkit tools are not yet "
            "visible."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    }]


def main() -> None:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw)
        except Exception:
            continue

        method = req.get("method")
        req_id = req.get("id")

        if method == "initialize":
            _send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": True}},
                    "serverInfo": {
                        "name": "investing-toolkit (bootstrap)",
                        "version": _plugin_version(),
                    },
                },
            })
        elif method == "notifications/initialized":
            pass  # no response required
        elif method == "tools/list":
            _send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": _tool_schema()},
            })
        elif method == "tools/call":
            params = req.get("params", {}) or {}
            name = params.get("name")
            if name == "investing_toolkit_status":
                _send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": _status_message()}],
                    },
                })
            else:
                _send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": f"Unknown tool: {name}"},
                })
        elif req_id is not None:
            _send({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            })


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, BrokenPipeError):
        pass
