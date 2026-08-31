"""Tests for the recoverable schema-v3 close-and-rechart operation."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import map_transaction  # noqa: E402
import map_lifecycle  # noqa: E402
import map_lock  # noqa: E402

RESEARCH_RESOLUTION = (
    "factual-answer: slice shipped\n"
    "inspectable-evidence: docs/loom/results/slice.md"
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _assert_only_lock_artifact(map_dir: Path) -> None:
    assert sorted(path.name for path in (map_dir / ".transactions").iterdir()) == [
        ".map.lock"
    ]


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
- DA-1: Slice works | state: open | kind: objective

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
type: research
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
            resolution=RESEARCH_RESOLUTION,
            unknowns=routes,
        )

    monkeypatch.setattr(map_transaction, "_before_terminalize", lambda: None)
    result = map_transaction.close_and_rechart(
        map_dir,
        "ship-slice",
        gist="Slice shipped.",
        resolution=RESEARCH_RESOLUTION,
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
    _assert_only_lock_artifact(map_dir)


def test_delivery_close_requires_current_policy_evidence_before_any_write(
    tmp_path: Path,
) -> None:
    # @req: REQ-83
    map_dir, ticket = _make_map(tmp_path)
    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace("type: research", "type: delivery"),
        encoding="utf-8",
    )
    before_map = (map_dir / "MAP.md").read_bytes()
    before_ticket = ticket.read_bytes()

    with pytest.raises(map_transaction.CloseTransactionError, match="evidence|policy"):
        map_transaction.close_and_rechart(
            map_dir,
            "ship-slice",
            gist="Slice shipped.",
            resolution="delivery-evidence: commit 0123456",
            unknowns=[],
        )

    assert (map_dir / "MAP.md").read_bytes() == before_map
    assert ticket.read_bytes() == before_ticket
    _assert_only_lock_artifact(map_dir)


def test_delivery_close_rechecks_current_policy_before_terminal_write(
    tmp_path: Path,
) -> None:
    # @req: REQ-82
    map_dir, ticket = _make_map(tmp_path)
    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace("type: research", "type: delivery"),
        encoding="utf-8",
    )
    brief = """# Delivery

## Acceptance

- [x] Slice is shipped.

## Delivery closure

policy: pr-ci
review-evidence: reviewed abc1234
verification-evidence: verified abc1234
"""
    plan = """# Plan

Stage: finishing

## Task 1 — Ship

- Status: done(abc1234)
"""

    def current_pr(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command == [
            "gh", "pr", "view", "42", "--json",
            "headRefOid,state,statusCheckRollup,mergedAt",
        ]
        payload = {
            "headRefOid": "abc1234",
            "state": "OPEN",
            "mergedAt": None,
            "statusCheckRollup": [
                {
                    "__typename": "CheckRun",
                    "status": "COMPLETED",
                    "conclusion": "SUCCESS",
                }
            ],
        }
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload), stderr="")

    result = map_transaction.close_and_rechart(
        map_dir,
        "ship-slice",
        gist="Slice shipped.",
        resolution="delivery-evidence: PR #42",
        unknowns=[],
        delivery_closure=map_transaction.DeliveryClosureInputs(
            brief_text=brief,
            plan_text=plan,
            acceptance_satisfied=True,
            review_head="abc1234",
            verification_head="abc1234",
            pr="42",
            pr_owners={"42": "tickets/ship-slice.md"},
            ownership_complete=True,
            run=current_pr,
        ),
    )

    assert result.routed == 0
    assert "status: closed" in ticket.read_text(encoding="utf-8")


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
            resolution=RESEARCH_RESOLUTION,
            unknowns=[],
        )

    assert (map_dir / "MAP.md").read_bytes() == before_map
    assert external_ticket.read_bytes() == before_external
    _assert_only_lock_artifact(map_dir)


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
        + f"\n\n## Resolution\n\n{RESEARCH_RESOLUTION}\n",
        encoding="utf-8",
    )
    before_map = (map_dir / "MAP.md").read_bytes()
    before_ticket = ticket.read_bytes()

    with pytest.raises(map_transaction.CloseTransactionError, match="prepared"):
        map_transaction.close_and_rechart(
            map_dir,
            "ship-slice",
            gist="Slice shipped.",
            resolution=RESEARCH_RESOLUTION,
            unknowns=[],
        )

    assert (map_dir / "MAP.md").read_bytes() == before_map
    assert ticket.read_bytes() == before_ticket
    _assert_only_lock_artifact(map_dir)


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
            resolution=RESEARCH_RESOLUTION,
            unknowns=routes,
        )

    assert (map_dir / "MAP.md").read_bytes() == before_map
    assert ticket.read_bytes() == before_ticket
    _assert_only_lock_artifact(map_dir)


def test_closed_retry_revalidates_authoritative_v3_source(
    tmp_path: Path,
) -> None:
    # @req: REQ-84
    map_dir, ticket = _make_map(tmp_path)
    request = dict(
        gist="Slice shipped.",
        resolution=RESEARCH_RESOLUTION,
        unknowns=[],
    )
    map_transaction.close_and_rechart(map_dir, "ship-slice", **request)
    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace(
            "type: research", "type: task"
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
        resolution=RESEARCH_RESOLUTION,
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
            "factual-answer: slice shipped", "factual-answer: changed"
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
                "- DA-1: Slice works | state: open | kind: objective",
                "- DA-1: Slice works | state: satisfied | kind: objective",
            ),
        encoding="utf-8",
    )

    before = {
        map_dir / "MAP.md": (map_dir / "MAP.md").read_bytes(),
        map_dir / "tickets/ship-slice.md": (
            map_dir / "tickets/ship-slice.md"
        ).read_bytes(),
    }
    with pytest.raises(map_transaction.CloseTransactionError, match="broken Map"):
        map_transaction.close_and_rechart(
            map_dir,
            "ship-slice",
            gist="Slice shipped.",
            resolution=RESEARCH_RESOLUTION,
            unknowns=[],
        )
    assert {path: path.read_bytes() for path in before} == before


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
        map_lifecycle, "_before_stability_check", mutate_descendant
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
        resolution=RESEARCH_RESOLUTION,
        unknowns=[],
    )
    assert (clean_map / ".transactions" / "close-ship-slice.json").is_file()
    monkeypatch.setattr(
        map_lifecycle, "_before_stability_check", lambda: None
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
        map_lifecycle,
        "_before_transition",
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
        map_lifecycle, "_before_state_replace", edit_at_replace_boundary
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
        resolution=RESEARCH_RESOLUTION,
        unknowns=[],
    )
    map_path = map_dir / "MAP.md"
    map_path.write_text(
        map_path.read_text(encoding="utf-8")
        .replace("state: active", "state: clear")
        .replace(
            "- DA-1: Slice works | state: open | kind: objective",
            "- DA-1: Slice works | state: satisfied | kind: objective | "
            "evidence: PR #123",
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
        map_lifecycle, "_after_state_replace", break_ticket_after_archive_write
    )
    real_atomic_write = map_lifecycle._atomic_write
    calls = 0

    def fail_only_rollback(path, text, *, expected=None) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated rollback I/O failure")
        real_atomic_write(path, text, expected=expected)

    monkeypatch.setattr(map_lifecycle, "_atomic_write", fail_only_rollback)
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


def test_claim_and_topology_transactions_detect_revision_conflicts(
    tmp_path: Path,
) -> None:
    # @req: REQ-87
    map_dir, ticket = _make_map(tmp_path)
    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace(
            "status: claimed\nclaim: codex, 2026-08-30",
            "status: open\nclaim: null",
        ),
        encoding="utf-8",
    )
    observed = map_transaction.capture_revision(map_dir)
    first = map_transaction.claim_ticket(
        map_dir,
        "ship-slice",
        owner="alice",
        claimed_on="2026-08-30",
        operation_id="claim-alice",
        expected_revision=observed,
    )
    assert first.applied is True and first.reused is False
    retry = map_transaction.claim_ticket(
        map_dir,
        "ship-slice",
        owner="alice",
        claimed_on="2026-08-30",
        operation_id="claim-alice",
        expected_revision=observed,
    )
    assert retry.applied is False and retry.reused is True
    with pytest.raises(map_transaction.CloseTransactionError, match="conflict.*re-read"):
        map_transaction.claim_ticket(
            map_dir,
            "ship-slice",
            owner="bob",
            claimed_on="2026-08-30",
            operation_id="claim-bob",
            expected_revision=observed,
        )

    blocker = map_dir / "tickets" / "blocker.md"
    _write(
        blocker,
        "---\ntype: research\nstatus: open\nclaim: null\n"
        "graduated-from: null\n---\n\nMeasure the blocker.\n",
    )
    topology_revision = map_transaction.capture_revision(map_dir)
    (map_dir / "MAP.md").write_text(
        (map_dir / "MAP.md").read_text(encoding="utf-8")
        + "\nConcurrent topology note.\n",
        encoding="utf-8",
    )
    with pytest.raises(map_transaction.CloseTransactionError, match="conflict.*re-read"):
        map_transaction.update_blockers(
            map_dir,
            "blocker",
            [],
            operation_id="block-ship",
            expected_revision=topology_revision,
        )


def test_transaction_retry_recovers_partial_claim_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-87
    map_dir, _ = _make_map(tmp_path)
    recovering = map_dir / "tickets" / "recovering.md"
    _write(
        recovering,
        "---\ntype: research\nstatus: open\nclaim: null\n"
        "graduated-from: null\n---\n\nRecover this claim.\n",
    )
    recovery_revision = map_transaction.capture_revision(map_dir)
    real_atomic_write = map_transaction.map_store._atomic_write
    calls = 0

    def fail_first_effect(path, text, *, expected=None) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("simulated effect interruption")
        real_atomic_write(path, text, expected=expected)

    monkeypatch.setattr(
        map_transaction.map_store, "_atomic_write", fail_first_effect
    )
    with pytest.raises(map_transaction.CloseTransactionError, match="interruption"):
        map_transaction.claim_ticket(
            map_dir,
            "recovering",
            owner="alice",
            claimed_on="2026-08-30",
            operation_id="claim-recovering",
            expected_revision=recovery_revision,
        )
    monkeypatch.setattr(
        map_transaction.map_store, "_atomic_write", real_atomic_write
    )
    recovered = map_transaction.claim_ticket(
        map_dir,
        "recovering",
        owner="alice",
        claimed_on="2026-08-30",
        operation_id="claim-recovering",
        expected_revision=recovery_revision,
    )
    assert recovered.applied is True and recovered.reused is False


def test_filesystem_probe_cleans_partial_probe_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-87
    map_dir, _ = _make_map(tmp_path)
    real_mkstemp = map_transaction.tempfile.mkstemp
    probe_calls = 0

    def fail_second_probe(*args, **kwargs):
        nonlocal probe_calls
        probe_calls += 1
        if probe_calls == 2:
            raise OSError("simulated probe interruption")
        return real_mkstemp(*args, **kwargs)

    monkeypatch.setattr(map_transaction.tempfile, "mkstemp", fail_second_probe)
    with pytest.raises(map_transaction.CloseTransactionError, match="unsupported"):
        map_transaction._assert_supported_filesystem(map_dir)
    assert not list(map_dir.glob(".map-cas-probe-*"))
    monkeypatch.setattr(map_transaction.tempfile, "mkstemp", real_mkstemp)


def test_revision_capture_refuses_symlinked_ticket_topology(tmp_path: Path) -> None:
    # @req: REQ-87
    map_dir, _ = _make_map(tmp_path)
    unsafe_map = tmp_path / "unsafe-map"
    unsafe_map.mkdir()
    (unsafe_map / "MAP.md").write_bytes((map_dir / "MAP.md").read_bytes())
    (unsafe_map / "tickets").symlink_to(
        map_dir / "tickets", target_is_directory=True
    )
    with pytest.raises(
        map_transaction.CloseTransactionError, match="non-regular.*tickets"
    ):
        map_transaction.capture_revision(unsafe_map)


def test_unsupported_filesystem_refuses_before_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-87
    map_dir, ticket = _make_map(tmp_path)
    blocker = map_dir / "tickets" / "blocker.md"
    _write(
        blocker,
        "---\ntype: research\nstatus: open\nclaim: null\n"
        "graduated-from: null\n---\n\nMeasure the blocker.\n",
    )
    before = {path: path.read_bytes() for path in (map_dir / "MAP.md", ticket, blocker)}
    monkeypatch.setattr(
        map_transaction,
        "_assert_supported_filesystem",
        lambda _directory: (_ for _ in ()).throw(
            map_transaction.CloseTransactionError(
                "unsupported atomic-replacement assumption"
            )
        ),
    )
    with pytest.raises(map_transaction.CloseTransactionError, match="unsupported"):
        map_transaction.update_blockers(
            map_dir,
            "blocker",
            [],
            operation_id="unsupported-block",
            expected_revision=map_transaction.capture_revision(map_dir),
        )
    assert {path: path.read_bytes() for path in before} == before


def test_concurrent_opposing_blocker_updates_serialize_one_winner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-87
    map_dir, _ = _make_map(tmp_path)
    for slug in ("first", "second"):
        _write(
            map_dir / "tickets" / f"{slug}.md",
            "---\ntype: research\nstatus: open\nclaim: null\n"
            "graduated-from: null\n---\n\nResearch this edge.\n",
        )
    observed = map_transaction.capture_revision(map_dir)
    barrier = threading.Barrier(2)
    real_prepare = map_transaction._prepare_mutation

    def prepare_then_rendezvous(*args, **kwargs):
        result = real_prepare(*args, **kwargs)
        try:
            barrier.wait(timeout=0.25)
        except threading.BrokenBarrierError:
            pass
        return result

    monkeypatch.setattr(map_transaction, "_prepare_mutation", prepare_then_rendezvous)
    outcomes: list[tuple[str, str]] = []

    def update(ticket: str, blocker: str) -> None:
        try:
            map_transaction.update_blockers(
                map_dir,
                ticket,
                [blocker],
                operation_id=f"block-{ticket}",
                expected_revision=observed,
            )
        except map_transaction.CloseTransactionError as exc:
            outcomes.append((ticket, str(exc)))
        else:
            outcomes.append((ticket, "applied"))

    workers = [
        threading.Thread(target=update, args=("first", "second")),
        threading.Thread(target=update, args=("second", "first")),
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=2)

    assert all(not worker.is_alive() for worker in workers)
    assert sum(result == "applied" for _, result in outcomes) == 1, outcomes
    assert sum("conflict" in result for _, result in outcomes) == 1, outcomes
    code, message = map_transaction.map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


@pytest.mark.parametrize("operation", ["claim", "blockers", "close"])
def test_unrelated_read_set_change_after_prepare_refuses_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    # @req: REQ-87
    map_dir, ticket = _make_map(tmp_path)
    unrelated = map_dir / "tickets" / "unrelated.md"
    _write(
        unrelated,
        "---\ntype: research\nstatus: open\nclaim: null\n"
        "graduated-from: null\n---\n\nUnrelated evidence.\n",
    )

    def mutate_unrelated() -> None:
        unrelated.write_text(
            unrelated.read_text(encoding="utf-8") + "Concurrent note.\n",
            encoding="utf-8",
        )

    if operation == "close":
        real_prepare_close = map_transaction._load_or_prepare_intent

        def prepare_close_then_change(*args, **kwargs):
            result = real_prepare_close(*args, **kwargs)
            mutate_unrelated()
            return result

        monkeypatch.setattr(
            map_transaction, "_load_or_prepare_intent", prepare_close_then_change
        )
        with pytest.raises(map_transaction.CloseTransactionError, match="conflict"):
            map_transaction.close_and_rechart(
                map_dir,
                "ship-slice",
                gist="Slice shipped.",
                resolution=RESEARCH_RESOLUTION,
                unknowns=[],
            )
        assert "status: claimed" in ticket.read_text(encoding="utf-8")
        assert "Slice shipped" not in (map_dir / "MAP.md").read_text(encoding="utf-8")
        return

    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace(
            "status: claimed\nclaim: codex, 2026-08-30",
            "status: open\nclaim: null",
        ),
        encoding="utf-8",
    )
    observed = map_transaction.capture_revision(map_dir)
    real_prepare = map_transaction._prepare_mutation

    def prepare_then_change(*args, **kwargs):
        result = real_prepare(*args, **kwargs)
        mutate_unrelated()
        return result

    monkeypatch.setattr(map_transaction, "_prepare_mutation", prepare_then_change)
    with pytest.raises(map_transaction.CloseTransactionError, match="conflict"):
        if operation == "claim":
            map_transaction.claim_ticket(
                map_dir,
                "ship-slice",
                owner="alice",
                claimed_on="2026-08-30",
                operation_id="claim-after-prepare",
                expected_revision=observed,
            )
        else:
            map_transaction.update_blockers(
                map_dir,
                "ship-slice",
                [],
                operation_id="block-after-prepare",
                expected_revision=observed,
            )
    assert "status: open" in ticket.read_text(encoding="utf-8")


def test_transaction_lock_refuses_symlink_alias(tmp_path: Path) -> None:
    # @req: REQ-87
    map_dir, ticket = _make_map(tmp_path)
    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace(
            "status: claimed\nclaim: codex, 2026-08-30",
            "status: open\nclaim: null",
        ),
        encoding="utf-8",
    )
    transactions = map_dir / ".transactions"
    transactions.mkdir()
    outside = tmp_path / "outside.lock"
    outside.write_text("outside\n", encoding="utf-8")
    (transactions / ".map.lock").symlink_to(outside)
    observed = map_transaction.capture_revision(map_dir)

    with pytest.raises(map_transaction.CloseTransactionError, match="lock"):
        map_transaction.claim_ticket(
            map_dir,
            "ship-slice",
            owner="alice",
            claimed_on="2026-08-30",
            operation_id="claim-lock-alias",
            expected_revision=observed,
        )
    assert outside.read_text(encoding="utf-8") == "outside\n"
    assert "status: open" in ticket.read_text(encoding="utf-8")


def test_transaction_lock_refuses_parent_directory_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-87
    map_dir, ticket = _make_map(tmp_path)
    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace(
            "status: claimed\nclaim: codex, 2026-08-30",
            "status: open\nclaim: null",
        ),
        encoding="utf-8",
    )
    transactions = map_dir / ".transactions"
    transactions.mkdir()
    parked = map_dir / ".transactions-parked"
    outside = tmp_path / "outside-transactions"
    outside.mkdir()

    def swap_parent() -> None:
        transactions.rename(parked)
        transactions.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(
        map_lock, "_before_lock_file_open", swap_parent
    )
    observed = map_transaction.capture_revision(map_dir)
    with pytest.raises(map_transaction.CloseTransactionError, match="lock"):
        map_transaction.claim_ticket(
            map_dir,
            "ship-slice",
            owner="alice",
            claimed_on="2026-08-30",
            operation_id="claim-parent-swap",
            expected_revision=observed,
        )
    assert not (outside / ".map.lock").exists()
    assert "status: open" in ticket.read_text(encoding="utf-8")


def test_transaction_lock_fails_closed_without_directory_open_primitive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # @req: REQ-87
    map_dir, ticket = _make_map(tmp_path)
    ticket.write_text(
        ticket.read_text(encoding="utf-8").replace(
            "status: claimed\nclaim: codex, 2026-08-30",
            "status: open\nclaim: null",
        ),
        encoding="utf-8",
    )
    observed = map_transaction.capture_revision(map_dir)
    monkeypatch.delattr(map_lock.os, "O_DIRECTORY")

    with pytest.raises(map_transaction.CloseTransactionError, match="unsupported"):
        map_transaction.claim_ticket(
            map_dir,
            "ship-slice",
            owner="alice",
            claimed_on="2026-08-30",
            operation_id="claim-no-directory-open",
            expected_revision=observed,
        )
    assert "status: open" in ticket.read_text(encoding="utf-8")


@pytest.mark.parametrize("operation", ["claim", "blockers", "close"])
def test_transaction_runs_final_validation_after_its_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    # @req: REQ-87
    map_dir, ticket = _make_map(tmp_path)
    if operation != "close":
        ticket.write_text(
            ticket.read_text(encoding="utf-8").replace(
                "status: claimed\nclaim: codex, 2026-08-30",
                "status: open\nclaim: null",
            ),
            encoding="utf-8",
        )
    if operation == "blockers":
        _write(
            map_dir / "tickets/done.md",
            "---\ntype: research\nstatus: closed\nclaim: null\n"
            "graduated-from: null\n---\n\nDone.\n\n## Resolution\n\n"
            "factual-answer: Done.\ninspectable-evidence: evidence.md\n",
        )
        (map_dir / "MAP.md").write_text(
            (map_dir / "MAP.md").read_text(encoding="utf-8").replace(
                "## Decisions-so-far\n",
                "## Decisions-so-far\n\n- Done. (tickets/done.md)\n",
            ),
            encoding="utf-8",
        )
    validated_effects: list[str] = []
    real_validate = map_transaction.map_store.validate

    def record_validation(*args, **kwargs):
        validated_effects.append(
            ticket.read_text(encoding="utf-8")
            + (map_dir / "MAP.md").read_text(encoding="utf-8")
        )
        return real_validate(*args, **kwargs)

    monkeypatch.setattr(map_transaction.map_store, "validate", record_validation)
    if operation == "claim":
        map_transaction.claim_ticket(
            map_dir,
            "ship-slice",
            owner="alice",
            claimed_on="2026-08-30",
            operation_id="claim-final-validation",
            expected_revision=map_transaction.capture_revision(map_dir),
        )
        expected = "status: claimed"
    elif operation == "blockers":
        map_transaction.update_blockers(
            map_dir,
            "ship-slice",
            ["done"],
            operation_id="block-final-validation",
            expected_revision=map_transaction.capture_revision(map_dir),
        )
        expected = "blocked-by: done"
    else:
        map_transaction.close_and_rechart(
            map_dir,
            "ship-slice",
            gist="Slice shipped.",
            resolution=RESEARCH_RESOLUTION,
            unknowns=[],
        )
        expected = "status: closed"
    assert validated_effects
    assert expected in validated_effects[-1]


def test_symlink_guard_delegates_to_map_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """map_transaction._assert_no_symlink_components must delegate to
    map_lock.assert_no_symlink_components (Task 1's public seam) rather than
    re-implementing the symlink walk, so both callers share one behavior."""
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    os.symlink(real, link)

    with pytest.raises(map_transaction.CloseTransactionError):
        map_transaction._assert_no_symlink_components(link / "x")

    def _fake(path: Path, error: type[Exception] = map_lock.MapLockError) -> None:
        raise RuntimeError("delegated")

    monkeypatch.setattr(map_lock, "assert_no_symlink_components", _fake)

    with pytest.raises(RuntimeError, match="delegated"):
        map_transaction._assert_no_symlink_components(link / "x")


def test_claim_ticket_refuses_already_claimed_ticket(tmp_path: Path) -> None:
    # @req: REQ-97
    map_dir, ticket = _make_map(tmp_path)
    before = ticket.read_bytes()
    observed = map_transaction.capture_revision(map_dir)

    with pytest.raises(
        map_transaction.CloseTransactionError, match="ticket must be open before claim"
    ):
        map_transaction.claim_ticket(
            map_dir,
            "ship-slice",
            owner="bob",
            claimed_on="2026-08-30",
            operation_id="claim-bob",
            expected_revision=observed,
        )

    assert ticket.read_bytes() == before
