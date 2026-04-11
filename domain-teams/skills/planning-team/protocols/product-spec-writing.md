# Product Spec Writing Protocol

Write cross-domain product specs (PRODUCT-SPEC.md / 企画書).
A good product spec lets any team (code, design, research) understand
what to build, why, and the boundaries.

## Primary Sources

- `standards/planning-frameworks.md` — JTBD (Christensen 2003, Christensen et al. 2016 HBR, Adams 2016 Intercom for Job Story template), Business Model Canvas (Osterwalder 2010), Lean Canvas (Maurya 2022), 4 Big Risks (Cagan 2017), Assumption Mapping (Bland & Osterwalder 2020), 3C 分析 (大前 1975), Value Proposition Canvas (Osterwalder et al. 2014)
- `standards/discovery-frameworks.md` — Lean Startup (Ries 2011), Customer Development (Blank 2005), Product Discovery (Cagan 2017), Opportunity Solution Tree (Torres 2021), PR/FAQ Working Backwards (Bryar & Carr 2021 Ch.4)
- `standards/goals-and-metrics.md` — OKR (Grove 1983 / Doerr 2018), North Star Metric (Ellis & Brown 2017), AARRR (McClure 2007), Goals/Non-Goals (Ubl 2020)
- `standards/spec-completeness-standards.md` — 5W2H completeness check + decision rationale rule + JP 企画 cultural anchors

## Phase 1: Vision & Opportunity

1. Clarify the core problem or opportunity
2. Identify target users (who benefits, who decides, who pays)
3. Define the user's **Job-to-be-Done**:
   - Use the **Job Story** template from
     `standards/planning-frameworks.md` §JTBD:
     "When [situation], I want to [motivation], so I can [outcome]."
     Cite Adams (2016) Intercom blog for the template — NOT Christensen.
   - Ground the underlying theory in Christensen (2003) *Innovator's
     Solution* Ch.3 or Christensen et al. (2016) HBR.
4. Define success criteria (measurable outcomes, not features) —
   `standards/goals-and-metrics.md` §North Star Metric for the single
   load-bearing value indicator.
5. Assess market context (existing solutions, gaps, timing)
   - If competitors exist, use **3C 分析**
     (`standards/planning-frameworks.md` §3C 分析 — cite 大前研一 1975
     『企業参謀』プレジデント社 as primary; Ohmae 1982 *The Mind of
     the Strategist* as English access point)
   - If market data is needed, request the user to invoke `research-team`

## Phase 2: Concept Definition

1. **Value proposition** — one sentence: what + for whom + why better.
   For customer-facing products use the **Value Proposition Canvas**
   (`standards/planning-frameworks.md` §VPC — Osterwalder et al. 2014)
   to map Customer Jobs / Pains / Gains against Products & Services /
   Pain Relievers / Gain Creators.
2. **Core user scenarios** — 2-3 primary use cases, narrative form.
3. **Key differentiators** — what makes this different from alternatives.
4. **Design principles** — 3-5 guiding principles for all decisions.

## Phase 3: Scope & Boundaries

1. **Goals** — what the product WILL do in this version. If using OKRs,
   express the top-level Objective + 3-5 Key Results per
   `standards/goals-and-metrics.md` §OKRs (Grove 1983 / Doerr 2018):
   "I will [Objective] as measured by [Key Results]".
2. **Non-Goals** — what it explicitly WON'T do. Per
   `standards/goals-and-metrics.md` §Goals/Non-Goals (Ubl 2020): name
   **plausible goals that were considered and rejected**, not things
   that are obviously out of scope. Empty or trivial Non-Goals is a
   gate failure.
3. **Assumption discovery**: map each assumption to one of the
   **4 Big Risks** (`standards/planning-frameworks.md` §The 4 Big Risks
   — Cagan 2017 *Inspired* 2nd ed Part III): Value / Usability /
   Feasibility / Business Viability. Then use Bland & Osterwalder (2020)
   **Assumption Mapping** to rank by Impact × Evidence; top 3 are
   `[ASSUMPTION]` tags with a named validation approach.
4. **MVP definition** — per `standards/discovery-frameworks.md` §MVP
   (Ries 2011 *The Lean Startup* Part Two): the **minimum product that
   lets the team collect the maximum validated learning about
   customers with the least effort**. NOT "the smallest shippable
   feature set". Every MVP definition must name what it is trying to
   learn.
5. **Future phases** — logged for reference, not committed.

## Phase 4: Direction Setting

1. **UX direction**:
   - Core user flow (entry → primary task → outcome)
   - Interaction model (CLI / GUI / API / conversational)
   - Key design constraints (platform, accessibility, performance)
2. **Technical direction**:
   - Architecture approach with rationale (decision rationale rule
     from `standards/spec-completeness-standards.md` §Decision
     Rationale — every "we chose X" needs a "because Y")
   - Key technical constraints (language, platform, deployment)
   - Technical risks and mitigation strategies
   - External dependencies (APIs, models, services)
3. **Business direction** (if applicable):
   - Revenue model / monetization — reference
     `standards/planning-frameworks.md` §Business Model Canvas or
     §Lean Canvas depending on product maturity
   - If the product has a clear conversion funnel, reference
     `standards/goals-and-metrics.md` §AARRR (McClure 2007 5-stage
     canonical: Acquisition / Activation / Retention / Referral /
     Revenue)
   - Distribution strategy
   - Regulatory / compliance constraints

## Phase 5: Handoff Preparation

1. Identify downstream work:
   - What needs TECH-SPEC.md (code-team)?
   - What needs UI/UX design (design-team)?
   - What needs deeper research (research-team)?
2. List open questions that downstream teams must resolve — mark
   with `[OPEN]` tag
3. Define handoff format: PRODUCT-SPEC.md sections map to team
   assignments
4. **5W2H final cross-check** — before handoff, verify the spec
   answers all 7 letters per
   `standards/spec-completeness-standards.md` §5W2H — Per-Letter
   Checks. Any missing letter is an incomplete spec.

## Rules

- **Cross-domain**: cover business + design + engineering, not just
  one
- **Decision rationale required**: every "we chose X" needs
  "because Y" (`standards/spec-completeness-standards.md` §Decision
  Rationale Rule)
- **Non-Goals mandatory**: explicitly exclude plausible rejected goals
  to prevent scope creep (Ubl 2020 via
  `standards/goals-and-metrics.md`)
- **User scenarios over feature lists**: describe what users DO, not
  what the system HAS (Job Story template, Adams 2016)
- **MVP is about learning, not shipping**: cite Ries (2011) and
  define what the MVP is trying to learn — do NOT treat MVP as
  "smallest shippable feature set"
- **Concrete over abstract**: use examples, numbers, and specific
  names
- **Mark open questions explicitly**: `[OPEN]` tag for items needing
  downstream resolution

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
