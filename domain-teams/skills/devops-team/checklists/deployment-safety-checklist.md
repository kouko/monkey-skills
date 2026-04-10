# Deployment Safety Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's output.
You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below -- use the type specified.

Derived from Google SRE Book §5 (Eliminating Toil) and Humble & Farley,
*Continuous Delivery* §10 (Deploying and Releasing). See
`standards/sre-practices.md` and `standards/continuous-delivery.md`.

## Checklist

- [ ] **CHK-DEP-001 (Rollback Plan)** [FATAL]: Every deployment has a documented rollback procedure executable without manual intervention. Rollback steps must be concrete (revert image tag, restore config), not vague ("roll back if needed").
- [ ] **CHK-DEP-002 (Secrets Exposure)** [FATAL]: No secrets hardcoded in pipeline configs, Dockerfiles, or IaC definitions. All sensitive values reference a secret manager or environment variable injection (per 12-Factor III). No secrets appear in build logs or artifact metadata.
- [ ] **CHK-DEP-003 (Health Check)** [FATAL]: Deployment includes a health check or readiness probe. Pipeline verifies health status before marking deployment as successful. Health check endpoint must be distinct from application endpoints.
- [ ] **CHK-DEP-004 (Environment Isolation)** [FIXABLE]: Staging and production environments are isolated. No shared credentials, databases, or API endpoints between environments. Environment-specific config is injected, not baked into artifacts (per 12-Factor X Dev/prod parity).
- [ ] **CHK-DEP-005 (Idempotency)** [FIXABLE]: Pipeline and IaC definitions are re-runnable without side effects. Running the same deployment twice produces the same result. No manual state cleanup required between runs.
- [ ] **CHK-DEP-006 (Pipeline Gating)** [FIXABLE]: Every commit reaching the production branch has passed through the full deployment pipeline (lint → test → build → scan → staging deploy → verify → production). No manual bypass paths exist. Aligns with Humble & Farley "every green build is releasable" principle.

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
      "id": "CHK-DEP-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific config reference or finding",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```
