# Security & Safety Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's output.
You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below — use the type specified.

## Checklist

- [ ] **CHK-SEC-001 (Secrets)** [FATAL]: No hardcoded passwords, API keys, tokens, or secrets. All sensitive values read from environment variables or secret managers.
- [ ] **CHK-SEC-002 (Input Sanitization)** [FATAL]: All user-facing inputs have validation and sanitization. No raw user input passed to SQL queries, shell commands, or HTML rendering.
- [ ] **CHK-SEC-003 (Error Exposure)** [FIXABLE]: Error handlers do NOT leak stack traces, internal paths, or system details to external responses.
- [ ] **CHK-SEC-004 (Injection Risk)** [FATAL]: No obvious SQL injection, XSS, command injection, or path traversal vulnerabilities.

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
      "id": "CHK-SEC-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific code reference or finding",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```
