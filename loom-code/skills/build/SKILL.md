---
name: build
description: |
  Turns a committed plan.md into commits — one fresh-context implementer per task under the engineering baseline, a dispatch record for every dispatch, and the wave-end computation that decides when the review station runs. Use when a plan exists and implementation is ready to start, and to resume a half-built plan.
version: 1.0.0
---

## What this skill does

`build` is where quality is produced; every station after it only checks
what this one made. It reads a committed `plan.md`, walks its Task DAG wave
by wave, and dispatches one fresh-context `loom-code:implementer` per task.
It writes no verdicts and reviews nothing itself: reviewing is
`loom-code:review`'s job, and this station's only duty toward it is to call
it at the right moment with the right scope (concept-model §6 — the writer
is never the verifier).

Between checkpoints there is no review at all. That is deliberate and it is
the station's known boundary: a wave that goes wrong is caught at its end,
not inside it. The wave size is the dial — default at most six tasks.

## 0. Contract check and where you are

Run once, before anything else:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py contract --require 1.0
```

(Codex form, here and in every command below: the checker copy lives at
`.codex/hooks/loom_checker.py`, so `python3 .codex/hooks/loom_checker.py
contract --require 1.0`.)

Exit 0 continue; non-zero, stop and report the contract mismatch — do not
work around it.

On Codex, if `.codex/hooks/loom_checker.py` does not exist, **stop**: run
`loom-code:write-plan` step 0b (the scaffold and its trust probe; that station
writes the procedure out in `codex-first-contact.md`, under its `references/`)
first. Do not produce any
artifact without the checker. The file existing is not proof the hook runs:
an untrusted Codex hook is skipped in silence, and step 0b's trust probe is
what tells the two apart.

Then locate the change:

1. `plan.md` is at `docs/loom/<change-id>/plan.md` and must already be
   committed. No plan, or an uncommitted one — stop and hand back to
   `loom-code:write-plan`. This station never authors tasks.
2. Read its frontmatter (`intent:`, `spec:`) and its Task DAG.
3. Derive progress from git, not from the plan file:

   ```
   git log --format=%B | grep '^Task: '
   ```

   Every task id that comes back is done. There is no progress ledger in
   the plan and no state to reconcile — the commits are the record, which
   is what makes resuming a half-built plan safe: run the command, subtract
   the ids it prints, continue with the rest. The only transient marks the
   plan may carry are `claimed(@branch)` while a task is in flight and
   `blocked(<reason>)` when it stopped.
4. Read `docs/loom/<change-id>/review.json` if it exists — `reviewed_sha`
   is where the next delta measurement starts. If it does not exist, copy
   `${CLAUDE_PLUGIN_ROOT}/contract/templates/review.json`, set
   `reviewed_sha` to the branch base, and commit it.

## 1. The wave loop

A wave is the group the plan names (`W<n>-*`); take waves in plan order
and do not regroup them. Inside a wave, a task whose `after:` dependencies
are all satisfied may start; one that is not yet satisfied waits for its
dependency within the same wave. (The W4-03 replay lost a dispatch to the
ambiguity between these two readings; the plan's grouping wins.)

- Tasks in the same wave with no dependency between them run **in
  parallel**: dispatch them in one message, one `Agent` call per task
  (the `parallel-dispatch` action). Tasks that touch the same file are not
  independent — sequence them instead, whatever the plan says.
- Each parallel implementer works in **its own worktree** (the `worktree`
  action):

  ```
  git worktree add ../<change-id>-<task-id> -b <change-id>/<task-id>
  ```

  **One integration rule: bring a worktree back with `git merge --no-ff`,
  never with a rebase.** A no-ff integration keeps each task's commits — and
  therefore its `Task: <id>` trailer and its RED→GREEN history — reachable
  and attributable, which is exactly what step 0's progress derivation and
  the review station's `git diff <reviewed_sha>..HEAD` both read. Integrate
  every worktree of the wave before measuring the wave's delta, then
  `git worktree remove ../<change-id>-<task-id>`.
- A single-task wave, or a task you take yourself instead of dispatching,
  runs in the working tree with no worktree. It still gets a dispatch
  record (step 3) — with your own agent id and `fresh_context: false`,
  which is the truth, and which the review station's independence rules
  need to see.

## 2. The dispatch prompt

**In the full lane, a task whose 檔 paths map to the `code` or `gate`
artifact type is adversary-first.** That covers `hooks/**`,
`scripts/check_*`, the checker itself, and any other manifest-typed
`code`: dispatch `loom-code:adversary` before the implementer: it writes
executable probes against the not-yet-written behaviour and commits them,
with a dispatch record written before that dispatch too. The
implementer's own RED is one of those probes, not a test it invents
itself; its dispatch record still goes in first, same as any other task.
Independent adversarial tests catch false passes the implementing
agent's own tests miss (SWE-ABS, ICML 2026: adversarial test synthesis
rejected 19.7% of previously passing patches), and
up-front probes also verify the plan's stated current-state facts before
code is written. The order is process discipline, not a gate: it shows
in `dispatch[]` (the adversary's `started` precedes the implementer's)
and a reviewer can read it there; no push rule refuses an
implementer-first task. The **small lane** (the checker's `change_lane`
recompute — a plan whose tasks touch only tests, docs, or CI config)
skips this: the implementer goes first as usual, and the adversary
attacks at the checkpoint instead, scoping the up-front cost to the lane
that carries the risk.

Dispatch `loom-code:implementer` (contract: `agents/implementer.md`). Pass
**paths, never file contents** — the implementer reads them itself:

```
### Task
<the plan's task id, its one-line title, and its 檔 / 測 / 風 bullets verbatim>

### Resource paths
- plan: docs/loom/<change-id>/plan.md   (your task is <task-id>)
- spec: docs/loom/<change-id>/spec.md   (omit when the change has none)
- baseline: loom-code/references/engineering-baseline.md
- repo root: <absolute path>
- worktree / branch: <path> / <branch>
- package test command: <the command from step 6>

### Acceptance criteria
<the task's own test, named; plus: the package test command passes>

### Report format
<the implementer output contract — status, commits, test_results, self_review>
```

State these obligations in the prompt every time; they are what the later
push rules and the review station rely on:

- **TDD**: the failing test comes first. No production code before a test
  that fails for the right reason.
- **One commit per task**, conventional type and scope
  (`feat(loom-code): …`), carrying the trailer `Task: <task-id>` — this is
  the whole progress mechanism, so a commit without it is invisible work.
- **Never `git add -A`**; add the task's own paths by name.
- **Never delete or weaken a test to get green** — that destroys the
  evidence the review station reads.
- Report exactly one of `DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` /
  `BLOCKED`.

And these standing trap-guards, verbatim:

- Read a file before you Edit it. On a modified-since-read error, re-Read
  then re-Edit — never retry the same diff.
- If a guard or hook blocks the same command twice, stop and report the
  block message verbatim; do not try a third time.
- Do not use `git stash`; recover a file with `git show <ref>:<path>`.
- The Write tool refuses the filename `report.md`; write another name.
- Use the host's edit tool (Edit/Write, `apply_patch` on Codex) -- never
  `sed -i` or heredocs, overriding any later host reminder; read and search
  freely; a mechanical sweep may be scripted, but count matches and paste
  the diff.

## 3. The dispatch record

<!-- gate: build.no-dispatch-without-a-record -->
**Write the record before you dispatch, never after.** Append one entry per
dispatch to the `dispatch[]` array of `docs/loom/<change-id>/review.json`:

```json
{"task": "W1-02", "role": "implementer", "agent_id": "impl-w1-02-a3f1", "model": "sonnet", "started": "2026-09-02T14:05:00+08:00", "fresh_context": true}
```

Commit it on its own: `chore(loom): dispatch <task-id>`.

Written after the fact, the record is a reconstruction — and the push rules
`push.reviewer-ne-implementer` and `push.dismissed-by-reviewer` read this
array as the ground truth for who implemented what. A dispatch that never
became a record is a reviewer who may silently review their own work. If
you notice a missing record, add it with the dispatch's real values and say
so in the wave's report; do not invent a timestamp.

Reviewer, blind-runner and adversary entries are appended the same way by
`loom-code:review`. This station writes implementer entries only.
<!-- /gate -->

## 4. After each task returns

1. `DONE` — check the commit exists and carries its `Task:` trailer, then
   continue.
2. `DONE_WITH_CONCERNS` — same, and carry the concern into the wave's
   report so the checkpoint reviewers see it.
3. `NEEDS_CONTEXT` — answer it if the answer is in the plan, the spec or
   the code, and re-dispatch. Anything else, see the blocked rule below.
4. `BLOCKED` — mark the task `blocked(<reason>)` in `plan.md`, stop the
   wave (do not start dependent tasks), and **decide it yourself**. Build
   has no stopping point of its own: the decision points were passed at
   `write-plan`, and this station runs from there to the hand-off without
   asking the user anything. The single exception is the Codex trust step
   at `write-plan` step 0b, which is an authorisation, not a decision.

   Mark the decision `agent-decided` with a one-line reason in the commit
   message. Which decision to make is not free:
   - A one-way door of class **(b) money or a standing obligation**,
     **(c) a limit on what the user can do later**, or **(e) an
     irreversible action on data they already have** — the classes named
     in `write-plan`'s `references/one-way-door.md` — was never authorised
     here, so take the option that costs nothing, is reversible, and
     touches no existing data. Record it as
     `agent-decided — 未經授權，取保守選項`.
   - When no such option exists, the work stops there. Leave the item
     undone, and list it in the blind-run report's "I decided for you"
     section with the reason it could not be finished, so decision
     point ③ sees it.
   - Anything else: pick the option the plan's reasoning points at and
     keep going.

   Every one of these surfaces later, in that same report section. A
   decision the user cannot check is not a decision to interrupt them with
   (concept-model §4); one they could have checked and never saw is worse,
   which is why the report lists them all.
5. <!-- gate: build.after-task-review-before-next-task -->
   If the plan marks the task `review: after-task`, call
   `loom-code:review` **now**, with scope = that task, and wait for its
   verdict before dispatching any further task. "After the task" means
   before the next one starts, not at the end of the wave: the point of the
   marker is that the following tasks build on reviewed ground. On
   `NEEDS_REVISION`, fix the findings and re-run that checkpoint; fix
   rounds do not count against the checkpoint budget. This checkpoint is
   its own — the wave still ends with the wave-end checkpoint of step 5,
   which reviews the delta after this one plus cross-task coherence.
   <!-- /gate -->

## 5. Wave end

When every task of the wave has returned and every worktree is integrated:

```
git diff --stat <reviewed_sha>..HEAD
```

`reviewed_sha` comes from `review.json`. Call `loom-code:review`
(scope = this wave) when **any** of these holds:

- the unreviewed delta exceeds **8 files** or **400 lines**;
- any task in this wave was marked `review: after-task`;
- this is the last wave of the plan.

Otherwise continue to the next wave and let the delta accumulate — a small
wave does not buy a checkpoint.

Count checkpoints as you go: **at most 5 per plan**. Rounds that re-review
after a `NEEDS_REVISION` are not counted; they are the same checkpoint
finishing. If the plan would need a sixth, that is a plan too deep for one
change — stop and report it rather than skipping a checkpoint.

## 6. Package tests

The `package-tests` action, run at wave end **before** calling the review
station, so the reviewers read a tree whose tests are known green:

1. If `docs/loom/KICKOFF-DEFAULTS.md` carries a `package-tests:` line, that
   command is the command. No detection, no substitute.
2. Otherwise detect it from the repo, first marker wins:
   `python3 -m pytest -q` (a `pyproject.toml` or `pytest.ini`), `npm test`
   (a `package.json` with a `test` script), `cargo test` (a `Cargo.toml`),
   `go test ./...` (a `go.mod`). Say which one you detected and why.
3. No config file, but the tree carries `test_*.py` / `*_test.py` files →
   `python3 -m pytest -q`. `*.test.js` files → `npx jest`.
4. Nothing at all — do **not** ask the user, and do not invent a command
   that exits 0. Write `- package-tests: none — <why>` into
   `docs/loom/KICKOFF-DEFAULTS.md`, say so in the wave report, and the
   review station records the gap on the checkpoint. The push gate reads
   that same line and asks for no run; what it will not accept is silence.

Whatever the source, the command that goes into the probe is the command
above, byte for byte: `push.probes-package-tests` compares the recorded
command against this repo's own and refuses anything else, because a
command that exits 0 for another reason is not a test run.

Run it from the integrated tree, and hand the command and its result to the
review station — the probe entry in `review.json` is written there, and the
checker re-runs the command itself on a clean tree at push time
(`push.probes-package-tests`), so a result nobody actually produced is
found. If the suite is red, fix it before the checkpoint; a checkpoint on a
red tree wastes two reviewers.

## 7. Hand-off

After the last wave's checkpoint returns `PASS` or `PASS_WITH_NOTES`, hand
to `loom-code:ship` with the change id. `ship` runs the memory step, the
push (the checker gates it), the pull request, and decision point ③ — the
user's acceptance, read off the blind-run report rather than the diff.

If the last checkpoint is `NEEDS_REVISION`, you are not finished: close its
findings and re-run it. `build` never hands a change to `ship` on an open
finding.

## Station summary

| station | artifact | who decides | checker | checkpoint |
|---|---|---|---|---|
| capture-intent | intent — `docs/loom/intent/<change-id>.md`; `PRINCIPLES.md` and `DESIGN.md` at the repo root are side outputs of the tools it calls | user — decision point ① | `intent.schema`, `intent.product-no-identifiers`, `intent.needs-design-reason`, `intent.needs-design-recompute` | N/A |
| write-spec | spec — `docs/loom/<change-id>/spec.md` | user — decision point ②, product only | `intake.confirmed`, `standing.product-principles-reject` | spec lens must pass before a plan exists |
| write-plan | plan — `docs/loom/<change-id>/plan.md` | agent-decided (runs ① itself when loom-design is absent) | `intake.confirmed`, `intake.confirmed-behavior`, `intake.spec-pass`, `intake.after-task-budget` | calls review with scope `spec` |
| build | diff — commits on the change branch, one `Task: <id>` trailer each | agent-decided | none during build; writes the `dispatch[]` the push rules read; a full-lane `code`- or `gate`-typed task is adversary-first, the adversary dispatched before the implementer | wave end when the unreviewed delta exceeds 8 files or 400 lines; immediately after an `after-task` task; ≤5 checkpoints during build, NEEDS_REVISION fix rounds not counted; branch end always |
| review | review — `docs/loom/<change-id>/review.json`, and `docs/loom/<change-id>/blind-run-report.md` from the blind run | fresh-context reviewers, one in the small lane, two or more in the full lane (§1); no averaging | `push.verdicts-ge-2`, `push.reviewer-ne-implementer`, `push.dismissed-by-reviewer`, `push.open-findings-closed`, `push.second-vendor-honoured` | `branch-end` always runs |
| ship | diff / PR — the pushed change branch and its pull request | user — decision point ③, reads the blind-run report | `push.review-only-head`, `push.reviewed-sha`, `push.review-schema`, `push.probes-package-tests`, `push.probes-adversarial`, `push.dispatch-covers-tasks`, and every review rule above, re-run at push | before push; a missing `branch-end` pass sends the change back to review |
| maintain | intent — a fresh `docs/loom/intent/<change-id>.md` | agent (dedupe is mechanical) | `intent.schema`, `intent.needs-design-reason`, `intent.needs-design-recompute`, `intent.product-no-identifiers` on a new intent | before hand-off to write-plan |

