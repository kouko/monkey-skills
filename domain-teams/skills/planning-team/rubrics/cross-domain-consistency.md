# Cross-Domain Consistency Gate

## Evaluation Instructions

Evaluate whether the PRODUCT-SPEC.md maintains consistency across
its business, design, and technical sections.

## FLAG-XD-001: Business ↔ Technical Alignment

🟢 Clear: Technical approach directly supports business goals.
    All constraints trace to business requirements.
🟡 Warning: Some technical choices lack business justification.
    Or business goals imply requirements not reflected in technical direction.
🔴 Fatal: Technical approach contradicts business goals.
    Or critical business constraint is ignored in technical section.

## FLAG-XD-002: Business ↔ Design Alignment

🟢 Clear: UX direction serves the target users and business goals.
    Design principles align with value proposition.
🟡 Warning: UX direction is generic, not tailored to stated users.
    Or design principles don't clearly connect to business goals.
🔴 Fatal: UX direction contradicts target user needs or business model.

## FLAG-XD-003: Design ↔ Technical Alignment

🟢 Clear: Technical constraints are reflected in UX direction.
    No UX promises that technology can't deliver.
🟡 Warning: Some UX assumptions may conflict with technical constraints.
    Or technical risks could impact UX but aren't acknowledged.
🔴 Fatal: UX direction requires capabilities the technical approach can't provide.

## FLAG-XD-004: Scope Consistency

🟢 Clear: Goals, Non-Goals, and MVP scope are mutually consistent.
    Nothing in Non-Goals appears in Goals. MVP is a subset of Goals.
🟡 Warning: Scope boundaries are ambiguous for some features.
    Or MVP scope seems to include Non-Goal items implicitly.
🔴 Fatal: Goals and Non-Goals contradict. Or MVP exceeds stated Goals.

## FLAG-XD-005: Terminology Consistency

🟢 Clear: Same concept uses the same name across all sections.
🟡 Warning: Minor naming inconsistencies that could cause confusion.
🔴 Fatal: Critical terms mean different things in different sections.

## Verdict Rules

- 1 🔴 → NEEDS_REVISION
- 2+ 🟡 → NEEDS_REVISION
- 1 🟡 → PASS_WITH_NOTES
- All 🟢 → PASS
