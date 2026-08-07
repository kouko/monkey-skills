---
name: a-composed-cli-hands-back-only-the-fields-it-dispatches
description: A routine that composes another tool's CLI can only act on the fields that tool's own dispatch payload emits — writing a step against a field the payload never carries (because the field exists in the human-facing source of record, not in the machine handoff) produces a document that reads correctly and cannot be executed, and when that step is a fail-closed safety guard the improvised input makes it pass instead of refuse
type: gotcha
origin: 2026-08-07 whole-branch review of feat/u1-nightly-phase2-loop — ROUTINE.md Step 4, both docs-reviewer arms independently
---

The Phase 2 execution loop's brief chose to COMPOSE
`loom-pipeline/scripts/batch_queue.py` rather than duplicate its queue and
state machinery — the right call, and the code honors it. But the routine
document written on top of it specified its scope guard as
`requires_real_agent_surface(<picked entry's description>)`, and no
`description` reaches the executor: `_dispatch_entry` builds exactly eight
keys (`segment`, `changeId`, `projectPath`, `planPath`, `budgets`, `models`,
`skillsRoot`, `branch`), and the branch's own entry-authoring helper emitted
only three fields. Note the precise shape of the wall — `load_queue` does
NOT reject an unknown key, so a `description` added to `QUEUE.toml` parses
fine and then goes nowhere, because the payload is assembled from a fixed
key set downstream. "It was accepted" and "it arrived" are different
questions, and only the second one matters. The description was real,
but it lived in the campaign doc's checklist line — the human-facing source
of record — which the composed CLI has no reason to carry.

Two things make this worse than an ordinary omission:

- **It reads correctly.** Every other claim in that document verified
  clean against `batch_queue.py`: every subcommand shape it drives, the exit-3 HALT
  semantics, the `loom/<changeId>` branch model, the payload key list. The
  defect is in what the prose assumed was available, not in what it said.
- **The guard fails OPEN under improvisation.** An unattended executor
  reaching that step has exactly one string in hand (`changeId`, e.g.
  `"B1"`), and `requires_real_agent_surface("B1")` returns `False` — so
  the metered real-agent item the guard exists to refuse gets dispatched.
  A fail-closed guard handed a guessed input is a guard that passes.

A second-order version of the same shape sat one step later: the guard's
skip path said "leave the entry for a human", but `next` had already
written `RUNNING` and created the worktree, so simply exiting stranded the
entry and made the next run's `reconcile` report a false `SUSPECT`.
Composing a tool means inheriting the side effects its earlier calls
already committed — the exit path has to name a real transition
(`force-fail` here; `reset` would requeue and re-refuse forever).

**What to do**: when a step consumes a field, trace it to the emitter
before writing the step — and if the field lives in a human-facing
document rather than the machine handoff, make reading it an explicit,
named, testable call. Related: [[a-correction-issued-in-a-dispatch-packet-evaporates]].
