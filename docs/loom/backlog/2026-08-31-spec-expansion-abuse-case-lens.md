---
name: 2026-08-31-spec-expansion-abuse-case-lens
description: Add an abuse-case / misuse-case fan-out lens to loom-design:spec-expansion so the attack catalogue can grow from the spec, not only from post-hoc audits
status: open
origin: 2026-08-31 — adversarial-audit-station arc (docs/loom/specs/2026-08-31-adversarial-audit-station.md `## Out of Scope`), deferred from BI-11's scope
start: event — a second adopting repo's `ATTACK-CATALOGUE.md` is authored mostly by copying loom-code's shipped classes rather than by reasoning from that repo's own spec, showing the catalogue isn't growing from specs on its own
---

Today `loom-code:adversarial-audit-station` grows its attack catalogue
one way: an audit finds a hole, the finding becomes a pinned test and a
catalogue line. `loom-design:spec-expansion` fans a sparse seed out into
objects, states, paths, and edge cases, but has no misuse-case lens —
nothing in that fan-out asks "who would want to defeat this requirement,
and how" the way Sindre & Opdahl's misuse-case extension to use-case
modeling does (G. Sindre, A. L. Opdahl, "Eliciting security requirements
with misuse cases", Requirements Engineering 10(1), 2005).

Adding that lens would let a spec draft seed the attack catalogue at
authoring time — before any code exists to audit — instead of the
catalogue only ever growing retroactively from a reproduced finding.
The two feed each other: a misuse case fanned out at spec time becomes a
candidate attack class; an attack class reproduced by the station could
in turn prompt re-running the lens on the next spec touching a similar
surface.

Next step: a `loom-design` brief scoping where the lens sits in
`spec-expansion`'s existing fan-out passes and how (or whether) its
output threads into `loom-code`'s catalogue format
(`docs/loom/ATTACK-CATALOGUE.md`) without creating a hard cross-plugin
dependency.
