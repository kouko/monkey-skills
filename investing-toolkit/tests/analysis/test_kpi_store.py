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

import concurrent.futures
import importlib.util
import json
import sys
import threading
import time

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


def test_point_in_time_excludes_later_recast(kpi_store_module, tmp_path, monkeypatch):
    """A point-in-time query at a date BETWEEN an early point's as_of and a
    later recast's as_of must return the EARLY point, not the recast — a
    later restatement must never retroactively change what an earlier-dated
    query sees (no look-ahead bias). A query dated BEFORE the earliest as_of
    must return None (nothing qualifies yet).
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    prov = {
        "source_accession": "0000320193-24-000123",
        "source_table_id": "ex99-1-operating-summary",
        "source_cell_ref": "r5c2",
    }
    early = {
        "company": "AAPL",
        "kpi_id": "iphone_units",
        "period": "FY2024",
        "as_of": "2024-11-01",
        "value": "A",
        **prov,
    }
    recast = {
        **early,
        "as_of": "2025-02-15",
        "value": "B",
        "source_accession": "0000320193-25-000045",
    }
    kpi_store_module.append(early)
    kpi_store_module.append(recast)

    result = kpi_store_module.query_point_in_time(
        "AAPL", "iphone_units", "FY2024", "2024-12-31"
    )
    assert result is not None and result["value"] == "A", (
        "a query dated before the recast's as_of must see only the early point"
    )

    before_earliest = kpi_store_module.query_point_in_time(
        "AAPL", "iphone_units", "FY2024", "2024-01-01"
    )
    assert before_earliest is None, (
        "a query dated before ANY as_of must return None"
    )

    # Inclusive boundary: a query dated EXACTLY on an as_of returns that
    # record (the `<=` contract) — a regression to `<` would break this while
    # leaving the strictly-after/strictly-before cases above green.
    on_early = kpi_store_module.query_point_in_time(
        "AAPL", "iphone_units", "FY2024", "2024-11-01"
    )
    assert on_early is not None and on_early["value"] == "A", (
        "as_of_date exactly on the early point's as_of must return it (<= is inclusive)"
    )
    on_recast = kpi_store_module.query_point_in_time(
        "AAPL", "iphone_units", "FY2024", "2025-02-15"
    )
    assert on_recast is not None and on_recast["value"] == "B", (
        "as_of_date exactly on the recast's as_of must return the recast"
    )


def test_latest_returns_greatest_asof(kpi_store_module, tmp_path, monkeypatch):
    """query_latest returns the record with the greatest as_of overall for a
    (company, kpi_id, period) — the later recast, not the early point.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    prov = {
        "source_accession": "0000320193-24-000123",
        "source_table_id": "ex99-1-operating-summary",
        "source_cell_ref": "r5c2",
    }
    early = {
        "company": "AAPL",
        "kpi_id": "iphone_units",
        "period": "FY2024",
        "as_of": "2024-11-01",
        "value": "A",
        **prov,
    }
    recast = {
        **early,
        "as_of": "2025-02-15",
        "value": "B",
        "source_accession": "0000320193-25-000045",
    }
    kpi_store_module.append(early)
    kpi_store_module.append(recast)

    result = kpi_store_module.query_latest("AAPL", "iphone_units", "FY2024")
    assert result is not None and result["value"] == "B", (
        "query_latest must return the greatest-as_of record (the recast)"
    )

    # Symmetry with point-in-time: no matching series (or period) → None,
    # not a raise.
    assert kpi_store_module.query_latest("AAPL", "iphone_units", "FY1999") is None
    assert kpi_store_module.query_latest("NOPE", "nope", "FY2024") is None


def test_concurrent_appends_both_persist(kpi_store_module, tmp_path, monkeypatch):
    """Two+ concurrent writers appending DISTINCT points to the SAME series
    must ALL persist — no lost update from the read-modify-write race in
    `append()` (load series -> dedup-scan -> atomic write). A
    `threading.Barrier` forces every writer to enter `append()` at
    (approximately) the same instant; `_load_series` is monkeypatched with a
    deliberate sleep AFTER the read to widen the load->write race window to
    something a thread-scheduling accident can't paper over — this is what
    makes the test a real exercise of the lock rather than a
    serialized-by-luck pass.

    Regression for the lost-update bug: without a lock spanning the FULL
    read-modify-write cycle, two writers can both read the same
    (empty-of-each-other's-point) series, each append their own point in
    memory, and the second `_atomic_write`'s rename clobbers the first —
    losing one point. With the lock, only one writer holds the series at a
    time, so every point survives.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    original_load_series = kpi_store_module._load_series

    def slow_load_series(path):
        envelope = original_load_series(path)
        time.sleep(0.05)  # widen the race window between read and write
        return envelope

    monkeypatch.setattr(kpi_store_module, "_load_series", slow_load_series)

    prov = {
        "source_table_id": "ex99-1-operating-summary",
        "source_cell_ref": "r5c2",
    }
    n_writers = 6
    barrier = threading.Barrier(n_writers)

    def make_point(i):
        return {
            "company": "AAPL",
            "kpi_id": "concurrent_kpi",
            "period": "FY2024",
            "as_of": f"2024-11-{i + 1:02d}",
            "value": i,
            "source_accession": f"0000320193-24-00{i:04d}",
            **prov,
        }

    def writer(i):
        barrier.wait()  # force all writers to hit append() simultaneously
        kpi_store_module.append(make_point(i))

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_writers) as executor:
        futures = [executor.submit(writer, i) for i in range(n_writers)]
        for f in futures:
            f.result()

    series_files = list(tmp_path.rglob("*.json"))
    assert len(series_files) == 1, (
        f"expected exactly one series file, found {series_files}"
    )
    envelope = json.loads(series_files[0].read_text(encoding="utf-8"))
    assert len(envelope["points"]) == n_writers, (
        f"expected all {n_writers} concurrent appends to persist, found "
        f"{len(envelope['points'])} — lost update from an unlocked "
        f"read-modify-write race"
    )
    values = sorted(p["value"] for p in envelope["points"])
    assert values == list(range(n_writers)), (
        "every writer's distinct point must be present, none lost"
    )


def test_append_degrades_loud_when_fcntl_unavailable(
    kpi_store_module, tmp_path, monkeypatch, capsys
):
    """On a host with no `fcntl` (non-POSIX), append must still WRITE the
    point (degrade, not crash or silently drop) and emit exactly ONE loud
    stderr warning that it is not concurrency-safe — never per-call spam,
    never a silent skip.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    # Simulate the non-POSIX host: no fcntl module, warn-once flag reset.
    monkeypatch.setattr(kpi_store_module, "fcntl", None)
    monkeypatch.setattr(kpi_store_module, "_warned_no_fcntl", False)

    base = {
        "company": "AAPL",
        "kpi_id": "iphone_units",
        "period": "FY2024",
        "source_accession": "0000320193-24-000123",
        "source_table_id": "ex99-1-operating-summary",
        "source_cell_ref": "r5c2",
    }
    kpi_store_module.append({**base, "as_of": "2024-11-01", "value": 1})
    # Second append (distinct dedup key) must NOT re-warn — warn-once.
    kpi_store_module.append(
        {**base, "as_of": "2025-02-15", "value": 2,
         "source_accession": "0000320193-25-000045"}
    )

    series_files = list(tmp_path.rglob("*.json"))
    assert len(series_files) == 1
    envelope = json.loads(series_files[0].read_text(encoding="utf-8"))
    assert len(envelope["points"]) == 2, (
        "append must still persist points when running unlocked (degraded)"
    )

    err = capsys.readouterr().err
    assert err.count("fcntl unavailable") == 1, (
        "the degradation warning must fire exactly once, not per append"
    )
