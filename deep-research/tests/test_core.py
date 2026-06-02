"""Tests for core.py — deep_research() orchestration happy path.

RED: core.py does not exist — this test must fail on import.
"""
import asyncio
import pytest


# ---------------------------------------------------------------------------
# Mock provider implementations
# ---------------------------------------------------------------------------

class MockLLM:
    """Schema-routed LLM mock: dispatches by JSON Schema required-fields tuple.

    Concurrent pipeline stages call complete() in non-deterministic order,
    so routing by schema (not call index) is required for correctness.

    Routing table key: frozenset of schema["required"] values.
    Value: a callable(prompt) -> dict, or a list consumed FIFO for stages
    that are called multiple times with the same schema (SEARCH, EXTRACT,
    VERDICT).
    """

    def __init__(self, routes: dict):
        """routes: {frozenset(required_fields): response_or_list}"""
        self._routes = routes
        self._cursors: dict = {}  # frozenset -> list index for FIFO lists

    async def complete(self, prompt: str, schema: dict) -> dict | None:
        key = frozenset(schema.get("required", []))
        route = self._routes.get(key)
        if route is None:
            raise RuntimeError(f"MockLLM: no route for schema required={list(key)}")
        if isinstance(route, list):
            idx = self._cursors.get(key, 0)
            if idx >= len(route):
                raise RuntimeError(
                    f"MockLLM: FIFO list exhausted for {list(key)} (call #{idx})"
                )
            self._cursors[key] = idx + 1
            return route[idx]
        # single response (returned every time)
        return route


class MockSearch:
    """Returns canned results; tracks invocations."""

    def __init__(self, results: list[dict]):
        self._results = results
        self.calls: list[str] = []  # queries received

    async def search(self, query: str) -> list[dict]:
        self.calls.append(query)
        return self._results


class MockFetch:
    """Returns a canned HTML string; tracks invocations."""

    def __init__(self, content: str | None = "<html>mock page content about caffeine</html>"):
        self._content = content
        self.calls: list[str] = []  # URLs fetched

    async def fetch(self, url: str) -> str | None:
        self.calls.append(url)
        return self._content


# ---------------------------------------------------------------------------
# Canned response fixtures
# ---------------------------------------------------------------------------

_SCOPE_RESPONSE = {
    "question": "What is the effect of caffeine on sleep?",
    "summary": "Multi-angle decomposition of caffeine–sleep relationship.",
    "angles": [
        {"label": "Primary research", "query": "caffeine sleep effects studies", "rationale": "Core science"},
        {"label": "Mechanisms", "query": "caffeine adenosine receptor sleep mechanism", "rationale": "Biology"},
        {"label": "Practical", "query": "caffeine timing sleep quality recommendations", "rationale": "Guidance"},
    ],
}

_SEARCH_RESULT_ROWS = [
    {"url": "https://example.com/study1", "title": "Caffeine Study 1", "relevance": "high", "snippet": "Key finding"},
    {"url": "https://example.com/study2", "title": "Caffeine Study 2", "relevance": "high", "snippet": "Another finding"},
]

_SEARCH_RESPONSE_A = {
    "results": _SEARCH_RESULT_ROWS,
}

# All three angles return the SAME two URLs — dedup should collapse to 2 unique
# fetches (budget = MAX_FETCH=15, so no budget drop).

# Two extract responses (one per unique URL)
_EXTRACT_RESPONSE_CONFIRMED = {
    "sourceQuality": "primary",
    "publishDate": "2024-01-01",
    "claims": [
        {
            "claim": "Caffeine delays sleep onset by 30-60 minutes.",
            "quote": "Our study found caffeine ingestion delayed sleep onset significantly.",
            "importance": "central",
        }
    ],
}

_EXTRACT_RESPONSE_KILLED = {
    "sourceQuality": "blog",
    "publishDate": "2023-06-15",
    "claims": [
        {
            "claim": "One cup of coffee has no effect on sleep.",
            "quote": "Many people drink coffee all day with no issue.",
            "importance": "supporting",
        }
    ],
}

# Verdict responses for the 2 claims × 3 voters each = 6 verdicts total.
# Claim 1 (confirmed): 0 refuted → survives (0 < REFUTATIONS_REQUIRED=2, valid=3 >= 2)
_VERDICT_SURVIVE = {"refuted": False, "evidence": "Consistent with known pharmacology.", "confidence": "high"}
# Claim 2 (killed): 2 refuted → killed (refuted=2 >= REFUTATIONS_REQUIRED=2)
_VERDICT_REFUTE = {"refuted": True, "evidence": "Contradicted by multiple primary sources.", "confidence": "high"}

_REPORT_RESPONSE = {
    "summary": "Caffeine demonstrably delays sleep onset based on primary research.",
    "findings": [
        {
            "claim": "Caffeine delays sleep onset by 30-60 minutes.",
            "confidence": "high",
            "sources": ["https://example.com/study1"],
            "evidence": "Multiple primary studies confirm this.",
        }
    ],
    "caveats": "Individual variation not accounted for.",
    "openQuestions": ["Does decaf have any effect?"],
}


# ---------------------------------------------------------------------------
# Build schema-routed MockLLM
# ---------------------------------------------------------------------------

def _build_mock_llm() -> "MockLLM":
    """Build a MockLLM routed by JSON Schema required-fields.

    Concurrent pipeline stages call complete() with the same schema type
    in non-deterministic order, so routing by schema key is required.

    SCOPE  required=["question","angles","summary"]
    SEARCH required=["results"]
    EXTRACT required=["claims","sourceQuality"]
    VERDICT required=["refuted","evidence","confidence"]
    REPORT  required=["summary","findings","caveats"]

    SEARCH: 3 calls (one per angle), all return same search results.
    EXTRACT: 2 calls — study1 (primary/confirmed), study2 (blog/killed).
             Angles 1+2 see same URLs → already in seen → 0 novel → 0 calls.
    VERDICT: 6 calls (2 claims × 3 voters).
             Claim 0: 3× survive → quorum passes.
             Claim 1: 2× refute + 1× survive → quorum fails (killed).
             FIFO order: survive, survive, survive, refute, refute, survive.
             gather_bounded preserves claim order but votes within a claim
             may interleave with votes of another — use survive/refute
             pattern that kills claim 1 regardless of interleaving:
             we need ≥2 refutations for claim 1 and 0 for claim 0.
             Since verdicts are grouped by claim index AFTER gather_bounded,
             we emit 3 survives then 3 (refute,refute,survive) — that works
             as long as the FIFO respects claim 0 before claim 1, which
             gather_bounded guarantees (indices 0..2 for claim 0, 3..5 for
             claim 1 in the flat thunks list).
    """
    from deep_research.schemas import (
        SCOPE_SCHEMA, SEARCH_SCHEMA, EXTRACT_SCHEMA, VERDICT_SCHEMA, REPORT_SCHEMA,
    )

    def _key(schema: dict) -> frozenset:
        return frozenset(schema.get("required", []))

    routes = {
        _key(SCOPE_SCHEMA): _SCOPE_RESPONSE,
        _key(SEARCH_SCHEMA): [
            _SEARCH_RESPONSE_A,   # angle 0
            _SEARCH_RESPONSE_A,   # angle 1 (same URLs → deduped)
            _SEARCH_RESPONSE_A,   # angle 2 (same URLs → deduped)
        ],
        _key(EXTRACT_SCHEMA): [
            _EXTRACT_RESPONSE_CONFIRMED,   # study1 → claim survives
            _EXTRACT_RESPONSE_KILLED,      # study2 → claim killed
        ],
        _key(VERDICT_SCHEMA): [
            # claim 0 voters 0,1,2 — all survive
            _VERDICT_SURVIVE, _VERDICT_SURVIVE, _VERDICT_SURVIVE,
            # claim 1 voters 0,1,2 — 2 refutations → killed
            _VERDICT_REFUTE, _VERDICT_REFUTE, _VERDICT_SURVIVE,
        ],
        _key(REPORT_SCHEMA): _REPORT_RESPONSE,
    }
    return MockLLM(routes)


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

class TestEndToEndMocked:
    async def test_end_to_end_mocked(self):
        """Happy-path integration: scripted mocks, assert all pipeline invariants."""
        from deep_research.core import deep_research

        llm = _build_mock_llm()
        search = MockSearch(_SEARCH_RESULT_ROWS)
        fetch = MockFetch()

        result = await deep_research(
            "What is the effect of caffeine on sleep?",
            llm=llm,
            search=search,
            fetch=fetch,
            concurrency=4,
        )

        # --- structural shape ---
        assert isinstance(result, dict), "deep_research must return a dict"
        assert "question" in result
        assert "summary" in result
        assert "findings" in result
        assert "refuted" in result
        assert "sources" in result
        assert "stats" in result

        # --- angles decomposed ---
        stats = result["stats"]
        assert stats["angles"] == 3, f"Expected 3 angles, got {stats['angles']}"

        # --- sources deduped: 2 unique URLs across 3 angles ---
        assert stats["sourcesFetched"] == 2, (
            f"Expected 2 fetched sources (deduped), got {stats['sourcesFetched']}"
        )

        # --- claims extracted (1 per source) ---
        assert stats["claimsExtracted"] == 2, (
            f"Expected 2 extracted claims, got {stats['claimsExtracted']}"
        )

        # --- claims verified (2 ranked, 2 verified) ---
        assert stats["claimsVerified"] == 2

        # --- quorum: 1 confirmed, 1 killed ---
        assert stats["confirmed"] == 1, f"Expected 1 confirmed claim, got {stats['confirmed']}"
        assert stats["killed"] == 1, f"Expected 1 killed claim, got {stats['killed']}"

        # --- findings reflect confirmed claims ---
        findings = result["findings"]
        assert len(findings) >= 1, "Expected at least 1 finding from synthesis"

        # --- refuted list reflects killed claims ---
        refuted_list = result["refuted"]
        assert isinstance(refuted_list, list)
        assert len(refuted_list) == 1, f"Expected 1 refuted claim, got {len(refuted_list)}"
        assert "One cup of coffee" in refuted_list[0]["claim"]

        # --- sources list populated ---
        assert isinstance(result["sources"], list)
        assert len(result["sources"]) > 0

        # --- agentCalls formula: 1 + angles + sources + (verified × VOTES) + 1 ---
        # 1 + 3 + 2 + (2 × 3) + 1 = 13
        assert stats["agentCalls"] == 13, f"Expected 13 agentCalls, got {stats['agentCalls']}"

        # --- 3-vote verify ran: verified claims × VOTES_PER_CLAIM = 6 total verdict calls ---
        # Implicitly confirmed by agentCalls count above.

        # --- Gap 1: search and fetch providers MUST be invoked (not hallucinated) ---
        # 3 angles → 3 search.search() calls
        assert len(search.calls) == 3, (
            f"search.search() must be called once per angle (3), got {len(search.calls)}"
        )
        # 2 unique URLs → 2 fetch.fetch() calls (dedup collapses angles 1+2)
        assert len(fetch.calls) == 2, (
            f"fetch.fetch() must be called once per novel source (2), got {len(fetch.calls)}"
        )
        assert set(fetch.calls) == {"https://example.com/study1", "https://example.com/study2"}


class TestFetchFailDegradation:
    """Gap 1: fetch.fetch() returning None → claims:[] + sourceQuality:'unreliable'."""

    async def test_fetch_none_produces_no_claims(self):
        """When fetch returns None the source is treated as unreliable with 0 claims."""
        from deep_research.core import deep_research
        from deep_research.schemas import (
            SCOPE_SCHEMA, SEARCH_SCHEMA, EXTRACT_SCHEMA, VERDICT_SCHEMA, REPORT_SCHEMA,
        )

        def _key(schema: dict) -> frozenset:
            return frozenset(schema.get("required", []))

        # Scope with a single angle
        scope = {
            "question": "Q",
            "summary": "s",
            "angles": [{"label": "A", "query": "q", "rationale": "r"}],
        }
        empty_report = {
            "summary": "No confirmed claims.",
            "findings": [],
            "caveats": "All sources failed.",
            "openQuestions": [],
        }
        routes = {
            _key(SCOPE_SCHEMA): scope,
            _key(SEARCH_SCHEMA): [{"results": [{"url": "https://fail.example.com", "title": "Fail", "relevance": "high"}]}],
            _key(REPORT_SCHEMA): empty_report,
        }
        llm = MockLLM(routes)
        search = MockSearch([{"url": "https://fail.example.com", "title": "Fail", "relevance": "high"}])
        fetch = MockFetch(content=None)  # always fails

        result = await deep_research("Q", llm=llm, search=search, fetch=fetch, concurrency=1)

        # fetch was called for the one novel source
        assert len(fetch.calls) == 1, f"Expected 1 fetch call, got {len(fetch.calls)}"
        # no claims extracted → 0 verified claims
        assert result["stats"]["claimsExtracted"] == 0
        assert result["stats"]["claimsVerified"] == 0
        assert result["stats"]["confirmed"] == 0


class TestDeepResearchFunctionLength:
    """Gap 3: deep_research() body must be under 50 lines (house ceiling)."""

    def test_deep_research_under_50_lines(self):
        """deep_research() must be a thin coordinator — extract helpers enforce ceiling."""
        import inspect
        from deep_research.core import deep_research

        source = inspect.getsource(deep_research)
        lines = [ln for ln in source.splitlines() if ln.strip()]  # non-blank lines
        # subtract the def line itself
        body_lines = len(lines) - 1
        assert body_lines <= 50, (
            f"deep_research() body is {body_lines} non-blank lines; "
            "must be ≤50. Extract helpers to shrink it."
        )


class TestConfirmedBlockVoteAndEvidence:
    """RED: _confirmed_block must emit Vote: and Verifier evidence lines (spec §SYNTHESIS {block})."""

    def test_confirmed_block_includes_vote_and_evidence(self):
        """Confirmed-claim block must include Vote: x-y and Verifier evidence (conf): text lines.

        WHY: synthesis LLM uses vote tally + verifier evidence to assign
        per-finding confidence. Omitting these lines silently degrades the
        LLM's ability to distinguish high-signal from low-signal claims.
        """
        from deep_research.core import _confirmed_block

        claim = {
            "claim": "Caffeine delays sleep onset by 30-60 minutes.",
            "sourceUrl": "https://example.com/study1",
            "sourceQuality": "primary",
            "quote": "Our study found caffeine ingestion delayed sleep onset significantly.",
        }
        # 3 verdicts: 3 non-refuting (survive). valid=3, refuted=0 → Vote: 3-0.
        # best non-refuting verdict is confidence=high.
        verdicts_per_claim = [
            [
                {"refuted": False, "evidence": "Consistent with pharmacology.", "confidence": "high"},
                {"refuted": False, "evidence": "Backed by multiple RCTs.", "confidence": "medium"},
                {"refuted": False, "evidence": "Well-known effect.", "confidence": "low"},
            ]
        ]
        survived = [True]

        block = _confirmed_block([claim], survived, verdicts_per_claim)

        assert "Vote:" in block, "Block must contain a Vote: line"
        assert "3-0" in block, "Vote tally must be 3-0 (3 valid, 0 refuted)"
        assert "Verifier evidence (" in block, "Block must contain Verifier evidence line"
        assert "high" in block, "Best non-refuting verdict confidence (high) must appear"
        assert "Consistent with pharmacology." in block, (
            "Best non-refuting verdict evidence text must appear"
        )

    def test_confirmed_block_picks_best_non_refuting_verdict(self):
        """When some voters refute, best evidence is from highest-confidence non-refuter.

        WHY: confRank = {high:0, medium:1, low:2} — lowest confRank value = most confident.
        """
        from deep_research.core import _confirmed_block

        claim = {
            "claim": "Coffee disrupts REM sleep.",
            "sourceUrl": "https://example.com/rem",
            "sourceQuality": "secondary",
            "quote": "REM disruption observed in subjects.",
        }
        # 3 verdicts: 1 refuting, 2 non-refuting. valid=3, refuted=1 → Vote: 2-1.
        # Non-refuting verdicts have confidence medium and low; pick medium (confRank 1 < 2).
        verdicts_per_claim = [
            [
                {"refuted": True, "evidence": "No REM disruption in our study.", "confidence": "high"},
                {"refuted": False, "evidence": "Medium-confidence support.", "confidence": "medium"},
                {"refuted": False, "evidence": "Low-confidence support.", "confidence": "low"},
            ]
        ]
        survived = [True]

        block = _confirmed_block([claim], survived, verdicts_per_claim)

        assert "Vote:" in block
        assert "2-1" in block, "Vote tally must be 2-1"
        assert "Verifier evidence (medium)" in block, (
            "Best non-refuting verdict is medium confidence"
        )
        assert "Medium-confidence support." in block


class TestMaxFetchParam:
    """max_fetch parameter caps the number of sources actually fetched."""

    async def test_max_fetch_caps_sources(self):
        """Passing max_fetch=2 with 4 novel sources results in only 2 fetches.

        WHY: max_fetch is a documented override. Without a real parameter
        the override is silently dropped — the user's budget is ignored.
        """
        from deep_research.core import deep_research
        from deep_research.schemas import (
            SCOPE_SCHEMA, SEARCH_SCHEMA, EXTRACT_SCHEMA, VERDICT_SCHEMA, REPORT_SCHEMA,
        )

        def _key(schema: dict) -> frozenset:
            return frozenset(schema.get("required", []))

        # 4 distinct URLs; first 2 high-relevance, rest medium.
        # filter_novel drops medium/low when fetch_slots <= 0, so with max_fetch=2
        # only 2 sources (the high-relevance ones) should be fetched.
        search_results_4 = [
            {"url": "https://example.com/src0", "title": "Source 0", "relevance": "high"},
            {"url": "https://example.com/src1", "title": "Source 1", "relevance": "high"},
            {"url": "https://example.com/src2", "title": "Source 2", "relevance": "medium"},
            {"url": "https://example.com/src3", "title": "Source 3", "relevance": "medium"},
        ]

        extract_resp = {
            "sourceQuality": "primary",
            "publishDate": "2024-01-01",
            "claims": [{"claim": "Claim X.", "quote": "quote", "importance": "central"}],
        }
        verdict_survive = {"refuted": False, "evidence": "ok", "confidence": "high"}
        report_resp = {"summary": "s", "findings": [], "caveats": "c", "openQuestions": []}

        routes = {
            _key(SCOPE_SCHEMA): {
                "question": "Q",
                "summary": "s",
                "angles": [{"label": "A", "query": "q", "rationale": "r"}],
            },
            _key(SEARCH_SCHEMA): [{"results": search_results_4}],
            # Provide 2 extract responses — only 2 fetches should happen with max_fetch=2
            _key(EXTRACT_SCHEMA): [extract_resp, extract_resp],
            # 2 claims × 3 voters = 6 verdicts
            _key(VERDICT_SCHEMA): [verdict_survive] * 6,
            _key(REPORT_SCHEMA): report_resp,
        }

        class _LLM:
            def __init__(self, routes):
                self._routes = routes
                self._cursors = {}

            async def complete(self, prompt, schema):
                key = frozenset(schema.get("required", []))
                route = self._routes.get(key)
                if isinstance(route, list):
                    idx = self._cursors.get(key, 0)
                    self._cursors[key] = idx + 1
                    return route[idx]
                return route

        search = MockSearch(search_results_4)
        fetch = MockFetch()

        result = await deep_research(
            "Q",
            llm=_LLM(routes),
            search=search,
            fetch=fetch,
            concurrency=1,
            max_fetch=2,  # budget: only 2 of 4 sources
        )

        assert len(fetch.calls) == 2, (
            f"max_fetch=2 must cap fetch invocations at 2, got {len(fetch.calls)}"
        )
