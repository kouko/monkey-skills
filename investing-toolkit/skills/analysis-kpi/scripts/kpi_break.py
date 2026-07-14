#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Break-event detection + human adjudication lifecycle (operational-kpi
capability, slice 6).

The module surface (through Task 2):
- `detect_breaks(prev_summary, curr_summary)` — PURE COMPUTE, no
  persistence. Compares two consecutive-period KPI summaries and returns a
  list of candidate break-events `[{"trigger": ..., "detail": ...}]`:
    * `resegmentation` — the SET of segment names changed (added/removed/
      count-changed) between prev and curr.
    * `relabel` — a kpi_id present in BOTH summaries' `kpi_labels` whose
      label text differs.
    * `arithmetic-mismatch` — a kpi_id in curr's `reconciliation` whose
      `parts` don't sum to `total` within a 1% relative tolerance
      (`math.isclose(rel_tol=0.01)`).
  Identical summaries -> []. A summary with no `reconciliation` key simply
  cannot raise arithmetic-mismatch (N/A, not an error — `.get` throughout).
- `flag_break(company, schema_version, candidate, review_item_id)` persists
  a new FLAGGED break-event record to a per-company durable file (distinct
  `.kpi-breaks.json` suffix, lock-guarded RMW via `_store_fs`, mirroring
  `kpi_schema.propose`) AND enqueues a `subject_type="break-event"`
  review-item via `review_queue.enqueue` (reused seam, not reimplemented).
  `get_break`/`list_breaks` are read-only queries over that store.

Task 3 (confirm_break/dismiss_break, routed through
`review_queue.adjudicate`'s reused human-confirm auth boundary) and Task 4
(CLI) are NOT built in this task.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

# Resolve same-dir modules without a package, so `import _store_fs` /
# `import review_queue` work both under `uv run --script` and under
# importlib test loading (mirrors kpi_schema.py's / kpi_gate.py's own
# same-dir import shim).
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import _store_fs  # noqa: E402
import review_queue  # noqa: E402


def detect_breaks(prev_summary: dict, curr_summary: dict) -> list:
    """Compare two consecutive-period KPI summaries and return candidate
    break-events. Pure compute — no side effects, no store/queue writes.

    Each summary is a dict with:
      - `segments`: a list/set of segment names.
      - `kpi_labels`: a dict kpi_id -> label.
      - `reconciliation` (optional): a dict kpi_id -> {"parts": [...],
        "total": ...}.
    """
    candidates = []

    prev_segments = set(prev_summary.get("segments", []))
    curr_segments = set(curr_summary.get("segments", []))
    if prev_segments != curr_segments:
        candidates.append({
            "trigger": "resegmentation",
            "detail": {
                "prev_segments": sorted(prev_segments),
                "curr_segments": sorted(curr_segments),
            },
        })

    prev_labels = prev_summary.get("kpi_labels", {})
    curr_labels = curr_summary.get("kpi_labels", {})
    for kpi_id, curr_label in curr_labels.items():
        if kpi_id in prev_labels and prev_labels[kpi_id] != curr_label:
            candidates.append({
                "trigger": "relabel",
                "detail": {
                    "kpi_id": kpi_id,
                    "prev_label": prev_labels[kpi_id],
                    "curr_label": curr_label,
                },
            })

    reconciliation = curr_summary.get("reconciliation", {})
    for kpi_id, recon in reconciliation.items():
        parts = recon.get("parts", [])
        total = recon.get("total")
        if total is not None and not math.isclose(sum(parts), total, rel_tol=0.01):
            candidates.append({
                "trigger": "arithmetic-mismatch",
                "detail": {
                    "kpi_id": kpi_id,
                    "parts": parts,
                    "sum_parts": sum(parts),
                    "total": total,
                },
            })

    return candidates


# A record-shape change here is a detectable migration, not a silent misread
# (mirrors kpi_schema.SCHEMA_ENVELOPE_VERSION's rationale).
BREAK_ENVELOPE_VERSION = "1.0"

# Distinct from kpi_schema's ".kpi-schema.json", review_queue's shared
# "review-queue.json", and kpi_store's/kpi_gate's own per-company suffixes —
# each durable store under the same DATA dir owns its own filename so a
# collision can never silently merge two stores' records.
BREAK_FILENAME_SUFFIX = ".kpi-breaks.json"


def _break_path(company: str) -> Path:
    """One file per company, sanitized the same way as kpi_schema's
    `_schema_path` (every char outside `[A-Za-z0-9_-]` -> `_`) so a
    malicious or malformed company name can never escape the store dir via
    `../` or a path separator.
    """
    company_key = _store_fs._UNSAFE_KEY_CHARS.sub("_", str(company)) or "_"
    return _store_fs.resolve_store_dir() / f"{company_key}{BREAK_FILENAME_SUFFIX}"


def _load_break_file(path: Path) -> dict:
    """Read the existing per-company break-event envelope, or return a
    fresh empty one. Mirrors kpi_schema._load_schema_file.
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope.setdefault("breaks", [])
        return envelope
    return {
        "_kpi_break_meta": {"version": BREAK_ENVELOPE_VERSION},
        "breaks": [],
    }


def flag_break(company: str, schema_version: str, candidate: dict, review_item_id: str) -> dict:
    """Persist a new FLAGGED break-event record for `company` and enqueue a
    `subject_type="break-event"` review-item referencing it.

    `candidate` is one of `detect_breaks`'s returned dicts
    (`{"trigger": ..., "detail": ...}`) — `flag_break` interprets nothing
    about its content beyond copying `trigger`/`detail` verbatim into the
    durable record. `break_id` is derived from the count of this company's
    existing break records (`f"{company}:{schema_version}:{n}"`), so it is
    stable and unique per company without a separate counter file.

    The read-modify-write of the per-company break-event file is guarded by
    `_store_fs._acquire_series_lock` (reused, not reimplemented), mirroring
    `kpi_schema.propose`'s locking exactly.

    AFTER the break-event file is durably written, enqueues the review-item
    via `review_queue.enqueue` (reused human-confirm seam, not
    reimplemented) — this is what Task 3's `confirm_break`/`dismiss_break`
    will later adjudicate through.

    Returns the newly-created break-event record.
    """
    path = _break_path(company)
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_break_file(path)
        break_id = f"{company}:{schema_version}:{len(envelope['breaks'])}"
        record = {
            "break_id": break_id,
            "company": company,
            "schema_version": schema_version,
            "trigger": candidate["trigger"],
            "detail": candidate["detail"],
            "status": "FLAGGED",
            "mapping": None,
        }
        envelope["breaks"].append(record)
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)

    review_queue.enqueue({
        "review_item_id": review_item_id,
        "subject_type": "break-event",
        "subject_id": break_id,
        "reason": (
            f"Break-event flagged for {company!r} (schema {schema_version!r}, "
            f"trigger={record['trigger']!r}) pending human adjudication"
        ),
    })

    return record


def get_break(company: str, break_id: str) -> dict | None:
    """Return the break-event record matching `break_id` for `company`, or
    `None` if no such record exists. Read-only, no lock needed (a single
    read of a file that is only ever replaced atomically).
    """
    envelope = _load_break_file(_break_path(company))
    for record in envelope["breaks"]:
        if record["break_id"] == break_id:
            return record
    return None


def list_breaks(company: str) -> list:
    """Return all break-event records for `company` (`[]` if none flagged
    yet — not an error, mirrors `review_queue.list_open`'s missing-file
    convention). Read-only.
    """
    return _load_break_file(_break_path(company))["breaks"]
