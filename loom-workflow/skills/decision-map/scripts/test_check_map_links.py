"""Tests for check_map_links.py — the Decisions-so-far link gate.

Grammar SSOT: references/map-format.md §MAP.md schema (Decisions-so-far
bullet) and §Command surface. Every fixture below is built through
map_store's own writers where possible; here we hand-write minimal
MAP.md/ticket text since map_store ships no writer yet — this mirrors
test_map_store.py's own fixture style.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import check_map_links

SCRIPT = Path(__file__).with_name("check_map_links.py")


def _map_md(decisions_body: str) -> str:
    return f"""---
map-id: demo
schema_version: 1
state: active
---

## Destination

Chart the thing.

## Notes

n/a

## Decisions-so-far

{decisions_body}

## Not-yet-specified (fog)

## Out-of-scope

## Parts

"""


def _ticket(status: str) -> str:
    return f"""---
type: task
status: {status}
claim: null
graduated-from: null
---

The ticket body.
"""


def _write_map(tmp_path: Path, decisions_body: str) -> Path:
    map_dir = tmp_path / "demo"
    (map_dir / "tickets").mkdir(parents=True)
    (map_dir / "MAP.md").write_text(_map_md(decisions_body), encoding="utf-8")
    return map_dir


def _run(map_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(map_dir), "--repo-root", str(map_dir)],
        capture_output=True,
        text=True,
    )


def test_flags_decision_line_without_closed_ticket(tmp_path):
    map_dir = _write_map(
        tmp_path, "- Picked the storage layer. (tickets/storage.md)"
    )
    (map_dir / "tickets" / "storage.md").write_text(_ticket("open"), encoding="utf-8")

    result = _run(map_dir)

    assert result.returncode == 2
    assert "storage.md" in result.stderr
    assert "Picked the storage layer" in result.stderr


def test_flags_dangling_ticket_link(tmp_path):
    map_dir = _write_map(
        tmp_path, "- Picked the storage layer. (tickets/missing.md)"
    )

    result = _run(map_dir)

    assert result.returncode == 2
    assert "missing.md" in result.stderr


def test_clean_map_exits_zero(tmp_path):
    map_dir = _write_map(
        tmp_path, "- Picked the storage layer. (tickets/storage.md)"
    )
    (map_dir / "tickets" / "storage.md").write_text(
        _ticket("closed"), encoding="utf-8"
    )

    result = _run(map_dir)

    assert result.returncode == 0


def test_operational_error_on_missing_map_dir(tmp_path):
    result = _run(tmp_path / "nonexistent")

    assert result.returncode == 1


def test_flags_escaping_ticket_link(tmp_path):
    # A link that resolves outside <map_dir>/tickets/ (e.g. via `../`)
    # must never be silently followed and read — it is a violation,
    # exit 2, naming the offending line — even when the escaped-to
    # file exists and is a genuinely closed ticket. Without a
    # containment check this would silently succeed (exit 0).
    map_dir = _write_map(
        tmp_path, "- Leaked outside the map. (../outside.md)"
    )
    (tmp_path / "outside.md").write_text(_ticket("closed"), encoding="utf-8")

    result = _run(map_dir)

    assert result.returncode == 2
    assert "../outside.md" in result.stderr


def test_check_links_function_directly(tmp_path):
    map_dir = _write_map(
        tmp_path, "- Picked the storage layer. (tickets/storage.md)"
    )
    (map_dir / "tickets" / "storage.md").write_text(
        _ticket("closed"), encoding="utf-8"
    )

    code, message = check_map_links.check_links(map_dir)

    assert code == 0
    assert "resolve to closed tickets" in message
