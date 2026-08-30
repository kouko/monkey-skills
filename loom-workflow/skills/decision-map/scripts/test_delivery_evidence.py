"""Tests for current formal evidence required to close one delivery slice."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import delivery_evidence  # noqa: E402


BRIEF = """# Deliver the slice

## Acceptance

- [x] The promised behavior is present.

## Delivery closure

policy: pr-ci
review-evidence: review.md
verification-evidence: pytest -q
"""

TERMINAL_PLAN = """# Plan

Stage: finishing

## Task 1 — Deliver

- **Status**: done(abc1234)
"""


def _gh(*, head: str = "abc1234", conclusion: str = "SUCCESS"):
    def run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        assert command == [
            "gh",
            "pr",
            "view",
            "42",
            "--json",
            "headRefOid,state,statusCheckRollup,mergedAt",
        ]
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "headRefOid": head,
                    "state": "OPEN",
                    "mergedAt": None,
                    "statusCheckRollup": [
                        {"__typename": "CheckRun", "status": "COMPLETED", "conclusion": conclusion}
                    ],
                }
            ),
            stderr="",
        )

    return run


# @req: REQ-82
@pytest.mark.parametrize(
    ("override", "reason"),
    [
        ({"brief_text": BRIEF.replace("policy: pr-ci\n", "")}, "policy"),
        ({"acceptance_satisfied": False}, "acceptance"),
        ({"plan_text": TERMINAL_PLAN.replace("done(abc1234)", "pending")}, "terminal Plan"),
        ({"review_head": ""}, "review"),
        ({"verification_head": ""}, "verification"),
        ({"pr": ""}, "PR"),
    ],
)
def test_delivery_closure_requires_current_policy_evidence(
    override: dict[str, object], reason: str
) -> None:
    arguments: dict[str, object] = {
        "brief_text": BRIEF,
        "plan_text": TERMINAL_PLAN,
        "acceptance_satisfied": True,
        "review_head": "abc1234",
        "verification_head": "abc1234",
        "pr": "42",
        "run": _gh(),
    }
    arguments.update(override)

    result = delivery_evidence.evaluate_closure(**arguments)

    assert result.ready is False
    assert result.phase == "repair-required"
    assert reason in result.reason


# @req: REQ-82
def test_pr_head_drift_invalidates_delivery_readiness() -> None:
    result = delivery_evidence.evaluate_closure(
        brief_text=BRIEF,
        plan_text=TERMINAL_PLAN,
        acceptance_satisfied=True,
        review_head="abc1234",
        verification_head="abc1234",
        pr="42",
        run=_gh(head="def5678"),
    )

    assert result.ready is False
    assert result.phase == "repair-required"
    assert "current PR head def5678" in result.reason
    assert "reviewed head abc1234" in result.reason


# @req: REQ-82
def test_current_formal_evidence_permits_delivery_closure() -> None:
    result = delivery_evidence.evaluate_closure(
        brief_text=BRIEF,
        plan_text=TERMINAL_PLAN,
        acceptance_satisfied=True,
        review_head="abc1234",
        verification_head="abc1234",
        pr="42",
        run=_gh(),
    )

    assert result.ready is True
    assert result.phase == "ready"
    assert result.head == "abc1234"


# @req: REQ-82
def test_current_green_commit_status_permits_delivery_closure() -> None:
    def run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "headRefOid": "abc1234",
                    "state": "OPEN",
                    "mergedAt": None,
                    "statusCheckRollup": [
                        {"__typename": "StatusContext", "state": "SUCCESS"}
                    ],
                }
            ),
            stderr="",
        )

    result = delivery_evidence.evaluate_closure(
        brief_text=BRIEF,
        plan_text=TERMINAL_PLAN,
        acceptance_satisfied=True,
        review_head="abc1234",
        verification_head="abc1234",
        pr="42",
        run=run,
    )

    assert result.ready is True


# @req: REQ-82
@pytest.mark.parametrize("conclusion", ["FAILURE", "CANCELLED", None])
def test_non_green_or_incomplete_exact_head_checks_refuse_closure(
    conclusion: str | None,
) -> None:
    result = delivery_evidence.evaluate_closure(
        brief_text=BRIEF,
        plan_text=TERMINAL_PLAN,
        acceptance_satisfied=True,
        review_head="abc1234",
        verification_head="abc1234",
        pr="42",
        run=_gh(conclusion=conclusion),
    )

    assert result.ready is False
    assert result.phase == "repair-required"
    assert "checks" in result.reason


# @req: REQ-82
@pytest.mark.parametrize(
    "plan_text",
    [
        TERMINAL_PLAN.replace(
            "- **Status**: done(abc1234)",
            "- **Status**: done(abc1234)\n- **Status**: pending",
        ),
        TERMINAL_PLAN.replace("Stage: finishing", "Stage: finishing\nStage: reviewing"),
    ],
)
def test_conflicting_terminal_plan_evidence_refuses_closure(plan_text: str) -> None:
    result = delivery_evidence.evaluate_closure(
        brief_text=BRIEF,
        plan_text=plan_text,
        acceptance_satisfied=True,
        review_head="abc1234",
        verification_head="abc1234",
        pr="42",
        run=_gh(),
    )

    assert result.ready is False
    assert result.phase == "repair-required"
    assert "terminal Plan" in result.reason


# @req: REQ-82
def test_unknown_check_rollup_shape_fails_closed() -> None:
    def run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "headRefOid": "abc1234",
                    "state": "OPEN",
                    "mergedAt": None,
                    "statusCheckRollup": [
                        {
                            "__typename": "FutureCheckType",
                            "status": "COMPLETED",
                            "conclusion": "SUCCESS",
                        }
                    ],
                }
            ),
            stderr="",
        )

    result = delivery_evidence.evaluate_closure(
        brief_text=BRIEF,
        plan_text=TERMINAL_PLAN,
        acceptance_satisfied=True,
        review_head="abc1234",
        verification_head="abc1234",
        pr="42",
        run=run,
    )

    assert result.ready is False
    assert result.phase == "repair-required"
    assert "checks" in result.reason


def test_multi_pr_delivery_is_ordered_and_pr_owner_is_unique() -> None:
    # @req: REQ-83
    first = delivery_evidence.PRRole("41", "implementation", "abc1234", "abc1234")
    second = delivery_evidence.PRRole("42", "release", "def5678", "def5678")

    pending = delivery_evidence.evaluate_closure(
        brief_text=BRIEF,
        plan_text=TERMINAL_PLAN,
        acceptance_satisfied=True,
        review_head="",
        verification_head="",
        pr="",
        pr_roles=(first, second),
        ticket="docs/loom/maps/wayfinder/tickets/delivery.md",
        pr_owners={"41": "docs/loom/maps/wayfinder/tickets/delivery.md", "42": "docs/loom/maps/wayfinder/tickets/delivery.md"},
        ownership_complete=True,
        run=lambda command, **_: subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "headRefOid": "abc1234" if command[3] == "41" else "def5678",
                    "state": "OPEN",
                    "mergedAt": None,
                    "statusCheckRollup": [
                        {"__typename": "CheckRun", "status": "COMPLETED", "conclusion": "SUCCESS" if command[3] == "41" else None}
                    ],
                }
            ),
            stderr="",
        ),
    )

    shared = delivery_evidence.evaluate_closure(
        brief_text=BRIEF,
        plan_text=TERMINAL_PLAN,
        acceptance_satisfied=True,
        review_head="",
        verification_head="",
        pr="",
        pr_roles=(first, second),
        ticket="docs/loom/maps/wayfinder/tickets/delivery.md",
        pr_owners={"41": "docs/loom/maps/wayfinder/tickets/other.md"},
        ownership_complete=True,
        run=_gh(),
    )

    assert pending.ready is False
    assert pending.evidence_state == "pending"
    assert "release" in pending.reason
    assert shared.ready is False
    assert shared.evidence_state == "contradictory"
    assert "already owned" in shared.reason


def test_evidence_distinguishes_invalid_stale_unavailable_and_pending() -> None:
    # @req: REQ-89
    common = {
        "brief_text": BRIEF,
        "plan_text": TERMINAL_PLAN,
        "acceptance_satisfied": True,
        "review_head": "abc1234",
        "verification_head": "abc1234",
        "pr": "42",
    }
    unavailable = delivery_evidence.evaluate_closure(
        **common,
        run=lambda *_args, **_kwargs: (_ for _ in ()).throw(subprocess.TimeoutExpired("gh", 30)),
    )
    unauthorized = delivery_evidence.evaluate_closure(
        **common,
        run=lambda command, **_: subprocess.CompletedProcess(command, 1, stdout="", stderr="HTTP 401 authentication required"),
    )
    stale = delivery_evidence.evaluate_closure(**common, run=_gh(head="def5678"))
    pending = delivery_evidence.evaluate_closure(**common, run=_gh(conclusion=None))
    invalid = delivery_evidence.evaluate_closure(**{**common, "acceptance_satisfied": False}, run=_gh())

    assert unavailable.evidence_state == "unavailable"
    assert unauthorized.evidence_state == "unauthorized"
    assert stale.evidence_state == "stale"
    assert pending.evidence_state == "pending"
    assert invalid.evidence_state == "invalid"
    assert all(not result.ready for result in (unavailable, unauthorized, stale, pending, invalid))


def test_authored_policy_controls_pr_merge_and_artifact_closure() -> None:
    # @req: REQ-96
    merged = BRIEF.replace("policy: pr-ci\nreview-evidence: review.md\nverification-evidence: pytest -q", "policy: merged\npr: 42\nmerge-evidence: mergedAt")
    artifact = BRIEF.replace("policy: pr-ci\nreview-evidence: review.md\nverification-evidence: pytest -q", "policy: artifact\nartifact: dist/slice.zip\nacceptance-probe: python3 -m pytest -q")
    common = dict(plan_text=TERMINAL_PLAN, acceptance_satisfied=True, review_head="abc1234", verification_head="abc1234", pr="42")
    open_merged = delivery_evidence.evaluate_closure(brief_text=merged, run=_gh(), **common)
    completed_merged = delivery_evidence.evaluate_closure(
        brief_text=merged,
        run=lambda command, **_: subprocess.CompletedProcess(command, 0, stdout=json.dumps({"headRefOid": "abc1234", "state": "MERGED", "mergedAt": "2026-08-30T00:00:00Z", "statusCheckRollup": [{"__typename": "CheckRun", "status": "COMPLETED", "conclusion": "SUCCESS"}]}), stderr=""),
        **common,
    )
    merged_without_pr_ci_heads = delivery_evidence.evaluate_closure(
        brief_text=merged,
        review_head="",
        verification_head="",
        run=lambda command, **_: subprocess.CompletedProcess(command, 0, stdout=json.dumps({"headRefOid": "abc1234", "state": "MERGED", "mergedAt": "2026-08-30T00:00:00Z", "statusCheckRollup": [{"__typename": "CheckRun", "status": "COMPLETED", "conclusion": "SUCCESS"}]}), stderr=""),
        **{key: value for key, value in common.items() if key not in {"review_head", "verification_head"}},
    )
    missing_probe = delivery_evidence.evaluate_closure(brief_text=artifact, artifact_probe=None, run=_gh(), **common)
    passed_probe = delivery_evidence.evaluate_closure(brief_text=artifact, artifact_probe=True, run=_gh(), **common)

    assert open_merged.evidence_state == "pending"
    assert completed_merged.ready is True
    assert merged_without_pr_ci_heads.ready is True
    assert missing_probe.evidence_state == "unavailable"
    assert passed_probe.ready is True


def test_pr_roles_require_complete_unique_ownership_and_exercise_all_states() -> None:
    # @req: REQ-83
    roles = (delivery_evidence.PRRole("42", "implementation", "abc1234", "abc1234"),)
    assert delivery_evidence.validate_pr_ownership(roles, "ticket", None, False)[1] == "contradictory"
    assert delivery_evidence.validate_pr_ownership((roles[0], roles[0]), "ticket", {"42": "ticket"}, True)[1] == "contradictory"
    assert delivery_evidence.validate_pr_ownership(roles, "ticket", {"42": "other"}, True)[1] == "contradictory"
    assert delivery_evidence.validate_pr_ownership(roles, "ticket", {"42": "ticket"}, True) == (None, "valid")


def test_missing_or_duplicate_authored_policy_fields_fail_closed() -> None:
    # @req: REQ-96
    assert delivery_evidence.validate_closure_policy(BRIEF.replace("review-evidence: review.md\n", ""))[0] is None
    assert delivery_evidence.validate_closure_policy(BRIEF + "policy: pr-ci\n")[0] is None
