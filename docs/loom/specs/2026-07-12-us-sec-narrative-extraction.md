# Brief — US SEC primary-source data layer (narrative + tables + operational-KPI time-series)

**Date**: 2026-07-12
**Stage**: brainstorming → loom-spec (requirement fan-out; scope exceeds a single brief)
**Design-side on-ramp**: N/A — brownfield increment to an existing toolkit (Axis 0 negative guard). No PRINCIPLES.md in repo.
**Scope note**: This started as "extract 10-K/10-Q/8-K narrative text" and, through this session's research + user direction, graduated into **building toward a general operational-KPI extraction + multi-quarter trend system for US filings** — done as **staged-C** (general architecture, staged trust). This brief is the seed for a loom-spec change-folder.

## Problem

(Axis 1 — JTBD) When the equity-memo pipeline analyzes a US ticker, the
memo writer sees only XBRL-tagged financial-statement numbers + price. It
sees **none of management's narrative** (MD&A, risk factors, 8-K events)
and — verified this session — **none of the operational KPIs, guidance, or
market data** that are NOT XBRL-tagged and live only in the document
tables/prose (unit sales, market share, ASP, segment KPIs, forward
guidance). The job: *"when I analyze a US company, I want its operational
KPIs and management narrative — as a citable, multi-quarter trend I can
trust — not just the standard financials, so the thesis reflects the
business, not only the accounting."*

## Users

(Axis 2) The `report-equity-memo` pipeline + `investing-team` memo worker
(consumers, US path); the human memo reader (end beneficiary). Reliability
bar is high: this feeds investment verdicts, and the codebase just shipped
(PR #548) verdict-layer defenses against fabricated numbers — a KPI trend
built on silently-wrong extractions is the highest-blast-radius version of
exactly that failure mode.

## Current State Evidence

- **Forward**: `pack_us.py:552-591` `pack_memo_fetch()` calls SEC EDGAR
  `--action filings` (index) + `--action facts` (XBRL) only. No narrative,
  no document tables reach the memo.
- **Reverse**: `data-markets/scripts/` is single-copy (25 scripts, no
  distribute/SSOT sync for `sec_edgar_client.py`). Edit in place.
- **Error**: US fails per-section (`market-us.md:42-44`) → new sections
  follow per-section fail-loud, feed `pack_inventory`/`_status`.
- **Data**: `sec_edgar_client.py` has a regex `parse_item_sections()`
  (`:398`) + `narrative` action (`:693`, requires `--accession`) +
  exhibit-index skip (`:478`). Works on 10-K/10-Q Item bodies; **misses
  8-K Exhibit 99.x** (where results/guidance live).
- **Boundary**: regex parser fights TOC-vs-body (`:405,:420`); research
  flags it fragile. Verified XBRL coverage boundary (see Decision).

Evidence paths: `investing-toolkit/skills/data-markets/scripts/{pack_us,sec_edgar_client}.py`,
`.../references/market-us.md`, `/tmp/research-us-sec-narrative.md`,
`/tmp/research-processing-layer.md`, `/tmp/research-xbrl-coverage-boundary.md`,
`/tmp/research-kpi-timeseries.md`.

## Decision

Build toward a **general** US operational-KPI + narrative data layer, as
**staged-C**: general architecture from day one, but **staged trust** —
prove the engine on 1-3 tickers, gate on measured extraction accuracy,
then scale schema coverage. Three capabilities:

1. **Narrative text** (edgartools, key-free): 10-K Item 7 (MD&A) + Item 1A
   (Risk), 10-Q Item 2, 8-K Items 2.02/7.01/8.01 **following Exhibit 99.x**.
   Replaces the fragile regex parser. Narrative → LLM reads/cites.
2. **Financial-statement tables + XBRL cross-validation**: doc table vs
   XBRL fact matched by concept+period+dimension, ~1% tolerance, model
   legitimate divergence (scale/rounding/adjusted-vs-GAAP), adopt XBRL US
   DQC ruleset. The second-source verification for STANDARD financials.
3. **Operational-KPI extraction + multi-quarter bitemporal trend** (the
   hard, general part). Per verified research:
   - **XBRL does NOT cover these** — document tables are the only source
     (SEC MD&A rule 33-10890 declined structured tagging; guidance & 8-K
     Ex-99.1 untagged). Must extract from document HTML.
   - **locate-then-parse**: LLM/ML **locates the cell**, a deterministic
     parser **emits the number** — never LLM-generated (schema-constrained
     output fixes format, not value; naive RAG hallucinates numbers
     12-18%). Rule-validate (units/sign/subtotal=sum/GAAP-vs-non-GAAP),
     XBRL cross-check where a tagged equivalent exists, low-confidence →
     human-review queue.
   - **schema registry, not hardcoded**: per-company KPI schema; the
     general seam is **LLM proposes a new company's schema → human confirms
     once → then trusted**. (No vendor ships open-ended auto-discovery;
     incumbents with LLMs still keep humans on schema + drift.)
   - **bitemporal / point-in-time store** keyed (company, kpi_id, period,
     as_of), never overwrite. Definition-drift = a **curated break/mapping
     event** per re-segmentation (ASC 280 recast) + dual as-reported vs
     recast series with a visible break flag. **Never concatenate naively.**
   - **reliability gate**: a company's series is not trusted (not fed to
     the memo) until extraction accuracy on a held-out set clears a
     measured bar.

Consistent with the codebase's numbers-by-code / narrative-by-LLM +
provenance + fail-loud discipline (PR #548), applied one level deeper:
LLM reads/locates, code emits the number, everything cites its source, and
untrusted data is flagged not fabricated.

## Alternatives Considered

(Axis 4 — this session's research)

| Approach | Verdict | Why |
|---|---|---|
| **staged-C** (general arch, staged trust, LLM-proposes/human-confirms) | **CHOSEN** | The only shipped-precedented path to general; delivers KPI+trend without pretending open-ended auto-discovery is solved |
| Foundation-first (narrative + fin-table cross-val; defer KPI) | Rejected by user | KPI value too late; user wants it early |
| Open-ended auto-discovery, no human seam ("LLMs solve it now") | Rejected | No vendor ships it; format-not-value hallucination; silently-wrong trends = the exact failure PR #548 defends against |
| edgartools structured cells for operational tables | Rejected (infeasible) | edgartools gives structured cells only for XBRL-backed financial statements; arbitrary MD&A/exhibit tables are text-only → DIY HTML parse (pandas.read_html/lxml) |

Conditional reversal: if measured extraction accuracy on the pilot tickers
can't clear a usable reliability bar even with locate-then-parse + rules,
fall back to narrative + financial-table-cross-val only (drop the
open-ended KPI ambition) and revisit.

## What Becomes Obsolete

(Axis 5, same PR as capability 1) `sec_edgar_client.py` regex
`parse_item_sections()` + `action_narrative` internals + exhibit-skip
heuristic → replaced by edgartools (keep the `narrative` CLI action name).
`market-us.md:12` narrative description → update.

## Out of Scope

- TW / JP narrative + KPI (later arcs; this proves the pattern on US).
- Real-time / intraday; this is filing-cadence.
- Auto-correcting definition drift (we flag + human-map, never silent).
- A UI for the human-confirm/review seam beyond a minimal queue+CLI (defer
  richer tooling).

## Open Questions (for loom-spec to resolve)

- The measured reliability bar (accuracy metric + threshold) that gates a
  company's series into the memo.
- Pilot ticker set (1-3) + initial KPI schema per pilot company.
- Bitemporal store substrate (files/JSON vs sqlite) given the toolkit's
  no-DB, pure-script footprint.
- Where the human-confirm/review seam lives (CLI action + a queue file?).
- edgartools dependency weight (pulls pandas etc.) — acceptable footprint?
