---
name: optional-template-sections-produce-no-behavior
description: A template section marked optional ("remove if none") produces near-zero compliance even when preloaded doctrine tells writers when to fill it — measured 1/29 plans-briefs carrying a Mermaid block while the brief template already had a `## Diagrams` section; behavior appeared only after the slot became fill-or-declare (embed the artifact or write a pinned N/A line with a reason, deleting the heading forbidden) with a reviewer dimension that treats an absent slot or false N/A as a finding
type: practice
origin: feat/visualization-trigger-layer (2026-08-11) — loom-code 0.76.0 / loom-spec 0.9.0 / loom-interface-design 0.11.0
---

Before this arc, the brief template carried an optional `## Diagrams`
section ("remove this section if no diagrams"), the family reception
preloaded the channel rule every session, and visual-companion.md held a
content-shape→diagram-type mapping — yet 1 of 29 plans/briefs contained
a Mermaid block and 0 spec-layer docs did. The doctrine was all
guard-shaped (HOW to draw once drawing was decided); nothing forced the
decision itself to be made visibly.

**Why:** an optional slot with no fill-or-declare obligation and no
reviewer check is behaviorally equivalent to no slot: skipping it is
free and invisible. Forcing a *declaration* (fill the slot or write the
pinned `N/A — …: <reason>` line) converts the skip into a reviewable
claim without mandating decoration — the slot forces the decision, not
the drawing. This is the artifact-side counterpart of
[[imperative-trigger-cards-beat-descriptive-preloads]] (chat-side):
both show that citable doctrine alone does not steer behavior; the
mechanism must bind at the acting moment (there: the imperative card;
here: the template slot the writer cannot silently omit).

**How to apply:** when a template section SHOULD usually be filled,
never mark it removable — make it fill-or-declare with a pinned N/A
line + mandatory one-line reason, and wire "slot absent / N/A reason
does not hold" into the relevant reviewer's omission dimension. Keep
the trigger shape-based (flow/state/architecture-shaped content), never
count-based — quotas induce decorative artifacts.
