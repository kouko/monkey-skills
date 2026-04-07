# Technical Debt Checklist Gate

## Evaluation Instructions

You are a strict technical debt auditor. Check each item below against the target codebase or code artifact.
You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below — use the type specified.

## Checklist

- [ ] **CHK-DEBT-001 (Dead Code)** [FIXABLE]: No unreachable code, unused imports, unused variables, or unused functions. All exported symbols have at least one consumer.
- [ ] **CHK-DEBT-002 (Hardcoded Values)** [FIXABLE]: No hardcoded file paths, URLs, port numbers, or magic numbers that should be configuration. Environment-specific values are externalized.
- [ ] **CHK-DEBT-003 (Duplication)** [FIXABLE]: No copy-pasted logic blocks (3+ lines substantially identical). Repeated patterns are extracted into shared utilities or base classes.
- [ ] **CHK-DEBT-004 (Cyclomatic Complexity)** [FATAL]: No single function exceeds cyclomatic complexity of 15. Functions with deeply nested conditionals (>3 levels) are flagged.
- [ ] **CHK-DEBT-005 (Dependency Hygiene)** [FIXABLE]: No unused dependencies in manifest (package.json, requirements.txt, etc.). No pinned dependencies with known critical CVEs.
- [ ] **CHK-DEBT-006 (TODO/FIXME/HACK)** [FIXABLE]: All TODO/FIXME/HACK comments have an associated issue or ticket reference. No orphaned temporary workarounds.

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
      "id": "CHK-DEBT-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific code reference or finding",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```

Reference `standards/code-conventions.md` for naming and style rules.
