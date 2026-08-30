---
name: 2026-08-30-implementation-task-and-review-checkpoint-granularity
description: Loom planning has no size control separating fine requirements from implementation and review checkpoints
status: open
origin: Outcome Map v3 implementation on branch codex/outcome-map-v3-design
start: event — writing-plans or subagent-driven-development next changes task sizing or review checkpoint policy
---

Outcome Map v3 kept useful fine-grained requirements and TDD tests, but also
turned nearly every requirement into its own implementation task, commit,
privacy gate, immutable packet, spec review, and quality review. Several tasks
shared one capability boundary: delivery evidence spanned T8, T9, T15, and T22;
transaction and recovery behavior spanned T10, T13, and T24. Reviewing each
partial state forced repeated setup and repeatedly raised the question whether
a finding was a current defect or merely a later requirement. The fixed review
cost became disproportionate to the code increment.

This is distinct from the requirement-ownership backlog entry. Explicit owned
requirements constrain what may block a review; this entry constrains how much
work should share one implementation and review checkpoint in the first place.

The next step is to add and dogfood a task-sizing rule in planning and
subagent-driven development. Requirements and RED/GREEN tests may remain
fine-grained, while implementation tasks should group work that shares one
module invariant or capability boundary. A full commit/privacy/spec/quality
checkpoint should occur at the capability boundary, not automatically once per
requirement. The planner should split again when the batch cannot be reviewed
coherently, crosses independent failure domains, or exceeds the executor's
bounded context; it should merge adjacent tasks when their intermediate states
are knowingly incomplete and reviewers would need future requirements to judge
them correctly.

Acceptance evidence should compare per-requirement and capability-batch plans
on the same corpus. Measure review rounds, reviewer setup calls, false scope
expansions, escaped defects, total elapsed work, and maximum diff size. Adopt a
mechanical heuristic only if it reduces review cost without lowering defect
detection or making requirement-to-test traceability weaker.
