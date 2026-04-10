# Risk Register Depth Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the risk register
section of the TEST-PLAN.md under evaluation. This is a MAY gate — it only
runs when the user explicitly requests risk register review.

You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with
specific evidence. The failure type for each item is defined below — use
the type specified.

Risk vocabulary: `standards/risk-assessment.md` (ISTQB Risk Level = Likelihood × Impact).

## Checklist

- [ ] **CHK-RSK-001 (ISTQB L×I Notation)** [FIXABLE]: Each risk item uses ISTQB
  Likelihood × Impact notation (e.g., L/M/H per axis mapped to the matrix in
  `standards/risk-assessment.md` §Risk Level Matrix), NOT free-form prose
  descriptions of severity.

- [ ] **CHK-RSK-002 (Likelihood Evidence)** [FIXABLE]: Likelihood rating justification
  references concrete evidence — at least one of: code complexity metric,
  developer familiarity, technology novelty, defect history, dependency
  stability, or change scope. Vague "could happen" justifications fail.

- [ ] **CHK-RSK-003 (Impact Evidence)** [FIXABLE]: Impact rating justification
  references user or business consequence — at least one of: financial loss,
  reputational damage, safety/compliance violation, users affected count, or
  business criticality. Vague "bad outcome" justifications fail.

- [ ] **CHK-RSK-004 (Mitigation Traceability)** [FIXABLE]: Every risk with
  Level ≥ Medium has at least one mitigation linking to a test case ID
  (TC-XXX format). Risks without test case coverage must either be marked
  Low or have an explicit "accepted without test coverage" rationale.

## Verdict Rules

- Any **1 item** is `FAIL_FATAL` → final verdict is `NEEDS_REVISION` (escalate to user)
- Only `FAIL_FIXABLE` items (no FATALs) → final verdict is `PASS_WITH_NOTES` (trigger auto-revise)
- All items are `PASS` → final verdict is `PASS`

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "checklist_results": [
    {
      "id": "CHK-RSK-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific risk register entry or finding",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```
