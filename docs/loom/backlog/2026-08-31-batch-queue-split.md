---
name: 2026-08-31-batch-queue-split
description: loom-design/scripts/pipeline/batch_queue.py mixes queue-state I/O, freeze checks, worktree lifecycle, dispatch/circuit-breaker logic, and CLI command handlers in one 1369-line module
status: closed
origin: 2026-08-31 — three-plugin script audit (Phase 3 item 3b), deferred from docs/loom/specs/2026-08-31-decision-map-script-cleanup.md §Out of Scope
start: event — the next change that touches two of its responsibility regions in one task
---

`loom-design/scripts/pipeline/batch_queue.py` is 1369 lines. The module has
no `# ---` section-comment banners; the responsibility split below is
read off its function groupings, not literal headers — report what is
actually there rather than forcing a fixed count.

Regions found:

- **Queue/state I/O** (`load_queue`, `load_state`, `save_state`,
  `_state_lock`, `effective_entries`, lines ~87-240) — reads/writes
  `QUEUE.toml` and `queue-state.json`, plus the file-lock context manager.
- **Freeze gate** (`check_frozen`, ~241-327) — plan-header reviewer-verdict
  regex check, its own concern with a dedicated comment block above it.
- **Worktree lifecycle** (`ensure_worktree`, `_teardown_worktree`,
  ~328-400 and ~919-953) — creates/tears down the per-change git worktree.
- **Dispatch + reconciliation** (`_dispatch_entry`, `_check_circuit_breaker`,
  `_halt_notice_if_tripped`, `_reconcile_running_entries`,
  `_classify_running_entry`, `_read_wf_terminal_status`,
  `_parse_iso_timestamp`, `_describe_non_terminal_entry`, ~575-1080
  interleaved with CLI handlers) — workflow-run polling, timeout/circuit-
  breaker classification, and reconciling entries stuck in `running`.
- **CLI command handlers** (`_cmd_mark`, `_cmd_mark_running`,
  `_cmd_reconcile`, `_cmd_reset`, `_cmd_force_fail`, `_cmd_status`,
  `_cmd_next`, plus `_resolve_paths_and_validate_id`/`_require_running`,
  ~401-1216) — by far the largest region, ~750 of 1369 lines; each
  handler owns argument validation, state mutation, and stdout formatting
  for one subcommand.
- **Argparse wiring** (`_build_parser`, `_add_next_subparser`, `main`,
  `_assert_valid_change_id`, ~1217-1369) — CLI entry point and id
  validation shared across handlers.

Candidate cut: split `_cmd_*` handlers into a `commands.py` (or one file
per verb group) that imports the queue/state I/O and dispatch/
reconciliation logic as a library; keep `batch_queue.py` as the thin
argparse entry point plus `main`.

Why it matters: the CLI-handler region alone is over half the file and
is where most future edits will land (new subcommand, changed flag,
tweaked output format) — those edits currently require reading past
worktree lifecycle and dispatch/circuit-breaker code that shares no
state with them beyond the loaded `state` dict.

Risk: `_cmd_*` handlers, `_dispatch_entry`, and `_check_circuit_breaker`
share mutable `state`/`entries` dicts passed by reference: a split must
preserve call order and mutation visibility, not just move text. No
tests currently pin cross-function state-mutation ordering, so a
mechanical split risks silently reordering side effects.
**That last sentence is false.** It was refuted by measurement before the
split was attempted; see Correction below.

## Correction (2026-09-01) — the stated risk was wrong

The sentence above claiming "No tests currently pin cross-function
state-mutation ordering" is factually wrong, and it is left standing
rather than deleted because that claim is the reason this work was
deferred in the first place — a future reader has to be able to see that
the deferral rested on a false premise.

`loom-design/scripts/pipeline/test_pipeline_batch_queue.py` already held
85 test functions when this entry was filed
(`grep -c '^def test_' …`), 13 of them `next`-focused behavioural tests.
One of them,
`test_next_reconciles_running_entries_before_normal_scan`, pins exactly
the cross-function ordering the sentence said nothing pinned: it asserts
that a single `next` invocation runs reconcile's logic first — force-
FAILING a stranded RUNNING entry with a reconcile audit line — and only
then proceeds to dispatch the next QUEUED entry. A reordering split
fails that test rather than passing silently.

## Closed — shipped

Shipped on branch `loom-script-refactor-phase3`. `batch_queue.py` was
split into `queue_core.py` and `queue_commands.py`; `batch_queue.py` is
now the thin argparse entry point the "Candidate cut" above proposed,
keeping only `_build_parser`, `_add_next_subparser` and `main`. At the
time of writing, `wc -l` over the three files reports roughly 160 /
780 / 475 lines against the original 1369, with the pipeline suite
green.
