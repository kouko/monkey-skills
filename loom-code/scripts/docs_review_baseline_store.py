"""Immutable JSON record primitives for the docs-review baseline."""
from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid
from typing import Any, Mapping


_RECORD_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_CAPABILITY_SEAL = object()
_RECEIPT_SEAL = object()
_CONSUMED_RECEIPTS: set[str] = set()


class RecordConflictError(ValueError):
    """A record ID already belongs to different immutable bytes."""


@dataclass(frozen=True)
class PublishedRecord:
    """The immutable identity and decoded value of a published record."""

    record_id: str
    digest: str
    record: dict[str, Any]
    path: Path


@dataclass(frozen=True, init=False)
class CampaignCapability:
    """An in-process proof that authority came from campaign bootstrap."""

    store_identity: str
    trust_root_digest: str
    authority_revision_id: str
    authority_revision_digest: str
    _seal: object


@dataclass(frozen=True, init=False)
class AuthorizationReceipt:
    """A sealed, single-use authorization for one exact mutation."""

    store_identity: str
    trust_root_digest: str
    authority_revision_id: str
    authority_revision_digest: str
    actor: str
    action: str
    target: str
    audit_record_id: str
    nonce: str
    _seal: object


def canonical_json_bytes(record: object) -> bytes:
    """Encode JSON with one stable representation suitable for hashing."""
    return json.dumps(
        record,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def record_digest(record: object) -> str:
    """Return the SHA-256 identity of a canonical JSON record."""
    return hashlib.sha256(canonical_json_bytes(record)).hexdigest()


def _record_path(store_root: Path, record_id: str) -> Path:
    if _RECORD_ID.fullmatch(record_id) is None:
        raise ValueError(f"invalid record ID: {record_id!r}")
    return store_root / "records" / f"{record_id}.json"


def _directory_open_flags() -> int:
    """Return the flags required for descriptor-anchored directory traversal."""
    try:
        return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    except AttributeError as error:
        raise OSError("secure no-follow directory operations are unavailable") from error


def _open_directory_path(path: Path, *, create: bool) -> int:
    """Open ``path`` one no-follow component at a time, optionally creating it."""
    flags = _directory_open_flags()
    directory_fd = os.open(os.sep if path.is_absolute() else os.curdir, flags)
    components = path.parts[1:] if path.is_absolute() else path.parts
    try:
        for component in components:
            if component in {"", os.curdir}:
                continue
            if component == os.pardir:
                raise ValueError("store root cannot contain '..'")
            if create:
                try:
                    os.mkdir(component, 0o700, dir_fd=directory_fd)
                except FileExistsError:
                    pass
                else:
                    os.fsync(directory_fd)
            child_fd = os.open(component, flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = child_fd
    except BaseException:
        os.close(directory_fd)
        raise
    return directory_fd


def _open_records_directory(store_root: Path, *, create: bool) -> int:
    store_fd = _open_directory_path(store_root, create=create)
    try:
        if create:
            try:
                os.mkdir("records", 0o700, dir_fd=store_fd)
            except FileExistsError:
                pass
            else:
                os.fsync(store_fd)
        return os.open("records", _directory_open_flags(), dir_fd=store_fd)
    finally:
        os.close(store_fd)


def _read_regular_file(directory_fd: int, name: str, path: Path) -> bytes:
    try:
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    except AttributeError as error:
        raise OSError("secure no-follow record operations are unavailable") from error
    file_fd = os.open(name, flags, dir_fd=directory_fd)
    try:
        if not stat.S_ISREG(os.fstat(file_fd).st_mode):
            raise ValueError(f"published record is not a regular file: {path}")
        chunks: list[bytes] = []
        while chunk := os.read(file_fd, 1024 * 1024):
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(file_fd)


def _write_all(file_fd: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(file_fd, view)
        if written <= 0:
            raise OSError("short record write")
        view = view[written:]


def _published(record_id: str, path: Path, payload: bytes) -> PublishedRecord:
    try:
        record = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"published record is not JSON: {path}") from error
    if not isinstance(record, dict) or canonical_json_bytes(record) != payload:
        raise ValueError(f"published record is not canonical JSON: {path}")
    return PublishedRecord(record_id, hashlib.sha256(payload).hexdigest(), record, path)


def publish_record(
    store_root: Path, record_id: str, record: Mapping[str, object]
) -> PublishedRecord:
    """Atomically publish one canonical payload for ``record_id``.

    Repeating the same bytes succeeds; a different payload for the same ID is
    refused rather than overwriting history.
    """
    store_root = Path(store_root)
    path = _record_path(store_root, record_id)
    payload = canonical_json_bytes(record)
    final_name = path.name
    temporary_name = f".{record_id}.{uuid.uuid4().hex}.tmp"
    records_fd = _open_records_directory(store_root, create=True)
    temporary_fd: int | None = None
    temporary_created = False
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        temporary_fd = os.open(
            temporary_name, flags, 0o600, dir_fd=records_fd
        )
        temporary_created = True
        _write_all(temporary_fd, payload)
        os.fsync(temporary_fd)
        os.close(temporary_fd)
        temporary_fd = None
        try:
            os.link(
                temporary_name,
                final_name,
                src_dir_fd=records_fd,
                dst_dir_fd=records_fd,
                follow_symlinks=False,
            )
        except FileExistsError:
            existing = _read_regular_file(records_fd, final_name, path)
            if existing != payload:
                raise RecordConflictError(
                    f"record ID already has different immutable bytes: {record_id}"
                )
        else:
            os.fsync(records_fd)
    finally:
        if temporary_fd is not None:
            os.close(temporary_fd)
        if temporary_created:
            try:
                os.unlink(temporary_name, dir_fd=records_fd)
            except FileNotFoundError:
                pass
            else:
                os.fsync(records_fd)
        os.close(records_fd)
    return _published(record_id, path, payload)


def read_record(store_root: Path, record_id: str) -> PublishedRecord:
    """Read and validate an existing immutable record."""
    store_root = Path(store_root)
    path = _record_path(store_root, record_id)
    try:
        records_fd = _open_records_directory(store_root, create=False)
    except FileNotFoundError as error:
        raise ValueError(f"record does not exist: {record_id}") from error
    try:
        try:
            payload = _read_regular_file(records_fd, path.name, path)
        except FileNotFoundError as error:
            raise ValueError(f"record does not exist: {record_id}") from error
    finally:
        os.close(records_fd)
    return _published(record_id, path, payload)


def admit_historical_case(
    store_root: Path,
    case_id: str,
    *,
    authorization_receipt: AuthorizationReceipt,
    actor: str,
    snapshot_bytes: bytes | None,
    source_locator: str,
    evidence_locators: list[str],
) -> PublishedRecord:
    """Publish an inspectable historical case without reading its locators.

    ``snapshot_bytes`` is the caller's explicit trusted snapshot input.  The
    locators are retained as provenance only and are never treated as paths.
    """
    if not isinstance(source_locator, str) or not source_locator:
        raise ValueError("source_locator must be a non-empty string")
    if not isinstance(evidence_locators, list) or not evidence_locators:
        raise ValueError("evidence_locators must be a non-empty list")
    if any(not isinstance(locator, str) or not locator for locator in evidence_locators):
        raise ValueError("evidence_locators must contain non-empty strings")
    record: dict[str, object] = {
        "case_id": case_id,
        "evidence_locators": evidence_locators,
        "kind": "historical_case",
        "schema_version": 1,
        "source_locator": source_locator,
    }
    if snapshot_bytes is None:
        record["missing_replay_evidence"] = ["snapshot_bytes"]
        record["status"] = "unscoreable"
    elif isinstance(snapshot_bytes, bytes):
        record["snapshot"] = {
            "bytes_base64": base64.b64encode(snapshot_bytes).decode("ascii"),
            "digest": hashlib.sha256(snapshot_bytes).hexdigest(),
        }
        record["status"] = "candidate"
    else:
        raise ValueError("snapshot_bytes must be bytes or None")
    consume_authorization_receipt(
        Path(store_root),
        authorization_receipt,
        action="nominate_historical_case",
        actor=actor,
        target=case_id,
    )
    return publish_record(store_root, case_id, record)


def _snapshot_value(snapshot_bytes: bytes) -> dict[str, str]:
    if not isinstance(snapshot_bytes, bytes):
        raise ValueError("snapshot_bytes must be bytes")
    return {
        "bytes_base64": base64.b64encode(snapshot_bytes).decode("ascii"),
        "digest": hashlib.sha256(snapshot_bytes).hexdigest(),
    }


def _snapshot_bytes(record: Mapping[str, object]) -> bytes:
    snapshot = record.get("snapshot")
    if not isinstance(snapshot, Mapping):
        raise ValueError("document revision must retain snapshot bytes")
    encoded = snapshot.get("bytes_base64")
    digest = snapshot.get("digest")
    if not isinstance(encoded, str) or not isinstance(digest, str):
        raise ValueError("document revision snapshot is malformed")
    try:
        payload = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError("document revision snapshot is malformed") from error
    if hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError("document revision snapshot digest does not match bytes")
    return payload


def _diff_value(parent: bytes, child: bytes) -> dict[str, str]:
    try:
        parent_text = parent.decode("utf-8").splitlines(keepends=True)
        child_text = child.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as error:
        raise ValueError("document revision snapshots must be UTF-8") from error
    diff_bytes = "".join(
        difflib.unified_diff(
            parent_text,
            child_text,
            fromfile="parent",
            tofile="child",
            lineterm="\n",
        )
    ).encode("utf-8")
    return {
        "algorithm": "unified-diff-utf8-v1",
        "bytes_base64": base64.b64encode(diff_bytes).decode("ascii"),
        "digest": hashlib.sha256(diff_bytes).hexdigest(),
    }


def publish_document_revision(
    store_root: Path,
    revision_id: str,
    *,
    snapshot_bytes: bytes,
    event_locator: str,
    responsible_stage: str,
    lineage_available: bool = True,
) -> PublishedRecord:
    """Freeze an initial document snapshot and its authoring evidence."""
    if not isinstance(lineage_available, bool):
        raise ValueError("lineage_available must be a boolean")
    record: dict[str, object] = {
        "event_locator": _required_text(event_locator, "event_locator"),
        "kind": "document_revision",
        "responsible_stage": _required_text(
            responsible_stage, "responsible_stage"
        ),
        "schema_version": 1,
        "snapshot": _snapshot_value(snapshot_bytes),
    }
    if lineage_available:
        record["diff"] = _diff_value(b"", snapshot_bytes)
        record["lineage_status"] = "root"
    else:
        record["lineage_status"] = "unavailable"
    return publish_record(store_root, revision_id, record)


def correct_document_revision(
    store_root: Path,
    parent_revision_id: str,
    *,
    snapshot_bytes: bytes,
    event_locator: str,
    responsible_stage: str,
) -> PublishedRecord:
    """Freeze a child document snapshot with a reproducible parent diff."""
    parent = read_record(store_root, parent_revision_id)
    if parent.record.get("kind") != "document_revision":
        raise ValueError("document revision parent must be a document revision")
    parent_snapshot = _snapshot_bytes(parent.record)
    child: dict[str, object] = {
        "diff": _diff_value(parent_snapshot, snapshot_bytes),
        "event_locator": _required_text(event_locator, "event_locator"),
        "kind": "document_revision",
        "lineage_status": "child",
        "parent_revision_id": parent_revision_id,
        "responsible_stage": _required_text(
            responsible_stage, "responsible_stage"
        ),
        "schema_version": 1,
        "snapshot": _snapshot_value(snapshot_bytes),
    }
    return append_revision(store_root, parent_revision_id, child)


def ratify_defect_origin(
    store_root: Path,
    revision_id: str,
    *,
    observable_revision_id: str,
    defect_evidence: bytes,
    evidence_locator: str,
    claimed_origin: str,
    ratifier: str,
) -> PublishedRecord:
    """Ratify origin only when immutable revision evidence supports it."""
    if claimed_origin not in {"initial_writing", "fix_introduced", "unknown"}:
        raise ValueError(f"unsupported claimed_origin: {claimed_origin!r}")
    if not isinstance(defect_evidence, bytes) or not defect_evidence:
        raise ValueError("defect_evidence must be non-empty bytes")
    observable = read_record(store_root, observable_revision_id)
    if observable.record.get("kind") != "document_revision":
        raise ValueError("observable revision must be a document revision")
    child_bytes = _snapshot_bytes(observable.record)
    if defect_evidence not in child_bytes:
        raise ValueError("defect_evidence is not observable in the document revision")

    record: dict[str, object] = {
        "claimed_origin": claimed_origin,
        "defect_evidence": _snapshot_value(defect_evidence),
        "eligible_for_official_metrics": False,
        "evidence_locator": _required_text(evidence_locator, "evidence_locator"),
        "governance_status": "unbound",
        "kind": "defect_origin_attribution",
        "observable_revision_digest": observable.digest,
        "observable_revision_id": observable.record_id,
        "ratifier": _human_ratifier(ratifier),
        "schema_version": 1,
    }
    diff = observable.record.get("diff")
    parent_revision_id = observable.record.get("parent_revision_id")
    missing: list[str] = []
    if not isinstance(parent_revision_id, str):
        missing.append("parent_revision")
    if not isinstance(diff, Mapping):
        missing.append("inspectable_diff")

    supported = claimed_origin == "unknown"
    parent: PublishedRecord | None = None
    if not missing and isinstance(parent_revision_id, str):
        parent = read_record(store_root, parent_revision_id)
        parent_bytes = _snapshot_bytes(parent.record)
        expected_diff = _diff_value(parent_bytes, child_bytes)
        expected_stage = {
            "fix_introduced": "remediation",
            "initial_writing": "initial_authoring",
        }.get(claimed_origin)
        supported = (
            expected_stage is not None
            and observable.record.get("parent_digest") == parent.digest
            and diff == expected_diff
            and defect_evidence not in parent_bytes
            and observable.record.get("responsible_stage") == expected_stage
        )
    if supported and claimed_origin != "unknown" and parent is not None:
        record.update(
            {
                "defect_origin": claimed_origin,
                "diff_digest": diff["digest"],
                "excluded_from_origin_rates": False,
                "origin_event_locator": observable.record["event_locator"],
                "parent_revision_digest": parent.digest,
                "parent_revision_id": parent.record_id,
                "responsible_stage": observable.record["responsible_stage"],
            }
        )
        if claimed_origin == "fix_introduced":
            record["remediation_event_locator"] = observable.record[
                "event_locator"
            ]
    else:
        record["defect_origin"] = "unknown"
        record["excluded_from_origin_rates"] = True
        record["missing_revision_evidence"] = missing or [
            "origin_not_supported_by_revision_diff"
        ]
    return publish_record(store_root, revision_id, record)


def ratify_governed_defect_origin(
    store_root: Path,
    revision_id: str,
    *,
    observable_revision_id: str,
    defect_evidence: bytes,
    evidence_locator: str,
    claimed_origin: str,
    ratifier: str,
    capability: CampaignCapability,
) -> PublishedRecord:
    """Bind an origin judgment to frozen authority before it becomes official."""
    governance = _ratification_governance(
        store_root,
        capability=capability,
        action="ratify_defect_origin",
        actor=ratifier,
        target=revision_id,
    )
    if isinstance(governance, PublishedRecord):
        return governance
    authority, independence = governance
    draft = ratify_defect_origin(
        store_root,
        f"{revision_id}--ungoverned-draft",
        observable_revision_id=observable_revision_id,
        defect_evidence=defect_evidence,
        evidence_locator=evidence_locator,
        claimed_origin=claimed_origin,
        ratifier=ratifier,
    )
    record = dict(draft.record)
    record["governance_source_record_id"] = draft.record_id
    _bind_governance(record, authority, independence)
    if independence["status"] != "satisfied":
        record["defect_origin"] = "unknown"
        record["excluded_from_origin_rates"] = True
        record["status"] = "disputed"
    else:
        record["status"] = (
            "ratified"
            if record.get("defect_origin") != "unknown"
            else "unscoreable"
        )
    return publish_record(store_root, revision_id, record)


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


_AUTHORITY_ROLES = {
    "case_nominator",
    "dispute_adjudicator",
    "execution_actor",
    "evidence_freezer",
    "document_author",
    "oracle_author",
    "oracle_ratifier",
    "attribution_ratifier",
    "raw_evidence_inspector",
    "report_publisher",
    "reviewer_output_author",
    "run_dispatcher",
    "run_invalidator",
    "policy_owner",
}

GOVERNED_ACTION_ROLES = {
    "nominate_historical_case": "case_nominator",
    "ratify_oracle": "oracle_ratifier",
    "ratify_attribution": "attribution_ratifier",
    "ratify_defect_origin": "attribution_ratifier",
    "dispatch_review": "run_dispatcher",
    "adjudicate_finding": "dispute_adjudicator",
    "freeze_evidence_population": "evidence_freezer",
    "invalidate_run": "run_invalidator",
    "inspect_raw_evidence": "raw_evidence_inspector",
    "publish_metric_report": "report_publisher",
}

_TRUST_ROOT_NAME = "campaign-trust-root.json"

_CONFLICT_ROLES = {
    "document_author",
    "oracle_author",
    "reviewer_output_author",
    "policy_owner",
}


def _authority_fields(
    *,
    campaign_policy_revision_id: object,
    role_identities: object,
    action_authorities: object,
    allowed_self_ratification: object,
) -> dict[str, object]:
    if not isinstance(role_identities, Mapping):
        raise ValueError("role_identities must be an object")
    roles = {
        _required_text(role, "role name"): _required_text(identity, f"role {role}")
        for role, identity in role_identities.items()
    }
    missing_roles = sorted(_AUTHORITY_ROLES - roles.keys())
    if missing_roles:
        raise ValueError(f"role_identities missing required roles: {missing_roles}")
    if not isinstance(action_authorities, Mapping):
        raise ValueError("action_authorities must be an object")
    actions: dict[str, list[str]] = {}
    for action, identities in action_authorities.items():
        action = _required_text(action, "action")
        if action not in GOVERNED_ACTION_ROLES:
            raise ValueError(f"unsupported governed action: {action!r}")
        if not isinstance(identities, list) or not identities:
            raise ValueError(f"action_authorities.{action} must be a non-empty list")
        actions[action] = sorted(
            {_required_text(identity, f"action_authorities.{action}") for identity in identities}
        )
    missing_actions = sorted(GOVERNED_ACTION_ROLES.keys() - actions.keys())
    if missing_actions:
        raise ValueError(
            f"action_authorities missing required governed actions: {missing_actions}"
        )
    if not isinstance(allowed_self_ratification, list) or any(
        not isinstance(item, str) or "=" not in item
        for item in allowed_self_ratification
    ):
        raise ValueError(
            "allowed_self_ratification must be a list of role=conflict_role rules"
        )
    return {
        "action_authorities": actions,
        "allowed_self_ratification": sorted(set(allowed_self_ratification)),
        "campaign_policy_revision_id": _required_text(
            campaign_policy_revision_id, "campaign_policy_revision_id"
        ),
        "kind": "authority_assignment",
        "role_identities": roles,
        "schema_version": 1,
    }


def _store_identity(store_root: Path) -> str:
    return os.path.abspath(os.fspath(Path(store_root)))


def _publish_campaign_trust_root(
    store_root: Path, record: Mapping[str, object]
) -> PublishedRecord:
    """Create/load the one immutable root outside the generic record namespace."""
    store_root = Path(store_root)
    payload = canonical_json_bytes(record)
    root_fd = _open_directory_path(store_root, create=True)
    temporary_name = f".campaign-trust-root.{uuid.uuid4().hex}.tmp"
    temporary_fd: int | None = None
    temporary_created = False
    path = store_root / _TRUST_ROOT_NAME
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        temporary_fd = os.open(temporary_name, flags, 0o600, dir_fd=root_fd)
        temporary_created = True
        _write_all(temporary_fd, payload)
        os.fsync(temporary_fd)
        os.close(temporary_fd)
        temporary_fd = None
        try:
            os.link(
                temporary_name,
                _TRUST_ROOT_NAME,
                src_dir_fd=root_fd,
                dst_dir_fd=root_fd,
                follow_symlinks=False,
            )
        except FileExistsError:
            existing = _read_regular_file(root_fd, _TRUST_ROOT_NAME, path)
            if existing != payload:
                raise RecordConflictError(
                    "campaign trust root already has different immutable bytes"
                )
        else:
            os.fsync(root_fd)
    finally:
        if temporary_fd is not None:
            os.close(temporary_fd)
        if temporary_created:
            try:
                os.unlink(temporary_name, dir_fd=root_fd)
            except FileNotFoundError:
                pass
            else:
                os.fsync(root_fd)
        os.close(root_fd)
    return _published("campaign-trust-root", path, payload)


def _read_campaign_trust_root(store_root: Path) -> PublishedRecord:
    store_root = Path(store_root)
    root_fd = _open_directory_path(store_root, create=False)
    path = store_root / _TRUST_ROOT_NAME
    try:
        try:
            payload = _read_regular_file(root_fd, _TRUST_ROOT_NAME, path)
        except FileNotFoundError as error:
            raise ValueError("campaign trust root does not exist") from error
    finally:
        os.close(root_fd)
    return _published("campaign-trust-root", path, payload)


def _make_capability(
    store_root: Path, trust_root: PublishedRecord, authority: PublishedRecord
) -> CampaignCapability:
    capability = object.__new__(CampaignCapability)
    for field, value in {
        "store_identity": _store_identity(store_root),
        "trust_root_digest": trust_root.digest,
        "authority_revision_id": authority.record_id,
        "authority_revision_digest": authority.digest,
        "_seal": _CAPABILITY_SEAL,
    }.items():
        object.__setattr__(capability, field, value)
    return capability


def bootstrap_campaign_authority(
    store_root: Path,
    revision_id: str,
    *,
    campaign_policy_revision_id: str,
    role_identities: Mapping[str, str],
    action_authorities: Mapping[str, list[str]],
    allowed_self_ratification: list[str],
) -> tuple[PublishedRecord, CampaignCapability]:
    """Create/load the unique trust root and return its sealed live authority."""
    authority_fields = _authority_fields(
        campaign_policy_revision_id=campaign_policy_revision_id,
        role_identities=role_identities,
        action_authorities=action_authorities,
        allowed_self_ratification=allowed_self_ratification,
    )
    trust_root = _publish_campaign_trust_root(
        Path(store_root),
        {
            "authority_fields_digest": record_digest(authority_fields),
            "authority_revision_id": _required_text(revision_id, "revision_id"),
            "kind": "campaign_trust_root",
            "schema_version": 1,
        },
    )
    bound_authority = dict(authority_fields)
    bound_authority["trust_root_digest"] = trust_root.digest
    authority = publish_record(Path(store_root), revision_id, bound_authority)
    return authority, _make_capability(Path(store_root), trust_root, authority)


def load_campaign_capability(store_root: Path) -> CampaignCapability:
    """Load the immutable root and mint a capability only from its binding."""
    trust_root = _read_campaign_trust_root(Path(store_root))
    authority_id = _required_text(
        trust_root.record.get("authority_revision_id"), "authority_revision_id"
    )
    authority = read_record(Path(store_root), authority_id)
    expected_fields = dict(authority.record)
    root_digest = expected_fields.pop("trust_root_digest", None)
    if root_digest != trust_root.digest or record_digest(expected_fields) != (
        trust_root.record.get("authority_fields_digest")
    ):
        raise ValueError("campaign authority does not match the trust root")
    return _make_capability(Path(store_root), trust_root, authority)


def _validate_capability(
    store_root: Path, capability: object
) -> tuple[CampaignCapability, PublishedRecord]:
    if not isinstance(capability, CampaignCapability) or capability._seal is not _CAPABILITY_SEAL:
        raise TypeError("capability must come from campaign bootstrap")
    if capability.store_identity != _store_identity(store_root):
        raise ValueError("capability belongs to a different store")
    loaded = load_campaign_capability(Path(store_root))
    if (
        loaded.trust_root_digest != capability.trust_root_digest
        or loaded.authority_revision_id != capability.authority_revision_id
        or loaded.authority_revision_digest != capability.authority_revision_digest
    ):
        raise ValueError("capability is stale")
    return capability, read_record(Path(store_root), capability.authority_revision_id)


def publish_authority_assignment(
    store_root: Path,
    revision_id: str,
    *,
    campaign_policy_revision_id: str,
    role_identities: Mapping[str, str],
    action_authorities: Mapping[str, list[str]],
    allowed_self_ratification: list[str],
) -> PublishedRecord:
    """Freeze campaign roles, action authority, and independence exceptions."""
    return publish_record(
        store_root,
        revision_id,
        _authority_fields(
            campaign_policy_revision_id=campaign_policy_revision_id,
            role_identities=role_identities,
            action_authorities=action_authorities,
            allowed_self_ratification=allowed_self_ratification,
        ),
    )


def revise_authority_assignment(
    store_root: Path,
    parent_revision_id: str,
    *,
    role_identities: Mapping[str, str],
    action_authorities: Mapping[str, list[str]],
    allowed_self_ratification: list[str],
    reason: str,
) -> PublishedRecord:
    """Record a reason-bearing role change as a child authority revision."""
    parent = read_record(store_root, parent_revision_id)
    if parent.record.get("kind") != "authority_assignment":
        raise ValueError("authority revision parent must be an authority assignment")
    child = _authority_fields(
        campaign_policy_revision_id=parent.record.get(
            "campaign_policy_revision_id"
        ),
        role_identities=role_identities,
        action_authorities=action_authorities,
        allowed_self_ratification=allowed_self_ratification,
    )
    child["parent_revision_id"] = parent_revision_id
    child["revision_reason"] = _required_text(reason, "reason")
    return append_revision(store_root, parent_revision_id, child)


def _governed_action_authority(
    store_root: Path,
    *,
    authority_revision_id: str,
    action: str,
    actor: str,
    trusted_authority_revision_digest: str,
) -> tuple[PublishedRecord, dict[str, object], str, bool]:
    if action not in GOVERNED_ACTION_ROLES:
        raise ValueError(f"unsupported governed action: {action!r}")
    authority = read_record(store_root, authority_revision_id)
    if authority.record.get("kind") != "authority_assignment":
        raise ValueError("authority_revision_id must name an authority assignment")
    trusted_digest = _required_text(
        trusted_authority_revision_digest, "trusted_authority_revision_digest"
    )
    if re.fullmatch(r"[0-9a-f]{64}", trusted_digest) is None:
        raise ValueError(
            "trusted_authority_revision_digest must be a lowercase SHA-256 digest"
        )
    if authority.digest != trusted_digest:
        raise ValueError("authority assignment does not match trusted authority revision digest")
    actor = _required_text(actor, "actor")
    try:
        assignment = _authority_fields(
            campaign_policy_revision_id=authority.record.get(
                "campaign_policy_revision_id"
            ),
            role_identities=authority.record.get("role_identities"),
            action_authorities=authority.record.get("action_authorities"),
            allowed_self_ratification=authority.record.get(
                "allowed_self_ratification"
            ),
        )
    except ValueError as error:
        raise ValueError("authority assignment is malformed") from error
    if any(authority.record.get(field) != value for field, value in assignment.items()):
        raise ValueError("authority assignment is malformed")
    actions = assignment["action_authorities"]
    roles = assignment["role_identities"]
    exceptions = assignment["allowed_self_ratification"]
    permitted = actions.get(action, [])
    action_role = GOVERNED_ACTION_ROLES[action]
    authorized = actor in permitted and roles.get(action_role) == actor
    return authority, assignment, actor, authorized


def _ratification_authority_evidence(
    store_root: Path,
    *,
    authority_revision_id: str,
    action: str,
    actor: str,
    trusted_authority_revision_digest: str,
) -> tuple[PublishedRecord, dict[str, object], bool]:
    actor = _human_ratifier(actor)
    authority, assignment, actor, authorized = _governed_action_authority(
        store_root,
        authority_revision_id=authority_revision_id,
        action=action,
        actor=actor,
        trusted_authority_revision_digest=trusted_authority_revision_digest,
    )
    roles = assignment["role_identities"]
    exceptions = assignment["allowed_self_ratification"]
    ratifier_role = GOVERNED_ACTION_ROLES[action]
    conflicts = sorted(
        role
        for role in _CONFLICT_ROLES
        if roles.get(role) == actor
        and f"{ratifier_role}={role}" not in exceptions
    )
    evidence = {
        "allowed_exceptions": list(exceptions),
        "conflicting_roles": conflicts,
        "ratifier_role": ratifier_role,
        "rule": "distinct-role-identity-v1",
        "status": "insufficient" if conflicts else "satisfied",
    }
    return authority, evidence, authorized


def authorize_governed_action(
    store_root: Path,
    *,
    authority_revision_id: str,
    action: str,
    actor: str,
    target: str,
    trusted_authority_revision_digest: str,
) -> PublishedRecord:
    """Audit one authority decision before a caller mutates its target."""
    authority, _assignment, actor, authorized = _governed_action_authority(
        store_root,
        authority_revision_id=authority_revision_id,
        action=action,
        actor=actor,
        trusted_authority_revision_digest=trusted_authority_revision_digest,
    )
    audit = {
        "action": action,
        "actor": actor,
        "authority_revision_digest": authority.digest,
        "authority_revision_id": authority.record_id,
        "campaign_policy_revision_id": authority.record[
            "campaign_policy_revision_id"
        ],
        "kind": "governance_audit_event",
        "outcome": "authorized" if authorized else "refused_unauthorized",
        "schema_version": 1,
        "target": _required_text(target, "target"),
    }
    return publish_record(store_root, f"audit-{record_digest(audit)}", audit)


def _make_receipt(
    capability: CampaignCapability,
    *,
    actor: str,
    action: str,
    target: str,
    audit_record_id: str,
) -> AuthorizationReceipt:
    receipt = object.__new__(AuthorizationReceipt)
    for field, value in {
        "store_identity": capability.store_identity,
        "trust_root_digest": capability.trust_root_digest,
        "authority_revision_id": capability.authority_revision_id,
        "authority_revision_digest": capability.authority_revision_digest,
        "actor": actor,
        "action": action,
        "target": target,
        "audit_record_id": audit_record_id,
        "nonce": uuid.uuid4().hex,
        "_seal": _RECEIPT_SEAL,
    }.items():
        object.__setattr__(receipt, field, value)
    return receipt


def authorize_governed_action_with_capability(
    store_root: Path,
    *,
    capability: CampaignCapability,
    action: str,
    actor: str,
    target: str,
) -> AuthorizationReceipt:
    """Audit a decision and return a sealed receipt only on authorization."""
    capability, authority = _validate_capability(Path(store_root), capability)
    authority, _assignment, actor, authorized = _governed_action_authority(
        Path(store_root),
        authority_revision_id=authority.record_id,
        action=action,
        actor=actor,
        trusted_authority_revision_digest=authority.digest,
    )
    target = _required_text(target, "target")
    audit = {
        "action": action,
        "actor": actor,
        "authority_revision_digest": authority.digest,
        "authority_revision_id": authority.record_id,
        "campaign_policy_revision_id": authority.record[
            "campaign_policy_revision_id"
        ],
        "kind": "governance_audit_event",
        "outcome": "authorized" if authorized else "refused_unauthorized",
        "schema_version": 1,
        "target": target,
        "trust_root_digest": capability.trust_root_digest,
    }
    audit_record = publish_record(
        Path(store_root), f"audit-{record_digest(audit)}", audit
    )
    if not authorized:
        raise PermissionError(f"actor is not authorized for {action}")
    return _make_receipt(
        capability,
        actor=actor,
        action=action,
        target=target,
        audit_record_id=audit_record.record_id,
    )


def consume_authorization_receipt(
    store_root: Path,
    receipt: AuthorizationReceipt,
    *,
    action: str,
    actor: str,
    target: str,
) -> None:
    """Validate and consume one receipt before its exact target mutation."""
    if (
        not isinstance(receipt, AuthorizationReceipt)
        or getattr(receipt, "_seal", None) is not _RECEIPT_SEAL
    ):
        raise TypeError("receipt must come from governed action authorization")
    if receipt.store_identity != _store_identity(store_root):
        raise ValueError("receipt belongs to a different store")
    if receipt.action != action:
        raise ValueError("receipt action does not match")
    if receipt.actor != actor:
        raise ValueError("receipt actor does not match")
    if receipt.target != target:
        raise ValueError("receipt target does not match")
    if receipt.nonce in _CONSUMED_RECEIPTS:
        raise ValueError("receipt is already consumed or stale")
    capability = object.__new__(CampaignCapability)
    for field, value in {
        "store_identity": receipt.store_identity,
        "trust_root_digest": receipt.trust_root_digest,
        "authority_revision_id": receipt.authority_revision_id,
        "authority_revision_digest": receipt.authority_revision_digest,
        "_seal": _CAPABILITY_SEAL,
    }.items():
        object.__setattr__(capability, field, value)
    _validate_capability(Path(store_root), capability)
    audit = read_record(Path(store_root), receipt.audit_record_id)
    if audit.record.get("outcome") != "authorized" or any(
        audit.record.get(field) != value
        for field, value in {
            "action": receipt.action,
            "actor": receipt.actor,
            "authority_revision_digest": receipt.authority_revision_digest,
            "authority_revision_id": receipt.authority_revision_id,
            "target": receipt.target,
            "trust_root_digest": receipt.trust_root_digest,
        }.items()
    ):
        raise ValueError("receipt audit binding is invalid")
    _CONSUMED_RECEIPTS.add(receipt.nonce)


def _ratification_governance(
    store_root: Path,
    *,
    capability: CampaignCapability,
    action: str,
    actor: str,
    target: str,
) -> tuple[PublishedRecord, dict[str, object]] | PublishedRecord:
    capability, authority = _validate_capability(Path(store_root), capability)
    authority, evidence, authorized = _ratification_authority_evidence(
        store_root,
        authority_revision_id=authority.record_id,
        action=action,
        actor=actor,
        trusted_authority_revision_digest=authority.digest,
    )
    if not authorized:
        audit = {
            "action": action,
            "actor": actor,
            "authority_revision_digest": authority.digest,
            "authority_revision_id": authority.record_id,
            "campaign_policy_revision_id": authority.record[
                "campaign_policy_revision_id"
            ],
            "kind": "governance_audit_event",
            "outcome": "refused_unauthorized",
            "schema_version": 1,
            "target": target,
        }
        return publish_record(store_root, f"audit-{record_digest(audit)}", audit)
    return authority, evidence


def _validated_findings(findings: object) -> list[dict[str, object]]:
    if not isinstance(findings, list) or not findings:
        raise ValueError("findings must be a non-empty list")
    validated: list[dict[str, object]] = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, Mapping):
            raise ValueError(f"findings[{index}] must be an object")
        item = dict(finding)
        for field in ("finding_id", "expectation", "rationale", "evidence_locator"):
            _required_text(item.get(field), f"findings[{index}].{field}")
        validated.append(item)
    return validated


def _oracle_fields(
    *,
    case_id: object,
    snapshot_digest: object,
    findings: object,
    negative_control_intent: object,
    ratifier: object,
) -> dict[str, object]:
    digest = _required_text(snapshot_digest, "snapshot_digest")
    if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("snapshot_digest must be a lowercase SHA-256 digest")
    return {
        "case_id": _required_text(case_id, "case_id"),
        "eligible_for_official_metrics": False,
        "findings": _validated_findings(findings),
        "governance_status": "unbound",
        "kind": "ratified_oracle",
        "negative_control_intent": _required_text(
            negative_control_intent, "negative_control_intent"
        ),
        "ratifier": _required_text(ratifier, "ratifier"),
        "schema_version": 1,
        "snapshot_digest": digest,
        "status": "ratified",
    }


def ratify_oracle(
    store_root: Path,
    revision_id: str,
    *,
    case_id: str,
    snapshot_digest: str,
    findings: list[Mapping[str, object]],
    negative_control_intent: str,
    ratifier: str,
) -> PublishedRecord:
    """Freeze one complete, named human oracle revision."""
    record = _oracle_fields(
        case_id=case_id,
        snapshot_digest=snapshot_digest,
        findings=findings,
        negative_control_intent=negative_control_intent,
        ratifier=ratifier,
    )
    return publish_record(store_root, revision_id, record)


def ratify_governed_oracle(
    store_root: Path,
    revision_id: str,
    *,
    case_id: str,
    snapshot_digest: str,
    findings: list[Mapping[str, object]],
    negative_control_intent: str,
    ratifier: str,
    capability: CampaignCapability,
) -> PublishedRecord:
    """Ratify an oracle only through frozen authority and independence rules."""
    governance = _ratification_governance(
        store_root,
        capability=capability,
        action="ratify_oracle",
        actor=ratifier,
        target=revision_id,
    )
    if isinstance(governance, PublishedRecord):
        return governance
    authority, independence = governance
    record = _oracle_fields(
        case_id=case_id,
        snapshot_digest=snapshot_digest,
        findings=findings,
        negative_control_intent=negative_control_intent,
        ratifier=ratifier,
    )
    _bind_governance(record, authority, independence)
    if independence["status"] != "satisfied":
        record["status"] = "disputed"
    return publish_record(store_root, revision_id, record)


def correct_oracle(
    store_root: Path,
    parent_revision_id: str,
    *,
    findings: list[Mapping[str, object]],
    negative_control_intent: str,
    reason: str,
    ratifier: str,
) -> PublishedRecord:
    """Freeze a reason-bearing child while preserving the ratified parent."""
    parent = read_record(store_root, parent_revision_id)
    if parent.record.get("kind") != "ratified_oracle" or parent.record.get(
        "status"
    ) != "ratified":
        raise ValueError("oracle correction parent must be a ratified oracle")
    child = _oracle_fields(
        case_id=parent.record.get("case_id"),
        snapshot_digest=parent.record.get("snapshot_digest"),
        findings=findings,
        negative_control_intent=negative_control_intent,
        ratifier=ratifier,
    )
    child["correction_reason"] = _required_text(reason, "reason")
    child["parent_revision_id"] = parent_revision_id
    return append_revision(store_root, parent_revision_id, child)


def freeze_corpus_manifest(
    store_root: Path,
    bindings: list[tuple[str, str, str]],
    *,
    capability: CampaignCapability,
) -> PublishedRecord:
    """Freeze an exact ordered corpus and return its digest-bound revision."""
    capability, trusted_authority = _validate_capability(Path(store_root), capability)
    trusted_digests = [trusted_authority.digest]
    if not isinstance(bindings, list) or not bindings:
        raise ValueError("corpus bindings must be a non-empty list")
    manifest_bindings: list[dict[str, str]] = []
    seen_cases: set[str] = set()
    for index, binding in enumerate(bindings):
        if not isinstance(binding, tuple) or len(binding) != 3:
            raise ValueError(
                f"bindings[{index}] must be (case_id, snapshot_digest, oracle_revision_id)"
            )
        case_id, snapshot_digest, oracle_revision_id = binding
        case_id = _required_text(case_id, f"bindings[{index}].case_id")
        snapshot_digest = _required_text(
            snapshot_digest, f"bindings[{index}].snapshot_digest"
        )
        oracle_revision_id = _required_text(
            oracle_revision_id, f"bindings[{index}].oracle_revision_id"
        )
        if oracle_revision_id == "latest":
            raise ValueError("corpus bindings must not use latest")
        if re.fullmatch(r"[0-9a-f]{64}", snapshot_digest) is None:
            raise ValueError(
                f"bindings[{index}].snapshot_digest must be a lowercase SHA-256 digest"
            )
        if case_id in seen_cases:
            raise ValueError(f"duplicate corpus case_id: {case_id}")
        oracle = read_record(store_root, oracle_revision_id)
        if (
            oracle.record.get("kind") != "ratified_oracle"
            or oracle.record.get("status") != "ratified"
        ):
            raise ValueError(
                f"binding {case_id} oracle revision is not ratified: {oracle_revision_id}"
            )
        independence = oracle.record.get("independence_evidence")
        if (
            oracle.record.get("governance_status") != "bound"
            or not isinstance(independence, Mapping)
            or independence.get("status") != "satisfied"
        ):
            raise ValueError(
                f"binding {case_id} oracle governance is not bound and satisfied: "
                f"{oracle_revision_id}"
            )
        if oracle.record.get("eligible_for_official_metrics") is not True:
            raise ValueError(
                f"binding {case_id} oracle is not eligible for official metrics: "
                f"{oracle_revision_id}"
            )
        authority_revision_id = _required_text(
            oracle.record.get("authority_revision_id"),
            f"binding {case_id} oracle authority_revision_id",
        )
        authority_revision_digest = _required_text(
            oracle.record.get("authority_revision_digest"),
            f"binding {case_id} oracle authority_revision_digest",
        )
        if authority_revision_digest not in trusted_digests:
            raise ValueError(
                f"binding {case_id} oracle does not match a trusted authority revision digest: "
                f"{oracle_revision_id}"
            )
        if oracle.record.get("authority_trust") != {
            "rule": "campaign-bootstrap-digest-v1",
            "trusted_authority_revision_digest": authority_revision_digest,
        }:
            raise ValueError(
                f"binding {case_id} oracle trust decision does not match authority: "
                f"{oracle_revision_id}"
            )
        authority, recomputed_independence, authorized = (
            _ratification_authority_evidence(
                store_root,
                authority_revision_id=authority_revision_id,
                action="ratify_oracle",
                actor=oracle.record.get("ratifier"),
                trusted_authority_revision_digest=authority_revision_digest,
            )
        )
        if oracle.record.get("authority_revision_digest") != authority.digest:
            raise ValueError(
                f"binding {case_id} oracle authority revision digest does not match: "
                f"{oracle_revision_id}"
            )
        if not authorized:
            raise ValueError(
                f"binding {case_id} oracle authority does not authorize ratifier: "
                f"{oracle_revision_id}"
            )
        if dict(independence) != recomputed_independence:
            raise ValueError(
                f"binding {case_id} oracle independence evidence does not match "
                f"authority: {oracle_revision_id}"
            )
        if oracle.record.get("role_identities") != authority.record.get(
            "role_identities"
        ):
            raise ValueError(
                f"binding {case_id} oracle role assignment does not match authority: "
                f"{oracle_revision_id}"
            )
        if oracle.record.get("case_id") != case_id:
            raise ValueError(
                f"binding {case_id} oracle describes a different case: {oracle_revision_id}"
            )
        if oracle.record.get("snapshot_digest") != snapshot_digest:
            raise ValueError(
                f"binding {case_id} oracle snapshot digest does not match: "
                f"{oracle_revision_id}"
            )
        seen_cases.add(case_id)
        manifest_bindings.append(
            {
                "case_id": case_id,
                "authority_revision_digest": authority_revision_digest,
                "oracle_revision_id": oracle_revision_id,
                "snapshot_digest": snapshot_digest,
            }
        )
    record: dict[str, object] = {
        "bindings": manifest_bindings,
        "kind": "corpus_manifest",
        "schema_version": 1,
        "trusted_authority_revision_digests": trusted_digests,
    }
    return publish_record(store_root, f"corpus-{record_digest(record)}", record)


_DISPATCH_OUTCOMES = {
    "success",
    "timeout",
    "transport_failure",
    "parse_failure",
    "cancelled",
    "interruption",
    "quota_exhaustion",
}

_HUMAN_VERDICTS = {
    "true_positive",
    "false_positive",
    "duplicate",
    "new_defect",
    "oracle_escape",
    "unscorable",
    "unknown",
    "disputed",
}

_DEFECT_ORIGINS = {"initial_writing", "fix_introduced", "unknown"}


def prepare_dispatch_attempt(
    store_root: Path,
    attempt_id: str,
    *,
    authorization_receipt: AuthorizationReceipt,
    actor: str,
    sequence: int,
    profile_id: str,
    corpus_id: str,
    case_id: str,
) -> PublishedRecord:
    """Consume exact dispatch authority, then persist immutable bindings."""
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise ValueError("sequence must be a positive integer")
    attempt_id = _required_text(attempt_id, "attempt_id")
    record: dict[str, object] = {
        "attempt_id": attempt_id,
        "case_id": _required_text(case_id, "case_id"),
        "corpus_id": _required_text(corpus_id, "corpus_id"),
        "kind": "dispatch_attempt",
        "profile_id": _required_text(profile_id, "profile_id"),
        "schema_version": 1,
        "sequence": sequence,
        "status": "prepared",
    }
    consume_authorization_receipt(
        Path(store_root),
        authorization_receipt,
        action="dispatch_review",
        actor=actor,
        target=attempt_id,
    )
    return publish_record(store_root, attempt_id, record)


def record_dispatch_outcome(
    store_root: Path,
    attempt_id: str,
    *,
    outcome: str,
    resource_telemetry: Mapping[str, object],
    raw_response_bytes: bytes | None = None,
    failure: str | None = None,
) -> PublishedRecord:
    """Attach one immutable terminal child to a prepared dispatch attempt."""
    parent = read_record(store_root, attempt_id)
    if parent.record.get("kind") != "dispatch_attempt" or parent.record.get(
        "status"
    ) != "prepared":
        raise ValueError("dispatch outcome parent must be a prepared attempt")
    if outcome not in _DISPATCH_OUTCOMES:
        raise ValueError(f"unsupported dispatch outcome: {outcome!r}")
    if not isinstance(resource_telemetry, Mapping):
        raise ValueError("resource_telemetry must be an object")
    if outcome in {"success", "parse_failure"} and not isinstance(
        raw_response_bytes, bytes
    ):
        raise ValueError(f"raw_response_bytes are required for {outcome}")
    if raw_response_bytes is not None and not isinstance(raw_response_bytes, bytes):
        raise ValueError("raw_response_bytes must be bytes or None")
    if outcome == "success":
        if failure is not None:
            raise ValueError("success must not carry a failure")
    else:
        failure = _required_text(failure, "failure")

    record: dict[str, object] = {
        "kind": "dispatch_outcome",
        "outcome": outcome,
        "parent_attempt_id": attempt_id,
        "parent_digest": parent.digest,
        "resource_telemetry": dict(resource_telemetry),
        "schema_version": 1,
    }
    if failure is not None:
        record["failure"] = failure
    if raw_response_bytes is not None:
        record["raw_response"] = {
            "bytes_base64": base64.b64encode(raw_response_bytes).decode("ascii"),
            "digest": hashlib.sha256(raw_response_bytes).hexdigest(),
        }
    return publish_record(store_root, f"{attempt_id}--outcome", record)


def capture_finding_observation(
    store_root: Path,
    observation_id: str,
    *,
    outcome_record_id: str,
    finding_identity: str,
    raw_span: bytes,
    payload_hash: str,
    wording: str,
    location: str,
    severity: str,
    reviewer_verdict: str,
) -> PublishedRecord:
    """Preserve one reviewer-stated finding without adjudicating its truth."""
    record = _observation_fields(
        store_root,
        outcome_record_id=outcome_record_id,
        finding_identity=finding_identity,
        raw_span=raw_span,
        payload_hash=payload_hash,
        wording=wording,
        location=location,
        severity=severity,
        reviewer_verdict=reviewer_verdict,
    )
    return publish_record(store_root, observation_id, record)


def _observation_fields(
    store_root: Path,
    *,
    outcome_record_id: str,
    finding_identity: str,
    raw_span: bytes,
    payload_hash: str,
    wording: str,
    location: str,
    severity: str,
    reviewer_verdict: str,
) -> dict[str, object]:
    outcome = read_record(store_root, outcome_record_id)
    if outcome.record.get("kind") != "dispatch_outcome":
        raise ValueError("observation parent must be a dispatch outcome")
    attempt_record_id = _required_text(
        outcome.record.get("parent_attempt_id"), "parent_attempt_id"
    )
    attempt = read_record(store_root, attempt_record_id)
    if outcome.record.get("parent_digest") != attempt.digest:
        raise ValueError("dispatch outcome does not match its attempt parent")
    raw_response = outcome.record.get("raw_response")
    if not isinstance(raw_response, Mapping):
        raise ValueError("observation parent must retain raw response bytes")
    if not isinstance(raw_span, bytes) or not raw_span:
        raise ValueError("raw_span must be non-empty bytes")
    try:
        response_bytes = base64.b64decode(
            _required_text(raw_response.get("bytes_base64"), "raw response bytes"),
            validate=True,
        )
    except ValueError as error:
        raise ValueError("observation parent raw response is invalid") from error
    if raw_span not in response_bytes:
        raise ValueError("raw_span must occur in the parent raw response")
    payload_hash = _required_text(payload_hash, "payload_hash")
    if re.fullmatch(r"[0-9a-f]{64}", payload_hash) is None:
        raise ValueError("payload_hash must be a lowercase SHA-256 digest")
    record: dict[str, object] = {
        "attempt_digest": attempt.digest,
        "attempt_record_id": attempt.record_id,
        "finding_identity": _required_text(finding_identity, "finding_identity"),
        "kind": "finding_observation",
        "location": _required_text(location, "location"),
        "outcome_digest": outcome.digest,
        "outcome_record_id": outcome_record_id,
        "payload_hash": payload_hash,
        "raw_span": {
            "bytes_base64": base64.b64encode(raw_span).decode("ascii"),
            "digest": hashlib.sha256(raw_span).hexdigest(),
        },
        "reviewer_verdict": _required_text(reviewer_verdict, "reviewer_verdict"),
        "schema_version": 1,
        "severity": _required_text(severity, "severity"),
        "wording": _required_text(wording, "wording"),
    }
    return record


def correct_finding_observation(
    store_root: Path,
    parent_observation_id: str,
    *,
    finding_identity: str,
    raw_span: bytes,
    payload_hash: str,
    wording: str,
    location: str,
    severity: str,
    reviewer_verdict: str,
    reason: str,
) -> PublishedRecord:
    """Preserve a parser correction as a child observation revision."""
    parent = read_record(store_root, parent_observation_id)
    if parent.record.get("kind") != "finding_observation":
        raise ValueError("observation correction parent must be an observation")
    outcome_record_id = _required_text(
        parent.record.get("outcome_record_id"), "outcome_record_id"
    )
    child = _observation_fields(
        store_root,
        outcome_record_id=outcome_record_id,
        finding_identity=finding_identity,
        raw_span=raw_span,
        payload_hash=payload_hash,
        wording=wording,
        location=location,
        severity=severity,
        reviewer_verdict=reviewer_verdict,
    )
    child["correction_reason"] = _required_text(reason, "reason")
    child["parent_observation_id"] = parent_observation_id
    return append_revision(store_root, parent_observation_id, child)


def _human_ratifier(value: object) -> str:
    ratifier = _required_text(value, "ratifier")
    if ratifier.lower().startswith(("model:", "reviewer:", "assistant:")):
        raise ValueError("human ratifier must not identify a model or reviewer")
    return ratifier


def _attribution_fields(
    *,
    observation: PublishedRecord,
    oracle_revision_id: object,
    oracle_matches: object,
    human_verdict: object,
    defect_origin: object,
    rationale: object,
    dispute_evidence: object,
    ratifier: object,
) -> dict[str, object]:
    if not isinstance(oracle_matches, list) or any(
        not isinstance(match, str) or not match.strip() for match in oracle_matches
    ):
        raise ValueError("oracle_matches must be a list of non-empty strings")
    if not isinstance(dispute_evidence, list) or any(
        not isinstance(item, str) or not item.strip() for item in dispute_evidence
    ):
        raise ValueError("dispute_evidence must be a list of non-empty strings")
    verdict = _required_text(human_verdict, "human_verdict")
    if verdict not in _HUMAN_VERDICTS:
        raise ValueError(f"unsupported human_verdict: {verdict!r}")
    origin = _required_text(defect_origin, "defect_origin")
    if origin not in _DEFECT_ORIGINS:
        raise ValueError(f"unsupported defect_origin: {origin!r}")
    if verdict == "disputed" and not dispute_evidence:
        raise ValueError("disputed attribution requires dispute_evidence")
    return {
        "defect_origin": origin,
        "dispute_evidence": list(dispute_evidence),
        "eligible_for_official_metrics": False,
        "excluded_from_false_alarm_denominator": verdict in {"unknown", "disputed"},
        "governance_status": "unbound",
        "human_verdict": verdict,
        "kind": "attribution_revision",
        "observation_digest": observation.digest,
        "observation_id": observation.record_id,
        "oracle_matches": list(oracle_matches),
        "oracle_revision_id": _required_text(oracle_revision_id, "oracle_revision_id"),
        "ratifier": _human_ratifier(ratifier),
        "rationale": _required_text(rationale, "rationale"),
        "schema_version": 1,
        "status": "ratified",
    }


def ratify_attribution(
    store_root: Path,
    revision_id: str,
    *,
    observation_id: str,
    oracle_revision_id: str,
    oracle_matches: list[str],
    human_verdict: str,
    defect_origin: str,
    rationale: str,
    dispute_evidence: list[str],
    ratifier: str,
) -> PublishedRecord:
    """Freeze a named human judgment separately from model observations."""
    observation = read_record(store_root, observation_id)
    if observation.record.get("kind") != "finding_observation":
        raise ValueError("attribution target must be a finding observation")
    record = _attribution_fields(
        observation=observation,
        oracle_revision_id=oracle_revision_id,
        oracle_matches=oracle_matches,
        human_verdict=human_verdict,
        defect_origin=defect_origin,
        rationale=rationale,
        dispute_evidence=dispute_evidence,
        ratifier=ratifier,
    )
    return publish_record(store_root, revision_id, record)


def ratify_governed_attribution(
    store_root: Path,
    revision_id: str,
    *,
    observation_id: str,
    oracle_revision_id: str,
    oracle_matches: list[str],
    human_verdict: str,
    defect_origin: str,
    rationale: str,
    dispute_evidence: list[str],
    ratifier: str,
    capability: CampaignCapability,
) -> PublishedRecord:
    """Ratify an attribution through the same frozen campaign authority."""
    governance = _ratification_governance(
        store_root,
        capability=capability,
        action="ratify_attribution",
        actor=ratifier,
        target=revision_id,
    )
    if isinstance(governance, PublishedRecord):
        return governance
    authority, independence = governance
    observation = read_record(store_root, observation_id)
    if observation.record.get("kind") != "finding_observation":
        raise ValueError("attribution target must be a finding observation")
    record = _attribution_fields(
        observation=observation,
        oracle_revision_id=oracle_revision_id,
        oracle_matches=oracle_matches,
        human_verdict=human_verdict,
        defect_origin=defect_origin,
        rationale=rationale,
        dispute_evidence=dispute_evidence,
        ratifier=ratifier,
    )
    _bind_governance(record, authority, independence)
    if independence["status"] != "satisfied":
        record["status"] = "disputed"
        record["human_verdict"] = "disputed"
    return publish_record(store_root, revision_id, record)


def _bind_governance(
    record: dict[str, object],
    authority: PublishedRecord,
    independence: Mapping[str, object],
) -> None:
    record.update(
        {
            "authority_revision_digest": authority.digest,
            "authority_revision_id": authority.record_id,
            "authority_trust": {
                "rule": "campaign-bootstrap-digest-v1",
                "trusted_authority_revision_digest": authority.digest,
            },
            "campaign_policy_revision_id": authority.record[
                "campaign_policy_revision_id"
            ],
            "excluded_from_affected_denominators": (
                independence.get("status") != "satisfied"
            ),
            "eligible_for_official_metrics": (
                independence.get("status") == "satisfied"
            ),
            "governance_status": "bound",
            "independence_evidence": dict(independence),
            "role_identities": authority.record["role_identities"],
        }
    )


def correct_attribution(
    store_root: Path,
    parent_revision_id: str,
    *,
    oracle_matches: list[str],
    human_verdict: str,
    defect_origin: str,
    rationale: str,
    dispute_evidence: list[str],
    reason: str,
    ratifier: str,
) -> PublishedRecord:
    """Freeze a reason-bearing attribution child while preserving its parent."""
    parent = read_record(store_root, parent_revision_id)
    if parent.record.get("kind") != "attribution_revision" or parent.record.get(
        "status"
    ) != "ratified":
        raise ValueError("attribution correction parent must be ratified")
    observation_id = _required_text(parent.record.get("observation_id"), "observation_id")
    observation = read_record(store_root, observation_id)
    child = _attribution_fields(
        observation=observation,
        oracle_revision_id=parent.record.get("oracle_revision_id"),
        oracle_matches=oracle_matches,
        human_verdict=human_verdict,
        defect_origin=defect_origin,
        rationale=rationale,
        dispute_evidence=dispute_evidence,
        ratifier=ratifier,
    )
    child["correction_reason"] = _required_text(reason, "reason")
    child["parent_revision_id"] = parent_revision_id
    return append_revision(store_root, parent_revision_id, child)


def append_revision(
    store_root: Path, parent_record_id: str, revision: Mapping[str, object]
) -> PublishedRecord:
    """Publish a digest-named child revision without changing its parent."""
    parent = read_record(store_root, parent_record_id)
    child = dict(revision)
    supplied_parent = child.setdefault("parent_digest", parent.digest)
    if supplied_parent != parent.digest:
        raise ValueError("revision parent_digest does not match its parent record")
    child_id = f"{parent_record_id}--{record_digest(child)}"
    return publish_record(store_root, child_id, child)
