"""Tests for concrete provider adapters in adapters.py.

Intent: verify that each concrete adapter
  1. is structurally an instance of its Protocol (runtime_checkable)
  2. maps canned API responses to the expected output shape
  3. raises a clear RuntimeError when a required env key is missing

All network calls are mocked — NO real API calls are made in this suite.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from deep_research.providers import FetchProvider, LLMProvider, SearchProvider


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


def test_anthropic_llm_conforms_to_llm_provider():
    """AnthropicLLM with a key present is an LLMProvider."""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        from deep_research.adapters import AnthropicLLM
        adapter = AnthropicLLM()
        assert isinstance(adapter, LLMProvider)


def test_brave_search_conforms_to_search_provider():
    """BraveSearch with a key present is a SearchProvider."""
    with patch.dict(os.environ, {"BRAVE_API_KEY": "test-key"}):
        from deep_research.adapters import BraveSearch
        adapter = BraveSearch()
        assert isinstance(adapter, SearchProvider)


def test_httpx_fetch_conforms_to_fetch_provider():
    """HttpxFetch is a FetchProvider (no key required)."""
    from deep_research.adapters import HttpxFetch
    adapter = HttpxFetch()
    assert isinstance(adapter, FetchProvider)


# ---------------------------------------------------------------------------
# AnthropicLLM.complete — maps tool-use response to expected dict
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_anthropic_llm_complete_returns_tool_input():
    """complete() extracts the tool-use input dict from Anthropic response."""
    canned_input = {"claims": ["A is true"], "confidence": 0.9}

    # Build a fake Anthropic response object
    tool_use_block = MagicMock()
    tool_use_block.type = "tool_use"
    tool_use_block.input = canned_input

    fake_response = MagicMock()
    fake_response.content = [tool_use_block]
    fake_response.stop_reason = "tool_use"

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        from deep_research.adapters import AnthropicLLM

        adapter = AnthropicLLM()
        # Patch the internal async client messages.create
        adapter._client.messages.create = AsyncMock(return_value=fake_response)

        result = await adapter.complete(
            prompt="test prompt",
            schema={"type": "object", "properties": {}},
        )

    assert result == canned_input


@pytest.mark.asyncio
async def test_anthropic_llm_complete_returns_none_on_non_tool_stop():
    """complete() returns None when stop_reason is not tool_use."""
    fake_response = MagicMock()
    fake_response.stop_reason = "end_turn"
    fake_response.content = []

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        from deep_research.adapters import AnthropicLLM

        adapter = AnthropicLLM()
        adapter._client.messages.create = AsyncMock(return_value=fake_response)

        result = await adapter.complete(
            prompt="test prompt",
            schema={"type": "object"},
        )

    assert result is None


# ---------------------------------------------------------------------------
# BraveSearch.search — maps Brave JSON body to result-dict list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_brave_search_maps_results():
    """search() maps Brave JSON web results to [{'url','title','snippet','relevance'}]."""
    brave_body = {
        "web": {
            "results": [
                {
                    "url": "https://example.com",
                    "title": "Example Title",
                    "description": "Example snippet text",
                },
                {
                    "url": "https://second.com",
                    "title": "Second Result",
                    "description": "Second snippet",
                },
            ]
        }
    }

    import httpx

    with patch.dict(os.environ, {"BRAVE_API_KEY": "brave-key"}):
        from deep_research.adapters import BraveSearch

        adapter = BraveSearch()

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = brave_body

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)

            results = await adapter.search("test query")

    assert len(results) == 2
    first = results[0]
    assert first["url"] == "https://example.com"
    assert first["title"] == "Example Title"
    assert first["snippet"] == "Example snippet text"
    assert "relevance" in first


@pytest.mark.asyncio
async def test_brave_search_returns_empty_on_http_error():
    """search() returns [] on non-200 response (graceful degradation)."""
    import httpx

    with patch.dict(os.environ, {"BRAVE_API_KEY": "brave-key"}):
        from deep_research.adapters import BraveSearch

        adapter = BraveSearch()

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 403

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)

            results = await adapter.search("test query")

    assert results == []


# ---------------------------------------------------------------------------
# HttpxFetch.fetch — returns text on 200, None on 500
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_httpx_fetch_returns_text_on_200():
    """fetch() returns response.text on HTTP 200."""
    import httpx

    from deep_research.adapters import HttpxFetch

    adapter = HttpxFetch()

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = "<html>Hello</html>"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await adapter.fetch("https://example.com")

    assert result == "<html>Hello</html>"


@pytest.mark.asyncio
async def test_httpx_fetch_returns_none_on_500():
    """fetch() returns None on HTTP 500."""
    import httpx

    from deep_research.adapters import HttpxFetch

    adapter = HttpxFetch()

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 500

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await adapter.fetch("https://example.com")

    assert result is None


@pytest.mark.asyncio
async def test_httpx_fetch_returns_none_on_exception():
    """fetch() returns None when an exception occurs (e.g., timeout)."""
    import httpx

    from deep_research.adapters import HttpxFetch

    adapter = HttpxFetch()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timed out"))

        result = await adapter.fetch("https://example.com")

    assert result is None


# ---------------------------------------------------------------------------
# Debug logging on exception (observability — OWASP ASVS V16)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_anthropic_llm_complete_logs_debug_on_exception(caplog):
    """complete() emits a DEBUG log record when the Anthropic API call raises."""
    import logging
    import anthropic

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        from deep_research.adapters import AnthropicLLM

        adapter = AnthropicLLM()
        adapter._client.messages.create = AsyncMock(
            side_effect=anthropic.APIConnectionError(request=MagicMock())
        )

        with caplog.at_level(logging.DEBUG, logger="deep_research.adapters"):
            result = await adapter.complete("prompt", {"type": "object"})

    assert result is None
    assert any(r.levelno == logging.DEBUG for r in caplog.records), (
        "Expected a DEBUG log record when AnthropicLLM.complete raises"
    )


@pytest.mark.asyncio
async def test_brave_search_logs_debug_on_exception(caplog):
    """search() emits a DEBUG log record when the HTTP call raises."""
    import logging
    import httpx

    with patch.dict(os.environ, {"BRAVE_API_KEY": "brave-key"}):
        from deep_research.adapters import BraveSearch

        adapter = BraveSearch()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(
                side_effect=httpx.ConnectError("connection refused")
            )

            with caplog.at_level(logging.DEBUG, logger="deep_research.adapters"):
                results = await adapter.search("test query")

    assert results == []
    assert any(r.levelno == logging.DEBUG for r in caplog.records), (
        "Expected a DEBUG log record when BraveSearch.search raises"
    )


@pytest.mark.asyncio
async def test_httpx_fetch_logs_debug_on_exception(caplog):
    """fetch() emits a DEBUG log record when the HTTP call raises."""
    import logging
    import httpx

    from deep_research.adapters import HttpxFetch

    adapter = HttpxFetch()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(
            side_effect=httpx.TimeoutException("timed out")
        )

        with caplog.at_level(logging.DEBUG, logger="deep_research.adapters"):
            result = await adapter.fetch("https://example.com")

    assert result is None
    assert any(r.levelno == logging.DEBUG for r in caplog.records), (
        "Expected a DEBUG log record when HttpxFetch.fetch raises"
    )


# ---------------------------------------------------------------------------
# Missing env key → clear RuntimeError
# ---------------------------------------------------------------------------


def test_anthropic_llm_missing_key_raises():
    """AnthropicLLM raises RuntimeError when ANTHROPIC_API_KEY is absent."""
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    with patch.dict(os.environ, env, clear=True):
        from deep_research.adapters import AnthropicLLM
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            AnthropicLLM()


def test_brave_search_missing_key_raises():
    """BraveSearch raises RuntimeError when BRAVE_API_KEY is absent."""
    env = {k: v for k, v in os.environ.items() if k != "BRAVE_API_KEY"}
    with patch.dict(os.environ, env, clear=True):
        from deep_research.adapters import BraveSearch
        with pytest.raises(RuntimeError, match="BRAVE_API_KEY"):
            BraveSearch()
