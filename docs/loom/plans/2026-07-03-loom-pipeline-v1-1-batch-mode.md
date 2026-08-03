# Plan: loom-pipeline v1.1 — batch implementation mode

**Source brief**: docs/loom/specs/2026-07-03-loom-pipeline-v1-1-batch-mode.md
**Total tasks**: 13
**Critical-path depth**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-07-03 15:49)

## Settled open questions (brief §Open Questions → in-plan decisions)

1. **Queue file format = TOML** (`docs/loom/QUEUE.toml` in the target project).
   Rationale: stdlib `tomllib` parses it (CI pins Python 3.11 —
   `.github/workflows/loom-pipeline-ci.yml:56`), nested tables carry
   `budgets.perStation` naturally, and TOML stays pleasant to hand-edit at
   freeze time. Because `tomllib` is read-only, **status never lives in
   QUEUE.toml**: intent (human-edited QUEUE.toml) is separated from state
   (machine-owned `docs/loom/queue-state.json`, written only by
   `batch_queue.py`). The script never modifies the human's file.
2. **Worktree/branch naming** adopts the `using-git-worktrees` house
   convention (`.worktrees/<branch-slug>/`, gitignored): branch
   `loom/<change-id>`, worktree `<projectPath>/.worktrees/loom-<change-id>`.
3. **Circuit breaker**: after 2 consecutive FAILED items (in dispatch order),
   `next` refuses with exit code 3 and a HALT message; `--override-halt`
   proceeds anyway. Default matches the brief's proposal.

## Task 1 — QUEUE.toml parser happy path

- **Description**: Create `loom-pipeline/scripts/batch_queue.py` with
  `load_queue(queue_path)` parsing `[[change]]` array-of-tables via stdlib
  `tomllib`: returns entries in file order, each with `id`, `plan`
  (project-relative path), `budgets` (dict with `run`, optional
  `perStation`), optional `models` (dict). Pure stdlib, resolves nothing yet.
- **Module**: `loom-pipeline/scripts/batch_queue.py` (new file)
- **Files touched**: `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/test_pipeline_batch_queue.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/build_driver.py` (house style: stdlib-only, cwd-independent path resolution)
- **Acceptance**:
  - **RED**: `test_pipeline_batch_queue.py::test_load_queue_returns_entries_in_file_order` fails (module/function absent)
  - **GREEN**: a tmp QUEUE.toml with 3 `[[change]]` entries returns 3 dicts in file order with `id` / `plan` / `budgets.run` populated
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: "Queue convention — one human-editable file in the target project … ordered entries of change-id / planPath / pre-authorized budgets / model policy / status" + Decision §"Human gates: (a) change-id minting and (c) cost policy move to freeze time (queue-entry authoring)"

## Task 2 — QUEUE.toml fail-loud validation

- **Description**: Extend `load_queue` to fail loud (raise `QueueError` with
  the offending entry id/index and field name) when an entry is missing
  `id`, `plan`, or `budgets.run`, when `id` violates the driver's changeId
  allow-list (`[A-Za-z0-9._-]+`, no `..`), or when ids collide; missing or
  non-TOML file also raises. Mirrors guardArgs's no-improvised-defaults
  stance.
- **Module**: `loom-pipeline/scripts/batch_queue.py`
- **Files touched**: `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/test_pipeline_batch_queue.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/driver_10_guard.js` (changeId allow-list + fail-loud message style)
- **Acceptance**:
  - **RED**: `test_pipeline_batch_queue.py::test_load_queue_fails_loud_on_missing_required_field` fails (no validation yet)
  - **GREEN**: entry missing `budgets.run` raises `QueueError` naming the entry id and the missing field; valid file still parses
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: Decision §"script-owned bookkeeping … queue parsing" + Error evidence "exit non-zero on malformed queue file"

## Task 3 — state file helpers

- **Description**: Add `load_state(state_path)` / `save_state(state_path, state)`
  (JSON, machine-owned, `docs/loom/queue-state.json`) and
  `effective_entries(entries, state)` merging queue entries with recorded
  statuses — an entry absent from state is `QUEUED`; state records carry
  `status` (`RUNNING|DONE|FAILED|SKIPPED`), optional `runId`, `branch`,
  `worktree`, `reason`. `save_state` writes atomically (tmp + rename).
- **Module**: `loom-pipeline/scripts/batch_queue.py`
- **Files touched**: `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/test_pipeline_batch_queue.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-loom-pipeline-v1-1-batch-mode.md` (§Smallest End State — durable batch state)
- **Acceptance**:
  - **RED**: `test_pipeline_batch_queue.py::test_effective_entries_defaults_absent_ids_to_queued` fails (helpers absent)
  - **GREEN**: round-trip load→save→load preserves records; unmerged entry reports status `QUEUED`
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: "This file is gate (c) moved to freeze time AND the durable batch state" (state half — machine record separated from human intent, see §Settled open questions 1)

## Task 4 — freeze predicate

- **Description**: Add `check_frozen(entry, project_path, skills_root)` →
  `(eligible: bool, reason: str)`: runs
  `python3 <skills_root>/loom-spec/scripts/validate_spec_output.py
  <project_path>/docs/loom/<id>` via subprocess and requires exit 0, and
  requires `<project_path>/<entry.plan>` to exist. Ineligible returns the
  specific reason (validator exit N / plan missing), never raises for
  ineligibility.
- **Module**: `loom-pipeline/scripts/batch_queue.py`
- **Files touched**: `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/test_pipeline_batch_queue.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/driver_40_seg2.js` (validator invocation convention, lines 106-127)
- **Acceptance**:
  - **RED**: `test_pipeline_batch_queue.py::test_check_frozen_rejects_when_validator_nonzero` fails (function absent); test injects a stub validator script under a tmp skills_root
  - **GREEN**: stub validator exit 1 → `(False, reason)` naming the exit code; exit 0 + plan present → `(True, ...)`
- **External surfaces**:
  - Internal sibling-team contract: `loom-spec/scripts/validate_spec_output.py <changeDir>` exit-0 gate — grounding: in-repo evidence `loom-pipeline/scripts/driver_40_seg2.js:109,127`
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: Decision §"Freeze predicate = loom-spec validator exit-0 + plan written. No segment 2.5."

## Task 5 — worktree + branch creation

- **Description**: Add `ensure_worktree(project_path, change_id)` →
  `(worktree_path, branch)`: creates branch `loom/<change-id>` and worktree
  `<project_path>/.worktrees/loom-<change-id>` via
  `git -C <project_path> worktree add -b <branch> <worktree_path>` from
  current HEAD; idempotent when the worktree already exists on the right
  branch (returns it); fails loud on a branch/path conflict it did not
  create.
- **Module**: `loom-pipeline/scripts/batch_queue.py`
- **Files touched**: `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/test_pipeline_batch_queue.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/using-git-worktrees/SKILL.md` (§The `.worktrees/` convention)
- **Acceptance**:
  - **RED**: `test_pipeline_batch_queue.py::test_ensure_worktree_creates_branch_and_path` fails (function absent); test builds a tmp git repo with one commit
  - **GREEN**: worktree dir exists, `git -C <worktree> rev-parse --abbrev-ref HEAD` == `loom/<id>`; second call returns same path without error
- **External surfaces**:
  - CLI flag: `git worktree add -b <branch> <path>` — grounding: in-repo evidence `loom-code/skills/using-git-worktrees/SKILL.md` §The `.worktrees/` convention (house-verified pattern)
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: "create its worktree + branch" (Smallest End State §2 `next`); Decision §"script-owned bookkeeping … worktree/branch creation"

## Task 6 — `mark` command

- **Description**: Add CLI entry (`argparse`, subcommands) with
  `mark <change-id> done|failed [--run-id <id>] [--reason <text>]`
  updating the state file record for that id; unknown id or invalid status
  → non-zero exit with message. `python3 batch_queue.py mark …` runnable
  from any cwd via `--project <path>` (state path derived from it).
- **Module**: `loom-pipeline/scripts/batch_queue.py`
- **Files touched**: `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/test_pipeline_batch_queue.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/batch_queue.py` (state helpers from Task 3)
- **Acceptance**:
  - **RED**: `test_pipeline_batch_queue.py::test_mark_writes_status_and_run_id` fails (CLI absent)
  - **GREEN**: `mark X done --run-id wf_1` → state file records `{status: DONE, runId: wf_1}` for X; exit 0
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Brief item covered**: "`mark <change-id> done|failed [--run-id …]` — write back status" (Smallest End State §2)

## Task 7 — `status` command

- **Description**: Add `status` subcommand rendering a one-screen plain-text
  overview: one line per queue entry in order — id, effective status, runId
  if any, reason if SKIPPED/FAILED — plus a totals line. This is the first
  thing a fresh session reads to take over a batch.
- **Module**: `loom-pipeline/scripts/batch_queue.py`
- **Files touched**: `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/test_pipeline_batch_queue.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/batch_queue.py` (parser from Task 1, state helpers from Task 3)
- **Acceptance**:
  - **RED**: `test_pipeline_batch_queue.py::test_status_lists_every_entry_with_effective_status` fails (subcommand absent)
  - **GREEN**: stdout contains one line per entry with id + status and a final totals line
- **Dependencies**: Tasks 1, 3 complete first
- **Independent**: false
- **Brief item covered**: "`status` — one-screen queue overview (what a fresh session reads first)" (Smallest End State §2)

## Task 8 — `next` command happy path

- **Description**: Add `next --project <path> --skills-root <path>`
  [`--queue <path>` default `docs/loom/QUEUE.toml`]: pick the first entry
  with effective status `QUEUED`, run the freeze predicate, create its
  worktree/branch, record `RUNNING` (+ branch/worktree) in state, and print
  a single JSON object to stdout with ready-to-use Workflow args —
  `{segment: 3, changeId, projectPath: <worktree_path>, planPath:
  <absolute plan path inside worktree>, budgets, models, skillsRoot}` —
  matching the driver's guardArgs/seg3 required fields. Empty queue →
  exit 0 with `{"done": true}`.
- **Module**: `loom-pipeline/scripts/batch_queue.py`
- **Files touched**: `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/test_pipeline_batch_queue.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/driver_10_guard.js` (required arg fields)
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/driver_50_seg3.js` (planPath guard, lines 72-83)
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/skills/using-loom-pipeline/SKILL.md` (§Run inputs field table)
- **Acceptance**:
  - **RED**: `test_pipeline_batch_queue.py::test_next_emits_workflow_args_and_marks_running` fails (subcommand absent); test uses tmp git repo + stub validator
  - **GREEN**: stdout JSON carries all six fields with `projectPath` = worktree path; state shows the id `RUNNING`
- **External surfaces**:
  - Internal sibling-team contract: driver run-input args shape (`segment/changeId/projectPath/budgets/models`, `planPath` for segment 3) — grounding: in-repo evidence `loom-pipeline/scripts/driver_10_guard.js:19`, `driver_50_seg3.js:72`
- **Dependencies**: Tasks 2, 3, 4, 5 complete first
- **Independent**: false
- **Brief item covered**: "`next` — return the next QUEUED entry after verifying the freeze predicate … emit the ready-to-use Workflow args as JSON" (Smallest End State §2)

## Task 9 — `next` skips ineligible entries loudly

- **Description**: Extend `next`: when the head entry fails the freeze
  predicate, record `SKIPPED` with the predicate's reason in state, print a
  one-line notice to stderr, and advance to the next QUEUED entry (loop
  until an eligible entry, `{"done": true}`, or halt). Never silent, never
  blocking the queue.
- **Module**: `loom-pipeline/scripts/batch_queue.py`
- **Files touched**: `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/test_pipeline_batch_queue.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/batch_queue.py` (Task 8's `next`)
- **Acceptance**:
  - **RED**: `test_pipeline_batch_queue.py::test_next_skips_unfrozen_entry_and_advances` fails (skip loop absent)
  - **GREEN**: with entry A unfrozen and B frozen, `next` returns B's args; state shows A `SKIPPED` with the validator reason
- **Dependencies**: Task 8 completes first
- **Independent**: false
- **Brief item covered**: "ineligible entries are marked SKIPPED loudly, never silently" (Smallest End State §2); Decision §"Failure policy: isolate and continue"

## Task 10 — consecutive-failure circuit breaker

- **Description**: Extend `next`: before selecting, scan state in queue
  order — if the 2 most recent terminal outcomes are consecutive `FAILED`,
  exit 3 with a HALT message naming both ids (systemic-failure signal);
  `--override-halt` bypasses. SKIPPED does not count toward the breaker.
- **Module**: `loom-pipeline/scripts/batch_queue.py`
- **Files touched**: `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/test_pipeline_batch_queue.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/batch_queue.py` (Task 8's `next`)
- **Acceptance**:
  - **RED**: `test_pipeline_batch_queue.py::test_next_halts_after_two_consecutive_failures` fails (breaker absent)
  - **GREEN**: state with X FAILED then Y FAILED → `next` exits 3 naming X,Y; `--override-halt` returns the next entry's args
- **Dependencies**: Task 8 completes first
- **Independent**: false
- **Brief item covered**: brief §Open Questions 3 "halt after 2 consecutive failures, report" (settled in-plan, §Settled open questions 3)

## Task 11 — SKILL.md §Batch mode

- **Description**: Add §Batch mode to
  `loom-pipeline/skills/using-loom-pipeline/SKILL.md`: the QUEUE.toml
  convention (fields + example block), the intent/state file separation, and
  the dispatcher-only loop contract — one `batch_queue.py next` → one
  `Workflow({segment: 3, …})` with the JSON emitted by `next` → one
  `batch_queue.py mark` → repeat; main agent never parses the queue file,
  never composes git commands, never diagnoses failures mid-batch;
  end-of-batch human report lists DONE/FAILED/SKIPPED with ledger paths.
  Extend `test_pipeline_skill_contract.py` with the batch-mode assertions.
- **Module**: `loom-pipeline/skills/using-loom-pipeline/SKILL.md`
- **Files touched**: `loom-pipeline/skills/using-loom-pipeline/SKILL.md`, `loom-pipeline/scripts/test_pipeline_skill_contract.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/batch_queue.py` (final CLI surface from Tasks 6-10)
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/test_pipeline_skill_contract.py` (existing assertion style)
- **Acceptance**:
  - **RED**: `test_pipeline_skill_contract.py::test_skill_batch_mode_section_contract` fails (section absent)
  - **GREEN**: test asserts §Batch mode presence + the three dispatcher-only prohibitions + the `next`→Workflow→`mark` loop wording
- **Dependencies**: Tasks 6, 7, 9, 10 complete first
- **Independent**: true
- **Brief item covered**: "SKILL.md §Batch mode — the loop contract for the main agent … dispatcher-only" (Smallest End State §3)

## Task 12 — README flip + BACKLOG entry removal

- **Description**: In `loom-pipeline/README.md`, replace §"Committed next
  (v1.1): batch implementation mode" with a §Batch mode documentation
  section (queue file, batch_queue.py loop, sequential-only, parked v1.1.x
  parallel variant untouched); delete the v1.1 entry from
  `docs/loom/BACKLOG.md` (completed items are deleted). Extend
  `test_pipeline_readme.py` with the flip assertion.
- **Module**: `loom-pipeline/README.md`
- **Files touched**: `loom-pipeline/README.md`, `docs/loom/BACKLOG.md`, `loom-pipeline/scripts/test_pipeline_readme.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/README.md` (§Committed next, §Parked items)
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/test_pipeline_readme.py` (existing assertion style)
- **Acceptance**:
  - **RED**: `test_pipeline_readme.py::test_readme_batch_mode_documented_not_committed_next` fails (README still says Committed next)
  - **GREEN**: README has §Batch mode, no "Committed next (v1.1)" heading; BACKLOG.md has no "v1.1 — batch implementation mode" entry
- **Dependencies**: Tasks 6, 7, 9, 10 complete first
- **Independent**: true
- **Brief item covered**: "README update — §Committed next flips to a documented §Batch mode" (Smallest End State §4) + What Becomes Obsolete (BACKLOG v1.1 entry)

## Task 13 — plugin version bump

- **Description**: Bump loom-pipeline plugin version 0.1.0 → 0.2.0 in
  `loom-pipeline/.claude-plugin/plugin.json` and sync the marketplace entry
  description/version if the marketplace file carries them (check
  `.claude-plugin/marketplace.json` at repo root); keep manifest tests green.
- **Module**: `loom-pipeline/.claude-plugin/plugin.json`
- **Files touched**: `loom-pipeline/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/test_pipeline_manifests.py`
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/test_pipeline_marketplace_entry.py`
- **Acceptance**:
  - **RED**: diagnostic — `grep '"version": "0.2.0"' loom-pipeline/.claude-plugin/plugin.json` exits non-zero before the change
  - **GREEN**: grep exits 0; `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-pipeline/scripts/test_pipeline_manifests.py loom-pipeline/scripts/test_pipeline_marketplace_entry.py -q` passes
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Decision §"Build batch mode as a conductor-layer loop" (shipping a feature release of the plugin; version bump is the release mechanics)

## Notes

- **Post-PASS amendment (2026-07-03 15:49)**: appended the human-gates
  Decision quote to Task 1's `Brief item covered` per the reviewer's
  traceability note. Additive referent only — all required fields, task
  scopes, and DAG structure unchanged — re-review skipped.
- **Critical path**: Task 1 → 2 → 8 → 9 (or 10) → 11 (or 12) = depth 5.
  Tasks 1/3/4/5 share `batch_queue.py` so they are NOT parallel-dispatch
  eligible (overlapping `Files touched`) despite `Dependencies: none` —
  SDD's sequential dispatch is the floor for Tasks 1-10; Tasks 11+12 are
  `Independent: true` (disjoint files) and may dispatch in one wave;
  Task 13 is independent of everything and may join any wave.
- **QUEUE.toml sketch** (authoritative version lands in SKILL.md, Task 11):
  ```toml
  [[change]]
  id = "add-export-csv"
  plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
  models = { code = "sonnet", review = "sonnet" }
  [change.budgets]
  run = 200000
  perStation = { code = 40000, review = 20000 }
  ```
- **Branch base**: `ensure_worktree` branches from the project's current
  HEAD — freezing implies the change-folder + plan are committed, so the
  worktree sees them. The freeze predicate runs against the main checkout;
  the worktree is created after it passes.
- **skillsRoot** is a CLI flag (`--skills-root`), not a queue field — it is
  per-machine, not per-change.
- **No driver changes**: zero `driver_*.js` edits; no
  `build_driver.py` rebuild; the generated asset is untouched (brief
  §Current State Evidence, Reverse).
