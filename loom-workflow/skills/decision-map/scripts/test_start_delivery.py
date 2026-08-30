"""Tests for entering a claimed delivery arc through its canonical Brief."""

from __future__ import annotations

import sys
from pathlib import Path, PurePosixPath

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import delivery_binding  # noqa: E402
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
def test_start_delivery_rolls_back_partial_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure_point: str
) -> None:
    # @req: REQ-80
    ticket, brief = _ticket(tmp_path)
    original_ticket = ticket.read_bytes()
    original_replace = start_delivery._replace_at

    if failure_point == "brief":
        def fail_ticket(parent_fd: int, leaf: str, text: str) -> None:
            if leaf == ticket.name:
                raise OSError("injected ticket replacement failure")
            original_replace(parent_fd, leaf, text)

        monkeypatch.setattr(start_delivery, "_replace_at", fail_ticket)
    else:
        monkeypatch.setattr(
            delivery_binding, "validate", lambda *_args, **_kwargs: (2, "injected validation failure")
        )

    code, message = start_delivery.start_delivery(
        ticket, brief.relative_to(tmp_path).as_posix(), repo_root=tmp_path
    )

    assert code in {1, 2}, message
    assert ticket.read_bytes() == original_ticket
    assert not brief.exists()


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
