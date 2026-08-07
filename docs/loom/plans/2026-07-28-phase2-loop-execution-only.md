# Plan: Phase 2 loop — execution-only redesign

Source brief: docs/loom/specs/2026-07-28-phase2-loop-execution-only.md
Total tasks: 4
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible (Tasks 2-3 parallel after Task 1; Task 4 depends on Task 2)
Plan-document-reviewer verdict: PASS (2026-07-28, 14/14)

## Task 1 — Housekeeping: rename phase2-loop directory, retire dead code

- **Description**: `git mv scripts/nightly-phase2-loop scripts/phase2-loop`. Delete `backlog_parser.py`/`test_backlog_parser.py` (fully retired — replaced by Task 2's `queue_entry.py`, not moved). Remove `assert_safe_target_branch` from `safety_gates.py` and its corresponding test from `test_safety_gates.py` (dead code — `loom-pipeline/scripts/batch_queue.py`'s `ensure_worktree` already isolates every queue entry into its own branch/worktree, superseding this repo's own branch-collision check). `journal_writer.py`/`test_journal_writer.py` move as-is with no content change (still `append_journal_line`; only its call-site role changes, documented in Task 3's routine, not in code).
- **Module**: `scripts/phase2-loop/` (directory-level housekeeping)
- **Files touched**: `scripts/phase2-loop/safety_gates.py`, `scripts/phase2-loop/test_safety_gates.py`, `scripts/phase2-loop/journal_writer.py`, `scripts/phase2-loop/test_journal_writer.py` (moved); `scripts/nightly-phase2-loop/backlog_parser.py`, `scripts/nightly-phase2-loop/test_backlog_parser.py` (deleted, not moved); `AGENTS.md` (path update only, in the already-declared "Run the nightly Phase 2 loop test suite" command-surface bullet)
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/scripts/nightly-phase2-loop/safety_gates.py` (current content, pre-move)
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-28-phase2-loop-execution-only.md` (brief — §What Becomes Obsolete grounds every removal here)
- **Acceptance**:
  - **RED**: a new test `scripts/phase2-loop/test_safety_gates.py::test_assert_safe_target_branch_removed` (asserting `hasattr(safety_gates, "assert_safe_target_branch") is False`) fails today — the function still exists at the old path.
  - **GREEN**: after the move + deletions, `scripts/phase2-loop/test_safety_gates.py` passes in full (including the new removal-assertion test); `is_nightly_paused`/`requires_real_agent_surface` behavior is unchanged (existing tests for both still pass, moved verbatim); `scripts/nightly-phase2-loop/` no longer exists; `backlog_parser.py`/`test_backlog_parser.py` are gone (not present anywhere in the repo).
  - **Command-surface note**: `AGENTS.md`'s existing "Run the nightly Phase 2 loop test suite" bullet's path (`scripts/nightly-phase2-loop/` and its `.venv`) must be updated to `scripts/phase2-loop/` — a mechanical path correction to an already-declared command, not a new command needing a fresh bullet.
- **External surfaces**: none (file move + stdlib test logic)
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "What Becomes Obsolete: `safety_gates.py`'s `assert_safe_target_branch` (+ its test)... remove in the same change" + "the 'nightly' naming across the surface (`scripts/nightly-phase2-loop/` → `scripts/phase2-loop/`...) — the clock-time framing this replaces" + "Repurpose the two still-useful pieces already committed (`safety_gates.py`'s kill switch + scope guard; a narrowed `journal_writer.py`...)" (Decision — this task is the vehicle carrying both functions forward unchanged into the renamed module)

## Task 2 — `propose_queue_entry` planning-stage helper

- **Description**: implement `propose_queue_entry(item_id: str, plan_path: Path, campaign_doc_path: Path, budget_run: int) -> str` in `scripts/phase2-loop/queue_entry.py`. Validates `plan_path`'s content contains a `Plan-document-reviewer verdict: PASS` line — fail loud (raise `ValueError` naming the missing verdict) if absent, mirroring `batch_queue.py`'s own no-improvised-defaults / fail-loud style rather than inventing a different error shape. Validates `item_id` (e.g. `"B1"`) appears as a Phase 2 checklist line (`- [ ] B<n>: ...`) in `campaign_doc_path`'s content — reusing the checklist-scanning approach from the retired `backlog_parser.py` (grep/regex over the `## Phase 2` section, same as its predecessor), fail loud naming the missing item if not found. Returns the drafted `[[change]]` TOML block text (`id`, `plan` as a project-relative path string, `budgets.run`).
- **Module**: `scripts/phase2-loop/queue_entry.py`
- **Files touched**: `scripts/phase2-loop/queue_entry.py`, `scripts/phase2-loop/test_queue_entry.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/dbt-wiki-quality-campaign.md` (real Phase 2 checklist — use its actual current section structure as realistic test input)
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/batch_queue.py` (`load_queue`'s required-field / fail-loud conventions, `_fail`/`QueueError` message shape — mirror this style)
- **Acceptance**:
  - **RED**: `scripts/phase2-loop/test_queue_entry.py::test_propose_queue_entry_fails_loud_without_reviewer_pass` fails (`propose_queue_entry` does not exist).
  - **GREEN**: given a temp plan-file fixture containing `Plan-document-reviewer verdict: PASS`, a temp campaign-doc fixture containing `- [ ] B1: ...` under a `## Phase 2` heading, and `item_id="B1"`, `propose_queue_entry` returns TOML text containing `id = "B1"`, the given plan path, and the given `budgets.run` value; given a plan-file fixture WITHOUT the PASS line, raises `ValueError` naming the missing verdict; given an `item_id` not present in the campaign doc's Phase 2 section, raises `ValueError` naming the missing item.
- **External surfaces**: none (pure stdlib string/file logic)
- **Dependencies**: Task 1 completes first (needs the renamed directory in place and the old `backlog_parser.py` already removed, so there is no stale duplicate module)
- **Independent**: true
- **Brief item covered**: "Planning-stage helper: `propose_queue_entry(...)` — repurposed from the existing `backlog_parser.py`'s `parse_next_backlog_item`... Validates the target plan file already carries the `Plan-document-reviewer verdict: PASS` line (fail loud... mirroring `batch_queue.py`'s own no-improvised-defaults stance)" + "Budget breaker: batch mode's own per-entry `budgets.run` TOML field (set explicitly when authoring the `QUEUE.toml` entry, never left at a platform default)"

## Task 3 — Rewrite the execution-stage routine doc

- **Description**: write `scripts/phase2-loop/ROUTINE.md` — the document a scheduled invocation follows — replacing the retired `NIGHTLY-ROUTINE.md` draft (already deleted). Must specify, in order: (1) check `is_nightly_paused` on `docs/loom/PHASE2_LOOP_PAUSED` — exit immediately if paused; (2) run `batch_queue.py reconcile --project <root>` FIRST (catches stuck/dead prior runs before anything else); (3) run `batch_queue.py next --project <root> --skills-root <root>` — exit no-op on `{"done": true}`; on exit code 3 (circuit breaker HALT), stop and leave for human review, do not override; (4) scope guard — `requires_real_agent_surface` on the picked entry's description; journal + exit if `True`; (5) dispatch `Workflow()` with `next`'s printed args (segment 3 ONLY — this stage never brainstorms or plans); (6) call `batch_queue.py mark-running <id> --run-id --session-dir` immediately after `Workflow()` returns; (7) unattended escalation ceiling — point at `loom-code/skills/using-loom-code/references/continuous-mode.md`'s existing "no human pumping → earlier halt" precedent by name and path; do not invent a new threshold; (8) on completion, `batch_queue.py mark <id> done|failed`; (9) `append_journal_line` with one human-readable summary line; (10) never touch any `plugin.json`/`VERSION` field; (11) never open a PR, never merge, never touch `main` or any other human-owned branch. Explicitly state this routine never calls `propose_queue_entry` — that is the planning-stage tool, out of scope for execution.
- **Module**: `scripts/phase2-loop/ROUTINE.md`
- **Files touched**: `scripts/phase2-loop/ROUTINE.md`, `scripts/phase2-loop/test_routine_doc.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/scripts/phase2-loop/safety_gates.py` (Task 1's output — kill switch + scope guard functions this doc calls)
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/batch_queue.py` (`reconcile`/`next`/`mark-running`/`mark` subcommand contracts — ground the exact invocation shapes against this file, not assumption)
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/using-loom-code/references/continuous-mode.md` (the earlier-halt precedent this doc points at)
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-28-phase2-loop-execution-only.md` (brief — full Smallest End State + Decision ground every step above)
- **Acceptance**:
  - **RED**: `scripts/phase2-loop/test_routine_doc.py::test_routine_doc_covers_required_steps` fails (`ROUTINE.md` does not exist at the new path).
  - **GREEN**: documentation artifact — RED/GREEN is structural-completeness (same class as the retired draft's own test), not behavioral. The test `Read`s `ROUTINE.md` and asserts, via deterministic substring/section-header checks: names the sentinel path `docs/loom/PHASE2_LOOP_PAUSED`; references all four `batch_queue.py` subcommands used (`reconcile`, `next`, `mark-running`, `mark`); names `continuous-mode.md` by path; states the fail-closed/never-retry rule on any failure; states the never-merge / never-PR / never-touch-main rule; states the no-version-pre-bump rule; and does NOT contain the strings "brainstorming" or "subagent-driven-development" as something this stage invokes itself (this stage only ever dispatches segment 3 / already-frozen work).
- **External surfaces**: informational only — the doc references `batch_queue.py`/`Workflow`/`CronCreate`, but this task's own test makes no direct external call
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "Execution-stage routine (`scripts/phase2-loop/ROUTINE.md`...): kill switch → `batch_queue.py reconcile` → `batch_queue.py next`... → scope guard... → dispatch `Workflow()` for segment 3... → `mark-running`... → `mark done|failed`... → one campaign-journal line. Unattended-context escalation ceiling: reuse `continuous-mode.md`'s existing... halt discipline"

## Task 4 — Integration proof: `propose_queue_entry` output validates against `batch_queue.py`

- **Description**: write an integration test proving `queue_entry.propose_queue_entry`'s TOML output, written into a temp `QUEUE.toml` fixture alongside a temp plan-file fixture carrying the PASS verdict line, round-trips cleanly through `loom-pipeline/scripts/batch_queue.py`'s `load_queue` and `check_frozen` (Form B path: no `docs/loom/<id>/` change-folder exists for the synthetic fixture, so the plan's own PASS line is the gate) — `check_frozen` must return `eligible=True` for the drafted entry. This is the brief's Open-Question "prove the wiring end-to-end" ask, deliberately scoped to a synthetic fixture rather than a real, currently-unplanned Phase 2 item — see Notes.
- **Module**: `scripts/phase2-loop/test_queue_entry_batch_integration.py`
- **Files touched**: `scripts/phase2-loop/test_queue_entry_batch_integration.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/scripts/phase2-loop/queue_entry.py` (Task 2's output)
  - `/Users/kouko/GitHub/monkey-skills/loom-pipeline/scripts/batch_queue.py` (`load_queue`, `check_frozen` — imported directly in-process; note the cross-plugin-directory import path handling this needs, e.g. `sys.path` manipulation scoped to the test module)
- **Acceptance**:
  - **RED**: `scripts/phase2-loop/test_queue_entry_batch_integration.py::test_proposed_entry_passes_batch_queue_freeze_check` fails (the test module does not exist yet).
  - **GREEN**: given `propose_queue_entry`'s output written into a temp `QUEUE.toml`, `load_queue` parses it without raising, and `check_frozen` returns `(True, ...)` for that entry via the Form B (brief+plan) path.
- **External surfaces**: none beyond an in-repo Python import of `loom-pipeline/scripts/batch_queue.py` (sibling-plugin cross-import, same repo)
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: Open Question — "recommend proving it end-to-end in the same change... `writing-plans` should scope one task to... seed `QUEUE.toml` with that one entry" (scoped per Notes below to a synthetic integration proof, not a live Phase-2-item run)

## Notes

- **Deviation from the brief's Open Question, with reason**: the brief's Open Question suggested seeding the REAL `docs/loom/QUEUE.toml` with an actual first Phase 2 item run through planning stage "for real." This plan does NOT do that — running a real Phase 2 item through brainstorming + writing-plans + reviewer-PASS is itself a full separate change (its own brief, its own plan, its own SDD cycle), not a task inside an infrastructure-only plan. Task 4's synthetic integration test proves the wiring (`propose_queue_entry` output is genuinely consumable by `batch_queue.py`) without conflating "build the tool" with "use the tool on a real backlog item," which is future work once this plan ships. The real `docs/loom/QUEUE.toml` is intentionally NOT created by this plan — it comes into existence the first time a real Phase 2 item is actually planned and queued, not pre-seeded speculatively.
- Tasks 2 and 3 are independent leaves once Task 1 completes (disjoint files, no semantic dependency) — dispatch their implementers in one parallel wave per `dispatching-parallel-agents`.
- This plan is infrastructure-only, per the brief's scope: it does not process any real Phase 2 backlog item, does not touch Phase 2's backlog CONTENT, and does not register a live `CronCreate` schedule (that remains a separate, explicitly-confirmed follow-up after this plan ships, same standing gate the original U1 plan's Task 5 named).
