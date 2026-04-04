# OSS Due Diligence Checklist Gate

## Evaluation Instructions

You are a strict open-source compliance auditor. Check each item below against the technology evaluation output.
You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below — use the type specified.

## Checklist

- [ ] **CHK-OSS-001 (License Compliance)** [FATAL]: The dependency's license is explicitly identified (SPDX). License is compatible with the project's license and use case. No GPL/AGPL in proprietary-distributed projects unless confirmed acceptable.
- [ ] **CHK-OSS-002 (Known Vulnerabilities)** [FATAL]: No unpatched critical or high-severity CVEs in the evaluated version. Security advisory history has been checked (GitHub Advisories, NVD, Snyk).
- [ ] **CHK-OSS-003 (Maintenance Status)** [FIXABLE]: The project has had at least one commit in the last 12 months. There is at least one active maintainer responding to issues. No "archived" or "unmaintained" status.
- [ ] **CHK-OSS-004 (Test Coverage)** [FIXABLE]: The project has a visible CI pipeline. Test suite exists and passes on the default branch. No obvious gaps in critical path testing.
- [ ] **CHK-OSS-005 (Documentation)** [FIXABLE]: API documentation exists and covers primary use cases. Migration/upgrade guides are available for major version bumps. README includes installation, usage, and configuration.
- [ ] **CHK-OSS-006 (Supply Chain)** [FATAL]: No known supply chain compromises (typosquatting, malicious releases). Package name matches the official repository. Published artifacts are traceable to source.

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
      "id": "CHK-OSS-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific finding with source link",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```

Reference `standards/oss-safety.md` for license and production-readiness rules.
Reference `standards/citation-standards.md` for source verification rules.
