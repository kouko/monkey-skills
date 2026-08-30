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
