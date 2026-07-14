# Plan: operational-kpi slice 9 — deterministic cell parser + token taxonomy

Source brief: docs/loom/specs/2026-07-14-operational-kpi-cell-parser.md
Total tasks: 3
Critical-path depth: 3 (≤5)   ← T1 → T2 → T3
Execution order: sequential (all tasks touch one module kpi_parse.py + one test file)
Plan-document-reviewer verdict: PASS (2026-07-14; 14/14 applicable checks, no gaps)

Change-folder binding: realizes a SUBSET of operational-kpi/spec.md (Requirements
"Locate-then-parse parser-emits-number invariant", "Unparseable-cell token taxonomy is
defined"). Not archived (LLM/network layer still unshipped).

Notes:
- kpi_parse.py is PURE COMPUTE (stdlib only, no persistence/network/LLM; mirrors
  kpi_validate). The CORE property is FAIL-LOUD: an unparseable/missing token RAISES, never
  coerces to 0; a true 0 is a real value. The deterministic parser emits the number — the
  LLM (a later slice) only LOCATES the cell, never types the number.

## Task 1 — kpi_parse scaffold + parse_cell (numeric: currency/thousands/decimal/sign/parens/true-0)
- Description: Create `scripts/kpi_parse.py` (PEP-723, stdlib only). `parse_cell(cell_text)`
  → a `float` for a genuinely-numeric cell: strip a leading `$` + thousands `,`, handle a
  decimal point, a leading `+`/`-` sign, and the accounting parenthesized-negative convention
  (`(123)` / `(1,234)` → negative). A true `"0"`/`"0.0"` → `0.0`. Register KPI_PARSE_SCRIPT in
  conftest.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_parse.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_parse.py,
  investing-toolkit/tests/analysis/test_kpi_parse.py,
  investing-toolkit/tests/analysis/conftest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
  - docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_parse.py::test_parse_cell_numeric_forms fails
  - GREEN: `$1,234` → 1234.0; `1,234.56` → 1234.56; `1234` → 1234.0; `0` → 0.0; `(123)` →
    -123.0; `-45` → -45.0.
- External surfaces: stdlib only (re / decimal); no third-party.
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State #1 "Numeric parse". Change-folder join: operational-
  kpi / Requirement "Locate-then-parse parser-emits-number invariant" / Scenario "LLM output
  is a cell reference, not a number" (the deterministic parser emits the number).

## Task 2 — fail-loud unparseable-cell token taxonomy (never coerce a missing token to 0)
- Description: `parse_cell` RAISES loud (a distinct exception / ValueError naming the token)
  for the not-a-number tokens: `NM`, `n/a` / `N/A`, an em/en/figure dash or a bare hyphen used
  as "not applicable" (`—` / `–` / `-`), and blank / whitespace-only. These MUST NOT be
  coerced to `0` (a missing cell → a caller review-item, never a fabricated zero). A `0` /
  `0.0` still parses to `0.0` (a real value, NOT missing) — the true-zero-vs-blank distinction.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_parse.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_parse.py,
  investing-toolkit/tests/analysis/test_kpi_parse.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_parse.py
- Acceptance:
  - RED: ...::test_parse_cell_fails_loud_on_unparseable_tokens fails
  - GREEN: `parse_cell("NM")`, `("n/a")`, `("—")`, `("-")`, `("")`, `("   ")`, `("foo")` each
    RAISE (not return 0); AND `parse_cell("0")` still returns 0.0 (a true zero is NOT missing).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #2 "Unparseable-cell token taxonomy (fail loud)".
  Change-folder join: operational-kpi / Requirement "Unparseable-cell token taxonomy is
  defined" / Scenario "Currency/NM/dash/zero tokens are handled explicitly".

## Task 3 — kpi_parse CLI: parse
- Description: argparse CLI `parse` (--cell / stdin the cell text → print the parsed number,
  exit 0; an unparseable cell → the ValueError → exit 1 with a clean stderr, no traceback;
  malformed invocation → argparse exit 2). Document in analysis-kpi/SKILL.md `## CLI (kpi_parse)`.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_parse.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_parse.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/tests/analysis/test_kpi_parse.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_parse.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
  - investing-toolkit/skills/analysis-kpi/SKILL.md
- Acceptance:
  - RED: ...::test_cli_parse_roundtrip fails
  - GREEN: `parse` a numeric cell (stdin `$1,234`) → stdout 1234.0, exit 0; `parse` an
    unparseable cell (`NM`) → exit 1, clean stderr (no traceback); subcommand listed by
    `--help` AND documented in SKILL.md `## CLI (kpi_parse)`.
- Command surface: the parse verb declared in analysis-kpi/SKILL.md `## CLI (kpi_parse)`.
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: Smallest End State #3 "a thin CLI".
