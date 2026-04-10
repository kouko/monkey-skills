# Test Plan Completeness Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's output.
You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below -- use the type specified.

## Checklist

- [ ] **CHK-TP-001 (Critical Path Coverage)** [FATAL]: Every critical user path (money, auth, data mutation) has at least one test case with explicit steps and expected results.
- [ ] **CHK-TP-002 (Pass/Fail Criteria)** [FATAL]: Each test case has explicit binary pass/fail criteria. No subjective judgments like "works correctly" or "behaves as expected."
- [ ] **CHK-TP-003 (Environment Requirements)** [FIXABLE]: Test environment prerequisites are documented, including required services, test data, and infrastructure dependencies.
- [ ] **CHK-TP-004 (Risk Prioritization)** [FIXABLE]: Test cases are prioritized by risk level (High/Medium/Low) with justification for each classification.
- [ ] **CHK-TP-005 (Traceability)** [FIXABLE]: Test cases trace back to spec requirements (TECH-SPEC.md or PRODUCT-SPEC.md sections). Requirements without test coverage are flagged.

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
