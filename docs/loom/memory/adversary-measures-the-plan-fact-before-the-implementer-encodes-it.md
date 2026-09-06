---
name: adversary-measures-the-plan-fact-before-the-implementer-encodes-it
description: A plan's quantitative current-state fact (a call count, a spawn count) is measured by the adversary-first probe before any implementer reads it, because a plan number written from a code read is routinely wrong by a hidden nested call — when the probe's measurement disagrees with the plan, the plan's un-landed task line is amended with the reason and the probe's number becomes the contract, never the other way round
type: process
origin: 2026-09-07-loom-script-performance W1-05 — plan said update-blockers reads each ticket 2N times; the adversary's counting wrapper measured 4N+1 (a nested validate() inside _require_valid_store); plan amended at dfbdfdf9 before the implementer started
---

The plan for a "read each ticket once" task stated the current cost from
a code read: two `glob` + `read_ticket` passes, so 2N reads, target N.
The adversary's first probe wrapped `read_ticket` with a counter and
measured 25 calls for N=6 — 4N+1 — because `_require_valid_store` calls
`validate()`, which runs its own two passes. Had the implementer been
dispatched on the plan's number, the "N" assertion would have been
unreachable without widening the task into `validate()`'s public
signature, and the honest outcome (2N+1) would have looked like a
failure.

**Why:** a number derived by reading code counts the calls the reader
saw; a number derived by running code counts the calls that happen. The
gap is always a nested call in a helper the reader did not open, and it
is exactly the kind of fact `intake.test-case-pair` cannot check because
the plan's Test line is prose.

**How to apply:** an adversary-first probe for any task whose acceptance
is a count measures the count first and reports it; the orchestrator
compares it with the plan's Test line before dispatching the implementer.
On disagreement, amend the un-landed task line (the plan charter's
`unlanded-task-amended-with-reason` policy, reason in the commit
message), tell the implementer which probe assertion encodes the old
fact and that it may correct that one assertion in its own commit, and
let the blind-run report explain the delta to the user in plain words.
The plan's number is never defended against a measurement.
