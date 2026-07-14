# Plan: operational-kpi slice 7 — apply break → dual as-reported/recast series

Source brief: docs/loom/specs/2026-07-14-operational-kpi-dual-series.md
Total tasks: 4
Critical-path depth: 3 (≤5)   ← longest chain T2 → T3 → T4 (T1 is a parallel leaf)
Execution order: parallel-where-possible (T1 kpi_break + T2 kpi_series are disjoint files)
Plan-document-reviewer verdict: PASS (2026-07-14; 12/14 applicable checks, T1/T2 Independent:true disjoint confirmed)

Change-folder binding: realizes a SUBSET of operational-kpi/spec.md (Requirements "Dual
as-reported/recast series with visible break flag", "Naive concatenation is rejected").
Not archived (multi-slice; memo-feed = slice 8).

Notes:
- apply_break extends kpi_break.py's break lifecycle (CONFIRMED → APPLIED) — the break
  representation stays cohesive in kpi_break. The split/view representation lives in a
  new pure-compute kpi_series.py that takes series `points` as an argument (does NOT
  query kpi_store — decoupled, mirroring kpi_validate).
- T1 (kpi_break.py) and T2 (kpi_series.py) touch DISJOINT files → Independent:true; they
  may dispatch in one wave. T3/T4 share kpi_series.py with T2 → Independent:false.
- No wall-clock; apply_break lock-guarded (reuse _store_fs). The no-naive-concat guard is
  the load-bearing property.

## Task 1 — apply_break: CONFIRMED → APPLIED on the kpi_break record (+ break_period)
- Description: Add `apply_break(company, break_id, break_period)` to `kpi_break.py`:
  require the break-event is CONFIRMED (from slice 6); transition CONFIRMED → APPLIED,
  recording `break_period` on the record; reject loud applying a non-CONFIRMED break
  (FLAGGED / DISMISSED / already-APPLIED). Lock-guarded RMW via _store_fs (mirror
  confirm_break's store write). Apply is a mechanical follow-through of the slice-6
  human confirm — NOT a new human-confirm (no review_queue adjudication needed).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py,
  investing-toolkit/tests/analysis/test_kpi_break.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_break.py::test_apply_break_confirmed_to_applied fails
  - GREEN: flag→confirm→apply_break(break_period) → status APPLIED + break_period stored;
    apply on a FLAGGED/DISMISSED/already-APPLIED break → raises loud, unchanged.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #1 "Apply a confirmed break". Change-folder join:
  operational-kpi / Requirement "Dual as-reported/recast series with visible break flag" /
  Scenario "Trend view shows both lineages" (the apply that precedes it).

## Task 2 — kpi_series scaffold + split_series (pure compute)
- Description: Create `scripts/kpi_series.py` (PEP-723, same-dir import shim; pure compute
  — no persistence). `split_series(points, applied_breaks)`: given period-ordered
  `points` (each `{period, value, ...}`) and APPLIED breaks (each `{break_period, ...}`),
  return `{"as_reported": [points with period < earliest break_period], "recast": [points
  at/after it], "break_markers": [{break_period}...]}`. No applied breaks → all points in
  `as_reported`, `break_markers: []`. Register KPI_SERIES_SCRIPT in conftest.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_series.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_series.py,
  investing-toolkit/tests/analysis/test_kpi_series.py,
  investing-toolkit/tests/analysis/conftest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_series.py::test_split_series_partitions_by_break fails
  - GREEN: points across a break_period split into as_reported (before) + recast
    (at/after) + a marker; no breaks → all as_reported, no markers.
- External surfaces: stdlib only; no third-party.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #2 "Split a series by its applied breaks".
  Change-folder join: operational-kpi / Requirement "Dual as-reported/recast series with
  visible break flag" / Scenario "Trend view shows both lineages".

## Task 3 — series_view: basis-required (no naive concatenation across a break)
- Description: Add `series_view(points, applied_breaks, basis)` to kpi_series.py: `basis`
  ∈ "as-reported" | "recast" | "dual". Returns the as_reported list / recast list / the
  full dual dict (as_reported+recast+markers) accordingly. If there IS an applied break
  AND basis is None → raise loud ("a series across a break requires an explicit basis;
  refusing naive concatenation"). No applied break → return the flat series for any basis
  (or None) — nothing to disambiguate.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_series.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_series.py,
  investing-toolkit/tests/analysis/test_kpi_series.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_series.py
- Acceptance:
  - RED: ...::test_series_view_requires_basis_across_break fails
  - GREEN: with an applied break, basis None → raises; "as-reported"/"recast"/"dual"
    return the respective view; with NO break, basis None → returns the flat series (no raise).
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: Smallest End State #3 "Basis-required view (no naive concat)".
  Change-folder join: operational-kpi / Requirement "Naive concatenation is rejected" /
  Scenario "Naive concatenation is rejected".

## Task 4 — kpi_series CLI: apply / view
- Description: argparse CLI (mirror sibling CLIs, exit 0/1/2): `apply` (--company
  --break-id --break-period → kpi_break.apply_break, print the updated break record),
  `view` (--company --basis + points JSON + applied_breaks JSON from stdin/--file →
  series_view result JSON). Document in analysis-kpi/SKILL.md `## CLI (kpi_series)`.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_series.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_series.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/tests/analysis/test_kpi_series.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_series.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py
  - investing-toolkit/skills/analysis-kpi/SKILL.md
- Acceptance:
  - RED: ...::test_cli_apply_and_view_roundtrip fails
  - GREEN: (after a flag+confirm setup) `apply --break-period ...` → break record APPLIED;
    `view --basis dual` (points + applied_breaks stdin) → the dual dict; `view` with a
    break and NO --basis → exit 1 (the refuse-naive-concat ValueError); malformed JSON →
    exit 2; subcommands listed by `--help` AND documented in SKILL.md `## CLI (kpi_series)`.
- Command surface: apply/view verbs declared in analysis-kpi/SKILL.md `## CLI (kpi_series)`.
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: Smallest End State #4 "a thin CLI".
