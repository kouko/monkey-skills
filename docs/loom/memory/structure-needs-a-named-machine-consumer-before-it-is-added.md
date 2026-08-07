---
name: structure-needs-a-named-machine-consumer-before-it-is-added
description: Structure added to a prose artifact (a tag, a field, a class, a required section) earns its place only when a NAMED machine consumer branches on it — reader-aimed structure tested as a no-op (a reviewer harm-gate A/B found no fewer gating findings than control) while consumer-checked structure recorded real catches (critic-found rows surfaced 6 shipped-vs-enumerated gaps); before adding structure, name the consumer that will act on it — no consumer, no structure: park the idea as a backlog re-trigger instead
type: practice
origin: 2026-08-07 research session (loom 機制 × review error-rate investigation)
---

The family's structural conventions divide cleanly by whether a machine
consumes them, and the two groups have opposite track records:

- **Consumer-checked structure caught real defects.** `critic-found`
  provenance rows are consumed by ui-verification as first-class
  checklist items — its first live run surfaced 6 mismatches, all
  mapping to critic-found rows the task cut never implemented
  (`docs/loom/dogfood/2026-07-03-ui-verification-first-live-run.md`).
  The `class: instruction | evidence` split is consumed by the
  aggregation rule (evidence never gates), closing the 🟡-accumulation
  path by construction — cold-read dogfoods confirmed reviewers apply it
  (`docs/loom/dogfood/2026-08-04-docs-review-0490-fix-trap-probe.md`).
  Review-finding `origin:` lines are consumed by `loom_gate_markers.py`'s
  origin-quote verification against committed content. (This store's own
  frontmatter `origin:` field, by contrast, has no validator — it is
  context for humans, not consumer-checked structure.)
- **Reader-aimed structure tested as a no-op.** A proposed harm-gate
  (each finding must name concrete reader harm — structure whose only
  consumer is the reading reviewer) was pre-registered and A/B'd:
  treatment arms found no fewer gating findings than control, and the
  proposal was dropped unbuilt
  (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`).
  The inspection literature's checklist-reading replications point the
  same way: directing attention helps, the structured artifact itself
  does not (checklist-based reading gave no significant improvement in
  replication — Empirical Software Engineering, DOI
  10.1007/s10664-022-10123-8).

**Why:** structure aimed at readers adds authoring cost, review surface,
and drift risk without moving outcomes; structure with a machine
consumer converts a convention into a checkable invariant — the
consumer, not the markup, is what catches defects. This is the
prose-side dual of
[producer-marker-inert-until-consumer-branches-on-it](producer-marker-inert-until-consumer-branches-on-it.md):
a marker nothing branches on is inert regardless of which side of the
producer/consumer contract it lives on.

**How to apply:** before adding any structural element to a prose
artifact (frontmatter field, provenance tag, severity class, required
section), name the machine consumer — the validator, gate, aggregation
rule, or downstream checklist that will branch on it — and ship the
consumer in the same change. If no consumer can be named, do not add
the structure; park the idea as a backlog entry with a `start:`
re-trigger describing the consumer that would justify it.
