"""Tests for core.py graceful-degradation branches (Task 10).

Covers three fallback paths that trigger BEFORE or INSTEAD OF synthesis:
  Path 1 — 0 claims extracted (ranked_claims empty after rank step)
  Path 2 — all claims refuted (confirmed empty, voted non-empty)
  Path 3 — synthesis llm.complete returns None → salvage dict

RED: degradation guards not yet implemented in core.py — these must fail first.
"""
from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Re-usable mock provider helpers (minimal; not shared with test_core.py
# to satisfy skill-independence convention — each test file is self-contained)
# ---------------------------------------------------------------------------


class _LLM:
    """Schema-routed mock LLM; routes by frozenset of schema required fields.

    If a route value is a list, entries are consumed FIFO per key.
    If a route value is None, complete() returns None (simulates failure).
    """

    def __init__(self, routes: dict):
        self._routes = routes
        self._cursors: dict = {}

    async def complete(self, prompt: str, schema: dict) -> dict | None:
        key = frozenset(schema.get("required", []))
        if key not in self._routes:
            raise RuntimeError(f"_LLM: no route for required={sorted(key)}")
        route = self._routes[key]
        if route is None:
            return None
        if isinstance(route, list):
            idx = self._cursors.get(key, 0)
            if idx >= len(route):
                raise RuntimeError(
                    f"_LLM: FIFO list exhausted for {sorted(key)} (call #{idx})"
                )
            self._cursors[key] = idx + 1
            return route[idx]
        return route


class _Search:
    async def search(self, query: str) -> list[dict]:
        return []


class _Fetch:
    def __init__(self, content: str | None = None):
        self._content = content

    async def fetch(self, url: str) -> str | None:
        return self._content


# ---------------------------------------------------------------------------
# Shared schema key helper
# ---------------------------------------------------------------------------

def _key(schema: dict) -> frozenset:
    return frozenset(schema.get("required", []))


# ---------------------------------------------------------------------------
# Path-1 fixture builders
# ---------------------------------------------------------------------------

def _make_path1_llm():
    """Path 1: fetch always None → no claims extracted → ranked_claims=[].

    The scope returns 1 angle, search returns 1 URL, fetch returns None so no
    EXTRACT call is ever made, and rank_claims([]) returns [].
    No VERDICT or REPORT calls should happen.
    """
    from deep_research.schemas import SCOPE_SCHEMA, SEARCH_SCHEMA

    return _LLM({
        _key(SCOPE_SCHEMA): {
            "question": "Is the sky blue?",
            "summary": "Checking sky color.",
            "angles": [{"label": "Basic", "query": "sky color", "rationale": "core"}],
        },
        _key(SEARCH_SCHEMA): [
            {"results": [{"url": "https://sky.example.com", "title": "Sky", "relevance": "high"}]}
        ],
    })


# ---------------------------------------------------------------------------
# Path-2 fixture builders
# ---------------------------------------------------------------------------

def _make_path2_llm():
    """Path 2: all claims extracted, all claims refuted by verify.

    2 claims extracted; 6 votes (3 per claim), all refuted=True.
    confirmed=[] but voted non-empty.  Synthesis must NOT be called.
    """
    from deep_research.schemas import (
        SCOPE_SCHEMA, SEARCH_SCHEMA, EXTRACT_SCHEMA, VERDICT_SCHEMA,
    )

    refute_vote = {"refuted": True, "evidence": "Totally wrong.", "confidence": "high"}

    return _LLM({
        _key(SCOPE_SCHEMA): {
            "question": "All refuted Q",
            "summary": "Test all-refute path.",
            "angles": [{"label": "A", "query": "q", "rationale": "r"}],
        },
        _key(SEARCH_SCHEMA): [
            {"results": [
                {"url": "https://a.example.com", "title": "A", "relevance": "high"},
            ]}
        ],
        _key(EXTRACT_SCHEMA): [
            {
                "sourceQuality": "blog",
                "claims": [
                    {"claim": "The moon is cheese.", "quote": "It really is.", "importance": "central"},
                ],
            }
        ],
        _key(VERDICT_SCHEMA): [
            # 1 claim × 3 voters, all refuted
            refute_vote, refute_vote, refute_vote,
        ],
    })


# ---------------------------------------------------------------------------
# Path-3 fixture builders
# ---------------------------------------------------------------------------

def _make_path3_llm():
    """Path 3: happy-path until synthesis; synthesis returns None.

    1 claim confirmed; synthesis llm.complete returns None.
    Core must salvage and never raise.
    """
    from deep_research.schemas import (
        SCOPE_SCHEMA, SEARCH_SCHEMA, EXTRACT_SCHEMA, VERDICT_SCHEMA, REPORT_SCHEMA,
    )

    survive_vote = {"refuted": False, "evidence": "Looks good.", "confidence": "high"}

    return _LLM({
        _key(SCOPE_SCHEMA): {
            "question": "Synthesis fail Q",
            "summary": "Test synthesis-None path.",
            "angles": [{"label": "A", "query": "q", "rationale": "r"}],
        },
        _key(SEARCH_SCHEMA): [
            {"results": [
                {"url": "https://b.example.com", "title": "B", "relevance": "high"},
            ]}
        ],
        _key(EXTRACT_SCHEMA): [
            {
                "sourceQuality": "primary",
                "claims": [
                    {"claim": "Claim C3.", "quote": "Evidence.", "importance": "central"},
                ],
            }
        ],
        _key(VERDICT_SCHEMA): [
            # 1 claim × 3 voters, all survive
            survive_vote, survive_vote, survive_vote,
        ],
        # REPORT route = None → synthesis call returns None
        _key(REPORT_SCHEMA): None,
    })


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFallbackShapes:
    """Three sub-cases: each exercises one degradation branch."""

    async def test_path1_no_claims_extracted(self):
        """Path 1: 0 claims extracted → salvage dict with summary, findings=[], stats.claims=0.

        The function must NOT raise even when ranked_claims=[].
        """
        from deep_research.core import deep_research

        llm = _make_path1_llm()
        search = _Search()
        fetch = _Fetch(content=None)  # all fetches fail

        result = await deep_research(
            "Is the sky blue?", llm=llm, search=search, fetch=fetch, concurrency=1
        )

        # Must return a dict (never raise)
        assert isinstance(result, dict), "Must return dict, not raise"

        # Required top-level keys
        assert "summary" in result, "Missing 'summary'"
        assert "findings" in result, "Missing 'findings'"
        assert "refuted" in result, "Missing 'refuted'"
        assert "sources" in result, "Missing 'sources'"
        assert "stats" in result, "Missing 'stats'"

        # findings must be empty list (no confirmed claims)
        assert result["findings"] == [], f"findings must be [], got {result['findings']}"
        assert result["refuted"] == [], f"refuted must be [], got {result['refuted']}"

        # stats.claims == 0
        stats = result["stats"]
        assert stats["claimsExtracted"] == 0, (
            f"claimsExtracted must be 0, got {stats['claimsExtracted']}"
        )

        # summary must mention the failure/empty state (not a synthesis product)
        summary = result["summary"].lower()
        assert any(
            kw in summary for kw in ("no claims", "empty", "failed", "extracted", "0 ")
        ), f"summary should describe empty-claim state, got: {result['summary']!r}"

    async def test_path2_all_claims_refuted(self):
        """Path 2: verify ran, confirmed=[], voted non-empty → salvage with refuted list.

        Must NOT call synthesis LLM; summary must acknowledge refutation.
        """
        from deep_research.core import deep_research

        llm = _make_path2_llm()
        # provide a real fetch so claims are extracted
        fetch = _Fetch(content="<html>moon is cheese content</html>")
        search = _Search()

        # Override search to return the one URL we need
        class _S:
            async def search(self, query: str) -> list[dict]:
                return [{"url": "https://a.example.com", "title": "A", "relevance": "high"}]

        result = await deep_research(
            "All refuted Q", llm=llm, search=_S(), fetch=fetch, concurrency=1
        )

        assert isinstance(result, dict), "Must return dict, not raise"

        assert "summary" in result
        assert "findings" in result
        assert "refuted" in result
        assert "sources" in result
        assert "stats" in result

        # findings must be empty (nothing confirmed)
        assert result["findings"] == [], f"findings must be [], got {result['findings']}"

        # refuted must contain the killed claims
        assert len(result["refuted"]) >= 1, (
            f"refuted must contain the killed claims, got {result['refuted']}"
        )

        # summary must acknowledge refutation / inconclusive state
        summary = result["summary"].lower()
        assert any(
            kw in summary for kw in ("refut", "inconclusive", "all", "killed", "no confirmed")
        ), f"summary should describe all-refuted state, got: {result['summary']!r}"

        # stats.confirmed == 0
        assert result["stats"]["confirmed"] == 0, (
            f"stats.confirmed must be 0, got {result['stats']['confirmed']}"
        )

    async def test_path3_synthesis_returns_none(self):
        """Path 3: synthesis llm.complete returns None → salvage with surviving claims.

        Must NOT raise; findings may be [] (unmerged claims listed separately);
        summary must note synthesis was skipped/failed.
        """
        from deep_research.core import deep_research

        llm = _make_path3_llm()

        class _S:
            async def search(self, query: str) -> list[dict]:
                return [{"url": "https://b.example.com", "title": "B", "relevance": "high"}]

        fetch = _Fetch(content="<html>some content</html>")

        result = await deep_research(
            "Synthesis fail Q", llm=llm, search=_S(), fetch=fetch, concurrency=1
        )

        assert isinstance(result, dict), "Must return dict, not raise"

        assert "summary" in result
        assert "findings" in result
        assert "refuted" in result
        assert "sources" in result
        assert "stats" in result

        # summary must note synthesis failure / skipped
        summary = result["summary"].lower()
        assert any(
            kw in summary for kw in (
                "synthesis", "skipped", "failed", "unmerged", "verified claims"
            )
        ), f"summary should describe synthesis-failure state, got: {result['summary']!r}"

        # At least 1 confirmed claim survived verification
        assert result["stats"]["confirmed"] >= 1, (
            f"stats.confirmed must be >=1 (claims survived verify), got {result['stats']['confirmed']}"
        )
