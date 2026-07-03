"""Tests for loom-pipeline/scripts/batch_queue.py."""
from __future__ import annotations

from pathlib import Path

from batch_queue import load_queue

QUEUE_TOML = """\
[[change]]
id = "add-export-csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
models = { code = "sonnet", review = "sonnet" }
[change.budgets]
run = 200000
perStation = { code = 40000, review = 20000 }

[[change]]
id = "fix-login-redirect"
plan = "docs/loom/plans/2026-07-03-fix-login-redirect.md"
[change.budgets]
run = 150000

[[change]]
id = "add-dark-mode"
plan = "docs/loom/plans/2026-07-03-add-dark-mode.md"
[change.budgets]
run = 180000
"""


def test_load_queue_returns_entries_in_file_order(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(QUEUE_TOML, encoding="utf-8")

    entries = load_queue(queue_path)

    assert len(entries) == 3
    assert [e["id"] for e in entries] == [
        "add-export-csv",
        "fix-login-redirect",
        "add-dark-mode",
    ]
    assert entries[0]["plan"] == "docs/loom/plans/2026-07-03-add-export-csv.md"
    assert entries[0]["budgets"]["run"] == 200000
    assert entries[1]["id"] == "fix-login-redirect"
    assert entries[1]["budgets"]["run"] == 150000
    assert entries[2]["id"] == "add-dark-mode"
    assert entries[2]["budgets"]["run"] == 180000
