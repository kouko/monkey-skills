# Plan ledger notes

Companion file to `SKILL.md`, kept out of the body to stay under the
CHK-SKL-010 word cap. It carries the Progress ledger and Decision Log
maintenance guidance in full — the section itself is the rule; the
SKILL.md body pointer is the route to it.

## Progress ledger — maintain `Status` per task + resume from it (v0.10.0+; default-on since v0.60.0 — old plans opt-in by presence)

When the plan carries the per-task `Status` field (see `writing-plans/references/plan-format.md` §Progress ledger), the orchestrator **writes it back into the plan as it executes** so the plan becomes a durable, shared progress record:

- On dispatch → set `Status: claimed(@<agent>)` (`<agent>` = the worktree branch name, unique per agent; for a single-orchestrator run use the current branch).
- On resolved DONE (both reviewers PASS / PASS_WITH_NOTES **— or, on the `Review-weight: mechanical` path in `SKILL.md`, the self-check passing in place of reviewer verdicts**) **after committing** → set `Status: done(<sha>)` with that task's commit sha.
- On `BLOCKED` / NEEDS_CONTEXT / the 3-round cap → set `Status: blocked`.

Commit the ledger update **per task** (lean: keep it maximally current so a crash loses at most the one in-flight task). The plan file is the SSOT for progress; the per-task code commits are the durable artifacts the ledger points at.

**Resume after interruption:** on re-entry, **read the plan ledger first** — skip every `done(<sha>)` task (its work is committed), redo only **your own** in-flight `claimed(@<this-agent>)` task, and continue. (In mode (b), leave a sibling agent's live `claimed(@other)` alone — it owns that slice; see `dispatching-parallel-agents` §Multiple concurrent sessions.) This is the continuous, finer-grained complement to `dev-workflow:handoff` (which stays for the cross-session narrative + verification commands). A plan with no `Status` fields → behaves exactly as before (the ledger is opt-in by presence).

## Decision Log maintenance — append during execution

When the orchestrator or an implementer report surfaces an agent-decided engineering choice that was classified by the §Asking the user two-axis test in `SKILL.md` and did **not** escalate to a briefing (any non-briefed, classified decision — both two-way-door cells, per `kickoff-briefing.md` §a/§e), append one entry to the plan's `## Decision Log` per `writing-plans/references/plan-format.md`'s record spec (pointer — do not restate the format). Write it into the plan document itself, the same artifact the Progress ledger lives in. Commit the entry with that task's ledger update — same per-task cadence as `Status`, above. **Appetite read**: before applying the threshold, check the target repo's `docs/loom/PRINCIPLES.md` Engineering Principles section for an `escalation appetite` entry (landing shape: `loom-design/skills/product-principles/references/principles-rules.md` §Escalation appetite — landing shape) and tune the bar accordingly, read once, never re-ask; absent → default to the threshold as written.
