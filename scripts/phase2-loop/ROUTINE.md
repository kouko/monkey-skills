# Phase 2 loop — execution-stage routine

The exact, ordered checklist a **scheduled / unattended** invocation follows
to execute **one** already-frozen Phase 2 backlog item. This document is the
whole contract for the execution stage: it dispatches loom-code SDD
execution (loom-pipeline batch mode's **segment 3**) against a plan a human
has already written and a reviewer has already PASSed — nothing more.

> **Scope, stated once and enforced throughout.** This stage NEVER explores
> intent, NEVER writes or re-scopes a plan, and NEVER authors a queue entry.
> Those belong to the **planning stage** — a separate, interactive process
> (brainstorm → write plan → `Plan-document-reviewer verdict: PASS`) that
> this document does not describe and this routine does not run. In
> particular this routine NEVER calls `propose_queue_entry`
> (`scripts/phase2-loop/queue_entry.py`) — that helper drafts a `[[change]]`
> entry during the planning stage and is out of scope here. If the queue has
> no eligible frozen work, this routine does nothing; it does not go find
> more.

Source brief: `docs/loom/specs/2026-07-28-phase2-loop-execution-only.md`.
Plan: `docs/loom/plans/2026-07-28-phase2-loop-execution-only.md` (Task 3).

`<root>` below is the absolute path to this repo checkout (the `--project`
and `--skills-root` for a monkey-skills run are the same path).

---

## Step 1 — Kill switch (read-only)

Call `safety_gates.is_nightly_paused(Path("<root>/docs/loom/PHASE2_LOOP_PAUSED"))`.

- If it returns `True`, **exit immediately as a no-op.** Do nothing else.
- The routine only ever **READS** this sentinel. kouko toggles the pause by
  committing / removing `docs/loom/PHASE2_LOOP_PAUSED` (renamed from the old
  `docs/loom/NIGHTLY_PAUSED`); its git history is the audit log. This check
  MUST NOT create, move, or delete the file.

## Step 2 — Reconcile stranded prior runs FIRST

Before selecting or dispatching anything, run:

```
python3 loom-pipeline/scripts/batch_queue.py reconcile --project <root>
```

This scans every `RUNNING` entry left over from a prior invocation against
its Workflow record: it auto-transitions definitively `failed`/`killed`
entries to `FAILED`, and prints one line per entry it flags `SUSPECT` (stale,
no evidence) or `SUSPECT-COMPLETE` (wf-record says completed but never marked
done) to stderr. `SUSPECT` / `SUSPECT-COMPLETE` entries are **left for a
human** — do not force-transition them yourself. Running this first means a
dead prior run is cleared (or surfaced) before it can distort the circuit
breaker or the done-check below.

## Step 3 — Pick the next frozen entry

```
python3 loom-pipeline/scripts/batch_queue.py next --project <root> --skills-root <root>
```

`next` re-runs reconcile internally, enforces the freeze predicate
(`check_frozen`) and the circuit breaker, then either dispatches or reports
no work. Read its exit code and stdout:

- **Exit code `3` — circuit breaker HALT.** Two consecutive `FAILED` terminal
  entries tripped the breaker. **STOP and leave the batch for human review.**
  Do NOT override. This unattended routine MUST NOT pass `--override-halt` —
  a systemic-failure signal is exactly the case a human must see.
- **stdout `{"done": true}`** (or `{"done": false, "non_terminal": [...]}`
  listing only in-flight / non-eligible entries, i.e. nothing this scan could
  dispatch) — **exit as a no-op.** There is no frozen, queued work to run.
- **stdout a dispatch payload** (a JSON object with `segment`, `changeId`,
  `projectPath`, `planPath`, `budgets`, `models`, `skillsRoot`, `branch`) —
  this is the entry to execute. `next` has already recorded it `RUNNING` and
  readied its isolated worktree + `loom/<changeId>` branch. Continue.

## Step 4 — Scope guard on the picked entry

Call
`safety_gates.requires_real_agent_surface(<picked entry's description>)`.

- If it returns `True`, this loop MUST NOT drive the item unattended (it
  gestures at the metered real-headless-agent eval surface — W1/G1/G2/G3).
  Do the following and then **exit**:
  1. `append_journal_line(Path("<root>/docs/dbt-wiki-quality-campaign.md"),
     "<id>: skipped, needs human scoping (real-agent surface)")`
  2. Do not dispatch. Leave the entry for a human to scope. (The guard fails
     **closed** — an ambiguous description is refused, never guessed.)

## Step 5 — Dispatch segment 3 (execution only)

Call `Workflow()` using the args `next` printed **as-is** — pass its dispatch
payload through unchanged (`projectPath` is the worktree, `planPath` is
resolved inside it, `branch` is `loom/<changeId>`).

This is **loom-code SDD execution against an already-frozen plan** — segment
3 only. This routine does not explore intent and does not author or re-scope
a plan; the plan was frozen and reviewer-PASSed during the planning stage.
The routine drives the frozen plan forward; it does not decide what the plan
should be.

## Step 6 — Record RUNNING run metadata immediately

The moment `Workflow()` returns its run id and session directory, run:

```
python3 loom-pipeline/scripts/batch_queue.py mark-running <id> \
  --project <root> --run-id <runId> --session-dir <dir>
```

(`mark-running` requires the entry to already be `RUNNING` — `next` set that
in Step 3 — and requires both `--run-id` and `--session-dir`.) This closes
the gap where a crash between dispatch and this call would leave a `RUNNING`
entry with no run evidence for `reconcile` to judge.

## Step 7 — Unattended escalation ceiling

This routine runs with **no human present to pump the loop**, so its
escalation tolerance is one round tighter than an interactive run. Follow the
existing halt discipline documented at
`loom-code/skills/using-loom-code/references/continuous-mode.md` — its
"no human pumping → hand back slack one round earlier" precedent (the STOP
contract there). Do not invent a new threshold and do not restate its
mechanics here; that file is the single source of truth for when an
unattended run stops and escalates.

## Step 8 — Mark the terminal outcome

When execution finishes, record the outcome:

```
python3 loom-pipeline/scripts/batch_queue.py mark <id> done --project <root>
```

or, on failure:

```
python3 loom-pipeline/scripts/batch_queue.py mark <id> failed \
  --project <root> --reason "<one-line reason>"
```

**Fail closed, never retry.** On any failure the routine marks the entry
`failed` and stops touching it — it does NOT re-dispatch, re-plan, or retry
the item within this or a later invocation. A `failed` entry waits for a
human; two consecutive failures trip the Step 3 circuit breaker by design.

## Step 9 — Narrate one campaign-journal line

Regardless of pass / fail / skip, append exactly one human-readable summary
line:

```
append_journal_line(Path("<root>/docs/dbt-wiki-quality-campaign.md"), line)
```

where `line` is a single line such as `<id>: done` / `<id>: failed —
<reason>` / `<id>: skipped, needs human scoping`.

---

## Hard boundaries (always, no exception)

- **No version pre-bump.** This routine NEVER edits any `plugin.json` or any
  `VERSION` field, ever — not before, during, or after a run. Version /
  marketplace bookkeeping is human-owned and out of scope.
- **Never merge, never open a PR, never touch `main`.** The routine's job
  ends at whatever `batch_queue.py`'s own worktree/branch model produced:
  each queue entry gets its own isolated `loom/<changeId>` branch + worktree
  via `ensure_worktree`. This routine does NOT manage branches itself, does
  NOT merge, does NOT open a PR, and does NOT touch `main` or any other
  human-owned branch. A human reviews and merges on their own rhythm.
- **Only reads the kill switch.** `PHASE2_LOOP_PAUSED` is read, never
  written (Step 1).
- **Never authors a queue entry.** `propose_queue_entry` is a planning-stage
  tool; this execution-stage routine never calls it.
