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

import tomllib
from pathlib import Path


def load_queue(queue_path: Path) -> list[dict]:
    """Parse ``[[change]]`` entries from queue_path, in file order.

    Each returned dict carries at least ``id``, ``plan``
    (project-relative path string), and ``budgets`` (dict with ``run``
    and optionally ``perStation``); ``models`` is included when present
    in the source entry. Resolves nothing (no filesystem checks beyond
    reading queue_path itself).
    """
    with queue_path.open("rb") as f:
        data = tomllib.load(f)
    return list(data.get("change", []))
