# Plan: operational-kpi slice 5 — reliability gate + ground-truth label set

Source brief: docs/loom/specs/2026-07-14-operational-kpi-reliability-gate.md
Total tasks: 4
Critical-path depth: 4 (≤5)   ← T1 → T2 → T3 → T4
Execution order: sequential (all tasks touch one module kpi_gate.py + one test file)
Plan-document-reviewer verdict: PASS (2026-07-14; 13/13 applicable checks, no defects)

Change-folder binding: realizes a SUBSET of operational-kpi/spec.md (Requirements
"Ground-truth label set is a first-class object", "Reliability-gate evaluation against a
held-out labeled set", "Reliability-gate withhold-below-bar", "Reliability threshold
calibration [deferred]", "Recast series is itself gated"). Not archived (multi-slice).

Notes:
- kpi_gate.py is a DURABLE-STORE module reusing `_store_fs` (dir/lock/atomic-write) by
  same-skill import, exactly like kpi_schema — NOT a new fs impl, NOT cache_util.
- FAIL-CLOSED is the posture: a never-evaluated / below-bar / too-few-samples company is
  never TRUSTED. A WITHHELD/NOT_EVALUATED verdict is a NORMAL result, not an exception;
  only malformed input is loud. `evaluated_at` is caller-supplied (NO wall-clock).
- All tasks share kpi_gate.py + test_kpi_gate.py → Independent:false, sequential.

## Task 1 — kpi_gate scaffold + ground-truth label-set store (add_labels / get_labels)
- Description: Create `scripts/kpi_gate.py` (PEP-723, same-dir import shim → `import
  _store_fs`). `add_labels(company, labels)` appends human-labeled `{kpi_id, period,
  value}` entries to a per-company label-set file (durable, lock-guarded RMW, versioned
  envelope, append-only); `get_labels(company)` reads them ([] if none). Register
  KPI_GATE_SCRIPT in conftest.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py,
  investing-toolkit/tests/analysis/test_kpi_gate.py,
  investing-toolkit/tests/analysis/conftest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/_store_fs.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_gate.py::test_add_labels_persists_and_reads_back fails
  - GREEN: add_labels(company, [labels]) then get_labels(company) round-trips the labels; the RMW is lock-guarded (reuse _store_fs); KPI_STORE_DIR redirects to tmp.
- External surfaces: stdlib + same-skill _store_fs import; no third-party/cache_util.
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State #1 "Ground-truth label set". Change-folder join:
  operational-kpi / Requirement "Ground-truth label set is a first-class object" /
  Scenario "Gate cannot evaluate without a label set".

## Task 2 — evaluate: cell-level accuracy + gate record + TRUSTED/WITHHELD/NOT_EVALUATED verdict
- Description: `evaluate(company, schema_version, extracted_values, threshold=None,
  min_samples=<default>, evaluated_at=None)`: match each label (kpi_id, period) to the
  corresponding extracted value, compute cell-level accuracy = correct / total labeled;
  persist a gate record `{company, schema_version, metric, sample_size, verdict,
  evaluated_at}` (lock-guarded, keyed by company+schema_version). Verdict:
  NOT_EVALUATED if no labels OR sample_size < min_samples; TRUSTED if sample_size ≥ min
  AND accuracy ≥ threshold (INCLUSIVE); WITHHELD if sample_size ≥ min AND accuracy <
  threshold. If threshold is None (unset), fail-closed: never TRUSTED (→ NOT_EVALUATED
  or WITHHELD per the spec's deferred-calibration default).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py,
  investing-toolkit/tests/analysis/test_kpi_gate.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
- Acceptance:
  - RED: ...::test_evaluate_verdict_by_accuracy_and_samples fails
  - GREEN: with a label set of ≥min cells, all-correct extracted + threshold 0.95 →
    TRUSTED; accuracy exactly == threshold → TRUSTED (inclusive); accuracy < threshold →
    WITHHELD; a sub-min-samples label set → NOT_EVALUATED (not a verdict); threshold
    None → never TRUSTED.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #2/#3/#5 "Gate evaluation + threshold +
  recast (version-scoped)". Change-folder join: operational-kpi / Requirement
  "Reliability-gate evaluation against a held-out labeled set" / Scenarios "Pilot ticker
  gets an initial gate evaluation", "At-threshold accuracy is trusted (inclusive)",
  "Minimum sample size guards the verdict".

## Task 3 — fail-closed gate_verdict / is_trusted (default WITHHELD, never trusted-by-omission)
- Description: `gate_verdict(company, schema_version)` → the recorded verdict, defaulting
  **WITHHELD** when no gate record exists (a never-evaluated company is fail-closed);
  `is_trusted(company, schema_version)` → True ONLY when the recorded verdict is TRUSTED
  (WITHHELD/NOT_EVALUATED/absent → False).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py,
  investing-toolkit/tests/analysis/test_kpi_gate.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
- Acceptance:
  - RED: ...::test_unevaluated_company_is_fail_closed fails
  - GREEN: a never-evaluated (company, version) → gate_verdict WITHHELD, is_trusted
    False; after a TRUSTED evaluate → is_trusted True; after a WITHHELD evaluate →
    is_trusted False.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: Smallest End State #4 "Fail-closed trust query". Change-folder
  join: operational-kpi / Requirement "Reliability-gate withhold-below-bar" / Scenario
  "Unevaluated company is fail-closed".

## Task 4 — kpi_gate CLI: add-labels / evaluate / verdict, declared at the command surface
- Description: argparse CLI: `add-labels` (--company + labels JSON stdin/--file),
  `evaluate` (--company --schema-version [--threshold --min-samples --at] + extracted
  values JSON stdin/--file → prints the gate record), `verdict` (--company
  --schema-version → prints {verdict, trusted}). Fail-loud exit codes mirroring the
  sibling CLIs (0 ok / 1 ValueError / 2 malformed). Document in analysis-kpi/SKILL.md
  `## CLI (kpi_gate)`.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/tests/analysis/test_kpi_gate.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
  - investing-toolkit/skills/analysis-kpi/SKILL.md
- Acceptance:
  - RED: ...::test_cli_add_labels_evaluate_verdict_roundtrip fails
  - GREEN: `add-labels` a label set → `evaluate` with matching extracted values +
    --threshold 0.95 → gate record TRUSTED → `verdict` shows trusted True; a never-
    evaluated (company,version) `verdict` → WITHHELD/trusted False; malformed JSON →
    exit 2. Subcommands listed by `--help` AND documented in SKILL.md `## CLI (kpi_gate)`.
- Command surface: add-labels/evaluate/verdict verbs declared in analysis-kpi/SKILL.md `## CLI (kpi_gate)`.
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: Smallest End State #6 "a thin CLI".
