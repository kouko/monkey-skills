---
name: 2026-08-07-merge-sdd-review-weight-exemption-protocols
description: SDD carries two parallel review-weight exemption protocols that could be one table
status: PARKED
origin: 2026-08-07 family complexity audit (docs/loom/audits/2026-08-07-family-complexity-audit.md, item A4)
start: a third review-weight exemption shape appears, or either protocol needs a semantic edit anyway
---

subagent-driven-development/SKILL.md:94-110 specifies two separately
written exemption protocols that fork the reviewer triad: the mechanical
3-part self-check and the prose docs-reviewer substitution. They could
plausibly merge into one "narrow-scope review substitution" table.

Parked rather than done because the two have genuinely different
self-check shapes (script re-run vs reviewer swap), and this repo has a
documented precedent of exemption-text compression flipping rule
polarity. Merging now trades a modest word saving against a known
failure class. If the start condition fires, reconcile semantics first,
then merge, and pin the merged table with a weak-model cold-read.
