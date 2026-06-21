# Brief: cite-check skill (research-toolkit)

Date: 2026-06-03 · Plugin: research-toolkit · Sibling of: deep-research
Batch: 2 of 3 (fact-check / cite-check / deep-read) — recommended build order #2 (highest value)

## Problem (Axis 1)

I often hold a document I did NOT write — a research report, an LLM answer, an
article — that makes claims and cites sources. The dangerous failure is the
**post-rationalized citation**: a source that superficially matches but does
not actually support the claim (literature reports up to ~57% of RAG citations
are post-rationalized). `deep-research` only ever verifies claims **it
generated** against sources **it fetched**; it never audits a foreign document.

JTBD: *When I have a cited document I didn't produce, I want to audit each cited
claim by fetching the source and confirming it actually supports the claim, so
I can flag unsupported / misattributed / hallucinated / dead-link citations
before I trust or ship it.*

## Users (Axis 2)

Repo owner (kouko). Job story: *When I receive a report or LLM output with
inline links / footnotes, I run `cite-check <doc>`, so the agent parses out
each (claim, cited-source) pair, fetches the source, and tells me per-citation
whether the source supports the claim — supported / partial / unsupported /
misattributed / unresolvable / unsourced.*

## Smallest End State (Axis 3)

A `research-toolkit/skills/cite-check/` skill that audits a markdown document:

- **Stage 1 — Parse (NEW)**: doc → list of `{claim, citedUrl|citedRef, locator,
  claimType}`. Deterministic pre-extractor (`parse_doc.py`: regex for
  `[text](url)`, `[^n]`/`[n]` + reference-list resolution) + an LLM binding
  pass (new prompt + `EXTRACT_CITED_CLAIMS` schema). Unsourced claims flagged,
  not audited.
- **Stage 2 — Fetch source (REUSE)**: per distinct citedUrl, `fetch_prompt` +
  `EXTRACT_SCHEMA` capture what the source actually says (+ quality tag); dedup
  URLs via `norm_url`; dead/paywalled → `unresolvable`.
- **Stage 3 — Support-verdict (REUSE, reframed)**: per (claim, source), a
  support-focused `verify_prompt` variant whose primary check is "does THIS
  cited source support the claim?" → 3-way scale (supported / partial /
  unsupported) + `misattributed` / `unresolvable` flags. Optional 3-voter
  quorum for high-stakes audits.
- **Stage 4 — Audit report (mostly NEW renderer)**: per-citation verdict table
  + summary counts.

## Current State Evidence

- **Forward / Reuse (~70% of machinery)**:
  `research-toolkit/skills/deep-research/scripts/prompts.py:66` (`fetch_prompt`)
  + `:98` (`verify_prompt` — checklist item #1 "claim actually supported by the
  quote?" is the load-bearing reuse), `scripts/schemas.py:71` (`EXTRACT_SCHEMA`)
  + `:93` (`VERDICT_SCHEMA`), `scripts/rank.py:58` (`quorum_survives`, all-abstain
  guard valuable for dead links), `scripts/dedup.py` (`norm_url`/`filter_novel`).
- **Genuinely NEW (the real surface)**: doc → (claim, cited-URL) **parsing** —
  no deep-research primitive does this (deep-research generates pairs; cite-check
  must extract them from an existing doc). Needs `parse_doc.py` (deterministic
  link/footnote pre-extract) + a new binding prompt + `EXTRACT_CITED_CLAIMS`
  schema + a 3-way `SUPPORT_VERDICT` schema + an audit-report renderer.
- **Boundary vs deep-research**: deep-research verifies claims it produced
  against sources it fetched (open contradiction-hunt: "is this true?");
  cite-check verifies claims+citations in a doc it did NOT produce (closed to
  the given URL first: "does THIS source support it?"). No other repo skill
  touches citation auditing.

## Decision

Build `cite-check` as the highest-value sibling: a foreign-document citation
auditor. Reuse deep-research's fetch/extract + verify + quorum + dedup; add the
new doc-parsing front-end and a 3-way support verdict. v1 audits markdown
(inline links first, footnotes second). Correctness-only (does the cited source
support the claim); true faithfulness (did the author rely on it) is unknowable
for a foreign doc → explicitly out of scope. Agent supplies LLM + WebFetch; no
API key.

## Alternatives Considered (Axis 4 — research-grounded)

This is a named, active research area — strong validation. Sources (EN):
arXiv 2412.18004 ("Correctness is not Faithfulness in RAG Attributions" — the
57% post-rationalization figure), 2602.23452 (CiteAudit — a multi-agent pipeline
that independently arrives at our exact stage flow: claim extraction → evidence
retrieval → passage matching → judgment), 2604.03173 (reference-hallucination
detection naming deep-research agents as the audit target), 2601.05866 (FACTUM —
"partial support" is the hardest regime). (JA): Scite (支持/反論/言及 3-way
taxonomy — mirror it), Trinka/Letterpress citation checkers (DOI resolution as a
separate productized step). **Alternative rejected**: binary supported/unsupported
verdict — the literature + Scite favor 3-way (supported/partial/unsupported)
because partial-support is both common and the hardest case.

## Open Questions

- OQ1: Verdict scale — 3-way (recommended, per Scite + FACTUM) vs binary.
- OQ2: Claim–citation binding — deterministic pre-extract + LLM bind (recommended); how to represent "one cite backs a whole paragraph".
- OQ3: Non-URL references — flag-and-skip v1, or attempt DOI/title resolution (defer — whole sub-system).
- OQ4: Quorum default — single-voter (citation-support is more deterministic) with quorum opt-in?
- OQ5: Unsourced claims — report as a separate class, don't hunt (scope-creep guard).

## Out of Scope

- True faithfulness (author-reliance) — unknowable for a foreign doc.
- DOI/CrossRef resolution of citation strings (v2+).
- PDF / HTML input (markdown first).
- Generating citations or fixing the document (audit-only, read-only verdict).
