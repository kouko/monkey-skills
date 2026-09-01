#!/usr/bin/env python3
"""CLI command handlers for loom-pipeline batch mode.

The ``_cmd_*`` subcommand implementations behind ``batch_queue.py``'s
argparse wiring, plus the two helpers they share
(``_resolve_paths_and_validate_id``, ``_require_running``). Every piece
of queue/state machinery they drive — queue/state loading, the freeze
gate, worktree lifecycle, the reconcile engine and the circuit breaker —
lives in the sibling module ``queue_core`` and is imported below.

Pure stdlib (Python 3.11+). Paths are resolved by the caller; this
module does not depend on cwd.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import queue_core


def _resolve_paths_and_validate_id(
    args: argparse.Namespace, verb: str
) -> tuple[Path, Path] | int:
    """Shared queue-load + unknown-id preamble for the four state-mutating
    subcommands (``mark``, ``mark-running``, ``reset``, ``force-fail``).

    Resolves ``queue_path``/``state_path`` from ``args.project`` and loads
    the queue to validate ``args.change_id`` against it. On success returns
    ``(queue_path, state_path)``. On failure — a ``load_queue`` error, or
    ``args.change_id`` not present in the queue — prints the caller-facing
    error to stderr (prefixed with ``verb``, matching each subcommand's
    prior wording) and returns the process exit code ``1`` instead, so
    callers can do ``result = _resolve_paths_and_validate_id(args, "mark");
    if isinstance(result, int): return result``.
    """
    project_path = Path(args.project)
    queue_path = project_path / "docs" / "loom" / "QUEUE.toml"
    state_path = project_path / "docs" / "loom" / "queue-state.json"

    try:
        entries = queue_core.load_queue(queue_path)
    except queue_core.QueueError as e:
        print(str(e), file=sys.stderr)
        return 1

    known_ids = {entry["id"] for entry in entries}
    if args.change_id not in known_ids:
        print(
            f'{verb}: unknown change id "{args.change_id}" — not present in '
            f'"{queue_path}".',
            file=sys.stderr,
        )
        return 1

    return queue_path, state_path


def _require_running(
    existing: dict, change_id: str, verb: str, refusal_clause: str
) -> int | None:
    """Shared RUNNING-precursor guard for the three state-mutating
    subcommands that only accept a currently-``RUNNING`` entry —
    ``_cmd_mark``, ``_cmd_mark_running``, ``_cmd_force_fail`` (Rule of
    Three: the reject/print/return-1/zero-mutation block appeared
    identically in all three).

    Takes the already-loaded ``existing`` state record — the caller owns
    ``load_state``/the ``_state_lock`` span; this does NOT re-load state,
    so it stays safe to call from inside a lock already held. Returns
    ``1`` after printing a caller-facing refusal (verb-prefixed, with
    ``refusal_clause`` as the trailing per-command wording) to stderr when
    ``existing``'s recorded status is not ``RUNNING``; else returns
    ``None`` so the caller proceeds with its own mutation.
    """
    status = existing.get("status", queue_core.QUEUED)
    if status != "RUNNING":
        print(
            f'{verb}: entry "{change_id}" is not RUNNING '
            f"(status={status!r}) — refusing {refusal_clause}.",
            file=sys.stderr,
        )
        return 1
    return None


def _cmd_mark(args: argparse.Namespace) -> int:
    """Implements the ``mark`` subcommand — see ``batch_queue._build_parser``.

    Writes/updates the state record for ``args.change_id`` and returns a
    process exit code (0 on success, 1 on a caller-facing error such as an
    unknown change id — printed to stderr, never raised as an exception,
    since this is the CLI boundary). Status is stored uppercase (DONE /
    FAILED) to match ``effective_entries``'s vocabulary.

    Requires the entry's CURRENT recorded status to be ``RUNNING`` before
    accepting a terminal mark — mirroring ``_cmd_mark_running``'s own
    precursor-state guard (a terminal status is only reachable from
    RUNNING). A QUEUED entry (no state record — never dispatched) or an
    already-terminal one is a caller-facing error — printed to stderr,
    exit 1, no state mutation — instead of silently jumping straight to
    DONE/FAILED and dropping the work while the batch reports success.
    """
    resolved = _resolve_paths_and_validate_id(args, "mark")
    if isinstance(resolved, int):
        return resolved
    _, state_path = resolved

    with queue_core._state_lock(state_path):
        state = queue_core.load_state(state_path)
        existing = state.get(args.change_id, {})
        rejection = _require_running(
            existing,
            args.change_id,
            "mark",
            "to mark a terminal status without a prior dispatch",
        )
        if rejection is not None:
            return rejection

        record = dict(existing)
        record["status"] = args.status.upper()
        if args.run_id:
            record["runId"] = args.run_id
        if args.reason:
            record["reason"] = args.reason
        state[args.change_id] = record

        queue_core._test_rmw_sleep()
        queue_core.save_state(state_path, state)
    return 0


def _cmd_mark_running(args: argparse.Namespace) -> int:
    """Implements the ``mark-running`` subcommand — see
    ``batch_queue._build_parser``.

    Records ``runId`` + ``sessionDir`` on the state record for
    ``args.change_id``, called by the dispatcher immediately after
    ``Workflow()`` returns (design SSOT §4c Fix 1 revised design point 1 —
    closes the no-runId-at-RUNNING-write blocker; ``_dispatch_entry``
    itself has no runId yet at RUNNING-write time). Requires the entry's
    CURRENT recorded status to be ``RUNNING``: an unknown change id or an
    entry not in ``RUNNING`` (already terminal, or never dispatched) is a
    caller-facing error — printed to stderr, exit 1, no state mutation —
    mirroring ``_cmd_mark``'s error-reporting shape.
    """
    resolved = _resolve_paths_and_validate_id(args, "mark-running")
    if isinstance(resolved, int):
        return resolved
    _, state_path = resolved

    with queue_core._state_lock(state_path):
        state = queue_core.load_state(state_path)
        existing = state.get(args.change_id, {})
        rejection = _require_running(
            existing,
            args.change_id,
            "mark-running",
            "to record runId/sessionDir without mutation",
        )
        if rejection is not None:
            return rejection

        record = dict(existing)
        record["runId"] = args.run_id
        record["sessionDir"] = args.session_dir
        state[args.change_id] = record
        queue_core.save_state(state_path, state)
    return 0


def _cmd_reconcile(args: argparse.Namespace) -> int:
    """Implements the ``reconcile`` subcommand — see
    ``batch_queue._build_parser``. Also invoked at the top of ``next``
    (never in ``status``).

    Loads the queue + state, runs ``_reconcile_running_entries`` under the
    same ``_state_lock`` span as every other state-mutating subcommand, and
    prints the resulting listing lines to stdout (one per flagged entry).
    Returns a process exit code (0 on success, 1 when the queue file is
    missing/malformed — printed to stderr, mirroring ``_cmd_status``).
    """
    project_path = Path(args.project)
    queue_path = project_path / "docs" / "loom" / "QUEUE.toml"
    state_path = project_path / "docs" / "loom" / "queue-state.json"

    try:
        entries = queue_core.load_queue(queue_path)
    except queue_core.QueueError as e:
        print(str(e), file=sys.stderr)
        return 1

    with queue_core._state_lock(state_path):
        state = queue_core.load_state(state_path)
        lines = queue_core._reconcile_running_entries(entries, state)
        queue_core.save_state(state_path, state)

    for line in lines:
        print(line)
    return 0


def _cmd_reset(args: argparse.Namespace) -> int:
    """Implements the ``reset`` subcommand — see ``batch_queue._build_parser``.

    Requeues an entry currently ``RUNNING`` or ``FAILED`` back to
    ``QUEUED`` (design SSOT §4c Fix-1 point 4 — the Airflow
    clear/Temporal reset analog): ``attempts`` increments (initialized to
    0 when absent) and an audit line is appended. Any other current
    status (including unknown-id) is a caller-facing error — printed to
    stderr, exit 1, zero mutation — mirroring ``_cmd_mark_running``.

    Also pops ``runId``/``sessionDir``/``dispatched_at`` from the record:
    those name the crashed attempt's now-dead run, and a QUEUED entry has
    no live run — carrying them forward would leave a stale ``runId``
    sitting next to a terminal wf-record once Task 12's reconcile ships,
    which would misread the freshly re-dispatched attempt as the
    already-finished one and force-FAIL it.
    """
    resolved = _resolve_paths_and_validate_id(args, "reset")
    if isinstance(resolved, int):
        return resolved
    _, state_path = resolved

    with queue_core._state_lock(state_path):
        state = queue_core.load_state(state_path)
        existing = state.get(args.change_id, {})
        current_status = existing.get("status", queue_core.QUEUED)
        if current_status not in ("RUNNING", "FAILED"):
            print(
                f'reset: entry "{args.change_id}" is not RUNNING or FAILED '
                f"(status={current_status!r}) — refusing to requeue "
                "without mutation.",
                file=sys.stderr,
            )
            return 1

        record = dict(existing)
        record["status"] = queue_core.QUEUED
        record["attempts"] = record.get("attempts", 0) + 1
        for stale_field in ("runId", "sessionDir", "dispatched_at"):
            record.pop(stale_field, None)
        queue_core._append_audit_line(record, "reset", args.reason)
        state[args.change_id] = record
        queue_core.save_state(state_path, state)
    return 0


def _cmd_force_fail(args: argparse.Namespace) -> int:
    """Implements the ``force-fail`` subcommand — see
    ``batch_queue._build_parser``.

    Transitions an entry currently ``RUNNING`` to ``FAILED`` (design SSOT
    §4c Fix-1 point 4 — the mark-failed/terminate analog): an audit line
    is appended; the resulting FAILED status counts toward
    ``_check_circuit_breaker`` naturally (no separate breaker logic — it
    reads ``effective_entries`` status the same as any other FAILED
    entry). Any status other than RUNNING (including unknown-id) is a
    caller-facing error — printed to stderr, exit 1, zero mutation.
    """
    resolved = _resolve_paths_and_validate_id(args, "force-fail")
    if isinstance(resolved, int):
        return resolved
    _, state_path = resolved

    with queue_core._state_lock(state_path):
        state = queue_core.load_state(state_path)
        existing = state.get(args.change_id, {})
        rejection = _require_running(
            existing,
            args.change_id,
            "force-fail",
            "to transition without mutation",
        )
        if rejection is not None:
            return rejection

        record = dict(existing)
        record["status"] = "FAILED"
        queue_core._append_audit_line(record, "force-fail", args.reason)
        state[args.change_id] = record
        queue_core.save_state(state_path, state)
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    """Implements the ``status`` subcommand — see ``batch_queue._build_parser``.

    Prints a one-screen plain-text overview to stdout: one line per queue
    entry, in queue order (``effective_entries`` preserves ``load_queue``'s
    file order), carrying id + effective status + ``runId`` (when recorded)
    + ``reason`` (only for SKIPPED/FAILED — a record re-marked done can
    retain a stale ``reason`` field, so this guard is deliberate, not
    incidental), followed by a final totals line (count per status). This
    is the first thing a fresh session reads to take over a batch, so the
    format is kept grep-friendly and stable: one ``key=value`` per field
    after the id and status columns.

    Returns a process exit code (0 on success, 1 when the queue file is
    missing/malformed — printed to stderr, mirroring ``_cmd_mark``).
    """
    project_path = Path(args.project)
    queue_path = project_path / "docs" / "loom" / "QUEUE.toml"
    state_path = project_path / "docs" / "loom" / "queue-state.json"

    try:
        entries = queue_core.load_queue(queue_path)
    except queue_core.QueueError as e:
        print(str(e), file=sys.stderr)
        return 1

    with queue_core._state_lock(state_path):
        state = queue_core.load_state(state_path)
        merged = queue_core.effective_entries(entries, state)

        totals: dict[str, int] = {}
        for entry in merged:
            status = entry["status"]
            totals[status] = totals.get(status, 0) + 1

            fields = [entry["id"], status]
            if "runId" in entry:
                fields.append(f'runId={entry["runId"]}')
            if status in ("SKIPPED", "FAILED") and "reason" in entry:
                fields.append(f'reason={entry["reason"]}')
            print("  ".join(fields))

        totals_fields = " ".join(
            f"{status}={count}" for status, count in sorted(totals.items())
        )
        print(f"total={len(merged)} {totals_fields}".rstrip())
    return 0


_TERMINAL_STATUSES = frozenset({"DONE", "FAILED", "SKIPPED"})


def _cmd_next(args: argparse.Namespace) -> int:
    """Implements the ``next`` subcommand — see its registration in
    ``batch_queue._add_next_subparser``.

    Runs ``_reconcile_running_entries`` first (Task 12 — reconcile's logic,
    never ``_cmd_status``'s), so a stranded RUNNING entry with definitive
    wf-record evidence is force-FAILED (freeing up the circuit breaker /
    done check) before this scan below ever runs. Reconcile notices go to
    stderr, same channel as the skip/HALT notices below.

    Scans effective entries in queue order for the first one that is both
    ``QUEUED`` and eligible. An entry that fails ``check_frozen``
    (validator non-zero, or plan missing in the main checkout) is recorded
    ``SKIPPED`` with the predicate's reason, a one-line notice goes to
    stderr, and the scan advances to the next ``QUEUED`` entry — Task 9 of
    docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md
    ("ineligible entries are marked SKIPPED loudly, never silently").
    Nothing is ever silent and one bad entry never blocks the queue.

    **Invariant** (plan §Branch base note): ``ensure_worktree`` branches
    from the project's current HEAD, so freezing implies the change-folder
    + plan are committed — the worktree sees them too. That invariant can
    be violated by a plan edited/created after the freeze check ran but
    never committed, so a defensive re-check runs *between*
    ``ensure_worktree`` and recording ``RUNNING``: if
    ``<worktree_path>/<entry["plan"]>`` is not a file, this entry is ALSO
    recorded ``SKIPPED`` (reason names the uncommitted-plan cause) instead
    of ``RUNNING``, with the same notice-and-advance semantics as the
    freeze-predicate skip above — and the worktree + branch this call just
    created are torn down (``_teardown_worktree``), so a later re-queue
    starts clean instead of leaving an undiscoverable leftover.

    On the first entry that clears both checks: ``_dispatch_entry`` records
    ``RUNNING`` (+ ``branch``, ``worktree``) in state and prints ONE JSON
    object to stdout carrying the driver's ready-to-use Workflow args (see
    its docstring for the field contract). When no entry gets dispatched
    (empty queue, or every remaining ``QUEUED`` entry got skipped), ``done``
    is derived from ``terminal_count == total`` (Task 13, design SSOT §4c
    Fix 1 revised design point 5) rather than assumed: DONE/FAILED/SKIPPED
    are the terminal set (SKIPPED has no automatic path back to QUEUED, so
    it counts as final here the same way it already does for dispatch
    purposes). If any entry is still QUEUED or RUNNING, ``{"done": false}``
    is printed alongside a ``non_terminal`` list (id + status + reason per
    entry, via ``_describe_non_terminal_entry``) instead of silently
    claiming the batch is finished. Exits 0 either way.

    **Circuit breaker** (Task 10, plan §Settled open questions 3): before
    selecting, ``_halt_notice_if_tripped`` scans for two consecutive FAILED
    entries among the most recent terminal (DONE/FAILED) outcomes. If
    tripped, this exits 3 with a HALT message naming both ids instead of
    scanning at all — unless ``args.override_halt`` is set, which bypasses
    the check entirely.

    Only machine-readable JSON goes to stdout (the dispatch payload, or
    ``{"done": true}``); all human-facing notices (skip reasons, the HALT
    message) go to stderr, mirroring ``_cmd_mark``/``_cmd_status``. A
    ``QueueError`` raised mid-scan by ``ensure_worktree``/
    ``_teardown_worktree`` is not caught here — ``main`` catches it at the
    dispatch level so it exits 1 like a ``load_queue`` failure, instead of
    propagating as a raw traceback.
    """
    project_path = Path(args.project).resolve()
    skills_root = Path(args.skills_root).resolve()
    queue_path = (
        Path(args.queue) if args.queue else project_path / "docs" / "loom" / "QUEUE.toml"
    )
    state_path = project_path / "docs" / "loom" / "queue-state.json"

    try:
        entries = queue_core.load_queue(queue_path)
    except queue_core.QueueError as e:
        print(str(e), file=sys.stderr)
        return 1

    with queue_core._state_lock(state_path):
        state = queue_core.load_state(state_path)

        # Task 12: reconcile RUNNING entries against wf-record evidence
        # BEFORE the normal scan (never inside _cmd_status — that stays a
        # pure query). Mutates `state` in place for any AUTO-FAILED
        # transitions; must be saved here since a `{"done": true}` or
        # skip-only run below may otherwise never call save_state again.
        reconcile_lines = queue_core._reconcile_running_entries(entries, state)
        if reconcile_lines:
            queue_core.save_state(state_path, state)
            for line in reconcile_lines:
                print(line, file=sys.stderr)

        merged = queue_core.effective_entries(entries, state)

        if queue_core._halt_notice_if_tripped(merged, args.override_halt):
            return 3

        for entry in merged:
            if entry["status"] != queue_core.QUEUED:
                continue

            eligible, reason = queue_core.check_frozen(entry, project_path, skills_root)
            if not eligible:
                queue_core._skip_entry(state, state_path, entry["id"], reason)
                continue

            worktree_path, branch = queue_core.ensure_worktree(project_path, entry["id"])
            plan_path = (worktree_path / entry["plan"]).resolve()

            if not plan_path.is_file():
                queue_core._teardown_worktree(project_path, worktree_path, branch)
                queue_core._skip_entry(
                    state,
                    state_path,
                    entry["id"],
                    queue_core._uncommitted_plan_reason(entry["id"], plan_path),
                )
                continue

            queue_core._dispatch_entry(
                state, state_path, entry, worktree_path, plan_path, skills_root, branch
            )
            return 0

        final_merged = queue_core.effective_entries(entries, state)
        non_terminal = [
            e for e in final_merged if e["status"] not in _TERMINAL_STATUSES
        ]
        if non_terminal:
            payload = {
                "done": False,
                "non_terminal": [
                    queue_core._describe_non_terminal_entry(e, state) for e in non_terminal
                ],
            }
        else:
            payload = {"done": True}
        print(json.dumps(payload))
        return 0
