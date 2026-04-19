#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""validate_mcp_tools.py — lint registered MCP tools for description +
schema quality.

Checks each tool exposed by `servers/mcp_server.py --self-check` + stdio
`tools/list`:
  - description present, 40-1200 chars
  - description starts with a capital letter (not "return ..." etc.)
  - inputSchema has type=object and properties dict
  - tool name is snake_case `[a-z][a-z0-9_]*`

Exits 0 if clean, 1 if any tool fails. Intended for CI (run
`uv run --script tools/validate_mcp_tools.py`).

Can be extended per v1.16.x+ as new conventions emerge.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "servers" / "mcp_server.py"

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

MIN_DESC_LEN = 40
MAX_DESC_LEN = 1200


def get_tools() -> list[dict]:
    """Spawn mcp_server.py stdio, return list of tool dicts from tools/list."""
    initialize = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "validator", "version": "0.1"},
        },
    }) + "\n"
    notified = '{"jsonrpc":"2.0","method":"notifications/initialized"}\n'
    list_req = '{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n'

    res = subprocess.run(
        ["uv", "run", "--script", str(SERVER)],
        input=initialize + notified + list_req,
        capture_output=True, text=True, timeout=120, cwd=str(ROOT),
    )
    if res.returncode != 0:
        print(f"mcp_server.py stdio failed: {res.stderr[-400:]}", file=sys.stderr)
        sys.exit(2)

    frames = [
        json.loads(ln)
        for ln in res.stdout.splitlines()
        if ln.strip().startswith("{")
    ]
    list_frames = [f for f in frames if f.get("id") == 2]
    if not list_frames:
        print("no tools/list reply", file=sys.stderr)
        sys.exit(2)
    return list_frames[0]["result"]["tools"]


def check_tool(tool: dict) -> list[str]:
    """Return a list of validation errors for a single tool (empty = OK)."""
    errors: list[str] = []
    name = tool.get("name", "")
    desc = tool.get("description", "") or ""
    schema = tool.get("inputSchema", {}) or {}

    if not NAME_RE.match(name):
        errors.append(f"name {name!r} not snake_case")

    desc_stripped = desc.strip()
    if len(desc_stripped) < MIN_DESC_LEN:
        errors.append(
            f"description too short ({len(desc_stripped)} chars, "
            f"min {MIN_DESC_LEN})"
        )
    if len(desc_stripped) > MAX_DESC_LEN:
        errors.append(
            f"description too long ({len(desc_stripped)} chars, "
            f"max {MAX_DESC_LEN})"
        )
    if desc_stripped and not desc_stripped[0].isupper():
        first = desc_stripped[:20]
        errors.append(f"description should start with capital; got {first!r}")

    if schema.get("type") != "object":
        errors.append(f"inputSchema.type must be 'object' (got {schema.get('type')!r})")
    if "properties" not in schema:
        errors.append("inputSchema.properties missing")

    return errors


def main() -> None:
    tools = get_tools()
    print(f"Checking {len(tools)} MCP tools from mcp_server.py...")
    failures = 0
    for tool in sorted(tools, key=lambda t: t.get("name", "")):
        errors = check_tool(tool)
        name = tool.get("name", "<unnamed>")
        if errors:
            failures += 1
            print(f"  ❌ {name}")
            for err in errors:
                print(f"     - {err}")
        else:
            print(f"  ✅ {name}")

    print()
    if failures:
        print(f"{failures} tool(s) failed validation.")
        sys.exit(1)
    print(f"All {len(tools)} tools pass validation.")


if __name__ == "__main__":
    main()
