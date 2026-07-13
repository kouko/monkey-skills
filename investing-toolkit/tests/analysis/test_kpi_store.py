"""Tests for analysis-kpi/scripts/kpi_store.py — the append-only bitemporal
KPI store (operational-kpi capability, slice 1).

Task 1 (plan: docs/loom/plans/2026-07-14-operational-kpi-bitemporal-store.md)
ships the skill scaffold + `append(point)` writing ONE fully-provenanced
point to a versioned file-per-series JSON under a durable DATA dir. The
store dir is redirected to a tmp path via the `KPI_STORE_DIR` env override.

`kpi_store.py` is loaded directly via importlib (same convention as
tests/analysis/test_analysis_xval.py's `xval_module` fixture) — its functions
are a library surface, not (yet) a subprocess CLI (the CLI lands in Task 8).
"""
from __future__ import annotations

import importlib.util
import json
import sys

from conftest import KPI_STORE_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_store_module():
    """Load kpi_store.py as an importable module for unit tests of its
    library surface (append/query) before a CLI wraps it (Task 8).
    """
    spec = importlib.util.spec_from_file_location("kpi_store_test", KPI_STORE_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_store_test"] = module
    spec.loader.exec_module(module)
    return module


def test_append_creates_versioned_series_file_with_point(
    kpi_store_module, tmp_path, monkeypatch
):
    """Appending one valid, fully-provenanced point (store dir redirected to
    a tmp path via KPI_STORE_DIR) creates exactly ONE series file whose JSON
    carries `_kpi_store_meta.version` and a `points` list containing that
    point, round-tripping unchanged.

    Why round-trip-unchanged matters: this slice persists the point verbatim
    (incl. optional lineage/restates), interpreting nothing — a downstream
    point-in-time query (later slice) must read back exactly what was stored,
    so the store must not mutate, reshape, or drop any field on write.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    point = {
        "company": "AAPL",
        "kpi_id": "iphone_units",
        "period": "FY2024",
        "as_of": "2024-11-01",
        "value": 231000000,
        "source_accession": "0000320193-24-000123",
        "source_table_id": "ex99-1-operating-summary",
        "source_cell_ref": "r5c2",
        # Optional fields: persisted verbatim, NOT interpreted this slice.
        "lineage": {"kind": "as-reported"},
        "restates": None,
    }

    kpi_store_module.append(point)

    series_files = list(tmp_path.rglob("*.json"))
    assert len(series_files) == 1, (
        f"expected exactly one series file, found {series_files}"
    )

    envelope = json.loads(series_files[0].read_text(encoding="utf-8"))
    assert "_kpi_store_meta" in envelope
    assert envelope["_kpi_store_meta"].get("version"), (
        "series envelope must carry a versioned _kpi_store_meta.version"
    )

    assert isinstance(envelope.get("points"), list)
    assert len(envelope["points"]) == 1
    # Round-trips unchanged: the stored point equals the input verbatim.
    assert envelope["points"][0] == point


def test_distinct_series_never_share_a_file(kpi_store_module, tmp_path, monkeypatch):
    """Two logically-distinct series whose sanitized prefixes COLLIDE must
    still land in separate files — the file-per-series invariant this store
    is named for must hold for arbitrary input, not just clean input.

    Regression for the sanitizer-collision hole: `_` is an allowed key char,
    so (company="AAPL_", kpi_id="X") and (company="AAPL", kpi_id="_X") both
    sanitize to the same `AAPL___X` prefix. Without the raw-pair digest they
    would intermingle their points in ONE file; distinct points below must
    yield TWO files, each with exactly its own point.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    prov = {
        "source_accession": "0000000000-00-000000",
        "source_table_id": "t0",
        "source_cell_ref": "r1c1",
    }
    point_a = {"company": "AAPL_", "kpi_id": "X", "period": "FY2024",
               "as_of": "2024-11-01", "value": 1, **prov}
    point_b = {"company": "AAPL", "kpi_id": "_X", "period": "FY2024",
               "as_of": "2024-11-01", "value": 2, **prov}

    kpi_store_module.append(point_a)
    kpi_store_module.append(point_b)

    series_files = list(tmp_path.rglob("*.json"))
    assert len(series_files) == 2, (
        f"colliding-prefix series must not share a file; found {series_files}"
    )
    stored_values = sorted(
        json.loads(f.read_text(encoding="utf-8"))["points"][0]["value"]
        for f in series_files
    )
    assert stored_values == [1, 2]


def test_append_rejects_missing_provenance(kpi_store_module, tmp_path, monkeypatch):
    """A point missing (empty) `source_cell_ref` must raise loud and write
    NOTHING — never an unattributed record slipping into the durable store.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    point = {
        "company": "AAPL",
        "kpi_id": "iphone_units",
        "period": "FY2024",
        "as_of": "2024-11-01",
        "value": 231000000,
        "source_accession": "0000320193-24-000123",
        "source_table_id": "ex99-1-operating-summary",
        "source_cell_ref": "",  # empty — must be rejected
    }

    with pytest.raises(ValueError, match="source_cell_ref"):
        kpi_store_module.append(point)

    assert list(tmp_path.rglob("*.json")) == [], (
        "rejecting a point for missing provenance must write nothing"
    )


def test_append_rejects_wallclock_or_absent_as_of(kpi_store_module, tmp_path, monkeypatch):
    """`as_of` must be accession/disclosure-derived, never wall-clock:

    (a) an empty `as_of` is rejected loud, nothing written;
    (b) a point explicitly flagged `as_of_is_wallclock: True` is rejected
        loud, nothing written — even though `as_of` itself looks valid;
    (c) a point with a valid accession-derived `as_of` (no wall-clock flag)
        still appends normally — exactly one file, one point.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    prov = {
        "source_accession": "0000320193-24-000123",
        "source_table_id": "ex99-1-operating-summary",
        "source_cell_ref": "r5c2",
    }
    base = {
        "company": "AAPL",
        "kpi_id": "iphone_units",
        "period": "FY2024",
        "value": 231000000,
        **prov,
    }

    # (a) as_of absent/empty
    point_no_asof = {**base, "as_of": ""}
    with pytest.raises(ValueError, match="as_of"):
        kpi_store_module.append(point_no_asof)
    assert list(tmp_path.rglob("*.json")) == [], (
        "rejecting a point for absent as_of must write nothing"
    )

    # (b) as_of present but explicitly wall-clock-derived
    point_wallclock = {**base, "as_of": "2024-11-01", "as_of_is_wallclock": True}
    with pytest.raises(ValueError, match="as_of"):
        kpi_store_module.append(point_wallclock)
    assert list(tmp_path.rglob("*.json")) == [], (
        "rejecting a wall-clock-flagged as_of must write nothing"
    )

    # (c) valid accession-derived as_of still appends
    point_valid = {**base, "as_of": "2024-11-01"}
    kpi_store_module.append(point_valid)
    series_files = list(tmp_path.rglob("*.json"))
    assert len(series_files) == 1
    envelope = json.loads(series_files[0].read_text(encoding="utf-8"))
    assert len(envelope["points"]) == 1
    assert envelope["points"][0] == point_valid


def test_reappend_same_accession_is_noop(kpi_store_module, tmp_path, monkeypatch):
    """Re-appending the IDENTICAL point (same dedup key = company, kpi_id,
    period, as_of, source_accession) is a no-op — no second record. A
    corrected value carrying a NEW as_of + source_accession is a DIFFERENT
    dedup key, so it appends a new record and BOTH are retained
    (append-only, bitemporal — never overwrite).
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    point = {
        "company": "AAPL",
        "kpi_id": "iphone_units",
        "period": "FY2024",
        "as_of": "2024-11-01",
        "value": 231000000,
        "source_accession": "0000320193-24-000123",
        "source_table_id": "ex99-1-operating-summary",
        "source_cell_ref": "r5c2",
    }

    # (1) append once, then append the IDENTICAL point again → still ONE record.
    kpi_store_module.append(point)
    kpi_store_module.append(dict(point))

    series_files = list(tmp_path.rglob("*.json"))
    assert len(series_files) == 1
    envelope = json.loads(series_files[0].read_text(encoding="utf-8"))
    assert len(envelope["points"]) == 1, (
        "re-appending the identical dedup key must be a no-op"
    )

    # (2) same (company, kpi_id, period) but a NEW as_of + accession →
    # a DIFFERENT dedup key, so it appends → TWO records total, both retained.
    corrected = {
        **point,
        "as_of": "2024-12-15",
        "source_accession": "0000320193-24-000456",
        "value": 232000000,
    }
    kpi_store_module.append(corrected)

    envelope = json.loads(series_files[0].read_text(encoding="utf-8"))
    assert len(envelope["points"]) == 2, (
        "a new as_of + source_accession is a different dedup key — "
        "both records must be retained"
    )


def test_same_dedup_key_different_value_keeps_first(
    kpi_store_module, tmp_path, monkeypatch
):
    """Documented contract: a same-dedup-key re-append with a DIFFERENT value
    is still a no-op that keeps the FIRST record. A corrected value must carry
    a new as_of (or accession) to supersede — that is the bitemporal rule;
    silently overwriting on an unchanged key would break append-only history.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    point = {
        "company": "AAPL",
        "kpi_id": "services_revenue",
        "period": "FY2024",
        "as_of": "2024-11-01",
        "value": 96000,
        "source_accession": "0000320193-24-000123",
        "source_table_id": "ex99-1-operating-summary",
        "source_cell_ref": "r7c2",
    }
    kpi_store_module.append(point)
    # Same 5-tuple dedup key, different value → no-op, first record kept.
    kpi_store_module.append({**point, "value": 99999})

    series_files = list(tmp_path.rglob("*.json"))
    assert len(series_files) == 1
    envelope = json.loads(series_files[0].read_text(encoding="utf-8"))
    assert len(envelope["points"]) == 1, (
        "same dedup key must stay a no-op even when the value differs"
    )
    assert envelope["points"][0]["value"] == 96000, (
        "first-wins: the original value is kept; a correction needs a new as_of"
    )
