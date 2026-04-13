# QA Brainstorming Protocol

Understand testing intent, explore testing approaches, and confirm
direction before writing a test plan. Core principles: one question
at a time, propose 2-3 testing strategies, prioritize risk over
coverage percentage, AI proposes human decides.

## Protocol

### Phase 0: Context Discovery & Shared Understanding

#### Step 1: Clarify intent

1. **Ask intent**: What are we testing, why now, and what does
   "well-tested" look like for this project? Ask one question at a
   time, prefer multiple choice when possible. Keep this brief
   (1-2 questions) to establish direction before exploring code.

#### Step 2: Explore codebase

2. **Scan existing tests**: Explore current test suite -- framework,
   coverage, test types in use, CI integration. Do not propose
   strategies before understanding what exists.
3. **Read specs**: Find PRODUCT-SPEC.md, TECH-SPEC.md, or equivalent
   documentation. Identify critical user paths and system boundaries.
4. **Identify constraints**: Test infrastructure (CI/CD, test
   environments, data availability), time budget, team testing
   experience, and hard boundaries.

#### Step 3: Grill — challenge assumptions

Using codebase and spec findings, question the user's testing intent
and assumptions to reach shared understanding. One question at a
time. For each question, provide your recommended answer.

5. **Challenge assumptions**: "You want E2E tests, but the existing
   suite already covers X — are you seeing gaps there, or is this
   about a different risk?" Surface contradictions between stated
   intent and existing test reality.
6. **Probe dependencies**: "Testing X requires a staging environment
   with Y — is that available?" Walk down each branch of the
   decision tree, resolving dependencies one by one.
7. **Test boundaries**: "What's acceptable test execution time?
   What's the failure tolerance for flaky tests?" Push on unstated
   requirements and implicit expectations.
8. **Explore the codebase** instead of asking, when a question can
   be answered by reading code or specs.

Continue until no unresolved branches remain, or the user requests
to move on. Do not set a fixed question limit.

#### Step 4: Understanding Summary

9. **Produce Understanding Summary** and ask user to confirm before
   proceeding to Phase 1:

```
## Understanding Summary

### Intent
[What we're testing and why]

### Key Constraints
[Infrastructure, time budget, team experience constraints]

### Confirmed Assumptions
[Assumptions validated during grill]

### Resolved Ambiguities
[Questions that were unclear but now resolved]
```

Skip Phase 0 Steps 3-4 for simple, single-component test plans
— proceed directly to Phase 1.

### Phase 1: Approach Exploration

5. **Identify test levels and types needed** (see `standards/istqb-vocabulary.md`):
   Pick from ISTQB's two orthogonal axes:
   - **Levels**: Component, Integration, System, Acceptance
   - **Types**: Functional, Non-functional, Structural, Change-related
   Concrete examples like "E2E", "smoke", and "performance" are instances:
   E2E is System/Acceptance + Functional; smoke is Acceptance + Functional
   (deployment sanity subset); performance is Non-functional (applicable at
   any level).
6. **Generate 2-3 strategies**: Propose with trade-offs. Each strategy
   should vary in coverage depth, infrastructure cost, and
   maintenance burden. Reference a framework from `protocols/test-strategy-selection.md`
   (Pyramid / Trophy / Sizes) to ground the discussion.
7. **Risk-based prioritization**: Rank test areas using **Risk = Likelihood × Impact**
   per ISTQB CTFL v4.0 §5.2 (see `standards/risk-assessment.md`). Do not rank
   by code coverage percentage.

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
- During grill (Step 3): provide your recommended answer with each
  question — don't just ask, also propose
- If a question can be answered by exploring the codebase or specs,
  explore instead of asking the user
- Understanding Summary must be confirmed by user before Phase 1
- Prioritize by risk impact, not code coverage percentage
- AI presents options and recommendations; human decides
- Skip Phase 0 grill (Steps 3-4) for simple, single-component
  test plans
- Early questions are cheaper than late rework -- resolve ambiguity
  before moving forward

## Output Format

1. **Intent Summary**: What we are testing and why
2. **Current State**: Existing tests, infra, gaps
3. **Strategy Comparison**: 2-3 strategies with trade-off table
4. **Selected Direction**: Chosen strategy with scope boundary
5. **Viewpoint Readiness Note**: Whether downstream should invoke
   `protocols/test-viewpoint-extraction.md` before test case writing
   (yes for non-trivial systems, no for single-component bug fixes)
6. **Plan Handoff**: Structured input for `protocols/test-plan-writing.md`
   (Intent, Constraints, Test Levels & Types, Scope, Priority Areas,
   Strategy Framework, Viewpoint Extraction Y/N)
