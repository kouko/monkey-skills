---
name: 2026-08-30-task-review-packets-lack-requirement-ownership
description: Per-task review packets cannot distinguish owned requirements from later-task requirements
status: open
origin: Outcome Map v3 Task 6 review on branch codex/outcome-map-v3-design
start: event — the subagent-driven-development review packet or reviewer contract is next revised
---

Per-task review currently binds the reviewer to an immutable commit and the full
spec, but it does not mechanically state which requirements the current task
owns. During Outcome Map v3 Task 6, the spec reviewer used REQ-87, assigned to
Task 13, as a blocking Task 6 finding. Some cited cases exposed real direct
Start-delivery data-loss bugs and deserved immediate repair, but the protocol
could not distinguish those from requests to implement the later generic
transaction framework early. The result is repeated review expansion and a
higher cost to close otherwise atomic tasks.

The next step is to design and test a review-packet contract with explicit
`owned_requirements`, `future_requirements`, and a blocking rule: a finding may
block the current task only when it violates an owned requirement, its stated
acceptance, or demonstrates a direct regression or safety defect in the task's
actual change. A later requirement may supply context but cannot by itself
expand the task. The reviewer verdict schema and immutable packet validator
should make this boundary observable rather than relying on dispatch prose.

Acceptance evidence should include a corpus with both legitimate cross-REQ
safety findings and illegitimate future-task expansion, plus an A/B comparison
showing fewer review rounds without suppressing real defects.
