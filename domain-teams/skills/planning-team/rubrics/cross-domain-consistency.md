# Cross-Domain Consistency Gate

## Evaluation Instructions

Evaluate whether the PRODUCT-SPEC.md maintains consistency across
its business, design, and technical sections. Cross-reference the
team's grounded standards to verify that each cross-domain claim is
anchored properly.

Reference standards:
- `standards/planning-frameworks.md` — JTBD, 4 Big Risks, BMC, Lean Canvas, 3C, VPC
- `standards/discovery-frameworks.md` — Lean Startup, Product Discovery vs Delivery
- `standards/goals-and-metrics.md` — OKR, North Star Metric, Goals/Non-Goals
- `standards/spec-completeness-standards.md` — decision rationale rule, 5W2H cross-check

## FLAG-XD-001: Business ↔ Technical Alignment

🟢 Clear: Technical approach directly supports business goals.
    All constraints trace to business requirements. Decision rationale
    explicitly links every technical choice to a business "because Y"
    per `standards/spec-completeness-standards.md` §Decision Rationale.
🟡 Warning: Some technical choices lack business justification.
    Or business goals imply requirements not reflected in technical
    direction.
🔴 Fatal: Technical approach contradicts business goals.
    Or critical business constraint is ignored in technical section.

## FLAG-XD-002: Business ↔ Design Alignment

🟢 Clear: UX direction serves the target users and business goals.
    Design principles align with value proposition. Every Job Story
    (Adams 2016) has a corresponding UX flow that services that Job.
🟡 Warning: UX direction is generic, not tailored to stated users.
    Or design principles don't clearly connect to business goals or
    to the Jobs-to-be-Done.
🔴 Fatal: UX direction contradicts target user needs or business
    model. Or the UX flow does not actually service the stated JTBD.

## FLAG-XD-003: Design ↔ Technical Alignment

🟢 Clear: Technical constraints are reflected in UX direction.
    No UX promises that technology can't deliver. The 4 Big Risks
    (`standards/planning-frameworks.md`) Usability and Feasibility
    axes are explicitly reconciled.
🟡 Warning: Some UX assumptions may conflict with technical
    constraints. Or technical risks could impact UX but aren't
    acknowledged.
🔴 Fatal: UX direction requires capabilities the technical approach
    can't provide.

## FLAG-XD-004: Scope Consistency

🟢 Clear: Goals, Non-Goals, and MVP scope are mutually consistent.
    Nothing in Non-Goals appears in Goals. MVP is a subset of Goals.
    Non-Goals names **plausible rejected goals** per
    `standards/goals-and-metrics.md` §Goals/Non-Goals (Ubl 2020), not
    trivially-excluded items. MVP is defined as
    minimum-for-validated-learning (Ries 2011) not
    smallest-shippable-feature-set.
🟡 Warning: Scope boundaries are ambiguous for some features.
    Or MVP scope seems to include Non-Goal items implicitly. Or
    Non-Goals is near-empty (fails to name plausible rejected goals).
🔴 Fatal: Goals and Non-Goals contradict. Or MVP exceeds stated
    Goals. Or MVP is defined as a feature set rather than a learning
    mechanism.

## FLAG-XD-005: Assumption → Risk Coverage

🟢 Clear: Every `[ASSUMPTION]` tag is mapped to one of the 4 Big
    Risks (Value / Usability / Feasibility / Business Viability per
    Cagan 2017) with a named validation approach. Top 3 assumptions
    cover at least 2 distinct risk categories.
🟡 Warning: Some assumptions are untagged, or multiple assumptions
    crowd into a single risk category (suggests the team has not
    actually stress-tested all 4 axes). Or 4-axis framework is
    misattributed to Bland instead of Cagan.
🔴 Fatal: Top 3 assumptions all cluster in one risk category with
    others unexplored. Or 4-axis framework is not used at all.

## FLAG-XD-006: Terminology Consistency

🟢 Clear: Same concept uses the same name across all sections.
    Framework citations are internally consistent — e.g., if Job
    Story template is introduced, all user-need statements use Job
    Story form (Adams 2016), not mixed with user-story form.
🟡 Warning: Minor naming inconsistencies that could cause confusion.
    Or mixed Job Story / user story forms without explicit rationale.
🔴 Fatal: Critical terms mean different things in different sections.
    Or MVP is defined one way in Scope and a different way in
    Success Criteria.

## Verdict Rules

- 1 🔴 → NEEDS_REVISION
- 2+ 🟡 → NEEDS_REVISION
- 1 🟡 → PASS_WITH_NOTES
- All 🟢 → PASS
