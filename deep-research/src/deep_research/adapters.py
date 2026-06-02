"""Concrete provider adapters for deep-research.

These are the ONLY files that may import third-party SDKs (anthropic / httpx).
All other deep_research modules depend only on the three Protocols in providers.py.

Missing required env key
------------------------
- AnthropicLLM: raises RuntimeError at construction if ANTHROPIC_API_KEY is absent.
- BraveSearch:  raises RuntimeError at construction if BRAVE_API_KEY is absent.
- HttpxFetch:   no key required; never raises at construction.
"""

import logging
import os

import anthropic
import httpx

logger = logging.getLogger(__name__)


_BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
_HTTPX_TIMEOUT = 15.0
_HTTPX_UA = "deep-research/0.1 (https://github.com/kouko/monkey-skills)"


class AnthropicLLM:
    """LLMProvider backed by the Anthropic Messages API.

    Structured output is enforced via a single tool whose ``input_schema``
    is set to ``schema`` and ``tool_choice={"type":"tool","name":"output"}``.
    On success, returns the ``input`` dict from the tool-use block.
    Returns ``None`` when the response stop_reason is not ``"tool_use"``
    or on any exception (null-on-skip contract).

    Parameters
    ----------
    model:
        Anthropic model identifier.  Defaults to ``claude-sonnet-4-5``.
    """

    _TOOL_NAME = "output"

    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Export it before constructing AnthropicLLM."
            )
        self._model = model
        self._client = anthropic.AsyncAnthropic(api_key=key)

    async def complete(self, prompt: str, schema: dict) -> dict | None:
        """Call the Anthropic API and return the structured tool-use input dict.

        Grounding: Anthropic Messages API tool-use with forced tool-choice.
        Reference: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
        Verified: 2026-06-02
        """
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                tools=[
                    {
                        "name": self._TOOL_NAME,
                        "description": "Structured output conforming to the provided schema.",
                        "input_schema": schema,
                    }
                ],
                tool_choice={"type": "tool", "name": self._TOOL_NAME},
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIError:
            # anthropic.APIError is the base for all SDK errors (auth 401, rate-limit 429,
            # connection errors, etc.).
            # Reference: https://github.com/anthropics/anthropic-sdk-python#error-handling
            # Verified: 2026-06-02
            logger.debug("AnthropicLLM.complete failed", exc_info=True)
            return None
        except Exception:
            # Residual catch for unexpected non-SDK Exceptions. Note: BaseException
            # (incl. asyncio.CancelledError, KeyboardInterrupt) is intentionally NOT
            # caught here, so cancellation/interrupts still propagate.
            logger.debug("AnthropicLLM.complete unexpected error", exc_info=True)
            return None

        if response.stop_reason != "tool_use":
            return None

        for block in response.content:
            if getattr(block, "type", None) == "tool_use":
                return block.input  # type: ignore[return-value]

        return None


class BraveSearch:
    """SearchProvider backed by the Brave Search API.

    Result relevance heuristic: first result → "high", second → "medium",
    remainder → "low".  This is a simple rank-based approximation.

    Parameters
    ----------
    count:
        Maximum number of results to request from Brave (default 10).
    """

    _RELEVANCE = ["high", "medium"] + ["low"] * 100  # rank → relevance

    def __init__(self, count: int = 10) -> None:
        key = os.environ.get("BRAVE_API_KEY")
        if not key:
            raise RuntimeError(
                "BRAVE_API_KEY environment variable is not set. "
                "Export it before constructing BraveSearch."
            )
        self._key = key
        self._count = count

    async def search(self, query: str) -> list[dict]:
        """GET Brave web search results; returns [] on any failure.

        Grounding: Brave Web Search API response structure (web.results[] array).
        Reference: https://api-dashboard.search.brave.com/app/documentation/web-search/get-started
        Verified: 2026-06-02
        """
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self._key,
        }
        params = {"q": query, "count": self._count}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    _BRAVE_SEARCH_URL, headers=headers, params=params
                )
        except httpx.HTTPError:
            # httpx.HTTPError is the base for all httpx errors (RequestError,
            # TransportError, TimeoutException, ConnectError, etc.).
            # Reference: https://www.python-httpx.org/exceptions/
            # Verified: 2026-06-02
            logger.debug("BraveSearch.search failed", exc_info=True)
            return []
        except Exception:
            # Catch unexpected non-httpx exceptions.
            logger.debug("BraveSearch.search unexpected error", exc_info=True)
            return []

        if response.status_code != 200:
            return []

        body = response.json()
        raw_results = body.get("web", {}).get("results", [])

        return [
            {
                "url": r.get("url", ""),
                "title": r.get("title", ""),
                "snippet": r.get("description", ""),
                "relevance": self._RELEVANCE[i] if i < len(self._RELEVANCE) else "low",
            }
            for i, r in enumerate(raw_results)
        ]


class HttpxFetch:
    """FetchProvider that GETs a URL with httpx.

    Returns ``response.text`` on HTTP 200, ``None`` on any non-200 status
    or any exception (including timeouts).  No API key required.
    """

    def __init__(self) -> None:
        pass

    async def fetch(self, url: str) -> str | None:
        """Fetch ``url`` and return its text, or None on failure."""
        headers = {"User-Agent": _HTTPX_UA}
        try:
            async with httpx.AsyncClient(timeout=_HTTPX_TIMEOUT) as client:
                response = await client.get(url, headers=headers)
        except httpx.HTTPError:
            # httpx.HTTPError is the base for all httpx errors (RequestError,
            # TransportError, TimeoutException, ConnectError, etc.).
            # Reference: https://www.python-httpx.org/exceptions/
            # Verified: 2026-06-02
            logger.debug("HttpxFetch.fetch failed", exc_info=True)
            return None
        except Exception:
            # Catch unexpected non-httpx exceptions.
            logger.debug("HttpxFetch.fetch unexpected error", exc_info=True)
            return None

        if response.status_code != 200:
            return None

        return response.text
