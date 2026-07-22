"""RED-first tests for the store enumeration primitive (Slice C, Task 1).

`kpi_store.list_series()` scans the store dir and returns the
`(company, kpi_id)` pairs held, recovered from each series file's stored
point CONTENT — the filename stem carries a one-way SHA-1 digest of the raw
(company, kpi_id) pair (`kpi_store.py:68-93`), so the raw identity can only
be read back from the points, never reversed out of the digest. An absent
store dir returns `[]`, never raises (matching the store's never-raise-on-read
posture, e.g. `_matching_points`/`query_latest`).

No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-22-kpi-observation-
history.md) binds tasks by "Brief item covered", not registered loom-spec
REQ-ids, so there is no id in the living-spec namespace to bind to (same
convention as test_kpi_8k_candidates_commit.py).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPT = (
    _TESTS_DIR.parent
    / "skills"
    / "analysis-kpi"
    / "scripts"
    / "kpi_store.py"
)

# A real accession so the store's accession-derived as_of guard passes; the
# store rejects a wall-clock or absent as_of.
_ACCESSION = "0001065280-25-000033"


def _load_module():
    spec = importlib.util.spec_from_file_location("kpi_store_enumerate", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_store_enumerate"] = module
    spec.loader.exec_module(module)
    return module


def _point(company: str, kpi_id: str, value: str) -> dict:
    """A minimal store-valid point: full provenance + an accession-derived
    (non-wall-clock) as_of, so `append` accepts it.
    """
    return {
        "company": company,
        "kpi_id": kpi_id,
        "period": "Q4-2024",
        "as_of": "2025-01-30",
        "value": value,
        "source_accession": _ACCESSION,
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
    }


def test_list_series_recovers_company_kpi(tmp_path, monkeypatch):
    """Append two points under distinct (company, kpi_id) series, then
    `list_series()` returns BOTH pairs — recovered from the stored point
    content, not by reversing the one-way filename digest.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    module.append(_point("AMZN", "employees", "1556000"))
    module.append(_point("TSLA", "deliveries", "495570"))

    series = module.list_series()

    assert sorted(series) == [
        ("AMZN", "employees"),
        ("TSLA", "deliveries"),
    ], series


def test_list_series_absent_store_returns_empty(tmp_path, monkeypatch):
    """`list_series()` on a store dir that does not exist returns `[]` and
    never raises — the store's never-raise-on-read posture.
    """
    store_dir = tmp_path / "does-not-exist"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    assert module.list_series() == []


def test_list_series_skips_a_corrupt_file_and_keeps_the_rest(tmp_path, monkeypatch):
    """A single malformed / non-dict series file in a long-lived store must
    degrade PER-FILE, not per-store: enumeration skips the bad file and still
    returns every OTHER series. Without the per-file guard, one interrupted
    external edit would blind the whole store.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    module.append(_point("AMZN", "employees", "1556000"))

    # A corrupt sibling: valid path, invalid JSON. Also a structurally-wrong
    # one: valid JSON whose `points` is not a list.
    (store_dir / "corrupt__x__deadbeef0000.json").write_text(
        "{ not json", encoding="utf-8"
    )
    (store_dir / "wrongshape__y__deadbeef0001.json").write_text(
        '{"points": null}', encoding="utf-8"
    )

    # The one good series still surfaces; the two bad files are skipped, not raised.
    assert module.list_series() == [("AMZN", "employees")]
