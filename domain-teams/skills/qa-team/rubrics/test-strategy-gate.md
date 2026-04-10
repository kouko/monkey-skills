# Test Strategy Quality Gate

## Scope Boundary

Review the _strategy_ of the test plan, not individual test case details.
Do NOT review test code, implementation, or security -- those belong to
code-team gates.

## Flag Definitions

### Test Type Coverage
- Red **Fatal**: Only one test type used for a multi-service or multi-layer system
- Yellow **Warning**: Missing one relevant test type that the system architecture warrants
- Green **Clear**: All relevant test types covered with justification for inclusion/exclusion

### Boundary Design
- Red **Fatal**: Integration tests rely entirely on mocks with no plan for real-service testing
- Yellow **Warning**: Unclear separation between unit and integration test scope
- Green **Clear**: Clear boundaries between test types with justification for mock vs real decisions

### Regression Strategy
- Red **Fatal**: No regression approach defined for a system with existing functionality
- Yellow **Warning**: Generic "re-run all tests" without targeting change-affected areas
- Green **Clear**: Targeted regression strategy tied to change scope with explicit selection criteria

### Realism
- Red **Fatal**: Test plan requires infrastructure or environments that do not exist and have no provisioning plan
- Yellow **Warning**: Some environment gaps acknowledged but unresolved
- Green **Clear**: Environment plan is executable with current or planned infrastructure

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 Red fatal flag
2. **NEEDS_REVISION**: 2 or more Yellow warning flags
3. **PASS_WITH_NOTES**: Exactly 1 Yellow warning flag, no Red
4. **PASS**: All Green clear

## Rules

- If the strategy covers the system's risk areas and the cost of being wrong is low, PASS. Don't be a gatekeeper for the sake of gatekeeping.
- When issuing NEEDS_REVISION, you MUST include an "Alternatives Considered" section with at least one concrete alternative strategy and its trade-offs.
- Evaluate against actual system complexity, not hypothetical larger scope.

## Output Format

1. **Flags**: List each triggered flag with `[Red Dimension]` or `[Yellow Dimension]`
2. **Evidence**: Specific strategic problem with rationale
3. **Alternatives Considered** (NEEDS_REVISION only): Concrete alternatives with trade-offs
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues will be auto-revised without human review.
Be specific about what to restructure and how.
