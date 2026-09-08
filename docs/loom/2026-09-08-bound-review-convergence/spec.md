# Bound Loom review convergence — spec
intent: 2026-09-08-bound-review-convergence@377ceb082
pre-build-review: required — this changes the public Review contract and adds terminal state to the checker-owned review boundary

## Requirements
REQ-1 — Three functional-content attempts
  WHEN closing Review evaluates a functional-content digest not yet seen in the current episode, the Review station shall assign the next round from one through three, while the same digest, a different reviewer or model, an app restart, and an execution retry shall not reset or increment that sequence → Acceptance #1

REQ-2 — Round-owned work
  WHERE a closing Review episode is active, the Review station shall use round one for whole-change findings, round two for the resulting fixes, and, when blockers remain, let the agent reshape the internal design before round three performs the terminal validation → Acceptance #2

REQ-3 — Execution retries are separate
  IF a reviewer call fails before returning a conforming verdict because of a transient transport error or malformed output, THEN the Review station shall retry that call at most once against the same functional content without consuming another review round and shall end with an execution-failed outcome if the retry also fails → Acceptance #3

REQ-4 — Detect non-progress before the cap
  WHEN a blocker survives two consecutive rounds, the blocker count does not fall after a functional fix, or the proposed repair repeats the same mechanism shape, the Review station shall stop local patching and require the agent to perform the internal-design re-look before the next available round → Acceptance #4

REQ-5 — Round three is terminal
  IF either required reviewer still returns NEEDS_REVISION for the third distinct functional-content digest, THEN the Review station shall end the episode as NON_CONVERGENT, refuse to dispatch a fourth review for that confirmed intent, and require the agent to report the remaining blocker, its consequence, the failed approaches, and one concrete replacement recommendation without offering another round → Acceptance #5

REQ-6 — Technical decisions stay with the agent
  WHILE responding to review findings, the agent shall change implementation, structure, or internal design without asking the user when confirmed requirements, visible behaviour, and guarantees remain unchanged; only a replacement that changes one of those shall return to intent confirmation → Acceptance #6

REQ-7 — Prove the smallest enforcement first
  The change shall first enforce the three-round terminal behaviour in the existing Review and reviewer contracts and verify it with blind behavioural cases; IF any case dispatches a fourth review, resets after an executor change, or asks the user whether to continue, THEN implementation shall stop and this spec shall be amended before adding the smallest runner-owned state, while the committed attestation and repository remain free of review-round bookkeeping → Acceptance #7

## Design decision
- agent-decided — Replace the existing open-ended fix-round paragraphs in `review/SKILL.md` and `agents/reviewer.md` with one shared episode definition and terminal transitions. The first implementation adds no command, schema, hook, or stored ledger.
- agent-decided — A closing Review episode is identified by its confirmed-intent commit and begins when reviewers first evaluate completed functional content. PASS or PASS_WITH_NOTES followed by successful finalization ends it as PASS; a second failed reviewer invocation ends it as EXECUTION_FAILED; third-round NEEDS_REVISION ends it as NON_CONVERGENT. Only a newly confirmed intent starts another episode.
- agent-decided — A changed functional-content digest represents a new semantic review attempt; repeated evaluation of the same digest for an allowed executor retry does not spend another round. Task, app, reviewer, vendor, model, branch name, and internal redesign changes do not create another episode.
- agent-decided — Keep stuck-pattern recognition in the Review and reviewer contracts because repeated-mechanism equivalence is semantic. Round two forces an internal-design re-look before the one remaining validation instead of opening another local patch cycle.
- agent-decided — Give one retry to a failed reviewer invocation. This separates transient executor failure from a semantic review round while bounding quota and elapsed time.
- agent-decided — Scope the budget to the closing Review station. A required pre-build spec review checks a different artifact before Build and does not consume the closing functional-content budget.
- agent-decided — Preserve two fresh-context reviewers on the final functional content and the existing one-time package suite and adversarial execution required by PRINCIPLES.md.
- agent-decided — Blind behavioural cases cover clean PASS, one fix then PASS, design re-look then PASS, terminal third-round failure, repeated digest, executor replacement, app/task resume, and attempts to ask the user for a fourth round. Any passing behaviour is the admission condition for keeping the state-free design.

## Alternatives considered
- Keep the current advisory third-round sentence without behavioural verification — rejected because historical changes continued far beyond it and the contract never states a terminal outcome.
- A committed review ledger with findings and resolutions — rejected because PRs #805 and #806 removed that bookkeeping; the cap needs attempt identity, not a second evidence record.
- Add runner or Git-common-directory state immediately — deferred by the confirmed intent; it becomes eligible only if a blind behavioural case proves the smallest contract cannot stop reliably, and requires a spec amendment covering concurrency, atomic writes, malformed state, retention, and reset before implementation.
- Count commits, reviewer identities, or model calls — rejected because rebases, vendor retries, and model changes do not identify distinct functional content and are not portable across repositories.
- Ask the user whether to continue after round three — rejected because the user cannot reliably adjudicate internal technical blockers and caution predictably selects another round.
- Automatically reset the counter after an internal redesign — rejected because it turns redesign into an unlimited-budget escape hatch.
- Apply one shared budget to pre-build spec review and closing Review — rejected because the checkpoints evaluate different artifacts and would leave high-risk changes less repair room after mandatory design review.

## Current state evidence
- Forward: `loom-code/skills/review/SKILL.md` section `## 4. Fix functional findings once` asks for one fix batch but defines no terminal outcome when renewed verdicts fail.
- Reverse: `loom-code/agents/reviewer.md` section `## Fix rounds — when you are the resumed reader` sends a third round to a design re-look but still permits a later fix round.
- Error: `docs/loom/2026-09-06-reuse-branch-end-suite-result/review.json` records verdict rounds through 26, showing that advisory re-look wording did not bound the episode.
- Data: `loom-code/scripts/loom_checker.py` function `cmd_finalize_review` accepts only passing verdicts and writes the final attestation; the first-stage design deliberately leaves that generated evidence schema unchanged.
- Boundary: `loom-code/skills/ship/SKILL.md` validates the generated attestation and owns publication; review-budget state shall not change publication or CI behaviour.

## UI flows
N/A — this changes internal agent orchestration and checker state; it adds no interface the user reads or types into.
