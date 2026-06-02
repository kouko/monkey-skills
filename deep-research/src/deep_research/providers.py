"""Provider Protocols for deep-research core.

All three Protocols are decorated ``@runtime_checkable`` so that mock and
concrete implementations can be validated structurally via ``isinstance``
without importing concrete provider code into ``core``.  This is the
boundary that makes L1 the portability line: ``core`` depends ONLY on these
Protocols — never on a concrete provider.

Null-on-skip contract (LLMProvider)
-------------------------------------
``complete()`` returns ``None`` when the call is skipped or the provider is
unavailable.  ``core`` treats ``None`` as "drop this agent vote" during
quorum counting (``valid >= 2 and refuted < 2`` per the CC binary constants).
Concrete implementations MUST return ``None`` rather than raising for
transient/intentional non-availability, so that quorum degradation works
correctly without try/except scattered through orchestration code.

Structured-output contract (LLMProvider)
------------------------------------------
``complete()`` accepts a ``schema`` dict (a JSON Schema object) and MUST
return a dict that validates against it, or ``None``.  The five schemas
extracted verbatim from the CC binary live in ``deep_research/schemas/`` and
are passed in by the orchestration layer; adapters are responsible for
instructing their underlying LLM to produce conforming output.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Async LLM completion with structured output.

    Parameters
    ----------
    prompt:
        The full prompt text to send to the model.
    schema:
        A JSON Schema dict describing the expected response shape.
        Adapters MUST instruct the underlying model to conform.

    Returns
    -------
    dict | None
        A dict validated against ``schema``, or ``None`` when the call is
        skipped or the provider is unavailable (null-on-skip contract).
        Returning ``None`` causes the orchestrator to treat this agent vote
        as an abstention, preserving quorum arithmetic.
    """

    async def complete(self, prompt: str, schema: dict) -> dict | None:
        ...


@runtime_checkable
class SearchProvider(Protocol):
    """Async web / knowledge-base search.

    Parameters
    ----------
    query:
        The search query string.

    Returns
    -------
    list[dict]
        Zero or more result dicts.  Each dict SHOULD contain at minimum
        ``title``, ``url``, and ``snippet`` keys, matching the shape expected
        by the source-deduplication and fetch stages.  Empty list on failure
        (never raise for search errors — return [] to degrade gracefully).
    """

    async def search(self, query: str) -> list[dict]:
        ...


@runtime_checkable
class FetchProvider(Protocol):
    """Async URL fetcher.

    Parameters
    ----------
    url:
        The URL to retrieve.

    Returns
    -------
    str | None
        The page text (HTML or plain text), or ``None`` on any fetch failure
        (network error, timeout, non-200 status).  Returning ``None`` causes
        the orchestrator to mark the source with
        ``sourceQuality: "unreliable"`` and ``claims: []``, matching the
        original CC binary's error-degradation behaviour.
    """

    async def fetch(self, url: str) -> str | None:
        ...
