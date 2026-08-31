"""Tests for immutable, content-addressed docs-review baseline records."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
import stat

import pytest

import docs_review_baseline_store as store
from docs_review_baseline_store import (
    RecordConflictError,
    admit_historical_case,
    append_revision,
    canonical_json_bytes,
    correct_oracle,
    publish_record,
    ratify_oracle,
    read_record,
    record_digest,
)


def test_req_99_historical_case_admission(tmp_path) -> None:
    # @req: REQ-99
    """Only explicit snapshot bytes can admit a scoreable replay candidate."""
    snapshot = b"# Historical draft\n\nThe original document bytes.\n"
    candidate = admit_historical_case(
        tmp_path,
        "case-2026-08-27",
        snapshot_bytes=snapshot,
        source_locator="git:abc123:docs/example.md",
        evidence_locators=["review:2026-08-27#finding-4"],
    )

    assert candidate.record == {
        "case_id": "case-2026-08-27",
        "evidence_locators": ["review:2026-08-27#finding-4"],
        "kind": "historical_case",
        "schema_version": 1,
        "snapshot": {
            "bytes_base64": "IyBIaXN0b3JpY2FsIGRyYWZ0CgpUaGUgb3JpZ2luYWwgZG9jdW1lbnQgYnl0ZXMuCg==",
            "digest": "2c30de42ffe3d2b9ecd4b8d0e87c2e88f7b837fd0f5429365b2e5aff5a09b29d",
        },
        "source_locator": "git:abc123:docs/example.md",
        "status": "candidate",
    }
    assert candidate.digest == record_digest(candidate.record)
    assert read_record(tmp_path, candidate.record_id) == candidate

    unscoreable = admit_historical_case(
        tmp_path,
        "case-narrative-only",
        snapshot_bytes=None,
        source_locator="issue:2026-08-27-incident",
        evidence_locators=["issue:2026-08-27-incident#description"],
    )

    assert unscoreable.record == {
        "case_id": "case-narrative-only",
        "evidence_locators": ["issue:2026-08-27-incident#description"],
        "kind": "historical_case",
        "missing_replay_evidence": ["snapshot_bytes"],
        "schema_version": 1,
        "source_locator": "issue:2026-08-27-incident",
        "status": "unscoreable",
    }
    assert "snapshot" not in unscoreable.record


def test_req_100_oracle_ratification_is_immutable(tmp_path) -> None:
    # @req: REQ-100
    """Ratification freezes a named oracle; corrections form reasoned children."""
    oracle = ratify_oracle(
        tmp_path,
        "oracle-case-1-r1",
        case_id="case-1",
        snapshot_digest="a" * 64,
        findings=[
            {
                "finding_id": "missing-risk",
                "expectation": "The review names the unbounded migration risk.",
                "rationale": "The rollout has no limiting condition.",
                "evidence_locator": "git:abc123:docs/strategy.md#rollout",
            }
        ],
        negative_control_intent="Do not reward generic requests for more detail.",
        ratifier="maintainer:kuku",
    )
    frozen_bytes = oracle.path.read_bytes()

    assert oracle.record["ratifier"] == "maintainer:kuku"
    assert oracle.record["negative_control_intent"] == (
        "Do not reward generic requests for more detail."
    )
    assert oracle.digest == record_digest(oracle.record)
    with pytest.raises(RecordConflictError):
        ratify_oracle(
            tmp_path,
            "oracle-case-1-r1",
            case_id="case-1",
            snapshot_digest="a" * 64,
            findings=[
                {
                    "finding_id": "missing-risk",
                    "expectation": "Changed in place.",
                    "rationale": "This remains structurally complete.",
                    "evidence_locator": "git:abc123:docs/strategy.md#rollout",
                }
            ],
            negative_control_intent="Changed in place.",
            ratifier="maintainer:kuku",
        )

    correction = correct_oracle(
        tmp_path,
        oracle.record_id,
        findings=[
            {
                "finding_id": "missing-risk",
                "expectation": "The review names the bounded migration risk.",
                "rationale": "The rollout is limited to one cohort.",
                "evidence_locator": "git:def456:docs/strategy.md#rollout",
            }
        ],
        negative_control_intent="Do not reward generic requests for more detail.",
        reason="The original snapshot interpretation ignored the cohort limit.",
        ratifier="maintainer:kuku",
    )

    assert correction.record["parent_revision_id"] == oracle.record_id
    assert correction.record["parent_digest"] == oracle.digest
    assert correction.record["correction_reason"]
    assert correction.digest != oracle.digest
    assert correction.record_id != oracle.record_id
    assert oracle.path.read_bytes() == frozen_bytes
    assert read_record(tmp_path, oracle.record_id) == oracle

    with pytest.raises(ValueError, match="reason"):
        correct_oracle(
            tmp_path,
            oracle.record_id,
            findings=correction.record["findings"],
            negative_control_intent=correction.record["negative_control_intent"],
            reason="",
            ratifier="maintainer:kuku",
        )


def test_canonical_record_publish_is_atomic_and_content_addressed(tmp_path) -> None:
    """A record ID chooses one canonical payload without rewriting history."""
    first = {"kind": "oracle", "labels": ["a"], "version": 1}
    equivalent = {"version": 1, "labels": ["a"], "kind": "oracle"}
    conflicting = {"kind": "oracle", "labels": ["b"], "version": 1}

    assert canonical_json_bytes(first) == canonical_json_bytes(equivalent)
    assert record_digest(first) == record_digest(equivalent)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(publish_record, tmp_path, "oracle-1", record)
            for record in (first, conflicting)
        ]
    results = [future.exception() or future.result() for future in futures]
    published = [result for result in results if not isinstance(result, Exception)]
    conflicts = [result for result in results if isinstance(result, RecordConflictError)]

    assert len(published) == 1
    assert len(conflicts) == 1
    winner = published[0]
    assert winner.digest in {record_digest(first), record_digest(conflicting)}
    assert publish_record(tmp_path, "oracle-1", winner.record) == winner
    with pytest.raises(RecordConflictError):
        publish_record(tmp_path, "oracle-1", conflicting if winner.record == first else first)

    revision = append_revision(tmp_path, "oracle-1", {"status": "corrected"})
    assert revision.record["parent_digest"] == winner.digest
    assert revision.record_id != winner.record_id


def test_publish_refuses_symlinked_store_root(tmp_path) -> None:
    """A caller cannot redirect publication by replacing the store root."""
    actual_store = tmp_path / "actual-store"
    actual_store.mkdir()
    store_alias = tmp_path / "store-alias"
    store_alias.symlink_to(actual_store, target_is_directory=True)

    with pytest.raises(OSError):
        publish_record(store_alias, "oracle-1", {"kind": "oracle"})

    assert not (actual_store / "records").exists()


def test_publish_refuses_symlinked_records_directory(tmp_path) -> None:
    """The records component cannot redirect a descriptor-anchored write."""
    outside = tmp_path / "outside"
    outside.mkdir()
    store_root = tmp_path / "store"
    store_root.mkdir()
    (store_root / "records").symlink_to(outside, target_is_directory=True)

    with pytest.raises(OSError):
        publish_record(store_root, "oracle-1", {"kind": "oracle"})

    assert list(outside.iterdir()) == []


def test_record_operations_refuse_final_symlink(tmp_path) -> None:
    """Neither idempotent publish nor read may follow a substituted record."""
    records = tmp_path / "records"
    records.mkdir()
    payload = canonical_json_bytes({"kind": "oracle"})
    outside = tmp_path / "outside.json"
    outside.write_bytes(payload)
    (records / "oracle-1.json").symlink_to(outside)

    with pytest.raises(OSError):
        read_record(tmp_path, "oracle-1")
    with pytest.raises(OSError):
        publish_record(tmp_path, "oracle-1", {"kind": "oracle"})

    assert outside.read_bytes() == payload


def test_record_operations_refuse_non_regular_existing_record(tmp_path) -> None:
    """A directory at a record name is invalid evidence, not a record."""
    record_path = tmp_path / "records" / "oracle-1.json"
    record_path.mkdir(parents=True)

    with pytest.raises(ValueError, match="not a regular file"):
        read_record(tmp_path, "oracle-1")
    with pytest.raises(ValueError, match="not a regular file"):
        publish_record(tmp_path, "oracle-1", {"kind": "oracle"})


def test_publish_fsyncs_directory_after_link_and_unlink(tmp_path, monkeypatch) -> None:
    """Each publication metadata change is followed by a directory sync."""
    (tmp_path / "records").mkdir()
    events: list[str] = []
    real_fsync = os.fsync
    real_link = os.link
    real_unlink = os.unlink

    def recording_fsync(fd: int) -> None:
        events.append("dir-fsync" if stat.S_ISDIR(os.fstat(fd).st_mode) else "file-fsync")
        real_fsync(fd)

    def recording_link(*args, **kwargs) -> None:
        events.append("link")
        real_link(*args, **kwargs)

    def recording_unlink(*args, **kwargs) -> None:
        events.append("unlink")
        real_unlink(*args, **kwargs)

    monkeypatch.setattr(store.os, "fsync", recording_fsync)
    monkeypatch.setattr(store.os, "link", recording_link)
    monkeypatch.setattr(store.os, "unlink", recording_unlink)

    publish_record(tmp_path, "oracle-1", {"kind": "oracle"})

    assert events == ["file-fsync", "link", "dir-fsync", "unlink", "dir-fsync"]


def test_publish_fails_loud_when_directory_fsync_fails(tmp_path, monkeypatch) -> None:
    """A record is not reported durable when directory durability is absent."""
    real_fsync = os.fsync

    def unavailable_for_directories(fd: int) -> None:
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError("directory fsync unavailable")
        real_fsync(fd)

    monkeypatch.setattr(store.os, "fsync", unavailable_for_directories)

    with pytest.raises(OSError, match="directory fsync unavailable"):
        publish_record(tmp_path, "oracle-1", {"kind": "oracle"})


def test_append_revision_preserves_parent_bytes_and_value(tmp_path) -> None:
    """A child revision cannot mutate the parent bytes or decoded value."""
    parent = publish_record(tmp_path, "oracle-1", {"kind": "oracle", "version": 1})
    parent_bytes = parent.path.read_bytes()
    parent_value = read_record(tmp_path, parent.record_id)

    append_revision(tmp_path, parent.record_id, {"status": "corrected"})

    assert parent.path.read_bytes() == parent_bytes
    assert read_record(tmp_path, parent.record_id) == parent_value
