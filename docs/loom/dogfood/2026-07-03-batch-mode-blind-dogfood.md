# loom-pipeline v1.1 batch mode — blind dogfood (pre-release)

> 2026-07-03, branch `feat/loom-pipeline-v1-1-batch-mode` (pre-merge).
> Method: a **Haiku** subagent, blind — its only manual was
> `using-loom-pipeline/SKILL.md` §Batch mode plus two paths (target
> project, skillsRoot). Forbidden from reading `batch_queue.py` source.
> The weak tier is deliberate: if Haiku can follow the doc literally,
> the doc carries the contract; anywhere it guesses is a doc hole.

## Fixture

Toy git project with a 2-entry `docs/loom/QUEUE.toml`:

| entry | freeze state | expected path |
|---|---|---|
| `note-color` | frozen — change folder passes the REAL loom-spec validator (exit 0), plan committed | dispatch |
| `dark-mode` | not frozen — plan file absent | loud skip, queue continues |

One deviation by design: the Workflow step was simulated (run treated
as succeeded, `wf-dogfood-1`) — **Segment 3's real interior stays
reserved for the first real change** (BACKLOG decision 2026-07-04:
don't burn the first live seg3 on a toy).

## Result: PASS — friction log EMPTY

- Loop followed literally: `next` → (Workflow simulated) → `mark
  note-color done --project … --run-id wf-dogfood-1` → `next` (skips
  dark-mode with the predicate's reason, then `{"done": true}`) →
  `status` end-of-batch report. Every flag correct on first try —
  including `mark --project`, the exact flag whose omission the
  whole-branch review caught in the doc one commit earlier.
- Emitted Workflow args: all 8 fields (`segment/changeId/projectPath/
  planPath/budgets/models/skillsRoot/branch`), `projectPath` = the
  worktree, `planPath` inside the worktree — matches the driver
  contract (`driver_10_guard.js` / `driver_50_seg3.js`).
- Disk state verified by the orchestrator (not taken from the agent's
  report): worktree `.worktrees/loom-note-color` on branch
  `loom/note-color`; `queue-state.json` records DONE + runId + branch
  + worktree for note-color, SKIPPED + reason for dark-mode.
- Cost: single Haiku agent, ~37k tokens, 13 tool calls, ~67s.

## Not covered (deliberate)

- Real Segment 3 dispatch through the driver asset (→ first real
  change; BACKLOG "Segment-3 first live run").
- Circuit-breaker HALT path (unit-tested; not exercised end-to-end
  here — would need two seeded FAILED outcomes).
- Resume-after-session-death (queue file + state file are the durable
  carriers by design; exercised only as `status` cold-read).
