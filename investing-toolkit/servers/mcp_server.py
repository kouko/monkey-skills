#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp[cli]>=1.2",
#   "requests==2.33.1",
#   "yfinance==1.3.0",
#   "pandas==3.0.2",
#   "curl_cffi>=0.15",
#   "akshare==1.18.55",
#   "xlrd>=2",
# ]
# ///
"""
mcp_server.py — investing-toolkit MCP server entry point (v1.14.0+).

Imports all 8 client modules from ../scripts/ and wires each module's
register_mcp_tools() into a single FastMCP instance. Claude Code /
Claude Cowork spawns one of these processes per plugin activation;
stdio transport by default.

Invocation:
  # Normal: start MCP server (stdio)
  uv run --script servers/mcp_server.py

  # Pre-warm uv cache + resolve deps without entering MCP loop
  uv run --script servers/mcp_server.py --self-check
  # → prints {"ok": true, "version": "1.14.0", "tools": N} and exits.

See docs/mcp-setup.md for install paths and troubleshooting.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

VERSION = "1.14.0"

# Resolve plugin root. Normally Claude sets CLAUDE_PLUGIN_ROOT; fall back
# to __file__ location for direct invocation / testing.
_here = Path(__file__).resolve().parent
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or _here.parent)
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"

if not SCRIPTS_DIR.exists():
    print(
        json.dumps({
            "error": f"scripts/ directory not found at {SCRIPTS_DIR}",
            "hint": "Set CLAUDE_PLUGIN_ROOT to the investing-toolkit plugin root.",
        }),
        file=sys.stderr,
    )
    sys.exit(2)

sys.path.insert(0, str(SCRIPTS_DIR))


def _import_clients():
    """Import all 8 client modules. Returns list of (name, module)."""
    import akshare_client
    import finmind_client
    import fred_client
    import mops_client
    import nbs_client
    import sec_edgar_client
    import twse_openapi_client
    import yfinance_client

    return [
        ("yfinance", yfinance_client),
        ("akshare", akshare_client),
        ("nbs", nbs_client),
        ("fred", fred_client),
        ("sec_edgar", sec_edgar_client),
        ("mops", mops_client),
        ("twse_openapi", twse_openapi_client),
        ("finmind", finmind_client),
    ]


def _self_check() -> None:
    """Pre-warm mode: resolve + import everything, report tool count, exit."""
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as e:  # pragma: no cover
        print(json.dumps({"ok": False, "error": f"mcp import failed: {e}"}))
        sys.exit(1)

    clients = _import_clients()
    mcp = FastMCP("investing-toolkit")
    for _, mod in clients:
        mod.register_mcp_tools(mcp)

    # FastMCP exposes tools via internal registry; count via list_tools() coroutine
    # is async — we just report known counts statically for self-check speed.
    tool_counts = {
        "yfinance": 3, "akshare": 1, "nbs": 1, "fred": 1,
        "sec_edgar": 4, "mops": 1, "twse_openapi": 1, "finmind": 1,
    }
    total = sum(tool_counts.values())
    print(json.dumps({
        "ok": True,
        "version": VERSION,
        "plugin_root": str(PLUGIN_ROOT),
        "scripts_dir": str(SCRIPTS_DIR),
        "tools": total,
        "tools_per_client": tool_counts,
    }))
    sys.exit(0)


def main() -> None:
    if "--self-check" in sys.argv:
        _self_check()
        return

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("investing-toolkit")
    for _, mod in _import_clients():
        mod.register_mcp_tools(mcp)

    mcp.run()


if __name__ == "__main__":
    main()
