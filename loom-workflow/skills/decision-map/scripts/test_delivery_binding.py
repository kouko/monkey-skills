"""Tests for reciprocal, repository-contained delivery Ticket/Brief bindings."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import delivery_binding  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _bound_ticket(tmp_path: Path, brief_path: str | None = None) -> tuple[Path, Path]:
    ticket = tmp_path / "docs/loom/maps/wayfinder/tickets/deliver-search.md"
    brief = tmp_path / "docs/loom/specs/deliver-search.md"
    ticket_relative = ticket.relative_to(tmp_path).as_posix()
    brief_relative = brief.relative_to(tmp_path).as_posix()
    _write(
        ticket,
        f"---\ntype: delivery\nstatus: claimed\nbrief: {brief_path or brief_relative}\n---\n",
    )
    _write(brief, f"# Deliver search\n\nOutcome Map ticket: {ticket_relative}\n")
    return ticket, brief


def _snapshot(*paths: Path) -> dict[Path, bytes]:
    return {path: path.read_bytes() for path in paths}


def test_reciprocal_ticket_brief_binding_is_canonical_and_contained(
    tmp_path: Path,
) -> None:
    # @req: REQ-79
    ticket, brief = _bound_ticket(tmp_path)
    before = _snapshot(ticket, brief)

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 0, message
    assert _snapshot(ticket, brief) == before


@pytest.mark.parametrize(
    "brief_path",
    [
        "/tmp/brief.md",
        "docs/loom/specs/../specs/deliver-search.md",
        "docs/loom/specs//deliver-search.md",
    ],
    ids=["absolute", "traversing", "non-normalized"],
)
def test_rejects_unsafe_ticket_brief_paths_without_writes(
    tmp_path: Path, brief_path: str
) -> None:
    # @req: REQ-79
    ticket, brief = _bound_ticket(tmp_path, brief_path)
    before = _snapshot(ticket, brief)

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 2, message
    assert _snapshot(ticket, brief) == before


def test_rejects_symlink_escape_brief_path(tmp_path: Path) -> None:
    # @req: REQ-79
    outside = tmp_path.parent / "outside-brief.md"
    _write(outside, "# Outside\n")
    ticket, brief = _bound_ticket(tmp_path, "docs/loom/specs/link.md")
    link = brief.with_name("link.md")
    link.symlink_to(outside)

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 2
    assert "symlink" in message


def test_rejects_in_repository_final_symlink_brief_path(tmp_path: Path) -> None:
    # @req: REQ-79
    ticket, brief = _bound_ticket(tmp_path, "docs/loom/specs/link.md")
    link = brief.with_name("link.md")
    link.symlink_to(brief)

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 2
    assert "symlink" in message


def test_rejects_in_repository_symlink_directory_component(tmp_path: Path) -> None:
    # @req: REQ-79
    ticket, brief = _bound_ticket(tmp_path, "docs/loom/linked-specs/deliver-search.md")
    link_dir = brief.parent.parent / "linked-specs"
    link_dir.symlink_to(brief.parent, target_is_directory=True)

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 2
    assert "symlink" in message


def test_rejects_in_repository_final_symlink_ticket_path(tmp_path: Path) -> None:
    # @req: REQ-79
    ticket, _ = _bound_ticket(tmp_path)
    link = ticket.with_name("linked-ticket.md")
    link.symlink_to(ticket)

    code, message = delivery_binding.validate(link, repo_root=tmp_path)

    assert code == 2
    assert "symlink" in message


@pytest.mark.parametrize("target_kind", ["missing", "directory"])
def test_rejects_missing_or_nonregular_brief_target(
    tmp_path: Path, target_kind: str
) -> None:
    # @req: REQ-79
    ticket, brief = _bound_ticket(tmp_path)
    if target_kind == "missing":
        brief.unlink()
    else:
        brief.unlink()
        brief.mkdir()

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 2, message


@pytest.mark.parametrize(
    "reciprocal",
    [
        "# Deliver search\n",
        "Outcome Map ticket: docs/loom/maps/wayfinder/tickets/other.md\n",
        "Outcome Map ticket: {ticket}\nOutcome Map ticket: {ticket}\n",
    ],
    ids=["absent", "wrong", "duplicate"],
)
def test_rejects_missing_wrong_or_duplicate_reciprocal_line(
    tmp_path: Path, reciprocal: str
) -> None:
    # @req: REQ-79
    ticket, brief = _bound_ticket(tmp_path)
    ticket_relative = ticket.relative_to(tmp_path).as_posix()
    _write(brief, reciprocal.format(ticket=ticket_relative))

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 2, message
    assert "must contain exactly" in message


def test_rejects_non_delivery_ticket_with_brief(tmp_path: Path) -> None:
    # @req: REQ-79
    ticket, _ = _bound_ticket(tmp_path)
    _write(
        ticket,
        ticket.read_text(encoding="utf-8").replace("type: delivery", "type: research"),
    )

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 2
    assert "only delivery tickets" in message


def test_rejects_duplicate_brief_ownership(tmp_path: Path) -> None:
    # @req: REQ-79
    ticket, brief = _bound_ticket(tmp_path)
    duplicate = ticket.with_name("deliver-again.md")
    brief_relative = brief.relative_to(tmp_path).as_posix()
    _write(duplicate, f"---\ntype: delivery\nstatus: claimed\nbrief: {brief_relative}\n---\n")

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 2
    assert "already owned" in message


def test_rejects_malformed_duplicate_candidate_ticket(tmp_path: Path) -> None:
    # @req: REQ-79
    ticket, _ = _bound_ticket(tmp_path)
    _write(ticket.with_name("broken.md"), "not frontmatter\n")

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 2
    assert "candidate ticket" in message


def test_rejects_non_normalized_duplicate_candidate_alias(tmp_path: Path) -> None:
    # @req: REQ-79
    ticket, brief = _bound_ticket(tmp_path)
    alias = ticket.with_name("deliver-alias.md")
    _write(
        alias,
        "---\ntype: delivery\nstatus: claimed\n"
        f"brief: {brief.relative_to(tmp_path).as_posix().replace('specs/', 'specs//')}\n---\n",
    )

    code, message = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 2
    assert "not normalized" in message
