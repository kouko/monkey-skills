"""Tests for the MCP stdio server entry point (mcp_server.py).

Tests skip cleanly if the mcp SDK is not installed.
No network calls — core.deep_research and all adapters are monkeypatched.
"""
import json
import pytest

mcp = pytest.importorskip("mcp")


@pytest.mark.asyncio
async def test_tool_registered(monkeypatch):
    """The server exposes exactly one tool named 'deep_research' with the
    expected description and an inputSchema that contains 'question'."""
    from deep_research import mcp_server

    server = mcp_server.build_server()

    # Trigger the list_tools handler directly.
    import mcp.types as types

    req = types.ListToolsRequest(method="tools/list")
    # Reach into request_handlers to call the registered handler.
    handler = server.request_handlers[types.ListToolsRequest]
    result = await handler(req)

    # result is a ServerResult wrapping ListToolsResult
    tools_result = result.root
    assert isinstance(tools_result, types.ListToolsResult)
    tools = tools_result.tools
    names = [t.name for t in tools]
    assert "deep_research" in names, f"Expected 'deep_research' tool, got: {names}"

    dr_tool = next(t for t in tools if t.name == "deep_research")
    assert dr_tool.description, "Tool must have a non-empty description"
    assert "question" in dr_tool.inputSchema.get(
        "properties", {}
    ), "inputSchema must contain 'question' property"


@pytest.mark.asyncio
async def test_tool_handler_returns_canned_report(monkeypatch):
    """Invoking the tool handler with monkeypatched core + adapters returns
    the canned report content as JSON text in the response."""
    import mcp.types as types
    from deep_research import mcp_server

    _CANNED = {
        "question": "test q",
        "summary": "test summary",
        "findings": [],
        "caveats": [],
        "openQuestions": [],
        "refuted": [],
        "sources": [],
        "stats": {},
    }

    # Monkeypatch core.deep_research to return canned report.
    async def _fake_deep_research(*args, **kwargs):
        return _CANNED

    monkeypatch.setattr(mcp_server.core, "deep_research", _fake_deep_research)

    # Monkeypatch adapter constructors to avoid requiring env vars.
    monkeypatch.setattr(
        mcp_server,
        "_build_adapters",
        lambda: (object(), object(), object()),
    )

    server = mcp_server.build_server()

    # Invoke the call_tool handler.
    req = types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(
            name="deep_research",
            arguments={"question": "test q"},
        ),
    )
    handler = server.request_handlers[types.CallToolRequest]
    result = await handler(req)

    call_result = result.root
    assert isinstance(call_result, types.CallToolResult)
    assert not call_result.isError, f"Expected success, got error: {call_result}"
    assert call_result.content, "Expected non-empty content"

    text_block = call_result.content[0]
    assert isinstance(text_block, types.TextContent)
    parsed = json.loads(text_block.text)
    assert parsed["question"] == "test q"
    assert parsed["summary"] == "test summary"


@pytest.mark.asyncio
async def test_unknown_tool_raises_value_error(monkeypatch):
    """The call_tool handler must raise ValueError for unknown tool names.

    WHY: The if-name-guard is the only protection against typo tool names;
    without this test the branch is invisible and could silently no-op.
    """
    import mcp.types as types
    from deep_research import mcp_server

    monkeypatch.setattr(
        mcp_server,
        "_build_adapters",
        lambda: (object(), object(), object()),
    )

    server = mcp_server.build_server()

    req = types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(
            name="nonexistent_tool",
            arguments={"question": "q"},
        ),
    )
    handler = server.request_handlers[types.CallToolRequest]

    # MCP SDK wraps handler exceptions into error results rather than
    # re-raising — check isError flag in the response.
    result = await handler(req)
    call_result = result.root
    assert call_result.isError, (
        "Calling an unknown tool name must produce an error result"
    )


@pytest.mark.asyncio
async def test_tool_handler_forwards_max_fetch_and_concurrency(monkeypatch):
    """max_fetch and concurrency from arguments must be forwarded to core.deep_research.

    WHY: Without explicit forwarding the user's budget/concurrency overrides
    are silently dropped — the advertised tool schema is a lie.
    """
    import mcp.types as types
    from unittest.mock import AsyncMock
    from deep_research import mcp_server

    _CANNED = {
        "question": "q", "summary": "s", "findings": [],
        "caveats": "", "openQuestions": [], "refuted": [], "sources": [], "stats": {},
    }

    mock_core = AsyncMock(return_value=_CANNED)
    monkeypatch.setattr(mcp_server.core, "deep_research", mock_core)
    monkeypatch.setattr(
        mcp_server,
        "_build_adapters",
        lambda: (object(), object(), object()),
    )

    server = mcp_server.build_server()

    req = types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(
            name="deep_research",
            arguments={"question": "q", "max_fetch": 3, "concurrency": 2},
        ),
    )
    handler = server.request_handlers[types.CallToolRequest]
    await handler(req)

    called_kwargs = mock_core.call_args.kwargs
    assert called_kwargs.get("max_fetch") == 3, (
        f"core.deep_research must be called with max_fetch=3, got kwargs={called_kwargs}"
    )
    assert called_kwargs.get("concurrency") == 2, (
        f"core.deep_research must be called with concurrency=2, got kwargs={called_kwargs}"
    )
