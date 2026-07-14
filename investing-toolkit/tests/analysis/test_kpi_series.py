"""Tests for analysis-kpi/scripts/kpi_series.py — split a period-ordered
series into as-reported/recast lineages by its applied breaks
(operational-kpi capability, slice 7, Task 2).

kpi_series.py is PURE-COMPUTE (stdlib only) — it does NOT import
`_store_fs`, resolve a store dir, lock, or persist anything; `split_series`
takes `points` + `applied_breaks` as plain arguments. No `KPI_STORE_DIR`
fixture is needed.

The library function is exercised by loading `kpi_series.py` via importlib
(same convention as test_kpi_validate.py's `kpi_validate_module` fixture).

No `@req` tags: this dispatch's plan/spec trace work by named change-folder
Requirements (operational-kpi / "Dual as-reported/recast series with visible
break flag"), NOT by registered loom-spec REQ-ids — so `@req` is omitted per
the implementer contract.
"""
from __future__ import annotations

import importlib.util
import sys

from conftest import KPI_SERIES_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_series_module():
    """Load kpi_series.py as an importable module for unit tests of its
    library surface (split_series).
    """
    spec = importlib.util.spec_from_file_location("kpi_series_test", KPI_SERIES_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_series_test"] = module
    spec.loader.exec_module(module)
    return module


def test_split_series_partitions_by_break(kpi_series_module):
    """Task 2: split_series(points, applied_breaks) partitions a
    period-ordered series into as_reported (periods before the earliest
    break_period) and recast (periods AT/after it), plus one break_marker
    per applied break. No applied_breaks → all points in as_reported,
    recast and break_markers both empty.
    """
    points = [
        {"period": "FY2022", "value": 100},
        {"period": "FY2023", "value": 110},
        {"period": "FY2024", "value": 120},
        {"period": "FY2025", "value": 130},
    ]
    applied_breaks = [{"break_period": "FY2024"}]

    result = kpi_series_module.split_series(points, applied_breaks)

    assert result["as_reported"] == [
        {"period": "FY2022", "value": 100},
        {"period": "FY2023", "value": 110},
    ]
    assert result["recast"] == [
        {"period": "FY2024", "value": 120},
        {"period": "FY2025", "value": 130},
    ]
    assert result["break_markers"] == [{"break_period": "FY2024"}]

    # No applied breaks → nothing to split; all points stay as_reported.
    no_break_result = kpi_series_module.split_series(points, [])
    assert no_break_result["as_reported"] == points
    assert no_break_result["recast"] == []
    assert no_break_result["break_markers"] == []

    # MULTIPLE (out-of-order) applied breaks: the two-way split uses the
    # EARLIEST break_period as the boundary, and EVERY break is surfaced in
    # break_markers (a regression to latest-boundary or dropped markers must fail here).
    multi_breaks = [{"break_period": "FY2024"}, {"break_period": "FY2023"}]
    multi = kpi_series_module.split_series(points, multi_breaks)
    assert [p["period"] for p in multi["as_reported"]] == ["FY2022"], (
        "split must use the EARLIEST break_period (FY2023) as the boundary"
    )
    assert [p["period"] for p in multi["recast"]] == ["FY2023", "FY2024", "FY2025"]
    assert len(multi["break_markers"]) == 2, "every applied break must be surfaced"

    # Empty points → empty partitions, no crash.
    empty = kpi_series_module.split_series([], applied_breaks)
    assert empty["as_reported"] == []
    assert empty["recast"] == []
