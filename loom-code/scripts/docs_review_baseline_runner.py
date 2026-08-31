"""Execution-boundary primitives for docs-review historical replay."""
from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Callable, Mapping

import docs_review_baseline_store as _store
from docs_review_baseline_store import (
    CampaignCapability,
    PublishedRecord,
    authorize_governed_action_with_capability,
    load_campaign_capability,
    publish_record,
    read_record,
)


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
_REPLAY_BOUNDARY_SEAL = object()


@dataclass(frozen=True, init=False)
class ReplayBoundary:
    """Data-only reviewer input minted from governed records."""

    content: bytes
    snapshot_digest: str
    classification: str
    allowed_capabilities: tuple[str, ...]
    isolation_events: tuple[dict[str, object], ...]
    _seal: object


class ReplayCapabilityBroker:
    """The sole capability interface available to a reviewer adapter."""

    def __init__(self, allowed: tuple[str, ...]) -> None:
        self._allowed = frozenset(allowed)
        self.events: list[dict[str, object]] = []

    def request(self, capability: str) -> None:
        if capability not in self._allowed:
            self.events.append({"event": "capability-denied", "capability": capability})
            raise PermissionError(f"replay capability is denied: {capability}")


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


def build_repeat_cohorts(
    store_root: Path, runs: list[Mapping[str, object]]
) -> dict[str, object]:
    """Partition runs only after resolving distinct immutable attempts."""
    groups: dict[str, dict[str, object]] = {}
    excluded: list[dict[str, str]] = []
    seen_run_ids: set[str] = set()
    seen_attempt_digests: set[str] = set()
    for run in runs:
        run_value = run.get("run_id")
        run_id = run_value.strip() if isinstance(run_value, str) else ""
        if not run_id:
            raise ValueError("repeat run is missing run_id")
        if run_id in seen_run_ids:
            raise ValueError(f"repeat run_id is not independent: {run_id}")
        seen_run_ids.add(run_id)
        attempt_record_id = run.get("attempt_record_id")
        attempt_digest = run.get("attempt_digest")
        if not isinstance(attempt_record_id, str) or not attempt_record_id.strip():
            raise ValueError(f"run {run_id} is missing immutable attempt identity")
        if not isinstance(attempt_digest, str) or not attempt_digest.strip():
            raise ValueError(f"run {run_id} is missing immutable attempt digest")
        if attempt_digest in seen_attempt_digests:
            raise ValueError("repeat runs resolve to the same immutable attempt")
        attempt = read_record(store_root, attempt_record_id)
        if attempt.digest != attempt_digest:
            raise ValueError(f"run {run_id} attempt digest does not match storage")
        if (
            attempt.record.get("kind") != "dispatch_attempt"
            or attempt.record.get("attempt_id") != attempt_record_id
            or attempt.record.get("status") != "prepared"
            or run_id != attempt_record_id
        ):
            raise ValueError(f"run {run_id} does not bind a prepared dispatch attempt")
        seen_attempt_digests.add(attempt_digest)
        outcome_record_id = run.get("outcome_record_id")
        outcome_digest = run.get("outcome_digest")
        if not isinstance(outcome_record_id, str) or not outcome_record_id.strip():
            raise ValueError(f"run {run_id} is missing immutable outcome identity")
        if not isinstance(outcome_digest, str) or not outcome_digest.strip():
            raise ValueError(f"run {run_id} is missing immutable outcome digest")
        outcome = read_record(store_root, outcome_record_id)
        if outcome.digest != outcome_digest:
            raise ValueError(f"run {run_id} outcome digest does not match storage")
        if (
            outcome.record.get("kind") != "dispatch_outcome"
            or outcome.record.get("parent_attempt_id") != attempt.record_id
            or outcome.record.get("parent_digest") != attempt.digest
        ):
            raise ValueError(f"run {run_id} outcome does not bind its attempt")
        if outcome.record.get("outcome") != "success":
            excluded.append(
                {"run_id": run_id, "reason": "run is not valid and scoreable"}
            )
            continue
        profile_record_id = run.get("profile_record_id")
        profile_digest = run.get("profile_digest")
        if not isinstance(profile_record_id, str) or not profile_record_id.strip():
            raise ValueError(f"run {run_id} is missing immutable profile identity")
        if not isinstance(profile_digest, str) or not profile_digest.strip():
            raise ValueError(f"run {run_id} is missing immutable profile digest")
        profile = read_record(store_root, profile_record_id)
        if profile.digest != profile_digest:
            raise ValueError(f"run {run_id} profile digest does not match storage")
        if (
            profile.record.get("kind") != "scored_execution_binding"
            or attempt.record.get("profile_id") != profile.record_id
        ):
            raise ValueError(f"run {run_id} profile does not bind its attempt")
        identity: dict[str, str] = {}
        for field in _COHORT_FIELDS:
            value = profile.record.get(field)
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


def _freeze_governed_replay_record(
    store_root: Path,
    *,
    record_id: str,
    record: Mapping[str, object],
    capability: CampaignCapability,
    actor: str,
) -> PublishedRecord:
    receipt = authorize_governed_action_with_capability(
        store_root,
        capability=capability,
        action="freeze_evidence_population",
        actor=actor,
        target=record_id,
    )
    governed = {
        **dict(record),
        "actor": actor,
        "audit_record_id": receipt.audit_record_id,
        "authorization_nonce": receipt.nonce,
        "authority_revision_digest": receipt.authority_revision_digest,
        "authority_revision_id": receipt.authority_revision_id,
        "trust_root_digest": receipt.trust_root_digest,
    }
    return _store._publish_record_with_authorization_receipt(
        store_root,
        receipt,
        action="freeze_evidence_population",
        actor=actor,
        target=record_id,
        record_id=record_id,
        record=governed,
    )


def freeze_replay_policy(
    store_root: Path,
    *,
    record_id: str,
    approved_classifications: list[str],
    allowed_capabilities: list[str],
    capability: CampaignCapability,
    actor: str,
) -> PublishedRecord:
    """Freeze the classifications and capabilities allowed for replay."""
    if not approved_classifications or not all(
        isinstance(value, str) and value.strip() for value in approved_classifications
    ):
        raise ValueError("approved replay classifications are required")
    if not all(isinstance(value, str) and value.strip() for value in allowed_capabilities):
        raise ValueError("allowed replay capabilities must be names")
    return _freeze_governed_replay_record(
        store_root,
        record_id=record_id,
        capability=capability,
        actor=actor,
        record={
            "allowed_capabilities": sorted(set(allowed_capabilities)),
            "approved_classifications": sorted(set(approved_classifications)),
            "kind": "replay_policy",
            "schema_version": 1,
        },
    )


def freeze_replay_classification(
    store_root: Path,
    *,
    record_id: str,
    snapshot_digest: str,
    classification: str,
    classifier: str,
    approver: str,
    handling_basis: str,
    policy_record_id: str,
    capability: CampaignCapability,
    actor: str,
) -> PublishedRecord:
    """Freeze one classification decision for exact bytes and policy."""
    values = (snapshot_digest, classification, classifier, approver, handling_basis)
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise ValueError("classification decision fields are required")
    policy = read_record(store_root, policy_record_id)
    return _freeze_governed_replay_record(
        store_root,
        record_id=record_id,
        capability=capability,
        actor=actor,
        record={
            "approver": approver,
            "classification": classification,
            "classifier": classifier,
            "handling_basis": handling_basis,
            "kind": "replay_classification",
            "policy_digest": policy.digest,
            "policy_record_id": policy.record_id,
            "schema_version": 1,
            "snapshot_digest": snapshot_digest,
        },
    )


def _publication_marker(store_root: Path, record: PublishedRecord) -> dict[str, object]:
    nonce = record.record.get("authorization_nonce")
    if not isinstance(nonce, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", nonce) is None:
        raise ValueError("governed publication evidence is invalid")
    marker_name = f"{nonce}.json"
    try:
        with _store._receipt_consumption_lock(store_root) as directory_fd:
            payload = _store._read_regular_file(
                directory_fd,
                marker_name,
                Path(_store._RECEIPT_NAMESPACE) / marker_name,
            )
        marker = json.loads(payload.decode("utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("governed publication evidence is invalid") from error
    if not isinstance(marker, dict):
        raise ValueError("governed publication evidence is invalid")
    return marker


def _validate_governed_replay_record(
    store_root: Path, record: PublishedRecord
) -> None:
    capability = load_campaign_capability(store_root)
    audit_id = record.record.get("audit_record_id")
    try:
        audit = read_record(store_root, str(audit_id))
    except (FileNotFoundError, ValueError) as error:
        raise ValueError("governed publication evidence is invalid") from error
    expected_audit = {
        "action": "freeze_evidence_population",
        "actor": record.record.get("actor"),
        "authority_revision_digest": capability.authority_revision_digest,
        "authority_revision_id": capability.authority_revision_id,
        "outcome": "authorized",
        "target": record.record_id,
        "trust_root_digest": capability.trust_root_digest,
    }
    marker = _publication_marker(store_root, record)
    expected_marker = {
        "action": "freeze_evidence_population",
        "actor": record.record.get("actor"),
        "audit_record_id": audit.record_id,
        "kind": "authorization_receipt_consumption",
        "nonce": record.record.get("authorization_nonce"),
        "published_digest": record.digest,
        "published_record_id": record.record_id,
        "schema_version": 1,
        "target": record.record_id,
    }
    authority_fields_match = all(
        record.record.get(field) == value
        for field, value in {
            "authority_revision_digest": capability.authority_revision_digest,
            "authority_revision_id": capability.authority_revision_id,
            "trust_root_digest": capability.trust_root_digest,
        }.items()
    )
    if (
        not authority_fields_match
        or any(audit.record.get(field) != value for field, value in expected_audit.items())
        or marker != expected_marker
    ):
        raise ValueError("governed publication evidence is invalid")


def _load_replay_record(
    store_root: Path, record_id: str, *, missing_message: str
) -> PublishedRecord:
    try:
        record = read_record(store_root, record_id)
    except (FileNotFoundError, ValueError) as error:
        raise ValueError(missing_message) from error
    _validate_governed_replay_record(store_root, record)
    return record


def _seal_replay_boundary(
    snapshot: bytes,
    *,
    classification: str,
    required_capabilities: list[str],
) -> ReplayBoundary:
    events: tuple[dict[str, object], ...] = ()
    if _ARTIFACT_INSTRUCTION.search(snapshot):
        events = ({"event": "artifact-instruction-denied", "count": 1},)
    boundary = object.__new__(ReplayBoundary)
    for field, value in {
        "allowed_capabilities": tuple(sorted(set(required_capabilities))),
        "classification": classification,
        "content": snapshot,
        "isolation_events": events,
        "snapshot_digest": bytes_digest(snapshot),
        "_seal": _REPLAY_BOUNDARY_SEAL,
    }.items():
        object.__setattr__(boundary, field, value)
    return boundary


def build_isolated_replay_envelope(
    store_root: Path,
    snapshot: bytes,
    *,
    classification_record_id: str,
    policy_record_id: str,
    reviewer_contract: Mapping[str, object],
) -> ReplayBoundary:
    """Seal approved bytes as data behind a governed capability boundary."""
    classification = _load_replay_record(
        store_root,
        classification_record_id,
        missing_message="classification decision is required",
    )
    policy = _load_replay_record(
        store_root, policy_record_id, missing_message="replay policy is required"
    )
    digest = bytes_digest(snapshot)
    if classification.record.get("kind") != "replay_classification":
        raise ValueError("classification decision is required")
    if policy.record.get("kind") != "replay_policy":
        raise ValueError("replay policy is required")
    if classification.record.get("snapshot_digest") != digest:
        raise ValueError("classification decision does not bind snapshot digest")
    if (
        classification.record.get("policy_record_id") != policy.record_id
        or classification.record.get("policy_digest") != policy.digest
    ):
        raise ValueError("classification decision does not bind replay policy")
    approved = policy.record.get("approved_classifications", [])
    if classification.record.get("classification") not in approved:
        raise ValueError("snapshot classification is not approved for replay")
    allowed = policy.record.get("allowed_capabilities", [])
    required = reviewer_contract.get("required_capabilities", [])
    if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
        raise ValueError("reviewer capability contract is malformed")
    if sorted(set(required) - set(allowed)):
        raise ValueError("reviewer contract requests a capability denied by policy")
    return _seal_replay_boundary(
        snapshot,
        classification=str(classification.record["classification"]),
        required_capabilities=required,
    )


def run_isolated_reviewer(
    boundary: ReplayBoundary,
    reviewer: Callable[[bytes, ReplayCapabilityBroker], Any],
) -> dict[str, object]:
    """Invoke a trusted adapter with bytes plus the sole capability broker."""
    if not isinstance(boundary, ReplayBoundary) or boundary._seal is not _REPLAY_BOUNDARY_SEAL:
        raise TypeError("replay boundary must come from governed envelope construction")
    broker = ReplayCapabilityBroker(boundary.allowed_capabilities)
    result = reviewer(boundary.content, broker)
    return {
        "isolation_events": [*boundary.isolation_events, *broker.events],
        "result": result,
        "snapshot_digest": boundary.snapshot_digest,
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
