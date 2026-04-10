# IaC Quality Review Gate

## Scope Boundary

Review the _infrastructure design_ of the solution, not application logic.
Do NOT review application code, business logic, or security vulnerabilities
in application code -- those belong to code-team gates.

## Flag Definitions

### State Management
- :red_circle: **Fatal**: Local state only, no remote backend or locking mechanism. Multiple operators will corrupt state.
- :yellow_circle: **Warning**: Remote state backend configured but no state locking. Concurrent applies risk corruption.
- :green_circle: **Clear**: Remote state with locking and versioning. State is recoverable and concurrent-safe.

### Modularity
- :red_circle: **Fatal**: Monolithic IaC file exceeding 300 lines with no logical separation. All resources in one blast radius.
- :yellow_circle: **Warning**: Some logical grouping exists but modules are tightly coupled or share state directly.
- :green_circle: **Clear**: Modular design with reusable components, clear interfaces between modules, and independent apply scope.

### Drift Detection
- :red_circle: **Fatal**: No mechanism to detect or report configuration drift. Manual changes go unnoticed.
- :yellow_circle: **Warning**: Drift detection exists but requires manual execution (ad-hoc plan commands).
- :green_circle: **Clear**: Automated drift detection integrated into CI/CD pipeline. Drift alerts trigger reconciliation.

### Least Privilege
- :red_circle: **Fatal**: Wildcard permissions (e.g., `*:*`) or admin/root roles assigned to services or CI runners.
- :yellow_circle: **Warning**: Permissions are scoped to services but broader than necessary (e.g., full S3 access instead of single bucket).
- :green_circle: **Clear**: Minimal permissions per service and role. Permissions follow the principle of least privilege with documented justification.

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 :red_circle: fatal flag
2. **NEEDS_REVISION**: 2 or more :yellow_circle: warning flags
3. **PASS_WITH_NOTES**: Exactly 1 :yellow_circle: warning flag, no :red_circle:
4. **PASS**: All :green_circle: clear

## Rules

- If the infrastructure works and the cost of being wrong is low, PASS. Don't be a gatekeeper for the sake of gatekeeping.
- When issuing NEEDS_REVISION, you MUST include an "Alternatives Considered" section with at least one concrete alternative approach and its trade-offs.
- Evaluate against actual project scale, not hypothetical enterprise scale.

## Output Format

1. **Flags**: List each triggered flag with `[:red_circle: Dimension]` or `[:yellow_circle: Dimension]`
2. **Evidence**: Specific structural problem with rationale
3. **Alternatives Considered** (NEEDS_REVISION only): Concrete alternatives with trade-offs
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues will be auto-revised without human review.
Be specific about what to restructure and how.
