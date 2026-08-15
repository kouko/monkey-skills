# Phase 2 loop — execution-stage routine

The exact, ordered checklist a **scheduled / unattended** invocation follows
to execute **one** already-frozen Phase 2 backlog item. This document is the
whole contract for the execution stage: it dispatches loom-code SDD
execution (loom-design batch mode's **segment 3**) against a plan a human
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
python3 loom-design/scripts/pipeline/batch_queue.py reconcile --project <root>
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
python3 loom-design/scripts/pipeline/batch_queue.py next --project <root> --skills-root <root>
```

`next` re-runs reconcile internally, enforces the freeze predicate
(`check_frozen`) and the circuit breaker, then either dispatches or reports
no work. Read its exit code and stdout:

- **Exit code `3` — circuit breaker HALT.** Two consecutive `FAILED` terminal
  entries tripped the breaker. **STOP and leave the batch for human review.**
  Do NOT override. This unattended routine MUST NOT pass `--override-halt` —
  a systemic-failure signal is exactly the case a human must see.
- **stdout `{"done": true}`** (or `{"done": false, "non_terminal": [...]}`
  listing the entries still in flight, i.e. nothing this scan could
  dispatch) — **exit as a no-op.** There is no frozen, queued work to run.
- **stdout a dispatch payload** (a JSON object with `segment`, `changeId`,
  `projectPath`, `planPath`, `budgets`, `models`, `skillsRoot`, `branch`) —
  this is the entry to execute. `next` has already recorded it `RUNNING` and
  readied its isolated worktree + `loom/<changeId>` branch. Continue.
- **Any other nonzero exit** (`1` — a `QueueError`, a malformed
  `QUEUE.toml`, an unreadable state file) — **STOP and exit.** There is no
  dispatch payload, so there is nothing to guard, dispatch, or mark; falling
  through to Step 4 would scope-guard a payload that does not exist. Leave
  stderr for the human.

**Tooling-failure rule, applying to every `batch_queue.py` call in this
document (Steps 2, 3, 4, 6 and 8 — Step 4 calls `force-fail` on both of its
exit paths).** A nonzero exit from the CLI itself — as
opposed to a failure of the dispatched item, which Step 8 covers — means this
invocation STOPS where it stands. Do not retry the command, do not proceed to
the next step, and do not invent a compensating transition.

**What "STOP" leaves behind differs by step, and both shapes are correct.**
The dividing line is whether `next` already claimed an entry. Steps 2 and 3
exit owning nothing — `next` writes `RUNNING` only when it dispatches, so a
nonzero exit there leaves no entry to release, which is what Step 3's own
bullet means by "there is nothing to guard, dispatch, or mark". Step 4 is the
first step that exits holding a claimed entry, and both of its exits must
release it: a `RUNNING` entry with no run evidence is a false anomaly that
`reconcile` will report as `SUSPECT` for a human who has nothing to look at.

At Steps 6 and 8 a run exists — in flight or finished — so exiting with the
entry still `RUNNING` is the intended outcome, not a leak: it gets surfaced to
a human either way, and the evidence is what makes that surfacing useful.
(Mechanism, for the reader who wants it: after Step 6 succeeded there is a
`runId`, so `reconcile` reads the Workflow record and flags
`SUSPECT-COMPLETE` on a completed run; if Step 6 itself failed there is no
`runId`, so the entry is instead surfaced as stale after a grace window.
Either way a human sees it.) Never `force-fail` a live run to tidy the state;
the evidence is what a human needs.

If a `force-fail` release at Step 4 is itself what exits nonzero, stop there
too. The entry stays `RUNNING` with no `runId` and `reconcile` surfaces it as
stale — worse than a clean release, but safe, and not something this routine
may paper over with a second attempt.

## Step 4 — Scope guard on the picked entry

**Where the description comes from.** `next`'s dispatch payload carries no
description — `_dispatch_entry` builds exactly the eight keys listed in Step
3. Adding a `description` key to `QUEUE.toml` does not help either: it would
survive `load_queue` (which validates required fields and returns the raw
TOML dicts rather than rejecting unknown ones) but never reach the executor,
because the payload is built from a fixed key set. The campaign doc's own
Phase 2 checklist line is the description of record, and
`queue_entry.lookup_backlog_description` is the only supported way to read
it — it returns the item's head line plus its wrapped continuation lines,
because a signal the guard must catch can sit on a continuation line.

```
description = queue_entry.lookup_backlog_description(
    <changeId from the Step 3 payload>,
    Path("<root>/docs/dbt-wiki-quality-campaign.md"),
)
```

It raises `ValueError` when the id is not a Phase 2 checklist item. Release
the entry the same way the guard-`True` path below does — `force-fail <id>`
with the reason `"scope guard: no Phase 2 checklist entry for this id"` —
then journal one line per Step 9's single-line rule, using its
`- <id>: failed — <reason>` shape, and exit. **Do not simply exit here.**
Step 3's
tooling-failure rule does not apply: its justification is "there is no
dispatch payload, so there is nothing to guard, dispatch, or mark", and at
this point the payload exists and the entry is already `RUNNING`. Leaving it
would strand exactly the state the next section is about to argue against.

Never substitute another string for the description — passing `changeId`
itself, or an empty string, makes the guard return `False` and dispatches the
very item it exists to refuse.

(This calls `lookup_backlog_description`, NOT `propose_queue_entry` — the
authoring helper in the same module remains a planning-stage tool this stage
never runs.)

Then call `safety_gates.requires_real_agent_surface(description)`.

- If it returns `True`, this loop MUST NOT drive the item unattended (it
  gestures at the metered real-headless-agent eval surface — W1/G1/G2/G3).
  Do the following, in this order, and then **exit**:
  1. Release the queue entry — Step 3's `next` already recorded it `RUNNING`,
     so simply exiting would strand a `RUNNING` entry with no run evidence
     and make Step 2's `reconcile` report a false `SUSPECT` on the next
     invocation:
     ```
     python3 loom-design/scripts/pipeline/batch_queue.py force-fail <id> \
       --project <root> --reason "scope guard: real-agent surface, needs human scoping"
     ```
     `force-fail` is the only valid transition out of `RUNNING` here (`reset`
     would requeue the item, and the next scheduled run would pick it up and
     refuse it again — a loop). The resulting `FAILED` counts toward the Step
     3 circuit breaker like any other, which is intended: two consecutive
     items needing human scoping SHOULD stop the loop and fetch a human.
  2. `journal_writer.append_journal_line(...)` — one line, per Step 9's
     single-line rule and its exact format.
  3. Do not dispatch. (The guard fails **closed** — an ambiguous description
     is refused, never guessed.)

  **Known residue, stated rather than hidden**: `force-fail` transitions
  queue state but does not tear down the `loom/<changeId>` worktree and
  branch `next` created (`batch_queue.py`'s `_teardown_worktree` is internal
  to its own skip path and exposed by no CLI verb). This routine does NOT
  remove them itself — that would violate its never-manage-branches boundary
  below. The worktree is left for the human the `FAILED` entry summons.

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
python3 loom-design/scripts/pipeline/batch_queue.py mark-running <id> \
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
mechanics here; that file is the single source of truth for **when** an
unattended run stops and escalates. It is not the source of truth for what
happens next: its stop contract ends at a PR-open this routine forbids
outright (see Hard boundaries), so the terminal bookkeeping below applies
instead.

**An escalation halt is a terminal outcome, not a third state.** Its
"stop-and-wait and emit why I stopped" ending presumes a reader who is by
definition absent here, so record it the same way any other failure is
recorded — Step 8's `mark <id> failed` with the halt reason, then Step 9's
one journal line. An unattended halt must never leave the entry `RUNNING`
with no journal line: that is indistinguishable from a crash.

## Step 8 — Mark the terminal outcome

When execution finishes, record the outcome:

```
python3 loom-design/scripts/pipeline/batch_queue.py mark <id> done --project <root>
```

or, on failure:

```
python3 loom-design/scripts/pipeline/batch_queue.py mark <id> failed \
  --project <root> --reason "<one-line reason>"
```

**Fail closed, never retry.** On any failure the routine marks the entry
`failed` and stops touching it — it does NOT re-dispatch, re-plan, or retry
the item within this or a later invocation. A `failed` entry waits for a
human; two consecutive failures trip the Step 3 circuit breaker by design.

## Step 9 — Narrate one campaign-journal line

Exactly **one** journal line is appended per invocation, whatever the outcome
— done, failed, escalation-halt, or either of Step 4's two early exits (the
scope-guard skip and the unknown-id `ValueError` release). Each of those exits
writes that invocation's one line, not an extra one: it calls this step's
helper with a shape from this step's list and then exits, so control never
reaches here twice.

```
journal_writer.append_journal_line(
    Path("<root>/docs/dbt-wiki-quality-campaign.md"), line
)
```

`line` MUST begin with `- ` — every entry in the target `## Journal` section
is a markdown list item, and `append_journal_line` inserts after the last
content line, so an unprefixed line is absorbed into the preceding bullet as
a lazy continuation instead of rendering as its own entry. Use one of:

```
- <id>: done
- <id>: failed — <reason>
- <id>: skipped, needs human scoping (real-agent surface)
```

This list is closed. The `failed` shape carries every non-`done`, non-skip
outcome, its `<reason>` being the same string passed to `mark … --reason` or
`force-fail … --reason` — an escalation halt and Step 4's unknown-id release
both land here. If an outcome ever arises that none of the three fit, that is
a gap in this document to report, not a line to invent.

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
