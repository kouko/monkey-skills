"""Start delivery writes an intent bound to the Map, never a Brief.

Loom 1.0 deleted the delivery ticket and its reciprocal Brief. These tests
pin the replacement: one intent file under `docs/loom/intent/`, one
`delivery-intent:` line under the Destination acceptance criterion it
serves, and refusals that keep a Map from opening an arc it cannot own.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import map_store  # noqa: E402
import start_delivery  # noqa: E402


MAP_TEMPLATE = """---
map-id: {map_id}
schema_version: 3
state: {state}
---

## Destination

Ship the thing.

user-ratified: tester, 2026-09-03

- DA-1: the thing ships | state: open | kind: objective
- DA-2: it stays shipped | state: satisfied | kind: objective | evidence: docs/loom/evidence/shipped.md

## Notes

## Decisions-so-far

## Not-yet-specified (fog)

- F-1: unknown

## Out-of-scope
"""


def _map(tmp_path: Path, *, state: str = "active", map_id: str = "demo") -> Path:
    map_dir = tmp_path / "docs" / "loom" / "maps" / map_id
    (map_dir / "tickets").mkdir(parents=True)
    (map_dir / "MAP.md").write_text(
        MAP_TEMPLATE.format(map_id=map_id, state=state), encoding="utf-8"
    )
    return map_dir


def test_creates_intent_and_lists_it_under_the_criterion(tmp_path: Path) -> None:
    map_dir = _map(tmp_path)

    code, message = start_delivery.start_delivery(
        map_dir, "DA-1", "2026-09-03-ship-it", repo_root=tmp_path
    )

    assert code == 0, message
    intent = tmp_path / "docs" / "loom" / "intent" / "2026-09-03-ship-it.md"
    text = intent.read_text(encoding="utf-8")
    assert "originator: map:demo" in text
    assert "map: demo" in text
    assert "status: open" in text
    assert "## Acceptance" in text
    notes = map_store.read_map(map_dir).sections["Notes"]
    assert "- delivery-intent: DA-1 | docs/loom/intent/2026-09-03-ship-it.md" in notes


def test_writes_no_brief_and_no_ticket_binding(tmp_path: Path) -> None:
    map_dir = _map(tmp_path)

    start_delivery.start_delivery(
        map_dir, "DA-1", "plain-slice", repo_root=tmp_path
    )

    assert not (tmp_path / "docs" / "loom" / "briefs").exists()
    assert list((map_dir / "tickets").iterdir()) == []
    assert "brief" not in (map_dir / "MAP.md").read_text(encoding="utf-8").lower()


def test_reuse_is_idempotent(tmp_path: Path) -> None:
    map_dir = _map(tmp_path)
    first = start_delivery.start_delivery(
        map_dir, "DA-1", "again", repo_root=tmp_path
    )
    intent = tmp_path / "docs" / "loom" / "intent" / "again.md"
    intent.write_text(
        intent.read_text(encoding="utf-8").replace("status: open", "status: confirmed 2026-09-03"),
        encoding="utf-8",
    )

    second = start_delivery.start_delivery(
        map_dir, "DA-1", "again", repo_root=tmp_path
    )

    assert first[0] == 0 and second[0] == 0, (first, second)
    assert "reused" in second[1]
    assert "status: confirmed 2026-09-03" in intent.read_text(encoding="utf-8")
    notes = map_store.read_map(map_dir).sections["Notes"]
    assert notes.count("delivery-intent: DA-1") == 1


def test_refuses_an_intent_bound_to_another_map(tmp_path: Path) -> None:
    map_dir = _map(tmp_path)
    foreign = tmp_path / "docs" / "loom" / "intent" / "foreign.md"
    foreign.parent.mkdir(parents=True)
    foreign.write_text("# foreign\nmap: elsewhere\nstatus: open\n", encoding="utf-8")

    code, message = start_delivery.start_delivery(
        map_dir, "DA-1", "foreign", repo_root=tmp_path
    )

    assert code == 2, message
    assert "map:demo" in message


@pytest.mark.parametrize(
    ("da_id", "change_id", "fragment"),
    [
        ("DA-9", "slice", "not a Destination acceptance criterion"),
        ("DA-2", "slice", "already satisfied"),
        ("D1", "slice", "DA-<n>"),
        ("DA-1", "Not A Slug", "lowercase letters"),
    ],
)
def test_structural_refusals(
    tmp_path: Path, da_id: str, change_id: str, fragment: str
) -> None:
    map_dir = _map(tmp_path)

    code, message = start_delivery.start_delivery(
        map_dir, da_id, change_id, repo_root=tmp_path
    )

    assert code == 2, message
    assert fragment in message
    assert not (tmp_path / "docs" / "loom" / "intent").exists()


def test_refuses_a_charting_map(tmp_path: Path) -> None:
    map_dir = _map(tmp_path, state="charting")

    code, message = start_delivery.start_delivery(
        map_dir, "DA-1", "too-early", repo_root=tmp_path
    )

    assert code == 2, message
    assert "charting" in message
