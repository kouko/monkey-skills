"""L3 MCP stdio server entry point.

Exposes one tool: ``deep_research``.
Thin wrapper — delegates all logic to ``deep_research.core``.

Run with::

    python -m deep_research.mcp_server

or via the ``deep-research-mcp`` console script (if configured).
"""
from __future__ import annotations

import asyncio
import json
import os

import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server

from deep_research import core


# ---------------------------------------------------------------------------
# Adapter factory — isolated so tests can monkeypatch it cheaply.
# ---------------------------------------------------------------------------

def _build_adapters():
    """Build (llm, search, fetch) adapters from environment variables."""
    from deep_research.adapters import AnthropicLLM, BraveSearch, HttpxFetch

    return AnthropicLLM(), BraveSearch(), HttpxFetch()


# ---------------------------------------------------------------------------
# Server factory — separated from main() to allow test introspection.
# ---------------------------------------------------------------------------

def build_server() -> Server:
    """Construct and return the MCP Server with the deep_research tool registered.

    Grounding: Model Context Protocol (MCP) Python SDK Server + stdio_server API.
    Reference: https://github.com/modelcontextprotocol/python-sdk
    Verified: 2026-06-02
    """
    server = Server("deep-research")

    @server.list_tools()
    async def _list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="deep_research",
                description=(
                    "Deep multi-source adversarially-verified research report"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The research question to investigate.",
                        },
                        "max_fetch": {
                            "type": "integer",
                            "description": "Maximum number of sources to fetch (optional).",
                        },
                        "concurrency": {
                            "type": "integer",
                            "description": "Pipeline concurrency level (optional, default 8).",
                        },
                    },
                    "required": ["question"],
                },
            )
        ]

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        if name != "deep_research":
            raise ValueError(f"Unknown tool: {name}")

        question: str = arguments["question"]
        concurrency: int = int(arguments.get("concurrency", 8))
        max_fetch: int | None = arguments.get("max_fetch", None)
        if max_fetch is not None:
            max_fetch = int(max_fetch)

        llm, search, fetch = _build_adapters()
        report = await core.deep_research(
            question, llm, search, fetch, concurrency=concurrency, max_fetch=max_fetch
        )
        return [types.TextContent(type="text", text=json.dumps(report, ensure_ascii=False, indent=2))]

    return server


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def _run_stdio():
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        init_opts = server.create_initialization_options(
            notification_options=NotificationOptions()
        )
        await server.run(read_stream, write_stream, init_opts)


def main():
    """Run the MCP stdio server (blocking)."""
    asyncio.run(_run_stdio())


if __name__ == "__main__":
    main()
