# Test Plan Completeness Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's output.
You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below -- use the type specified.

Checklist items are aligned to ISO/IEC/IEEE 29119-3:2021 Annex A sections
(see `standards/iso-29119-structure.md`) and ISTQB CTFL v4.0 vocabulary
(see `standards/istqb-vocabulary.md`).

## Checklist

- [ ] **CHK-TP-001 (Test Items Identified)** [FATAL]: Test items (components,
  modules, features) are explicitly listed with versions, aligning to
  29119-3 §3. Every critical user path (money, auth, data mutation) has
  at least one test case with explicit steps and expected results.
- [ ] **CHK-TP-002 (Pass/Fail Criteria)** [FATAL]: Each test case has explicit
  binary pass/fail criteria per `standards/istqb-vocabulary.md` §Pass/Fail.
  No subjective judgments like "works correctly" or "behaves as expected."
- [ ] **CHK-TP-003 (Test Environment)** [FIXABLE]: Test environment prerequisites
  are documented per 29119-3 §9 — required services, test data, infrastructure
  dependencies, and (for non-functional tests) observability instrumentation
  requirements per `standards/quality-philosophy.md` §SLI/SLO/RED/USE.
- [ ] **CHK-TP-004 (Risk Register using ISTQB L×I)** [FIXABLE]: Risks are
  expressed using the ISTQB Risk Level = Likelihood × Impact format per
  `standards/risk-assessment.md`. Each risk has justified Likelihood and
  Impact factors, and each risk ≥ Medium is mapped to at least one test
  case ID. This aligns with 29119-3 §4.
- [ ] **CHK-TP-005 (Traceability)** [FIXABLE]: Test cases trace back to spec
  requirements (TECH-SPEC.md or PRODUCT-SPEC.md sections). Requirements
  without test coverage are flagged as gaps.
- [ ] **CHK-TP-006 (Viewpoint Coverage Statement)** [FIXABLE]: The plan declares
  whether viewpoint extraction was performed (per `protocols/test-viewpoint-extraction.md`).
  If yes, the viewpoint list is included or linked and each non-trivial test
  case cites at least one V-NN ID. If no, explicit rationale is given
  (e.g., "single-component bug fix, viewpoint extraction not applicable").
- [ ] **CHK-TP-007 (Design Technique Documented)** [FIXABLE]: Each non-trivial
  test case cites at least one ISTQB design technique from
  `standards/istqb-vocabulary.md` §Design Techniques (Equivalence Partitioning,
  Boundary Value Analysis, Decision Table, State Transition, Use Case, or
  Experience-based). Cases with no technique stated are gaps.

## Verdict Rules

- Any **1 item** is `FAIL_FATAL` -> final verdict is `NEEDS_REVISION` (escalate to user)
- Only `FAIL_FIXABLE` items (no FATALs) -> final verdict is `PASS_WITH_NOTES` (trigger auto-revise)
- All items are `PASS` -> final verdict is `PASS`

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "checklist_results": [
    {
      "id": "CHK-TP-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific reference to test plan content or finding",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```
