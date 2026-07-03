#!/usr/bin/env python3
"""Deterministic bookkeeping CLI for loom-pipeline batch mode.

Parses the human-editable ``QUEUE.toml`` (array-of-tables ``[[change]]``)
that lives in the target project's ``docs/loom/`` directory. Intent
(QUEUE.toml) is separate from state (machine-owned ``queue-state.json``,
not touched by this module yet) — see
docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md
§Settled open questions 1.

Pure stdlib (``tomllib``, Python 3.11+). Paths are resolved by the
caller; this module does not depend on cwd.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import tomllib
from pathlib import Path
from typing import NoReturn

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
    required). Malformed JSON fails loud with ``QueueError``, mirroring
    ``load_queue``'s no-improvised-defaults stance (FAIL_LOUD_NOTICE).
    """
    if not state_path.is_file():
        return {}

    try:
        with state_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        _fail(f'"{state_path}" is not valid JSON ({e}).', fn="load_state")


def save_state(state_path: Path, state: dict) -> None:
    """Write state to state_path atomically (tmp file + ``os.replace``).

    The tmp file is created in state_path's own directory so the rename
    is same-filesystem and therefore atomic; it is cleaned up on failure.
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
