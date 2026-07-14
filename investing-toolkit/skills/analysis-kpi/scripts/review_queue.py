#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Review-item queue + human-confirm seam (operational-kpi capability, slice 2).

Layer 2 (Analysis) internal persistence — NOT external I/O. A single durable
append-only queue file (`review-queue.json`) under the store root holds the
review items that need human adjudication before a flagged KPI point is
trusted. The queue file is the single source of pending work: enqueue appends
an OPEN item; later slices list the OPEN items, adjudicate them (carrying an
immutable append-only adjudicator identity), and reopen resolved items.

This slice ships the scaffold + `enqueue(item)` only (plan
docs/loom/plans/2026-07-14-operational-kpi-review-queue.md, Task 1);
list_open / adjudicate / reopen / the confirm-seam authorization boundary /
the CLI are later tasks.

Durable-dir resolution is REUSED from slice-1 `kpi_store.resolve_store_dir`
(same-skill import below), NOT re-implemented and NOT sourced from cache_util:
a review queue is durable, human-in-the-loop state that must survive cache
eviction, so it roots under the same DATA dir as the KPI store. The small
atomic tmp+rename write mirrors kpi_store._atomic_write's pattern; per
docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md the shared
extract is deferred until a THIRD durable store appears — import, do not copy
the dir-resolution; mirror the tiny write helper locally.

A review-item's `created_at` is a RUNTIME event (caller-supplied) and is
preserved verbatim — it is NOT held to slice-1's accession-derived `as_of`
guard.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Resolve same-dir modules without a package, so `import kpi_store` works both
# under `uv run --script` and under importlib test loading (mirrors
# analysis-comps/scripts/comps_compute.py's sector_classifier import shim).
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import kpi_store  # noqa: E402

# A record-shape change here is a detectable migration, not a silent misread
# (mirrors kpi_store.STORE_SCHEMA_VERSION's rationale).
QUEUE_SCHEMA_VERSION = "1.0"

QUEUE_FILENAME = "review-queue.json"


def _queue_path() -> Path:
    """The single durable queue file under the reused slice-1 store root."""
    return kpi_store.resolve_store_dir() / QUEUE_FILENAME


def _load_queue(path: Path) -> dict:
    """Read the existing queue envelope, or return a fresh empty one.

    Append-only: an existing file's `items` list is preserved and never
    overwritten. A fresh queue starts with a versioned `_review_queue_meta`
    envelope and an empty `items` list.
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope.setdefault("items", [])
        return envelope
    return {
        "_review_queue_meta": {"version": QUEUE_SCHEMA_VERSION},
        "items": [],
    }


def _atomic_write(path: Path, envelope: dict) -> None:
    """Write the queue envelope atomically (tmp + rename), mirroring
    kpi_store._atomic_write's pattern.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=str(path.parent),
        prefix=f".{path.name}.", suffix=".tmp", delete=False,
    ) as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2)
        tmp = Path(f.name)
    tmp.rename(path)


def enqueue(item: dict) -> None:
    """Append one review-item to the durable append-only queue file.

    An item is a dict `{review_item_id, subject_type, subject_id, reason}`.
    `status` DEFAULTS to `"OPEN"` if absent (a freshly enqueued item is
    pending work); a caller-supplied `created_at` is preserved verbatim (a
    review-item's created_at is a runtime event — NOT slice-1's
    accession-derived as_of). The item is otherwise stored unchanged so a
    later list/adjudicate reads back exactly what was queued.

    Concurrency: unlike kpi_store's file-per-series layout, EVERY enqueue
    targets the SAME single shared queue file, so an unlocked
    load->append->write cycle would lose concurrent writers' items (atomic
    tmp+rename prevents a torn file, not a lost update). The full
    read-modify-write cycle is guarded by kpi_store's existing per-path
    `fcntl.flock` lock (reused, not reimplemented — same-skill import),
    mirroring kpi_store.append's try/finally structure exactly.
    """
    stored = dict(item)
    stored.setdefault("status", "OPEN")

    path = _queue_path()
    lock_file = kpi_store._acquire_series_lock(path)
    try:
        envelope = _load_queue(path)
        envelope["items"].append(stored)
        _atomic_write(path, envelope)
    finally:
        kpi_store._release_series_lock(lock_file)
