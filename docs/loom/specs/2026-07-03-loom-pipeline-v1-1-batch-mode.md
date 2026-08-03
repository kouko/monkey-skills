# loom-pipeline v1.1 — batch implementation mode (brief)

> Brainstorming brief (loom-code:brainstorming), 2026-07-03. Consumed by
> writing-plans. Fork decisions made with kouko in-session; see §Decision.

## Problem

kouko wants to discuss and freeze multiple change specs interactively, then
have the pipeline implement them **unattended as a batch** — N PR branches +
N ledgers waiting for human review, merge always human. The original
requirement (2026-07-03, verbatim): 「我還是有點想要那種 先討論多個backlog
之後自動實作 的自動化 讓我可以白天討論規格 晚上agent自動實作」 with the
clarification that day/night is a METAPHOR — the capability is
time-agnostic, no scheduler.

v1 of loom-pipeline already runs one change's Segment 3 end-to-end, but each
run needs a human to collect run inputs, confirm cost policy, and invoke the
Workflow call. The job to be done: move every per-change human decision to
**freeze time**, so the run stretch needs no human at all.

## Users

kouko, solo, on a Claude Code host with the Workflow primitive. Job story:
*When I have several changes whose spec is validator-clean and whose plan is
written, I want to queue them and walk away, so I can come back to N
reviewable PR branches instead of babysitting N interactive runs.*

Failure tolerance: a change failing mid-batch must NOT stall the queue
(failure isolates to its item); a dead session must NOT lose batch progress
(resumable from durable state by a fresh session).

## Smallest End State

Four deliverables, no driver changes:

1. **Queue convention** — one human-editable file in the target project
   (working name `docs/loom/QUEUE.md`): ordered entries of
   `change-id / planPath / pre-authorized budgets / model policy / status`.
   This file is gate (c) moved to freeze time AND the durable batch state.
2. **`loom-pipeline/scripts/batch_queue.py`** (+ mirror test, TDD) — a
   deterministic bookkeeping CLI the main agent calls each iteration:
   - `next` — return the next QUEUED entry after verifying the freeze
     predicate (loom-spec validator exit-0 **and** planPath exists), create
     its worktree + branch, emit the ready-to-use Workflow args as JSON;
     ineligible entries are marked SKIPPED loudly, never silently.
   - `mark <change-id> done|failed [--run-id …]` — write back status.
   - `status` — one-screen queue overview (what a fresh session reads first).
3. **SKILL.md §Batch mode** — the loop contract for the main agent:
   one `batch_queue.py next` → one `Workflow({segment: 3, …})` → one
   `batch_queue.py mark` → repeat until the queue is empty. The main agent
   is **dispatcher-only**: it never parses the queue file, never composes
   git commands, never diagnoses failures mid-batch — those are script-owned
   or deferred to the human report at the end.
4. **README update** — §Committed next flips to a documented §Batch mode.

Explicitly SEQUENTIAL: one change at a time. Parallel variant (v1.1.x) stays
parked with its git-commit dispatch-lock re-trigger (README §Parked items).

## Current State Evidence

- **Forward**: entry is `using-loom-pipeline/SKILL.md` §Invocation — one
  Workflow call per segment, never one for the whole run
  (`loom-pipeline/skills/using-loom-pipeline/SKILL.md:82-98`); Segment 3's
  entry point is `runSegment3(args)` requiring `planPath`
  (`loom-pipeline/scripts/driver_50_seg3.js:289`, guard at `:72`); its
  terminal state is PR-ready branch + ledger, never a merge
  (`driver_50_seg3.js:26-28`).
- **Reverse**: the shipped asset
  `skills/using-loom-pipeline/assets/loom-pipeline.js` is GENERATED —
  canonical SSOT is `loom-pipeline/scripts/driver_NN_*.js`, concatenated by
  `loom-pipeline/scripts/build_driver.py:26-36` (banner forbids hand-edits;
  drift test enforces byte-identity). v1.1 touches NO driver module, so no
  rebuild is needed; `batch_queue.py` is a sibling host-side script, outside
  the concat contract.
- **Error**: the driver's fail-loud contract is `guardArgs`
  (`loom-pipeline/scripts/driver_10_guard.js:15` — missing/`"undefined"`
  inputs throw; F4 lesson). Batch mode inherits it per invocation; the queue
  script adds the freeze predicate as its own fail-loud layer (ineligible →
  SKIPPED + reason, exit non-zero on malformed queue file).
- **Data**: per-run budget is already a per-invocation delta baseline
  (`loom-pipeline/scripts/driver_90_main.js:73-104` — `budget.spent()` is
  turn-scoped, so each run captures a baseline), which makes
  `budgets.run` a natural **per-change** cap under one-invocation-per-change;
  ledgers land at `<projectPath>/docs/loom/<changeId>/pipeline-ledger.md`
  (`loom-pipeline/scripts/driver_60_ledger.js:212`), so N changes → N
  ledgers with zero new convention.
- **Boundary**: freeze predicate reuses the Segment-2 validator path
  convention `<skillsRoot>/loom-spec/scripts/validate_spec_output.py
  <changeDir>` (`loom-pipeline/scripts/driver_40_seg2.js:109,127`);
  `Workflow`'s `resumeFromRunId` is **same-session only** (host tool
  contract), which is why durable batch state lives in the queue file, not
  in Workflow journals; worktree/branch creation happens in the main
  session's script via `git -C <projectPath> worktree add …` (driver layer
  has no filesystem/git primitive — every read routes through `agent()`,
  `driver_50_seg3.js:220-222`).

Evidence paths appendix:
`loom-pipeline/skills/using-loom-pipeline/SKILL.md`,
`loom-pipeline/scripts/driver_10_guard.js`,
`loom-pipeline/scripts/driver_40_seg2.js`,
`loom-pipeline/scripts/driver_50_seg3.js`,
`loom-pipeline/scripts/driver_60_ledger.js`,
`loom-pipeline/scripts/driver_90_main.js`,
`loom-pipeline/scripts/build_driver.py`,
`docs/loom/research/2026-06-17-plan-frozen-auto-advance-orchestration.md`,
`docs/loom/research/2026-07-03-pipeline-driver-industry-research.md`.

## Decision

Build batch mode as **a conductor-layer loop with script-owned bookkeeping**
("A + script-ified bookkeeping", kouko sign-off in-session 2026-07-03):

- The **loop lives in the main session** (conductor skill), preserving the
  documented one-Workflow-invocation-per-segment rule — extended naturally
  to one invocation per (change × segment 3).
- Everything deterministic in the loop is **script-owned**
  (`batch_queue.py`): queue parsing, freeze verification, worktree/branch
  creation, status write-back. The main agent's only irreducible jobs are
  (1) issuing the Workflow tool call and (2) the end-of-batch human report.
  Rationale (kouko, in-session): the main agent's context is the batch's
  scarcest resource and every mid-loop improvisation is an error site
  (F4/F5 class) — move all non-judgment out of the main agent.
- **Freeze predicate = loom-spec validator exit-0 + plan written.** No
  segment 2.5. This applies the documented scope decision verbatim:
  "freeze point = the plan (atomic tasks + RED/GREEN); stop point = PR-open
  (human merges)"
  (`docs/loom/research/2026-06-17-plan-frozen-auto-advance-orchestration.md:4-6`).
  writing-plans stays interactive, done before freezing.
- **Failure policy: isolate and continue.** A failed change is marked
  FAILED with its runId and the queue moves on; no mid-batch diagnosis. The
  end-of-batch report surfaces failures for the human (the 2026-06-17
  research: the load-bearing piece is the STOP/ESCALATE trigger, not the
  plumbing).
- Human gates: (a) change-id minting and (c) cost policy move to freeze
  time (queue-entry authoring); (b) product forks cannot occur (spec+plan
  frozen); (d) final merge unchanged — the pipeline never merges.

We will NOT build: a driver batch segment (`args.queue` — see Alternatives),
a `/goal`/`/loop` supervision shell, a scheduler, auto-merge, parallel
execution, any change to the four station plugins, any new driver module.

## Alternatives Considered

1. **Driver-internal batch segment** (one Workflow invocation loops the
   whole queue in-script). Rejected: violates the documented
   one-invocation-per-segment rule; the driver layer has no git primitive,
   so worktree creation would be delegated to agents (new error surface);
   per-change budget caps must be re-invented as in-script delta
   accounting; `resumeFromRunId` is same-session only, so its single-journal
   resume advantage dies with the session — exactly the failure batch mode
   must survive.
2. **External orchestrator runtime** (LangGraph/MemorySaver-style
   checkpointed graph app). Rejected: a new runtime to own and babysit;
   crutch-class per the 2026-06-17 research ("build the stop rule; don't
   build the brain"); our durable state is a human-readable repo file
   instead of a checkpointer DB.
3. **`/goal` (or `/loop`) supervision shell over the loop.** Dropped: `/goal`
   does not exist on the current host (spike finding 2026-07-03; only
   `/loop` exists), and the conductor-layer loop is already unattended —
   Workflow completion re-invokes the main session; no shell needed.
4. **Segment 2.5 (plan station in the pipeline).** Rejected: contradicts the
   documented freeze-point decision (plan is authored interactively before
   freeze); would move a judgment-heavy interactive step into the unattended
   stretch, exactly where the research says failures concentrate.

Industry grounding (EN+JA convergent, no counter-evidence found):
worktree-per-task isolation + task queue + PR-per-task with human merge is
the shipped mainstream shape — EN: Mike Mason "Coherence Through
Orchestration" (mikemason.ca, 2026-01), Ralph-loop batch pattern
(beyond.addy.ie/2026-trends); JA: git worktree 並列実行ハンズオン
(qiita.com/kai_kou), VibeKanban × worktree タスク並列
(zenn.dev/coconala). The unattended envelope (freeze plan → auto-run → stop
at PR) is the verified conclusion of
`docs/loom/research/2026-06-17-plan-frozen-auto-advance-orchestration.md`.

## What Becomes Obsolete

- `loom-pipeline/README.md` §Committed next (v1.1) — flips from commitment
  to documentation in the same change.
- `docs/loom/BACKLOG.md` v1.1 entry — deleted on ship (completed items are
  deleted, not archived).
- Nothing else; purely-additive is acknowledged: the batch loop was
  committed in the v1 brief and demanded by the user requirement.

## Open Questions

1. **Queue file exact format** — markdown table vs entry blocks; needs to be
   trivially script-parsable AND pleasant to hand-edit at freeze time.
   → writing-plans decides; test-first via `batch_queue.py`'s parser tests.
2. **Worktree/branch naming** — adopt `loom-code:using-git-worktrees`
   conventions (and its known bash-guard quirk with `git -C`) vs a
   pipeline-local `loom/<change-id>` scheme. → writing-plans decides.
3. **Circuit breaker** — should N consecutive FAILED items halt the queue
   (systemic-failure signal, e.g. broken base branch) instead of grinding
   through? Default proposal: halt after 2 consecutive failures, report.
   → confirm during writing-plans.
