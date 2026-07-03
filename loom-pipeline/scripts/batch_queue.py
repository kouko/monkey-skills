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

import re
import tomllib
from pathlib import Path

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


def load_queue(queue_path: Path) -> list[dict]:
    """Parse ``[[change]]`` entries from queue_path, in file order.

    Each returned dict carries at least ``id``, ``plan``
    (project-relative path string), and ``budgets`` (dict with ``run``
    and optionally ``perStation``); ``models`` is included when present
    in the source entry. Resolves nothing (no filesystem checks beyond
    reading queue_path itself).

    Raises ``QueueError`` naming the offending entry (its ``id``, or its
    index when ``id`` itself is absent) and the specific problem when:
    the file is missing or not valid TOML; an entry is missing ``id``,
    ``plan``, or ``budgets.run``; ``id`` violates the changeId allow-list
    ``^[A-Za-z0-9._-]+$`` or contains ``..``; or two entries share an
    ``id``. No improvised defaults — see FAIL_LOUD_NOTICE.
    """
    if not queue_path.is_file():
        raise QueueError(
            f'load_queue: queue file not found at "{queue_path}". {FAIL_LOUD_NOTICE}'
        )

    try:
        with queue_path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise QueueError(
            f'load_queue: "{queue_path}" is not valid TOML ({e}). {FAIL_LOUD_NOTICE}'
        ) from e

    entries = list(data.get("change", []))
    seen_ids: set[str] = set()
    for index, entry in enumerate(entries):
        label = entry.get("id") or f"<entry at index {index}>"

        for field in ("id", "plan"):
            if not entry.get(field):
                raise QueueError(
                    f'load_queue: entry "{label}" is missing required field '
                    f'"{field}". {FAIL_LOUD_NOTICE}'
                )

        budgets = entry.get("budgets")
        if not isinstance(budgets, dict) or not budgets.get("run"):
            raise QueueError(
                f'load_queue: entry "{label}" is missing required field '
                f'"budgets.run". {FAIL_LOUD_NOTICE}'
            )

        entry_id = entry["id"]
        if not _CHANGE_ID_ALLOWED_PATTERN.match(entry_id) or ".." in entry_id:
            raise QueueError(
                f'load_queue: entry "{label}" has "id" that must match '
                f"{_CHANGE_ID_ALLOWED_PATTERN.pattern} (letters, digits, dot, "
                f'underscore, hyphen only; no ".."); received {entry_id!r}. '
                f"{FAIL_LOUD_NOTICE}"
            )

        if entry_id in seen_ids:
            raise QueueError(
                f'load_queue: duplicate "id" {entry_id!r} in "{queue_path}". '
                f"{FAIL_LOUD_NOTICE}"
            )
        seen_ids.add(entry_id)

    return entries
