"""Execution-boundary primitives for docs-review historical replay."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import re
import sqlite3
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
_DISPATCH_OUTCOMES = frozenset(
    {"completed", "partial", "cancelled", "cancellation-uncertain", "failed"}
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


def _dispatch_database(store_root: Path) -> sqlite3.Connection:
    store_root.mkdir(parents=True, exist_ok=True)
    database = store_root / "dispatch-state.sqlite3"
    if database.is_symlink():
        raise ValueError("dispatch state database must not be a symlink")
    connection = sqlite3.connect(database, timeout=30, isolation_level=None)
    connection.execute("PRAGMA busy_timeout=30000")
    connection.execute("PRAGMA synchronous=FULL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS dispatch_leases (
            attempt_id TEXT PRIMARY KEY,
            owner_id TEXT NOT NULL,
            fence_generation INTEGER NOT NULL,
            state TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS dispatch_captures (
            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            fence_generation INTEGER NOT NULL,
            outcome TEXT NOT NULL,
            raw_bytes BLOB NOT NULL,
            raw_digest TEXT NOT NULL,
            late INTEGER NOT NULL,
            scoreable INTEGER NOT NULL
        )
        """
    )
    return connection


def claim_dispatch(
    store_root: Path,
    attempt_id: str,
    owner_id: str,
    *,
    takeover_expected_generation: int | None = None,
) -> dict[str, object]:
    """Claim one dispatch owner or fence an explicitly uncertain predecessor."""
    if not attempt_id.strip() or not owner_id.strip():
        raise ValueError("attempt_id and owner_id are required")
    connection = _dispatch_database(store_root)
    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT owner_id, fence_generation, state FROM dispatch_leases "
            "WHERE attempt_id = ?",
            (attempt_id,),
        ).fetchone()
        if row is None:
            if takeover_expected_generation is not None:
                raise ValueError("takeover has no predecessor lease")
            generation = 1
            connection.execute(
                "INSERT INTO dispatch_leases VALUES (?, ?, ?, 'active')",
                (attempt_id, owner_id, generation),
            )
        else:
            _prior_owner, prior_generation, state = row
            if takeover_expected_generation is None:
                raise ValueError("attempt already has an active owner")
            if (
                state != "uncertain"
                or prior_generation != takeover_expected_generation
            ):
                raise ValueError("takeover does not match an uncertain lease")
            generation = prior_generation + 1
            connection.execute(
                "UPDATE dispatch_leases SET owner_id = ?, fence_generation = ?, "
                "state = 'active' WHERE attempt_id = ?",
                (owner_id, generation, attempt_id),
            )
        connection.execute("COMMIT")
        return {
            "attempt_id": attempt_id,
            "fence_generation": generation,
            "owner_id": owner_id,
            "state": "active",
        }
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()


def capture_dispatch_bytes(
    store_root: Path,
    *,
    attempt_id: str,
    owner_id: str,
    fence_generation: int,
    raw_bytes: bytes,
    outcome: str,
) -> dict[str, object]:
    """Atomically retain every byte stream while fencing stale owners."""
    if outcome not in _DISPATCH_OUTCOMES:
        raise ValueError(f"unsupported dispatch outcome: {outcome}")
    if not isinstance(raw_bytes, bytes):
        raise TypeError("raw_bytes must be bytes")
    connection = _dispatch_database(store_root)
    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT owner_id, fence_generation, state FROM dispatch_leases "
            "WHERE attempt_id = ?",
            (attempt_id,),
        ).fetchone()
        if row is None:
            raise ValueError("dispatch attempt has no lease")
        current_owner, current_generation, state = row
        authoritative = (
            owner_id == current_owner
            and fence_generation == current_generation
            and state == "active"
        )
        late = not authoritative
        scoreable = authoritative and outcome == "completed"
        digest = bytes_digest(raw_bytes)
        cursor = connection.execute(
            "INSERT INTO dispatch_captures "
            "(attempt_id, owner_id, fence_generation, outcome, raw_bytes, "
            "raw_digest, late, scoreable) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                attempt_id,
                owner_id,
                fence_generation,
                outcome,
                raw_bytes,
                digest,
                int(late),
                int(scoreable),
            ),
        )
        if authoritative:
            next_state = "completed" if outcome == "completed" else "uncertain"
            connection.execute(
                "UPDATE dispatch_leases SET state = ? WHERE attempt_id = ?",
                (next_state, attempt_id),
            )
        connection.execute("COMMIT")
        return {
            "capture_sequence": cursor.lastrowid,
            "late": late,
            "outcome": outcome,
            "raw_digest": digest,
            "scoreable": scoreable,
        }
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()


def read_dispatch_captures(
    store_root: Path, attempt_id: str
) -> list[dict[str, object]]:
    """Read immutable capture evidence in commit order."""
    connection = _dispatch_database(store_root)
    try:
        rows = connection.execute(
            "SELECT sequence, owner_id, fence_generation, outcome, raw_bytes, "
            "raw_digest, late, scoreable FROM dispatch_captures "
            "WHERE attempt_id = ? ORDER BY sequence",
            (attempt_id,),
        ).fetchall()
    finally:
        connection.close()
    return [
        {
            "capture_sequence": row[0],
            "owner_id": row[1],
            "fence_generation": row[2],
            "outcome": row[3],
            "raw_bytes": bytes(row[4]),
            "raw_digest": row[5],
            "late": bool(row[6]),
            "scoreable": bool(row[7]),
        }
        for row in rows
    ]
