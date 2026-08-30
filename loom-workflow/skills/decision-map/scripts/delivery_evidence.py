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
_POLICY_FIELD = re.compile(r"^(?P<key>[a-z][a-z-]*): (?P<value>\S.*)$")
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
    evidence_state: str = "invalid"


@dataclass(frozen=True)
class PRRole:
    """One ordered PR role that a delivery ticket must close."""

    pr: str
    role: str
    review_head: str
    verification_head: str


@dataclass(frozen=True)
class ArtifactProbeEvidence:
    artifact: str
    probe: str
    succeeded: bool
    current: bool


def _refuse(
    reason: str, head: str | None = None, evidence_state: str = "invalid"
) -> ClosureReadiness:
    return ClosureReadiness(False, "repair-required", reason, head, evidence_state)


def _authored_policy(brief_text: str) -> tuple[str | None, str | None]:
    sections = list(_DELIVERY_CLOSURE.finditer(brief_text))
    if len(sections) != 1:
        return None, "Brief must author exactly one Delivery closure policy"
    policies = list(_POLICY.finditer(sections[0].group("body")))
    if len(policies) != 1:
        return None, "Brief must author exactly one delivery policy"
    return policies[0].group("value"), None


def validate_closure_policy(brief_text: str) -> tuple[str | None, str | None]:
    """Return an authored policy only when its required evidence is present.

    This is the policy parser shared by binding validation and closure checks.
    """
    policy, error = _authored_policy(brief_text)
    if error:
        return None, error
    assert policy is not None
    section = _DELIVERY_CLOSURE.search(brief_text)
    assert section is not None
    fields: dict[str, str] = {}
    for line in section.group("body").splitlines():
        if not line:
            continue
        match = _POLICY_FIELD.fullmatch(line)
        if match is None:
            return None, f"delivery policy has malformed field: {line!r}"
        key, value = match.group("key"), match.group("value")
        if key in fields:
            return None, f"delivery policy evidence field {key!r} is duplicated"
        fields[key] = value
    required = {
        "pr-ci": ("review-evidence", "verification-evidence"),
        "merged": ("pr", "merge-evidence"),
        "artifact": ("artifact", "acceptance-probe"),
    }
    if policy not in required:
        return None, f"delivery policy {policy!r} is unsupported"
    allowed = {"policy", *required[policy]}
    unknown = sorted(set(fields) - allowed)
    if unknown:
        return None, f"delivery policy {policy!r} has unknown field(s): {', '.join(unknown)}"
    missing = [key for key in required[policy] if not fields.get(key, "").strip()]
    if missing:
        return None, f"delivery policy {policy!r} is missing required evidence: {', '.join(missing)}"
    return policy, None


def _policy_fields(brief_text: str) -> dict[str, str]:
    section = _DELIVERY_CLOSURE.search(brief_text)
    assert section is not None
    return {
        match.group("key"): match.group("value")
        for line in section.group("body").splitlines() if line
        for match in [_POLICY_FIELD.fullmatch(line)] if match is not None
    }


def validate_pr_ownership(
    roles: tuple[PRRole, ...], ticket: str | None, owners: dict[str, str] | None,
    ownership_complete: bool,
) -> tuple[str | None, str]:
    """Validate ordered roles against the authoritative complete owner population."""
    if not ticket or owners is None or not ownership_complete:
        return "authoritative PR ownership evidence is missing", "contradictory"
    seen_prs: set[str] = set()
    seen_roles: set[str] = set()
    for role in roles:
        if not role.pr or not role.role or role.pr in seen_prs or role.role in seen_roles:
            return "PR declarations require unique non-empty PR ids and roles", "contradictory"
        seen_prs.add(role.pr)
        seen_roles.add(role.role)
        if owners.get(role.pr) != ticket:
            return f"PR {role.pr} is already owned by delivery ticket {owners.get(role.pr)!r}", "contradictory"
    owned_prs = {pr for pr, owner in owners.items() if owner == ticket}
    if owned_prs != seen_prs:
        return (
            "declared PR roles do not equal the authoritative owned-PR population",
            "contradictory",
        )
    return None, "valid"


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
        state = "unauthorized" if completed.returncode == 4 else "unavailable"
        return None, (
            f"current PR evidence is {state}: "
            + (completed.stderr.strip() or f"gh exited {completed.returncode}")
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return None, f"current PR evidence is unavailable: invalid gh JSON ({exc.msg})"
    if not isinstance(payload, dict):
        return None, "current PR evidence is unavailable: gh returned a non-object"
    return payload, None


def _checks_state(value: Any) -> str:
    if not isinstance(value, list) or not value:
        return "pending"
    for check in value:
        if not isinstance(check, dict):
            return "unavailable"
        kind = check.get("__typename")
        if kind == "StatusContext":
            state = check.get("state")
            if state in {"PENDING", "EXPECTED"}:
                return "pending"
            if state != "SUCCESS":
                return "invalid"
        elif kind == "CheckRun":
            if check.get("status") != "COMPLETED":
                return "pending"
            if check.get("conclusion") is None:
                return "pending"
            if check.get("conclusion") not in _PASS_CONCLUSIONS:
                return "invalid"
        elif kind != "CheckRun":
            return "unavailable"
    return "valid"


def _external_error_state(error: str) -> str:
    normalized = error.lower()
    if "evidence is unauthorized" in normalized:
        return "unauthorized"
    if any(token in normalized for token in ("401", "403", "authentication", "not logged in", "permission")):
        return "unauthorized"
    return "unavailable"


def _evaluate_pr(
    role: PRRole, run: Callable[..., subprocess.CompletedProcess[str]], policy: str
) -> ClosureReadiness:
    payload, error = _run_pr_view(role.pr, run)
    if error:
        return _refuse(error, evidence_state=_external_error_state(error))
    assert payload is not None
    head = payload.get("headRefOid")
    if not isinstance(head, str) or not head:
        return _refuse("current PR evidence has no head SHA", evidence_state="unavailable")
    if policy == "pr-ci" and role.review_head != head:
        return _refuse(
            f"current PR head {head} differs from reviewed head {role.review_head}", head, "stale"
        )
    if policy == "pr-ci" and role.verification_head != head:
        return _refuse(
            f"current PR head {head} differs from verified head {role.verification_head}", head, "stale"
        )
    if payload.get("state") not in {"OPEN", "MERGED"}:
        return _refuse("current PR is not open or merged", head)
    state, merged_at = payload["state"], payload.get("mergedAt")
    if state == "OPEN" and merged_at is not None:
        return _refuse("open PR has contradictory mergedAt evidence", head, "contradictory")
    if state == "MERGED" and (not isinstance(merged_at, str) or not merged_at):
        return _refuse("merged PR has contradictory mergedAt evidence", head, "contradictory")
    checks = _checks_state(payload.get("statusCheckRollup"))
    if checks != "valid":
        return _refuse("current exact-head checks are missing, pending, or non-green", head, checks)
    if policy == "merged":
        if state != "MERGED":
            return _refuse("current PR is not merged", head, "pending")
    return ClosureReadiness(True, "ready", "current formal delivery evidence passes", head, "valid")


def evaluate_closure(
    *,
    brief_text: str,
    plan_text: str,
    acceptance_satisfied: bool,
    review_head: str,
    verification_head: str,
    pr: str,
    pr_roles: tuple[PRRole, ...] | None = None,
    ticket: str | None = None,
    pr_owners: dict[str, str] | None = None,
    ownership_complete: bool = False,
    artifact_probe: ArtifactProbeEvidence | None = None,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> ClosureReadiness:
    """Return read-only closure readiness for the current PR-CI delivery arc."""
    policy, policy_error = validate_closure_policy(brief_text)
    if policy_error:
        return _refuse(policy_error)
    acceptance = _ACCEPTANCE.search(brief_text)
    if acceptance is None or not acceptance.group("body").strip() or not acceptance_satisfied:
        return _refuse("Brief acceptance is not satisfied with formal evidence")
    if not _plan_is_terminal(plan_text):
        return _refuse("delivery requires a terminal Plan before closure")
    if policy == "artifact":
        fields = _policy_fields(brief_text)
        if artifact_probe is None:
            return _refuse(
                "artifact acceptance probe evidence is unavailable", evidence_state="unavailable"
            )
        if artifact_probe.artifact != fields["artifact"] or artifact_probe.probe != fields["acceptance-probe"]:
            return _refuse("artifact probe evidence disagrees with authored artifact or probe", evidence_state="contradictory")
        if not artifact_probe.current:
            return _refuse("artifact probe evidence is stale", evidence_state="stale")
        if not artifact_probe.succeeded:
            return _refuse("artifact acceptance probe failed", evidence_state="invalid")
        return ClosureReadiness(True, "ready", "current artifact evidence passes", evidence_state="valid")
    if policy == "pr-ci" and not review_head and pr_roles is None:
        return _refuse("whole-branch review evidence is missing")
    if policy == "pr-ci" and not verification_head and pr_roles is None:
        return _refuse("verification evidence is missing")
    if not pr and pr_roles is None:
        return _refuse("PR evidence is missing")

    roles = pr_roles or (PRRole(pr, "delivery", review_head, verification_head),)
    if not roles or any(not role.pr or not role.role for role in roles):
        return _refuse("PR evidence is missing")
    ownership_error, ownership_state = validate_pr_ownership(
        roles, ticket, pr_owners, ownership_complete
    )
    if ownership_error:
        return _refuse(ownership_error, evidence_state=ownership_state)
    last_head: str | None = None
    for role in roles:
        result = _evaluate_pr(role, run, policy)
        if not result.ready:
            return _refuse(f"PR role {role.role}: {result.reason}", result.head, result.evidence_state)
        last_head = result.head
    return ClosureReadiness(True, "ready", "current formal delivery evidence passes", last_head, "valid")
