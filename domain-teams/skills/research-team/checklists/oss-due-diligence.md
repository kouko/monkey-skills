# OSS Due Diligence Checklist Gate

## Primary Sources

- `standards/oss-safety.md` — OpenSSF Scorecard 18 checks + NIST SSDF v1.1 practice groups + SLSA v1.1 build-integrity levels + CVSS v4.0 severity bands + SPDX v3.0 license identifiers
- `standards/citation-standards.md` — version number, CVE ID, and advisory URL citation rules

## Mode-Aware Triggering (v4.9.1)

This checklist is a **MAY gate** — user-requested only, never
auto-triggered. The mode interaction works as follows: the user
explicitly requests an OSS audit, and the worker then selects the
depth per the active mode (see SKILL.md §Research Modes).

- **Quick mode**: run a lightweight 3-check version — CHK-OSS-001
  (License Compliance), CHK-OSS-002 (Known Vulnerabilities), and
  CHK-OSS-006 (Supply Chain). These three are the load-bearing
  FATAL-class risks; the remaining FIXABLE items (maintenance,
  test coverage, documentation, SLSA) are deferred to deep mode.
  The worker performs this check as SELF attestation — no
  separate evaluator gate is dispatched.
- **Deep mode**: run all CHK-OSS-001 through CHK-OSS-007 items
  unchanged. The evaluator gate is dispatched per the usual
  SHOULD / MAY verdict rules in `gate-system.md`.

Per-mode threshold tuning (for example relaxing CHK-OSS-003
"maintenance status" for quick mode) is deferred to v4.9.2 if real
usage shows the binary split is too coarse.

See `standards/confidence-and-claim-language.md` §Cost-Aware
Early-Exit Rule for the mode-specific per-claim source thresholds
and the per-claim (not per-deliverable) policy.

## Evaluation Instructions

You are a strict open-source compliance auditor. Check each item below against the technology evaluation output.
You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below — use the type specified.

## Checklist

- [ ] **CHK-OSS-001 (License Compliance)** [FATAL]: The dependency's license is explicitly identified via SPDX v3.0 identifier per `standards/oss-safety.md` §SPDX v3.0 — License Identifiers and SBOM. License is compatible with the project's license and use case per §Acceptable Licenses. No GPL/AGPL in proprietary-distributed projects unless confirmed acceptable.
- [ ] **CHK-OSS-002 (Known Vulnerabilities)** [FATAL]: No unpatched Critical or High severity CVEs in the evaluated version. Severity is assessed via CVSS v4.0 bands per `standards/oss-safety.md` §CVSS v4.0 — 4 Metric Groups: Critical 9.0-10.0, High 7.0-8.9, Medium 4.0-6.9, Low 0.1-3.9. Security advisory history has been checked (GitHub Advisories, NVD, Snyk).
- [ ] **CHK-OSS-003 (Maintenance Status)** [FIXABLE]: The project has had at least one commit in the last 12 months. There is at least one active maintainer responding to issues. No "archived" or "unmaintained" status.
- [ ] **CHK-OSS-004 (Test Coverage)** [FIXABLE]: The project has a visible CI pipeline. Test suite exists and passes on the default branch. No obvious gaps in critical path testing.
- [ ] **CHK-OSS-005 (Documentation)** [FIXABLE]: API documentation exists and covers primary use cases. Migration/upgrade guides are available for major version bumps. README includes installation, usage, and configuration.
- [ ] **CHK-OSS-006 (Supply Chain)** [FATAL]: No known supply chain compromises (typosquatting, malicious releases). Package name matches the official repository. Published artifacts are traceable to source.
- [ ] **CHK-OSS-007 (SLSA Build Level)** [FIXABLE][MAY]: Optional MAY-tier check for security-critical adoption. The project's build process meets at least SLSA v1.1 Level 1 (documented build process, provenance generated) per `standards/oss-safety.md` §SLSA v1.1 — 4 Levels. SLSA L2+ (hosted build platform, authenticated provenance) is preferred for dependencies touching production auth, payments, or secrets handling.

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
