"""Immutable JSON record primitives for the docs-review baseline."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
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
    path = _record_path(Path(store_root), record_id)
    payload = canonical_json_bytes(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{record_id}.{uuid.uuid4().hex}.tmp"
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            existing = path.read_bytes()
            if existing != payload:
                raise RecordConflictError(
                    f"record ID already has different immutable bytes: {record_id}"
                )
    finally:
        temporary.unlink(missing_ok=True)
    return _published(record_id, path, payload)


def read_record(store_root: Path, record_id: str) -> PublishedRecord:
    """Read and validate an existing immutable record."""
    path = _record_path(Path(store_root), record_id)
    try:
        payload = path.read_bytes()
    except FileNotFoundError as error:
        raise ValueError(f"record does not exist: {record_id}") from error
    return _published(record_id, path, payload)


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
