"""Tests for reciprocal, repository-contained delivery Ticket/Brief bindings."""

from __future__ import annotations

import os
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


def test_delivery_migration_snapshot_records_brief_and_candidate_population(
    tmp_path: Path,
) -> None:
    # @req: REQ-85
    """Migration can CAS-cover every file inspected for a delivery binding."""
    ticket, brief = _bound_ticket(tmp_path)
    other = tmp_path / "docs/loom/maps/other/tickets/other.md"
    _write(other, "---\ntype: research\nstatus: open\n---\n")

    snapshot = delivery_binding.snapshot_delivery_migration_binding(
        ticket, repo_root=tmp_path
    )

    ticket_key = ticket.relative_to(tmp_path).as_posix()
    brief_key = brief.relative_to(tmp_path).as_posix()
    other_key = other.relative_to(tmp_path).as_posix()
    assert set(snapshot.texts) >= {ticket_key, brief_key, other_key}
    assert snapshot.ticket_membership == tuple(sorted((ticket_key, other_key)))


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


@pytest.mark.skipif(
    not os.path.samefile("/var", "/private/var"),
    reason="macOS /var alias is unavailable",
)
def test_accepts_ticket_in_callers_var_repo_root_namespace(tmp_path: Path) -> None:
    # @req: REQ-79
    ticket, _ = _bound_ticket(tmp_path)
    private_var = Path("/private/var")
    alias_root = Path("/var") / tmp_path.relative_to(private_var)
    alias_ticket = Path("/var") / ticket.relative_to(private_var)

    code, message = delivery_binding.validate(alias_ticket, repo_root=alias_root)

    assert code == 0, message


@pytest.mark.parametrize("target_kind", ["missing", "directory"])
def test_requested_missing_or_directory_ticket_is_operational(
    tmp_path: Path, target_kind: str
) -> None:
    # @req: REQ-79
    ticket, _ = _bound_ticket(tmp_path)
    if target_kind == "missing":
        ticket.unlink()
    else:
        ticket.unlink()
        ticket.mkdir()

    code, _ = delivery_binding.validate(ticket, repo_root=tmp_path)

    assert code == 1


def test_rejects_repo_root_replaced_by_symlink_before_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-79
    repo_root = tmp_path / "repo"
    ticket, _ = _bound_ticket(repo_root)
    original_open = delivery_binding.os.open
    replacement = tmp_path / "repo-original"
    replaced = False

    def replace_before_root_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        nonlocal replaced
        if not replaced and Path(path) == repo_root and "dir_fd" not in kwargs:
            repo_root.rename(replacement)
            repo_root.symlink_to(replacement, target_is_directory=True)
            replaced = True
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(delivery_binding.os, "open", replace_before_root_open)

    code, message = delivery_binding.validate(ticket, repo_root=repo_root)

    assert code == 2
    assert "repository root" in message
