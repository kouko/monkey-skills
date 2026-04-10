# Coverage Gap Audit Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's output.
You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below -- use the type specified.

## Checklist

Vocabulary reference: `standards/istqb-vocabulary.md` §Design Techniques.

- [ ] **CHK-COV-001 (Requirement Mapping)** [FIXABLE]: Every requirement from
  the spec has at least one mapped test. Unmapped requirements are explicitly
  flagged as gaps with ISTQB Risk = L×I classification per
  `standards/risk-assessment.md`.
- [ ] **CHK-COV-002 (Error Path Coverage)** [FIXABLE]: Error and exception paths
  are identified and have dedicated test cases or are explicitly flagged as
  gaps. Not just happy-path coverage.
- [ ] **CHK-COV-003 (EP + BVA Applied)** [FIXABLE]: For input-validation logic,
  **Equivalence Partitioning** (ISTQB CTFL v4.0 §4.2.1) and
  **Boundary Value Analysis** (§4.2.2) are applied. Empty inputs, min/max
  boundaries, and off-by-one scenarios have dedicated test cases. Absence
  without rationale is a gap.
- [ ] **CHK-COV-004 (Design Technique Diversity)** [FIXABLE]: The gap report
  identifies at least one area where **Decision Table** (§4.2.3) or
  **State Transition Testing** (§4.2.4) would add value — typically
  rule-heavy business logic or stateful workflows. If no such area exists,
  this must be stated explicitly.

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
      "id": "CHK-COV-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific reference to coverage report content or finding",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```
