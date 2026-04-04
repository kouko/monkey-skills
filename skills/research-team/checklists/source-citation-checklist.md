# Source Citation Checklist Gate

## Evaluation Instructions

You are a strict fact-checker. Check each item below against the
research draft. You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE`
for each item, with specific evidence.
The failure type for each item is defined below — use the type specified.

## Checklist

- [ ] **CHK-SRC-001 (Citations)** [FATAL]: Every factual claim has an explicit, verifiable source citation. No unsourced assertions of fact.
- [ ] **CHK-SRC-002 (Data Freshness)** [FATAL]: All cited data is current. For fast-moving topics, sources older than 6 months are flagged with their date. No stale data presented as current.
- [ ] **CHK-SRC-003 (Confidence Levels)** [FIXABLE]: Key conclusions are tagged with confidence level (高/中/低). No unqualified certainty on contested claims.
- [ ] **CHK-SRC-004 (Fact vs Opinion)** [FIXABLE]: The text clearly distinguishes facts (cited) from analysis (reasoned) from speculation (hedged). No opinion masquerading as fact.

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
      "id": "CHK-SRC-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific uncited claim or verification",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```

Reference `standards/citation-standards.md` for the full citation rules.
