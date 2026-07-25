# Brief — company total (top-line) revenue lane

Date: 2026-07-25
Arc: investing-toolkit, successor to arc (d) (`2026-07-24-kpi-xbrl-store-producer.md`)
Status: brief (brainstorming output) — awaiting user sign-off before `writing-plans`

## Design-side on-ramp

Axis 0 negative guard fired: this is a test-covered increment to an existing,
shipped data lane (no new product surface, no UI). No design-side detour
offered.

## Problem

A KPI tearsheet for a US filer currently shows *how revenue breaks down*
(segment / product / geography) but never *how much the company made in
total*. The job: **"when I open a company's tearsheet, I want the top-line
revenue row alongside the breakdown, so I can see whether a segment's move
mattered to the whole business"** — a breakdown without its total cannot be
sanity-checked, and the reader has to leave the tearsheet to find the number.

## Users

The toolkit operator (the repo owner) reading a one-page tearsheet for a US
filer, having already run the shipped dimensional producer for that ticker.
Conditions: offline-reproducible store, SEC EDGAR as the only primary source,
append-only durable history where a wrong write is a one-way door.

## Smallest End State

For a US ticker:

1. **Lane B (primary, per-filing)** — the existing per-filing XBRL parse also
   emits the company's flat top-line revenue fact, ingests it into `kpi_store`
   under a stable canonical `kpi_id`, and the tearsheet renders it beside the
   segment series with restatement `†` working as it already does.
2. **Lane A (history backfill, companyconcept)** — an **annual-only** backfill
   from the `companyconcept` REST series fills fiscal years older than the
   filings Lane B fetched, appended to the **same** series.
3. An overlapping fiscal year covered by BOTH lanes yields the **same value**
   (pinned by a real-data test) — disagreement is a fabricated `†` and must
   fail loud, never be silently stored.

## Current State Evidence

- **Forward (happy path)**: `extract_dimensional_revenue`
  (`investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py:2991`)
  → fact pack → `ingest_pack`
  (`investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py:125`)
  → `kpi_store.append` (`.../kpi_store.py:303`) → `tearsheet_format.py`
  (pure formatter, renders `†` + `## Revisions`).
- **Reverse (SSOT / ownership direction)**: no distribution or sync script
  governs these files — `scripts/` contains only checkers plus
  `sync_codex_manifests.py`, which syncs `.claude-plugin/plugin.json` →
  `.codex-plugin/plugin.json` (version only, no code). Each script is its own
  SSOT. Layer direction: `analysis-kpi` reaches `data-markets` by **subprocess,
  never import** (`kpi_8k_candidates.py:22,124`; repo-store memory
  `durable-store-mirrors-cache-util-not-imports-it`). `kpi_xbrl.py` stays pure
  (no store writes); `kpi_xbrl_ingest.py` is the only store-writing driver.
- **Error (fail-loud paths already in place)**: `_require_provenance`
  (`kpi_store.py:138`), `_require_accession_derived_as_of` (`:150`, rejects
  wall-clock `as_of`), the `kpi_id` collision guard
  (`kpi_xbrl_ingest.py:177-185`), `_unclassifiable` (`kpi_xbrl.py:312`), and
  the anti-fabrication floor "a >1-distinct-value signature+period RAISES".
- **Data**: point shape from `facts_to_points` (`kpi_xbrl.py:490-586`) —
  `company / kpi_id / period / period_start / period_end / period_kind /
  duration_class / cumulative / scale / as_of / value / source_accession /
  source_form / source_kind`. Dedup key is
  `("company","kpi_id","period","as_of","source_accession")`
  (`kpi_store.py:173`). `kpi_gate.TRUSTED_SOURCE_KINDS` (`kpi_gate.py:95`)
  **already contains `xbrl-companyfacts`** — Lane A needs no gate change.
- **Boundary**: flat facts are dropped at the FIRST gate —
  `_dimensional_revenue_candidate_gates` (`sec_edgar_client.py:2321`,
  `if not fact.get("is_dimensioned"): return False`) and
  `_is_dimensional_revenue_fact` (`:2353`, `return bool(dimensions)`).
  Everything downstream of that gate is dimension-agnostic:
  `_build_dimensional_revenue_fact` (`:2911-2961`) derives `period_start`,
  `duration_months`, `duration_weeks`, `week_lane_band`, `fiscal_year`,
  `fiscal_quarter` from the period + the filing's dei calendar only.

### Evidence paths

- Live probe (8 filers, latest 10-K each, real SEC fetch, reusing this
  module's own predicates): scratchpad
  `probe_flat_total_revenue.py` / `probe_flat_total_revenue_result.json`.
- Repo-store memory consulted: `sec-companyfacts-frames-api-omits-dimensional-members`,
  `fiscal-year-derive-per-fact-against-filing-calendar`,
  `derived-durable-id-slug-is-a-lossy-one-way-door`,
  `match-kpi-on-full-dimensional-signature-not-one-axis`,
  `new-arc-branch-bases-on-origin-main-not-merged-tip`,
  `same-economic-fact-different-concept-string-needs-first-present-fallback`.

### Probe findings (live, 2026-07-25, 8/8 filers)

| Ticker | flat top-line picked | value | note |
|---|---|---|---|
| AAPL | RFCC-Excluding | 416,161M | all-ASC-606, no `Revenues` |
| INTC | RFCC-Excluding | 52,853M | |
| JPM | `Revenues` == `RevenuesNetOfInterestExpense` | 182,447M | **7** flat revenue-shaped concepts; 5 are components |
| SNOW | RFCC-Excluding | 4,683.9M | |
| WMT | `Revenues` | 713,163M | RFCC is only 706,413M (excludes membership/other) |
| NVDA | `Revenues` | 215,938M | non-December FYE |
| XOM | `Revenues` | 332,238M | |
| COST | `Revenues` == RFCC | 275,235M | 53-week filer |

Two hazards the probe proved:

1. **"flat + revenue-shaped" ≠ top-line.** JPM emits 7 flat revenue concepts;
   only `Revenues` / `RevenuesNetOfInterestExpense` are the total. A naive
   pass-through would mint 5 bogus "total revenue" series.
2. **A consolidation-qualifier-only fact is NOT the consolidated total.**
   XOM's `Revenues` under `OperatingSegmentsMember` is 452,209M against a true
   total of 332,238M (segment view, pre-elimination); JPM's `ParentCompanyMember`
   is 53,036M (parent-only). Only `is_dimensioned == False` qualifies.

## Decision

Build **both lanes**, Lane B primary and Lane A as annual-only backfill
(user-chosen scope, 2026-07-25).

- **Lane B**: add a top-line lane to the existing per-filing extraction —
  relax only the two dimensionality gates, keep every other gate, and keep the
  whole downstream fiscal-labeling machinery. Marginal fetch cost is zero
  (same filing, same parse).
- **Concept selection is a closed, ordered, first-present allowlist**, grounded
  in XBRL US DQC Revenue Guidance (*"use the more specific
  revenue-from-contracts-with-customers element when all income is ASC 606; for
  mixed revenue types, `Revenues` is the total"*):
  1. `us-gaap:Revenues`
  2. `us-gaap:RevenuesNetOfInterestExpense`
  3. `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`
  4. `us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax`

  Anything outside this list is **not** top-line. Zero candidates → loud skip
  with a named reason, never a fabricated value. This list is NARROWER than
  the existing `_REVENUE_ALLOW_CONCEPT_LOCAL_NAMES` and must not reuse it.
- **`kpi_id` is a fixed canonical constant** (e.g. `total_revenue`), **NOT**
  `derive_kpi_id`'s empty-dimensions bare-concept slug. WMT/COST report two
  candidate concepts and AAPL reports only one; keying on the winning concept
  would fragment one company's durable series the moment its tagging changes —
  and `kpi_id` is a one-way door (`derived-durable-id-slug-is-a-lossy-one-way-door`).
  Same decision the TW producer took (PR #612: canonical field-slug, not raw
  concept).
- **Lane A is annual-only.** `companyconcept` carries no dei fiscal calendar,
  and its `fy`/`fp` are the *filing's* focus — trap #2 of
  `fiscal-year-derive-per-fact-against-filing-calendar`. For an ANNUAL fact the
  fiscal-year label is the period-end year by SEC convention
  (`_filing_period_end_calendar_year` docstring); for a quarterly fact it is
  not. So Lane A ingests annual rows only and never reads `fy`/`fp`.
  `source_kind = "xbrl-companyfacts"` (already trusted).
- **Overlap must agree.** Both lanes apply the identical first-present
  ordering; a fiscal year covered by both is pinned by a real-data test to
  produce the same value.

We will NOT touch `kpi_store`'s read logic, `tearsheet_format.py`, or the
shipped dimensional lane's behavior.

## Out of Scope

- Quarterly backfill via `companyconcept` (needs the dei calendar — that is
  exactly what Lane B provides; revisit with the multi-granularity arc).
- Non-US markets (TW producer is PR #612's lane).
- Any change to `kpi_store` read logic, `same_period`/`_qtrs`, or
  `tearsheet_format.py`.
- Reconciling total vs. sum-of-segments (a cross-check feature, not this arc).
- Restating or re-keying already-stored dimensional series.
- Non-revenue top-line concepts (net income, operating income).

## Alternatives Considered

| | Rejected alternative | Why rejected |
|---|---|---|
| A-only | `companyconcept` reshape as the sole source (the original BACKLOG plan) | No dei fiscal calendar → would rebuild the per-fact fiscal-labeling logic that took 3 patch rounds + a branch review to converge, in a second divergent copy; writes a possibly-mislabeled fiscal year into an append-only store (one-way door). Probe disproved its premise that flat totals are unavailable per-filing. |
| Naive flat pass-through | Emit every flat revenue-shaped fact as its own series | Probe: JPM would mint 5 bogus "total revenue" series from income-statement components. |
| Include qualifier-only facts | Treat `Revenues` under a consolidation member as the total | Probe: XOM 452,209M vs true 332,238M; JPM parent-only 53,036M. |
| Concept-keyed `kpi_id` | Reuse `derive_kpi_id`'s empty-dimensions bare-concept slug | Fragments a filer's durable series across a tagging change; `kpi_id` is a one-way door. |

## What Becomes Obsolete (remove in this change)

- `docs/loom/BACKLOG.md` §"company total (top-line) revenue lane" — its premise
  ("the only shipped source is `action_facts(ticker,'Revenues')`") is
  probe-disproved; rewrite to the two-lane decision.
- `kpi_xbrl_ingest.py:152-153` — the `continue` that skips flat facts, plus its
  "OUT OF SCOPE this arc" comment.
- `derive_kpi_id`'s docstring sentence "that case is OUT OF SCOPE for the
  driver (skipped before this is called)" (`kpi_xbrl_ingest.py:96-97`).
- The arc (d) brief's §Out of Scope top-line entry — mark superseded.

## Open Questions

1. **Placement (plan-time)**: does the top-line lane live inside
   `extract_dimensional_revenue` (shares the filing fetch → preserves the
   zero-marginal-cost property) or in a sibling function (cleaner boundary,
   duplicate fetch)? Leaning shared-fetch.
2. **52/53-week annual rows** (COST/WMT): confirm the annual top-line needs no
   `duration_weeks` handling beyond what the shared builder already emits.
3. **Version + base freshness**: PR #612 is OPEN at 2.35.0, so this arc is
   **2.36.0**; if #612 merges mid-arc, rebase onto `origin/main` before review
   (memory `new-arc-branch-bases-on-origin-main-not-merged-tip`; the #610
   precedent from arc (d)).
   *(RESOLVED 2026-07-25, before implementation started: #612 merged as
   `fa37de6b`; the arc branch `feat-total-revenue-lane` was cut at that SHA, so
   2.36.0 is confirmed and no mid-arc rebase was needed at kickoff.)*

## Sources

- XBRL US — Revenue Guidance: https://xbrl.us/data-rule/guid-revenue/ (EN)
- XBRL US — Guiding Principles for Element Selection:
  https://xbrl.us/home/priorities/data-quality/rules-guidance/principles/ (EN)
- Fidelity — Introduction to Compustat:
  https://www.fidelity.com/learning-center/trading-investing/fundamental-analysis/introduction-to-compustat (EN)
- *Lost in standardization* (Journal of Accounting & Economics, 2022):
  https://www.sciencedirect.com/science/article/abs/pii/S0165410122000969 (EN)
- piqcy — 財務分析に欠かせない、XBRLの構造を理解する:
  https://note.com/piqcy/n/nf66dbe290ada (JA)
- EDINET DB — 日本の有価証券報告書 XBRL を構造化するときに直面する 4 つの課題:
  https://edinetdb.jp/blog/xbrl-japan-securities-reports-structuring (JA)
