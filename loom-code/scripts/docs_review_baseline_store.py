"""Immutable JSON record primitives for the docs-review baseline."""
from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid
from typing import Any, Mapping


_RECORD_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class RecordConflictError(ValueError):
    """A record ID already belongs to different immutable bytes."""


@dataclass(frozen=True)
class PublishedRecord:
    """The immutable identity and decoded value of a published record."""

    record_id: str
    digest: str
    record: dict[str, Any]
    path: Path


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
    return publish_record(store_root, case_id, record)


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


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
        "findings": _validated_findings(findings),
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
    store_root: Path, bindings: list[tuple[str, str, str]]
) -> PublishedRecord:
    """Freeze an exact ordered corpus and return its digest-bound revision."""
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
                "oracle_revision_id": oracle_revision_id,
                "snapshot_digest": snapshot_digest,
            }
        )
    record: dict[str, object] = {
        "bindings": manifest_bindings,
        "kind": "corpus_manifest",
        "schema_version": 1,
    }
    return publish_record(store_root, f"corpus-{record_digest(record)}", record)


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
