# Product Spec Writing Protocol

Write cross-domain product specs (PRODUCT-SPEC.md / 企画書).
A good product spec lets any team (code, design, research) understand
what to build, why, and the boundaries.

## Phase 1: Vision & Opportunity

1. Clarify the core problem or opportunity
2. Identify target users (who benefits, who decides, who pays)
3. Define the user's Job-to-be-Done:
   "When [situation], I want to [motivation], so I can [outcome]."
   This frames the product around user need, not feature list.
4. Define success criteria (measurable outcomes, not features)
5. Assess market context (existing solutions, gaps, timing)
   - If competitors exist, use 3C analysis (see `standards/planning-frameworks.md`)
   - If market data needed, request user to invoke `research-team`

## Phase 2: Concept Definition

1. Value proposition (one sentence: what + for whom + why better)
2. Core user scenarios (2-3 primary use cases, narrative form)
3. Key differentiators (what makes this different from alternatives)
4. Design principles (3-5 guiding principles for all decisions)

## Phase 3: Scope & Boundaries

1. Goals (what the product WILL do in this version)
2. Non-Goals (what it explicitly WON'T do — equally important)
3. Assumption mapping: identify top 3 riskiest assumptions
   - Categorize: Desirability / Feasibility / Viability / Usability
   - Mark as [ASSUMPTION] in the spec with validation approach
   - See `standards/planning-frameworks.md` for the full process
4. MVP definition (minimum set to validate the riskiest assumptions)
5. Future phases (logged for reference, not committed)

## Phase 4: Direction Setting

1. UX direction:
   - Core user flow (entry → primary task → outcome)
   - Interaction model (CLI / GUI / API / conversational)
   - Key design constraints (platform, accessibility, performance)

2. Technical direction:
   - Architecture approach with rationale
   - Key technical constraints (language, platform, deployment)
   - Technical risks and mitigation strategies
   - External dependencies (APIs, models, services)

3. Business direction (if applicable):
   - Revenue model / monetization
   - Distribution strategy
   - Regulatory / compliance constraints

## Phase 5: Handoff Preparation

1. Identify downstream work:
   - What needs TECH-SPEC.md (code-team)?
   - What needs UI/UX design (design-team)?
   - What needs deeper research (research-team)?
2. List open questions that downstream teams must resolve
3. Define handoff format: PRODUCT-SPEC.md sections map to team assignments

## Rules

- Cross-domain: cover business + design + engineering, not just one
- Decision rationale required: every "we chose X" needs "because Y"
- Non-Goals are mandatory: explicitly exclude scope to prevent creep
- User scenarios over feature lists: describe what users DO, not what the system HAS
- Concrete over abstract: use examples, numbers, and specific names
- Mark open questions explicitly: [OPEN] tag for items needing downstream resolution

## Output Structure

Adapt section numbering and depth to the project. Typical structure:

1. Background & Opportunity
2. Target Users
3. Goals & Non-Goals
4. Core Concept (value proposition, scenarios, differentiators)
5. Design Principles
6. UX Direction (user flows, interaction model)
7. Technical Direction (architecture, constraints, risks)
8. Business Direction (if applicable)
9. Scope & Phasing (MVP, future phases)
10. Success Criteria
11. Open Questions & Risks
12. Downstream Handoff (team assignments)
