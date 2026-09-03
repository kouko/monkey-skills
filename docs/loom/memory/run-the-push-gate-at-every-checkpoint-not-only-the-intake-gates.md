---
name: run-the-push-gate-at-every-checkpoint-not-only-the-intake-gates
description: A checkpoint that runs only the intake gates (intent / standing / contract) and never `loom_checker.py push` against HEAD reaches decision point ③ with a push gate that has never been green; on simple-loom-flow the first real run blocked on five rules, all real, and closing them cost nine review rounds, three user-run history rewrites and three blind-run addenda — run `push` at every wave-end against HEAD, and treat orchestrator-inline commits as the violation the rule says they are
type: practice
origin: simple-loom-flow (2026-09-03) — rounds 22–30 of the branch-end review; findings R22-*/R23-*/R24-*, CI-1, CI-2
---

The push gate is the only rule set that recomputes the whole branch
(trailers vs `dispatch[]`, frozen stores, probe re-execution, second
vendor). The intake gates say nothing about any of that. On this change
every checkpoint recorded "three gates exit 0" and the push gate was first
run when the user asked how Codex fits, one step before ship.

What it found was not noise: the repo's own `.codex` shim pointed at a
script deleted three waves earlier; a frozen store had been edited; 17
commits carried dispatched work with no `Task:` trailer because the
orchestrator had "just fixed it" inline; four adversarial probes were
prose nobody could re-run; the scaffold overwrote an adopting repo's
`hooks.json`. Each of those is cheap at the wave it happened and
expensive at ship, where every fix is a code change after the final blind
run and reopens the records-only claim of the acceptance report.

Two corollaries. Orchestrator-inline work cannot be papered over: the
only repair is a user-run history rewrite plus an honest
`agent_id: orchestrator-inline` entry in `dispatch[]`. And a reviewer's
disposition must separate "done" from "scheduled": a sentence in the
completed tense for an action that lives in the next commit was judged a
fatal incorrect-fact twice (R25-C1, R28-C1).

Known gap carried forward: `push.dispatch-covers-tasks` classifies the
scaffold's own `.codex/hooks/contract/` copy as gate work, while
`changed_paths` exempts it — a pure copy refresh needs a trailer until the
two exemption sets are aligned. The intent status grammar in
`loom-code/contract/manifest.yaml` (`open | confirmed | withdrawn`) also
lacks the `closed <date> — PR #<N>` form the ship station writes.
