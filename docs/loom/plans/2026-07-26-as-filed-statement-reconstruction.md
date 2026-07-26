# Plan: reconstruct the three statements as the filer declared them

**Source brief**: docs/loom/specs/2026-07-26-as-filed-statement-reconstruction.md
**Total tasks**: 11
**Critical-path depth**: 5
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-07-26, round 2)

## Task 1 — exclude dimensional noise from statement lines

- **Description**: Write `is_statement_line(row) -> bool` deciding, structurally, whether a
  presentation row is a real statement line. Keep a row ONLY when it is proven undimensioned
  and its concept is not a placeholder; treat every other row as noise. The predicate is a
  POSITIVE allowlist of what a statement line looks like — never a denylist of observed
  member/axis names.
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_lines.py
- **Files touched**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_lines.py,
  investing-toolkit/tests/analysis/test_kpi_us_statement_lines.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statements.py
- **Acceptance**:
  - **RED**: `test_axis_domain_members_are_not_statement_lines` — a 2019-era row whose concept
    ends in `Member` and which carries NO dimension label (the measured failure: edgartools
    surfaced `TechnologyServiceMember` as IBM's first line and `NaturalGasReservesMember` as
    Duke's, 2019-2026) must be rejected; a same-era genuine line must be kept.
  - **GREEN**: rows are kept only when undimensioned AND non-placeholder; the suite covers BOTH
    eras (a pre-2018 dimension-labelled segment row AND a 2019+ Member row) and a filer whose
    real line legitimately contains the substring "Member" is not rejected by substring matching.
- **Dependencies**: none
- **Independent**: true
- **Status**: done(9154945e)
- **Brief item covered**: "Separating statement lines from dimensional noise is the single
  largest implementation risk, and it is NOT solved… it must be structural … and positive."

## Task 2 — classify a presentation role as one of the three statements

- **Description**: Write `statement_kind(role) -> "income" | "balance_sheet" | "cash_flow" | None`.
  Return `None` (not a guess) for parenthetical, comprehensive-income, and note roles. A role
  naming BOTH income and comprehensive income classifies as `income`, not `None`.
  CORRECTED 2026-07-26 (adjudicated by Task 2's spec-reviewer, recorded in `## Decision Log`):
  this Description originally also said "prefer a pure income role over a combined one when both
  exist". That is role SELECTION — a choice BETWEEN roles, needing a filing's whole role set,
  which this single-role signature structurally cannot see. It belongs to Task 3 and was moved
  there. Left uncorrected, Task 2 could not satisfy its own Description as written.
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_shape.py
- **Files touched**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_shape.py,
  investing-toolkit/tests/analysis/test_kpi_us_statement_shape.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statements.py
- **Acceptance**:
  - **RED**: `test_combined_income_and_comprehensive_role_is_still_income` — a role naming both
    income and comprehensive income classifies as `income` rather than being discarded.
    **Grounding CORRECTED 2026-07-26.** This clause originally read "measured: discarding it made
    CL/COST/MSFT/O/PGR/TRV look like they had no income statement at all". That was the
    orchestrator's INFERENCE from a probe in which those six filers yielded no income calculation
    tree — never a measurement of combined roles — and live fetches then refuted it: CL, COST and
    MSFT each file income and comprehensive income as SEPARATE roles. The real observed
    combined-role filer is Realty Income
    (`http://www.realtyincome.com/role/ConsolidatedStatementsOfIncomeAndComprehensiveIncome`), and
    that is what the test is now built on. The RED's premise stands — combined roles are real —
    only its evidence changed. Recorded rather than silently rewritten because the artifact's own
    tests already retract the claim, and a plan carrying a refuted premise forward feeds it to
    every downstream task.
  - **GREEN**: the three kinds classify from real role URIs; parenthetical/note roles return
    `None`; a role that matches no kind returns `None` and is never coerced into one.
- **Dependencies**: none
- **Independent**: true
- **Status**: done(f93f0e26)
  <!-- Four revision rounds. Quality re-review PASS_WITH_NOTES; the spec re-review's single
       remaining gap (a docstring invariant contradicted by the `tables` entry) was closed by the
       ORCHESTRATOR, not by a further reviewer pass — recorded plainly rather than reported as a
       clean PASS. -->
- **Brief item covered**: "From one accession: the three statements as ordered lines."

## Task 3 — assemble one filing's three statements

- **Description**: Write `statements_for(filing) -> dict[kind, list[Line]]` where each `Line`
  carries the filer's own label, concept, level, weight, calculation parent, and per-period
  values, in presentation order — composing Task 1's predicate and Task 2's classifier.
  **This task also owns ROLE SELECTION**, moved here from Task 2 on 2026-07-26: a filing carries
  14-132 roles and may offer several that classify as the same kind, so choosing BETWEEN them
  needs the whole role set, which Task 2's single-role signature structurally cannot see. Prefer a
  pure income role over a combined income-and-comprehensive one when both exist. Three further
  obligations Tasks 1 and 2 deliberately left here are recorded in `## Decision Log` and are part
  of this task, not optional: disposing of abstract header rows, re-confirming the LIVE row shape
  rather than inheriting Task 1's presence-based dimension presumption, and deciding deliberately
  whether a header row is a rendered line or noise.
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_shape.py
- **Files touched**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_shape.py,
  investing-toolkit/tests/analysis/test_kpi_us_statement_shape.py,
  investing-toolkit/tests/data/fixtures/capture_us_statement_reconstruction.py,
  investing-toolkit/tests/data/fixtures/us_statement_reconstruction_2026-07-26.json
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/data/fixtures/capture_us_statement_shapes_probe.py
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- **Acceptance**:
  - **RED**: `test_ko_fy2017_income_statement_is_twenty_six_lines` — KO's FY2017 income
    presentation role carries 80 rows and must reduce to its 26 real statement lines, first line
    labelled "NET OPERATING REVENUES", including the filer's own custom concept
    `ko_UnusualOrInfrequentItemOperating`.
  - **GREEN**: all three statements assemble for a committed multi-era fixture; lines preserve
    presentation order; `weight` and `calculation_parent` ride each line and may be `None` for
    lines outside every sum (EPS rows) without that being an error.
- **External surfaces**:
  - SDK package: edgartools==5.42.0 — `Filing.xbrl()`, `XBRL.get_statement`,
    `XBRL.calculation_trees` — grounding: live probe 2026-07-26 against KO
    0000021344-18-000008 and IBM 0001047469-17-001061; `CalculationNode` fields verified present
    (`parent`, `children`, `weight`, `order`, `balance_type`) and statement rows verified to carry
    `label`, `level`, `calculation_parent`, `weight`, `values`.
  - HTTP API: SEC EDGAR over HTTPS — grounding: reached ONLY through the existing acquirer
    `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py:928`
    (`_acquire_raw_filing`); the committed fixture is captured once so the suite makes no
    network call.
- **Dependencies**: Tasks 1, 2 parallel
- **Independent**: false
- **Status**: done(12b821df)
  <!-- Returned BLOCKED first, correctly: obligation 1.2 (re-confirm the LIVE row shape) found
       that Task 1 was deleting every statement's own top line. Fixed in 6c3c5c91 before this
       task resumed. Two revision rounds after that; the last two doc-claim corrections were
       applied by the ORCHESTRATOR, not by a further reviewer pass. -->
- **Review-weight note**: the BLOCKED round is the plan's most valuable single event so far — a
  defect that all 1230 package tests passed over was caught by a written obligation, not by a
  test. Keep such obligations explicit in the Decision Log for downstream tasks; they are the
  only mechanism here that has caught a green-but-wrong artifact.
- **Brief item covered**: "From one accession: the three statements as ordered lines — label,
  concept, level, weight, calculation parent, per-period values — segment slices excluded."

## Task 4 — verify every declared sum in Decimal

- **Description**: Write `verify(statements) -> list[SumCheck]` computing Σ(child × weight) per
  declared calculation parent in `Decimal` and comparing to the parent's own reported value.
  Report a group whose children are not fully tagged as `incomplete`, distinctly from a group
  that genuinely `disagrees` — a missing child is not a wrong sum.
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_check.py
- **Files touched**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_check.py,
  investing-toolkit/tests/analysis/test_kpi_us_statement_check.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_shape.py
- **Acceptance**:
  - **RED**: `test_sum_check_uses_decimal_not_binary_float` — a float-hostile value
    (a non-terminating binary fraction such as `1.005 × 1e9`, the case that already manufactured
    a false restatement in this module family) must reconcile; the same test written in binary
    float must be the thing that fails first.
  - **GREEN**: NEE's operating-cash-flow group — which declares both `ProfitLoss` and
    `NetIncomeLoss` as children and so double-counts net income by 5,378M — is reported as
    `disagrees` with both figures visible, never silently summed.
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: "Verification pass: every declared sum checked in `Decimal`; failures
  surfaced as flagged lines, and groups whose children are not fully tagged reported separately."

## Task 5 — type every empty cell

- **Description**: Write `cell_state(...) -> "value" | "not_presented" | "not_tagged" | "derived"`
  so no empty cell is undifferentiated. `not_presented` = the filer's statement has no such line;
  `not_tagged` = the line exists but that period carries no undimensioned value; `derived` =
  computed from the filer's own arithmetic, carrying its provenance.
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_cells.py
- **Files touched**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_cells.py,
  investing-toolkit/tests/analysis/test_kpi_us_statement_cells.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py
- **Acceptance**:
  - **RED**: `test_derived_total_liabilities_subtracts_whole_equity` — for a filer tagging
    `LiabilitiesAndStockholdersEquity` but not `Liabilities` (measured: 21 of 21 such filers are
    derivable), the derived value must subtract WHOLE equity; a fixture whose equity concept is
    parent-only `StockholdersEquity` with a non-zero minority interest must FAIL if the
    parent-only figure is used, since that pushes minority interest into "liabilities".
  - **GREEN**: the four states are distinguishable by a consumer; an oil major with no
    operating-income line yields `not_presented`, not an empty value; every `derived` cell names
    the arithmetic that produced it.
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: "Every empty cell must say which kind of empty it is… three kinds,
  three distinct renderings — never one blank."

## Task 6 — assemble a multi-year series keyed on the filer's own concept

- **Description**: Write `series_for(accessions) -> Series` joining N filings into 10+ years,
  keying series identity on the FILER'S OWN concept (measured near-stable: 0-1 transitions per
  decade) and never on its label. Record each concept transition as an explicit reviewable
  event carrying both concepts and both values; resolve overlapping vintages by the store's
  existing newest-filed policy rather than a new one.
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_series.py
- **Files touched**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_series.py,
  investing-toolkit/tests/analysis/test_kpi_us_statement_series.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py
- **Acceptance**:
  - **RED**: `test_label_churn_does_not_split_a_series` — IBM held one concept for 14 years while
    its label moved `Total revenue` → `Total revenue (Note T)` → `Revenue (Note O)` →
    `Revenue (Note C)` → `Revenue (Note D)` → `Revenue`; the series must stay ONE series, and a
    label-keyed implementation must be what fails.
  - **GREEN**: KO's single 2019 concept transition (`SalesRevenueGoodsNet` → `Revenues`) surfaces
    as one recorded transition event, not as two unrelated series and not as a silent merge.
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: "Series identity keys on the FILER'S OWN concept …, never on its label;
  a transition is recorded as an explicit, reviewable event rather than silently resolved."

## Task 7 — re-express the 15-field spine as a view, field list unchanged

- **Description**: Make `kpi_spine_view` derive its 15 fields from the reconstruction instead of
  resolving `SPINE_FIELD_CHAINS` against the raw store, WITHOUT changing which fields exist, and
  render `not_presented` distinctly from empty so the cell taxonomy survives to the reader.
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py
- **Files touched**: investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py,
  investing-toolkit/tests/analysis/test_kpi_spine_view.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_cells.py
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_series.py
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/analysis/test_kpi_spine_view.py
- **Acceptance**:
  - **RED**: `test_sector_revenue_no_longer_blank` — DUK (`RegulatedAndUnregulatedOperatingRevenue`)
    and PLD (`RealEstateRevenueNet`), whose revenue the chain cannot resolve at all, must yield a
    revenue value; and PSX must yield its own declared total `RevenuesAndOtherIncome`
    (104,622M) rather than the chain's 2.2%-low `SalesRevenueNet` (102,354M).
  - **GREEN**: the 15 field names are byte-identical to today's; the existing tearsheet tests
    still pass; an oil major's `operating_income` renders as `not_presented`, distinct from empty.
- **Dependencies**: Tasks 5, 6 complete first
- **Independent**: true
- **Brief item covered**: "The 15-field spine re-expressed as a view over the reconstruction …
  **The field list is unchanged** … the view renders 'not presented' distinctly from empty."

## Task 8 — report the per-era resolution rate

- **Description**: Emit, per reconstruction run, how many statements resolved and how many did
  not, BROKEN DOWN BY FILING ERA, plus the reason each unresolved one failed. The 63-of-65 figure
  was measured on 2016-2018 filings only, and a 10-year run spans years never sampled.
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_check.py
- **Files touched**: investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_check.py,
  investing-toolkit/tests/analysis/test_kpi_us_statement_check.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/specs/2026-07-26-as-filed-statement-reconstruction.md
- **Acceptance**:
  - **RED**: `test_unresolved_statements_are_counted_with_a_reason` — DUK's 2013-2017 filings
    yield 2-3 candidate totals and must be counted as unresolved WITH that reason, never dropped
    silently and never resolved by picking one.
  - **GREEN**: the report separates eras, and a run in which every statement resolves still emits
    the counts rather than staying silent.
- **Dependencies**: Task 4 completes first
- **Independent**: false
  <!-- shares kpi_us_statement_check.py with Task 4 AND depends on it, so it can never be
       dispatched in parallel with it; claiming true would be a false disjointness claim -->
- **Brief item covered**: "Per-era resolution rate reported, not assumed."

## Task 9 — expose the reconstruction on the command surface

- **Description**: Add a `reconstruct` verb producing one company's statements for N accessions,
  registered in the pack registry alongside the existing US-only packs, and declared in the
  skill's command surface.
- **Module**: investing-toolkit/skills/data-markets/scripts/pack_us.py
- **Files touched**: investing-toolkit/skills/data-markets/scripts/pack_us.py,
  investing-toolkit/skills/data-markets/scripts/pack.py,
  investing-toolkit/tests/data/test_data_markets_us.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/pack_us.py
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/pack.py
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/data/test_data_markets_us.py
- **Acceptance**:
  - **RED**: `test_reconstruct_pack_is_registered_and_us_only` — the new pack must appear in
    `SUPPORTED_PACKS`, dispatch through `build_pack`, and be rejected for non-US markets.
  - **GREEN**: the verb is declared in the skill's command surface and verified to run; a
    dependency-free invocation fails with the client-deps message rather than a bare
    `ModuleNotFoundError`.
- **External surfaces**:
  - SDK package: edgartools==5.42.0, supplied on the `uv run` invocation (`--with`), never
    imported by `pack.py` itself — grounding: `pack.py` is a zero-dependency facade
    (`investing-toolkit/skills/data-markets/scripts/pack.py` module header).
  - SDK package: requests==2.33.1, same invocation-supplied contract — grounding: the sibling
    as-reported lane's live dogfood failed with a bare
    `ModuleNotFoundError: No module named 'requests'` until it was passed on the invocation
    (recorded as a Gotcha trailer on PR #619, 2026-07-26).
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: "For ONE US company: the three statements as filed, for 10+ years."

## Task 10 — prove the reconstruction against a real filed document

- **Description**: Commit a hand-transcribed excerpt of one real 10-K's income statement and
  assert the reconstruction matches it LINE BY LINE — order, the filer's own labels, and values.
  Sum reconciliation cannot prove this: lines outside every sum (EPS rows carry no weight and no
  calculation parent), presentation order, and labels are all unverified by it.
- **Module**: investing-toolkit/tests/analysis/test_kpi_us_statement_reconstruction_fidelity.py
- **Files touched**:
  investing-toolkit/tests/analysis/test_kpi_us_statement_reconstruction_fidelity.py,
  investing-toolkit/tests/data/fixtures/ko_fy2017_income_statement_as_filed.json
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_shape.py
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statement_cells.py
- **Acceptance**:
  - **RED**: `test_reconstructed_statement_matches_the_filed_document_line_for_line` — the
    transcribed KO FY2017 income statement (accession 0000021344-18-000008) must match the
    reconstruction exactly; a single leaked dimensional row, dropped line, or reordering fails it.
  - **GREEN**: every transcribed line matches in order, label, and value, and the transcription's
    provenance (accession + the filed document URL) is recorded in the fixture.
- **Dependencies**: Tasks 3, 5 complete first
- **Independent**: true
- **Brief item covered**: "**Acceptance is line-by-line against the real filing**, not sum
  reconciliation alone."

## Task 11 — retire what this change makes obsolete

- **Description**: Dispose of the two artefacts this change orphans, in this change: give
  `SPINE_FIELD_CHAINS` a disposition — deleted, or kept with its remaining role written down —
  and close the superseded BACKLOG entry with a pointer to the brief. Leaving either as
  dead-but-live is the technical debt the brief names.
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py
- **Files touched**: investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py,
  investing-toolkit/tests/analysis/test_kpi_spine_view.py,
  docs/loom/BACKLOG.md
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/BACKLOG.md
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/specs/2026-07-26-as-filed-statement-reconstruction.md
- **Acceptance**:
  - **RED**: `test_spine_field_chains_has_a_stated_disposition` — fails while the symbol survives
    still described as resolving the spine's fields (the claim Task 7 makes false). Passes when
    the symbol is gone from the module, or when the prose that describes it names what it is
    still for. NOTE FOR THE IMPLEMENTER: `SPINE_FIELD_CHAINS` is a module-level TUPLE — it has no
    reachable `__doc__` (`SPINE_FIELD_CHAINS.__doc__` returns `tuple`'s own). Its prose is the
    `#` comment block immediately preceding it at `kpi_spine_view.py:190-200`; assert against the
    module SOURCE text, never against an attribute.
  - **GREEN**: the BACKLOG entry "spine chain misses 33 filer-years" is closed with a pointer to
    this brief rather than left implying the synonym fix is still the plan; no other BACKLOG entry
    is edited.
- **Dependencies**: Task 7 completes first
- **Independent**: false
- **Brief item covered**: "`SPINE_FIELD_CHAINS` … must not be left in place as dead-but-live
  config: either it is deleted, or its remaining role is written down explicitly, in the same
  change" + "The BACKLOG entry … must be closed with a pointer."

## Notes

- Change-folder binding: **N/A**. Two non-archived change-folders exist
  (`docs/loom/2026-07-12-us-sec-primary-source-layer`,
  `docs/loom/2026-07-19-8k-prose-kpi-intake`) but both belong to shipped arcs and neither
  matches this branch or this work; the input is the brainstorming brief named above. Archiving
  those two is unrelated housekeeping, filed to BACKLOG rather than done here.
- The brief's three Open Questions (financial-sector filers' derived view, whether the 3 cash-flow
  declaration quirks should ever be auto-corrected, and measured cost per company) are
  deliberately NOT tasks. They are decisions to surface with evidence, not work to schedule.
- Task 1 is the plan's highest-risk task and was measured to fail in its obvious form. It is
  isolated in its own module precisely so its test suite can be adversarial without entangling
  the assembly logic.
- Round-1 plan-document-reviewer findings, all applied: Task 8 `Independent` corrected to `false`
  (it shares a module with Task 4 and depends on it); Task 9's test retargeted from
  `tests/analysis/test_kpi_us_statement_shape.py` to `tests/data/test_data_markets_us.py`, which
  both removes a `Files touched` overlap with Task 2 and restores the repo's convention that every
  `SUPPORTED_PACKS` test lives beside its market's pack; Tasks 7 and 10 marked `Independent: true`
  (advisory — disjoint files, no dependency edge); `External surfaces` on Tasks 3 and 9 rewritten
  into the schema's `category: name — grounding: source` bullet form. Task 11 was ADDED for the
  `What Becomes Obsolete` gap the reviewer flagged as advisory and the planner had independently
  caught: no task committed to a disposition for `SPINE_FIELD_CHAINS` or to closing the superseded
  BACKLOG entry.
- Post-PASS amendment, re-review skipped (schema-safe, additive precision only — no field, task,
  dependency, or DAG change): Task 11's RED said "docstring", but `SPINE_FIELD_CHAINS` is a
  module-level tuple with no reachable `__doc__`; the wording now points the implementer at the
  `#` comment block at `kpi_spine_view.py:190-200` and at asserting against module SOURCE text.
  Task 9's `External surfaces` split into one bullet per surface per the schema.
- Depth moved 4 → 5 with Task 11 (it must follow Task 7, which shares `kpi_spine_view.py`). Five is
  the ceiling, not a comfortable margin: any further task appended to that chain forces a re-cut
  rather than a stretch.

Kickoff decision: the reconstruction is RECOMPUTED, never persisted. No derived cache, and
nothing is written to `kpi_store`. Measured 2026-07-26 on KO 0000021344-18-000008: a filing costs
10.7s cold and **1.3s warm** (edgartools already disk-caches its parse — warm parse is 0.32s), so
a 10-year company is ~42s cold and ~5s on re-read. A derived cache would buy back roughly five
seconds while adding an invalidation surface whose correct trigger is NOT time but OUR OWN CODE
CHANGING (filings are immutable; an amendment is a new accession, hence a new key), so a naive
TTL cache would serve a stale reconstruction after a logic fix — the exact "system disguises its
own failure as data" mode this arc exists to remove. Consequence for implementers: write the
reconstruction as a PURE FUNCTION of (filing, derivation version). A pure function can be wrapped
in a cache later without touching any caller, so the batch-screening case (100 filers x 42s) stays
an addition, never a rewrite.

Kickoff decision: where the filing declares no total, emit a VISIBLE, TYPED gap — never fall back
to `SPINE_FIELD_CHAINS`. User decision 2026-07-26 ("甲"), on the ground that a silently-low year
reads as a downturn on a 10-year trend. Known cost, accepted: CAT and NOW lose a currently-correct
chain-served number and become honest gaps. Net on the measured year is 12 filings fixed against
2 regressions to a gap.

## Decision Log

- **2026-07-26, Task 1 → Task 3 (raised by Task 1's spec-reviewer, PASS-with-notes).** Two
  obligations Task 1 deliberately did NOT take on, both of which land on Task 3's 80→26 reduction:
  1. **Abstract header rows are currently KEPT.** The XBRL convention also reserves `Abstract` and
     `RollForward`, and neither is in Task 1's `_STRUCTURAL_SUFFIXES` — correctly so, since the
     brief enumerates only the five placeholder kinds. So `us-gaap:IncomeStatementAbstract` passes
     `is_statement_line`. Task 3 must dispose of header rows itself, and must decide DELIBERATELY
     whether a header is a rendered line (it carries the section title a reader expects) or noise.
  2. **Dimension proof is presence-dependent, not absolute.** Task 1 rejects any row carrying a
     truthy key whose name contains "dimension", so a row carrying NO such key is PRESUMED
     undimensioned and kept. That fails closed only while edgartools keeps the substring in the
     key name; a rename that drops it, or a shape where the key is simply absent on dimensioned
     rows, fails OPEN. Task 3 touches the live `get_statement` shape and MUST re-confirm the real
     row shape rather than inheriting the presumption untested.

     **PREDICTION REFUTED 2026-07-26 — it failed CLOSED, not OPEN, and the obligation is what
     caught it.** Task 3 returned BLOCKED after measuring the live shape, and the orchestrator
     confirmed it directly. A `get_statement` row carries FOUR keys containing `dim`, in two
     groups meaning OPPOSITE things: `is_dimension` / `full_dimension_label` /
     `dimension_metadata` mark a row that IS a segment slice, while `has_dimension_children` marks
     an ordinary CONSOLIDATED line that HAS slices beneath it. Matching the substring therefore
     deleted the top line of every statement disclosing segments — KO FY2017 income kept 17 of 26
     (losing `NET OPERATING REVENUES`, `OPERATING INCOME`, `INCOME BEFORE INCOME TAXES`), DUK
     FY2017 income 18 of 52, and Realty Income FY2025 lost `Total assets` / `Total liabilities` /
     `Total equity`. That is silent DELETION of a filer's headline figures — the corruption the
     brief exists to prevent, arriving by the direction this entry ruled out.

     Root cause, recorded because the chain matters more than the fix: a reviewer correctly
     measured `dim_srt_ProductOrServiceAxis` on the FACT-row surface (`sec_edgar_client.py`
     :2277-2288) and recommended widening `dimension` to `dim`; the orchestrator relayed it as
     preferred; the implementer applied it to the PRESENTATION-row surface, which has a different
     key vocabulary. Evidence measured on one external surface was applied to another. The
     orchestrator's "verified live" row-key list in the Task 3 dispatch also omitted all three of
     the newly-relevant keys — as Task 3's implementer put it, a capture that had listed them
     would have caught this at plan time.
- **2026-07-26, Task 2 → Task 3.** Role SELECTION ("prefer a pure income role over a combined
  income-and-comprehensive one") was deliberately left out of `statement_kind`, which is total and
  order-free by design: choosing BETWEEN roles needs a filing's whole role set, which only Task 3's
  assembly sees. Task 3 owns it. Recorded here rather than only in the module's own docstring
  (§"SELECTING AMONG ROLES IS NOT THIS FUNCTION'S JOB"), because an obligation living solely in a
  docstring is one nobody is required to read. Cited by SECTION HEADING, not line number: this
  entry pointed at `:39`, then `:55`, and was stale both times after docstring edits — a line
  number is the wrong join key for a moving target.
