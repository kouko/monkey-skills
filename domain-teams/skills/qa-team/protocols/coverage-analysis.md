# Coverage Analysis Protocol

Analyze test coverage gaps by mapping existing tests to requirements
and identifying critical paths without verification. Produces a
prioritized gap report with actionable recommendations.

## Phase 1: Map Existing Tests

1. Inventory all existing tests by type (unit, integration, E2E,
   performance, smoke)
2. For each test, identify what requirement or behavior it verifies
3. Build a mapping: requirement/feature -> existing test(s)
4. Note tests that do not trace to any known requirement (orphaned tests)

## Phase 2: Identify Uncovered Paths

1. List all requirements from TECH-SPEC.md, PRODUCT-SPEC.md, or
   equivalent documentation
2. Cross-reference against the test mapping from Phase 1
3. Flag requirements with zero test coverage
4. For covered requirements, assess depth:
   - Happy path only (shallow)
   - Happy path + key error paths (moderate)
   - Happy path + error paths + edge cases (thorough)

## Phase 3: Classify Risk

For each uncovered or shallowly-covered area:
1. Assign risk level using standard definitions:
   - **High**: Failure causes data loss, security breach, or revenue impact
   - **Medium**: Failure degrades user experience or breaks secondary features
   - **Low**: Failure is cosmetic or affects internal tooling only
2. Consider: frequency of use, blast radius, data sensitivity,
   external visibility
3. Rank gaps by risk level (High first)

## Phase 4: Produce Gap Report

1. **Coverage summary**: Total requirements, covered count, gap count,
   coverage percentage by area
2. **Gap list**: Each gap with requirement reference, risk level,
   and current coverage depth
3. **Prioritized recommendations**: What to test next, ordered by
   risk impact (not by ease of implementation)
4. **Quick wins**: Gaps that can be closed with minimal effort
   (existing test infrastructure supports them)

## Rules

- Map to requirements, not to code lines -- coverage percentage
  alone does not indicate quality
- Risk classification must include justification, not just a label
- Recommendations must be actionable (specific enough for code-team
  to write tests from)
- Do not recommend tests for hypothetical future features
- Flag orphaned tests as maintenance candidates

## Output Format

1. **Coverage Summary Table**: Area | Requirements | Covered | Gaps | Depth
2. **Gap Details**: Per-gap entries with risk, requirement ref, recommendation
3. **Priority Queue**: Ordered list of gaps to close next
4. **Quick Wins**: Low-effort high-impact gaps
5. **Orphaned Tests**: Tests without requirement traceability
