# Bound Loom review convergence — spec
intent: 2026-09-08-bound-review-convergence@377ceb082
pre-build-review: required — this changes the public Review contract and adds terminal state to the checker-owned review boundary

## Requirements
REQ-1 — Three functional-content attempts
  WHEN closing Review submits reviewer verdicts for a functional-content digest not yet seen in the current change's review episode, the checker shall assign the next round from one through three, while the same digest, a different reviewer or model, and an execution retry shall not reset or increment that sequence → Acceptance #1

REQ-2 — Round-owned work
  WHERE a closing Review episode is active, the Review station shall use round one for whole-change findings, round two for the resulting fixes, and, when blockers remain, let the agent reshape the internal design before round three performs the terminal validation → Acceptance #2

REQ-3 — Execution retries are separate
  IF a reviewer call fails before returning a conforming verdict because of a transient transport error or malformed output, THEN the Review station shall retry that call at most once against the same functional content without consuming another review round and shall end with an execution-failed outcome if the retry also fails → Acceptance #3

REQ-4 — Detect non-progress before the cap
  WHEN a blocker survives two consecutive rounds, the blocker count does not fall after a functional fix, or the proposed repair repeats the same mechanism shape, the Review station shall stop local patching and require the agent to perform the internal-design re-look before the next available round → Acceptance #4

REQ-5 — Round three is terminal
  IF either required reviewer still returns NEEDS_REVISION for the third distinct functional-content digest, THEN the checker shall mark the episode NON_CONVERGENT, reject any fourth digest for that change, and require the agent to report the remaining blocker, its consequence, the failed approaches, and one concrete replacement recommendation without offering another round → Acceptance #5

REQ-6 — Technical decisions stay with the agent
  WHILE responding to review findings, the agent shall change implementation, structure, or internal design without asking the user when confirmed requirements, visible behaviour, and guarantees remain unchanged; only a replacement that changes one of those shall return to intent confirmation → Acceptance #6

REQ-7 — Ephemeral budget, generated evidence
  The checker shall keep only functional-content digests, assigned rounds, outcomes, and terminal status under the repository's Git common directory, exclude reviewer findings and prose from that state, and continue to generate the existing content-bound attestation only after passing verdicts and functional executions → Acceptance #7

## Design decision
- agent-decided — Extend the existing `finalize-review` transition to assign and close review rounds instead of adding a second review command; one authority already validates verdicts, runs final verification, and writes the attestation.
- agent-decided — Store the automatic budget under the Git common directory so it survives worktree and app restarts without becoming a committed review ledger or relying on repository-specific commit messages.
- agent-decided — Key attempts by the checker's existing functional-content digest. A changed digest represents a new semantic review attempt; repeated calls on the same digest are idempotent and do not spend another round.
- agent-decided — Treat PASS and PASS_WITH_NOTES as passing outcomes under the existing severity contract. NEEDS_REVISION spends a round but does not execute package or adversarial verification.
- agent-decided — On a third-round NEEDS_REVISION, write terminal NON_CONVERGENT state before returning failure. Later calls for a new digest fail without dispatching reviewers or functional executables.
- agent-decided — Keep stuck-pattern recognition in the Review and reviewer contracts because repeated-mechanism equivalence is semantic; the deterministic checker owns the hard three-digest ceiling and terminal state.
- agent-decided — Give one retry to a failed reviewer invocation. This separates transient executor failure from a semantic review round while bounding quota and elapsed time.
- agent-decided — Scope the budget to the closing Review station. A required pre-build spec review checks a different artifact before Build and does not consume the closing functional-content budget.
- agent-decided — Preserve two fresh-context reviewers on the final functional content and the existing one-time package suite and adversarial execution required by PRINCIPLES.md.

## Alternatives considered
- A prose-only three-round instruction — rejected because the current reviewer contract already calls a third round a design signal, yet historical changes continued far beyond it, and PRINCIPLES.md forbids prose-only blocking gates.
- A committed review ledger with findings and resolutions — rejected because PRs #805 and #806 removed that bookkeeping; the cap needs attempt identity, not a second evidence record.
- Count commits, reviewer identities, or model calls — rejected because rebases, vendor retries, and model changes do not identify distinct functional content and are not portable across repositories.
- Ask the user whether to continue after round three — rejected because the user cannot reliably adjudicate internal technical blockers and caution predictably selects another round.
- Automatically reset the counter after an internal redesign — rejected because it turns redesign into an unlimited-budget escape hatch.
- Apply one shared budget to pre-build spec review and closing Review — rejected because the checkpoints evaluate different artifacts and would leave high-risk changes less repair room after mandatory design review.

## Current state evidence
- Forward: `loom-code/skills/review/SKILL.md` section `## 4. Fix functional findings once` asks for one fix batch but defines no terminal outcome when renewed verdicts fail.
- Reverse: `loom-code/agents/reviewer.md` section `## Fix rounds — when you are the resumed reader` sends a third round to a design re-look but still permits a later fix round.
- Error: `docs/loom/2026-09-06-reuse-branch-end-suite-result/review.json` records verdict rounds through 26, showing that advisory re-look wording did not bound the episode.
- Data: `loom-code/scripts/loom_checker.py` function `cmd_finalize_review` accepts only passing verdicts and writes the final attestation; neither its input nor `loom-attestation/v1` carries a round budget.
- Boundary: `loom-code/skills/ship/SKILL.md` validates the generated attestation and owns publication; review-budget state shall not change publication or CI behaviour.

## UI flows
N/A — this changes internal agent orchestration and checker state; it adds no interface the user reads or types into.
