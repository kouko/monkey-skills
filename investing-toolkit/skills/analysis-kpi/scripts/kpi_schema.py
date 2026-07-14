#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
KPI schema propose-then-confirm lifecycle (operational-kpi capability, slice 3).

Layer 2 (Analysis) internal persistence — NOT external I/O. A file-per-company
JSON holds every schema VERSION ever proposed for that company (a durable,
versioned envelope under the same DATA dir as `kpi_store.py` / `review_queue.py`),
so a later confirm/amend transitions an existing version in place rather than
overwriting history.

This slice (Task 2) ships the module scaffold + `propose(company, kpi_defs,
review_item_id)`: on a company's first propose it writes version 1,
status "PROPOSED", storing the caller-supplied `kpi_defs` verbatim (the LLM
produces them upstream — NOT this module's job), AND enqueues a
`subject_type="kpi-schema"` review-item via `review_queue.enqueue` so a human
can later confirm it through the review queue's existing human-confirm seam
(reused, not reimplemented — Task 3). No extraction, no confirm, no amend, no
CLI here (Tasks 3-6).

Durable-dir resolution, atomic tmp+rename write, and series locking are ALL
REUSED from the shared `_store_fs.py` module (same-dir import below), NOT
re-implemented and NOT sourced from cache_util: a KPI schema is durable,
human-in-the-loop-gated state that must survive cache eviction, so it roots
under the same DATA dir as the KPI store and review queue.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Resolve same-dir modules without a package, so `import _store_fs` /
# `import review_queue` work both under `uv run --script` and under
# importlib test loading (mirrors kpi_store.py's / review_queue.py's own
# same-dir import shim).
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import _store_fs  # noqa: E402
import review_queue  # noqa: E402

# A record-shape change here is a detectable migration, not a silent misread
# (mirrors kpi_store.STORE_SCHEMA_VERSION / review_queue.QUEUE_SCHEMA_VERSION).
SCHEMA_ENVELOPE_VERSION = "1.0"

SCHEMA_FILENAME_SUFFIX = ".kpi-schema.json"


def _schema_path(company: str) -> Path:
    """One file per company, sanitized the same way as kpi_store's
    `_series_key` (every char outside `[A-Za-z0-9_-]` -> `_`) so a malicious
    or malformed company name can never escape the store dir via `../` or a
    path separator.
    """
    company_key = _store_fs._UNSAFE_KEY_CHARS.sub("_", str(company)) or "_"
    return _store_fs.resolve_store_dir() / f"{company_key}{SCHEMA_FILENAME_SUFFIX}"


def _load_schema_file(path: Path) -> dict:
    """Read the existing per-company schema envelope, or return a fresh
    empty one. `versions` holds every version ever proposed for this
    company, oldest first — never overwritten, only appended/mutated in
    place by confirm/amend (Tasks 3/5).
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope.setdefault("versions", [])
        return envelope
    return {
        "_kpi_schema_meta": {"version": SCHEMA_ENVELOPE_VERSION},
        "versions": [],
    }


def propose(company: str, kpi_defs: list, review_item_id: str) -> dict:
    """Propose a new KPI schema version for `company`.

    On a company's FIRST propose, writes version 1 with status "PROPOSED",
    storing `kpi_defs` (a list of dicts like `{kpi_id, label, unit,
    locate_hint}`, produced upstream by the LLM) verbatim — this module
    interprets nothing about their content. `confirmed_by`/`confirmed_at`
    start `None` (only `confirm`, Task 3, sets them).

    The read-modify-write of the per-company schema file is guarded by
    `_store_fs._acquire_series_lock`, mirroring `kpi_store.append` /
    `review_queue.enqueue`'s locking so a concurrent propose never tears or
    loses an update.

    AFTER the schema file is durably written, enqueues a
    `subject_type="kpi-schema"` review-item (via `review_queue.enqueue`)
    referencing the new schema's `schema_id` as `subject_id`, carrying the
    caller-supplied `review_item_id` — this is what a human will later
    confirm through the review queue's existing human-confirm seam (reused,
    not reimplemented).

    KNOWN LIMITATION (cross-store non-atomic seam): the schema write and the
    review-item enqueue touch two independent JSON files under separate locks,
    so a hard process crash BETWEEN them can leave a durable PROPOSED version
    with no review-item to confirm it. It is not a permanent block — a
    subsequent propose creates a fresh, review-item-backed version (the
    orphaned one lingers as dead weight), and `confirm` (Task 3) targets the
    latest PROPOSED version. True cross-file atomicity needs a transaction log
    (a DB the spec deliberately excludes); a lighter reconciliation — re-enqueue
    for a review-item-less PROPOSED head on retry instead of bumping the
    version — is a documented next-touch, not built this slice.

    Returns the newly-created version record.
    """
    path = _schema_path(company)
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_schema_file(path)
        next_version = len(envelope["versions"]) + 1
        schema_id = f"{company}:v{next_version}"
        record = {
            "schema_id": schema_id,
            "company": company,
            "version": next_version,
            "status": "PROPOSED",
            "kpi_defs": kpi_defs,
            "confirmed_by": None,
            "confirmed_at": None,
        }
        envelope["versions"].append(record)
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)

    review_queue.enqueue({
        "review_item_id": review_item_id,
        "subject_type": "kpi-schema",
        "subject_id": schema_id,
        "reason": (
            f"KPI schema proposed for {company!r} (version {next_version}) "
            "pending human confirmation before extraction can rely on it"
        ),
    })

    return record
