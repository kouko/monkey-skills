#!/usr/bin/env python3
"""Deterministic bookkeeping CLI for loom-pipeline batch mode.

The entry point: argparse wiring and ``main``. Intent (``QUEUE.toml``)
is separate from state (machine-owned ``queue-state.json``) — see
docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md
§Settled open questions 1. The ``_cmd_*`` subcommand handlers live in
the sibling module ``queue_commands``; the machinery they drive —
queue/state loading, the freeze gate, worktree lifecycle, the reconcile
engine and the circuit breaker — lives in ``queue_core``. Both are
imported below.

Pure stdlib (Python 3.11+). Paths are resolved by the caller; this
module does not depend on cwd. It does depend on sys.path: the two
sibling imports below are by bare name, so an importer must put this
file's own directory on ``sys.path`` first -- loading it by path
(``importlib.util.spec_from_file_location``) without that entry raises
``ModuleNotFoundError: No module named 'queue_commands'``.
"""
from __future__ import annotations

import argparse
import sys
from typing import Sequence

import queue_commands
import queue_core


def _build_parser() -> argparse.ArgumentParser:
    """Top-level argparse setup: ``mark``, ``mark-running``, ``reset``,
    ``force-fail``, ``status``, ``reconcile``, ``next`` subcommands."""
    parser = argparse.ArgumentParser(
        prog="batch_queue.py", description="loom-pipeline batch mode bookkeeping"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    mark_parser = subparsers.add_parser(
        "mark", help="record done/failed status for a queue entry"
    )
    mark_parser.add_argument("change_id")
    mark_parser.add_argument("status", choices=["done", "failed"])
    mark_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    mark_parser.add_argument("--run-id", dest="run_id")
    mark_parser.add_argument("--reason")
    mark_parser.set_defaults(func=queue_commands._cmd_mark)

    mark_running_parser = subparsers.add_parser(
        "mark-running",
        help="record runId + session-dir on an entry currently RUNNING",
    )
    mark_running_parser.add_argument("change_id")
    mark_running_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    mark_running_parser.add_argument(
        "--run-id", dest="run_id", required=True
    )
    mark_running_parser.add_argument(
        "--session-dir", dest="session_dir", required=True
    )
    mark_running_parser.set_defaults(func=queue_commands._cmd_mark_running)

    reset_parser = subparsers.add_parser(
        "reset",
        help="requeue a RUNNING or FAILED entry back to QUEUED (attempts+=1, audit line)",
    )
    reset_parser.add_argument("change_id")
    reset_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    reset_parser.add_argument("--reason", help="optional operator note for the audit line")
    reset_parser.set_defaults(func=queue_commands._cmd_reset)

    force_fail_parser = subparsers.add_parser(
        "force-fail",
        help="transition a RUNNING entry to FAILED (audit line; counts toward the circuit breaker)",
    )
    force_fail_parser.add_argument("change_id")
    force_fail_parser.add_argument(
        "--reason", required=True, help="operator note for the audit line"
    )
    force_fail_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    force_fail_parser.set_defaults(func=queue_commands._cmd_force_fail)

    status_parser = subparsers.add_parser(
        "status", help="print a one-screen overview of the queue"
    )
    status_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    status_parser.set_defaults(func=queue_commands._cmd_status)

    reconcile_parser = subparsers.add_parser(
        "reconcile",
        help="scan RUNNING entries against wf-record evidence: auto-FAIL on "
        "failed/killed, flag SUSPECT-COMPLETE/SUSPECT otherwise (also run "
        "at the top of `next`; never in `status`)",
    )
    reconcile_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    reconcile_parser.set_defaults(func=queue_commands._cmd_reconcile)

    _add_next_subparser(subparsers)

    return parser


def _add_next_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``next`` subcommand's arguments (split out of
    ``_build_parser`` to keep that function under the house length ceiling).
    """
    next_parser = subparsers.add_parser(
        "next",
        help="pick the next QUEUED entry, ready its worktree, print its Workflow args as JSON",
    )
    next_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    next_parser.add_argument(
        "--skills-root",
        dest="skills_root",
        required=True,
        help="absolute path to the installed loom-design plugin root",
    )
    next_parser.add_argument(
        "--queue",
        help="override path to QUEUE.toml (default: <project>/docs/loom/QUEUE.toml)",
    )
    next_parser.add_argument(
        "--override-halt",
        dest="override_halt",
        action="store_true",
        default=False,
        help="bypass the consecutive-FAILED circuit breaker (Task 10)",
    )
    next_parser.set_defaults(func=queue_commands._cmd_next)


def main(argv: Sequence[str] | None = None) -> int:
    """Parse argv and dispatch to the selected subcommand's ``func``.

    Catches ``QueueError`` at this single dispatch site: ``mark``/``status``
    already catch their own ``load_queue`` failures internally (so this is a
    no-op for them), but ``next`` can raise ``QueueError`` mid-scan via
    ``ensure_worktree``/``_teardown_worktree`` — this ensures that exits 1
    with a stderr message instead of propagating as a raw traceback.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except queue_core.QueueError as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
