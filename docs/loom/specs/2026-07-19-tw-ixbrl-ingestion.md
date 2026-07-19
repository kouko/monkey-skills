# TW iXBRL Full Ingestion — Brainstorming Brief

Date: 2026-07-19
Stage: loom-code Discovery (brainstorming) → next: spec-expansion / writing-plans
Decision locked with user (2026-07-19, signed off): **收斂版 ② (scoped)** — canonical statements
+ generic fact layer + curated ~5–10 high-value note fields. NOT a full note-reconstruction
engine (annual verification falsified the goldmine-at-scale thesis — see §Annual verification).

## Problem (Axis 1 — JTBD)

The investing-toolkit's TW analysis lane can currently only see **headline three-statement
summaries** (MOPS JSON, ~50–80 fields, consolidated only). Deep TW-equity work — credit,
quality-of-earnings, forensic, related-party/segment analysis — needs the **footnote-level
detail the filing actually contains** but the summary layer structurally drops.

Job story: *When analyzing a TW company in depth, I want the machine-readable footnote
breakdowns the filing already tags (aging, related-party, financial-instrument categories,
tax reconciliation, PP&E, endorsements, Mainland-China investment), so I can assess earnings
quality and balance-sheet composition without hand-reading the PDF.*

## Users (Axis 2)

The toolkit operator running TW equity analysis, wanting parity-and-beyond vs the US EDGAR
lane. Downstream consumers: `report-equity-memo`, `analysis-*`, `domain-teams:investing-team`.

## Current State Evidence (brownfield)

- **Forward (entry/dispatch)**: `pack.py:135` `detect_market()` (.TW→tw), `pack.py:91`
  `MARKET_MODULES`, dispatch `pack.py:408` → `module.build_pack()`. TW entry
  `pack_tw.py:687` `build_pack()`; pack fns at `pack_tw.py:328/404/510/541/632`;
  `SUPPORTED_PACKS` `pack_tw.py:52`, build if-chain `pack_tw.py:697-720`.
- **Reverse (SSOT / what feeds canonical)**: TW statements today come from
  `mops_client.py:57` (MOPS JSON API `mops.twse.com.tw/mops/api`), summary BS/IS/CF at
  `mops_client.py:321+`. Canonical statement mapping is **explicitly deferred**:
  `pack_tw.py:205-311` `_build_canonical_from_yf_financials_tw` ("deferred to a future PR").
  This is the slot to fill.
- **Error/boundary**: caching is fail-open (`cache_util.py:184` `load_cache` returns
  dict|None); MOPS post caching pattern at `mops_client.py:262` `_cached_post`.
- **Data (cache layer)**: `cache_util.py:170` `cache_path(source,key)`, `:184` `load_cache`,
  `:225` `save_cache` (atomic, envelope `{_cache_meta,data}`), TTL `:110`.
- **Reference pattern (US analogue)**: `sec_edgar_client.py:238` `fetch_facts()`,
  `:311` `build_companyfacts_pack()`, CLI `:665` `action_facts`; US-only dimensional XBRL
  work `sec_edgar_client.py:1822+` (feeds `kpi-quarterly`). JP XBRL: `edinet_client.py`,
  `tdnet_client.py`.

## Decision

Build a TW iXBRL ingestion path that mirrors the `sec_edgar_client.py` shape:

1. **Fetch** the full tagged inline-XBRL instance via MOPS **`t164sb01`** — a gate-free
   HTTP GET (no CAPTCHA / form-token / paid E-Shop):
   `https://mopsov.twse.com.tw/server-java/t164sb01?step=1&CO_ID=<id>&SYEAR=<western>&SSEASON=<1-4>&REPORT_ID=C`
   (C=合併/consolidated). Cache via `cache_util`. **Big5 decoding required.**
2. **Parse ALL facts generically** — `ix:nonFraction` + `ix:nonNumeric`, resolving concept,
   context (period/entity), scaling by the iXBRL `scale` attribute (scale-driven — NOT `decimals`,
   which is precision metadata; T1 impl found `PercentageOfOwnership4` disproves decimals-driving),
   unit (TWD).
3. **Fill the deferred canonical builder** (`pack_tw.py:205-311`) with real statement mapping.
4. **Surface a curated ~5–10 high-value note fields** as named concepts pulled directly from
   the generic fact layer (financial-instruments-by-measurement-category, Mainland-China-
   investment + MOEA ceiling, related-party balances + aggregate flows, endorsement/guarantee
   limits, employee-benefit expense). NO general note-table-reconstruction engine — annual
   verification showed the high-value data is a handful of concepts, not many tables.

**Fetch-layer requirements** (tier-agnostic parser; tier logic only here): all market tiers
(上市/上櫃/興櫃/KY) on one `t164sb01` URL; **season fallback** (98-byte "檔案不存在" = period
not filed, iterate seasons; 興櫃 primary = Q2/Q4); **502 retry-with-backoff**. Parser: extract
via `iterparse`/regex over `ix:` tags, never DOM traversal. Financial `-fh` filers captured at
the fact layer but their canonical/note mapping is a deferred sub-arc.

### Measured evidence (TSMC 2330 2024Q3, consolidated, real file)

- 2,002 tagged facts (1,552 numeric + 450 text), 383 distinct concepts.
- Statements ≈436 facts; **notes = 947 facts / 159 distinct `tifrs-notes` elements** + ~116
  `ifrs-full` note concepts; **0 `*TextBlock` dumps** — notes are granular, per-field tagged.
- Note tables present: financial instruments (27 distinct), related-party, receivables aging,
  income tax (6), PP&E, inventories, endorsements/guarantees, Mainland-China investment (TW-specific).
- Axes: only 2 (`ComponentsOfEquityAxis`, allowance-movement). Currency TWD; `decimals=-3` dominant.
- Cross-filer confirmed: Hon Hai 2317 Q3 = 7,462 numeric facts; same URL for any co_id/year/season.
- Taxonomy label reference: `github.com/thstarshine/siiIFRS` (TIFRS 2020-06-30).

### Multi-filer evidence (8 filings measured, 2024Q3 unless noted; method reproduced TSMC baseline exactly)

| Filer | co_id | facts | distinct notes | seg axis | bsci root | TextBlocks |
|---|---|---|---|---|---|---|
| TSMC (baseline) | 2330 | 2,002 | 159 | no | `-ci` | 0 |
| Hon Hai (EMS, multi-seg) | 2317 | 5,929 | 220 | **no** | `-ci` | 0 |
| MediaTek | 2454 | 3,924 | 163 | no | `-ci` | 0 |
| **Cathay FHC (financial)** | 2882 | 2,046 | 96 | no | **`-fh`** | 0 |
| Chunghwa Telecom | 2412 | 2,443 | 142 | no | `-ci` | 0 |
| GlobalWafers (TPEx/OTC) | 6488 | 2,150 | 173 | no | `-ci` | 0 |
| Formosa Plastics | 1301 | 2,237 | 178 | no | `-ci` | 0 |
| TSMC annual | 2330 23Q4 | 1,837 | 177 | no | `-ci` | 0 |

Union of the 7 quarterly filers = **264 distinct `tifrs-notes` elements** (+66% over TSMC's 159).

### Parser-impacting edge cases (confirmed by multi-filer diff)

1. **No segment axis, ever** — multi-segment filers (Hon Hai/Chunghwa) carry the same 2 axes
   as single-segment TSMC. Only 2 dims exist repo-wide (`ifrs-full:ComponentsOfEquityAxis`,
   `tifrs-notes:MovementOnAllowanceForDoubtfulAccounts…`). Do NOT design for segment dims.
2. **Financials use a different statement root** — Cathay swaps `tifrs-bsci-ci`→`tifrs-bsci-fh`,
   adds an insurance/banking concept family (`DepositsFromCustomers`, `LoansDiscountedNet`,
   `ReinsuranceAssets`, `NetInterestIncomeExpense`, `NonPerformingLoansRatio`, `CoverageRatio`),
   has NO gross-margin/cost-of-sales, and drops the allowance axis (1 axis). A ci-only catalog
   silently misses ~90 fh concepts. Statement *structure* differs, not just line items.
3. **Note catalog must be dynamic, not a fixed list** — hardcoding TSMC's 159 under-covers by 66%.
4. **Numbered concept variants** — `CategoriesOfRelatedParties4/5/8`, `Amount6`, `DisposalProceeds3`,
   `_n` suffixes. Catalog must pattern-match `<base><int>`/`_n`, and normalize before counting
   coverage ("distinct note elements" ≠ "distinct note tables").
5. **Hyphens inside localnames** (financials) — `Non-PerformingLoansRatio`,
   `AllowanceForBadDebts-AssetQualityForBankSubsidiaries`. Tokenizers must not split on `-`.
6. **Annual adds a policy-note class** (+18: `BasisOfPreparation`, `RevenueRecognition`, …) but
   filer complexity dominates the seasonal effect.
7. **`REPORT_ID=A` (parent-only) is NOT served by t164sb01** — returns 98-byte "檔案不存在!" for
   every filer/period tested (measured negative). Parent-only lives on a different endpoint.
8. **TPEx (上櫃) needs no special-casing** — identical `t164sb01` URL, HTTP 200 (GlobalWafers).
9. **No TextBlock dumps on any filer** — TW iXBRL is uniformly granular; no escaped-HTML blob path.

### Coverage across market tiers (16 filers measured: 上市/上櫃/興櫃/KY)

- **One code path holds.** 上市 (TWSE), 上櫃 (TPEx), 興櫃 (Emerging/ESM), and KY (foreign-
  registered) all serve on the **same `t164sb01` URL**, same `tifrs-*` taxonomy, same
  ≤2-axis / 0-TextBlock / TWD shape. KY is structurally identical to domestic. The only
  structural fork remains **`bsci-ci` (industrial) vs `bsci-fh` (financial)**.
- **興櫃 filing cadence** — semiannual (Q2/H1) + annual are mandatory; **Q1/Q3 are optional**.
  A 98-byte "檔案不存在" for a 興櫃 Q3 means "not filed that period," not "no such company"
  (verified: 芯測 6786 / 智微 4925 empty at Q3, full at Q2). Recent IPOs (映智 6563 reg.
  2025-03) legitimately have no prior-year filing.
- **Tier-specific logic lives ONLY at the fetch/orchestration layer** (season fallback +
  retry), never in the parser.

### More parser/fetch edge cases (from coverage run)

10. **⚠️ lxml DOM traversal silently drops ~85% of nested `ix:` facts** — `ix:nonFraction`
    nested inside `<td>` is discarded by HTML tree-repair (TSMC DOM-iter=387 vs true=2002).
    **MUST extract via regex or `iterparse` on `ix:` tags, not DOM traversal.** Biggest gotcha;
    a test must assert the total-fact count against a known baseline (2330 2024Q3 = 2002).
11. **Season fallback required** — iterate seasons; treat 98-byte "檔案不存在" as absence, not
    error. Emerging-board primary = Q2/Q4.
12. **Transient HTTP 502** — needs retry-with-backoff at the fetch layer.

## Smallest End State (Axis 3 — "full" delivered in two layers)

- **Layer A — Generic fact extraction** (first ship): every fact (incl. all 159 note
  elements) captured as structured queryable records. *This is "full 附註" at the data layer
  — nothing dropped.* One parser, uniform over all elements.
- **Layer B — Curated high-value note fields** (LOCKED scope, revised after annual verification):
  ~5–10 named concepts pulled directly from Layer A's fact layer — financial-instruments-by-
  measurement-category, Mainland-China-investment + MOEA ceiling, related-party balances +
  aggregate flows, endorsement/guarantee limits, employee-benefit expense. **NO general
  note-table-reconstruction engine** — annual verification (§Annual verification) showed the
  high-value data is a handful of concepts, not many tables; the "forensic" tables (aging
  buckets, tax bridge, PP&E rollforward, inventory write-downs) are absent from the iXBRL at
  any period, so reconstructing them would be a low-yield free-text project, out of scope.

First shippable end state = Layer A + canonical three-statements (industrial `ci`) + the
Layer-B curated field set.

**Statement-root scoping (from multi-filer evidence)**: Layer A is taxonomy-agnostic — it
captures ALL facts for BOTH industrial (`-ci`) and financial (`-fh`) filers uniformly (fh
filers lose nothing at the fact layer). **Canonical three-statement mapping + Layer-B tables,
tranche 1 = industrials (`-ci`) only.** Financial (`-fh`) canonical/table mapping is a
structurally distinct sub-arc (different statement shape, insurance/banking concepts, no
gross-margin) — deferred to a later slice; fh filers are still fully captured at Layer A and
must not crash the pipeline. Note catalog is **discovered dynamically** (pattern-matching
numbered variants), never a hardcoded TSMC list.

## Alternatives Considered (Axis 4)

- **① Summary-only** — rejected: leaves a confirmed free goldmine unused.
- **Middle path (curated tables only)** — folded into Layer-B sequencing rather than a
  separate option.
- **Paid E-Shop bulk XBRL (~NT$40k/mo)** — rejected: cost; t164sb01 is free.
- **Browser-scraping / Arelle-only** — rejected as access mechanism: t164sb01 is a plain GET;
  Arelle optional as a parse engine, but a targeted lxml parser may suffice and avoids a heavy dep.

## What Becomes Obsolete (Axis 5)

- `pack_tw.py:205-311` deferred stub — filled/replaced in the same arc.

## Out of Scope

- **Parent-only (個體) statements** — empirically confirmed NOT served by `t164sb01`
  (98-byte "檔案不存在!" for all filers/periods). Lives on a different endpoint — separate arc;
  handle the not-found response gracefully.
- **Financial (`-fh`) canonical + note-table mapping** — captured at Layer A (facts) but its
  structurally distinct statement/note mapping is a deferred sub-arc; don't build insurance/
  banking canonical now.
- TPEx special-casing — **confirmed unnecessary** (same URL works); no code needed.
- Segment-dimension handling — **confirmed absent** in TW instances; do not build.
- TextBlock/escaped-HTML blob parsing — **confirmed absent** across 8 filers; do not build.
- Taxonomy-version migration logic (2020 vs 2022) beyond what real filings need.
- A US-style dimensional KPI pack for TW — separate later arc.

## Annual verification (falsifies "notes are a machine-readable goldmine at scale")

Measured TSMC + Formosa **annual** (SSEASON=4) filings for the 6 forensic categories missing
in Q3: **0 of 6 unlock in the annual.** Inventory write-downs, tax-rate reconciliation, aging
buckets, PP&E gross/accum-deprec rollforward, pension actuarials, per-counterparty related-party
flows are absent as structured facts in BOTH periods, across fabless AND heavy-industrial filers
(taxonomy/regulatory gap, not business-driven). The annual's +18 elements over Q3 are all
accounting-**policy prose blocks** (`BasisOfPreparation`, `RevenueRecognition`, …), not forensic
facts. **Genuinely valuable note data is concentrated in ~5 categories, period-agnostic**:
financial-instruments-by-measurement-category, Mainland-China-investment-vs-ceiling,
related-party balances + aggregate flows, endorsement/guarantee limits, employee-benefit
*expense* breakdown (+ per-subsidiary NPL for financials, in the deferred fh arc). This is the
basis for scoping ② down to a curated field set rather than a full note-reconstruction engine.

## Open Questions

- **Parse engine — DECIDED by evidence**: targeted `iterparse`/regex over `ix:` tags; NOT lxml
  DOM traversal (drops ~85% of nested facts), NOT Arelle (no heavy dep needed). Confirm in plan.
- Curated high-value field set — confirm the ~5-10 named concepts (candidates above).
- New pack type vs extend `memo-fetch` — decide in writing-plans.
- **Residual (deferred fh arc)**: `bsci` variants beyond `ci`/`fh` (securities dealer, insurer,
  pure financial subsidiary) untested — resolve when the financial sub-arc starts, not now.
- Element→label mapping source: `siiIFRS` (2020-06-30) vs current 2022 taxonomy — version-match.
