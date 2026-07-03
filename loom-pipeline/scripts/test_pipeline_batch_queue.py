"""Tests for loom-pipeline/scripts/batch_queue.py."""
from __future__ import annotations

from pathlib import Path

import pytest

from batch_queue import QueueError, load_queue

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
    assert entries[0]["models"] == {"code": "sonnet", "review": "sonnet"}
    assert entries[1]["id"] == "fix-login-redirect"
    assert entries[1]["budgets"]["run"] == 150000
    assert entries[2]["id"] == "add-dark-mode"
    assert entries[2]["budgets"]["run"] == 180000


MISSING_FIELD_CASES = [
    pytest.param(
        """\
[[change]]
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
run = 200000
""",
        "id",
        id="missing-id",
    ),
    pytest.param(
        """\
[[change]]
id = "add-export-csv"
[change.budgets]
run = 200000
""",
        "plan",
        id="missing-plan",
    ),
    pytest.param(
        """\
[[change]]
id = "add-export-csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
perStation = { code = 40000 }
""",
        "budgets.run",
        id="missing-budgets-run",
    ),
]


@pytest.mark.parametrize("toml_text,missing_field", MISSING_FIELD_CASES)
def test_load_queue_fails_loud_on_missing_required_field(tmp_path, toml_text, missing_field):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(toml_text, encoding="utf-8")

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert missing_field in str(exc_info.value)


def test_load_queue_fails_loud_on_invalid_id_pattern(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(
        """\
[[change]]
id = "add export csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
run = 200000
""",
        encoding="utf-8",
    )

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert "add export csv" in str(exc_info.value)


def test_load_queue_fails_loud_on_non_string_id(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(
        """\
[[change]]
id = 42
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
run = 200000
""",
        encoding="utf-8",
    )

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert "42" in str(exc_info.value)
    assert "index 0" in str(exc_info.value)


def test_load_queue_fails_loud_on_id_containing_dotdot(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(
        """\
[[change]]
id = "a..b"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
run = 200000
""",
        encoding="utf-8",
    )

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert "a..b" in str(exc_info.value)


def test_load_queue_fails_loud_on_duplicate_ids(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(
        """\
[[change]]
id = "add-export-csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
run = 200000

[[change]]
id = "add-export-csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv-2.md"
[change.budgets]
run = 150000
""",
        encoding="utf-8",
    )

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert "add-export-csv" in str(exc_info.value)


def test_load_queue_fails_loud_on_missing_file(tmp_path):
    queue_path = tmp_path / "does-not-exist.toml"

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert str(queue_path) in str(exc_info.value)


def test_load_queue_fails_loud_on_invalid_toml(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text("this is not [ valid toml", encoding="utf-8")

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert str(queue_path) in str(exc_info.value)
