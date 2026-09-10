---
name: a-workflow-replay-must-preflight-its-harness-before-timing
description: A workflow replay whose declared command does not exist at the pinned target, uses the wrong command signature, or selects its runtime through a future placeholder is ungradeable before timing begins — validate every command against the target and bind every external runtime to exact bytes first, because repairing the harness after measuring can otherwise be mistaken for a policy speedup
type: gotcha
sources:
  - resource: 2026-09-06 remove-build-time-reviews historical replay
---

A fixed-patch replay can still compare the wrong thing. In this run the task
patches and order were immutable, but the first fixture named a test file that
did not exist in the target, combined two plugins in a command that accepts one,
used an incomplete version-check invocation, and described the candidate runtime
as a commit that could exist only after the replay result was written.

**Why:** A missing or malformed command is a harness failure, not a workflow
failure. A runtime selected by a future state is circular: the result determines
the bytes that were supposedly used to produce that result. Either defect makes
elapsed-time and quality comparisons ungradeable even when the applied source
trees are identical.

**How to apply:** Before starting the clock, materialize each target, verify that
every declared command path exists there, run each command's help or signature
check, and resolve external contracts to immutable content hashes. Record harness
corrections before execution; if exact target inputs cannot be recovered, report
UNGRADABLE rather than a speed win.
