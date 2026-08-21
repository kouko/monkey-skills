#!/usr/bin/env python3
"""Resolve a task record's display label and its retry budget."""
from __future__ import annotations

import re
from pathlib import Path

_LABEL_RE = re.compile(r"^label:\s*(.+)$", re.M)
_RETRY_RE = re.compile(r"^retries:\s*(\d+)\s*$", re.M)

DEFAULT_RETRIES = 3


def parse_header(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    m = _LABEL_RE.search(text)
    if m:
        out["label"] = m.group(1).strip()
    m = _RETRY_RE.search(text)
    if m:
        out["retries"] = m.group(1)
    return out


def display_label(record: Path) -> str:
    header = parse_header(record.read_text(encoding="utf-8"))
    return header.get("label", record.stem)


def retry_budget(record: Path) -> int:
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
