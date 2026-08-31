"""Execution-boundary primitives for docs-review historical replay."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
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


def _identity(record: Mapping[str, object]) -> str:
    payload = json.dumps(
        record,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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
