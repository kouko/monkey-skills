# QA Brainstorming Protocol

Understand testing intent, explore testing approaches, and confirm
direction before writing a test plan. Core principles: one question
at a time, propose 2-3 testing strategies, prioritize risk over
coverage percentage, AI proposes human decides.

## Protocol

### Phase 0: Context Discovery

1. **Clarify intent**: What are we testing, why now, and what does
   "well-tested" look like for this project? Ask one question at a
   time, prefer multiple choice when possible.
2. **Scan existing tests**: Explore current test suite -- framework,
   coverage, test types in use, CI integration. Do not propose
   strategies before understanding what exists.
3. **Read specs**: Find PRODUCT-SPEC.md, TECH-SPEC.md, or equivalent
   documentation. Identify critical user paths and system boundaries.
4. **Identify constraints**: Test infrastructure (CI/CD, test
   environments, data availability), time budget, team testing
   experience, and hard boundaries.

### Phase 1: Approach Exploration

5. **Identify test types needed**: For the system under test, which
   types are most valuable?
   - E2E (user journey validation)
   - Integration (service boundary verification)
   - Performance (latency, throughput, resource usage)
   - Regression (change impact verification)
   - Smoke (deployment sanity)
6. **Generate 2-3 strategies**: Propose with trade-offs. Each strategy
   should vary in coverage depth, infrastructure cost, and
   maintenance burden.
7. **Risk-based prioritization**: Rank test areas by failure impact
   (what breaks costs the most?) rather than code coverage percentage.

### Phase 2: Direction Confirmation

8. **Recommend**: Present your recommended strategy with reasoning.
9. **User selects**: AI presents options, human makes final call.
   Provide enough information for an informed decision.
10. **Scope boundary**: State explicitly what is IN scope and what
    is OUT of scope for testing. Out-of-scope items may be logged
    as future tasks.
11. **Handoff summary**: Structure the selected strategy as input
    for the test plan writing phase (Intent, Constraints, Test Types,
    Scope, Priority Areas).

## Rules

- One question at a time, multiple choice preferred
- Do not propose strategies before exploring existing tests --
  complete Phase 0 before Phase 1
- Prioritize by risk impact, not code coverage percentage
- AI presents options and recommendations; human decides
- Skip this protocol for simple, single-component test plans
- Early questions are cheaper than late rework -- resolve ambiguity
  before moving forward

## Output Format

1. **Intent Summary**: What we are testing and why
2. **Current State**: Existing tests, infra, gaps
3. **Strategy Comparison**: 2-3 strategies with trade-off table
4. **Selected Direction**: Chosen strategy with scope boundary
5. **Plan Handoff**: Structured input for `protocols/test-plan-writing.md`
   (Intent, Constraints, Test Types, Scope, Priority Areas)
