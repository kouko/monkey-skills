#!/usr/bin/env python3
"""Deterministic bookkeeping CLI for loom-pipeline batch mode.

Parses the human-editable ``QUEUE.toml`` (array-of-tables ``[[change]]``)
that lives in the target project's ``docs/loom/`` directory. Intent
(QUEUE.toml) is separate from state (machine-owned ``queue-state.json``,
loaded/written via ``load_state``/``save_state`` below and merged onto
queue entries by ``effective_entries``) — see
docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md
§Settled open questions 1.

Pure stdlib (``tomllib``, Python 3.11+). Paths are resolved by the
caller; this module does not depend on cwd.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import NoReturn, Sequence

# Status a queue entry has when no state record exists for its id yet.
QUEUED = "QUEUED"

# changeId becomes a path segment (docs/loom/<id>/...) — allow-list rather
# than deny-list, same reasoning as driver_10_guard.js's guardArgs():
# scripts/driver_10_guard.js:112-123.
_CHANGE_ID_ALLOWED_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")

FAIL_LOUD_NOTICE = (
    "fail-loud: refusing to improvise a missing or invalid queue entry — "
    "no defaults, no silent skip; load_queue FAILS rather than guessing."
)


class QueueError(Exception):
    """Raised when QUEUE.toml is missing, unparseable, or malformed.

    Mirrors driver_10_guard.js's guardArgs() no-improvised-defaults stance.
    """


def _fail(msg: str, *, fn: str = "load_queue") -> NoReturn:
    """Raise QueueError in the house fail-loud shape (single message site).

    ``fn`` names the failing function in the message prefix — callers other
    than ``load_queue`` (e.g. ``load_state``) pass their own name.
    """
    raise QueueError(f"{fn}: {msg} {FAIL_LOUD_NOTICE}")


def load_queue(queue_path: Path) -> list[dict]:
    """Parse ``[[change]]`` entries from queue_path, in file order.

    Each returned dict carries at least ``id``, ``plan``
    (project-relative path string), and ``budgets`` (dict with ``run``
    and optionally ``perStation``); ``models`` is included when present
    in the source entry. Resolves nothing (no filesystem checks beyond
    reading queue_path itself).

    Raises ``QueueError`` naming the offending entry (its ``id``, or its
    index when ``id`` is absent or not a string) and the specific problem
    when: the file is missing or not valid TOML; an entry is missing
    ``id``, ``plan``, or ``budgets.run``; ``id`` is not a string, violates
    the changeId allow-list ``^[A-Za-z0-9._-]+$``, or contains ``..``; or
    two entries share an ``id``. No improvised defaults — see
    FAIL_LOUD_NOTICE.
    """
    if not queue_path.is_file():
        _fail(f'queue file not found at "{queue_path}".')

    try:
        with queue_path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        _fail(f'"{queue_path}" is not valid TOML ({e}).')

    entries = list(data.get("change", []))
    seen_ids: set[str] = set()
    for index, entry in enumerate(entries):
        entry_id = entry.get("id")
        index_label = f"<entry at index {index}>"
        label = entry_id if isinstance(entry_id, str) and entry_id else index_label

        for field in ("id", "plan"):
            if not entry.get(field):
                _fail(f'entry "{label}" is missing required field "{field}".')

        budgets = entry.get("budgets")
        if not isinstance(budgets, dict) or not budgets.get("run"):
            _fail(f'entry "{label}" is missing required field "budgets.run".')

        if not isinstance(entry_id, str):
            _fail(
                f'entry "{index_label}" has "id" of wrong type — must be a '
                f"TOML string; received {entry_id!r} "
                f"({type(entry_id).__name__})."
            )

        if not _CHANGE_ID_ALLOWED_PATTERN.match(entry_id) or ".." in entry_id:
            _fail(
                f'entry "{label}" has "id" that must match '
                f"{_CHANGE_ID_ALLOWED_PATTERN.pattern} (letters, digits, dot, "
                f'underscore, hyphen only; no ".."); received {entry_id!r}.'
            )

        if entry_id in seen_ids:
            _fail(f'duplicate "id" {entry_id!r} in "{queue_path}".')
        seen_ids.add(entry_id)

    return entries


def load_state(state_path: Path) -> dict:
    """Load the machine-owned state file (``queue-state.json`` by convention).

    A missing file is a fresh batch and returns ``{}`` — this is not an
    error (unlike a missing QUEUE.toml, which is human-authored and
    required). Malformed JSON, or valid JSON whose top level is not an
    object (the state file is an object keyed by change id), fails loud
    with ``QueueError``, mirroring ``load_queue``'s
    no-improvised-defaults stance (FAIL_LOUD_NOTICE).
    """
    if not state_path.is_file():
        return {}

    try:
        with state_path.open("r", encoding="utf-8") as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        _fail(f'"{state_path}" is not valid JSON ({e}).', fn="load_state")

    if not isinstance(state, dict):
        _fail(
            f'"{state_path}" has wrong top-level JSON type — must be an '
            f"object keyed by change id; received {type(state).__name__}.",
            fn="load_state",
        )
    return state


def save_state(state_path: Path, state: dict) -> None:
    """Write state to state_path atomically (tmp file + ``os.replace``).

    The tmp file is created in state_path's own directory so the rename
    is same-filesystem and therefore atomic; it is cleaned up on failure.
    Precondition: ``state_path.parent`` must already exist (``docs/loom/``
    by convention) — this function does not create directories.
    """
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{state_path.name}.", suffix=".tmp", dir=state_path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp_name, state_path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def effective_entries(entries: list[dict], state: dict) -> list[dict]:
    """Merge ``load_queue`` entries with recorded ``load_state`` statuses.

    Returns a new list of shallow-copied entry dicts (inputs are not
    mutated), each augmented with ``status`` (``QUEUED`` when the entry's
    id has no state record) and, when present in the record, ``runId``,
    ``branch``, ``worktree``, ``reason``.
    """
    merged = []
    for entry in entries:
        record = state.get(entry["id"], {})
        effective = dict(entry)
        effective["status"] = record.get("status", QUEUED)
        for field in ("runId", "branch", "worktree", "reason"):
            if field in record:
                effective[field] = record[field]
        merged.append(effective)
    return merged


def check_frozen(entry: dict, project_path: Path, skills_root: Path) -> tuple[bool, str]:
    """Freeze predicate: loom-spec validator exit-0 AND plan file present.

    Decision §"Freeze predicate = loom-spec validator exit-0 + plan
    written" (docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md
    Task 4). Runs ``python3 <skills_root>/loom-spec/scripts/
    validate_spec_output.py <project_path>/docs/loom/<id>`` via subprocess
    (invocation convention: driver_40_seg2.js:106-127) and requires
    ``<project_path>/<entry["plan"]>`` to exist.

    Returns ``(eligible, reason)`` — **never raises for ineligibility**,
    including a path-traversal attempt in ``entry["plan"]``: the resolved
    plan path is guarded to stay inside ``project_path`` (``Path.resolve()``
    + ``relative_to`` check), and a traversal is reported as an eligibility
    failure via the return tuple, not a raised ``QueueError``. This keeps
    one failure channel for this function (contrast ``load_queue``, which
    raises ``QueueError`` for structural defects at parse time — this
    function runs later, per-entry, and its whole contract is "tell me why
    not" rather than "refuse to load").
    """
    project_path = Path(project_path).resolve()
    entry_id = entry["id"]

    # Trust-boundary re-assertion: entry["id"] is trusted-by-contract
    # (load_queue already validated it) — re-check here so the boundary is
    # explicit rather than emergent.
    if not _CHANGE_ID_ALLOWED_PATTERN.match(entry_id) or ".." in entry_id:
        _fail(
            f'entry "{entry_id}" has "id" that must match '
            f"{_CHANGE_ID_ALLOWED_PATTERN.pattern} (letters, digits, dot, "
            f'underscore, hyphen only; no ".."); received {entry_id!r}.',
            fn="check_frozen",
        )

    plan_path = (project_path / entry["plan"]).resolve()
    try:
        plan_path.relative_to(project_path)
    except ValueError:
        return (
            False,
            f'entry "{entry_id}" plan "{entry["plan"]}" resolves to '
            f'"{plan_path}", outside project_path "{project_path}" '
            "(path traversal).",
        )

    if not plan_path.is_file():
        return (False, f'entry "{entry_id}" plan not found at "{plan_path}".')

    change_dir = project_path / "docs" / "loom" / entry_id
    validator_script = Path(skills_root) / "loom-spec" / "scripts" / "validate_spec_output.py"
    result = subprocess.run(
        ["python3", str(validator_script), str(change_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return (
            False,
            f'entry "{entry_id}" failed the freeze predicate — validator '
            f"exited {result.returncode} for \"{change_dir}\" (ran: python3 "
            f'{validator_script} {change_dir}).',
        )

    return (True, f'entry "{entry_id}" is frozen — validator exit 0, plan present.')


def ensure_worktree(project_path: Path, change_id: str) -> tuple[Path, str]:
    """Create (or reuse) the worktree + branch for ``change_id``.

    Branch ``loom/<change_id>``, worktree
    ``<project_path>/.worktrees/loom-<change_id>`` — the house convention
    (using-git-worktrees/SKILL.md §The ``.worktrees/`` convention). Creates
    via ``git -C <project_path> worktree add -b <branch> <worktree_path>``
    from current HEAD (list-form subprocess args, no shell=True).

    Idempotent: if the worktree directory already exists and is checked
    out on ``branch``, returns it without error — no second ``git
    worktree add``.

    Fails loud with ``QueueError`` on any conflict this call did not
    create: the branch exists without the worktree directory, the
    directory exists but isn't checked out on ``branch`` (or isn't a git
    checkout at all), or the ``git worktree add`` command itself fails
    (git's stderr is included in the message).
    """
    # Trust-boundary re-assertion: change_id is trusted-by-contract
    # (callers derive it from load_queue's already-validated entries) —
    # re-check here so the boundary is explicit rather than emergent.
    if not _CHANGE_ID_ALLOWED_PATTERN.match(change_id) or ".." in change_id:
        _fail(
            f'change_id must match {_CHANGE_ID_ALLOWED_PATTERN.pattern} '
            f'(letters, digits, dot, underscore, hyphen only; no ".."); '
            f"received {change_id!r}.",
            fn="ensure_worktree",
        )

    project_path = Path(project_path)
    branch = f"loom/{change_id}"
    worktree_path = project_path / ".worktrees" / f"loom-{change_id}"

    if worktree_path.is_dir():
        head = subprocess.run(
            ["git", "-C", str(worktree_path), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
        )
        if head.returncode == 0 and head.stdout.strip() == branch:
            return worktree_path, branch
        found = head.stdout.strip() if head.returncode == 0 else head.stderr.strip()
        _fail(
            f'worktree path "{worktree_path}" already exists but is not '
            f'checked out on branch "{branch}" (found {found!r}) — refusing '
            "to touch a conflict this call did not create.",
            fn="ensure_worktree",
        )

    branch_check = subprocess.run(
        ["git", "-C", str(project_path), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        capture_output=True,
        text=True,
    )
    if branch_check.returncode == 0:
        _fail(
            f'branch "{branch}" already exists in "{project_path}" but its '
            f'worktree "{worktree_path}" does not — refusing to touch a '
            "conflict this call did not create.",
            fn="ensure_worktree",
        )

    add_result = subprocess.run(
        ["git", "-C", str(project_path), "worktree", "add", "-b", branch, str(worktree_path)],
        capture_output=True,
        text=True,
    )
    if add_result.returncode != 0:
        _fail(
            f'"git worktree add -b {branch} {worktree_path}" failed in '
            f'"{project_path}" (exit {add_result.returncode}): '
            f"{add_result.stderr.strip()}",
            fn="ensure_worktree",
        )

    return worktree_path, branch


def _cmd_mark(args: argparse.Namespace) -> int:
    """Implements the ``mark`` subcommand — see ``main``'s subparser setup.

    Writes/updates the state record for ``args.change_id`` and returns a
    process exit code (0 on success, 1 on a caller-facing error such as an
    unknown change id — printed to stderr, never raised as an exception,
    since this is the CLI boundary). Status is stored uppercase (DONE /
    FAILED) to match ``effective_entries``'s vocabulary.
    """
    project_path = Path(args.project)
    queue_path = project_path / "docs" / "loom" / "QUEUE.toml"
    state_path = project_path / "docs" / "loom" / "queue-state.json"

    try:
        entries = load_queue(queue_path)
    except QueueError as e:
        print(str(e), file=sys.stderr)
        return 1

    known_ids = {entry["id"] for entry in entries}
    if args.change_id not in known_ids:
        print(
            f'mark: unknown change id "{args.change_id}" — not present in '
            f'"{queue_path}".',
            file=sys.stderr,
        )
        return 1

    state = load_state(state_path)
    record = dict(state.get(args.change_id, {}))
    record["status"] = args.status.upper()
    if args.run_id:
        record["runId"] = args.run_id
    if args.reason:
        record["reason"] = args.reason
    state[args.change_id] = record

    save_state(state_path, state)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Top-level argparse setup. Subparser structure left open for the
    ``next``/``status`` subcommands added by later tasks.
    """
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
    mark_parser.set_defaults(func=_cmd_mark)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
