---
name: a-correction-issued-in-a-dispatch-packet-evaporates
description: Withdrawing a wrong acceptance criterion in the implementer's dispatch prompt instead of in the plan itself leaves the durable document still asserting it — the implementer obeys the correction, the artifact reflects it, and the next reviewer then enforces the withdrawn wording against a correct artifact; cost three review rounds before anyone looked at where the criterion actually lived
type: process
origin: branch docs-reuse-adequacy-brief-and-backlog (loom-code 0.43.0, 2026-08-01) — Task 1, spec-review rounds 2 and 3
---

A task's GREEN criterion said a pre-existing test "still passes". A review
found that test was guarding retired vocabulary, so the orchestrator withdrew
the criterion — **in the revision dispatch packet**: *"That criterion was wrong
and is hereby replaced."* The implementer complied and retired the test.

The plan on disk still said "still passes". Two consecutive spec-review rounds
then blocked a correct artifact: round 2 against the brief's parallel claim,
round 3 against the plan's. Both reviewers were right — they judge the artifact
against the documents, and the documents had not moved.

**Why:** a dispatch packet is ephemeral. It exists for one subagent, for one
run, and nothing downstream can read it. Every gate after that point — the
reviewers, the next session, a future reader of the plan — sees only the durable
document. A correction that never lands there is, from their position,
indistinguishable from no correction at all.

**How to apply:** withdraw or amend a criterion **in the plan first**, then
dispatch. If the correction is discovered mid-round and the packet is already
out, treat writing it back as part of closing that round, not as cleanup for
later. The diagnostic that catches this early: when a reviewer blocks an
artifact you believe is correct, check whether the rule it is enforcing still
exists where the reviewer reads it, before arguing about the artifact.
Related: [[contradicting-reviewer-verdicts-localize-the-defect-to-the-spec]].
