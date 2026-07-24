# Brief — US XBRL → kpi_store producer (dimensional revenue)

Arc (d). Date: 2026-07-24. Stage-1 brainstorming output → consumed by `writing-plans`.

## Problem

(Axis 1 — JTBD) As an investor, **when** I point the toolkit at a US ticker,
**I want** its operational-KPI observation history — including cross-filing
restatements — to land in `kpi_store` automatically, **so I can** render a KPI
tearsheet without hand-authoring glue.

The KPI tearsheet (read surface) and the bitemporal store (grouping + `†`
restatement marker) are SHIPPED and correct (verified by a 5-filer dogfood:
INTC/AAPL/JPM/SNOW/WMT rendered cleanly; INTC surfaced two real recasts with
`†` + Revisions). But there is **no shipped producer** that turns SEC XBRL into
store-shaped points — the observation-history slice explicitly deferred it
(`docs/loom/plans/2026-07-22-kpi-observation-history.md:199` "No XBRL-lane
producer task ... explicitly out of scope"). Today the only way to feed US XBRL
into the store is a hand-written glue script (the dogfood proved this). The
prose/8-K lane is the only producer wired to the store.

## Users

(Axis 2) The toolkit operator (kouko) running investing-toolkit on **US SEC
filers** (10-K/10-Q, dimensional revenue). Job story: *"When I want one US
company's KPI history with restatements visible, I want to name the ticker and
get a tearsheet, so I don't reverse-engineer the XBRL→store wiring each time."*
Current workaround: a bespoke `xbrl_to_store_points.py` glue script written per
dogfood session — not shipped, not repeatable.

## Smallest End State

(Axis 3 — user chose dimensional-segment-only v1) A **shipped, documented**
path that takes a US ticker → fetches dimensional revenue across filings →
emits store-shaped points carrying the period-identity fields the store needs →
appends **each vintage** (no collapse) → store. The EXISTING tearsheet then
renders. Concretely:

1. **Emit `period_start`** on the extracted fact — re-source from the raw XBRL
   duration context (already read at extract time, currently dropped) in
   `_build_dimensional_revenue_fact`.
2. **Emit `period_kind`** on the XBRL point — synthesize from the existing
   `duration_class`/`period_type` already on the point (duration vs instant).
3. **Emit `scale`** on the XBRL point — hardcoded `1` (XBRL values are base;
   matches the prose lane's rationale).
4. **A store-feed path** (new `kpi_xbrl` subcommand or thin driver) that appends
   **each vintage** via `kpi_store.append` — using the non-collapsing
   `facts_to_points`, NOT the collapsing `resolve_binding` path (Axis-4 decision
   below).
5. **SKILL wiring** — document the ticker→tearsheet workflow in
   `analysis-kpi`/`report-kpi-tearsheet` SKILL so it is runnable, not tribal.

No change to `tearsheet_format.py` or the store's read logic — they already work
given correctly-shaped points (dogfood-proven).

## Current State Evidence

Base path: `investing-toolkit/skills/`.

- **Forward** (who calls the producer today): NOTHING appends XBRL output to the
  store. `kpi_xbrl.py` never imports `kpi_store`; `build` dumps points to stdout
  (`analysis-kpi/scripts/kpi_xbrl.py:1854`), `quarterly-series` dumps series
  (`:1795`). The store-feed seam is absent — this is the core gap.
- **Reverse** (what feeds the fact-pack): `pack_us.pack_kpi_quarterly`
  (`data-markets/scripts/pack_us.py:957-1036`) stitches a 10-Q arm + a 10-K arm
  into one facts list (`:1012`), merging per-accession fiscal calendars
  (`:1013-1016`); vintages flow through un-collapsed. Emitted shape `{pack,
  ticker, fetched_at, company, facts, fiscal_calendars, coverage}` (`:1030`).
  Dimensional-only (no top-line total). `pack.py` is a facade routing to it
  (`pack.py:413`), enforcing US-only (`:109,391-396`).
- **Error** (store append contract): `kpi_store.append`
  (`analysis-kpi/scripts/kpi_store.py:303-361`) REQUIRES provenance
  (`source_accession`/`source_table_id`/`source_cell_ref`, `_require_provenance`
  `:138-147`, rejects falsy) + a non-wall-clock `as_of` (`:150-174`). It does
  NOT require or validate `period_start`/`period_kind`/`scale` — silently
  accepts + persists (`:357`). An XBRL point from `facts_to_points` ALREADY
  satisfies provenance (`source_*`=`xbrl:…` at `kpi_xbrl.py:543-546`) + `as_of`
  (`=filed`, `:541`), so it appends cleanly today — the missing fields only
  degrade read-side grouping, they don't block the write.
- **Data** (period fields on raw facts): `_build_dimensional_revenue_fact`
  (`data-markets/scripts/sec_edgar_client.py:2837-2958`, dict at `:2931-2939`)
  emits `period_end` only (`:2936`); `period_start` IS read upstream
  (`_duration_span_days` `:2391`) but DROPPED. Duration/instant is implicit
  (duration facts get `duration_months`/`duration_weeks` `:2940-2946`). dei
  calendar is used only for fiscal-year/quarter LABELS (`:2947-2954`), NOT for
  `period_start` — that comes from the raw XBRL context.
- **Boundary** (shape divergence): the three lanes already disagree on point
  shape and the store tolerates all three. Prose `_prose_candidate_to_point`
  (`kpi_prose_candidates.py:620-716`) carries `period_start/end/kind` as
  None-able pass-throughs (`:705-707`) + `scale=1` hardcoded (`:695`). 8-K
  `_candidate_to_point` (`kpi_8k_candidates.py:302-337`) sets `scale` from unit
  (`:332`) but OMITS the period triple entirely (only `period` label `:329`).
  XBRL `facts_to_points` (`kpi_xbrl.py:490-568`) emits `period_end` +
  `period_type`/`cumulative`/`duration_class` (`:529-531`) + `calendar_*`
  (`:536-537`), no `period_start`/`period_kind`/`scale`. v1 aligns the XBRL point
  toward the prose shape (the one lane that carries all three).

Evidence paths: `kpi_xbrl.py`, `kpi_store.py`, `kpi_prose_candidates.py`,
`kpi_8k_candidates.py` (analysis-kpi/scripts); `sec_edgar_client.py`,
`pack_us.py`, `pack.py` (data-markets/scripts). Recon 2026-07-24 (Explore agent).

## Decision

Build a **dimensional-revenue XBRL→store producer** for US filers: add
`period_start` (re-sourced from raw context), `period_kind` (synthesized), and
`scale=1` to the XBRL point, and add a **non-collapsing store-feed** that
appends each cross-filing vintage via the existing `kpi_store.append`, reusing
`pack_us.pack_kpi_quarterly` + `facts_to_points`. Wire the ticker→tearsheet
workflow into the SKILL so it is runnable. Do NOT touch the tearsheet formatter
or the store's read logic (dogfood-proven correct). Restatements are stored as
separate vintages, never collapsed — the store's bitemporal `†` needs ≥2
differing vintages, and this is what the store was designed for.

## Out of Scope

- **Top-line total revenue (GAP-3) — the IMMEDIATE NEXT ARC, not dropped.** User
  confirmed 「接下來就要做 公司總營收」. It needs a different, differently-shaped
  feed (`action_facts(ticker,'Revenues')` companyconcept series — API-endpoint
  shape, no dei calendar, mixes annual+quarterly under `fp:FY`,
  `sec_edgar_client.py:666-711,271-294`) and its own annual/quarterly
  disambiguation, which overlaps the multi-granularity arc. Separate arc, right
  after this one.
- **Changing `resolve_binding` / `_restatement_survivor` (policy C) collapse**
  (`kpi_xbrl.py:639,702-740`). That path serves a different consumer (a single
  survivor value). The store-feed bypasses it, not replaces it.
- **Non-US markets** (TW/JP/KR/CN) — this producer is US-XBRL specific.
- **Multi-granularity (monthly/half-year)** — arc (a), separate.
- **Tearsheet formatter or store read-logic changes** — none needed.

## Alternatives Considered

(Axis 4 — WebSearch EN+JA, 2026-07-24)

- **Append each vintage as a point-in-time record (CHOSEN)** — bitemporal
  "Snapshot + Delta": store multiple values for the same item as of different
  times; restatements are separate records. EN: [MDPI, just-in-time historical
  state](https://www.mdpi.com/2673-2688/7/4/117). JP: 決算訂正時は訂正開示と共に
  XBRL を**再登録**（別 filing/vintage）[JPX FAQ](https://faq.jpx.co.jp/disclo/tse/web/knowledge8408.html).
  EN+JA agree: restatements = separate vintages, not overwrite/collapse.
- **Collapse to a survivor value (REJECTED for the store-feed)** — what
  `resolve_binding` does; loses the vintage history the tearsheet `†` needs.
  Fine for its own consumer; wrong for the observation-history store.
- **My take: Recommend** appending each vintage via `facts_to_points` (which
  already does NOT collapse), mirroring the prose lane's store-feed. **Why:** it
  is the store's designed use and matches both EN and JA industry practice.
  **Conditional reversal:** only if a future consumer needs a single
  as-of-latest value would a collapse layer belong — and that is a read-side
  query (`kpi_store query --latest`), not a producer choice.

## What Becomes Obsolete

- The per-session hand glue (`xbrl_to_store_points.py`, dogfood-only) — replaced
  by the shipped producer; do not check it in.
- The observation-history plan's "No XBRL-lane producer task" deferral note is
  discharged by this arc.

## Open Questions

- Exact home of the store-feed: a new `kpi_xbrl` subcommand (`ingest`) vs a thin
  orchestration in the SKILL calling pack → facts_to_points → append. Resolve in
  `writing-plans` (implementation-design, not a user fork).
- Which single dimensional KPI per company the SKILL workflow demonstrates
  (segment vs geo) — cosmetic, pick the richest signature per the universe doc.

## Recall (memory rules carried into planning)

- Fiscal year per fact from its OWN `period_end` vs the filing's dei calendar —
  never `period_end[:4]` blindly, never filing-level `DocumentFiscalYearFocus`
  on every fact, never edgartools' `fiscal_year` column; fail loud if calendar
  unreadable (`fiscal-year-derive-per-fact-against-filing-calendar.md`,
  `edgartools-fiscal-year-column-unreliable.md`). The calendar-vs-fiscal
  primitive had 4 call sites — fix the primitive + its docstring, not symptoms.
- Producer must emit EVERY field the consumer reads; a partial schema resolves
  to a silent default and only whole-branch review catches it
  (`market-canonical-must-satisfy-consumer-field-contract.md`). Ship the field
  AND wire the consumer in the same change
  (`producer-marker-inert-until-consumer-branches-on-it.md`).
- Test cross-module field contracts with behavioral probes across the seam, not
  grep (`cross-module-field-contracts-execute-probes.md`). Fixtures must mirror
  the REAL producer shape; hand-typed (esp. Dec-FYE) fixtures hide the
  calendar-vs-fiscal trap (`fixtures-mirror-producer-shape.md`,
  `hand-authored-fixture-is-a-fabrication-risk.md`).
- Dimensional history iterates individual filings (companyfacts/frames omit
  dimensional members, `sec-companyfacts-frames-api-omits-dimensional-members.md`).
  Key KPI by full dimensional signature
  (`match-kpi-on-full-dimensional-signature-not-one-axis.md`). ticker→CIK can
  hit a decoy entity (`ticker-to-cik-can-resolve-to-a-decoy-entity.md`).
- Falsy provenance guard: render a truthy token at the producer boundary rather
  than weakening the guard (`falsy-guard-rejects-legitimate-zero-provenance.md`).
