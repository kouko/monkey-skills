"""Tests for a canonical delivery Brief; binding contract: delivery_binding.py::validate."""

from __future__ import annotations

import os
import sys
from pathlib import Path, PurePosixPath

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import delivery_binding  # noqa: E402
import map_store  # noqa: E402
import map_transaction  # noqa: E402
import start_delivery  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ticket(
    tmp_path: Path,
    *,
    ticket_type: str = "delivery",
    status: str = "claimed",
    schema_version: int = 3,
    blocked_by: str | None = None,
    promised_slice: str = "Deliver searchable outcome-map references.",
) -> tuple[Path, Path]:
    ticket = tmp_path / "docs/loom/maps/wayfinder/tickets/deliver-search.md"
    brief = tmp_path / "docs/loom/specs/deliver-search.md"
    _write(
        ticket.parent.parent / "MAP.md",
        f"---\nmap-id: wayfinder\nschema_version: {schema_version}\nstate: active\n---\n",
    )
    blocked = f"blocked-by: {blocked_by}\n" if blocked_by is not None else ""
    _write(
        ticket,
        f"---\ntype: {ticket_type}\nstatus: {status}\nclaim: codex, 2026-08-30\n{blocked}---\n"
        f"{promised_slice}\n",
    )
    return ticket, brief


def test_start_delivery_creates_reciprocal_binding_idempotently(tmp_path: Path) -> None:
    # @req: REQ-80
    """A claimed, unblocked v3 delivery enters loom-code through one Brief."""
    ticket = tmp_path / "docs/loom/maps/wayfinder/tickets/deliver-search.md"
    brief = tmp_path / "docs/loom/specs/deliver-search.md"
    _write(
        ticket.parent.parent / "MAP.md",
        "---\nmap-id: wayfinder\nschema_version: 3\nstate: active\n---\n",
    )
    _write(
        ticket,
        "---\ntype: delivery\nstatus: claimed\nclaim: codex, 2026-08-30\n---\n"
        "Deliver searchable outcome-map references.\n",
    )

    code, message = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code == 0, message
    ticket_relative = ticket.relative_to(tmp_path).as_posix()
    brief_text = brief.read_text(encoding="utf-8")
    assert "Deliver searchable outcome-map references." in brief_text
    assert "## Acceptance" in brief_text
    assert f"Outcome Map ticket: {ticket_relative}" in brief_text
    assert "brief: docs/loom/specs/deliver-search.md" in ticket.read_text(encoding="utf-8")
    assert delivery_binding.validate(ticket, repo_root=tmp_path)[0] == 0

    before_retry = (ticket.read_bytes(), brief.read_bytes())
    retry_code, retry_message = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert retry_code == 0, retry_message
    assert (ticket.read_bytes(), brief.read_bytes()) == before_retry
    assert list(brief.parent.glob("deliver-search*.md")) == [brief]


@pytest.mark.parametrize(
    ("ticket_type", "status", "schema_version", "blocked_by"),
    [
        ("research", "claimed", 3, None),
        ("delivery", "open", 3, None),
        ("delivery", "closed", 3, None),
        ("delivery", "withdrawn", 3, None),
        ("delivery", "claimed", 3, "other-ticket"),
        ("delivery", "claimed", 2, None),
    ],
    ids=["non-delivery", "open", "closed", "withdrawn", "blocked", "schema-v2"],
)
def test_start_delivery_refuses_ineligible_ticket_without_writes(
    tmp_path: Path,
    ticket_type: str,
    status: str,
    schema_version: int,
    blocked_by: str | None,
) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(
        tmp_path,
        ticket_type=ticket_type,
        status=status,
        schema_version=schema_version,
        blocked_by=blocked_by,
    )
    before = ticket.read_bytes()

    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code == 2
    assert ticket.read_bytes() == before
    assert not brief.exists()


def test_start_delivery_refuses_retired_map_without_writes(tmp_path: Path) -> None:
    # @req: REQ-86
    """An archived Map cannot acquire a new Brief relationship."""
    ticket, brief = _ticket(tmp_path)
    map_path = ticket.parent.parent / "MAP.md"
    _write(
        map_path,
        """---
map-id: wayfinder
schema_version: 3
state: active
---

## Destination

Preserve immutable delivery history.
user-ratified: kouko, 2026-08-30
- DA-1: Delivery history stays intact | state: open | kind: objective

## Notes

## Decisions-so-far

## Not-yet-specified (fog)

- F-1: decide whether renewed work is worthwhile

## Out-of-scope

""",
    )
    map_transaction.retire_map(
        map_path.parent,
        ratified_by="kouko",
        ratified_on="2026-08-30",
        reason="The outcome is no longer worth pursuing.",
        repo_root=tmp_path,
    )
    before = (map_path.read_bytes(), ticket.read_bytes())

    code, message = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code != 0, message
    assert (map_path.read_bytes(), ticket.read_bytes()) == before
    assert not brief.exists()


@pytest.mark.parametrize("map_state", ["charting", "clear"])
def test_start_delivery_requires_active_map_without_writes(
    tmp_path: Path, map_state: str
) -> None:
    # @req: REQ-86
    ticket, brief = _ticket(tmp_path)
    map_path = ticket.parent.parent / "MAP.md"
    _write(
        map_path,
        map_path.read_text(encoding="utf-8").replace(
            "state: active", f"state: {map_state}"
        ),
    )
    before = (map_path.read_bytes(), ticket.read_bytes())

    code, message = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code != 0, message
    assert (map_path.read_bytes(), ticket.read_bytes()) == before
    assert not brief.exists()


@pytest.mark.parametrize(
    "brief_path",
    ["/tmp/brief.md", "docs/loom/specs/../specs/brief.md"],
    ids=["absolute", "traversing"],
)
def test_start_delivery_refuses_unsafe_or_colliding_brief_path(
    tmp_path: Path, brief_path: str
) -> None:
    # @req: REQ-80
    ticket, _ = _ticket(tmp_path)
    before = ticket.read_bytes()

    code, _ = start_delivery.start_delivery(ticket, brief_path, repo_root=tmp_path)

    assert code == 2
    assert ticket.read_bytes() == before


def test_start_delivery_refuses_symlink_parent_collision_and_empty_slice(tmp_path: Path) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    outside = tmp_path.parent / "outside"
    outside.mkdir(exist_ok=True)
    brief.parent.symlink_to(outside, target_is_directory=True)
    before = ticket.read_bytes()

    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code == 2
    assert ticket.read_bytes() == before
    brief.parent.unlink()
    brief.parent.mkdir()
    _write(brief, "# Existing\n")
    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )
    assert code == 2
    assert ticket.read_bytes() == before

    ticket, brief = _ticket(tmp_path / "empty", promised_slice="")
    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path / "empty").as_posix(), repo_root=tmp_path / "empty"
    )
    assert code == 2
    assert not brief.exists()


def test_start_delivery_refuses_inconsistent_existing_binding(tmp_path: Path) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    _write(
        ticket,
        ticket.read_text(encoding="utf-8").replace(
            "---\nDeliver", "brief: docs/loom/specs/other.md\n---\nDeliver"
        ),
    )
    before = ticket.read_bytes()

    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code == 2
    assert ticket.read_bytes() == before
    assert not brief.exists()


@pytest.mark.parametrize("failure_point", ["brief", "ticket"])
def test_start_delivery_preserves_recoverable_orphan_on_partial_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure_point: str
) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    original_ticket = ticket.read_bytes()
    if failure_point == "brief":
        monkeypatch.setattr(
            start_delivery,
            "_replace_ticket",
            lambda *_args: (_ for _ in ()).throw(
                OSError("injected ticket replacement failure")
            ),
        )
    else:
        monkeypatch.setattr(
            delivery_binding, "validate", lambda *_args, **_kwargs: (2, "injected validation failure")
        )

    code, message = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code in {1, 2}, message
    assert ticket.read_bytes() == original_ticket
    assert brief.read_text(encoding="utf-8") == start_delivery._brief_text(
        PurePosixPath(ticket.relative_to(tmp_path).as_posix()),
        "Deliver searchable outcome-map references.",
    )


def test_start_delivery_recovers_an_orphaned_expected_brief(tmp_path: Path) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    ticket_relative = ticket.relative_to(tmp_path).as_posix()
    _write(
        brief,
        start_delivery._brief_text(
            PurePosixPath(ticket_relative), "Deliver searchable outcome-map references."
        ),
    )
    before = brief.read_bytes()

    code, message = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code == 0, message
    assert brief.read_bytes() == before
    assert delivery_binding.validate(ticket, repo_root=tmp_path)[0] == 0


def test_start_delivery_returns_operational_error_for_missing_ticket(tmp_path: Path) -> None:
    # @req: REQ-80
    missing = tmp_path / "docs/loom/maps/wayfinder/tickets/missing.md"

    code, _ = start_delivery.start_delivery(
        missing, "docs/loom/specs/missing.md", repo_root=tmp_path
    )

    assert code == 1


def test_start_delivery_preserves_binding_operational_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    assert start_delivery.start_delivery(ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path)[0] == 0
    monkeypatch.setattr(delivery_binding, "validate", lambda *_args, **_kwargs: (1, "injected unavailable binding"))

    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code == 1


def test_start_delivery_parent_swap_never_writes_outside_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    outside = tmp_path.parent / "outside-race"
    outside.mkdir(exist_ok=True)
    original_parent = brief.parent
    moved_parent = brief.parent.with_name("specs-before-swap")

    def swap_parent(_parent_fd: int, _leaf: str) -> None:
        original_parent.rename(moved_parent)
        original_parent.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(start_delivery, "_before_brief_write", swap_parent)
    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code != 0
    assert not (outside / brief.name).exists()


def test_start_delivery_refuses_concurrent_ticket_or_map_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    original_ticket = ticket.read_bytes()

    def change_ticket() -> None:
        _write(ticket, original_ticket.decode("utf-8") + "concurrent ticket change\n")

    monkeypatch.setattr(start_delivery, "_before_first_write", change_ticket)
    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )
    assert code != 0
    assert ticket.read_bytes() != original_ticket
    assert not brief.exists()

    ticket, brief = _ticket(tmp_path / "map")
    map_path = ticket.parent.parent / "MAP.md"
    original_map = map_path.read_bytes()

    def change_map() -> None:
        _write(map_path, original_map.decode("utf-8") + "concurrent map change\n")

    monkeypatch.setattr(start_delivery, "_before_first_write", lambda: None)
    monkeypatch.setattr(start_delivery, "_before_ticket_publish", change_map)
    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path / "map").as_posix(), repo_root=tmp_path / "map"
    )
    assert code != 0
    assert map_path.read_bytes() != original_map
    assert brief.read_text(encoding="utf-8") == start_delivery._brief_text(
        PurePosixPath(ticket.relative_to(tmp_path / "map").as_posix()),
        "Deliver searchable outcome-map references.",
    )


def test_start_delivery_ticket_replace_is_compare_and_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    original = ticket.read_text(encoding="utf-8")
    concurrent = original + "\nconcurrent final edit\n"

    def change_after_final_check() -> None:
        _write(ticket, concurrent)

    monkeypatch.setattr(
        start_delivery, "_before_ticket_replace", change_after_final_check, raising=False
    )
    code, message = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code != 0, message
    assert ticket.read_text(encoding="utf-8") == concurrent
    assert brief.read_text(encoding="utf-8") == start_delivery._brief_text(
        PurePosixPath(ticket.relative_to(tmp_path).as_posix()),
        "Deliver searchable outcome-map references.",
    )


def test_start_delivery_never_replaces_a_concurrently_created_brief(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    concurrent = "# Concurrent Brief\n"

    def create_competitor(parent_fd: int, leaf: str) -> None:
        fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=parent_fd)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(concurrent)

    monkeypatch.setattr(start_delivery, "_before_brief_write", create_competitor)
    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code != 0
    assert brief.read_text(encoding="utf-8") == concurrent
    assert "brief:" not in ticket.read_text(encoding="utf-8")


def test_start_delivery_does_not_remove_a_replaced_brief_during_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    concurrent = "# Concurrent replacement\n"
    map_path = ticket.parent.parent / "MAP.md"

    def replace_brief_then_change_map() -> None:
        brief.unlink()
        _write(brief, concurrent)
        _write(map_path, map_path.read_text(encoding="utf-8") + "changed\n")

    monkeypatch.setattr(start_delivery, "_before_ticket_publish", replace_brief_then_change_map)
    code, message = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code == 1
    assert "concurrent change" in message
    assert brief.read_text(encoding="utf-8") == concurrent


def test_orphan_recovery_refuses_a_brief_replaced_before_ticket_bind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    _write(
        brief,
        start_delivery._brief_text(
            PurePosixPath(ticket.relative_to(tmp_path).as_posix()),
            "Deliver searchable outcome-map references.",
        ),
    )
    original_ticket = ticket.read_bytes()
    concurrent = "# Replaced orphan\n"
    ticket_writes: list[str] = []
    original_replace = start_delivery._replace_at

    def replace_orphan() -> None:
        brief.unlink()
        _write(brief, concurrent)

    monkeypatch.setattr(start_delivery, "_before_ticket_publish", replace_orphan)
    def record_ticket_write(parent_fd: int, leaf: str, text: str) -> None:
        if leaf == ticket.name:
            ticket_writes.append(text)
        original_replace(parent_fd, leaf, text)

    monkeypatch.setattr(start_delivery, "_replace_at", record_ticket_write)
    code, _ = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code != 0
    assert ticket_writes == []
    assert ticket.read_bytes() == original_ticket
    assert brief.read_text(encoding="utf-8") == concurrent
