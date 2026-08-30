# Plan ledger notes

Companion file to `SKILL.md`, kept out of the body to stay under the
CHK-SKL-010 word cap. It carries the Progress ledger and Decision Log
maintenance guidance in full — the section itself is the rule; the
SKILL.md body pointer is the route to it.

## Progress ledger — maintain `Status` per task + resume from it (v0.10.0+; default-on since v0.60.0 — old plans opt-in by presence)

When the plan carries the per-task `Status` field (see `writing-plans/references/plan-format.md` §Progress ledger), the orchestrator **writes it back into the plan as it executes** so the plan becomes a durable, shared progress record:

- On dispatch → set `Status: claimed(@<agent>)` (`<agent>` = the worktree branch name, unique per agent; for a single-orchestrator run use the current branch).
- On a validated Batch member's locally committed and mechanically verified final bytes → only SDD sets `Status: implemented(<sha>)` with that exact reachable member commit. This is a Task state, not a Batch status or a second lifecycle.
- On individual resolved DONE (both reviewers PASS / PASS_WITH_NOTES **— or, on the `Review-weight: mechanical` path in `SKILL.md`, the self-check passing in place of reviewer verdicts**) **after committing** → set `Status: done(<sha>)` with that task's commit sha.
- On aggregate `finalize` → SDD passes the reducer's sealed transition authority, complete validated Batch member set, and exact implemented snapshot to `plan_card.atomic_batch_status_update`; every member becomes `done(<same-sha>)` in one replacement.
- On aggregate `reopen` → SDD passes that exact decision authority and applies its owner union in one atomic replacement; owners return to `pending` and unchanged members remain `implemented(<sha>)`.
- On `BLOCKED` / NEEDS_CONTEXT / the 3-round cap → set `Status: blocked`.

Every mutation uses the participating Loom writer lock from `plan_card`; inside that lock a Batch mutation re-reads declaration, disposition, membership, and member statuses and refuses any mismatch with the sealed Packet decision. Direct editors that bypass the lock must not run concurrently. Commit the ledger update **per task**, except that aggregate finalization or owner-union reopening commits its one atomic Batch replacement as one ledger update. The plan file is the only progress ledger; the transient authority is not persisted, and member code commits are the durable artifacts its Task states point at.

**Resume after interruption:** on re-entry, **read the plan ledger first** — skip every `done(<sha>)` task; preserve an exact `implemented(<sha>)` member and reconstruct eligibility and a fresh Packet from current authority; redo only **your own** in-flight `claimed(@<this-agent>)` task. Leave a sibling agent's live `claimed(@other)` alone — it owns that slice; see `dispatching-parallel-agents` §Multiple concurrent sessions. Never infer or persist a Batch status during resume.

## Decision Log maintenance — append during execution

When the orchestrator or an implementer report surfaces an agent-decided engineering choice that was classified by the §Asking the user two-axis test in `SKILL.md` and did **not** escalate to a briefing (any non-briefed, classified decision — both two-way-door cells, per `kickoff-briefing.md` §a/§e), append one entry to the plan's `## Decision Log` per `writing-plans/references/plan-format.md`'s record spec (pointer — do not restate the format). Write it into the plan document itself, the same artifact the Progress ledger lives in. Commit the entry with that task's ledger update — same per-task cadence as `Status`, above. **Appetite read**: before applying the threshold, check the target repo's `docs/loom/PRINCIPLES.md` Engineering Principles section for an `escalation appetite` entry (the landing shape is owned by `loom-design:product-principles`, §Escalation appetite) and tune the bar accordingly, read once, never re-ask; absent → default to the threshold as written.
