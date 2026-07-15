# Brief — operational-kpi tier-② pilot: real SEC XBRL (flat + dimensional) into the pipeline

Status: brainstorming output, awaiting sign-off → `writing-plans`. User signed off "proceed with
your recommendation (甲): build tier-② now; defer pre-2010 LLM extraction research."
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), **tier-② pilot** (first
real-data crossing, dimensional). The 9 offline slices shipped in investing-toolkit 2.18.0
(#567). This feeds them REAL Apple XBRL — flat concepts AND dimensional (product-line) facts.
Spec: `docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Design-side on-ramp

Axis 0: brownfield increment on an already-specced capability. No new design-side station.
Proceed direct. Empirical grounding: 4 live probes (Apple deep-dive + 8-company cross-section +
Apple 2007-2025 history + 8-company history) — findings baked into Current State Evidence.

## Problem

**Job:** *When I research a company, I want its own operating metrics — including company-
specific ones (iPhone / Gaming / Passenger revenue) — as a CORRECT multi-year trend read
straight from SEC's authoritative structured XBRL, so I can judge the trajectory, with the tool
(a) never fabricating a missing figure, and (b) never naively splicing across a segment/concept
reorganization into a misleading line.*

This tier-② pilot proves the 9-module machinery works end-to-end on REAL Apple XBRL, using the
data source that is its own ground truth (SEC-tagged), and — critically — handles the
**structural churn** that every company exhibits (verified across 8 companies: every one
reorganized segments/product-categories 1–3× over 2010–2025; concept + axis-namespace + member
names all change across eras). No LLM, no HTML-table extraction, no manual labeling.

## Users

**Job story:** *When I point the toolkit at AAPL, I want `iphone_revenue` as one continuous
logical KPI stitched across its two XBRL eras — `SalesRevenueNet` + `us-gaap:ProductOrServiceAxis`
+ `AppleIphoneMember` (FY2009–2017) → `RevenueFromContractWithCustomerExcludingAssessedTax` +
`srt:ProductOrServiceAxis` + `aapl:IPhoneMember` (FY2018–2025) — with the 2018 reorganization
handled as a declared definitional break (dual series, never naive concat); and `gross_profit`
as a simple flat single-concept trend — both trusted-by-source, both verifiable against SEC.*

Consumer: the equity-memo pipeline (a TRUSTED memo feed of filing-native KPI trends).

## Smallest End State

Two layers, honoring the toolkit's data/analysis split (CLAUDE.md cross-plugin contract):

**Data layer (I/O, edgartools — extends the existing `sec_edgar_client` / `data-markets`):**
1. A dimensional-revenue **fact-pack extractor** — given a ticker + form, fetch the filing's
   XBRL facts and emit a normalized JSON fact-pack: a list of `{concept, axis, member, value,
   period, fiscal_year, accession, filed}` for every revenue fact carrying a product/segment/geo
   axis (BOTH `us-gaap:*` and `srt:*` namespaces — the Apple false-negative lesson: never filter
   one namespace). Pure I/O, no analysis, no filtering-to-fabricate.

**Analysis layer (pure-compute, stdlib-only, `analysis-kpi` — mirrors kpi_validate/kpi_parse):**
2. **Fact → points adapter** `kpi_xbrl.extract_points(fact_pack, binding, company)` → kpi_store
   points. Maps XBRL provenance into the point shape: `source_accession` = `accession`,
   `source_table_id` = the axis (e.g. `xbrl:srt:ProductOrServiceAxis`), `source_cell_ref` =
   `concept|member` (the "cell" for a dimensional XBRL fact IS the concept+member),
   `as_of` = `filed` (accession-derived, NOT wall-clock), `source_kind` = `"xbrl-dimensional"`
   (or `"xbrl-companyfacts"` for flat). FAIL LOUD on a missing/malformed fact — never a 0.
3. **Era-specific binding** — one logical KPI (`iphone_revenue`) binds an ORDERED list of era
   source tuples `[(concept, axis, member, fy_range)...]`; the adapter resolves each fact to its
   logical kpi_id, emitting points under one id across eras (a multi-facet remap: concept + axis
   + member all differ across the boundary).
4. **Declared structural break** — the binding declares a definitional break at the
   reorganization boundary (2018 for Apple products; universal across companies). Injected as a
   pre-APPLIED break so the existing `split_series`/dual-series (slice 6/7) produces a correctly
   segmented as-reported trend — NEVER a naive concat. A value-anomaly detector would miss this
   (it is definitional, not a value jump); the break is declared from the binding.
5. **Trusted-by-source** — a point whose `source_kind ∈ {xbrl-companyfacts, xbrl-dimensional}`
   is trusted by source: `kpi_gate` recognizes these source_kinds as auto-qualifying (no sampled
   label set). The gate stays meaningful for tier-③ (narrative, LLM-located). One gate change.
6. **End-to-end demonstration** (a test + thin CLI): real Apple → `iphone_revenue` (the full
   case: dimensional, spans the 2018 declared break, dual series) + `gross_profit` (the simple
   flat single-concept case) — proving the 9-module chain on live data.

**Explicitly NOT in this slice:** LLM-locate; HTML/10-K table extraction; non-dollar operational
KPIs (units/subscribers/deliveries — verified narrative-only across 8 companies, tier-③);
pre-2010 filings (no XBRL — text-parsing, deferred to the LLM-extraction research the user
parked); auto-DISCOVERY of a company's segment reorganizations (the pilot DECLARES Apple's
binding + break by hand — a catalog/auto-detector is a later slice); non-US markets; archiving.

## Current State Evidence

- **Forward (consumer):** `kpi_memo_feed.build_memo_feed` requires per-point provenance
  completeness (`source_accession/source_table_id/source_cell_ref`, `kpi_memo_feed.py:77`) →
  the adapter's XBRL→provenance mapping (End State #2) satisfies it, no schema change.
- **Reverse (sibling pattern):** `kpi_validate.py` / `kpi_parse.py` are the pure-compute,
  stdlib, data-as-arg precedent the new `kpi_xbrl.py` follows (no `_store_fs`, no network).
  Append target: `kpi_store.append(point)` (`kpi_store.py:158`). The data-layer extractor
  follows `sec_edgar_client.py` (edgartools, already in the toolkit for xval/sec_narrative).
- **Error (fail-loud):** `kpi_store.append` enforces provenance completeness
  (`_require_provenance`, `kpi_store.py:116`) + accession-derived non-wall-clock `as_of`
  (`_require_accession_derived_as_of`, `kpi_store.py:128`). The break/dual-series machinery is
  `kpi_break.py` / `kpi_series.py` (slices 6/7) — the declared break reuses their APPLIED path.
- **Data (verified live — 4 probes):**
  - XBRL floor is **2010** universally (8/8 companies); dimensional revenue reliably present
    **~FY2011–2014** (some back to FY2008 via MSFT/JPM 2010–2011 filings); **pre-2010 = no XBRL**;
    pre-mid-1990s / pre-IPO = no filing.
  - Apple product revenue spans TWO tagging regimes: `SalesRevenueNet`+`us-gaap:ProductOrServiceAxis`
    +`AppleIphoneMember` (FY2009–2017) → `RevenueFromContract`+`srt:ProductOrServiceAxis`+
    `aapl:IPhoneMember` (FY2018+), plus a product-category redefinition (~FY2019 Other→Wearables).
  - **Structure churn is universal** (8/8 reorganized segments/categories 1–3×) — the era-binding
    + declared-break design is core, not an Apple special case.
  - Non-dollar operational KPIs (units/subscribers/deliveries/load-factor/same-store) are NOT
    XBRL-tagged across 8/8 — narrative-only (tier-③, out of scope).
  - kpi_store point shape: `{company, kpi_id, period, value, as_of, source_accession,
    source_table_id, source_cell_ref, ...}`; dedup key `(company, kpi_id, period, as_of,
    source_accession)` (`kpi_store.py:151`). Real dimensional fact shape (edgartools dataframe):
    `{concept, dim_<axis>: member, numeric_value, fiscal_year, period_end, accn, filed}`.
- **Boundary:** `source_kind` is a new point field the gate must learn (End State #5) — the one
  gate-behavior change. The era-binding spec is new config (not in `kpi_schema` yet — pilot keeps
  it adapter-config; formalizing into kpi_schema is a later slice).

Evidence paths: `investing-toolkit/skills/analysis-kpi/scripts/{kpi_store,kpi_memo_feed,kpi_gate,
kpi_break,kpi_series,kpi_validate,kpi_parse}.py`, `investing-toolkit/skills/data-markets/scripts/
sec_edgar_client.py`, live `data.sec.gov` XBRL (CIK0000320193 + 7 others), the 4 probe scripts +
result JSONs in the session scratchpad.

## Decision

Build a two-layer tier-② pilot: (data) an edgartools dimensional-revenue fact-pack extractor
alongside the existing sec_edgar_client; (analysis) a stdlib pure-compute `kpi_xbrl.py` adapter
that maps dimensional/flat XBRL facts to fail-loud, provenance-mapped, trusted-by-source
kpi_store points, resolves an era-specific logical-KPI binding, and declares a structural break
at a reorganization boundary so the existing dual-series machinery yields a correct (non-naive)
trend. Teach `kpi_gate` that XBRL source_kinds are trusted-by-source. Prove end-to-end on Apple's
real `iphone_revenue` (spanning the 2018 declared break) + `gross_profit`.

**We will NOT:** run any LLM; extract HTML tables; pull non-dollar operational KPIs; parse
pre-2010 filings; auto-discover reorganizations (declare Apple's by hand); fabricate labels for
SEC data; naively concat across the break; change the point schema (map into existing fields).

## Alternatives Considered

- **Reliability gate for XBRL-native values** — (a) trusted-by-source via `source_kind` the gate
  auto-qualifies **[chosen]**; (b) uniform label+min_samples gate (rejected — fabricating labels
  for authoritative filings is absurd); (c) separate no-gate path (rejected — drift). Grounded:
  XBRL US DQC rules treat tagged facts as authoritative source-of-record.
- **Cross-era logical-KPI continuity** — (a) era-specific binding + declared definitional break +
  dual-series **[chosen]**; (b) naive concat (rejected — user's explicit non-goal; DQC_0067 says
  the concepts are mutually exclusive; verified misleading across the Apple 2018 + 8-company
  reorganizations); (c) single-era-only (rejected — discards ~10yr of real history). Grounded:
  XBRL US DQC_0067 (`xbrl.us/data-rule/dqc_0067/`) + the 8-company churn finding.
- **Companyfacts flat API vs XBRL instance parse** — companyfacts drops dimensions (flattens),
  so product-line revenue is NOT retrievable there; the pilot parses the XBRL instance via
  edgartools **[chosen for tier-②]**; flat companyfacts still used for the simple `gross_profit`
  case (both feed the same adapter via source_kind).

## What Becomes Obsolete

Nothing removed — additive. Makes operational-kpi real on a live filing, delivers company-
specific KPIs (iPhone revenue) deterministically, and validates the slice-6/7 break/dual-series
machinery on the universal, industry-recognized reorganization problem.

## Out of Scope

- LLM-locate; HTML/table extraction; non-dollar operational KPIs; pre-2010 text parsing;
  auto-discovery of reorganizations; formalizing the binding into kpi_schema; non-US markets;
  tier-③ labeling; archiving.

## Open Questions

1. **Which proof KPIs?** Default: `iphone_revenue` (dimensional, spans the 2018 declared break —
   the full case) + `gross_profit` (flat single-concept — the simple case). Confirm in plan; the
   adapter is binding-agnostic so the set is config, not code.
2. **Fixture vs live in tests?** Default: the analysis-layer core is TDD'd against a REAL captured
   fixture (Apple facts from the probes); the data-layer extractor + end-to-end demo hit live
   edgartools behind a `network` marker (mirrors the existing live-test convention). Confirm in plan.
