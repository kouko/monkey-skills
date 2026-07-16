# Plan: operational-kpi-quarterly (scope B)

Source brief: docs/loom/2026-07-16-operational-kpi-quarterly/specs/operational-kpi-quarterly/spec.md (loom-spec change-folder, validate_spec_output exit-0)
Total tasks: 12
Critical-path depth: 5 (≤5)   ← T1→T5→T6→T8→T11
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-16, round 2 — coverage script exit-0, 14/14 checks)

Branch: feat-operational-kpi-quarterly (based on origin/main 5fdc188d, scope-A 2.21.0).
Fixtures: MACHINE-CAPTURED from real filings, sampled from the verification universe
(docs/loom/references/xbrl-verification-universe.md). Run pytest PYTHONDONTWRITEBYTECODE=1;
git from repo root. Analysis-layer tests that import the data layer MUST stub requests+edgar
in sys.modules before import (offline-import gotcha, docs/loom/memory/importing-a-module-runs-its-module-level-imports.md).
Data-layer tasks T1-T4,T10 all touch sec_edgar_client.py (same file → sequential in SDD, but
no inter-task Dependencies → one DAG level). period from period_end, never fiscal_year/fiscal_period.

## Task 1 — Emit duration_months per fact
- Description: In `_build_dimensional_revenue_fact`/extract, emit each fact's `duration_months` (period_end − period_start span), exclude instant contexts from the duration-flow output, and fail loud on a missing/malformed period_start.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py, investing-toolkit/tests/data/fixtures/xbrl_quarterly_msft.json
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (_build_dimensional_revenue_fact ~:1939, extract_dimensional_revenue ~:1985)
- Acceptance:
  - RED: `test_extract_emits_duration_months` — a fact carries duration_months (3 for a 3-month context, 9 for a 9-month, 12 for annual); an instant-context fact is excluded; a malformed period_start raises loudly.
  - GREEN: duration_months present + correct; instant excluded; malformed raises.
- External surfaces: edgartools (network) — period_start/period_end/period_type columns of facts.to_dataframe(); fixture machine-captured from a real MSFT Q3 10-Q (dual-duration confirmed live).
- Dependencies: none
- Independent: false  # same file as T2-T4,T10
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period duration is emitted per fact / Scenario: 10-Q carries both a 3-month and a YTD context
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period duration is emitted per fact / Scenario: annual fact keeps a 12-month duration
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period duration is emitted per fact / Scenario: instant (balance) context is excluded from the revenue flow
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period duration is emitted per fact / Scenario: missing period_start fails loud

## Task 2 — Revenue-concept allow/deny + $-unit filter fix (folds scope-A bug)
- Description: Replace `_is_revenue_concept`'s substring test with an ALLOW-list of legit operating-revenue concepts (incl. us-gaap:Revenues, RevenuesNetOfInterestExpense, RevenueNotFromContractWithCustomer, RevenueFromContractWithCustomerIncludingAssessedTax, recognized extensions) + a DENY-list (CostOfRevenue/COGS incl. OtherCostOfOperatingRevenue, *Percentage/*ChangePercent, RemainingPerformanceObligation, deferred-revenue liabilities, CollaborativeRevenue) + a $-unit guard rejecting non-currency (percentage/ratio) facts.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py, investing-toolkit/tests/data/fixtures/xbrl_concept_filter_cases.json
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (_is_revenue_concept ~:1857, _DEFERRED_REVENUE_CONCEPT_PREFIXES)
- Acceptance:
  - RED: `test_revenue_concept_filter_deny_allow_unit` — a dimensioned CostOfRevenue fact (CAT) is excluded; a *RevenuePercentage fact (BA/HON) is rejected by the $-unit guard; a RevenueNotFromContractWithCustomer fact (XOM) is KEPT.
  - GREEN: deny/allow/$-unit all hold; existing revenue extraction unregressed.
- External surfaces: edgartools (network) — fixture machine-captured from CAT (dim CostOfRevenue), BA/HON (percentage), XOM (RevenueNotFromContract), SBUX (deferred).
- Dependencies: none
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Revenue-concept matching is an allow/deny + $-unit gate, not a substring (folds a scope-A fix) / Scenario: dimensioned CostOfRevenue is not emitted as revenue
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Revenue-concept matching is an allow/deny + $-unit gate, not a substring (folds a scope-A fix) / Scenario: a percentage-valued *Revenue* concept is rejected by the unit guard
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Revenue-concept matching is an allow/deny + $-unit gate, not a substring (folds a scope-A fix) / Scenario: a legitimate non-RFCC revenue concept is kept

## Task 3 — Read fiscal calendar per-filing from dei tags
- Description: Emit each filing's `dei:DocumentFiscalPeriodFocus` + `dei:CurrentFiscalYearEndDate` onto the fact-pack (per filing), never caching/hardcoding the FYE per ticker (it drifts for 52/53-week filers; nominal for floaters).
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (the dei extraction path; extract_dimensional_revenue return)
- Acceptance:
  - RED: `test_extract_emits_dei_fiscal_calendar` — the pack carries the filing's DocumentFiscalPeriodFocus + CurrentFiscalYearEndDate; two filings from one 52/53-week filer with differing dei FYE (--01-31 vs --01-25) each keep their own value (not one cached).
  - GREEN: dei fields present per filing; no cross-filing caching.
- External surfaces: edgartools (network) — dei string facts (absent from bulk companyfacts; read via filing.xbrl()); fixture from NVDA (drifting FYE) + AAPL (Sep).
- Dependencies: none
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The fiscal calendar is read per-filing from dei tags, never cached per ticker / Scenario: non-December fiscal-year-end classifies by the filing's dei calendar
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The fiscal calendar is read per-filing from dei tags, never cached per ticker / Scenario: fiscal-year-end is read per-filing, not cached

## Task 4 — ADR / 20-F regime detect → explicit N/A
- Description: Detect a foreign-private-issuer ticker (submissions history has 20-F + 6-K, no 10-Q) and return an explicit quarterly-N/A with reason, never a silently-empty series.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (company.get_filings form enumeration ~:2025)
- Acceptance:
  - RED: `test_quarterly_foreign_filer_returns_na` — a ticker whose submissions have 20-F+6-K but no 10-Q (TSM) returns an explicit "no quarterly XBRL (foreign 20-F/6-K regime)" N/A with reason, not empty/fabricated.
  - GREEN: N/A-with-reason returned; not silently empty.
- External surfaces: edgartools (network) — submissions form histogram; fixture from TSM.
- Dependencies: none
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A foreign/ADR filer with no 10-Q is detected and returned N/A, never silently empty / Scenario: a 20-F-only filer returns an explicit quarterly-N/A

## Task 5 — Classify period_type from period_end + dei
- Description: In the analysis layer, classify each fact's period_type (Q1/Q2/Q3/FY) + cumulative flag + duration_class (3mo / 6mo-YTD / 9mo-YTD / 12mo-FY) from its duration_months + period_end relative to the dei fiscal calendar; comparatives classified from their own period_end (not the filing focus); an unclassifiable/stub period is surfaced, not guessed.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (_require_period ~:121, facts_to_points ~:151)
- Acceptance:
  - RED: `test_classify_period_type` — 3mo at fiscal Q1 end → Q1/single; non-Dec (Sep) 3mo ending late-Dec → Q1; 9mo → 9mo-YTD/cumulative; 6mo → 6mo-YTD/cumulative; a comparative fact classified from its own period; a stub/unclassifiable period surfaced.
  - GREEN: period_type + duration_class + cumulative correct across the cases; unclassifiable surfaced.
- Dependencies: Tasks 1, 3 complete first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period type is classified from duration and the fiscal calendar / Scenario: 3-month fact at a fiscal quarter end
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period type is classified from duration and the fiscal calendar / Scenario: non-December fiscal year end shifts the quarter boundaries
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period type is classified from duration and the fiscal calendar / Scenario: a 9-month fact is a YTD cumulative, not a single quarter
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period type is classified from duration and the fiscal calendar / Scenario: a 6-month fact is an H1 YTD cumulative (critic-found)
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period type is classified from duration and the fiscal calendar / Scenario: a transition or unclassifiable period is surfaced, not guessed
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The fiscal calendar is read per-filing from dei tags, never cached per ticker / Scenario: a prior-year comparative fact is classified from its own period, not the filing focus

## Task 6 — Identity key gains duration_class; de-conflate single-quarter vs YTD
- Description: Extend the resolve_binding identity key from (signature, period_type, period) to include duration_class so a single-quarter and a YTD fact sharing signature+period_end resolve to DISTINCT points (never deduped/raised against each other); identical cross-filing single-quarter dedupes; a restated quarter applies policy C on the duration-qualified key.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py, investing-toolkit/tests/analysis/fixtures/xbrl_quarterly_dualdur.json
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (resolve_binding dedup loop ~:268-334, the (_PERIOD_TYPE_FY, period_key) identity_key)
- Acceptance:
  - RED: `test_identity_key_deconflates_quarter_from_ytd` — a 3mo and a 9mo fact for one signature ending 9/30 produce two distinct points, neither triggers the >1-distinct-value RAISE against the other; an identical cross-filing single-quarter dedupes; a restated quarter → policy C newest-wins + DQC.
  - GREEN: de-conflation + dedupe + policy-C all correct on the duration-qualified key.
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The identity key de-conflates single-quarter from year-to-date / Scenario: single-quarter and YTD at the same period_end stay distinct
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The identity key de-conflates single-quarter from year-to-date / Scenario: the same single quarter reported in two filings dedupes
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The identity key de-conflates single-quarter from year-to-date / Scenario: a restated quarter across filings applies policy C

## Task 7 — A series carries a single granularity
- Description: build_series_with_break MUST keep annual and quarterly points in separate, granularity-labeled series; a quarterly request returns only sub-annual points; mixing granularities is rejected, never silently averaged/concatenated.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (build_series_with_break ~:296)
- Acceptance:
  - RED: `test_series_single_granularity` — a quarterly request returns only sub-annual points (no FY); a set mixing FY + single-quarter for one fiscal year excludes the off-granularity points (or rejects), never averaged/concatenated.
  - GREEN: single-granularity enforced both ways.
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A series carries a single granularity / Scenario: a quarterly request returns only sub-annual points
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A series carries a single granularity / Scenario: mixing granularities is rejected

## Task 8 — Q4 derive FY−9moYTD, guarded + segregated
- Description: Derive an untagged Q4 single-quarter as (FY − 9-month YTD); flag it as computed AND keep it in a segregated lane so a reported-only request excludes it; skip (never fabricate) when a source is absent OR the FY and 9mo-YTD are basis/vintage/unit-incompatible; record both contributing accessions on the derived point's DQC flag.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py, investing-toolkit/tests/analysis/fixtures/xbrl_q4_derive.json
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (the point-emission + dqc path)
- Acceptance:
  - RED: `test_q4_derive_guarded_segregated` — FY + 9mo-YTD present, no tagged Q4 → emits derived Q4 = FY−YTD9, flagged + segregated (a reported-only request excludes it), DQC records both accessions; 9mo-YTD missing → skip + surface; FY and YTD9 of mismatched vintage/unit → refuse (basis-mismatch flag), never silent subtraction; a directly-tagged Q4 3-month fact present → the reported Q4 is used unchanged, NO derived point emitted (no derivation, no computed flag).
  - GREEN: derive+segregate+guards all hold, and a directly-tagged Q4 short-circuits derivation.
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: Q4 derived when both inputs exist, and segregated
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: a reported-only request excludes derived Q4
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: Q4 not derived when a source is missing
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: a directly-tagged Q4 is used as-is
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: Q4 derivation refuses across mismatched restatement vintages or units (critic-found)
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every emitted point and DQC flag carries structured provenance (critic-found) / Scenario: a derived Q4 records both contributing accessions

## Task 9 — Structured point + DQC-flag schema provenance
- Description: Every emitted series point carries its source accession(s), source form (10-K|10-Q), and duration_class; every DQC flag follows one schema (type, old, new, contributing accession(s), reason); the sub-annual restatement flag carries old→new + both accessions (parity with scope-A policy C).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (facts_to_points point dict ~:178-202, the dqc field)
- Acceptance:
  - RED: `test_point_and_dqc_provenance_schema` — an emitted point carries accession(s) + source form + duration_class; a restatement DQC flag records old, new, and both accessions.
  - GREEN: point provenance + DQC schema present.
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every emitted point and DQC flag carries structured provenance (critic-found) / Scenario: a series point is traceable to its source filing
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every emitted point and DQC flag carries structured provenance (critic-found) / Scenario: a restatement DQC flag carries the full audit content (parity with scope-A policy C)

## Task 10 — Per-filing / per-quarter coverage honesty
- Description: Extend scope-A's coverage report to per-filing/per-quarter completeness within a covered year; distinguish not-yet-filed from fetch-error from out-of-range; flag a dimension present in the 10-K but absent from the 10-Qs as "no quarterly coverage" (distinct from a real zero / discontinued), never zero-filled.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (_dimensional_revenue_coverage from scope-A T2, the coverage key)
- Acceptance:
  - RED: `test_coverage_per_quarter_completeness` — a covered year with 10-K+Q1+Q2 but no Q3 reports partial (3/4, Q3 missing + reason); the three fetch-failure states are distinguished; a 10-K-only dimension is flagged "no quarterly coverage", not zero-filled.
  - GREEN: per-quarter coverage + failure-state distinction + dimension-absent flag.
- Dependencies: Tasks 1, 4 complete first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Coverage honesty extends to per-filing completeness (critic-found) / Scenario: a partial year reports which filings are missing
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Coverage honesty extends to per-filing completeness (critic-found) / Scenario: fetch-failure states are distinguished
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Coverage honesty extends to per-filing completeness (critic-found) / Scenario: a dimension absent from the quarterlies is flagged, not zero-filled

## Task 11 — Offline end-to-end quarterly seam test
- Description: A deterministic offline test driving the full quarterly chain (multi-filing quarterly facts with a dual-duration collision + a derived Q4 → classify → de-conflate identity key → series) over real machine-captured fixtures, asserting single-quarter and YTD stay distinct and a segregated derived Q4 flows through.
- Module: investing-toolkit/tests/analysis/test_kpi_xbrl_quarterly_e2e.py
- Files touched: investing-toolkit/tests/analysis/test_kpi_xbrl_quarterly_e2e.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (facts_to_points, resolve_binding, build_series_with_break)
- Acceptance:
  - RED: `test_quarterly_chain_deconflates_and_segregates_q4` — the assembled chain over the fixtures yields distinct single-quarter + YTD points and a segregated derived Q4. (Stub requests+edgar in sys.modules before importing the data layer.)
  - GREEN: chain produces the de-conflated quarterly series + segregated Q4; no crash.
- Dependencies: Tasks 5, 6, 7, 8, 9 complete first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The identity key de-conflates ... + Requirement: Q4 ... segregated (seam verification per cross-module-field-contracts)

## Task 12 — Live shape-anchor (network-marked)
- Description: A @pytest.mark.network live test capturing the REAL 10-Q dual-duration + dei shape: a recent MSFT (or COST) Q3 10-Q carries a 3mo and a 9mo fact for one dimensional-revenue signature under the same period_end, and the dei fiscal tags are present.
- Module: investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py
- Files touched: investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py
- Context paths:
  - investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py (existing network tests + uv-run pattern)
- Acceptance:
  - RED: `test_quarterly_dual_duration_live` — live fetch returns, for one signature+period_end, both a duration_months=3 and a =9 fact; dei DocumentFiscalPeriodFocus + CurrentFiscalYearEndDate present. Deselected in the offline run.
  - GREEN: live dual-duration + dei confirmed; network-marked.
- External surfaces: edgartools (network, live SEC EDGAR) — real 10-Q; flake budget accepted.
- Dependencies: Tasks 1, 3, 5 complete first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period duration is emitted per fact + Requirement: fiscal calendar read per-filing (live shape-anchor per fixtures-mirror-producer-shape)

## Notes
- DAG levels: L1={T1,T2,T3,T4} (data layer, same file — sequential in SDD, one DAG level).
  L2={T5(dep T1,T3), T10(dep T1,T4)}. L3={T6(dep T5), T12(dep T1,T3,T5)}. L4={T7,T8,T9 (all dep T6)}.
  L5={T11 (dep T5-T9)}. Critical path T1→T5→T6→T8→T11 = depth 5.
- No `Independent: true` pairs: T1-T4/T10 share sec_edgar_client.py; T5-T9 share kpi_xbrl.py; T11/T12
  are separate test files but each depends on multiple predecessors. SDD runs sequentially within each
  same-file group; cross-file groups (data vs analysis) can interleave but are not marked Independent
  to avoid the Check-14 shared-file violation seen in scope A.
- Fixtures per task are machine-captured from the verification-universe tickers named inline; never hand-typed.
- Scope B builds on scope-A's multi-filing fetch (since_year/until_year) — the quarterly path fetches
  10-K + 10-Q; granularity-gated fetching (only fetch 10-Qs when quarterly requested) is a usage-cost
  lever folded into T1/T10's extract path.
