"""Evaluate whether one delivery has current formal closure evidence.

This module is deliberately read-only.  The Brief authors the policy while
the caller supplies the recorded acceptance/review/verification evidence;
GitHub remains authoritative for the PR's current head and check state.
"""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


_DELIVERY_CLOSURE = re.compile(
    r"^## Delivery closure\s*$\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
)
_POLICY = re.compile(r"^policy:\s*(?P<value>\S+)\s*$", re.MULTILINE)
_ACCEPTANCE = re.compile(
    r"^## Acceptance\s*$\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
)
_TASK = re.compile(r"^## Task \d+ \u2014 .+?$", re.MULTILINE)
_NEXT_HEADING = re.compile(r"^## ", re.MULTILINE)
_STAGE_LINE = re.compile(r"^Stage:\s*(?P<value>\S.*?)\s*$", re.MULTILINE)
_STATUS_LINE = re.compile(
    r"^- \*{0,2}Status\*{0,2}:\s*(?P<value>\S.*?)\s*$", re.MULTILINE
)
_DONE_VALUE = re.compile(r"done\([^()\s]+\)")
_PASS_CONCLUSIONS = {"SUCCESS", "NEUTRAL", "SKIPPED"}


@dataclass(frozen=True)
class ClosureReadiness:
    ready: bool
    phase: str
    reason: str
    head: str | None = None


def _refuse(reason: str, head: str | None = None) -> ClosureReadiness:
    return ClosureReadiness(False, "repair-required", reason, head)


def _authored_policy(brief_text: str) -> tuple[str | None, str | None]:
    sections = list(_DELIVERY_CLOSURE.finditer(brief_text))
    if len(sections) != 1:
        return None, "Brief must author exactly one Delivery closure policy"
    policies = list(_POLICY.finditer(sections[0].group("body")))
    if len(policies) != 1:
        return None, "Brief must author exactly one delivery policy"
    return policies[0].group("value"), None


def _plan_is_terminal(plan_text: str) -> bool:
    stages = [match.group("value") for match in _STAGE_LINE.finditer(plan_text)]
    if stages != ["finishing"]:
        return False
    tasks = list(_TASK.finditer(plan_text))
    if not tasks:
        return False
    for task in tasks:
        following = _NEXT_HEADING.search(plan_text, task.end())
        block = plan_text[task.end() : following.start() if following else len(plan_text)]
        statuses = [match.group("value") for match in _STATUS_LINE.finditer(block)]
        if len(statuses) != 1 or _DONE_VALUE.fullmatch(statuses[0]) is None:
            return False
    return True


def _run_pr_view(
    pr: str,
    run: Callable[..., subprocess.CompletedProcess[str]],
) -> tuple[dict[str, Any] | None, str | None]:
    command = [
        "gh",
        "pr",
        "view",
        pr,
        "--json",
        "headRefOid,state,statusCheckRollup,mergedAt",
    ]
    try:
        completed = run(command, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"current PR evidence is unavailable: {exc}"
    if completed.returncode != 0:
        return None, (
            "current PR evidence is unavailable: "
            + (completed.stderr.strip() or f"gh exited {completed.returncode}")
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return None, f"current PR evidence is unavailable: invalid gh JSON ({exc.msg})"
    if not isinstance(payload, dict):
        return None, "current PR evidence is unavailable: gh returned a non-object"
    return payload, None


def _checks_are_green(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for check in value:
        if not isinstance(check, dict):
            return False
        kind = check.get("__typename")
        if kind == "StatusContext":
            if check.get("state") != "SUCCESS":
                return False
        elif kind == "CheckRun" and not (
            check.get("status") == "COMPLETED"
            and check.get("conclusion") in _PASS_CONCLUSIONS
        ):
            return False
        elif kind != "CheckRun":
            return False
    return True


def evaluate_closure(
    *,
    brief_text: str,
    plan_text: str,
    acceptance_satisfied: bool,
    review_head: str,
    verification_head: str,
    pr: str,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> ClosureReadiness:
    """Return read-only closure readiness for the current PR-CI delivery arc."""
    policy, policy_error = _authored_policy(brief_text)
    if policy_error:
        return _refuse(policy_error)
    if policy != "pr-ci":
        return _refuse(f"delivery policy {policy!r} is not evaluated by the PR-CI evidence gate")
    acceptance = _ACCEPTANCE.search(brief_text)
    if acceptance is None or not acceptance.group("body").strip() or not acceptance_satisfied:
        return _refuse("Brief acceptance is not satisfied with formal evidence")
    if not _plan_is_terminal(plan_text):
        return _refuse("delivery requires a terminal Plan before closure")
    if not review_head:
        return _refuse("whole-branch review evidence is missing")
    if not verification_head:
        return _refuse("verification evidence is missing")
    if not pr:
        return _refuse("PR evidence is missing")

    payload, error = _run_pr_view(pr, run)
    if error:
        return _refuse(error)
    assert payload is not None
    head = payload.get("headRefOid")
    if not isinstance(head, str) or not head:
        return _refuse("current PR evidence has no head SHA")
    if review_head != head:
        return _refuse(
            f"current PR head {head} differs from reviewed head {review_head}", head
        )
    if verification_head != head:
        return _refuse(
            f"current PR head {head} differs from verified head {verification_head}", head
        )
    if payload.get("state") not in {"OPEN", "MERGED"}:
        return _refuse("current PR is not open or merged", head)
    if not _checks_are_green(payload.get("statusCheckRollup")):
        return _refuse("current exact-head checks are missing, pending, or non-green", head)
    return ClosureReadiness(True, "ready", "current formal delivery evidence passes", head)
