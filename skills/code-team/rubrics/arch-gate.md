# Architecture Review Gate

## Scope Boundary

Review the _shape_ of the solution, not its implementation details.
Do NOT review code quality, bugs, or security — those belong to
quality-gate and the security checklist.

## Flag Definitions

### Approach Fitness
- 🔴 **Fatal**: Chosen approach is 3x+ more complex than an obviously simpler alternative that meets the same requirements
- 🔴 **Fatal**: Solution solves a hypothetical future problem, not the actual current requirement
- 🟡 **Warning**: Complexity is borderline justified — could go either way
- 🟢 **Clear**: Approach matches problem complexity; boring solution preferred

### Boundary Design
- 🔴 **Fatal**: Circular dependency between modules/services
- 🔴 **Fatal**: God object/module that absorbs responsibilities from 3+ distinct concerns
- 🟡 **Warning**: Dependencies point in the wrong direction (violates dependency inversion)
- 🟡 **Warning**: Over-abstraction — abstraction layer exists but has only one implementation with no foreseeable second
- 🟢 **Clear**: Boundaries are in the right places; coupling is appropriate

### Change Tolerance
- 🔴 **Fatal**: The most likely future change would require modifying 5+ files across 3+ modules
- 🟡 **Warning**: Extension points are missing where the domain is known to evolve
- 🟡 **Warning**: Extension points exist where the domain is stable (unnecessary flexibility)
- 🟢 **Clear**: Rigid where stable, flexible where it will evolve

### Ecosystem Fit
- 🟡 **Warning**: Deviates from project conventions without documented rationale
- 🟡 **Warning**: Other developers would need explanation to understand the design intent
- 🟢 **Clear**: Fits existing architecture; conventions followed

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Rules

- If the approach works and the cost of being wrong is low, PASS. Don't be a gatekeeper for the sake of gatekeeping.
- When issuing NEEDS_REVISION, you MUST include an "Alternatives Considered" section with at least one concrete alternative approach and its trade-offs.
- Evaluate against actual problem scope, not hypothetical larger scope.

## Output Format

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: Specific structural problem with rationale
3. **Alternatives Considered** (NEEDS_REVISION only): Concrete alternatives with trade-offs
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues will be auto-revised without human review.
Be specific about what to restructure and how.
