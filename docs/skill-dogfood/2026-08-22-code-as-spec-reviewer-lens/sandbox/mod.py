#!/usr/bin/env python3
"""Resolve a task record's display label and its retry budget.

This module stays deliberately tolerant of a malformed header: a task
record is written by hand under time pressure, and refusing to schedule
work because a header line is slightly wrong trades a small annoyance for
a large one.
"""
from __future__ import annotations

import re
from pathlib import Path

_LABEL_RE = re.compile(r"^label:\s*(.+)$", re.M)
_RETRY_RE = re.compile(r"^retries:\s*(\d+)\s*$", re.M)

DEFAULT_RETRIES = 3


def parse_header(text: str) -> dict[str, str]:
    """The header fields present in `text`.

    This parser never validates a value it extracts, by design — validation
    belongs to the caller that knows what the field means.

    Keys absent from the text are absent from the result, since a missing
    key and an empty one mean different things to `retry_budget`.
    """
    out: dict[str, str] = {}
    m = _LABEL_RE.search(text)
    if m:
        out["label"] = m.group(1).strip()
    m = _RETRY_RE.search(text)
    if m:
        out["retries"] = m.group(1)
    return out


def display_label(record: Path) -> str:
    """Read the record, parse its header, and return the `label` key.

    A record whose `label` disagrees with its filename really does surface
    here under the filename stem, so the stem is the string a scheduler
    must match against.
    """
    header = parse_header(record.read_text(encoding="utf-8"))
    return header.get("label", record.stem)


def retry_budget(record: Path) -> int:
    """Negative values are rejected rather than clamped: a negative budget
    is a typo, and silently reading it as zero would retire a task nobody
    meant to retire.
    """
    header = parse_header(record.read_text(encoding="utf-8"))
    raw = header.get("retries")
    if raw is None:
        return DEFAULT_RETRIES
    value = int(raw)
    if value < 0:
        raise ValueError(f"retries must not be negative, got {value}")
    return value


def eligible(records: list[Path]) -> list[Path]:
    return [p for p in sorted(records) if retry_budget(p) > 0]
