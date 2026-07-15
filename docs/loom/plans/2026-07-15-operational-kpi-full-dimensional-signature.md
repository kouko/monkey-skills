# Plan: operational-kpi full dimensional-signature extraction + exact-match binding

Source brief: docs/loom/specs/2026-07-15-operational-kpi-full-dimensional-signature.md
Total tasks: 7
Critical-path depth: 4 (≤5)   ← T1→T2→T3→T7 (analysis) and T4→T5→T6→T7 (data), joining at T7
Execution order: parallel-where-possible (Wave 1 = T1 + T4, disjoint files)
Plan-document-reviewer verdict: PASS (2026-07-15; 12/12 applicable; fixture magic values +
sec_edgar_client line numbers verified. One feasibility advisory heeded → Task 4 note below.
Post-PASS additive amendment: Task 4 note added — additive/clarifying, DAG + fields unchanged,
re-review skipped per the amend-a-PASS-plan rule.)

Notes:
- REAL fixture committed: investing-toolkit/tests/analysis/fixtures/xbrl_signature_factpack.json
  (machine-captured exact integers, never hand-typed — the pilot's hand-fixture fabrication lesson
  applied). NFLX cross-dim: {ProductOrService:StreamingMember} total = 45183036000 (FY2025) /
  39000966000 (2024) / 33640458000 (2023) vs region slices {Streaming, StatementGeographical:X}
  (US&Canada 19957152000, EMEA 14514646000, LatAm 5357521000, AsiaPacific 5353717000 @2025 — the
  four regions sum EXACTLY to the total). AAPL: {ProductOrService:IPhoneMember} 209586000000@2025
  (matches the pilot's corrected value — cross-check); {StatementBusinessSegments:AmericasSegmentMember}
  with consolidation=OperatingSegmentsMember = 178353000000@2025.
- Full-signature fact shape: {concept, dimensions:{axis_localname: member}, consolidation:member|null,
  value, period_end, fiscal_year, accession, filed} — `dimensions` = REAL breakdown axes only
  (ProductOrService/StatementBusinessSegments/StatementGeographical/Subsegments); `consolidation` =
  the srt:ConsolidationItemsAxis reconciliation qualifier (NOT a breakdown), captured separately.
- kpi_xbrl.py stays PURE COMPUTE stdlib; sec_edgar_client.py is the data layer (edgartools, network).
- This slice REPLACES the pilot's single-{axis,member} model in the same change (What Becomes Obsolete).
- TASK 4 FEASIBILITY NOTE (plan-doc-reviewer advisory #1, heeded): build the full signature from the
  edgartools dataframe's PER-ROW `dim_<axis>` columns (e.g. `dim_srt_ProductOrServiceAxis`,
  `dim_srt_StatementGeographicalAxis`) — the capture probe (2026-07-15) CONFIRMED multiple `dim_<axis>`
  columns are populated on ONE row (a single NFLX row carried both ProductOrService=Streaming AND
  Geographical=US&Canada), so NO context_ref/fact_id group-by is needed. Do NOT read the singular
  `dimension`/`member` convenience columns (they expose only one axis — the wrong-layer trap the repo's
  SEC-narrative slice recorded). The T4 implementer must live-verify the dim_<axis> multi-column shape
  before/while building (a real edgartools row, not only the sys.modules mock).

## Task 1 — resolve_binding exact-signature match (de-conflate NFLX)
- Description: Change `kpi_xbrl.resolve_binding` so a source's `dimensions` map EXACT-matches a
  fact's real-breakdown `dimensions` (an empty binding `dimensions` = the top-level total; a
  fact with extra breakdown axes does NOT match). Replaces the pilot's single concept+axis+member
  match. A source now = {concept, dimensions:{axis: member,...}}. Reuse facts_to_points for emission.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
  - investing-toolkit/tests/analysis/fixtures/xbrl_signature_factpack.json
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_xbrl.py::test_resolve_binding_exact_signature_deconflates
  - GREEN: a binding for `streaming_revenue` with sources dimensions EXACTLY
    {"ProductOrService":"StreamingMember"} resolves ONLY the 3 total facts (values 45183036000 /
    39000966000 / 33640458000, periods 2025/2024/2023) — NOT the region slices; a binding with
    dimensions {"ProductOrService":"StreamingMember","StatementGeographical":"UnitedStatesAndCanadaMember"}
    resolves ONLY the US&Canada slice (19957152000@2025). Exactly 3 points each, no conflation.
- External surfaces: stdlib only.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #2 "resolve_binding exact-match on the signature (empty
  dims = top-level total; de-conflates NFLX total vs slice)".

## Task 2 — anti-fabrication: >1 value for a bound (signature, period) RAISES
- Description: Extend `resolve_binding` so that if a bound signature matches MORE THAN ONE fact for
  the same (signature, period) — i.e. two distinct values that both satisfy the exact signature in
  one period — it RAISES a ValueError naming the kpi_id + period (never silently pick one). An
  unmatched signature stays skipped (unchanged). This is the anti-fabrication guard extended to
  signatures — an unseen ambiguity fails loud.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Acceptance:
  - RED: ...::test_resolve_binding_raises_on_ambiguous_signature_period
  - GREEN: a fact-pack with two facts sharing the SAME exact signature AND the same period but
    different values, bound by that signature, makes `resolve_binding` RAISE ValueError naming the
    period; a single-value signature+period still resolves cleanly.
- External surfaces: stdlib only.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #6 "a bound signature matching >1 value for (signature,
  period) RAISES, unmatched skipped".

## Task 3 — ConsolidationItems qualifier handling (operating-segments view)
- Description: In `resolve_binding`, treat the fact's `consolidation` (srt:ConsolidationItemsAxis
  member) as a reconciliation QUALIFIER, NOT part of the breakdown signature: a segment binding
  (dimensions {StatementBusinessSegments: X}) resolves the OperatingSegmentsMember-qualified fact,
  and RAISEs if both an operating-segments value AND another consolidation view match the same
  signature+period (ambiguous). The binding may specify a `consolidation` to disambiguate; default
  = OperatingSegmentsMember.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
  - investing-toolkit/tests/analysis/fixtures/xbrl_signature_factpack.json
- Acceptance:
  - RED: ...::test_resolve_binding_consolidation_qualifier_operating_segments
  - GREEN: a binding for `americas_segment_revenue` dimensions
    {"StatementBusinessSegments":"AmericasSegmentMember"} resolves the OperatingSegmentsMember-
    qualified fact (178353000000@2025) — the ConsolidationItems qualifier is NOT treated as a
    second breakdown axis (so the segment is not falsely cross-dim), and a single clean point results.
- External surfaces: stdlib only.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: Smallest End State #3 "ConsolidationItems qualifier handling (operating-
  segments view, RAISE on ambiguity)".

## Task 4 — extractor emits the full-signature fact-pack
- Description: Change `sec_edgar_client._build_dimensional_revenue_fact` (+ `_is_dimensional_revenue_fact`)
  so each emitted fact carries a `dimensions` map of ALL real breakdown axes present
  (ProductOrService/StatementBusinessSegments/StatementGeographical/Subsegments, keyed by axis
  local name) AND a separate `consolidation` field (the srt:ConsolidationItemsAxis member, or None)
  — replacing the single `{axis, member}`. period_end fail-loud + fiscal_year-from-period_end unchanged.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py,
  investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
  - investing-toolkit/tests/analysis/fixtures/xbrl_signature_factpack.json
- Acceptance:
  - RED: investing-toolkit/tests/data/test_sec_edgar_dimensional.py::test_build_fact_full_signature
  - GREEN (offline, via a mocked/synthetic edgartools row through the sys.modules-mock convention):
    a row carrying ProductOrService=Streaming AND Geographical=US builds a fact with
    dimensions={"ProductOrService":"StreamingMember","StatementGeographical":"...US..."} and
    consolidation=None; a row with BusinessSegments=X AND ConsolidationItems=OperatingSegments builds
    dimensions={"StatementBusinessSegments":"X"} + consolidation="OperatingSegmentsMember" (the
    consolidation axis is NOT in `dimensions`).
- External surfaces: edgartools==5.42.0 (data-layer only; the offline test mocks it via sys.modules).
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #1 "full-signature fact-pack in the extractor (dimensions
  map = all real breakdown axes; ConsolidationItemsAxis captured separately as a qualifier)".

## Task 5 — _is_revenue_concept excludes deferred-revenue pollution
- Description: Tighten `sec_edgar_client._is_revenue_concept` (:1845) to EXCLUDE contract-liability /
  deferred-revenue reconciliation concepts (`ContractWithCustomerLiabilityRevenue*` and similar
  rollforward items) that merely CONTAIN "Revenue" but are not operating revenue, while keeping the
  real revenue concepts (RevenueFromContract… / SalesRevenueNet / Revenues / RevenuesNetOfInterestExpense… /
  AdvertisingRevenue).
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py,
  investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Acceptance:
  - RED: ...::test_is_revenue_concept_excludes_deferred_revenue
  - GREEN: `_is_revenue_concept` is True for us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax,
    SalesRevenueNet, Revenues, RevenuesNetOfInterestExpense, AdvertisingRevenue; and FALSE for
    us-gaap:ContractWithCustomerLiabilityRevenueRecognized and
    ContractWithCustomerLiabilityRevenueRecognizedExcludingOpeningBalance.
- External surfaces: stdlib only (pure predicate).
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: Smallest End State #4 "_is_revenue_concept excludes ContractWithCustomerLiabilityRevenue*/
  deferred-revenue pollution".

## Task 6 — extract only from an exact 10-K (skip 10-K/A amendment)
- Description: Make `extract_dimensional_revenue` select the latest filing whose form is EXACTLY
  "10-K" (not "10-K/A"), so an amendment does not shadow the real annual report (TSLA's `.latest()`
  returned a 0-dimensional 10-K/A). If no exact 10-K exists, return the existing loud error slot.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py,
  investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
  - investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py
- Acceptance:
  - RED: ...::test_extract_dimensional_revenue_tsla_skips_amendment_live
  - GREEN (network-marked): `extract_dimensional_revenue("TSLA")` returns a fact-pack from a form
    exactly "10-K" (asserting the selected filing's accession/form is a 10-K, not a 10-K/A) with a
    non-empty facts list (dimensional revenue present) — OR the loud error slot if genuinely none;
    the offline suite stays green (this live test is @pytest.mark.network, deselected).
- External surfaces: edgartools==5.42.0 (network — SEC EDGAR filings list).
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: Smallest End State #5 "extract only from an exact 10-K (not 10-K/A)".

## Task 7 — rewire the pilot iphone_revenue binding + live e2e to full signatures
- Description: Update the pilot's iphone_revenue binding (in kpi_xbrl / the e2e test) to the new
  full-signature shape {ProductOrService: IPhoneMember} (exact), and update
  test_kpi_xbrl_e2e_live.py so the live chain uses full-signature bindings; ADD a live assertion
  that a NFLX streaming_revenue full-signature binding resolves the TOTAL only (one value per year,
  > 30e9), proving live de-conflation end-to-end. Keep the existing pilot behavior green.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/tests/analysis/test_kpi_xbrl_e2e_live.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
  - investing-toolkit/tests/analysis/test_kpi_xbrl_e2e_live.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_xbrl_e2e_live.py::test_nflx_streaming_deconflated_end_to_end_live
  - GREEN (network-marked): the live chain with a full-signature streaming_revenue binding
    ({ProductOrService: StreamingMember}, exact) yields ONE streaming total per period (> 30e9, not
    the conflated multi-value), and the existing AAPL iphone_revenue e2e (now {ProductOrService:
    IPhoneMember}) still passes; offline suite stays green.
- External surfaces: edgartools==5.42.0 (network; via the extractor).
- Dependencies: Tasks 3, 6 complete first
- Independent: false
- Brief item covered: Smallest End State "the pilot's iphone_revenue binding rewritten as a full
  signature" + What Becomes Obsolete (single-member model replaced in the same change).
