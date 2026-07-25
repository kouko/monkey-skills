# TW-market kpi_store producer (mirror US kpi_xbrl_ingest)

Brief (brainstorming output) — 2026-07-25. Branch `tw-kpi-store` off `560ad435`
(main @ investing-toolkit 2.34.0). Origin: user-selected from the US-vs-TW
analysis-gap map — build the TW version of the US `kpi_xbrl_ingest` producer
(PR #611) so a TW ticker gets the same cross-period KPI store → tearsheet path
the US path just shipped.

## Problem

The US analysis method turns a ticker's XBRL history into a **durable,
time-versioned KPI store** — every reporting period's revenue/income/etc.,
each vintage preserved so a later restatement is visible, not silently
overwritten — then renders it as a one-page tearsheet. TW reaches a full memo
pipeline but has **no such producer**: `pack_tw`/`twse_ixbrl` emit a single
period's canonical snapshot, nothing accumulates across filings. So a TW
analyst cannot see how a company's revenue evolved over quarters, or whether a
past figure was restated — the exact cross-period view the US tearsheet gives.

## Users

kouko analysing TW equities who wants the same cross-period KPI trend +
restatement-visibility view the US path offers. Job story: *when I evaluate a
TW company over time, I want its revenue / income / EPS / etc. accumulated
across filings into a versioned store and rendered as a tearsheet, so I can see
the trend and catch restatements — without hand-stitching each quarter's
snapshot.*

## Smallest End State

A **TW ingest producer only** — the store and tearsheet need NO change (recon
proved both are fully market-agnostic; a TW point with the same schema renders
in the existing tearsheet untouched). Concretely, a TW analog of
`kpi_xbrl_ingest ingest` that:

- Consumes the existing `pack_tw`/`twse_ixbrl` canonical facts (no new fetch of
  financials — the data is already produced).
- Derives a **TW kpi_id = `concept-slug` [+ `__basis-<C|A>`]** — TW has no
  us-gaap dimensional axes, so the one discriminator is
  consolidated (C/合併) vs parent-only (A/個體); basis substitutes for the US
  `axis=member` signature, keeping the two as distinct series. Reuse the US
  `derive_kpi_id` injective fail-loud collision guard
  ([[derived-durable-id-slug-is-a-lossy-one-way-door]]).
- Maps each fact's `period{instant|duration, start, end}` directly to the point
  schema (`period_start`/`period_end`/`period_kind`), `raw_value`→`value` with
  `scale=1` (twse parser already base-scales), and synthesizes TW provenance
  (`source_accession` from co_id+year+season+report_id, `source_form` = a TW
  form value, `source_table_id="tw:ixbrl"`, `source_cell_ref`=concept).
- **Captures a MOPS disclosure date for `as_of`** — the load-bearing
  prerequisite: the store rejects a wall-clock `as_of` (demands an
  accession-derived one), but the TW pipeline captures no filing date today.
  This arc must obtain a non-wall-clock disclosure date (fetch it from MOPS if
  cheaply available; else a deterministic per-season proxy — resolve in
  planning; see Open Questions).
- Appends to the **unchanged** `kpi_store` (reuse append / same_period / _qtrs /
  canonical_value / dump), does NOT reuse data-markets `cache_util`
  ([[durable-store-mirrors-cache-util-not-imports-it]] — the store already
  respects this; the TW producer must not breach the layer boundary either).
- One "See also" line broadening `report-kpi-tearsheet/SKILL.md` to name TW.

Cadence: `_qtrs = round(days/91.3125)` already handles TW quarterly (1..4). **興櫃
semiannual (6-mo → _qtrs==2) fits the same machinery with no new period_kind** —
the deferred 興櫃 multi-period arc converges here; this arc keeps the producer
興櫃-ready (emit the honest duration) but scopes fetch to listed quarterly.

## Current State Evidence

- **Forward**: US path `pack.py --pack kpi-quarterly`
  (`pack_us.pack_kpi_quarterly` `pack_us.py:957`) → `kpi_xbrl_ingest.py ingest`
  (`:203`) → `derive_kpi_id` (`:85-109`, concept + dim signature) →
  `facts_to_points` (`kpi_xbrl.py:526-564`, the point schema) →
  `kpi_store.append` (`store:135-170`). TW mirror branches in at the **ingest
  layer** (not the fetch pack — kpi-quarterly is `US_ONLY_PACKS`,
  `pack.py:109,391-396`, exit 64 for non-US): a sibling TW ingest consuming
  `pack_tw`/`twse_ixbrl` canonical.
- **Reverse (SSOT / reuse)**: `kpi_store.py` is FULLY market-agnostic (zero
  us-gaap/SEC/dimension coupling); `report-kpi-tearsheet/tearsheet_format.py`
  (`:65-239`) renders from `dump_company` only, `unit` free-text ("TWD"
  renders) — **producer-only arc confirmed**. `derive_kpi_id` algorithm + guard
  reusable.
- **Error / US-coupled pieces to invert or replace**: empty-dims **skip**
  (`ingest:151-153`) drops flat totals — TW is ALL flat totals, so **invert**
  (keep them); `source_form` from dei focus (`kpi_xbrl.py:289-309`, fail-loud)
  rejects TW → TW form; `classify_fact_period` (`:452-476`) needs an edgartools
  label group TW lacks → TW maps period from the parser directly.
- **Data (TW facts)**: `twse_ixbrl_parser.py:16-41` fact =
  `{concept(ifrs-full:*/tifrs-*), context_ref, raw_value(base-scaled :161),
  unit, period{instant|duration}}`; canonical KPIs
  `twse_ixbrl_canonical.py:56-81` = revenue / gross_profit / operating_income /
  pretax / net_income / eps_basic / total_assets / liabilities / equity / cash
  / OCF / ICF / FCF / capex (+ financial-family maps). Consolidation basis =
  report_id C/A (`twse_ixbrl.py:118`).
- **Boundary (the as_of gap)**: pipeline output `twse_ixbrl.py:123,139,156`
  carries NO disclosure date; the store's accession-derived-`as_of` guard
  (`store:135-170`) will reject a wall-clock date → the disclosure-date capture
  is the one real prerequisite sub-task.

Evidence paths: `investing-toolkit/skills/analysis-kpi/scripts/{kpi_xbrl_ingest,kpi_xbrl,kpi_store}.py`,
`investing-toolkit/skills/report-kpi-tearsheet/{SKILL.md,scripts/tearsheet_format.py}`,
`investing-toolkit/skills/data-markets/scripts/{pack.py,pack_us.py,pack_tw.py,twse_ixbrl*.py}`.
Full recon: `scratchpad/tw-kpi-producer-recon.md` (migrate key facts inline, do not cite the scratchpad path in code).

## Alternatives Considered

- **Generalize `ingest_pack` to accept a TW pack vs a sibling TW ingest** — the
  empty-dims-skip inversion + source_form + period-mapping differ enough that a
  sibling TW ingest (sharing the reusable `derive_kpi_id`/point schema/store) is
  cleaner than branching the US ingest with market conditionals. Decide the
  exact seam in planning; both keep the store/tearsheet untouched.
- **kpi_id = concept only vs concept+basis** — concept-only would merge
  consolidated and parent-only figures into one series (data corruption, the
  same class the derived-id memory warns about); basis-tagged keeps them
  distinct. Chosen: concept+basis.
- **as_of: real MOPS disclosure date vs deterministic per-season proxy** —
  real date is honest but needs a fetch addition; proxy is cheap but approximate.
  Open Question, resolved in planning by checking MOPS availability.

## What Becomes Obsolete

- Nothing removed — purely additive (a new producer). The tearsheet's US-only
  framing in `report-kpi-tearsheet/SKILL.md` gets one line broadened.

## Decision

Build a TW-market ingest producer that consumes the existing `twse_ixbrl`
canonical facts, derives a `concept[+__basis-C|A]` kpi_id (reusing the US
injective guard), maps periods/values directly, synthesizes TW provenance,
captures a non-wall-clock MOPS disclosure date for `as_of`, and appends to the
**unchanged** market-agnostic `kpi_store` — so the existing `report-kpi-tearsheet`
renders TW KPIs with no store/tearsheet code change. Listed quarterly is the
fetch scope; the producer stays 興櫃-semiannual-ready via the existing `_qtrs`
machinery. We will NOT modify `kpi_store` or the tearsheet render, NOT build a
TW dimensional signature (none exists), NOT wire the memo (Phase 3.5 chain is a
later follow-up).

## Out of Scope

- Any change to `kpi_store.py` or `tearsheet_format.py` (proven unnecessary).
- 興櫃 fetch (this arc keeps the machinery 興櫃-ready but scopes fetch to listed
  quarterly; 興櫃 fetch stays the deferred BACKLOG arc).
- Wiring the TW KPI store into the memo pipeline (report-equity-memo Phase 3.5 —
  a later follow-up, like the US chain).
- xval / sec_narrative TW equivalents (the other two US-vs-TW gaps).

## Open Questions

- **as_of source**: is a real MOPS disclosure/filing date cheaply fetchable per
  filing? If yes → capture it; if not → a deterministic per-season statutory-
  deadline proxy (non-wall-clock). Resolve in planning by a quick MOPS probe.
