"""Tests for the recoverable schema-v3 close-and-rechart operation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import map_transaction  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_map(tmp_path: Path) -> tuple[Path, Path]:
    map_dir = tmp_path / "docs" / "loom" / "maps" / "outcome"
    _write(
        map_dir / "MAP.md",
        """---
map-id: outcome
schema_version: 3
state: active
---

## Destination

Improve the outcome.
user-ratified: kouko, 2026-08-30
acceptance: Slice works | open | docs/loom/evidence.md

## Notes

Keep charting.

## Decisions-so-far

## Not-yet-specified (fog)

## Out-of-scope
""",
    )
    ticket = map_dir / "tickets" / "ship-slice.md"
    _write(
        ticket,
        """---
type: delivery
status: claimed
claim: codex, 2026-08-30
graduated-from: null
---

Ship one bounded slice.
""",
    )
    return map_dir, ticket


def test_close_records_gist_routes_unknowns_and_terminalizes_last(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-84
    map_dir, ticket = _make_map(tmp_path)
    routes = [
        map_transaction.UnknownRoute(
            text="Which cohort should be next?", destination="fog"
        ),
        map_transaction.UnknownRoute(
            text="Measure cohort retention",
            destination="ticket",
            ticket_slug="measure-retention",
            ticket_type="research",
        ),
        map_transaction.UnknownRoute(
            text="A mobile rewrite", destination="out-of-scope"
        ),
    ]

    def interrupt_before_terminalize() -> None:
        assert "- Slice shipped. (tickets/ship-slice.md)" in (
            map_dir / "MAP.md"
        ).read_text(encoding="utf-8")
        assert "- F-1: Which cohort should be next?" in (
            map_dir / "MAP.md"
        ).read_text(encoding="utf-8")
        assert (map_dir / "tickets" / "measure-retention.md").is_file()
        assert "status: claimed" in ticket.read_text(encoding="utf-8")
        raise RuntimeError("simulated interruption")

    monkeypatch.setattr(
        map_transaction, "_before_terminalize", interrupt_before_terminalize
    )
    with pytest.raises(RuntimeError, match="simulated interruption"):
        map_transaction.close_and_rechart(
            map_dir,
            "ship-slice",
            gist="Slice shipped.",
            resolution="delivery-evidence: commit 0123456",
            unknowns=routes,
        )

    monkeypatch.setattr(map_transaction, "_before_terminalize", lambda: None)
    result = map_transaction.close_and_rechart(
        map_dir,
        "ship-slice",
        gist="Slice shipped.",
        resolution="delivery-evidence: commit 0123456",
        unknowns=routes,
    )

    map_text = (map_dir / "MAP.md").read_text(encoding="utf-8")
    assert map_text.count("- Slice shipped. (tickets/ship-slice.md)") == 1
    assert map_text.count("- F-1: Which cohort should be next?") == 1
    assert map_text.count("- A mobile rewrite") == 1
    assert "status: closed" in ticket.read_text(encoding="utf-8")
    assert result.map_clear_eligible is False
    assert result.routed == 3


def test_invalid_closure_evidence_is_rejected_before_any_write(
    tmp_path: Path,
) -> None:
    # @req: REQ-84
    map_dir, ticket = _make_map(tmp_path)
    before_map = (map_dir / "MAP.md").read_bytes()
    before_ticket = ticket.read_bytes()

    with pytest.raises(map_transaction.CloseTransactionError, match="evidence"):
        map_transaction.close_and_rechart(
            map_dir,
            "ship-slice",
            gist="Slice shipped.",
            resolution="delivery-evidence: merely claimed",
            unknowns=[],
        )

    assert (map_dir / "MAP.md").read_bytes() == before_map
    assert ticket.read_bytes() == before_ticket
    assert not (map_dir / ".transactions").exists()


def test_symlinked_tickets_directory_refuses_without_any_mutation(
    tmp_path: Path,
) -> None:
    # @req: REQ-84
    map_dir, ticket = _make_map(tmp_path)
    external = tmp_path / "external-tickets"
    ticket.parent.rename(external)
    ticket.parent.symlink_to(external, target_is_directory=True)
    external_ticket = external / ticket.name
    before_map = (map_dir / "MAP.md").read_bytes()
    before_external = external_ticket.read_bytes()

    with pytest.raises(map_transaction.CloseTransactionError, match="symlink"):
        map_transaction.close_and_rechart(
            map_dir,
            "ship-slice",
            gist="Slice shipped.",
            resolution="delivery-evidence: commit 0123456",
            unknowns=[],
        )

    assert (map_dir / "MAP.md").read_bytes() == before_map
    assert external_ticket.read_bytes() == before_external
    assert not (map_dir / ".transactions").exists()


def test_closed_source_without_prepared_journal_cannot_bootstrap_resume(
    tmp_path: Path,
) -> None:
    # @req: REQ-84
    map_dir, ticket = _make_map(tmp_path)
    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace(
            "status: claimed",
            "status: closed",
        ).rstrip()
        + "\n\n## Resolution\n\ndelivery-evidence: commit 0123456\n",
        encoding="utf-8",
    )
    before_map = (map_dir / "MAP.md").read_bytes()
    before_ticket = ticket.read_bytes()

    with pytest.raises(map_transaction.CloseTransactionError, match="prepared"):
        map_transaction.close_and_rechart(
            map_dir,
            "ship-slice",
            gist="Slice shipped.",
            resolution="delivery-evidence: commit 0123456",
            unknowns=[],
        )

    assert (map_dir / "MAP.md").read_bytes() == before_map
    assert ticket.read_bytes() == before_ticket
    assert not (map_dir / ".transactions").exists()


def test_duplicate_ticket_route_slugs_refuse_before_any_write(
    tmp_path: Path,
) -> None:
    # @req: REQ-84
    map_dir, ticket = _make_map(tmp_path)
    before_map = (map_dir / "MAP.md").read_bytes()
    before_ticket = ticket.read_bytes()
    routes = [
        map_transaction.UnknownRoute(
            text="Measure retention",
            destination="ticket",
            ticket_slug="measure-next",
            ticket_type="research",
        ),
        map_transaction.UnknownRoute(
            text="Deliver retention report",
            destination="ticket",
            ticket_slug="measure-next",
            ticket_type="delivery",
        ),
    ]

    with pytest.raises(map_transaction.CloseTransactionError, match="ticket_slug"):
        map_transaction.close_and_rechart(
            map_dir,
            "ship-slice",
            gist="Slice shipped.",
            resolution="delivery-evidence: commit 0123456",
            unknowns=routes,
        )

    assert (map_dir / "MAP.md").read_bytes() == before_map
    assert ticket.read_bytes() == before_ticket
    assert not (map_dir / ".transactions").exists()


def test_closed_retry_revalidates_authoritative_v3_source(
    tmp_path: Path,
) -> None:
    # @req: REQ-84
    map_dir, ticket = _make_map(tmp_path)
    request = dict(
        gist="Slice shipped.",
        resolution="delivery-evidence: commit 0123456",
        unknowns=[],
    )
    map_transaction.close_and_rechart(map_dir, "ship-slice", **request)
    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace(
            "type: delivery", "type: task"
        ),
        encoding="utf-8",
    )
    before_map = (map_dir / "MAP.md").read_bytes()
    before_ticket = ticket.read_bytes()

    with pytest.raises(map_transaction.CloseTransactionError, match="schema-v3"):
        map_transaction.close_and_rechart(map_dir, "ship-slice", **request)

    assert (map_dir / "MAP.md").read_bytes() == before_map
    assert ticket.read_bytes() == before_ticket


def test_closed_retry_resolution_conflict_refuses_before_repairing_map(
    tmp_path: Path,
) -> None:
    # @req: REQ-84
    map_dir, ticket = _make_map(tmp_path)
    request = dict(
        gist="Slice shipped.",
        resolution="delivery-evidence: commit 0123456",
        unknowns=[],
    )
    map_transaction.close_and_rechart(map_dir, "ship-slice", **request)
    map_path = map_dir / "MAP.md"
    map_path.write_text(
        map_path.read_text(encoding="utf-8").replace(
            "- Slice shipped. (tickets/ship-slice.md)\n", ""
        ),
        encoding="utf-8",
    )
    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace(
            "commit 0123456", "commit abcdef0"
        ),
        encoding="utf-8",
    )
    journal = map_dir / ".transactions" / "close-ship-slice.json"
    before = (map_path.read_bytes(), ticket.read_bytes(), journal.read_bytes())

    with pytest.raises(map_transaction.CloseTransactionError, match="conflicts"):
        map_transaction.close_and_rechart(map_dir, "ship-slice", **request)

    assert (map_path.read_bytes(), ticket.read_bytes(), journal.read_bytes()) == before


def test_clear_assessment_reuses_req_78_acceptance_validation(
    tmp_path: Path,
) -> None:
    # @req: REQ-84
    map_dir, _ = _make_map(tmp_path)
    map_path = map_dir / "MAP.md"
    map_path.write_text(
        map_path.read_text(encoding="utf-8").replace(
            "acceptance: Slice works | open | docs/loom/evidence.md",
            "acceptance: | satisfied | docs/loom/evidence.md",
        ),
        encoding="utf-8",
    )

    result = map_transaction.close_and_rechart(
        map_dir,
        "ship-slice",
        gist="Slice shipped.",
        resolution="delivery-evidence: commit 0123456",
        unknowns=[],
    )

    assert result.map_clear_eligible is False


def test_retirement_refuses_partial_operations_and_descendant_races(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-98
    partial_map, partial_ticket = _make_map(tmp_path / "partial")
    partial_map_path = partial_map / "MAP.md"
    partial_map_path.write_text(
        partial_map_path.read_text(encoding="utf-8").replace(
            "## Not-yet-specified (fog)\n\n",
            "## Not-yet-specified (fog)\n\n- F-1: Which slice should ship?\n",
        ),
        encoding="utf-8",
    )
    partial_ticket.write_text(
        partial_ticket.read_text(encoding="utf-8").replace(
            "graduated-from: null", "graduated-from: F-1"
        ),
        encoding="utf-8",
    )
    partial_before = partial_map_path.read_bytes()
    with pytest.raises(map_transaction.CloseTransactionError, match="partial.*graduation"):
        map_transaction.retire_map(
            partial_map,
            ratified_by="kouko",
            ratified_on="2026-08-30",
            reason="Stop this outcome.",
            repo_root=tmp_path / "partial",
        )
    assert partial_map_path.read_bytes() == partial_before

    raced_map, raced_ticket = _make_map(tmp_path / "raced")
    raced_map_before = (raced_map / "MAP.md").read_bytes()

    def mutate_descendant() -> None:
        raced_ticket.write_text(
            raced_ticket.read_text(encoding="utf-8") + "\nConcurrent edit.\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(
        map_transaction, "_before_retirement_stability_check", mutate_descendant
    )
    with pytest.raises(map_transaction.CloseTransactionError, match="stable snapshot"):
        map_transaction.retire_map(
            raced_map,
            ratified_by="kouko",
            ratified_on="2026-08-30",
            reason="Stop this outcome.",
            repo_root=tmp_path / "raced",
        )
    assert (raced_map / "MAP.md").read_bytes() == raced_map_before

    clean_map, _ = _make_map(tmp_path / "clean")
    map_transaction.close_and_rechart(
        clean_map,
        "ship-slice",
        gist="Slice shipped.",
        resolution="delivery-evidence: commit 0123456",
        unknowns=[],
    )
    assert (clean_map / ".transactions" / "close-ship-slice.json").is_file()
    monkeypatch.setattr(
        map_transaction, "_before_retirement_stability_check", lambda: None
    )
    map_transaction.retire_map(
        clean_map,
        ratified_by="kouko",
        ratified_on="2026-08-30",
        reason="Stop this outcome.",
        repo_root=tmp_path / "clean",
    )
    assert "state: archived" in (clean_map / "MAP.md").read_text(encoding="utf-8")
    assert (clean_map / ".transactions" / "close-ship-slice.json").is_file()


def test_retirement_rechecks_descendants_at_transition_call_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-98
    map_dir, ticket = _make_map(tmp_path)
    map_path = map_dir / "MAP.md"
    map_before = map_path.read_bytes()

    def mutate_after_validated_snapshot() -> None:
        ticket.write_text(
            ticket.read_text(encoding="utf-8") + "\nLate descendant edit.\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(
        map_transaction,
        "_before_retirement_transition",
        mutate_after_validated_snapshot,
    )
    with pytest.raises(map_transaction.CloseTransactionError, match="stable snapshot"):
        map_transaction.retire_map(
            map_dir,
            ratified_by="kouko",
            ratified_on="2026-08-30",
            reason="Stop this outcome.",
            repo_root=tmp_path,
        )

    assert map_path.read_bytes() == map_before
    assert "state: archived" not in map_path.read_text(encoding="utf-8")


def test_retirement_map_replace_is_compare_and_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-98
    map_dir, _ = _make_map(tmp_path)
    map_path = map_dir / "MAP.md"
    original = map_path.read_bytes()
    concurrent = original + b"\nConcurrent MAP edit.\n"

    def edit_at_replace_boundary() -> None:
        map_path.write_bytes(concurrent)

    monkeypatch.setattr(
        map_transaction, "_before_retirement_replace", edit_at_replace_boundary
    )
    with pytest.raises(map_transaction.CloseTransactionError, match="changed"):
        map_transaction.retire_map(
            map_dir,
            ratified_by="kouko",
            ratified_on="2026-08-30",
            reason="Stop this outcome.",
            repo_root=tmp_path,
        )

    assert map_path.read_bytes() == concurrent
    assert b"state: archived" not in map_path.read_bytes()


def test_retirement_rollback_failure_records_broken_recovery_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-95
    # @req: REQ-98
    map_dir, ticket = _make_map(tmp_path)
    map_transaction.close_and_rechart(
        map_dir,
        "ship-slice",
        gist="Slice shipped.",
        resolution="delivery-evidence: commit 0123456",
        unknowns=[],
    )
    map_path = map_dir / "MAP.md"
    map_path.write_text(
        map_path.read_text(encoding="utf-8")
        .replace("state: active", "state: clear")
        .replace(
            "acceptance: Slice works | open | docs/loom/evidence.md",
            "acceptance: Slice works | satisfied | docs/loom/evidence.md",
        ),
        encoding="utf-8",
    )

    def break_ticket_after_archive_write() -> None:
        ticket.write_text(
            ticket.read_text(encoding="utf-8").replace(
                "graduated-from: null", "graduated-from: null\nphase: invalid"
            ),
            encoding="utf-8",
        )

    monkeypatch.setattr(
        map_transaction, "_after_archive_state_replace", break_ticket_after_archive_write
    )
    real_atomic_write = map_transaction._atomic_write
    calls = 0

    def fail_only_rollback(path, text, *, expected=None) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated rollback I/O failure")
        real_atomic_write(path, text, expected=expected)

    monkeypatch.setattr(map_transaction, "_atomic_write", fail_only_rollback)
    with pytest.raises(
        map_transaction.CloseTransactionError,
        match="BROKEN.*recovery-required",
    ):
        map_transaction.archive_map_transition(map_dir, repo_root=tmp_path)

    assert "state: archived" in map_path.read_text(encoding="utf-8")
    recovery = map_dir / ".transactions" / "retirement-recovery.json"
    evidence = json.loads(recovery.read_text(encoding="utf-8"))
    assert evidence["status"] == "BROKEN"
    assert evidence["action"] == "recovery-required"
    assert evidence["map_path"] == "MAP.md"
    assert "simulated rollback I/O failure" in evidence["rollback_error"]
