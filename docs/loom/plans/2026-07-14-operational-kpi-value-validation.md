# Plan: operational-kpi slice 4 — rule-based value validation (pure compute)

Source brief: docs/loom/specs/2026-07-14-operational-kpi-value-validation.md
Total tasks: 6
Critical-path depth: 4 (≤5)   ← T1 → {T2,T3,T4} → T5 → T6
Execution order: sequential (all tasks touch one module kpi_validate.py + one test file)
Plan-document-reviewer verdict: PASS (2026-07-14; 14/14 applicable checks, no gaps)

Change-folder binding: realizes a SUBSET of operational-kpi/spec.md (Requirement
"Rule-based validation of parsed values"). Not archived (capability multi-slice).

Notes:
- kpi_validate.py is a PURE-COMPUTE module (stdlib, JSON in → verdict out) mirroring
  analysis-comps/dcf compute scripts — NO `_store_fs`, NO lock, NO persistence, NO
  network. A rule FAILURE is a normal `eligible:false` verdict, not an exception; only
  MALFORMED input is a loud error.
- All tasks share kpi_validate.py + test_kpi_validate.py → Independent:false; sequential.
  Depth is on the Dependencies DAG (T2/T3/T4 depend on T1's scaffold; T5 on T1-T4).

## Task 1 — kpi_validate scaffold + check_sign
- Description: Create `scripts/kpi_validate.py` (PEP-723 header, stdlib only). `check_sign(value, kpi_def)` → a `{"rule":"sign","passed":bool,"detail":...}`-style result: a kpi_def with `sign=="non-negative"` FAILS on a negative value; `sign` absent or `"any"` → passes (no constraint). Register KPI_VALIDATE_SCRIPT in conftest.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py,
  investing-toolkit/tests/analysis/test_kpi_validate.py,
  investing-toolkit/tests/analysis/conftest.py
- Context paths:
  - investing-toolkit/skills/analysis-comps/scripts/comps_compute.py
  - docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_validate.py::test_check_sign_rejects_negative_for_nonneg_kpi fails
  - GREEN: non-negative KPI + negative value → not passed; sign="any"/absent + negative → passed.
- External surfaces: stdlib only (json/sys/math); no third-party, no _store_fs.
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State #1 "Sign check". Change-folder join: operational-kpi / Requirement "Rule-based validation of parsed values" / Scenario "Sign convention violation is caught".

## Task 2 — check_unit
- Description: `check_unit(value_unit, kpi_def)` → the value's unit must equal the def's `unit`; mismatch → not passed; equal → passed.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py,
  investing-toolkit/tests/analysis/test_kpi_validate.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Acceptance:
  - RED: ...::test_check_unit_flags_mismatch fails
  - GREEN: value_unit "USD" vs def unit "units" → not passed; matching units → passed.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #2 "Unit check". Change-folder join: operational-kpi / Requirement "Rule-based validation of parsed values" / Scenario "Sign convention violation is caught" (companion unit rule).

## Task 3 — check_subtotal (parts sum to total within tolerance; absent parts = N/A)
- Description: `check_subtotal(segments, total, tol=0.01)` → the sum of `segments` must be within a RELATIVE tolerance of `total` (math.isclose-style); mismatch → not passed. If `segments` or `total` is absent/empty → the rule is N/A (a distinct result, NOT a failure).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py,
  investing-toolkit/tests/analysis/test_kpi_validate.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Acceptance:
  - RED: ...::test_check_subtotal_flags_sum_mismatch fails
  - GREEN: segments [10,20,30] total 60 → passed; total 100 → not passed; no segments → N/A (not failed).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #3 "Subtotal check". Change-folder join: operational-kpi / Requirement "Rule-based validation of parsed values" / Scenario "Segment KPIs must sum to the reported total".

## Task 4 — check_gaap (a non-GAAP KPI is not forced against a GAAP tag)
- Description: `check_gaap(kpi_def, has_gaap_match=...)` → a kpi_def marked non-GAAP (`gaap` false/absent) must NOT be failed for lacking a GAAP match (passes / N/A); the rule only meaningfully constrains a GAAP-declared KPI. The point: never force a company-defined non-GAAP metric against a GAAP tag.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py,
  investing-toolkit/tests/analysis/test_kpi_validate.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Acceptance:
  - RED: ...::test_check_gaap_does_not_force_nongaap fails
  - GREEN: a non-GAAP kpi_def with no GAAP match → NOT failed (passed/N/A).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #4 "GAAP-vs-non-GAAP rule". Change-folder join: operational-kpi / Requirement "Rule-based validation of parsed values" / Scenario "Non-GAAP metric is not forced against a GAAP tag".

## Task 5 — aggregate validate() → eligibility verdict + failures
- Description: `validate(value_record, kpi_def)` runs every APPLICABLE rule (sign/unit/subtotal/gaap — skipping N/A ones) and returns `{"eligible": bool, "failures": [{"rule","detail"}, ...]}` — eligible only when no applicable rule failed. Side-effect-free.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py,
  investing-toolkit/tests/analysis/test_kpi_validate.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Acceptance:
  - RED: ...::test_validate_aggregates_applicable_rules fails
  - GREEN: a value_record passing all applicable rules → eligible True, failures []; one with a negative value for a non-negative KPI → eligible False, failures names "sign"; an N/A rule (no segments) does not appear in failures.
- Dependencies: Tasks 1, 2, 3, 4 complete first
- Independent: false
- Brief item covered: Smallest End State #5 "Aggregate validate". Change-folder join: operational-kpi / Requirement "Rule-based validation of parsed values" / Scenario "Segment KPIs must sum to the reported total" (aggregate gate).

## Task 6 — kpi_validate CLI: validate, declared at the command surface
- Description: argparse CLI `validate` reads `{value_record, kpi_def}` JSON from stdin/--file, prints the verdict JSON; exit 0 on a valid verdict (INCLUDING eligible:false — a validly-rejected value is not a CLI error), exit 2 on malformed/non-object JSON. Document in analysis-kpi/SKILL.md `## CLI (kpi_validate)`.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/tests/analysis/test_kpi_validate.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
  - investing-toolkit/skills/analysis-kpi/SKILL.md
- Acceptance:
  - RED: ...::test_cli_validate_roundtrip fails
  - GREEN: `validate` a passing record → exit 0, stdout verdict eligible True; a failing record → exit 0, eligible False; malformed JSON → exit 2, no traceback; subcommand listed by `--help` AND documented in SKILL.md `## CLI (kpi_validate)`.
- Command surface: the validate verb declared in analysis-kpi/SKILL.md `## CLI (kpi_validate)`.
- Dependencies: Tasks 1, 2, 3, 4, 5 complete first
- Independent: false
- Brief item covered: Smallest End State #6 "a thin CLI".
