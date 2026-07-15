# Plan: multi-filing historical fetch (scope A — annual)

Source brief: docs/loom/specs/2026-07-15-multi-filing-historical-fetch.md
Total tasks: 6
Critical-path depth: 3 (≤5)   ← T1→T2→T5 and T3→T4→T5
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-15)
  Advisory (Check 15) declined: T2/T4/T6 share source files with their L1 predecessors
  (T2↔T1 sec_edgar_client.py; T4↔T3 kpi_xbrl.py), so a blanket `Independent: true` would
  violate the Check-14 disjointness invariant. L2 concurrency is documented in §Notes; the
  high-value L1={T1,T3} parallelism is captured via `Independent: true`.
  Post-PASS amendment (additive, re-review skipped): added §Decision Log + §Kickoff sweep
  result — no task field, RED/GREEN, dependency, or DAG structure changed (schema-safe).

Fixture discipline (all tasks): fixtures are MACHINE-CAPTURED exact-integer dumps from the
live extractor, cross-checked against it — NEVER hand-typed (loom-memory
`hand-authored-fixture-is-a-fabrication-risk`). Run pytest with `PYTHONDONTWRITEBYTECODE=1`.

## Task 1 — Range-bounded consecutive multi-filing fetch
- Description: Un-collapse the single-filing seam in `extract_dimensional_revenue` — add
  `since_year`/`until_year` params (both default `None` = current latest-only behavior);
  when `since_year` is given, iterate the exact-form filings whose fiscal periods span
  [since_year, until_year], pull `.xbrl()` per filing, and concatenate their facts into the
  one flat `facts` list. Consecutive (every filing in range), never strided.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py, investing-toolkit/tests/data/fixtures/xbrl_multifiling_aapl.json
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py  (extract_dimensional_revenue:1985, the `max(exact_filings,…)` collapse at :2037, _build_dimensional_revenue_fact:1939, _dimension_signature:1889)
  - investing-toolkit/tests/data/test_sec_edgar_dimensional.py  (existing 8 offline tests — the exact-form/amendment-skip pattern at :320)
- Acceptance:
  - RED: `test_extract_dimensional_revenue_since_year_spans_multiple_filings` — with the multi-filing fixture, calling with `since_year` set returns facts drawn from >1 distinct `accession`; the default call (no `since_year`) still returns facts from exactly one (latest) accession.
  - GREEN: facts from every in-range exact-form 10-K are concatenated; existing 8 offline tests stay green (default path unchanged).
- External surfaces: edgartools (network) — `company.get_filings(form)` returns the iterable filing collection (already iterated at :2034); `filing.xbrl().facts.to_dataframe()` per filing. Fixture is captured by dumping each historical 10-K's raw facts dataframe via the existing single-filing path (per-accession), then concatenating — machine-captured, not hand-built.
- Dependencies: none
- Independent: true
- Brief item covered: "Change one seam — sec_edgar_client.py:2037 — from 'pick max filing' to a range-bounded, consecutive multi-filing fetch … Default = current behavior (latest filing only, ~3 yr) … Historical depth is opt-in via since_year."

## Task 2 — Coverage report + availability clamp (DQC honesty)
- Description: When the requested range exceeds availability (XBRL floor or before the
  company's first exact-form filing), return the facts that DO exist AND attach a coverage
  report to the returned pack: requested range, actual returned range, and the clamp reason.
  Never silently return a shorter range than requested.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py  (the extended fetch from Task 1; return dict at :2054)
- Acceptance:
  - RED: `test_extract_dimensional_revenue_reports_coverage_clamp` — requesting `since_year` earlier than the earliest available filing returns a pack whose `coverage` records requested-vs-actual + a clamp reason; the facts themselves stop at the real floor.
  - GREEN: `coverage` key present with `{requested, actual, clamp_reason}`; no silent truncation; an in-availability request records no clamp.
- External surfaces: edgartools (network) — filing enumeration determines the real availability floor; offline test uses the Task 1 fixture (bounded filing set) to simulate the floor.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Coverage honesty (DQC). When the requested range exceeds availability (XBRL floor ~2009, or before the company's first filing), return what exists AND report the clamp (requested vs actual + reason) — never silently return a shorter range."

## Task 3 — Reserve `period_type` on the identity key (A sets FY)
- Description: Extend the anti-fabrication identity/dedup key in `resolve_binding` from
  `(signature, period)` to `(signature, period_type, period)`, where scope A always sets
  `period_type = "FY"`. Emitted points carry `period_type`. This reserves the slot scope B
  (quarterly) extends without a core rewrite. A does NOT model quarters.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py  (resolve_binding:199, the dedup loop :259-277, _require_period:121, facts_to_points:151)
  - investing-toolkit/tests/analysis/test_kpi_xbrl.py  (existing 14 tests; dedupe test :346, ambiguous-raise test :315)
- Acceptance:
  - RED: `test_resolve_binding_identity_key_carries_period_type_fy` — emitted points include `period_type == "FY"` and the dedup grouping keys on `(signature, period_type, period)`.
  - GREEN: identity key includes `period_type`; A emits `"FY"`; existing 14 analysis tests stay green (annual grouping unchanged since all points are FY).
- Dependencies: none
- Independent: true
- Brief item covered: "Forward-compat period key (for scope B). A's identity/dedup key carries a period_type field, which A always sets to a single annual value (FY)."

## Task 4 — Overlap policy C: newest-filing-wins + restatement DQC flag
- Description: For duplicate `(signature, period_type, period)` groups whose values DIFFER
  across filings (a restatement), replace the current hard `ValueError` with: keep the value
  from the most-recently-filed 10-K (`filed`/`accession`), and emit a restatement DQC flag
  capturing old→new value + both accessions. Identical-value duplicates still dedupe; the
  intra-filing invariants (>1 source match, unmatched-skip, malformed-period fail-loud) are
  UNCHANGED — only the cross-filing value-disagreement branch changes.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py, investing-toolkit/tests/analysis/fixtures/xbrl_restatement_factpack.json
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py  (the dedup/raise logic :259-277, value-set equality at :267, the `len(values) > 1` raise at :269-274 — the branch this task changes)
- Acceptance:
  - RED: `test_resolve_binding_restatement_newest_wins_with_dqc_flag` — two facts, same `(signature, FY, period)`, different `value`, different `filed` dates → resolve_binding keeps the newer-filed value AND surfaces a restatement DQC flag (old→new + accessions); it does NOT raise.
  - GREEN: newer value kept; DQC flag emitted; no ValueError; the identical-duplicate dedupe test and the ambiguous-source-raise test both stay green.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "for duplicate (signature, period) pairs apply newest-filing-wins + a restatement DQC flag (prefer the value from the most-recently-filed 10-K; when a superseded value differs, record a data-quality flag capturing old→new + the two accessions) … the intra-filing anti-fabrication invariants … are UNCHANGED."
- Notes: the restatement fixture must be a REAL captured example (two adjacent 10-Ks reporting the same signature+period with genuinely different values). Machine-capture from a real reclassification/restatement; if no restatement exists in the pilot ticker's history, surface to the user rather than hand-fabricating a value delta.

## Task 5 — Offline end-to-end seam integration test
- Description: A deterministic offline test driving the full chain across the module seam:
  a mocked multi-filing pack → `extract_dimensional_revenue` shape → `resolve_binding` →
  `build_series_with_break`, asserting a multi-year series spanning >3 years is produced and
  a seeded restatement flows through as a DQC flag (not a crash). Behavioral probe across the
  data→analysis seam (loom-memory `cross-module-field-contracts-execute-probes`).
- Module: investing-toolkit/tests/analysis/test_kpi_xbrl_multifiling_e2e.py
- Files touched: investing-toolkit/tests/analysis/test_kpi_xbrl_multifiling_e2e.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py  (facts_to_points:151, resolve_binding:199, build_series_with_break:296 → split_series:308)
  - investing-toolkit/tests/analysis/fixtures/xbrl_signature_factpack.json  (existing multi-period oracle to extend)
- Acceptance:
  - RED: `test_multifiling_chain_produces_multiyear_series_with_dqc` — the assembled chain over the multi-filing + restatement fixtures yields a period-keyed series spanning >3 years with the restatement point carrying a DQC flag.
  - GREEN: series length spans the fixture's full year range; DQC flag present on the restated point; no exception.
- Dependencies: Tasks 1, 2, 3, 4 complete first
- Independent: false
- Brief item covered: "Everything downstream is unchanged: the concatenated flat facts list flows through resolve_binding → build_series_with_break as-is (proven filing-agnostic)." (seam verification per cross-module-field-contracts loom-memory)

## Task 6 — Live shape-anchor (network-marked)
- Description: A `@pytest.mark.network` live test capturing the REAL edgartools multi-filing
  shape: `extract_dimensional_revenue("AAPL", since_year=<~10y back>)` returns facts spanning
  more than one filing's worth of years with the expected `dim_<axis>`-derived signature
  shape. Guards the edgartools grounding at the real boundary (loom-memory
  `fixtures-mirror-producer-shape` — the live anchor caught edgartools shape wrong 3×).
- Module: investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py
- Files touched: investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py
- Context paths:
  - investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py  (existing 2 network tests — AAPL :44, TSLA amendment-skip :100)
- Acceptance:
  - RED: `test_extract_dimensional_revenue_multifiling_live_aapl` — pre-implementation the call rejects `since_year` (TypeError) / returns only ~3 years; post-implementation it returns facts spanning >3 distinct fiscal years across >1 accession, each with a non-null signature.
  - GREEN: live AAPL call returns a multi-filing fact set spanning the requested window; marked `network` so it is deselected in the default `-m "not network"` run.
- External surfaces: edgartools (network, live SEC EDGAR) — real historical 10-K fetch; flake budget accepted per the durable memory.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "reuses the exact live-validated code path that preserves each fact's full signature" + loom-memory constraint "live shape-anchor test worth the flake budget".

## Notes
- Parallel levels: L1 = {T1, T3} (disjoint files, no shared symbol — both `Independent: true`).
  L2 = {T2 (dep T1), T4 (dep T3), T6 (dep T1)} run concurrently (disjoint files). L3 = {T5}.
- Downstream `resolve_binding` → `build_series_with_break` period-keyed logic is otherwise
  UNCHANGED; T3/T4 only touch the identity key + the cross-filing value-disagreement branch.
- Scope B (quarterly / 10-Q + period-duration model) is a committed follow-up via loom-spec —
  NOT in this plan (see brief §Committed follow-up).

### Kickoff sweep result (2026-07-15)
Zero one-way-door decisions → no kickoff briefing. Policy C (RAISE→newest-wins) was
user-decided upstream (recorded, not re-briefed). All shape decisions below are two-way
doors (no external consumer exists yet) → Decision Log, agent-decided, late-vetoable.

Kickoff decision: filing-selection-without-per-filing-xbrl-fetch → pick the in-range
filing set from the filings-list metadata (filing_date / reporting period), NOT by
fetching every `.xbrl()` first; implementer verifies edgartools exposes per-filing period
on the Filings collection, else falls back to fetch-then-filter (arm-1 library look-up).

## Decision Log
- `since_year`/`until_year` semantics: inclusive year bounds; both `None` = latest-only
  (current behavior preserved); `since_year` alone → `[since_year, latest]`. (two-way)
- `coverage` shape (T2): `{requested:{since,until}, actual:{min_year,max_year},
  clamp_reason: str|null}` on the returned pack. (two-way, product-visible → late-vetoable)
- DQC restatement flag shape (T4): recommended = a flag on the affected point
  (`{type:"restatement", old, new, superseded_accession, kept_accession}`); implementer may
  refine placement (point vs pack-level list) as long as it is machine-readable. (two-way)
- `period_type` value (T3): string `"FY"` for scope A; B (loom-spec) owns the real
  enumeration. (two-way)
- `until_year` without `since_year` (T1, mid-impl): raises `ValueError` (unsupported —
  the Decision Log defines only both-None=latest-only and since_year-alone=[since_year,
  latest]). Chosen over silently ignoring it (fail-loud law) or inventing
  `[earliest, until_year]` semantics. (two-way, agent-decided per code-quality 🟡)
