# Test Plan Writing Protocol

Write implementation-ready test plans (TEST-PLAN.md).
Use TECH-SPEC.md and PRODUCT-SPEC.md as primary inputs when available.
A good test plan lets a developer (or code-team agent) write test code
by reading only this document.

**Structure reference**: `standards/iso-29119-structure.md` (29119-3 Annex A as checklist)
**Vocabulary reference**: `standards/istqb-vocabulary.md` (ISTQB CTFL v4.0)
**Risk reference**: `standards/risk-assessment.md` (Likelihood × Impact)

## Phase 1: Scope Analysis

Aligns with 29119-3 §1 (Scope) and §3 (Test items).

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
5. List test items: components, modules, features with versions

## Phase 2: Test Level & Type Selection

Aligns with 29119-3 §5 (Test strategy / approach). Uses ISTQB CTFL v4.0 two-axis taxonomy.

1. **Pick test levels** (see `standards/istqb-vocabulary.md` §Test Levels):
   - **Component** — isolated unit logic
   - **Integration** — interface/interaction between components
   - **System** — integrated product as a whole
   - **Acceptance** — user needs, business processes
2. **Pick test types** (see `standards/istqb-vocabulary.md` §Test Types):
   - **Functional** — what the system does
   - **Non-functional** — how well (performance, usability, reliability — see
     `standards/quality-philosophy.md` for SLI/SLO/RED/USE frameworks)
   - **Structural** — internal structure (white-box coverage)
   - **Change-related** — confirmation and regression
3. **Select strategy framework** per `protocols/test-strategy-selection.md`
   (Practical Test Pyramid / Testing Trophy / Sizes). Document the choice
   and rationale in TEST-PLAN.md §Strategy.
4. Justify each level/type selection with a specific risk it addresses
   (not "because best practice").

## Phase 2b: Viewpoint Extraction (optional but recommended)

For non-trivial systems or Japanese-context projects, invoke
`protocols/test-viewpoint-extraction.md` as a sub-protocol **before** Phase 3.
The output (a structured viewpoint list with V-NN IDs) feeds Phase 3 test
case design — each test case will cite one or more viewpoints.

Skip this phase only for single-component bug fixes or when a viewpoint
list already exists and is still current.

## Phase 3: Test Case Design

Aligns with 29119-3 Dynamic tier (Test Case Specification).

For each test case:

1. **ID**: Unique identifier (TC-{area}-{number})
2. **Scenario**: Scenario-based description (see `standards/istqb-vocabulary.md`
   §Test Case Naming Convention — "{context} {action} {expected outcome}")
3. **Preconditions**: Required state before test execution
4. **Steps**: Ordered actions to perform
5. **Expected Result**: Observable outcome
6. **Pass/Fail Criteria**: Explicit binary condition — must be binary,
   measurable, and specific (see `standards/istqb-vocabulary.md` §Pass/Fail)
7. **Test Level**: Component / Integration / System / Acceptance
8. **Test Type**: Functional / Non-functional / Structural / Change-related
9. **Design Technique**: Which ISTQB technique derived this case —
   Equivalence Partitioning (EP), Boundary Value Analysis (BVA),
   Decision Table, State Transition, Use Case, or Experience-based
   (see `standards/istqb-vocabulary.md` §Design Techniques)
10. **Viewpoint Ref**: One or more V-NN IDs from Phase 2b (if performed)
11. **Risk Level**: From Phase 5 prioritization

Group test cases by feature area, not by test level or type.

## Phase 4: Environment Requirements

Aligns with 29119-3 §9 (Test environment and data).

1. List required test environments (local, staging, production-like)
2. Document test data requirements (seed data, fixtures, generators)
3. Specify external service dependencies (real vs mock vs stub)
4. Note infrastructure prerequisites (databases, queues, caches)
5. For non-functional tests, specify observability requirements
   (SLI instrumentation, RED metrics, USE metrics per
   `standards/quality-philosophy.md`)

## Phase 5: Risk-Based Prioritization

Aligns with 29119-3 §4 (Risk register). Uses ISTQB L×I per
`standards/risk-assessment.md`.

1. Build the risk register using **Risk Level = Likelihood × Impact**:
   ```
   | R-ID | Description | L | I | Level | Mitigation (test case) |
   |------|-------------|---|---|-------|------------------------|
   ```
2. Map each risk to one or more test case IDs
3. Critical and High risks **must** have at least one test case;
   Medium risks **should**; Low risks **may**
4. Mark the minimum viable test set (what MUST pass before release)
5. For safety-critical systems, consult `standards/risk-assessment.md`
   §FMEA for optional RPN upgrade

## Phase 6: Traceability

Aligns with 29119-3 §7 (Exit criteria) and Dynamic tier traceability.

1. Map each test case back to a spec requirement (TECH-SPEC or PRODUCT-SPEC section)
2. Identify spec requirements with no test coverage — flag as gaps
3. Document the traceability matrix (requirement → test case ID)
4. If Phase 2b was performed, also trace viewpoints (V-NN) to test case IDs

## Rules

- Self-contained: reading TEST-PLAN.md alone must be enough to write tests
- Every test case has explicit binary pass/fail criteria — no subjective
  judgments like "works correctly"
- Every test case cites at least one ISTQB design technique
- Scenario-based naming per `standards/istqb-vocabulary.md`
- Risk levels use ISTQB L×I, not self-invented H/M/L
- Do not design tests for hypothetical future requirements
- Keep structure flat — avoid deeply nested sections
- Cite primary sources: ISTQB syllabus, ISO 29119-3, strategy framework origin

## Output Structure (aligned to ISO/IEC/IEEE 29119-3 Annex A)

```
1. Scope (§1)
2. References (§2) — TECH-SPEC, PRODUCT-SPEC, standards
3. Test items (§3)
4. Risk register (§4) — L×I format
5. Test strategy / approach (§5) — levels, types, strategy framework
6. Entry criteria (§6)
7. Exit criteria (§7)
8. Suspension / resumption criteria (§8)
9. Test environment and data (§9)
10. Test deliverables (§10)
11. Schedule (§11)
12. Roles and responsibilities (§12)

Appendices:
- Test cases (grouped by feature area)
- Traceability matrix
- Viewpoint list (if Phase 2b performed)
- Minimum viable test set
```

Sections may be omitted with explicit rationale — consult
`standards/iso-29119-structure.md` §Minimum Viable Test Plan.
