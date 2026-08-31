"""Execution-boundary primitives for docs-review historical replay."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import re
from typing import Mapping

from docs_review_baseline_store import PublishedRecord, publish_record, read_record


_ECONOMY_MODELS = {
    "claude-code": "haiku",
    "codex": "gpt-5.6-luna",
}
_IDENTITY_FIELDS = (
    "host",
    "model",
    "tier",
    "requested_effort",
    "contract_revision_id",
    "runtime_revision_id",
    "configuration_fingerprint",
)
_COHORT_FIELDS = (
    "corpus_digest",
    "artifact_digest",
    "contract_digest",
    "runtime_digest",
    "configuration_fingerprint",
    "host",
    "model",
    "tier",
    "requested_effort",
)
_REVIEWER_REVISION_KINDS = frozenset(
    {"reviewer_contract_revision", "reviewer_runtime_revision"}
)
_ARTIFACT_INSTRUCTION = re.compile(
    rb"(?:ignore\s+(?:the\s+)?(?:reviewer\s+)?contract|"
    rb"read\s+(?:another|an?\s+external|/)|"
    rb"(?:call|invoke|use)\s+(?:an?\s+)?(?:external\s+)?tool)",
    re.IGNORECASE,
)
_RESOURCE_LIMIT_FIELDS = (
    "max_runs",
    "max_retries_per_case",
    "max_concurrency",
    "max_wall_seconds_per_run",
    "max_input_bytes",
    "max_output_bytes",
    "max_usage_units",
)


def _identity(record: Mapping[str, object]) -> str:
    payload = json.dumps(
        record,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def bytes_digest(content: bytes) -> str:
    """Return the SHA-256 identity of exact artifact bytes."""
    if not isinstance(content, bytes):
        raise TypeError("content must be bytes")
    return hashlib.sha256(content).hexdigest()


def resolve_scored_execution_profile(
    requested: Mapping[str, object],
) -> dict[str, object]:
    """Resolve one exact economy binding without silent model substitution.

    A known host whose actual model identity is unavailable is retained as an
    unscoreable attempt. A known stronger or otherwise mismatched identity is
    refused before dispatch because it cannot provide weak-model evidence.
    """
    host_value = requested.get("host")
    host = host_value.strip() if isinstance(host_value, str) else ""
    if host not in _ECONOMY_MODELS:
        raise ValueError(f"unknown replay host: {host or '<missing>'}")

    resolved: dict[str, object] = {}
    for field in _IDENTITY_FIELDS:
        value = requested.get(field)
        if field == "model" and (not isinstance(value, str) or not value.strip()):
            resolved[field] = None
            continue
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"missing execution identity field: {field}")
        resolved[field] = value.strip()
    resolved["execution_profile"] = "economy"

    if resolved["model"] is None:
        return {
            "identity": _identity(resolved),
            "reason": "exact model identity is unavailable",
            "resolved": resolved,
            "scoreable": False,
        }

    expected_model = _ECONOMY_MODELS[host]
    if (
        resolved["tier"] != "economy"
        or resolved["requested_effort"] != "low"
        or resolved["model"] != expected_model
    ):
        raise ValueError(
            "resolved model, tier, or effort is outside the economy profile"
        )
    return {
        "identity": _identity(resolved),
        "reason": None,
        "resolved": resolved,
        "scoreable": True,
    }


def build_repeat_cohorts(runs: list[Mapping[str, object]]) -> dict[str, object]:
    """Partition valid independent runs by every repeatability identity."""
    groups: dict[str, dict[str, object]] = {}
    excluded: list[dict[str, str]] = []
    seen_run_ids: set[str] = set()
    for run in runs:
        run_value = run.get("run_id")
        run_id = run_value.strip() if isinstance(run_value, str) else ""
        if not run_id:
            raise ValueError("repeat run is missing run_id")
        if run_id in seen_run_ids:
            raise ValueError(f"repeat run_id is not independent: {run_id}")
        seen_run_ids.add(run_id)
        if run.get("valid") is not True or run.get("scoreable") is not True:
            excluded.append(
                {"run_id": run_id, "reason": "run is not valid and scoreable"}
            )
            continue
        identity: dict[str, str] = {}
        for field in _COHORT_FIELDS:
            value = run.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"run {run_id} is missing cohort field: {field}")
            identity[field] = value.strip()
        cohort_id = _identity(identity)
        group = groups.setdefault(
            cohort_id,
            {"cohort_id": cohort_id, "identity": identity, "run_ids": []},
        )
        run_ids = group["run_ids"]
        assert isinstance(run_ids, list)
        run_ids.append(run_id)

    cohorts: list[dict[str, object]] = []
    insufficient: list[dict[str, object]] = []
    for group in sorted(
        groups.values(),
        key=lambda item: tuple(item["identity"][field] for field in _COHORT_FIELDS),
    ):
        group["run_ids"] = sorted(group["run_ids"])
        if len(group["run_ids"]) >= 2:
            cohorts.append(group)
        else:
            insufficient.append(
                {**group, "reason": "repeat cohort requires at least two runs"}
            )
    return {
        "cohorts": cohorts,
        "excluded": sorted(excluded, key=lambda item: item["run_id"]),
        "insufficient": insufficient,
    }


def freeze_reviewer_revision(
    store_root: Path,
    *,
    record_id: str,
    kind: str,
    content: bytes,
    owner: str,
    parent_revision_id: str | None,
    change_reason: str,
) -> PublishedRecord:
    """Freeze contract or runtime bytes with independent revision lineage."""
    if kind not in _REVIEWER_REVISION_KINDS:
        raise ValueError(f"unsupported reviewer revision kind: {kind}")
    if not isinstance(content, bytes) or not content:
        raise ValueError("reviewer revision content must be non-empty bytes")
    if not isinstance(owner, str) or not owner.strip():
        raise ValueError("reviewer revision owner is required")
    if not isinstance(change_reason, str) or not change_reason.strip():
        raise ValueError("reviewer revision change reason is required")
    parent_digest = None
    if parent_revision_id is not None:
        parent = read_record(store_root, parent_revision_id)
        if parent.record.get("kind") != kind:
            raise ValueError("reviewer revision parent kind does not match")
        parent_digest = parent.digest
    record = {
        "change_reason": change_reason.strip(),
        "content_base64": base64.b64encode(content).decode("ascii"),
        "content_digest": hashlib.sha256(content).hexdigest(),
        "kind": kind,
        "owner": owner.strip(),
        "parent_revision_digest": parent_digest,
        "parent_revision_id": parent_revision_id,
        "serialization_version": "docs-reviewer-revision-v1",
    }
    return publish_record(store_root, record_id, record)


def build_isolated_replay_envelope(
    snapshot: bytes,
    *,
    classification: Mapping[str, object] | None,
    campaign_policy: Mapping[str, object],
    reviewer_contract: Mapping[str, object],
) -> dict[str, object]:
    """Bind approved bytes as data and expose only jointly allowed capabilities."""
    digest = bytes_digest(snapshot)
    if classification is None:
        raise ValueError("classification decision is required")
    required_decision_fields = (
        "snapshot_digest",
        "classification",
        "classifier",
        "approver",
        "handling_basis",
        "campaign_policy_revision_id",
    )
    if classification.get("ratified") is not True or any(
        not isinstance(classification.get(field), str)
        or not str(classification[field]).strip()
        for field in required_decision_fields
    ):
        raise ValueError("ratified classification decision is incomplete")
    if classification["snapshot_digest"] != digest:
        raise ValueError("classification decision does not bind snapshot digest")
    policy_revision = campaign_policy.get("revision_id")
    if classification["campaign_policy_revision_id"] != policy_revision:
        raise ValueError("classification decision does not bind campaign policy")
    approved = campaign_policy.get("approved_classifications", [])
    if (
        not isinstance(approved, list)
        or classification["classification"] not in approved
    ):
        raise ValueError("snapshot classification is not approved for replay")
    allowed = campaign_policy.get("allowed_capabilities", [])
    required = reviewer_contract.get("required_capabilities", [])
    if not isinstance(allowed, list) or not all(isinstance(x, str) for x in allowed):
        raise ValueError("campaign capability policy is malformed")
    if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
        raise ValueError("reviewer capability contract is malformed")
    denied = sorted(set(required) - set(allowed))
    if denied:
        raise ValueError("reviewer contract requests a capability denied by policy")
    events = []
    if _ARTIFACT_INSTRUCTION.search(snapshot):
        events.append({"event": "artifact-instruction-denied", "count": 1})
    return {
        "allowed_capabilities": sorted(set(required)),
        "artifact_role": "untrusted-review-content",
        "classification": classification["classification"],
        "content": snapshot,
        "isolation_events": events,
        "snapshot_digest": digest,
    }


def admit_bounded_run(
    *,
    artifact: bytes,
    policy: Mapping[str, object],
    usage: Mapping[str, object],
    requested_wall_seconds: int,
    requested_output_bytes: int,
    reserved_usage_units: int,
) -> dict[str, object]:
    """Admit one whole-artifact run only within every finite campaign limit."""
    limits: dict[str, int] = {}
    for field in _RESOURCE_LIMIT_FIELDS:
        value = policy.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"resource policy requires positive integer {field}")
        limits[field] = value
    counters: dict[str, int] = {}
    for field in ("runs_started", "case_retries", "active_runs", "usage_units"):
        value = usage.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"resource usage requires non-negative integer {field}")
        counters[field] = value
    for name, value in (
        ("requested_wall_seconds", requested_wall_seconds),
        ("requested_output_bytes", requested_output_bytes),
        ("reserved_usage_units", reserved_usage_units),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if counters["runs_started"] >= limits["max_runs"]:
        raise ValueError("run budget exhausted")
    if counters["case_retries"] >= limits["max_retries_per_case"]:
        raise ValueError("retry budget exhausted")
    if counters["active_runs"] >= limits["max_concurrency"]:
        raise ValueError("concurrency budget exhausted")
    if counters["usage_units"] + reserved_usage_units > limits["max_usage_units"]:
        raise ValueError("usage budget exhausted")
    if requested_wall_seconds > limits["max_wall_seconds_per_run"]:
        raise ValueError("wall-time request exceeds limit")
    if requested_output_bytes > limits["max_output_bytes"]:
        raise ValueError("output request exceeds limit")
    if len(artifact) > limits["max_input_bytes"]:
        raise ValueError("whole artifact exceeds input limit; truncation is forbidden")
    return {
        "artifact_bytes": len(artifact),
        "limits": dict(policy),
        "whole_artifact": True,
    }


def verify_execution_identity(
    *,
    prepared: Mapping[str, object],
    dispatch_attestation: Mapping[str, object],
    capture_attestation: Mapping[str, object],
) -> dict[str, object]:
    """Verify prepared weak identity at dispatch and again at capture."""
    expected = {field: prepared.get(field) for field in ("host", "model", "tier")}

    def verdict(
        stage: str, attestation: Mapping[str, object]
    ) -> str | None:
        if any(
            not isinstance(attestation.get(field), str)
            or not str(attestation[field]).strip()
            for field in expected
        ):
            return f"{stage} identity unavailable"
        if any(attestation[field] != expected[field] for field in expected):
            return f"{stage} identity mismatch"
        return None

    reason = verdict("dispatch", dispatch_attestation)
    if reason is None:
        reason = verdict("capture", capture_attestation)
    return {
        "capture_attestation": dict(capture_attestation),
        "dispatch_attestation": dict(dispatch_attestation),
        "prepared_identity": expected,
        "reason": reason,
        "scoreable": reason is None,
    }
