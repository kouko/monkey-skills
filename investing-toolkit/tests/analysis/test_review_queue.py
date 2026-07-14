"""Tests for analysis-kpi/scripts/review_queue.py — the review-item queue
+ human-confirm seam (operational-kpi capability, slice 2).

This slice's Task 1 ships the module scaffold + `enqueue(item)`: appending a
review-item to a durable append-only queue file (a single `review-queue.json`
under the store root) under a versioned envelope, reusing slice-1
`kpi_store.resolve_store_dir` for the durable dir. The store dir is redirected
to a tmp path via the `KPI_STORE_DIR` env override.

The library functions are exercised by loading `review_queue.py` via importlib
(same convention as test_kpi_store.py's `kpi_store_module` fixture).

No `@req` tags: this dispatch's plan/spec trace work by named change-folder
Requirements (operational-kpi / "Review-item queue lifecycle and human-confirm
seam"), NOT by registered loom-spec REQ-ids — so `@req` is omitted per the
implementer contract (mirrors the sibling data/test_sec_narrative.py rationale).
"""
from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import sys
import threading
import time

from conftest import REVIEW_QUEUE_SCRIPT

import pytest


@pytest.fixture(scope="module")
def review_queue_module():
    """Load review_queue.py as an importable module for unit tests of its
    library surface (enqueue/...) before a CLI wraps it (Task 7).
    """
    spec = importlib.util.spec_from_file_location(
        "review_queue_test", REVIEW_QUEUE_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["review_queue_test"] = module
    spec.loader.exec_module(module)
    return module


def test_enqueue_creates_queue_file_with_open_item(
    review_queue_module, tmp_path, monkeypatch
):
    """Enqueuing one review-item (queue dir redirected to a tmp path via
    KPI_STORE_DIR) creates a durable queue file whose JSON holds the item in
    its `items` list, defaulting `status=="OPEN"`, round-tripped.

    Why default-OPEN + round-trip matters: the queue file is the single source
    of pending work — a freshly enqueued item must be pending (OPEN) so a later
    list_open (Task 2) surfaces it, and every caller-supplied field must persist
    verbatim (incl. a runtime-event `created_at`) so an adjudicator sees exactly
    what was queued.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    item = {
        "review_item_id": "rev-0001",
        "subject_type": "kpi_point",
        "subject_id": "AAPL:iphone_units:FY2024",
        "reason": "value deviates >20% from prior as_of",
        "created_at": "2026-07-14T09:00:00Z",
    }

    review_queue_module.enqueue(item)

    queue_files = list(tmp_path.rglob("*.json"))
    assert len(queue_files) == 1, (
        f"expected exactly one queue file, found {queue_files}"
    )

    envelope = json.loads(queue_files[0].read_text(encoding="utf-8"))
    assert isinstance(envelope.get("items"), list)
    assert len(envelope["items"]) == 1

    stored = envelope["items"][0]
    assert stored["status"] == "OPEN", (
        "a freshly enqueued item must default to status OPEN"
    )
    # created_at preserved verbatim (runtime event — NOT held to slice-1's
    # accession-derived as_of rule).
    assert stored["created_at"] == "2026-07-14T09:00:00Z"
    # Every caller-supplied field round-trips unchanged.
    for key, value in item.items():
        assert stored[key] == value


def test_enqueue_appends_never_drops_existing(
    review_queue_module, tmp_path, monkeypatch
):
    """Enqueuing two DISTINCT items sequentially must leave BOTH in `items`
    — exercises `_load_queue`'s existing-file branch (the first call creates
    the file; the second must read it back and append, not overwrite it).
    This is the append-only invariant the queue's single-source-of-pending-
    work guarantee depends on.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    first = {
        "review_item_id": "rev-0001",
        "subject_type": "kpi_point",
        "subject_id": "AAPL:iphone_units:FY2024",
        "reason": "value deviates >20% from prior as_of",
        "created_at": "2026-07-14T09:00:00Z",
    }
    second = {
        "review_item_id": "rev-0002",
        "subject_type": "kpi_point",
        "subject_id": "AAPL:services_revenue:FY2024",
        "reason": "provenance table_id changed since last as_of",
        "created_at": "2026-07-14T09:05:00Z",
    }

    review_queue_module.enqueue(first)
    review_queue_module.enqueue(second)

    queue_files = list(tmp_path.rglob("*.json"))
    assert len(queue_files) == 1, (
        f"expected exactly one queue file, found {queue_files}"
    )

    envelope = json.loads(queue_files[0].read_text(encoding="utf-8"))
    ids = [item["review_item_id"] for item in envelope["items"]]
    assert ids == ["rev-0001", "rev-0002"], (
        "the second enqueue must not drop the first item — got "
        f"{ids!r}"
    )


def test_concurrent_enqueues_all_persist(
    review_queue_module, tmp_path, monkeypatch
):
    """Multiple concurrent enqueues to the SAME shared queue file must ALL
    persist — no lost update from the unlocked read-modify-write race in
    `enqueue()` (load queue -> append -> atomic write). A
    `threading.Barrier` forces every writer to enter `enqueue()` at
    (approximately) the same instant; `_load_queue` is monkeypatched with a
    deliberate sleep AFTER the read to widen the load->write race window,
    mirroring test_kpi_store.py::test_concurrent_appends_both_persist — this
    is what makes the test a real exercise of the lock rather than a
    serialized-by-luck pass.

    Regression for the lost-update bug (review finding 1): without a lock
    spanning the FULL read-modify-write cycle, two concurrent enqueues can
    both read the same (empty-of-each-other's-item) queue, each append
    their own item in memory, and the second `_atomic_write`'s rename
    clobbers the first — silently dropping a review item (a flagged KPI
    that never reaches a human adjudicator). With the lock, only one writer
    holds the queue at a time, so every item survives.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    original_load_queue = review_queue_module._load_queue

    def slow_load_queue(path):
        envelope = original_load_queue(path)
        time.sleep(0.05)  # widen the race window between read and write
        return envelope

    monkeypatch.setattr(review_queue_module, "_load_queue", slow_load_queue)

    n_writers = 6
    barrier = threading.Barrier(n_writers)

    def make_item(i):
        return {
            "review_item_id": f"rev-{i:04d}",
            "subject_type": "kpi_point",
            "subject_id": f"AAPL:concurrent_kpi:FY2024:{i}",
            "reason": "value deviates >20% from prior as_of",
            "created_at": f"2026-07-14T09:{i:02d}:00Z",
        }

    def writer(i):
        barrier.wait()  # force all writers to hit enqueue() simultaneously
        review_queue_module.enqueue(make_item(i))

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_writers) as executor:
        futures = [executor.submit(writer, i) for i in range(n_writers)]
        for f in futures:
            f.result()

    queue_files = list(tmp_path.rglob("*.json"))
    assert len(queue_files) == 1, (
        f"expected exactly one queue file, found {queue_files}"
    )
    envelope = json.loads(queue_files[0].read_text(encoding="utf-8"))
    ids = sorted(item["review_item_id"] for item in envelope["items"])
    expected = sorted(f"rev-{i:04d}" for i in range(n_writers))
    assert ids == expected, (
        f"expected all {n_writers} concurrent enqueues to persist, found "
        f"{len(envelope['items'])} — lost update from an unlocked "
        f"read-modify-write race"
    )
