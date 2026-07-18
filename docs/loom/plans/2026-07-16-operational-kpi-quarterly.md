# Plan: operational-kpi-quarterly (scope B) — REBUILD (2026-07-18)

Source brief: docs/loom/2026-07-16-operational-kpi-quarterly/specs/operational-kpi-quarterly/spec.md (loom-spec change-folder, validate_spec_output exit-0 after the 2026-07-18 spec-fix + critic-round-2 pass)
Decision record: docs/loom/2026-07-16-operational-kpi-quarterly/rebuild-findings.md (root cause, RESOLVED parallel-label design, resolved sub-questions)
Total tasks: 17 (4 DONE-kept + 13 active)
Critical-path depth: 5 (≤5)   ← T13→T5→T6→T8→T11
Execution order: parallel-where-possible (same-file groups sequential)
Plan-document-reviewer verdict: PASS (2026-07-18 — 14/14 checks; coverage script exit-0)

Branch: feat-operational-kpi-quarterly. Wave-1 T1-T4 KEPT (individually gate-passed, surgical
restart per user decision 2026-07-18); old T10's three commits (46f8ca72, 36d9d45f, f7e45497)
are SUPERSEDED by T18/T19 and will be reset out/replaced during the rebuild.
Fixtures: MACHINE-CAPTURED from real filings, sampled from the verification universe
(docs/loom/references/xbrl-verification-universe.md); the real NVDA range fixture from the
abandoned branch is reusable via `git show 10ff0cbc:investing-toolkit/tests/data/fixtures/xbrl_quarterly_nvda_range.json`.
Run pytest PYTHONDONTWRITEBYTECODE=1; git from repo root; never `git add -A`. Analysis-layer
tests that import the data layer MUST stub requests+edgar in sys.modules before import
(docs/loom/memory/importing-a-module-runs-its-module-level-imports.md).
RED LINES (docs/loom/memory/fiscal-year-derive-per-fact-against-filing-calendar.md): the
fiscal label derives per-fact from its OWN period_end vs the filing's dei calendar — NEVER
`period_end[:4]` (calendar trap), NEVER the filing's DocumentFiscalYearFocus stamped on every
fact (comparatives trap); fail loud on an unreadable calendar, never a calendar fallback.
Plan constants: FISCAL_BOUNDARY_TOLERANCE_DAYS = 10 (covers the live-verified ≤6-day
52/53-week drift with margin, ≪ quarter width; the spec defers the constant to this plan).

## Task 1 — Emit duration_months per fact  [DONE — Wave 1, kept]
- Description: In `_build_dimensional_revenue_fact`/extract, emit each fact's `duration_months` (period_end − period_start span), exclude instant contexts from the duration-flow output, and fail loud on a missing/malformed period_start.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py, investing-toolkit/tests/data/fixtures/xbrl_quarterly_msft.json
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (_build_dimensional_revenue_fact, extract_dimensional_revenue)
- Acceptance:
  - RED: `test_extract_emits_duration_months` — a fact carries duration_months (3/9/12); an instant-context fact is excluded; a malformed period_start raises loudly.
  - GREEN: shipped and gate-passed 2026-07-16/17 (per-task triad PASS).
- External surfaces: edgartools (network); fixture machine-captured from a real MSFT Q3 10-Q.
- Dependencies: none
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period duration is emitted per fact / Scenario: 10-Q carries both a 3-month and a YTD context
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period duration is emitted per fact / Scenario: annual fact keeps a 12-month duration
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period duration is emitted per fact / Scenario: instant (balance) context is excluded from the revenue flow
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period duration is emitted per fact / Scenario: missing period_start fails loud

## Task 2 — Revenue-concept allow/deny + $-unit filter fix  [DONE — Wave 1, kept]
- Description: Allow/deny + $-unit gate replacing the `_is_revenue_concept` substring test. Shipped code already denies `CollaborativeArrangement` (the real GAAP family) and the REIT pro-forma/ladder class the revised spec now names — no code change needed for the 2026-07-18 spec fixes; the renamed deny-list scenario maps here, the NEW synthetic backstop scenario is T21.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py, investing-toolkit/tests/data/fixtures/xbrl_concept_filter_cases.json
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (_is_revenue_concept)
- Acceptance:
  - RED: `test_revenue_concept_filter_deny_allow_unit` — CAT dimensioned CostOfRevenue excluded; BA/HON percentage-named concepts excluded by the deny list; XOM RevenueNotFromContractWithCustomer kept.
  - GREEN: shipped and gate-passed 2026-07-16/17 (per-task triad PASS).
- External surfaces: edgartools (network); fixtures machine-captured from CAT/BA/HON/XOM/SBUX.
- Dependencies: none
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Revenue-concept matching is an allow/deny + $-unit gate, not a substring (folds a scope-A fix) / Scenario: dimensioned CostOfRevenue is not emitted as revenue
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Revenue-concept matching is an allow/deny + $-unit gate, not a substring (folds a scope-A fix) / Scenario: a percentage-named *Revenue* concept is excluded by the deny list
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Revenue-concept matching is an allow/deny + $-unit gate, not a substring (folds a scope-A fix) / Scenario: a legitimate non-RFCC revenue concept is kept

## Task 3 — Read fiscal calendar per-filing from dei tags  [DONE — Wave 1, kept]
- Description: Emit each filing's `dei:DocumentFiscalPeriodFocus` + `dei:CurrentFiscalYearEndDate` onto the fact-pack per filing, never caching/hardcoding the FYE per ticker. (T13 extends this read with `dei:DocumentFiscalYearFocus` — the third cover-page tag.)
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (_extract_dei_calendar ~:2410)
- Acceptance:
  - RED: `test_extract_emits_dei_fiscal_calendar` — pack carries the per-filing dei values; two filings from one 52/53-week filer keep their own drifting FYE values.
  - GREEN: shipped and gate-passed 2026-07-16/17 (per-task triad PASS).
- External surfaces: edgartools (network) — dei string facts read via filing.xbrl(); NVDA + AAPL fixtures.
- Dependencies: none
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The fiscal calendar is read per-filing from dei tags, never cached per ticker / Scenario: fiscal-year-end is read per-filing, not cached

## Task 4 — ADR / 20-F regime detect → explicit N/A  [DONE — Wave 1, kept]
- Description: Detect a foreign-private-issuer ticker (20-F + 6-K, no 10-Q) and return an explicit quarterly-N/A with reason, never a silently-empty series.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (company.get_filings form enumeration)
- Acceptance:
  - RED: `test_quarterly_foreign_filer_returns_na` — TSM-shaped submissions return an explicit "no quarterly XBRL (foreign 20-F/6-K regime)" N/A with reason.
  - GREEN: shipped and gate-passed 2026-07-16/17 (per-task triad PASS).
- External surfaces: edgartools (network) — submissions form histogram; TSM fixture.
- Dependencies: none
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A foreign private issuer on the 20-F+6-K regime is detected and returned N/A, never silently empty / Scenario: a 20-F-only filer returns an explicit quarterly-N/A

## Task 13 — P0: fix the fiscal primitive + emit parallel calendar/fiscal labels
- Description: Replace the lying `_filing_period_year` (`int(period_of_report[:4])` under a "fiscal year" docstring) with an honest declared-fiscal-year path, and emit the parallel label schema on every fact. Selection: a fiscal-year range request selects filings by their DECLARED fiscal year (pre-fetch: sanctioned index-metadata derivation from form/period_of_report/filing-date; the derivation is explicitly a candidate GUESS — T14 reconciles it post-fetch). Emission: each fact carries `calendar_year`+`calendar_quarter` (calendar quarter containing period_end, Compustat DATACQTR rule) AND `fiscal_year`+`fiscal_quarter` (per-fact, own period_end vs that filing's dei calendar — comparatives from their OWN period, never the filing focus stamped; `dei:DocumentFiscalYearFocus` read as the third cover tag, authoritative for the current-period fact only). `fiscal_quarter` ∈ {Q1..Q4, FY}, derived jointly with duration_class: a 12-month fact carries FY, never a bare Q4. Unreadable dei calendar → distinct DQC-schema error, NEVER a period_end[:4] fallback. This is ONE atomic unit deliberately: the root defect had 4 call sites patched one-at-a-time three times — the fix is the primitive AND its contract together (memory: fiscal-year-derive-per-fact-against-filing-calendar).
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py, investing-toolkit/tests/data/fixtures/xbrl_quarterly_nvda_range.json
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (_filing_period_year ~:2218 and its call sites ~:2472/:2754/:2849/:2857/:2995, _build_dimensional_revenue_fact ~:2161, _extract_dei_calendar ~:2410)
  - docs/loom/memory/fiscal-year-derive-per-fact-against-filing-calendar.md
- Acceptance:
  - RED: `test_fiscal_range_selects_declared_years` — over the machine-captured NVDA range fixture, `form="10-Q", since_year=2026, until_year=2026` selects all three FY2026 10-Qs (period ends in calendar 2025) and no FY2027 filing; a fixed-December-FYE filer's selection is byte-identical to the previous calendar behaviour.
  - RED: `test_parallel_period_labels` — the NVDA FY2026-Q3 fact (period_end 2025-10-26) carries calendar_year=2025+calendar_quarter=Q4 AND fiscal_year=2026+fiscal_quarter=Q3; an AAPL-FY2019-10-K comparative fact ending 2018 carries fiscal_year=2018 (own period, not the filing focus 2019); a 12-month fact carries fiscal_quarter=FY never Q4; a filing with absent/malformed dei calendar raises a distinct DQC-schema error and never emits period_end[:4] as fiscal_year.
  - GREEN: both tests pass; `_filing_period_year`'s replacement has an honest name+docstring; all former call sites route through the corrected primitive; full offline suite green.
- External surfaces: edgartools (network) — dei cover tags (DocumentFiscalYearFocus/DocumentFiscalPeriodFocus/CurrentFiscalYearEndDate live-verified 90/90 across 6 filers × 5 FYs); fixtures machine-captured (NVDA range fixture recovered from `git show 10ff0cbc`, AAPL FY2019 captured fresh) — never hand-typed.
- Dependencies: none  # T1-T4 are DONE; this starts the rebuild
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A fiscal-year range request selects filings by their declared fiscal year / Scenario: a non-December-FYE filer's fiscal-year quarters are selected despite the calendar mismatch
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A fiscal-year range request selects filings by their declared fiscal year / Scenario: a December-FYE filer's selection is unchanged (calendar == fiscal)
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every fact carries parallel calendar and fiscal period labels, honestly named / Scenario: a non-December-FYE quarter carries diverging calendar and fiscal labels
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every fact carries parallel calendar and fiscal period labels, honestly named / Scenario: a prior-year comparative gets its own fiscal label, never the filing's focus stamped
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every fact carries parallel calendar and fiscal period labels, honestly named / Scenario: an unreadable fiscal calendar fails loud, never a calendar fallback
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every fact carries parallel calendar and fiscal period labels, honestly named / Scenario: an annual fact is labeled FY, never a bare Q4 (critic-found)

## Task 14 — Post-fetch reconciliation of the selection guess
- Description: After fetch, re-check each selected filing's range membership against its DECLARED `dei:DocumentFiscalYearFocus`: an out-of-range declaration excludes the filing AND surfaces the guess/declaration mismatch (DQC-schema flag or coverage line); an absent/malformed declaration raises a distinct flag naming the filing — never silently dropped, never bucketed by `period_of_report[:4]`.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (the T13 selection path + declared-FY reader)
- Acceptance:
  - RED: `test_selection_guess_reconciled_post_fetch` — a filing guess-selected for FY2026 whose fetched dei declares FY2027 is excluded from the FY2026 result with the mismatch surfaced; a fetched filing with unreadable DocumentFiscalYearFocus gets a distinct named flag and no calendar bucketing.
  - GREEN: both reconciliation outcomes surfaced, never silent in either direction.
- External surfaces: edgartools (network) — fixtures derived from the T13 NVDA range fixture (boundary filing).
- Dependencies: Task 13 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A fiscal-year range request selects filings by their declared fiscal year / Scenario: a selection-time guess is reconciled against the fetched declaration (critic-found)
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A fiscal-year range request selects filings by their declared fiscal year / Scenario: a filing with an unreadable fiscal-year declaration is flagged, never calendar-bucketed (critic-found)

## Task 16 — Boundary tolerance + projection derivation basis
- Description: Fiscal-boundary matching uses FISCAL_BOUNDARY_TOLERANCE_DAYS=10: a period_end within tolerance of a fiscal-quarter boundary maps to it; beyond tolerance the fact is flagged unclassifiable (DQC schema), never nearest-guessed. Each fiscal label records its derivation basis: `dei-declared` (tag in hand) or `projected` (+12mo projection of the prior declared FYE, sanctioned as fallback only — needed for in-progress years).
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (the T13 label-derivation path)
- Acceptance:
  - RED: `test_label_tolerance_and_projection_basis` — a transition/stub period_end beyond 10 days from every boundary → unclassifiable DQC flag, no nearest guess; a label grounded on a projected FYE (no dei tag for that year) carries derivation_basis="projected", one grounded on the tag carries "dei-declared".
  - GREEN: tolerance rule + basis disclosure both hold.
- External surfaces: edgartools (network) — 52/53-week fixture (NVDA drifting FYE, already captured for T3).
- Dependencies: Task 13 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every fact carries parallel calendar and fiscal period labels, honestly named / Scenario: an out-of-tolerance period_end is unclassifiable, never nearest-guessed (critic-found)
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every fact carries parallel calendar and fiscal period labels, honestly named / Scenario: a projection-grounded label or verdict is marked as such (critic-found)

## Task 17 — Cache schema versioning for the parallel-label payload
- Description: The parallel-label schema changes the meaning of `fiscal_year` and adds four fields; pre-revision cached payloads must never alias into the new pipeline. Version the cache key/schema (distinct key per docs/loom/memory/cache-key-collision-across-migration.md) and add the cross-shape regression: a pre-seeded legacy entry is a MISS for the new reader.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (the dimensional-revenue cache write/read path)
  - docs/loom/memory/cache-key-collision-across-migration.md
- Acceptance:
  - RED: `test_cache_schema_version_no_alias` — pre-seed the LEGACY key with an old-shape payload (calendar-valued fiscal_year, no parallel fields); the new reader does not alias it (miss → fresh fetch), and new writes land under the versioned key.
  - GREEN: no old-shape payload ever reaches parallel-label output.
- External surfaces: shared data-markets cache layer (filesystem) — no network.
- Dependencies: Task 13 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every fact carries parallel calendar and fiscal period labels, honestly named / Scenario: pre-revision cached payloads are never merged into parallel-label output (critic-found)

## Task 18 — Coverage rebuild: index-level absence states on the fiscal basis (supersedes old T10)
- Description: Rebuild per-filing/per-quarter coverage ON THE CORRECTED PRIMITIVE: fiscal grouping via T13's declared-FY/label machinery (never calendar slicing — AAPL FY2025-Q1 ends 2024-12-28). The report's comparison universe is the FULL filings index; index-level absences classify as not-yet-filed / out-of-requested-range / unclassified (pairwise distinguished, never one silent "gap"); a filing present in the index but missed by selection reports as index-visible-but-not-selected, never not-yet-filed.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (_dimensional_revenue_coverage from scope-A, T13's selection path)
- Acceptance:
  - RED: `test_coverage_per_quarter_completeness` — a covered year with 10-K+Q1+Q2 but no Q3 reports partial (3/4, Q3 + reason); the three index-absence states pairwise distinguished; a selection-missed index-visible filing reports as a selection gap. Fixtures machine-captured from AAPL/NVDA (never hand-typed — the hand-typed December-FYE fixture is what hid the round-1 bug).
  - GREEN: per-quarter coverage on the fiscal basis with honest absence states.
- External surfaces: edgartools (network) — filings-index metadata; AAPL/NVDA fixtures.
- Dependencies: Tasks 4, 13 complete first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Coverage honesty extends to per-filing completeness (critic-found) / Scenario: a partial year reports which filings are missing
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Coverage honesty extends to per-filing completeness (critic-found) / Scenario: absence states are distinguished
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Coverage honesty extends to per-filing completeness (critic-found) / Scenario: a selection-missed filing surfaces as a selection gap (critic-found)

## Task 19 — Coverage rebuild: observed failure states + quarantine blast radius
- Description: Add the two OBSERVED coverage states, each grounded by in-hand evidence: `attempted-fetch-failed` (a download/XBRL-parse raised — retryable, reported at the coverage layer via the existing error_class gap-slot idiom) and `filed-but-unlabelable` (fetched fine, the fail-loud fiscal derivation rejected the filing). Blast radius: one failed/unlabelable filing is quarantined — its facts excluded from fiscal-labeled output, the run continues, coverage reports the quarter honestly.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (T18's coverage report, T13's fail-loud path)
- Acceptance:
  - RED: `test_coverage_observed_failure_states` — an index-present 10-Q whose fetch/parse raises reports attempted-fetch-failed (retryable, grounded); a multi-year build with exactly one dei-unreadable filing completes, emits the other filings' series, excludes the bad filing's facts, and reports that quarter filed-but-unlabelable (DQC schema).
  - GREEN: both observed states surfaced; one bad filing never aborts the run.
- External surfaces: edgartools (network) — failure paths stubbed offline over machine-captured fixtures.
- Dependencies: Tasks 13, 18 complete first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Coverage honesty extends to per-filing completeness (critic-found) / Scenario: an actual fetch/parse failure is reported as attempted-and-failed, not an index absence (critic-found)
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Coverage honesty extends to per-filing completeness (critic-found) / Scenario: an unlabelable filing is quarantined and the run continues (critic-found)

## Task 21 — Synthetic $-unit backstop test
- Description: Add the ADMIT-default backstop regression the revised spec split out of the deny-list scenario: a `*Revenue*` concept that passes the allow/deny NAME gates but carries a non-currency XBRL unit is rejected by the $-unit guard. Synthetic fixture (no real filer case in the verification universe today) — test-only task; the guard code shipped in T2.
- Module: investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Files touched: investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (_is_revenue_concept + the $-unit guard)
- Acceptance:
  - RED: `test_unit_guard_backstop_synthetic` — a synthetic name-gate-passing, ratio-unit `*Revenue*` fact is rejected by the unit guard, never emitted.
  - GREEN: backstop asserted independently of the name gates.
- External surfaces: none (synthetic fixture, offline).
- Dependencies: none
- Independent: false  # shares test_sec_edgar_dimensional.py with the data-layer group
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Revenue-concept matching is an allow/deny + $-unit gate, not a substring (folds a scope-A fix) / Scenario: the $-unit guard backstops a non-currency fact that passes the name gates

## Task 5 — Classify period_type from emitted labels; migrate period keying to the fiscal basis
- Description: The analysis layer classifies each fact's period_type (Q1/Q2/Q3/Q4/FY) + cumulative flag + duration_class CONSUMING the data layer's emitted labels (per the resolved sub-questions: data layer derives, analysis consumes — rebuild-findings §RESOLVED tail), and MIGRATES the period key off `period_end[:4]` (kpi_xbrl.py:143, ruled a latent bug) onto the emitted fiscal label: a quarterly NVDA fact keys under fiscal_year 2026, not calendar 2025. Comparatives classified from their own labels; unclassifiable/stub surfaced, not guessed. Carries the Wave-1 review findings: an `error_class` N/A slot (T4) is branched on BEFORE `fact_pack.get("facts", [])`; a `None` per-filing calendar routes to the surfaced-unclassifiable path.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (_require_period ~:127-143, facts_to_points ~:157)
  - docs/loom/2026-07-16-operational-kpi-quarterly/rebuild-findings.md (§RESOLVED sub-questions)
- Acceptance:
  - RED: `test_classify_period_type` — 3mo at fiscal Q1 end → Q1/single; non-Dec (Sep) 3mo ending late-Dec → Q1; 9mo → 9mo-YTD/cumulative; 6mo → 6mo-YTD/cumulative; a comparative classified from its own labels; a stub/unclassifiable surfaced.
  - RED: `test_classify_uses_filing_dei_focus_not_calendar` — the spec's Q2 scenario asserted literally: a fiscal-Q2 fact from a non-December filer classifies as Q2 by the filing's dei calendar, not its calendar-quarter position.
  - RED: `test_period_key_is_fiscal_not_calendar` — a quarterly NVDA fact (period_end 2025-10-26, fiscal_year 2026) keys/groups under 2026; the calendar pair remains available on the point for calendarization.
  - RED: `test_fact_pack_na_slot_is_not_read_as_empty_series` — an `error_class == "foreign_private_issuer_no_quarterly_xbrl"` slot is branched on before facts access; a `None` calendar routes to surfaced-unclassifiable, never a calendar default.
  - GREEN: classification + fiscal keying + N/A-slot handling all hold; analysis tests stub requests+edgar pre-import.
- Dependencies: Tasks 1, 3, 13 complete first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period type is classified from duration and the fiscal calendar / Scenario: 3-month fact at a fiscal quarter end
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period type is classified from duration and the fiscal calendar / Scenario: non-December fiscal year end shifts the quarter boundaries
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period type is classified from duration and the fiscal calendar / Scenario: a 9-month fact is a YTD cumulative, not a single quarter
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period type is classified from duration and the fiscal calendar / Scenario: a 6-month fact is an H1 YTD cumulative (critic-found)
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period type is classified from duration and the fiscal calendar / Scenario: a transition or unclassifiable period is surfaced, not guessed
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The fiscal calendar is read per-filing from dei tags, never cached per ticker / Scenario: a prior-year comparative fact is classified from its own period, not the filing focus
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The fiscal calendar is read per-filing from dei tags, never cached per ticker / Scenario: non-December fiscal-year-end classifies by the filing's dei calendar

## Task 6 — Identity key gains duration_class; de-conflate + label-conflict flag
- Description: Extend the resolve_binding identity key with duration_class (single-quarter vs YTD at one period_end = DISTINCT points, never deduped/raised against each other; identical cross-filing single-quarter dedupes; restated quarter applies policy C on the duration-qualified key). NEW (critic round 2): when duplicates from two filings carry DIVERGENT fiscal labels (FYE drift / mid-history FYE change), the dedup flags the conflict (DQC schema, both source calendars) and keeps the later-filed filing's label deterministically.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py, investing-toolkit/tests/analysis/fixtures/xbrl_quarterly_dualdur.json
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (resolve_binding dedup loop, identity_key)
- Acceptance:
  - RED: `test_identity_key_deconflates_quarter_from_ytd` — 3mo + 9mo same signature/period_end → two distinct points, no cross-RAISE; identical cross-filing single-quarter dedupes; restated quarter → policy C newest-wins + DQC.
  - RED: `test_dedup_label_conflict_deterministic` — identical-value duplicates whose filings' calendars yield different fiscal labels → flagged with both calendars, later-filed label survives.
  - GREEN: de-conflation, dedupe, policy C, and label-conflict handling all correct.
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The identity key de-conflates single-quarter from year-to-date / Scenario: single-quarter and YTD at the same period_end stay distinct
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The identity key de-conflates single-quarter from year-to-date / Scenario: the same single quarter reported in two filings dedupes
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The identity key de-conflates single-quarter from year-to-date / Scenario: a restated quarter across filings applies policy C
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The identity key de-conflates single-quarter from year-to-date / Scenario: a cross-filing fiscal-label divergence at dedup is flagged, with a deterministic survivor (critic-found)

## Task 7 — Single-granularity series + fiscal-range output filter
- Description: build_series_with_break keeps annual and quarterly points in separate granularity-labeled series (mixing rejected, never averaged/concatenated); the dimension-absent-from-quarterlies flag surfaces end-to-end (calling the data layer's `_dimension_quarterly_absence`); NEW (critic round 2): the built series is range-filtered by each fact's OWN fiscal label — a selected FY2026 10-Q's FY2025 comparatives are usable internally (dedup/restatement) but never emitted as in-range points.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (build_series_with_break)
- Acceptance:
  - RED: `test_series_single_granularity` — quarterly request returns only sub-annual points; FY+quarter mix for one fiscal year excluded/rejected, never averaged.
  - RED: `test_series_flags_dimension_absent_from_quarterlies` — a 10-K-present signature tagged in no 10-Q surfaces as `no_quarterly_coverage`, distinct from zero and discontinued.
  - RED: `test_series_range_filtered_by_own_fiscal_label` — with range [2026,2026], FY2025 comparative facts from a selected FY2026 filing are not emitted as series points.
  - GREEN: granularity, dimension-absent flag, and fact-level range filter all enforced.
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A series carries a single granularity / Scenario: a quarterly request returns only sub-annual points
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A series carries a single granularity / Scenario: mixing granularities is rejected
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Coverage honesty extends to per-filing completeness (critic-found) / Scenario: a dimension absent from the quarterlies is flagged, not zero-filled
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: A fiscal-year range request selects filings by their declared fiscal year / Scenario: emitted points are range-filtered by each fact's OWN fiscal label (critic-found)

## Task 8 — Q4 derive FY−9moYTD, guarded + segregated + labeled
- Description: Derive an untagged Q4 as (FY − 9mo-YTD), flagged computed + segregated (reported-only requests exclude it); skip (never fabricate) on a missing source or basis/vintage/unit mismatch; record both contributing accessions. NEW (critic round 2): the derived point carries the three label groups, minted from the derived 3-month window against the 10-K's dei calendar; calendars disagreeing between the two sources → the basis-mismatch refusal.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py, investing-toolkit/tests/analysis/fixtures/xbrl_q4_derive.json
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (point emission + dqc path)
- Acceptance:
  - RED: `test_q4_derive_guarded_segregated` — derive when both inputs exist (flagged+segregated+dual-accession); skip+surface on missing source; refuse on vintage/unit mismatch; a directly-tagged Q4 short-circuits derivation.
  - RED: `test_q4_derived_carries_parallel_labels` — the derived point carries raw-window/calendar/fiscal groups grounded in the 10-K's calendar; source-calendar disagreement → basis-mismatch refusal.
  - GREEN: derivation guards + segregation + labels all hold.
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: Q4 derived when both inputs exist, and segregated
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: a reported-only request excludes derived Q4
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: Q4 not derived when a source is missing
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: a directly-tagged Q4 is used as-is
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: Q4 derivation refuses across mismatched restatement vintages or units (critic-found)
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated / Scenario: a derived Q4 carries the three label groups, grounded in the 10-K's calendar (critic-found)
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every emitted point and DQC flag carries structured provenance (critic-found) / Scenario: a derived Q4 records both contributing accessions

## Task 9 — Structured point + DQC-flag schema provenance
- Description: Every emitted series point carries source accession(s), source form (10-K|10-Q), and duration_class; every DQC flag — including the new classes from T13/T14/T16/T19 (unreadable-calendar, guess-mismatch, unclassifiable, label-conflict) — follows the ONE schema (type, old, new, contributing accession(s), reason); the sub-annual restatement flag carries old→new + both accessions (policy-C parity).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (facts_to_points point dict, the dqc field)
- Acceptance:
  - RED: `test_point_and_dqc_provenance_schema` — an emitted point carries accession(s)+form+duration_class; a restatement flag records old, new, both accessions; every new-class flag validates against the one schema.
  - GREEN: point provenance + unified DQC schema.
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every emitted point and DQC flag carries structured provenance (critic-found) / Scenario: a series point is traceable to its source filing
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Every emitted point and DQC flag carries structured provenance (critic-found) / Scenario: a restatement DQC flag carries the full audit content (parity with scope-A policy C)

## Task 11 — Offline end-to-end quarterly seam test
- Description: A deterministic offline test driving the full corrected chain (fiscal-selected multi-filing quarterly facts with a dual-duration collision + a derived Q4 → parallel labels → classify → de-conflate → series) over machine-captured fixtures, asserting fiscal keying end-to-end, distinct single-quarter/YTD points, and a segregated labeled derived Q4.
- Module: investing-toolkit/tests/analysis/test_kpi_xbrl_quarterly_e2e.py
- Files touched: investing-toolkit/tests/analysis/test_kpi_xbrl_quarterly_e2e.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (facts_to_points, resolve_binding, build_series_with_break)
- Acceptance:
  - RED: `test_quarterly_chain_deconflates_and_segregates_q4` — the assembled chain yields fiscal-keyed, parallel-labeled, de-conflated points + a segregated derived Q4. (Stub requests+edgar pre-import.)
  - GREEN: chain green over real fixtures; no crash.
- Dependencies: Tasks 5, 6, 7, 8, 9 complete first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: The identity key de-conflates ... + Requirement: Q4 ... segregated (seam verification per cross-module-field-contracts)

## Task 12 — Live shape-anchor (network-marked)
- Description: A @pytest.mark.network live test capturing the REAL 10-Q dual-duration + dei cover-tag shape (3mo+9mo facts for one signature/period_end; DocumentFiscalYearFocus + DocumentFiscalPeriodFocus + CurrentFiscalYearEndDate present), anchoring the fixtures' producer shape.
- Module: investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py
- Files touched: investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py
- Context paths:
  - investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py (existing network tests + uv-run pattern)
- Acceptance:
  - RED: `test_quarterly_dual_duration_live` — live 10-Q returns dual-duration facts + all three dei cover tags. Deselected offline.
  - GREEN: live shape confirmed; network-marked.
- External surfaces: edgartools (network, live SEC EDGAR); flake budget accepted.
- Dependencies: Tasks 1, 3, 13 complete first
- Independent: false
- Brief item covered: 2026-07-16-operational-kpi-quarterly / Requirement: Period duration is emitted per fact + Requirement: fiscal calendar read per-filing (live shape-anchor per fixtures-mirror-producer-shape)

## Notes
- REBUILD context: this plan supersedes the 2026-07-16 plan after the root-cause diagnosis +
  spec-fix + critic round 2. T1-T4 are DONE-kept (no re-dispatch); old T10 is SUPERSEDED by
  T18/T19 — its three commits are reset out/replaced during the rebuild. Task IDs are stable
  across plan versions (T15/T20 were absorbed: T15's label emission merged into T13 to keep the
  primitive+contract atomic AND the critical path ≤5; T20's range filter folded into T7).
- DAG levels: L1={T13, T21} (T21 shares the data-layer test file → sequential in the same-file
  group, own level slot). L2={T14, T16, T17, T18 (deps T13; T18 also T4-done)}. L3={T19 (deps
  T13,T18), T5 (deps T1,T3-done + T13), T12 (deps T1,T3-done + T13)}. L4={T6 (dep T5)}.
  L5={T7, T8, T9 (dep T6)}. L6-slot={T11 (deps T5-T9)} — critical path T13→T5→T6→T8→T11 =
  depth 5 (T11 counts as the 5th link on the longest Dependencies chain; T18→T19 is depth 3).
- No `Independent: true` pairs: T13-T19,T21 share sec_edgar_client.py and/or
  test_sec_edgar_dimensional.py; T5-T9 share kpi_xbrl.py; T11/T12 are separate files but
  multi-dependent. Sequential within groups (Check-14 discipline from scope A).
- Fixtures machine-captured from verification-universe tickers named inline; never hand-typed.
- Granularity-gated fetching (only fetch 10-Qs when quarterly requested) remains the usage-cost
  lever inside the extract path (user decision 2026-07-16: correctness machinery is
  runtime-cheap, only fetch VOLUME is the cost lever).
- FISCAL_BOUNDARY_TOLERANCE_DAYS=10 is this plan's ruling on the spec's deferred constant
  (bounded by the verified ≤6-day drift + margin); revisit only with new field data.
- Kickoff decision: versioned cache-key shape → a DISTINCT key carrying a schema tag (legacy
  key untouched → guaranteed miss), per docs/loom/memory/cache-key-collision-across-migration.md;
  T17 pins the exact literal in its regression test.
- Kickoff decision: new DQC flag classes (unreadable-calendar / guess-mismatch / unclassifiable /
  label-conflict / filed-but-unlabelable) → all instances of the ONE existing DQC schema
  (type, old, new, accessions, reason) — no per-class schema variants; T9 asserts conformance.
- Kickoff sweep 2026-07-18: zero one-way-door decisions (all local/unpushed/refetchable —
  two-way per kickoff-briefing §a) → no batched briefing; routed here + Decision Log.
- Amendment note: the three lines above + the PASS timestamp were added AFTER the
  plan-document-reviewer PASS; additive Notes-only, schema-safe — re-review skipped per
  writing-plans §Amending a PASS plan.

## Decision Log

- 2026-07-17 — **Re-home "a dimension absent from the quarterlies is flagged, not zero-filled" from T10 to T7.**
  WHY: both T10 reviewers ruled the scenario unmet end-to-end — T10 shipped `_dimension_quarterly_absence`
  as a pure function with no production caller and no other task claiming the scenario, silently orphaning a
  critic-found requirement. The spec's own WHEN ("when the quarterly series is built") locates it in the
  analysis layer (kpi_xbrl.py), not the data layer; wiring it into `extract_dimensional_revenue` would force a
  10-K `.xbrl()` fetch on every quarterly call — the usage-cost lever the user's 2026-07-16 decision
  explicitly protects ("correctness machinery is runtime-cheap, build it all; only fetch VOLUME is the
  cost lever"). T7 is where the series is built. Agent-decided (two-way door, no product consequence: the
  requirement ships either way, only its owning task changes). Rejected: forcing T10 to eat the double fetch.
- 2026-07-17 — **Carry T4's `error_class` consumption + T3's `None`-calendar handling into T5's acceptance.**
  WHY: T4's `foreign_private_issuer_no_quarterly_xbrl` N/A slot currently has ZERO production consumers; both
  T4 reviewers and T10's spec-reviewer independently found that kpi_xbrl.py reads `fact_pack.get("facts", [])`
  with a default, so an N/A slot is silently consumed as a real-empty series — the exact failure T4 exists to
  prevent, live today. Same shape for a `None` dei calendar from T3. Neither has a spec scenario of its own
  (both are integration seams under existing requirements), so they land as T5 acceptance criteria without a
  new `Brief item covered` line. Agent-decided (two-way door).
- 2026-07-17 — **Re-home the spec's Q2/dei-focus scenario assertion from T3 to T5.** WHY: T3's spec-reviewer
  ruled T3 structurally cannot satisfy it — T3 emits the calendar, classification is T5's module. The plan had
  mapped it to T3. Agent-decided (two-way door; scenario coverage preserved, owner corrected).
- 2026-07-18 — **REBUILD re-plan on the corrected spec (surgical restart, user-ratified).** T10 SUPERSEDED
  by T18/T19 (rebuilt on the corrected primitive — index-absence states + observed states + quarantine).
  P0 = T13 merges the primitive fix with the parallel-label emission deliberately: the root defect had four
  call sites patched one-at-a-time three times; the durable fix is the primitive AND its contract as one
  atomic unit (memory: fiscal-year-derive-per-fact-against-filing-calendar §Process lesson), and the merge
  keeps critical-path depth at 5. Agent-decided within the user-ratified restart shape.
- 2026-07-18 — **Sub-questions ruled (rebuild-findings §RESOLVED tail): data layer derives both label
  groups; kpi_xbrl migrates period keying to the emitted fiscal label** (calendar keying ruled a latent
  bug made load-bearing by quarterly; zero production callers → no live-consumer impact; calendar basis
  remains available on every point for calendarization). Agent-decided — both answers entailed by the
  user-ratified parallel-label design + repo evidence; recorded, not re-asked.
