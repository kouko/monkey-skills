# Brief — US as-reported statement lane + derived spine view

- Date: 2026-07-26
- Branch: `feat-us-as-reported-statement-lane` (based on `3ee2fcd3`)
- BACKLOG entry: §"investing-toolkit — full three-statement + management-KPI
  history in kpi_store", sub-arc (a). BACKLOG stays SSOT; this brief RESHAPES
  what (a) builds (see §Decision) and that reshaping needs the BACKLOG entry
  amended at close-out, not silently diverged from.
- Design-side on-ramp: not offered — no user-facing surface, no new product
  shape; an increment to a shipped pipeline (family reception negative guard).

## Problem

A US filer's three-statement history is computed on every memo run and then
thrown away. `pack_memo_fetch` assembles `income_statement` / `cash_flow` /
`balance_sheet` from 14 DCF-chosen concepts (`pack_us.py:125-182`, `:493-556`)
and **no `kpi_store` producer consumes it** — so nothing accumulates, and a
question like "show me this company's operating income every year since the
data exists" cannot be answered without re-fetching.

The job behind the request is **not** "add 15 more fields". It is: *make the
mechanical part of fundamental analysis a solved, accumulating substrate, so
analysis reads history instead of re-deriving it.* The user stated it as
「完整的三大表與管理/非財務指標的年度與季度的連續歷史資料給後續分析用」.

The hazard that makes this non-trivial: the store is **append-only**. A wrong
number that lands is permanent — a later fix either fabricates a restatement
dagger or requires a migration.

## Users

The repo owner, doing single-name fundamental work across US and TW markets,
with a store that already holds TW's 15-field spine and US dimensional KPIs.

Job story: *When I want to judge a company's trajectory, I want its statement
history already in the store with every vintage preserved, so I can compare
periods and see restatements without re-fetching or trusting a vendor's
normalization I cannot inspect.*

## Smallest End State

A US filer's **as-reported** statement lines land in `kpi_store` as durable
annual series, and the market-comparable 15-field spine is **derived at read
time** from them.

Concretely:
1. A new producer stores, per period, the filer's own us-gaap concepts for the
   spine's source concepts — `us-gaap:Revenues` and
   `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` are **two
   series**, not one resolved series.
2. A new pure view module maps the store's `dump --company` payload into a
   spine-shaped payload, resolving **which concept represents a field in that
   period** at read time. `tearsheet_format.py` is unchanged.
3. Ingest refuses, loudly, a filer whose resolved CIK carries no statement
   history.

**Why "as-reported stored, spine derived" is the shape** (the load-bearing
decision — see §Alternatives): storing the canonical slug makes concept
selection a **write-time, one-way** decision. Measured over the 47-filer
corpus, the naive per-company selection rule is wrong for **24/46 filers**
(26 field/filer pairs), losing up to 16 years of history — and 10 of those
are wrong in **shipped code today**. Storing as-reported makes that class of
error **structurally impossible**: both candidates are kept, and selection
becomes a correctable read-time function.

Measured cost of the shape: **median 21 series per company** (range 15-26)
versus 14 for canonical slugs and 71-108 for whole face statements — same
order of magnitude as the spine, so no filename-budget pressure.

## Current State Evidence

**Forward (happy path, write→read).**
`pack_us.pack_kpi_topline_backfill` (`pack_us.py:1043`) →
`sec_edgar_client.build_top_line_backfill` (`sec_edgar_client.py:2788`) →
`kpi_xbrl_ingest.ingest_pack` (`kpi_xbrl_ingest.py:499`) →
`kpi_xbrl.facts_to_points` (`kpi_xbrl.py:490`) → `kpi_store.append`
(`kpi_store.py:343`). Read side: `kpi_store.dump_company`
(`kpi_store.py:746`) → `tearsheet_format.render_tearsheet`
(`tearsheet_format.py:15-38`, one row per `kpi_id`).

**Reverse (SSOT / ownership).** The store is written ONLY by `analysis-kpi`
producers; `data-markets` never writes it and is never imported across the
boundary (`kpi_tw.py:1-13`, `kpi_tw_ingest.py:27-32`; envelopes are handed in).
The dump payload's schema SSOT is `docs/loom/plans/2026-07-23-kpi-tearsheet.md`
## Notes, transcribed verbatim into `tearsheet_format.py:8-9`; the formatter is
a pure function over it. **Read-side consumers: exactly one** (verified by
grep across `investing-toolkit/skills`), which is what makes a derived view a
two-way door.

**Error (fail-loud surfaces already in place).**
`kpi_store._require_provenance` (`kpi_store.py:178`),
`_require_accession_derived_as_of` (`:190`),
`kpi_xbrl_ingest._require_trusted_source_kinds` (`:426`),
`_require_no_stored_disagreement` (`:446` — evidence that two lanes writing one
economic quantity has already been painful once),
`kpi_xbrl._require_source_form` (`kpi_xbrl.py:289`, raises rather than guess a
form).

**Data (shapes and budgets).** Dedup key is the 5-tuple
`(company, kpi_id, period, as_of, source_accession)` (`kpi_store.py:213`).
Series stem budget `_MAX_STEM_BYTES = 220` (`kpi_store.py:87`). Field sets:
US DCF 14 (`pack_us.py:125-182`), TW spine 15 (`kpi_tw.py:33-50`). Top-line
allowlist 4 concepts (`sec_edgar_client.py:2402`); annual carrier allowlist
`{"10-K": "FY"}` (`sec_edgar_client.py:2666`).

**Boundary (what the data source cannot do — all measured, see §Probe).**
`companyfacts` carries **no calculation linkbase** and **no `decimals`
attribute**, so filer-declared subtotal relationships and per-fact precision
are both unavailable on this path. XBRL history begins with the SEC's
2009-2011 phase-in: **0/46 filers have ≥20 usable years**; median 18.
`resolve_cik` can return an entity with no statement history (measured 1/47
empty, 2/47 truncated).

**Evidence paths.** Probe scripts and raw JSON currently live in the session
scratchpad; per this repo's precedent
(`tests/data/fixtures/capture_kpi_id_identity_probe.py` +
`kpi_id_identity_probe_2026-07-25.json`) they MUST be committed as a capture
script plus a dated fixture in the plan's first task, or the numbers below
have no auditable source.

## Probe evidence (47-filer corpus, 2026-07-26)

Same corpus as the kpi_id arc (`capture_kpi_id_identity_probe.py:95-103`).
`companyfacts` only; one filer (XOM) resolves to an entity with 0 us-gaap
concepts and is excluded from per-field rates (n=46).

| Measurement | Result |
|---|---|
| Fields covered for all 46 | revenue, pretax_income, net_income, eps_basic, total_assets, total_equity, cash, operating/investing/financing_cash_flow (10 of 14) |
| `capex` | 41/46 — absent for PSX, JPM, BAC, WFC, MS |
| `operating_income` | 33/46 — absent across energy 3, financial 6, tech 1, consumer 1, health 2 |
| `total_liabilities` | 33/46 — 13 filers **never tag** a total (AMZN, INTC, AMD, ORCL, WMT, TGT, MCD, NKE, KO, MRK, HON, VZ, DIS) |
| `gross_profit` | 24/46 — absent for 22 filers across **7 sectors**, not only financials |
| Naive per-company concept selection is stale | **26 pairs / 24 filers**; worst: HD revenue −16y, MSFT revenue −15y, CAT net_income −15y, NVDA capex −14y |
| **Shipped `build_top_line_backfill` truncation** | **10/47** filers get a silently short series (HD→2010, MSFT→2010, HON→2011, MS→2014, TGT→2015, CRM→2017, META→2017, AAPL→2018, WFC→2019, F→2024); XOM errors |
| Balance identity `A = L + mezzanine + E` | checkable 32/46; **exact 30/32**. TSLA's residual was exactly its redeemable NCI (58,000,000) — the mezzanine term is required, not optional |
| Residual on the 2 non-exact | IBM and PG, each exactly 1,000,000 against values reported in millions (rounding). `decimals` is `None` on every component, so tolerance CANNOT be derived from the fact — a relative threshold is required (observed max 7.99e-06) |
| Custom (non-us-gaap) tag share | 0-2.8%, median 0.7% |
| Face-statement size (latest 10-K, edgartools 5.42.0) | AAPL 71 distinct concepts / JPM 108 / WMT 84 / TSLA 87, i.e. 12-17% of the whole concept inventory. JPM carries **17 `jpm:`-namespaced face concepts** including core lines (`jpm:TradingAssets`, `jpm:FeesAndCommissions1`) |
| As-reported series per company over the spine's source concepts | **median 21**, range 15-26 |
| Usable history | 0/46 filers ≥20 years; median 18; earliest fact 2006-06-30; first XBRL filings cluster 2009-05..2009-12 |
| Structure extraction check | `extract_statement_cells` succeeded on 4 filers × 3 statements, **100% of cells joined to a rendered row** — presentation structure is reachable. **Calculation structure was NOT verified** |

## Decision

Build a **US as-reported annual statement lane** writing to `kpi_store`, plus a
**pure read-side spine view**.

- **Identity**: `kpi_id` is the filer's own qname, namespace preserved
  (`us-gaap:Revenues`). Injective by construction — it IS the source key, so no
  lossy derivation and no collision guard theatre
  (`derived-durable-id-slug-is-a-lossy-one-way-door` is satisfied by not
  deriving). A `jpm:`-prefixed concept cannot collide with a `us-gaap:` one.
- **Scope of stored concepts**: the spine's source concepts only (measured
  median 21 series/filer). Widening later is purely additive under this shape.
- **Granularity**: annual (10-K-carried) only.
- **Selection**: happens in the VIEW, per period, first-present over an ordered
  chain. Never at write time.
- **Reconciliation**: the view computes `A − (L + mezzanine + E)` per period and
  emits a flag when it exceeds a relative tolerance; it does not refuse data
  (an as-reported value is not wrong because our selection was). The
  income-statement add-back is NOT available at this scope — see §Out of Scope.
- **Absence is data**: a field the filer never tagged renders absent. Never 0,
  never derived-by-guess. 22 filers have no gross profit; that is the truth.
- **CIK continuity**: refuse loudly when the resolved CIK carries no statement
  history; surface (not silently stitch) a truncated one
  (`ticker-to-cik-can-resolve-to-a-decoy-entity` forbids stitching).

**Not built**: a canonical-slug write lane; per-filing XBRL/linkbase parsing;
quarterly; custom (`jpm:`) concepts; any HTML/text extraction.

## Alternatives Considered

| Option | Why not |
|---|---|
| **A — canonical-slug spine written to the store** (the BACKLOG's original (a)) | Makes concept selection a write-time one-way decision; measured wrong for 24/46 filers. Also cannot ever reconcile the income statement (no COGS/opex/tax stored), so it cannot meet the BACKLOG's own "without the add-back check this lane is a silent-lie generator" bar |
| **B — full face-statement restoration first, spine derived after** | Right shape, wrong first step: 5-7× series/company (71-108) forces a filename-strategy redesign (JNJ sits 12 bytes from the OS limit), and pulls in custom-concept identity — two one-way doors decided with less information than after this arc |
| **C′ — per-filing linkbase as a structural oracle** (this session's earlier recommendation) | Measurement retired it: the dominant real defect is temporal (stale concept selection), not structural mis-mapping, and the balance identity reconciles exactly from `companyfacts` alone. Structure extraction is verified to work and stays available for a later arc |
| **Vendor-standardized source** | Compustat/FactSet standardizations diverge from as-filed AND from each other; buying one means inheriting an uninspectable model. Also the only route past ~18 years, so it stays on the table as a separate product decision |

## What Becomes Obsolete

- `sec_edgar_client.build_top_line_backfill`'s per-company first-present rule
  (`sec_edgar_client.py:2863-2872`) is demonstrably wrong. Either fixed in this
  branch or explicitly deferred — it must not be left undecided.
- Nothing else is retired. `_normalize_dcf` (`pack_us.py:368`) stays: it feeds
  the memo's DCF, already merges per period correctly, and is not a store path.

## Out of Scope

- **Quarterly** (Q4 derivation + 52/53-week fiscal labelling) — next arc.
- **Full face-statement restoration incl. custom concepts** — next arc; needs a
  filename strategy and a custom-concept identity decision first.
- **Income-statement add-back reconciliation** — needs COGS/opex/tax stored;
  purely additive under this shape, deliberately not in this arc.
- **Calculation-linkbase access** — unverified; only needed for the above.
- **Management / non-financial KPIs** — BACKLOG sub-arc (b), blocked on its own
  Part 3. Do not re-scope here.
- **Pre-2009 history via HTML/text extraction** — user-deferred 2026-07-26;
  the repo forbids body-text scraping (`extract_statement_cells` docstring).
- **Stitching predecessor CIKs** (GOOGL, DIS) — forbidden by memory.

## Resolved at kickoff (user, 2026-07-26)

1. **Fix `build_top_line_backfill`'s truncation IN THIS BRANCH.** Its
   per-company first-present rule (`sec_edgar_client.py:2863-2872`) is
   producing short series for 10/47 filers in shipped code today; the correct
   rule is the same per-period resolution this arc introduces, so the fix rides
   along rather than waiting. In scope, not a follow-up.
2. **Reconciliation tolerance: relative, 1e-5.** `decimals` is unavailable on
   every `companyfacts` component (verified on IBM/PG/AAPL), so an absolute or
   precision-derived tolerance is not constructible. 1e-5 clears the observed
   rounding residuals (max 7.99e-06, IBM and PG each exactly 1,000,000 against
   values reported in millions) with roughly one order of magnitude of headroom.
   A residual ABOVE it is a flag, never a refusal (§Decision).
3. **Branch renamed** `feat-us-three-statement-producer` →
   `feat-us-as-reported-statement-lane`, before any push.

## Open Questions

- None blocking. Two facts stay deliberately unverified because nothing in
  this scope reads them: calculation-linkbase reachability, and quarterly
  fiscal-period labelling. Both are named in §Out of Scope and must be
  re-verified by whichever arc first depends on them — not assumed from here.
