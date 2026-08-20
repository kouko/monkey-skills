---
name: 2026-08-10-design-system-leads-with-adjectives-where-the-format-says-lead-with-a-reference
description: design-system makes 3-5 inherited tone-and-manner adjectives the governing mood and ships six NEVER rules, but DESIGN.md's own PHILOSOPHY.md says adjectives describe a region while a specific reference describes a point, and that a long don't-list signals a description too vague to carry its own constraints
status: open
origin: 2026-08-08..10 DESIGN.md spec-conformance research — reading google-labs-code/design.md PHILOSOPHY.md (repo root, 110 lines; missed on the first pass because only docs/spec.md was read). Split out of docs/loom/specs/2026-08-08-design-md-spec-conformance.md so a mechanical token-shape fix would not be bundled with a taste decision about the station's generative layer.
start: next substantive edit to design-system's Overview / Brand section or its Anti-patterns list, or the first real run of design-system that produces a DESIGN.md worth judging
---

- Start: next substantive edit to design-system's Overview / Brand section or its Anti-patterns list, or the first real run of design-system that produces a DESIGN.md worth judging
- Origin: 2026-08-08..10 DESIGN.md spec-conformance research — reading google-labs-code/design.md PHILOSOPHY.md (repo root, 110 lines; missed on the first pass because only docs/spec.md was read). Split out of docs/loom/specs/2026-08-08-design-md-spec-conformance.md so a mechanical token-shape fix would not be bundled with a taste decision about the station's generative layer.

- What: `design-system` currently makes **inherited adjectives the
  governing layer**. `references/design-md-schema.md` (Overview / Brand)
  requires the mood to be inherited verbatim from `PRINCIPLES.md`'s
  `## Anchors` tone-and-manner row — "**those adjectives ARE this design
  system's governing mood**" — with the committed visual concept sitting
  alongside rather than above it. It also ships six `NEVER` anti-pattern
  rules (no Inter/Roboto without reason, no purple→blue gradient, no
  uniform border-radius, no #000-on-#fff, ≤2–3 accents, no token that
  contradicts PRINCIPLES).

  The format's own philosophy document argues the opposite ordering
  (verified verbatim,
  `https://raw.githubusercontent.com/google-labs-code/design.md/main/PHILOSOPHY.md`):

  > "The quality of a generated design is determined less by the
  > precision of its values than by how clearly the intent is described."

  > "Modern, clean, trustworthy, premium" evokes nothing specific.
  > "Adjectives describe a region." / "A specific reference describes a
  > point."

  > "A clear design reference carries its restrictions automatically …
  > a long rambling list is often a sign the description was too vague
  > to carry them."

  So both of the station's generative devices are the ones PHILOSOPHY.md
  names as weak: adjectives as the governing mood, and an explicit
  don't-list standing in for a reference specific enough to imply its
  own restrictions.

  Two independent corroborations from the same research round:
  Anthropic's `frontend-design` skill takes the reference-first position
  ("pin it yourself … name one concrete subject") and pairs it with a
  named anti-canon rather than generic bans; and BMAD's `bmad-ux`
  renders whole visual *directions* for the user to pick from —
  "a complete visual personality applied to the same key screen — not a
  palette swap" — i.e. it also traffics in points, not regions.

  The open question is the ordering, not the deletion. `PRINCIPLES.md`
  is loom's governance layer and the adjectives are how tone reaches
  this station; the candidate change is to make the **committed visual
  concept the governing layer** and demote the inherited adjectives to a
  constraint the concept must satisfy — plus a decision on whether the
  six NEVERs earn their place once a concept is required to be specific.
  Not obviously right: the anti-patterns list was added because a real
  failure mode was observed, and PHILOSOPHY.md's claim is an assertion
  with no measurement behind it.

  Evidence that the concern is real and not just doctrinal: two research
  legs independently observed the same taste-collapse. Anthropic names
  three looks AI design converges on (warm cream #F4F1EA + serif +
  terracotta; near-black + acid accent; broadsheet hairlines); Japanese
  practitioner reports name a different but analogous set (centred hero,
  three cards, emoji icons, purple gradient). Different specifics, same
  phenomenon, independent discovery.

  Related: [[docs/loom/specs/2026-08-08-design-md-spec-conformance.md]]
  (the mechanical half), and the OPEN entry
  `2026-07-10-dogfood-replay-eval-harness-for-the-principles-construction-flow`
  — if a replay harness ever exists, this ordering question is
  measurable rather than arguable.
