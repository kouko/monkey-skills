"""L1 orchestration: deep_research() happy-path pipeline.

Depends ONLY on deep_research pure modules + the 3 Provider Protocols.
Never import concrete adapters — that boundary is load-bearing for portability.

Pipeline shape (ported from decompiled-source.md §Pipeline shape):
  1. Scope  — 1 llm call → angles
  2. Search → dedup → Fetch — pipeline(angles, search_stage, fetch_stage)
               NO barrier; dedup mutates shared seen dict + fetch_slots.
  3. Rank   — barrier; flatten claims, rank+slice to MAX_VERIFY_CLAIMS.
  4. Verify — barrier; gather_bounded(VOTES_PER_CLAIM voters per claim).
  5. Synthesize — 1 llm call → Report dict.

Provider-feeds-LLM architecture note
--------------------------------------
The upstream CC binary ran search + fetch inside tool-equipped sub-agents
(WebSearch/WebFetch tools). This port uses explicit Provider Protocols instead:
  - search.search(query) → real results;  LLM ranks/filters them.
  - fetch.fetch(url)     → real page text; LLM extracts claims from it.
The original prompt TEXT (from prompts.py) is preserved verbatim; the
provider-fetched data is APPENDED as a data block to the same prompt.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from deep_research.dedup import filter_novel
from deep_research.pipeline import gather_bounded, pipeline
from deep_research.prompts import (
    fetch_prompt,
    scope_prompt,
    search_prompt,
    synthesis_prompt,
    verify_prompt,
)
from deep_research.providers import FetchProvider, LLMProvider, SearchProvider
from deep_research.rank import quorum_survives, rank_claims
from deep_research.schemas import (
    EXTRACT_SCHEMA,
    MAX_FETCH,
    MAX_VERIFY_CLAIMS,
    REPORT_SCHEMA,
    SCOPE_SCHEMA,
    SEARCH_SCHEMA,
    VERDICT_SCHEMA,
    VOTES_PER_CLAIM,
)


# ---------------------------------------------------------------------------
# Synthesis helpers
# ---------------------------------------------------------------------------

_CONF_RANK: dict[str, int] = {"high": 0, "medium": 1, "low": 2}


def _confirmed_block(
    ranked_claims: list[dict],
    vote_results: list[bool],
    verdicts_per_claim: list[list[dict]],
) -> str:
    """Build the confirmed-claims block for the synthesis prompt.

    Format per claim (spec §SYNTHESIS {block}):
      ### [i] {claim}
      Vote: {valid-refuted}-{refuted} · Source: {url} ({quality})
      Quote: "{quote}"
      Verifier evidence ({confidence}): {evidence}
    """
    lines: list[str] = []
    for i, (claim, survived, verdicts) in enumerate(
        zip(ranked_claims, vote_results, verdicts_per_claim)
    ):
        if not survived:
            continue
        valid = len(verdicts)
        refuted_count = sum(1 for v in verdicts if v and v.get("refuted"))
        non_refuting = [v for v in verdicts if v and not v.get("refuted")]
        best = min(
            non_refuting,
            key=lambda v: _CONF_RANK.get(v.get("confidence", "low"), 2),
            default=None,
        )
        conf = best.get("confidence", "low") if best else "low"
        evidence = best.get("evidence", "") if best else ""
        lines.append(
            f"### [{i}] {claim['claim']}\n"
            f"Vote: {valid - refuted_count}-{refuted_count} · "
            f"Source: {claim.get('sourceUrl', '')} ({claim.get('sourceQuality', '')})\n"
            f"Quote: \"{claim.get('quote', '')}\"\n"
            f"Verifier evidence ({conf}): {evidence}"
        )
    return "\n".join(lines)


def _killed_block(ranked_claims: list[dict], vote_results: list[bool]) -> str:
    """Build the refuted-claims block for the synthesis prompt."""
    lines: list[str] = ["## Refuted claims (for transparency)"]
    for claim, survived in zip(ranked_claims, vote_results):
        if not survived:
            lines.append(
                f"- \"{claim['claim']}\" "
                f"({claim.get('sourceUrl', '')})"
            )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Stage helpers extracted from deep_research() to keep it under 50 lines
# ---------------------------------------------------------------------------

async def _search_stage(
    angle: dict,
    question: str,
    search: SearchProvider,
    llm: LLMProvider,
) -> tuple[dict, list[dict]]:
    """Call search provider → LLM ranks results → return (angle, ranked_list)."""
    raw_results = await search.search(angle["query"])
    ranked = await llm.complete(
        search_prompt(angle, question)
        + "\n\n## Raw search results to rank/filter\n"
        + json.dumps(raw_results, ensure_ascii=False),
        SEARCH_SCHEMA,
    )
    results: list[dict] = (ranked or {}).get("results", [])
    return angle, results


async def _fetch_stage(
    angle_and_results: tuple[dict, list[dict]],
    question: str,
    fetch: FetchProvider,
    llm: LLMProvider,
    seen: dict[str, bool],
    fetch_slots_ref: list[int],
) -> list[dict]:
    """Dedup results, fetch novel sources, extract claims.

    filter_novel is synchronous — no await between its read and write of
    seen + fetch_slots_ref, so concurrent calls cannot race on shared state.
    """
    angle, results = angle_and_results
    novel, _dupes, _dropped, new_slots = filter_novel(results, seen, fetch_slots_ref[0])
    fetch_slots_ref[0] = new_slots

    extracted: list[dict] = []
    for source in novel:
        page_text = await fetch.fetch(source["url"])
        if page_text is None:
            continue
        extract_result = await llm.complete(
            fetch_prompt(source, angle.get("label", ""), question)
            + "\n\n## Page content extracted\n"
            + page_text,
            EXTRACT_SCHEMA,
        )
        if extract_result is None:
            continue
        source_quality = extract_result.get("sourceQuality", "unreliable")
        for raw_claim in extract_result.get("claims", []):
            extracted.append(
                {**raw_claim, "sourceUrl": source["url"], "sourceQuality": source_quality}
            )
    return extracted


async def _run_search_fetch(
    question: str,
    angles: list[dict],
    search: SearchProvider,
    fetch: FetchProvider,
    llm: LLMProvider,
    concurrency: int,
    fetch_budget: int,
) -> list[dict]:
    """Stages 2a-2c: search → dedup → fetch → extract claims for all angles."""
    seen: dict[str, bool] = {}
    fetch_slots_ref: list[int] = [fetch_budget]

    async def _search(angle: dict) -> tuple[dict, list[dict]]:
        return await _search_stage(angle, question, search, llm)

    async def _fetch(angle_and_results: tuple[dict, list[dict]]) -> list[dict]:
        return await _fetch_stage(angle_and_results, question, fetch, llm, seen, fetch_slots_ref)

    angle_claim_lists: list[Any] = await pipeline(
        angles, _search, _fetch, concurrency=concurrency
    )
    all_claims: list[dict] = []
    for slot in angle_claim_lists:
        if isinstance(slot, list):
            all_claims.extend(slot)
    return all_claims


async def _verify_all(
    question: str,
    ranked_claims: list[dict],
    llm: LLMProvider,
    concurrency: int,
) -> tuple[list[bool], list[list[dict]]]:
    """Stage 4: gather VOTES_PER_CLAIM voters per claim.

    Returns (survived_flags, verdicts_per_claim) where verdicts_per_claim[i]
    is the list of raw verdict dicts for ranked_claims[i].
    """

    async def vote(claim: dict, voter_idx: int) -> dict | None:
        return await llm.complete(
            verify_prompt(claim, voter_idx, question), VERDICT_SCHEMA
        )

    all_thunks = [
        (lambda c=claim, v=vi: vote(c, v))
        for claim in ranked_claims
        for vi in range(VOTES_PER_CLAIM)
    ]
    flat_verdicts = await gather_bounded(all_thunks, concurrency=concurrency)

    survived: list[bool] = []
    verdicts_per_claim: list[list[dict]] = []
    for i in range(len(ranked_claims)):
        start = i * VOTES_PER_CLAIM
        group = flat_verdicts[start : start + VOTES_PER_CLAIM]
        verdicts_per_claim.append([v for v in group if v is not None])
        survived.append(quorum_survives(group))
    return survived, verdicts_per_claim


# ---------------------------------------------------------------------------
# Collect + stats helpers
# ---------------------------------------------------------------------------

def _collect_sources(ranked_claims: list[dict]) -> list[str]:
    """Return unique source URLs in ranked-claim insertion order."""
    sources: list[str] = []
    seen_sources: set[str] = set()
    for claim in ranked_claims:
        url = claim.get("sourceUrl", "")
        if url and url not in seen_sources:
            sources.append(url)
            seen_sources.add(url)
    return sources


def _build_stats(
    angles: list[dict],
    sources: list[str],
    all_claims: list[dict],
    ranked_claims: list[dict],
    confirmed: list[dict],
    killed: list[dict],
) -> dict[str, int]:
    """Compute pipeline stats dict. agentCalls formula: 1+angles+sources+(verified×VOTES)+1."""
    n_verified = len(ranked_claims)
    return {
        "angles": len(angles),
        "sourcesFetched": len(sources),
        "claimsExtracted": len(all_claims),
        "claimsVerified": n_verified,
        "confirmed": len(confirmed),
        "killed": len(killed),
        "agentCalls": 1 + len(angles) + len(sources) + (n_verified * VOTES_PER_CLAIM) + 1,
    }


# ---------------------------------------------------------------------------
# Degradation helper
# ---------------------------------------------------------------------------

def _degraded_report(
    question: str,
    summary: str,
    ranked_claims: list[dict],
    angles: list[dict],
    all_claims: list[dict],
    confirmed_claims: list[dict],
    killed_claims: list[dict],
) -> dict[str, Any]:
    """Return a salvage Report dict for any early-exit degradation path."""
    sources = _collect_sources(ranked_claims)
    stats = _build_stats(angles, sources, all_claims, ranked_claims, confirmed_claims, killed_claims)
    return {
        "question": question,
        "summary": summary,
        "findings": [],
        "refuted": killed_claims,
        "sources": sources,
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# Main coordinator — thin; delegates stages to private helpers above
# ---------------------------------------------------------------------------

async def deep_research(
    question: str,
    llm: LLMProvider,
    search: SearchProvider,
    fetch: FetchProvider,
    *,
    concurrency: int = 8,
    max_fetch: int | None = None,
) -> dict[str, Any]:
    """Run the 5-stage deep-research pipeline; return a Report dict.

    Stages: Scope → Search/Fetch → Rank → Verify → Synthesize.
    Returns keys: question, summary, findings, caveats, openQuestions,
    refuted, sources, stats.
    """
    effective_max_fetch = max_fetch if max_fetch is not None else MAX_FETCH
    # 1. Scope
    scope_result = await llm.complete(scope_prompt(question), SCOPE_SCHEMA)
    angles: list[dict] = (scope_result or {}).get("angles", [])
    # 2. Search → dedup → fetch
    all_claims = await _run_search_fetch(question, angles, search, fetch, llm, concurrency, effective_max_fetch)
    # 3. Rank (barrier)
    ranked_claims = rank_claims(all_claims, limit=MAX_VERIFY_CLAIMS)
    # Degradation path 1: no claims extracted/ranked — return early.
    if not ranked_claims:
        return _degraded_report(question, f"No claims extracted. {len(angles)} angle(s) searched; all sources empty or failed.", [], angles, all_claims, [], [])  # noqa: E501
    # 4. Verify (barrier)
    survived_flags, verdicts_per_claim = await _verify_all(question, ranked_claims, llm, concurrency)
    confirmed_claims = [c for c, s in zip(ranked_claims, survived_flags) if s]
    killed_claims = [c for c, s in zip(ranked_claims, survived_flags) if not s]
    # Degradation path 2: all claims refuted — return early.
    if not confirmed_claims and killed_claims:
        return _degraded_report(question, f"All {len(killed_claims)} claim(s) refuted by adversarial verification. Research inconclusive.", ranked_claims, angles, all_claims, [], killed_claims)  # noqa: E501
    # 5. Synthesize (barrier)
    conf_block = _confirmed_block(ranked_claims, survived_flags, verdicts_per_claim)
    kill_block = _killed_block(ranked_claims, survived_flags)
    report: dict[str, Any] | None = await llm.complete(
        synthesis_prompt(question, conf_block, kill_block, len(confirmed_claims)),
        REPORT_SCHEMA,
    )
    # Degradation path 3: synthesis returned None — salvage confirmed claims unmerged.
    if report is None:
        return _degraded_report(question, f"Synthesis step was skipped or failed — returning {len(confirmed_claims)} verified claims unmerged.", ranked_claims, angles, all_claims, confirmed_claims, killed_claims)  # noqa: E501
    sources = _collect_sources(ranked_claims)
    stats = _build_stats(angles, sources, all_claims, ranked_claims, confirmed_claims, killed_claims)
    return {"question": question, **report, "refuted": killed_claims, "sources": sources, "stats": stats}
