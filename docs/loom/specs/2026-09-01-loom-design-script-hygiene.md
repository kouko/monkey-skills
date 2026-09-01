# loom-design script hygiene — one pytest root, and a CLI seam in batch_queue.py

Author: kouko (brief drafted by agent session, 2026-09-01)
Branch: `loom-script-refactor-phase3`

## Design-side on-ramp

not fired — refactor and test-infrastructure arc; the reception's negative guard skips the upstream-artifact walk for refactors, and no product-shaped, user-facing, or multi-state new work is proposed

## Queue relation

unqueued — the two backlog entries this arc closes are `status: open`, and the store holds zero live `bet` entries

## Problem

When I change one loom-design station script, I want a single command that runs
every loom-design test and a module whose region I can read without paging past
four unrelated ones, so I can find out that I broke a sibling station before CI
tells me.

## Users

- **kouko**, working in a git worktree, running tests locally before push. Today
  the only way to run all of loom-design's tests is to remember five separate
  per-directory pytest commands spread across three CI workflow files; running
  the obvious `pytest loom-design/scripts/` produces zero executed tests and
  looks like catastrophic breakage.
- **Dispatched agent sessions** (implementer / reviewer under SDD), which resolve
  a test command through `verification-before-completion`'s declared-first rule.
  A station directory that is not in any declared surface is silently untested by
  a worker who trusts the declared command.
- **Whoever adds the sixth loom-design station**: today that requires
  hand-writing a sixth CI job in the right one of three workflow files.

## Smallest End State

Two changes, both in `loom-design/`:

1. `python3 -m pytest loom-design/scripts/` runs as ONE green invocation, and
   the five per-directory CI jobs collapse to one.
2. `batch_queue.py`'s CLI-handler region moves to its own module; `batch_queue.py`
   keeps `main` and the argparse wiring, and `argv_exec.py`'s `batch_queue.main`
   call site is unchanged. Behavior and side-effect ordering are unchanged,
   proven by the existing 83 tests staying green.

Deliberately NOT part of the minimum: renaming any colliding basename,
deleting the byte-identical duplicate test files, adding `__init__.py`
packaging, or touching `loom_gate_markers.py`.

## Current State Evidence

**Forward**

- `python3 -m pytest loom-design/scripts/` aborts at collection today with the
  verbatim line `Interrupted: 8 errors during collection` and executes zero
  tests — the unified root does not exist even in a broken-but-running form.
- `.github/workflows/loom-pipeline-ci.yml` runs
  `python3 -m pytest loom-design/scripts/pipeline/ -q` as one of five
  per-directory invocations; `loom-siblings-ci.yml` holds three more and
  `loom-spec-ci.yml` the fifth.
- `batch_queue.py`'s `main` dispatches to `_cmd_*` handlers that are interleaved
  with the reconcile engine (`_reconcile_running_entries`) and the `next`
  helpers (`_dispatch_entry`), so a CLI-only edit reads past both.

**Reverse**

- `loom-design/scripts/pipeline/argv_exec.py` — `import batch_queue`, then
  `batch_queue.main(decoded)`. This is the only production importer; a split
  must keep `batch_queue.main` importable under exactly that name.
- `loom-design/scripts/pipeline/test_pipeline_batch_queue.py` imports eleven
  names from `batch_queue`, including the privates `_check_circuit_breaker`,
  `_classify_running_entry`, and `_read_wf_terminal_status`.
- `loom-design/skills/using-loom-pipeline/SKILL.md` pins CLI invocation strings,
  and `test_pipeline_skill_contract.py` subprocess-invokes
  `batch_queue.py status`, so the script's path and CLI surface must survive
  unchanged.

**Error**

- The refusal path is `_fail` raising `QueueError`, plus `check_frozen`'s
  plan-header verdict gate. A split must not change any refusal message text:
  `test_pipeline_skill_contract.py` asserts on that prose.
- Today's eight failures are `import file mismatch` collection errors, not test
  failures — so no loom-design test is currently known-red, and the collision
  masks nothing.

**Data**

- `QUEUE.toml` and `queue-state.json` are read and written through
  `load_queue`, `load_state`, and `save_state` under the `_state_lock` context
  manager. Inside `_cmd_next`'s single lock span the `state` dict is mutated by
  three writers (`_reconcile_running_entries`, `_skip_entry`, `_dispatch_entry`)
  and read back by `effective_entries`; `entries` itself is never mutated —
  `effective_entries` shallow-copies.

**Boundary**

- `[FRAGILE]` The repo's sibling-import convention, documented in
  `loom-code/scripts/sibling_import.py` as "no `__init__.py`, no conftest",
  is load-bearing here. Measured: `--import-mode=importlib` **alone** breaks it,
  raising `ModuleNotFoundError: No module named 'heading_window'` and turning 8
  collection errors into 18. Any import-mode change must restore each
  directory's own `sys.path` entry.
- `[ASYNC]` `ensure_worktree` and `_teardown_worktree` shell out to git
  worktree commands, and `_dispatch_entry` polls workflow-run status; these sit
  in the region a CLI split moves code away from, not into.
- `[FRAGILE]` Measured locally on pytest 9.0.3; CI pins Python 3.11 with
  `pytest pyyaml` installed. A fix that relies on version-specific import
  behavior must be verified on the CI version, not only locally.

**Evidence paths**

- `loom-design/scripts/pipeline/batch_queue.py` — `_cmd_next`, `_state_lock`,
  `effective_entries`, `check_frozen`, `_fail`, `main`
- `loom-design/scripts/pipeline/argv_exec.py` — `batch_queue.main(decoded)`
- `loom-design/scripts/pipeline/test_pipeline_batch_queue.py` —
  `test_next_reconciles_running_entries_before_normal_scan`,
  `test_next_halts_after_two_consecutive_failures`
- `loom-design/scripts/pipeline/test_pipeline_skill_contract.py` — subprocess
  invocation of `batch_queue.py status`
- `.github/workflows/loom-pipeline-ci.yml` — `python3 -m pytest loom-design/scripts/pipeline/ -q`
- `.github/workflows/loom-siblings-ci.yml` — "The suites MUST run as separate pytest invocations"
- `.github/workflows/loom-spec-ci.yml` — `python3 -m pytest loom-design/scripts/spec/ -v`
- `loom-code/scripts/sibling_import.py` — "no `__init__.py`, no conftest"
- `docs/loom/backlog/2026-08-31-batch-queue-split.md` — "No tests currently pin cross-function state-mutation ordering"
- `docs/loom/backlog/2026-08-31-loom-design-unified-pytest-root.md` — "collapse these to one pytest root"
- `docs/loom/backlog/2026-07-30-pytest-module-name-collision-loom-code-scripts-distribute-py-vs-obsidian.md` — the prior diagnosis of the same collision class

## Alternatives Considered

**My take: Option A — `--import-mode=importlib` plus a per-directory `conftest.py`
that inserts its own directory on `sys.path`.**

Why: it is the only candidate measured green end-to-end in this repo (1014 passed
in a single invocation, 9.5s), it leaves every existing per-directory invocation
working so CI can be collapsed without a flag day, it adds no import surface that
the sibling-import convention forbids, and it is structural — a sixth station
directory gets one four-line conftest instead of a sixth CI job.

Conditional reversal: if CI's Python 3.11 / pinned pytest behaves differently from
the locally measured pytest 9.0.3, this option loses its only real advantage
(measured green) and Option C's mechanical renames become the safe fallback.

| Option | Approach | Measured result | Why not chosen |
|---|---|---|---|
| **A (chosen)** | `pytest.ini` at `loom-design/scripts/` setting `addopts = --import-mode=importlib`, plus five 4-line `conftest.py` files inserting each station dir on `sys.path` | **1014 passed, one invocation.** Legacy per-dir call still green (247 passed). No leak into loom-code (83 passed unchanged). | — |
| B | Add `__init__.py` to each station directory, making them packages | Not run — reasoned out | Breaks the repo-wide documented sibling-import convention: bare `from batch_queue import ...` would have to become `from pipeline.batch_queue import ...` across every test and `argv_exec.py`. Large blast radius for a test-runner problem. |
| C | Rename the five colliding basenames to be unique | Not run | Touches 12 files plus every reference, and is a per-incident fix: the next station that adds a `test_plugin_manifest.py` re-opens the same bug. Does not remove the constraint, only this instance of it. |
| D | Keep five jobs; document the constraint better | Status quo | The backlog entry exists precisely because the job list grows with each station, and because the obvious local command silently reports zero tests. |

**Research (Axis 4, EN + JA).** Both language sets converge on the same two
remedies — add `__init__.py`, or use unique basenames — i.e. Options B and C.
Neither surfaced the `importlib` + per-directory-`conftest` combination that
actually works here. **The EN/JA agreement is itself the finding: the public
advice does not cover a repo that deliberately forbids `__init__.py`**, which is
why the measurement, not the search, decided this. Sources:
[pytest issue #529](https://github.com/pytest-dev/pytest/issues/529),
[pytest issue #3151](https://github.com/pytest-dev/pytest/issues/3151),
[Peterbe: pytest "import file mismatch"](https://www.peterbe.com/plog/pytest-import-file-mismatch),
[Qiita: pytest で同名テストファイルが ImportPathMismatchError になる原因と解決策](https://qiita.com/tamabe/items/256023e5138251c88a27),
[Qiita: Pytest 実行時にテストケースを記述している同名のファイルがある場合のエラーへの対応方法](https://qiita.com/manabian/items/ada7a0627865145db504).

For the `batch_queue.py` split no comparable design fork exists: the backlog
entry names one candidate cut (CLI handlers out, thin argparse entry point
retained), the only production importer constrains the entry point's name, and
no alternative module boundary was found that satisfies both.

## Diagrams

Not needed — the change is a file-level extraction plus a test-runner
configuration; the file inventory in Current State Evidence carries the shape
without a diagram.

## Decision

We will do two things in `loom-design/`. First, make
`python3 -m pytest loom-design/scripts/` a single green invocation, by adding a
scoped `pytest.ini` that selects `--import-mode=importlib` plus five four-line
`conftest.py` files that restore each station directory's own `sys.path` entry.
The five per-directory CI jobs then collapse into one, and the two CI comments
that currently assert the suites *must* run separately are rewritten.

Second, extract `batch_queue.py`'s CLI command handlers into their own module,
leaving `batch_queue.py` as argparse wiring plus `main`. `argv_exec.py`'s
`batch_queue.main` call site and every pinned CLI string stay unchanged.

We will NOT split `loom_gate_markers.py` in this arc. It is named by a claimed
ticket on the live `family-relocation` decision map, whose DA-1 ownership verdict
is still open and which the user confirmed on 2026-09-01 is still to be done;
choosing a module boundary inside a file whose owning plugin is under active
deliberation would have to be re-litigated once that verdict lands. Its backlog
entry stays `open` with its event trigger intact.

We will also NOT deduplicate the byte-identical test files that contribute to the
collision. Deleting them would reduce the collision count but not remove it —
`mint_critic_verdict.py` is two genuinely different programs in `interface/` and
`spec/` — so dedup is a separate deletion-first pass with its own judgment calls,
and the chosen fix does not depend on it.

## What Becomes Obsolete

- Four of the five per-directory pytest invocations
  (`loom-siblings-ci.yml` ×3, `loom-spec-ci.yml` ×1) — deleted, not left beside
  the unified job.
- The two CI comments that state the current constraint as a rule:
  `loom-siblings-ci.yml` "The suites MUST run as separate pytest invocations"
  and `loom-pipeline-ci.yml` "This suite runs as its OWN pytest invocation".
  These become false the moment the unified root lands and must be rewritten in
  the same change.
- Backlog entries `2026-08-31-loom-design-unified-pytest-root` and
  `2026-08-31-batch-queue-split` — both close.
- The risk claim inside the `batch-queue-split` entry ("No tests currently pin
  cross-function state-mutation ordering") is factually wrong and must be
  corrected in the closing note rather than closed silently: 83 tests exist and
  `test_next_reconciles_running_entries_before_normal_scan` pins exactly that
  ordering.

## Out of Scope

- Splitting `loom-code/scripts/loom_gate_markers.py` (deferred — see Decision).
- Withdrawing the stuck `task-inventory-consumers` claim on the
  `family-relocation` map. It is that map's debt, it belongs to another session's
  claim, and per REQ-97 a claim is not transferable; the user was asked and has
  not authorized touching it.
- Deleting or merging the byte-identical duplicate test files.
- Renaming any colliding basename.
- Any change to loom-code's own test layout, which has no unified-root problem
  in scope here.
- Adding a repo-root `pyproject.toml` or repo-wide pytest configuration; the
  `pytest.ini` in this arc is deliberately scoped to `loom-design/scripts/` and
  was measured not to affect loom-code.

## Open Questions

- **OQ-1 [RESOLVED]** Should the byte-identical duplicate test files be
  deduplicated as part of this arc? Resolved: no — the chosen fix is measured
  green without it, and two of the five collisions are genuinely distinct
  programs, so dedup is a separate deletion-first judgment call. Recorded in
  Out of Scope.
- **OQ-2 [RESOLVED]** Does the unified root need a repo-root pytest
  configuration? Resolved: no — a `pytest.ini` scoped to `loom-design/scripts/`
  was measured to give the unified run while leaving both the legacy
  per-directory invocation and loom-code's suite unaffected.
- **OQ-3 [RESOLVED]** Is the `batch-queue-split` entry's stated ordering risk
  real? Resolved: no — refuted by measurement (83 tests; two of them pin
  ordering explicitly). The split proceeds as an ordinary refactor under those
  tests, and the entry's claim is corrected on close.
