#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
KPI reliability gate — ground-truth label set + accuracy-based trust
verdict (operational-kpi capability, slice 5).

Layer 2 (Analysis) internal persistence — NOT external I/O. A file-per-
company JSON holds every human-labeled ground-truth entry ever added for
that company (a durable, versioned envelope under the same DATA dir as
`kpi_store.py` / `review_queue.py` / `kpi_schema.py`), so extraction
accuracy can later be evaluated against it and a TRUSTED/WITHHELD/
NOT_EVALUATED verdict recorded per (company, schema_version).

Task 1 shipped the ground-truth label-set store:
- `add_labels(company, labels)` APPENDS human-labeled entries (each a dict
  like `{kpi_id, period, value}`) to the company's label-set file — never
  overwrites prior labels, since the gate's accuracy computation depends
  on the FULL accumulated sample, not just the latest batch.
- `get_labels(company)` reads them back (`[]` if the company has none yet
  — "no labels" is a normal starting state, not an error, mirroring
  `kpi_schema._load_schema_file`'s missing-file convention).

Task 2 adds `evaluate(company, schema_version, extracted_values,
threshold=None, min_samples=5, evaluated_at=None)`: matches every labeled
`(kpi_id, period)` cell against the caller-supplied `extracted_values`,
computes cell-level accuracy, and persists a fail-closed gate record keyed
by `(company, schema_version)`.

`gate_verdict` / `is_trusted` / the CLI are NOT part of this task
(Tasks 3-4).

Durable-dir resolution, atomic tmp+rename write, and series locking are
ALL REUSED from the shared `_store_fs.py` module (same-dir import below),
NOT re-implemented and NOT sourced from cache_util: ground-truth labels
are durable, human-provided state that must survive cache eviction, so
they root under the same DATA dir as the KPI store, review queue, and
schema lifecycle.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

# Resolve same-dir modules without a package, so `import _store_fs` works
# both under `uv run --script` and under importlib test loading (mirrors
# kpi_store.py's / kpi_schema.py's own same-dir import shim).
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import _store_fs  # noqa: E402

# A record-shape change here is a detectable migration, not a silent misread
# (mirrors kpi_store.STORE_SCHEMA_VERSION / kpi_schema.SCHEMA_ENVELOPE_VERSION).
GATE_ENVELOPE_VERSION = "1.0"

# `.kpi-labels.json` — deliberately distinct from kpi_store's, review_queue's,
# and kpi_schema's own per-company filename suffixes so all four stores can
# coexist under the same DATA dir without colliding on one company's file.
LABELS_FILENAME_SUFFIX = ".kpi-labels.json"

# Gate records are a SEPARATE per-company file from the label set: labels
# accumulate independent of schema_version, while a gate record is scoped to
# one (company, schema_version) pair and gets overwritten on re-evaluation
# (a recast series is itself gated — Task 2's evaluate re-run replaces the
# prior record for that schema_version, it does not append history).
GATE_RECORDS_FILENAME_SUFFIX = ".kpi-gate-records.json"

# Verdicts are fail-closed: TRUSTED requires BOTH sample_size >= min_samples
# AND a calibrated threshold that accuracy meets/exceeds. Anything else
# (no labels, too few samples, or threshold unset/deferred) is
# NOT_EVALUATED; below-threshold-with-enough-samples is WITHHELD.
VERDICT_NOT_EVALUATED = "NOT_EVALUATED"
VERDICT_TRUSTED = "TRUSTED"
VERDICT_WITHHELD = "WITHHELD"


def _labels_path(company: str) -> Path:
    """One file per company, sanitized the same way as kpi_store's /
    kpi_schema's `_schema_path` (every char outside `[A-Za-z0-9_-]` -> `_`)
    so a malicious or malformed company name can never escape the store
    dir via `../` or a path separator.
    """
    company_key = _store_fs._UNSAFE_KEY_CHARS.sub("_", str(company)) or "_"
    return _store_fs.resolve_store_dir() / f"{company_key}{LABELS_FILENAME_SUFFIX}"


def _load_labels_file(path: Path) -> dict:
    """Read the existing per-company label-set envelope, or return a fresh
    empty one. `labels` holds every ground-truth entry ever added for this
    company — never overwritten, only appended to.
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope.setdefault("labels", [])
        return envelope
    return {
        "_kpi_gate_meta": {"version": GATE_ENVELOPE_VERSION},
        "labels": [],
    }


def add_labels(company: str, labels: list) -> None:
    """Append human-labeled ground-truth entries (each a dict like
    `{kpi_id, period, value}`) to `company`'s label-set file.

    APPEND-ONLY: a second call adds to the existing labels rather than
    replacing them, so accuracy evaluation (Task 2) always sees the full
    accumulated ground-truth sample.

    The read-modify-write of the per-company label-set file is guarded by
    `_store_fs._acquire_series_lock`, mirroring `kpi_schema.propose`'s /
    `kpi_store.append`'s locking so a concurrent add_labels call never
    tears or loses an update.
    """
    path = _labels_path(company)
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_labels_file(path)
        envelope["labels"].extend(labels)
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)


def get_labels(company: str) -> list:
    """The full accumulated list of ground-truth labels for `company`, or
    `[]` if none have been added yet. Read-only, no lock needed (a single
    read of a file that is only ever replaced atomically).
    """
    return _load_labels_file(_labels_path(company))["labels"]


def _gate_records_path(company: str) -> Path:
    """One gate-records file per company, sanitized identically to
    `_labels_path` — a distinct filename suffix so it never collides with
    that company's label-set file.
    """
    company_key = _store_fs._UNSAFE_KEY_CHARS.sub("_", str(company)) or "_"
    return _store_fs.resolve_store_dir() / f"{company_key}{GATE_RECORDS_FILENAME_SUFFIX}"


def _load_gate_records_file(path: Path) -> dict:
    """Read the existing per-company gate-records envelope, or return a
    fresh empty one. `records` maps `schema_version` (stringified) -> the
    latest gate record for that (company, schema_version) pair.
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope.setdefault("records", {})
        return envelope
    return {
        "_kpi_gate_records_meta": {"version": GATE_ENVELOPE_VERSION},
        "records": {},
    }


def _extracted_lookup(extracted_values) -> dict:
    """Normalize `extracted_values` into a `{(kpi_id, period): value}`
    lookup. Accepts either shape so a caller can pass whichever is more
    convenient for its own data:
      - a list of dicts shaped like labels: `{kpi_id, period, value}`
      - a mapping of `kpi_id -> {period: value}`
    """
    lookup = {}
    if isinstance(extracted_values, dict):
        for kpi_id, periods in extracted_values.items():
            for period, value in periods.items():
                lookup[(kpi_id, period)] = value
    else:
        for entry in extracted_values:
            lookup[(entry["kpi_id"], entry["period"])] = entry["value"]
    return lookup


def _cell_correct(label_value, extracted_value) -> bool:
    """A labeled cell is CORRECT if the extracted value matches the label:
    exact equality for int/str, or a small relative tolerance
    (`math.isclose(rel_tol=0.01)`) for floats — extraction of a floating
    figure can legitimately differ in the last digit without being wrong.
    """
    if isinstance(label_value, float) or isinstance(extracted_value, float):
        try:
            return math.isclose(float(label_value), float(extracted_value), rel_tol=0.01)
        except (TypeError, ValueError):
            return False
    return label_value == extracted_value


def evaluate(
    company: str,
    schema_version,
    extracted_values,
    threshold: float | None = None,
    min_samples: int = 5,
    evaluated_at=None,
) -> dict:
    """Evaluate extraction accuracy for `company`'s CONFIRMED schema
    version `schema_version` against its accumulated ground-truth label
    set, and persist a fail-closed gate record.

    Cell-level accuracy = correct_cells / total_labeled_cells, matching
    each label's `(kpi_id, period)` to `extracted_values` via
    `_extracted_lookup` and `_cell_correct`. A label with no matching
    entry in `extracted_values` counts as incorrect (not skipped) — a
    missing extraction is a real gap, not a free pass.

    VERDICT is fail-closed:
      - no labels at all, or `min_samples < 1` (a non-positive sample
        floor), or `sample_size < min_samples` -> NOT_EVALUATED (never a
        verdict from zero ground truth or too few samples — TRUSTED must
        never be reachable without at least one real labeled cell AND a
        positive sample floor, even if a caller passes `min_samples=0`
        together with `threshold=0.0`).
      - `sample_size >= min_samples` and `threshold is None` (deferred
        calibration) -> NOT_EVALUATED: the metric is measured and
        recorded, but with no calibrated bar to compare against the gate
        cannot certify TRUSTED.
      - `sample_size >= min_samples` and `accuracy >= threshold`
        (INCLUSIVE) -> TRUSTED.
      - `sample_size >= min_samples` and `accuracy < threshold` ->
        WITHHELD.

    `evaluated_at` is caller-supplied — this module never reads the wall
    clock, mirroring `kpi_schema.confirm`'s `adjudicated_at` convention.

    Persists the record keyed by `(company, schema_version)` via a
    lock-guarded read-modify-write on the company's gate-records file
    (`_store_fs._acquire_series_lock`, mirroring `add_labels`) — a
    re-evaluation of the same schema_version replaces its prior record
    (a recast series is itself gated: only the latest evaluation counts).

    Returns the gate record.
    """
    labels = get_labels(company)
    lookup = _extracted_lookup(extracted_values)

    sample_size = len(labels)
    correct = sum(
        1
        for label in labels
        if (label["kpi_id"], label["period"]) in lookup
        and _cell_correct(label["value"], lookup[(label["kpi_id"], label["period"])])
    )
    accuracy = correct / sample_size if sample_size else 0.0

    if not labels or min_samples < 1 or sample_size < min_samples:
        # Never TRUSTED without real ground truth or a positive sample
        # floor — a `min_samples <= 0` caller value must not let a
        # zero-sample evaluation fall through to the accuracy/threshold
        # comparison below (`0/0` accuracy guarded to 0.0 would otherwise
        # satisfy a `threshold=0.0` comparison and fabricate TRUSTED).
        verdict = VERDICT_NOT_EVALUATED
    elif threshold is None:
        verdict = VERDICT_NOT_EVALUATED
    elif accuracy >= threshold:
        verdict = VERDICT_TRUSTED
    else:
        verdict = VERDICT_WITHHELD

    record = {
        "company": company,
        "schema_version": schema_version,
        "metric": accuracy,
        "sample_size": sample_size,
        "verdict": verdict,
        "evaluated_at": evaluated_at,
    }

    path = _gate_records_path(company)
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_gate_records_file(path)
        envelope["records"][str(schema_version)] = record
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)

    return record
