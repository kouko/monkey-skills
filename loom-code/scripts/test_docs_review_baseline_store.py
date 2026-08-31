"""Tests for immutable, content-addressed docs-review baseline records."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from docs_review_baseline_store import (
    RecordConflictError,
    append_revision,
    canonical_json_bytes,
    publish_record,
    record_digest,
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
