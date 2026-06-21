# Brief: fact-check skill (research-toolkit)

Date: 2026-06-03 · Plugin: research-toolkit · Sibling of: deep-research
Batch: 1 of 3 (fact-check / cite-check / deep-read) — recommended build order #1 (lowest risk)

## Problem (Axis 1)

The `deep-research` skill answers an open question by manufacturing many claims
(scope → 5 angles → ≤15 fetches → 25 claims → 75 voter calls → synthesized
report). But the high-frequency real need is the inverse: **I already have ONE
specific proposition in hand and want a fast yes/no/maybe verdict with cited
evidence** — "X raised $2B in 2025", "drug Y treats Z", "framework A is faster
than B". Running the full breadth pipeline for one claim is wasteful.

JTBD: *When I have a single checkable claim, I want a lightweight adversarial
verdict (supported / refuted / inconclusive) with cited evidence, so I can
trust-or-discard it in seconds without commissioning a full research report.*

## Users (Axis 2)

Repo owner (kouko), inside any agent host with WebSearch/WebFetch. Job story:
*When I'm mid-conversation and a factual claim needs checking, I invoke
`fact-check "<claim>"`, so the agent gathers a little evidence and runs the
same adversarial quorum deep-research uses — returning a verdict, not a report.*

## Smallest End State (Axis 3)

A `research-toolkit/skills/fact-check/` skill (SKILL.md + minimal `scripts/`)
that, given one claim, runs a 3-stage flow and returns
`{verdict, confidence, evidence, sources, counterSources}`:

- **Stage A — Gather evidence**: 1-2 WebSearch queries (confirming +
  disconfirming) → small fetch budget (≈4-6 sources) → per-source WebFetch +
  extract a supporting/contradicting quote.
- **Stage B — Adversarial verify** (UNCHANGED from deep-research): 3 skeptic
  voters via `verify_prompt`, each emitting `VERDICT_SCHEMA`.
- **Stage C — Verdict**: `quorum_survives` → map to the 3-way taxonomy
  (supported / refuted / inconclusive), handling all-abstain / no-evidence.

## Current State Evidence

- **Forward / Reuse (deep-research primitives, near-direct)**:
  `research-toolkit/skills/deep-research/scripts/prompts.py:98` (`verify_prompt`),
  `scripts/rank.py:58` (`quorum_survives`) + `:85` (`rank.py quorum` CLI),
  `scripts/schemas.py:93` (`VERDICT_SCHEMA`), `:18-19`
  (`VOTES_PER_CLAIM=3` / `REFUTATIONS_REQUIRED=2`). Evidence-gathering reuses
  `search_prompt`/`SEARCH_SCHEMA`/`dedup.py`/`fetch_prompt`/`EXTRACT_SCHEMA`.
- **NOT reused**: `scope_prompt`/`SCOPE_SCHEMA` (no angle decomposition — the
  claim is the scope); `rank_claims`/`MAX_VERIFY_CLAIMS` (one claim, nothing to
  rank); `synthesis.py` (single verdict, not a merged report).
- **Genuinely new (small)**: a claim→evidence search framing (confirming +
  disconfirming), and a 3-way verdict mapper (~10 lines) — deep-research only
  has binary survive/kill + an "all-refuted" degradation note; fact-check needs
  `inconclusive` as a first-class verdict.
- **Boundary vs deep-research**: same verify engine, different front end — no
  scope/angle fan-out, no synthesis tail.

## Decision

Build `fact-check` as a sibling skill that reuses deep-research's verify+quorum
engine wholesale, adds a minimal evidence-gathering head and a 3-way verdict
mapper. Per repo convention (每個 skill 自包含), reused scripts are
functional-copied into fact-check's `scripts/` (accept drift over cross-skill
import coupling) — confirm at plan time. Agent supplies LLM + WebSearch +
WebFetch; no API key.

NOT building: angle decomposition, claim ranking, multi-finding synthesis,
claim decomposition of compound inputs (assume one atomic proposition; flag
multi-claim input back to the user).

## Alternatives Considered (Axis 4 — research-grounded)

Automated fact-checking is a canonical pipeline: decompose → query-generation →
evidence-retrieval → **stance/verdict**. Sources (EN): arXiv 2407.02351
(survey — NLI entailment/contradiction/neutral ↔ supported/refuted/inconclusive),
2506.17878 (multi-agent FC), 2510.01226 (ClaimCheck stepwise). (JA): NABLAS
LLMファクトチェッカー (decompose→evidence→match→verdict), Waterloo stance-detection.
The adversarial 3-voter quorum is our distinctive flavor of the standard
stance/verdict stage; the retrieve-then-verify backbone is industry-canonical.
**Alternative rejected**: voter-only (no Stage A) — each voter self-searches;
near-zero new code but no shared evidence pool / anchored quotes. Kept Stage A
minimal (≤6 sources) because every industry pipeline has an explicit
evidence-retrieval stage.

## Open Questions

- OQ1: Does Stage A earn its place vs voter-only self-search? (lean: keep, minimal.)
- OQ2: Exact `inconclusive` conditions (all-abstain / 0 evidence / split / low-quality-only).
- OQ3: Functional-copy reused scripts vs shared module (lean: copy, per sister-skill independence convention).
- OQ4: Keep `VOTES_PER_CLAIM=3` (already the lightweight number) — lean yes.

## Out of Scope

- Compound/multi-claim decomposition; checkworthiness scoring.
- Full report synthesis; angle decomposition.
- Domain-specific verification (investing/legal toolkits own those).
- Auditing an existing document's citations (that is the sibling `cite-check`).
