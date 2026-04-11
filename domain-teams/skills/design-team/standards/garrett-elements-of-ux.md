---
title: Garrett Elements of UX (5 Planes)
tier: 1
---

# Garrett Elements of UX (5 Planes)

Canonical anchor for Jesse James Garrett's 5-plane model, which
partitions the design-team quality gate hierarchy. Tier 1: the model
is well recovered from training; the body focuses on the gate mapping,
which is the design-team specific load-bearing artifact.

## Primary Sources

- Jesse James Garrett (2010) *The Elements of User Experience: User-Centered Design for the Web and Beyond*, 2nd edition. New Riders. Canonical source for the 5-plane model extended beyond the web.
- Jesse James Garrett (2000) "The Elements of User Experience" (original diagram). http://www.jjg.net/elements/pdf/elements.pdf. The original PDF diagram predating the 1st edition book.

## The Model

Garrett frames user experience as a bottom-up abstraction ladder from
business **Strategy** (the abstract) up to **Surface** visuals (the
concrete). Lower planes are more concrete and build on decisions made
at the upper, more abstract planes — but all five are revisited
iteratively throughout a project.

## The 5 Planes

- **Strategy** — user needs × business objectives. Why are we building
  this? For whom?
- **Scope** — functional requirements + content requirements. What
  features and what content will the product contain?
- **Structure** — interaction design + information architecture. How
  does the system behave when users interact; how is information
  organized?
- **Skeleton** — interface design + navigation design + information
  design. The placement of buttons, controls, labels, and navigation.
- **Surface** — visual design. The sensory final layer: typography,
  colour, imagery, composition.

## Gate Scope Partition (load-bearing for design-team)

The design-team quality gates map onto Garrett's planes as follows:

| Plane | Primary concern | design-team gate |
|---|---|---|
| Strategy | user needs × business objectives | `ux-strategy-gate` |
| Scope | functional + content requirements | `ux-strategy-gate` |
| Structure | interaction + information architecture | `ui-interaction-gate` |
| Skeleton | interface + navigation + information design | `ui-interaction-gate` |
| Surface | visual design | `visual-gate` |

Accessibility cross-cuts all five planes and is handled by a dedicated
`a11y-gate` that references `standards/wcag-baseline.md` as its rule
source.

## Not a Waterfall

The 5 planes are **not** a sequential phase gate. Upper planes
constrain lower planes, but real projects revisit all 5 iteratively:
Strategy is re-examined when Scope discoveries reveal unmet user
needs; Skeleton decisions may surface Structure ambiguities that
force an IA revision; Surface experiments may expose Skeleton
legibility issues. Treating the stack as a one-pass waterfall
violates Garrett's explicit guidance in the 2nd-edition preface and
leads to late-stage rework.
