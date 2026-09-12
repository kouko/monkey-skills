#!/usr/bin/env python3
"""Adversarially verify the committed dogfood evidence is public-safe."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
RAW = REPO / "docs/skill-dogfood/2026-09-12-capture-intent/raw"
REPORT = REPO / "docs/skill-dogfood/2026-09-12-capture-intent/report.md"
FORBIDDEN = re.compile(
    r"/Users/|/home/|/private/tmp|/tmp/|session_id|request_id|"
    r"messaging_socket_path|memory_paths|mcp_servers|permissionMode|"
    r"apiKeySource|\"signature\"|\bmsg_[A-Za-z0-9_-]+|"
    r"\btoolu_[A-Za-z0-9_-]+|"
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\b|"
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    re.IGNORECASE,
)


def _walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_sanitized_evidence_committed_public_safe() -> None:
    files = sorted(path for path in RAW.rglob("*") if path.is_file())
    assert len(files) == 79
    assert {path.suffix for path in files} == {".json", ".jsonl", ".md", ".txt"}

    json_count = jsonl_count = row_count = 0
    for path in files:
        text = path.read_text()
        assert not FORBIDDEN.search(text), path
        if path.suffix == ".json":
            json.loads(text)
            json_count += 1
        elif path.suffix == ".jsonl":
            jsonl_count += 1
            for line in text.splitlines():
                item = json.loads(line)
                row_count += 1
                assert item.get("type") not in {"system", "rate_limit_event"}
                for value in _walk(item):
                    if isinstance(value, dict) and "thinking" in value:
                        assert not str(value["thinking"]).strip()

    assert (json_count, jsonl_count, row_count) == (5, 48, 232)
    report = REPORT.read_text()
    assert not FORBIDDEN.search(report)
    assert "committed, sanitized execution evidence" in report
    assert "unsanitized streams remain local" in report


if __name__ == "__main__":
    test_sanitized_evidence_committed_public_safe()
