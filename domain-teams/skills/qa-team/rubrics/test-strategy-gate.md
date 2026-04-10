# Test Strategy Quality Gate

## Scope Boundary

Review the _strategy_ of the test plan, not individual test case details.
Do NOT review test code, implementation, or security -- those belong to
code-team gates.

## Flag Definitions

Vocabulary reference: `standards/istqb-vocabulary.md` (test levels and types).
Strategy framework reference: `protocols/test-strategy-selection.md`.

### Strategy Framework Citation
- 🔴 **Fatal**: No strategy framework cited — no Pyramid / Trophy / Sizes
  reasoning present. The plan proposes a distribution without grounding in
  any named framework.
- 🟡 **Warning**: Framework named but not justified for this project type
  (e.g., "Test Pyramid" stated for a frontend JavaScript app where Testing
  Trophy would be the conventional choice)
- 🟢 **Clear**: Framework explicitly cited with justification tied to project
  type — backend/systems → Practical Test Pyramid (Fowler/Vocke);
  frontend/JS → Testing Trophy (Dodds 2018); Google-scale monorepo →
  Small/Medium/Large Sizes

### Test Level & Type Coverage
- 🔴 **Fatal**: Only one ISTQB test type used for a multi-service or
  multi-layer system (e.g., all functional, no non-functional or change-related)
- 🟡 **Warning**: Missing one relevant test level or type that the system
  architecture warrants (e.g., no Component-level tests for a unit-testable
  library)
- 🟢 **Clear**: All relevant ISTQB levels (Component/Integration/System/Acceptance)
  and types (functional/non-functional/structural/change-related) covered
  with justification for inclusion or exclusion

### Boundary Design
- 🔴 **Fatal**: Integration tests rely entirely on mocks with no plan for
  real-service testing
- 🟡 **Warning**: Unclear separation between Component and Integration test
  scope
- 🟢 **Clear**: Clear boundaries between test levels with justification for
  mock vs real decisions

### Regression Strategy
- 🔴 **Fatal**: No regression approach defined for a system with existing
  functionality (change-related test type absent)
- 🟡 **Warning**: Generic "re-run all tests" without targeting change-affected
  areas
- 🟢 **Clear**: Targeted regression strategy tied to change scope with explicit
  selection criteria

### Realism
- 🔴 **Fatal**: Test plan requires infrastructure or environments that do not
  exist and have no provisioning plan
- 🟡 **Warning**: Some environment gaps acknowledged but unresolved
- 🟢 **Clear**: Environment plan is executable with current or planned
  infrastructure

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
