# Plan: US SEC financial-table cross-validation (analysis-xval)

**Source brief**: docs/loom/specs/2026-07-13-us-sec-financial-table-xval.md
**Change-folder spec**: docs/loom/2026-07-12-us-sec-primary-source-layer/specs/financial-table-xval/spec.md
**Total tasks**: 17 (width uncapped; only depth is the ceiling)
**Critical-path depth**: 4 (≤5 ✓ — 5 levels / 4 edges by the schema's edge-count convention; deepest chain T3→T4→T5→T8→{T9,T14})
**Execution order**: parallel-where-possible (two disjoint modules start in parallel; compute tasks share one file → sequential within Module X)
**Plan-document-reviewer verdict**: PASS (2026-07-13; 14/14 — Checks 12/16 N/A, 13–14 satisfied by the disjoint T1/T3 Independent pair; 3 advisory notes, none blocking)

> **Input**: loom-spec change-folder `2026-07-12-us-sec-primary-source-layer`, capability
> `financial-table-xval` (9 Requirements / 17 scenarios; **16 mapped, 1 user-approved DROP** — see Notes).
> Bound via **Layer 0 (explicit handoff)**. Validator `validate_spec_output.py` → `exit 0` (direct
> non-freeze consume, run 2026-07-13). Traceability is by stable join key
> `<change-id> / Requirement: <name> / Scenario: <name>` (point-don't-copy — the spec is SSOT;
> this plan links back, never duplicates the delta). THEN observables / magic values copied verbatim.
>
> **Module map** (two disjoint code modules + one doc):
> - **D** = data layer, `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
>   (+ offline `investing-toolkit/tests/data/test_sec_xval.py`, live anchor in existing
>   `investing-toolkit/tests/data/test_data_markets_live.py`). Source A statement extraction is
>   net-new I/O here (confirmed ABSENT today — recon: `get_statement`/`financials`/`to_dataframe`
>   token count = 0 in this file).
> - **X** = analysis layer, `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
>   (+ `investing-toolkit/tests/analysis/test_analysis_xval.py`). Pure compute over two pre-fetched
>   JSON paths — mirrors the analysis-comps template.
> - **S** = `investing-toolkit/skills/analysis-xval/SKILL.md` (new skill doc).
>
> The DAG is **wide-but-shallow**. Every Module-X compute task shares `xval_compute.py` → all
> `Independent: false` among themselves (shared write set), SDD dispatches them sequentially; the
> depth number is the *logical* dependency chain, not the dispatch order (same shape as the narrative
> plan). Only T1 (Module D) and T3 (Module X skeleton) are cross-module disjoint at level 1 →
> `Independent: true`, dispatchable in one wave.

---

## Task 1 — Source A: extract statement cells + live shape-anchor

- **Description**: Add `extract_statement_cells(filing, statement_name)` to `sec_edgar_client.py` that
  pulls a primary financial-statement table (balance sheet / income / cash flow / equity) from a filing
  via the edgartools XBRL statement API — `filing.xbrl().get_statement(<name>)` for rendered rows and
  `filing.xbrl().get_facts()` / `.facts.to_dataframe()` for the per-cell fact graph — and normalizes
  each cell to the **declared Source-A schema** (Notes §Schemas). Never free-text / regex the document
  body. Build on the working spine only; do NOT touch `filing.xbrl().instance` or
  `Company().financials` (dead traps on 5.42.0).
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_data_markets_live.py`, `investing-toolkit/tests/analysis/fixtures/xval_source_a_aapl_bs.json`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/data/test_data_markets_live.py`
- **Acceptance**:
  - **RED** (network shape-anchor — the arc's mandated live probe): `test_data_markets_live.py::test_extract_statement_cells_live_shape` (`@pytest.mark.network`) — against the real AAPL 10-K (accn `0000320193-25-000079`), assert `extract_statement_cells(filing, "BalanceSheet")` returns a non-empty list where **each** cell carries `concept`, `period`, `dimension` (null or `{axis, member}`), `value_displayed`, `numeric_value` (float), `decimals` (str, e.g. `"-6"`), and a `citation` with `accession` + `statement_name` + `row`/`col` + `context_ref`/`fact_id`. Also assert a real dimensional fact is reachable (iPhone segment under `srt:ProductOrServiceAxis` member `aapl:IPhoneMember`). This pins the edgartools shape in-repo.
  - **GREEN**: `extract_statement_cells` returns declared-schema cells for the real filing; a captured fixture `xval_source_a_aapl_bs.json` (mirrored from this real shape) is written for offline compute-task reuse (fixtures-mirror-producer-shape).
- **External surfaces**: SDK `edgartools` 5.42.0 — statement spine `filing.xbrl().get_statement(name)` (raises `StatementNotFound` on absent) / `.get_facts()` / `.facts.to_dataframe()`; dead traps `filing.xbrl().instance`, `Company().financials` (do NOT use). Grounding: brief §Grounding (live-verified AAPL 10-K, 2026-07-13).
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Extract financial-statement tables as structured cells / Scenario: Extract balance-sheet cells from a 10-K`

## Task 2 — Source A: fail loud when no structured statement exists

- **Description**: When a filing/statement variant has no XBRL-backed statement dataframe (pre-XBRL
  filing, or a statement edgartools cannot parse — surfaces as `StatementNotFound`), `extract_statement_cells`
  MUST report an extraction failure for that statement (typed error / error slot) and MUST NOT fall back
  to an LLM-guessed or regex-scraped cell value.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/data/conftest.py`
- **Acceptance**:
  - **RED**: `test_sec_xval.py::test_extract_raises_on_absent_statement` (offline; a mocked `filing.xbrl().get_statement` raising `StatementNotFound`) — `extract_statement_cells` surfaces an extraction-failure for that statement; the test asserts NO regex/free-text scrape path is taken and no synthesized cell value is returned.
  - **GREEN**: absent/unparseable statement → loud extraction-failure, never a fabricated cell.
- **External surfaces**: SDK `edgartools` 5.42.0 — `StatementNotFound` exception type.
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Extract financial-statement tables as structured cells / Scenario: Extraction fails loud when no structured statement exists`

## Task 3 — analysis-xval CLI + report skeleton (contract)

- **Description**: Create `analysis-xval/scripts/xval_compute.py` as a pure-compute skill mirroring the
  analysis-comps CLI template. `main() -> int` with argparse reading `--source-a <path>` (doc-table cells
  pack, Source A) and `--source-b <path>` (companyfacts pack, Source B), emitting a JSON report scaffold
  to stdout via `json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)` + trailing newline, exit 0.
  Bad arg combos (missing/unreadable path) → `parser.error(...)` / `return 2`. The report **envelope**
  fixes the declared report-entry schema (Notes §Schemas), including the load-bearing
  `source_mode: "two-source" | "single-source"` field on every entry. No matching/classify logic yet —
  empty `comparisons`.
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-comps/scripts/comps_compute.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/analysis/conftest.py`
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_cli_emits_report_scaffold` + `::test_bad_args_exit_2` — `run_script(XVAL_SCRIPT, "--source-a", a, "--source-b", b)` returns exit 0 with parseable JSON carrying keys `comparisons` (empty list), `high_alerts`, `single_source`, `_provenance`; a missing required arg / unreadable path → returncode 2.
  - **GREEN**: CLI resolves via `uv run --script`, emits the scaffold, exit codes correct.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: brief §Smallest End State — "A new `analysis-xval` skill (SKILL.md + `scripts/xval_compute.py` + a CLI), following the `analysis-comps` template … JSON report to stdout".

## Task 4 — Source B fact index reconstructed from companyfacts (independent)

- **Description**: In `xval_compute.py`, build the Source-B fact index from the companyfacts pack
  (rows in the `summarize_concept` shape: `start,end,value,accn,form,fy,fp,filed`, under a concept key),
  keyed by `(concept, period)` with `dimension = None` (companyfacts is consolidated-only — no dimension,
  no scale/decimals, per live probe). The index is built ONLY from the Source-B input path — never
  derived from or copied out of the Source-A input (independence invariant).
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`, `investing-toolkit/tests/analysis/fixtures/xval_source_b_aapl.json`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_source_b_index_from_companyfacts` — given a Source-B fixture (companyfacts shape) and NO Source-A input for the same fact, the built index exposes the concept's value keyed by `(concept, period)` with `dimension=None`, sourced from the companyfacts rows.
  - **GREEN**: index reconstructs `(concept, period)->value(+accn)` independently from Source B.
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Independently reconstruct the same facts from XBRL / Scenario: Reconstruct a concept's value from companyfacts`

## Task 5 — Match non-dimensional cell by concept+period

- **Description**: Match a Source-A doc-table cell to its Source-B fact by the triple
  `(concept, period, dimension)`; for a non-dimensional cell (`dimension=None`), pair it with the
  Source-B fact sharing that concept+period and no dimension member on either side. MUST NOT match by
  table position, row-label text, or label similarity.
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module from Task 3)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/2026-07-12-us-sec-primary-source-layer/specs/financial-table-xval/spec.md`
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_match_non_dimensional_by_concept_period` — a doc cell tagged `us-gaap:Revenues` FY2024 pairs with the Source-B fact sharing that concept+period, dimension=None both sides; a same-concept fact under a different label is not matched on label grounds.
  - **GREEN**: matcher pairs non-dimensional cells on the (concept, period) key only.
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Match doc-table cell to XBRL fact by concept+period+dimension / Scenario: Match a non-dimensional concept by concept+period`

## Task 6 — Dimensional match requires the dimension member to agree

- **Description**: Extend the matcher: for a doc cell carrying a dimension (e.g. `us-gaap:Revenues`
  under `srt:ProductOrServiceAxis` member `ProductA`), a candidate fact is accepted ONLY if its
  dimension member also equals `ProductA`; a same-concept / same-period fact under a different or no
  dimension member is NOT accepted.
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module from Task 3)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/2026-07-12-us-sec-primary-source-layer/specs/financial-table-xval/spec.md`
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_dimensional_match_requires_member_agreement` — a `ProductA` doc cell is NOT matched to a same-concept/same-period fact under a different (or no) member; only the member-equal fact is accepted.
  - **GREEN**: dimensional matching enforces member equality.
- **Dependencies**: Task 5 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Match doc-table cell to XBRL fact by concept+period+dimension / Scenario: Dimensional fact requires the dimension member to also agree`

## Task 7 — No XBRL counterpart → unmatched, routed to single-source

- **Description**: When a doc cell's `(concept, period, dimension)` triple has no matching Source-B fact,
  record it as unmatched and route it to single-source handling (NOT paired with an unrelated fact). This
  is the join point for Task 15's single-source-honesty output.
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module from Task 3)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/2026-07-12-us-sec-primary-source-layer/specs/financial-table-xval/spec.md`
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_no_counterpart_routes_to_single_source` — a doc cell whose triple has no Source-B fact is recorded unmatched and routed to single-source, never paired with an unrelated fact.
  - **GREEN**: unmatched cells are routed to single-source handling.
- **Dependencies**: Task 5 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Match doc-table cell to XBRL fact by concept+period+dimension / Scenario: No XBRL counterpart exists for the concept+period+dimension`

## Task 8 — Classify divergence into low/medium/high with xval's own 1%/5% bands

- **Description**: Reuse the analysis-comps **diff math** (`abs_diff`, `pct_diff = (abs_diff/xbrl_val)*100.0`)
  and mirror the classifier STRUCTURE, but with **xval's own band constants** — do NOT import comps'
  bands. Declare `XVAL_BAND_LOW = 0.01`, `XVAL_BAND_HIGH = 0.05`; classifier: `abs_pct <= XVAL_BAND_LOW*100`
  → `low`; `<= XVAL_BAND_HIGH*100` → `medium`; else `high` (matching comps' percent-scaled-input,
  fraction-band convention). Both values always retained on the entry.
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-comps/scripts/comps_compute.py`  (reuse `_compute_divergence` math + `_classify_divergence_alert` shape at `:946`/`:955`; NOT the `DIVERGENCE_BAND_*` values at `:67-68`)
- **Acceptance**:
  - **RED** (parametrized, two scenarios): `test_analysis_xval.py::test_classify_bands[low]` — a matched pair with `pct_diff` 0.4% → alert `low`; `::test_classify_bands[high]` — a matched pair with `pct_diff` 8% → alert `high`.
  - **GREEN**: classifier returns `low`/`medium`/`high` off the 1%/5% bands with both values retained.
- **Dependencies**: Task 5 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Classify divergence with a tolerance band / Scenario: Divergence within the low band`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Classify divergence with a tolerance band / Scenario: Divergence above the high band`

## Task 9 — Undefined divergence classified n/a, never dropped

- **Description**: Reuse comps' n/a-never-drop discipline: when the XBRL value is `0` (pct_diff undefined)
  or either side is `None`, classify `alert: "n/a"` with a `note` explaining why, and the pair STILL
  appears in output (never silently omitted).
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module from Task 3)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/2026-07-12-us-sec-primary-source-layer/specs/financial-table-xval/spec.md`
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_undefined_divergence_is_na_not_dropped` — an XBRL-value-0 (or None-side) pair → `alert == "n/a"` with a note, and the pair is present in the report.
  - **GREEN**: undefined-divergence pairs are `n/a` + noted + retained.
- **Dependencies**: Task 8 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Classify divergence with a tolerance band / Scenario: Undefined divergence is classified n/a, not dropped`

## Task 10 — Recognize scale/rounding as a legitimate divergence (TWO-SOURCE tolerance label)

> **REVISED 2026-07-13 (grounding verdict B + user decision A).** The brief's original single-source
> framing (reconcile a rendered display value vs the full-magnitude fact) is **not implementable** —
> a live probe confirmed edgartools exposes NO retrievable rendered/scaled display value across ANY
> structured surface (`get_statement` rows, `facts.to_dataframe()`, even `render().to_dataframe()`/
> `.to_dict()` all return full-magnitude floats; the "$39,777" mantissa exists only as a transient
> `render().__str__()` formatting side-effect via `CellFormatter`). So `value_displayed == numeric_value`
> on all 152 real cells — there is no second number to reconcile single-source. **User chose (A):
> reframe as a TWO-SOURCE rounding-tolerance label** on a matched pair. See Notes §Grounding.

- **Description**: Operate on a **matched (doc_cell, xbrl_fact) pair** (the `route_cells` matched bucket).
  Compute the divergence between the doc `numeric_value` and the companyfacts `value` (both
  full-magnitude), then check whether that divergence is fully explained by the rounding grain implied by
  the doc cell's `decimals` (e.g. `decimals="-6"` → grain `10**6`). When a NON-ZERO divergence falls
  within the rounding tolerance (≈ half a grain — the maximum a same-underlying-value can differ once each
  side is rounded to that grain) → annotate the entry `category: "scale/rounding"`, keep `alert: "low"`,
  set `source_mode: "two-source"`, and add a note — MUST NOT flag it as a tagging error. A divergence
  BEYOND the tolerance is a real divergence (leave it for the classifier's band, do NOT label
  scale/rounding). Model the grain off `decimals` only; NEVER read a nonexistent `scale` field, and NEVER
  invent a rendered-display value.
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module; `classify_divergence`/`_compute_divergence` from Task 8, `route_cells` matched pairs from Task 7)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/analysis/fixtures/xval_source_a_aapl_bs.json`  (real Source-A shape: `value_displayed == numeric_value`, `decimals` like `"-6"` — code to THIS shape, never the invented `$1,234` mantissa)
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_within_grain_divergence_annotated_scale_rounding` — a matched pair whose doc `numeric_value` and companyfacts `value` differ by an amount WITHIN the `decimals`-implied rounding grain (e.g. doc `1234000000` vs xbrl `1233800000`, `decimals="-6"`, |diff| 200000 ≤ half-grain 500000) → entry annotated `category == "scale/rounding"`, `alert == "low"`, `source_mode == "two-source"`, NOT a tagging error. Plus a NEGATIVE case: a divergence BEYOND the grain is NOT labeled scale/rounding (non-vacuous).
  - **GREEN**: a within-rounding-grain two-source divergence is labeled `scale/rounding` (low); a beyond-grain one is not.
- **Dependencies**: Task 8 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Recognize scale/rounding as a legitimate divergence source / Scenario: Millions-scale rounding stays within tolerance`

## Task 11 — Do not force-match non-GAAP figures to a GAAP tag

- **Description**: When a doc-table row is an adjusted/non-GAAP metric (e.g. "Adjusted EBITDA") with no
  us-gaap concept covering it, record it as doc-only / no-XBRL-counterpart; MUST NOT pair it with a
  similarly-labeled but conceptually different GAAP fact (e.g. `us-gaap:OperatingIncomeLoss`) on
  label-similarity grounds.
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module from Task 3)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/2026-07-12-us-sec-primary-source-layer/specs/financial-table-xval/spec.md`
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_non_gaap_not_force_matched` — an "Adjusted EBITDA" doc cell with no us-gaap concept is recorded doc-only, and is NOT paired with `us-gaap:OperatingIncomeLoss` or any GAAP concept on label similarity.
  - **GREEN**: non-GAAP metrics without a GAAP concept are single-source, never force-matched.
- **Dependencies**: Task 5 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Do not force-match adjusted or non-GAAP figures to a GAAP tag / Scenario: Adjusted EBITDA has no GAAP counterpart`

## Task 12 — Restatement-signal across two filings (companyfacts-only)

- **Description**: When a later filing's comparative figure for a period diverges from an earlier
  filing's tagged value for the same period, classify the divergence `restatement-signal` and cite BOTH
  filings' accession numbers — not a doc-vs-XBRL tagging error. Both filings' facts live in companyfacts
  keyed by `accn` (Source-B-only; no Source A needed). Confirm the accession keying against the Source-B
  pack shape at implementation time (Open Q2).
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module from Task 3)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`  (`summarize_concept` rows carry `accn` for cross-filing keying)
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_restatement_signal_cites_both_accessions` — the FY2023 comparative as tagged in the FY2023 10-K vs the same period as tagged in the FY2024 10-K diverge → entry classified `restatement-signal` with both accession numbers cited, NOT a tagging error.
  - **GREEN**: cross-filing comparative divergence → `restatement-signal` + both accns.
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Treat period/restatement mismatch and decimal-disagreement as signals, not bugs / Scenario: Prior-year comparative restated in the current filing`

## Task 13 — Decimal-disagreement flagged per DQC 2.4.1 (single-source, distinct category)

- **Description**: Detect XBRL US DQC rule 2.4.1 — a fact whose `decimals` attribute implies a precision
  inconsistent with the digits actually reported — and surface it as its OWN category
  `decimal-disagreement (DQC 2.4.1)`, distinct from a plain doc/XBRL value mismatch. Single-source
  structural check off `decimals` (per brief refinement).
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module from Task 3)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/2026-07-12-us-sec-primary-source-layer/specs/financial-table-xval/spec.md`
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_decimal_disagreement_dqc_241` — a fact whose `decimals` implies a precision inconsistent with its reported digits is flagged `decimal-disagreement (DQC 2.4.1)`, a category distinct from a value mismatch.
  - **GREEN**: DQC-2.4.1 inconsistency → its own `decimal-disagreement (DQC 2.4.1)` category.
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Treat period/restatement mismatch and decimal-disagreement as signals, not bugs / Scenario: Decimal-disagreement flagged per DQC 2.4.1`

## Task 14 — Surface high-alert divergence loudly + two/single-source label

- **Description**: Any `high`-alert pair is surfaced prominently under a `high_alerts` report section with
  the doc value, the XBRL value, `pct_diff`, and BOTH citations all present — MUST NOT silently pick one
  source, discard the other, or average them (mirrors comps direct-vs-compute surfacing). Also stamp every
  entry's `source_mode` (`two-source` for a doc-vs-companyfacts matched pair; `single-source` for a
  structural iXBRL-only finding) — the load-bearing two-source/single-source honesty label from the brief.
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module from Task 3)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-comps/scripts/comps_compute.py`  (direct-vs-compute alert surfacing to mirror)
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_high_alert_surfaced_both_values_and_label` — a `high` pair appears under `high_alerts` with doc value, XBRL value, `pct_diff`, and both citations intact (nothing dropped/overwritten), and its `source_mode == "two-source"`; a structural-only finding carries `source_mode == "single-source"`.
  - **GREEN**: high alerts surface loudly with both values + both citations; `source_mode` labelled on every entry.
- **Dependencies**: Task 8 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Surface high-alert divergence loudly, never silently reconcile / Scenario: High alert appears in output with both values intact`

## Task 15 — Single-source honesty: doc-only cell stated, not guessed

- **Description**: An unmatched doc-table cell (no XBRL counterpart, from Task 7) appears in the report
  with status `"doc-only, no XBRL counterpart"` and NO synthesized XBRL value invented to fill the gap
  (anti-fabrication invariant).
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module from Task 3; unmatched routing from Task 7)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/2026-07-12-us-sec-primary-source-layer/specs/financial-table-xval/spec.md`
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_doc_only_cell_stated_not_guessed` — an unmatched doc cell appears with status `"doc-only, no XBRL counterpart"` and no invented XBRL value.
  - **GREEN**: unmatched cells stated as doc-only, never gap-filled.
- **Dependencies**: Task 7 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: State single-source honesty and cite both sources for every compared number / Scenario: Doc-only cell stated, not guessed`

## Task 16 — Every compared fact carries both citations

- **Description**: For every matched-and-classified pair, attach BOTH provenance citations — a doc-table
  citation (`accession + statement name + cell location`) and an XBRL citation (`concept id + context ref`)
  — regardless of alert level.
- **Module**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`
- **Files touched**: `investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`, `investing-toolkit/tests/analysis/test_analysis_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (in-progress module from Task 3)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/2026-07-12-us-sec-primary-source-layer/specs/financial-table-xval/spec.md`
- **Acceptance**:
  - **RED**: `test_analysis_xval.py::test_compared_pair_carries_both_citations` — a matched/classified pair carries both a doc-table citation (accession + statement + cell) and an XBRL citation (concept id + context ref), at any alert level.
  - **GREEN**: every compared entry carries both citations.
- **Dependencies**: Task 5 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: State single-source honesty and cite both sources for every compared number / Scenario: Every compared fact carries both citations`

## Task 17 — analysis-xval SKILL.md (skill doc, analysis-comps template)

- **Description**: Author `analysis-xval/SKILL.md` mirroring the analysis-comps skeleton: frontmatter
  (`name: analysis-xval`, folded `description`), a Layer-2-contract / NO-I/O statement, an Input Contract
  (Source A + Source B pack paths), a CLI section pointing at `scripts/xval_compute.py` (the T3 contract),
  an Output Contract (the report envelope + two/single-source labels), and the i18n footer. Flat skill
  dir (no nested subfolders); body ≤ ~6,000 tokens.
- **Module**: `investing-toolkit/skills/analysis-xval/SKILL.md`
- **Files touched**: `investing-toolkit/skills/analysis-xval/SKILL.md`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-comps/SKILL.md`
- **Acceptance**:
  - **RED**: the skill-folder-structure hook + a doc read-back — `SKILL.md` exists with the required frontmatter (`name`/`description`) and the H2 sections (Input Contract, CLI, Output Contract); the `.claude/hooks/validate-skill-folder-structure.sh` PostToolUse check passes (flat dir).
  - **GREEN**: `SKILL.md` present, hook-clean, documents the T3 CLI contract; close-out read-back (Notes) confirms the shipped report sections match the doc.
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Brief item covered**: brief §Smallest End State — "A new `analysis-xval` skill (SKILL.md + `scripts/xval_compute.py` + a CLI)".

---

## Notes

### Scale/rounding grounding correction — Task 10 reframed (2026-07-13)
A SECOND grounding conflict in the scale/decimals neighborhood (the first was the companyfacts
scale/decimals DROP below). During SDD, the Task-10 code-quality reviewer caught a 🔴: the brief's
single-source scale/rounding check (reconcile a rendered display value vs the full-magnitude fact) is
**not implementable** on real data. A live probe (AAPL 10-K, edgartools 5.42.0) confirmed
**no retrievable rendered/scaled display value exists** on ANY structured edgartools surface —
`get_statement` rows, `facts.to_dataframe()`, and even `render().to_dataframe()`/`.to_dict()` all
return full-magnitude floats; the "$39,777" millions mantissa is only a transient `render().__str__()`
formatting artifact (`CellFormatter`). Hence `value_displayed == numeric_value` on all 152 real cells
(NOT a Task-1 capture bug — it faithfully reflects edgartools' data model). **User decision (A),
2026-07-13:** reframe scale/rounding as a **TWO-SOURCE rounding-tolerance label** — on a matched
doc↔companyfacts pair, a non-zero divergence within the `decimals`-implied rounding grain is annotated
`scale/rounding` (low, `source_mode:"two-source"`), never a tagging error; a beyond-grain divergence is
a real divergence. This honors the spec Requirement's intent ("MUST NOT classify a divergence fully
explained by display rounding as a tagging error") while being honest about the API. Rejected: (B) drop
the check; (C) a weak single-source decimals-consistency check overlapping DQC 2.4.1 (Task 13). The
brief's §Grounding "scale is not a separate field" refinement is superseded by this note; carry it when
the change-folder is archived.

### Post-PASS amendment (review-skip note)
Two cosmetic edits after the plan-document-reviewer returned PASS (14/14), both additive + schema-safe
so re-review is skipped per writing-plans §"Amending a PASS plan": (1) `Critical-path depth` header
corrected `5 → 4` (edge-count convention; still ≤5, no structural change); (2) verdict flipped
PENDING → PASS. Reviewer advisory notes NOT applied and why: its Check-15 hint to mark T2/T4 a second
parallel wave is declined — T2 shares `sec_edgar_client.py` with the already-`Independent: true` T1, so
flipping T2 would VIOLATE Check 14 (global pairwise `Files touched` disjointness among all
`Independent: true` tasks). T2 stays `Independent: false` by design.

### Coverage gate (change-folder input)
- Run BEFORE the plan-document-reviewer dispatch:
  `python3 loom-code/scripts/check_scenario_coverage.py docs/loom/2026-07-12-us-sec-primary-source-layer docs/loom/plans/2026-07-13-us-sec-financial-table-xval.md`
- **3-capability scope boundary (approved by design, not a gap):** the change-folder holds THREE
  capabilities (`narrative` / `financial-table-xval` / `operational-kpi`). This plan covers ONLY
  `financial-table-xval`. The coverage script scans all three, so its "dropped" set WILL list every
  `narrative` scenario (shipped in #558) and every `operational-kpi` scenario (blocked, future slice).
  Those are out-of-scope by design (brief §Out of Scope), the same approved boundary the narrative plan
  recorded (`docs/loom/plans/2026-07-12-us-sec-narrative.md` Notes). Self-review may PASS as long as the
  ONLY `financial-table-xval` scenario missing is the user-approved DROP below.

### User-approved DROP (coverage exception)
- Dropped join key: `2026-07-12-us-sec-primary-source-layer / Requirement: Independently reconstruct the
  same facts from XBRL / Scenario: companyfacts source carries scale and decimals metadata`
  (change-folder spec `:35-40`).
- **Reason**: factually FALSE per live probe (AAPL Revenue, all 113 facts, 2026-07-13) — the companyfacts
  API carries ONLY `accn,end,start,val,fy,fp,form,filed,frame`; NO `scale`, NO `decimals`/`precision`, NO
  dimension. The scenario cannot map to a task because the metadata it asserts does not exist.
  **Approval**: user signed off the HYBRID source model (brief §Decision) resolving this exact grounding
  error. The scale/rounding + DQC-2.4.1 requirements are re-homed as single-source structural checks
  against the doc-table's own iXBRL `decimals` (Tasks 10, 13) — no capability is lost, only re-sourced.
- The change-folder spec at `:35-40` is left UNTOUCHED (loom-spec consumer discipline); carry this
  correction when the change-folder is eventually archived.

### Declared schemas (producer/consumer decoupling — depth control)
So Module D (producer) and Module X (consumer) code to a plan-declared contract, not each other's runtime
(keeps T1 and T3 disjoint at level 1). Task 1's live shape-anchor pins the REAL edgartools shape; if it
diverges from this declaration, update the declaration at T1 and re-check dependents.
- **Source A cell** (doc-table, from edgartools statement extraction):
  `{concept, period:{type:"instant"|"duration", instant?, start?, end?}, dimension: null | {axis, member},
  value_displayed:str, numeric_value:float, decimals:str, citation:{accession, statement_name, row, col,
  label, context_ref, fact_id}}`
- **Source B fact** (companyfacts, `summarize_concept` shape under a concept key): `{concept,
  period:{start, end}, value:int (full-magnitude), accn, form, fy, fp, filed}` — no dimension, no
  scale/decimals (live-verified poverty).
- **Report entry**: `{concept, period, dimension, doc_value, xbrl_value, abs_diff, pct_diff, alert,
  source_mode:"two-source"|"single-source", category: null|"scale/rounding"|"restatement-signal"|
  "decimal-disagreement (DQC 2.4.1)", status?: "doc-only, no XBRL counterpart", doc_citation,
  xbrl_citation, note?}`. Report envelope: `{comparisons:[...], high_alerts:[...], single_source:[...],
  _provenance:{...}}`.

### Band constants (xval's own — do NOT reuse comps')
- `XVAL_BAND_LOW = 0.01` (~1%), `XVAL_BAND_HIGH = 0.05` (5%). Mirror comps' classifier convention
  (`_classify_divergence_alert` at `comps_compute.py:946` takes percent-scaled input, multiplies bands
  ×100) and its diff math (`_compute_divergence` at `:955`; edge cases: either side None → `n/a`+note;
  divisor 0 → `pct_diff=None, alert="n/a"`+note; both values always retained). Do NOT import comps'
  `DIVERGENCE_BAND_LOW=0.05`/`_HIGH=0.15` (`:67-68`) — different tuning.

### Anti-fabrication invariant (arc-wide, load-bearing)
The parser emits the number, never an LLM. Match by `concept+period+dimension` triple only — never by
table position, row label, or label similarity. Never synthesize a value to fill a gap. Never silently
reconcile a high alert (both values retained side by side).

### Fixture discipline (fixtures-mirror-producer-shape)
edgartools is a third-party producer — Task 1's `@pytest.mark.network` live anchor captures its REAL
statement/fact object shape; offline unit fixtures mirror THAT. Never hand-invent the edgartools shape.
Source B fixtures mirror the existing `summarize_concept` output shape.

### Close-out obligations (finishing-a-development-branch, NOT plan tasks)
- **Commit the untracked brief** `docs/loom/specs/2026-07-13-us-sec-financial-table-xval.md` with the
  first SDD commit (on disk, uncommitted).
- **Version bump**: any change under `investing-toolkit/skills/**` requires bumping
  `investing-toolkit/.claude-plugin/plugin.json` 2.7.0 → 2.8.0 + `python3 scripts/sync_codex_manifests.py
  investing-toolkit`; CI job `plugin version bump` enforces it.
- **Offline CI**: do NOT add `--with edgartools`/`--with requests` to the offline pytest command —
  offline tests stub/mock them; only network-marked tests may use them.
- **SKILL.md read-back** (T17 close-out): confirm the shipped `xval_compute.py` report sections match the
  documented Output Contract.
- Optional nit (out of scope, not required by brief): mention `analysis-xval` in the
  `using-investing-toolkit` router. Memo-wiring into `pack_memo_fetch` is DEFERRED (brief §Out of Scope).

### Open question carried to implementation
- **Q2 restatement accession keying**: Task 12 assumes both filings' comparatives are in companyfacts
  keyed by `accn`. Confirm the accession keying against the real Source-B pack shape at implementation
  time (companyfacts-only, no Source A).

### Kickoff one-way-door decisions (surface at SDD kickoff briefing)
1. **Source A extraction module boundary** — this plan homes net-new statement extraction in the DATA
   layer (`sec_edgar_client.py`), emitting a doc-table-cells pack that the pure-compute `xval_compute.py`
   consumes (layer discipline + narrative precedent). Alternative: put extraction inside the analysis-xval
   skill (rejected — mixes I/O into the analysis layer, breaks the fixture-test model).
2. **Memo-wiring deferred** — CLI/compute skill only; wiring xval into `pack_memo_fetch` is a follow-on
   slice (same cut narrative took). Late-vetoable.
3. **New skill vs extend** — `analysis-xval` is a NEW skill (recon found no existing validation/xval skill
   among the six `analysis-*`), following the analysis-comps template.
