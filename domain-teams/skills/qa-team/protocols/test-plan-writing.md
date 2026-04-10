# Test Plan Writing Protocol

Write implementation-ready test plans (TEST-PLAN.md).
Use TECH-SPEC.md and PRODUCT-SPEC.md as primary inputs when available.
A good test plan lets a developer (or code-team agent) write test code
by reading only this document.

## Phase 1: Scope Analysis

1. Identify the system under test (SUT) and its boundaries
2. Read TECH-SPEC.md and/or PRODUCT-SPEC.md to extract:
   - Critical user paths (money, auth, data mutation)
   - System integration points
   - Performance-sensitive operations
   - Known edge cases and error scenarios
3. Define test scope:
   - IN scope: what this plan covers
   - OUT of scope: what it explicitly excludes (with rationale)
4. Document assumptions about test environment and data

## Phase 2: Test Type Selection

1. For each area of the SUT, select the most valuable test type(s):
   - **E2E**: User journey from entry to outcome
   - **Integration**: Service/module boundary verification
   - **Performance**: Latency, throughput, resource limits
   - **Regression**: Change impact verification
   - **Smoke**: Deployment sanity check
2. Justify why each type was selected (not "because best practice"
   but because a specific risk exists)
3. Document what each test type will and will NOT cover

## Phase 3: Test Case Design

For each test case:
1. **ID**: Unique identifier (TC-{area}-{number})
2. **Scenario**: What situation is being tested (scenario-based, not
   method-based -- see `standards/test-conventions.md`)
3. **Preconditions**: Required state before test execution
4. **Steps**: Ordered actions to perform
5. **Expected Result**: Observable outcome
6. **Pass/Fail Criteria**: Explicit binary condition (measurable,
   not subjective)
7. **Test Type**: Which type this case belongs to
8. **Risk Level**: High / Medium / Low (see `standards/test-conventions.md`)

Group test cases by feature area, not by test type.

## Phase 4: Environment Requirements

1. List required test environments (local, staging, production-like)
2. Document test data requirements (seed data, fixtures, generators)
3. Specify external service dependencies (real vs mock vs stub)
4. Note infrastructure prerequisites (databases, queues, caches)

## Phase 5: Risk-Based Prioritization

1. Assign risk level to each test area:
   - **High**: Failure causes data loss, security breach, or revenue impact
   - **Medium**: Failure degrades user experience or breaks secondary features
   - **Low**: Failure is cosmetic or affects internal tooling only
2. Order test execution: High risk first, then Medium, then Low
3. Mark minimum viable test set (what MUST pass before release)

## Phase 6: Traceability

1. Map each test case back to a spec requirement (TECH-SPEC or
   PRODUCT-SPEC section)
2. Identify spec requirements with no test coverage -- flag as gaps
3. Document the traceability matrix (requirement -> test case ID)

## Rules

- Self-contained: reading TEST-PLAN.md alone must be enough to write tests
- Every test case has explicit binary pass/fail criteria -- no subjective
  judgments like "works correctly"
- Scenario-based naming: describe the situation, not the method under test
- Risk justification required: "High" must state what breaks and the impact
- Do not design tests for hypothetical future requirements
- Keep structure flat -- avoid deeply nested sections

## Output Structure

Adapt to the project. Typical TEST-PLAN.md structure:

1. Overview (SUT, scope, assumptions)
2. Test Strategy (selected types with justification)
3. Test Cases (grouped by feature area)
4. Environment Requirements
5. Risk Matrix (prioritized test areas)
6. Traceability Matrix (requirement -> test case mapping)
7. Minimum Viable Test Set (must-pass before release)
