"""test_derived_q4_calendar_fields.py — the derived Q4's calendar labels.

`_mint_derived_q4_point` computes `calendar_quarter` from the fiscal-year-end
month by integer division. A sampled mutation pass (2026-07-27) changed the
divisor from 3 to 4 with all 1363 tests still green: every existing test of
this function asserts the derived VALUE (FY total minus YTD) and the
segregated-lane markers, and none asserts the calendar labels.

The failure mode is the quiet kind. A wrong divisor does not raise — it files
a December fiscal-year-end under Q3 and a March one under Q1, so a
company's quarterly series is silently mis-binned by calendar quarter while
every figure in it is correct.

Which test holds which mutant, measured rather than assumed: under the
`// 3 -> // 4` mutation ONLY the December row fails — `(9-1)//4+1 = 3`,
`(6-1)//4+1 = 2` and `(1-1)//4+1 = 1` all still match their expected quarter.
`test_every_month_maps_into_exactly_four_quarters` is the guard that holds the
divisor in general. The non-December rows are not decoration: they carry the
fiscal-year shapes this repo's verification roster exists for — AAPL(Sep),
MSFT(Jun), NVDA(Jan) — and each fails under other single-line mutations of
this function (e.g. dropping the `+ 1`), but they are regression guards for
the labels rather than the killers of the divisor mutant.
"""
from __future__ import annotations

import importlib.util
import sys

import pytest
from conftest import KPI_XBRL_SCRIPT


@pytest.fixture(scope="module")
def kpi_xbrl_module():
    spec = importlib.util.spec_from_file_location(
        "kpi_xbrl_q4_calendar_test", KPI_XBRL_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_xbrl_q4_calendar_test"] = module
    spec.loader.exec_module(module)
    return module


def _pair(fy_end: str, ytd_end: str):
    fy = {
        "company": "TEST", "kpi_id": "revenue", "period_end": fy_end,
        "value": 100.0, "as_of": "2025-02-01",
        "source_accession": "0000000000-25-000001", "source_form": "10-K",
    }
    ytd = {
        "company": "TEST", "kpi_id": "revenue", "period_end": ytd_end,
        "value": 70.0, "as_of": "2024-11-01",
        "source_accession": "0000000000-24-000009", "source_form": "10-Q",
    }
    return fy, ytd


@pytest.mark.parametrize(
    "fy_end,ytd_end,expected_quarter,filer_shape",
    [
        ("2024-12-31", "2024-09-30", "Q4", "calendar-year filer"),
        ("2024-09-28", "2024-06-29", "Q3", "AAPL-shaped September FYE"),
        ("2024-06-30", "2024-03-31", "Q2", "MSFT-shaped June FYE"),
        ("2024-01-28", "2023-10-29", "Q1", "NVDA-shaped January FYE"),
    ],
)
def test_calendar_quarter_bins_the_fiscal_year_end_month(
    kpi_xbrl_module, fy_end, ytd_end, expected_quarter, filer_shape
):
    """Each fiscal-year-end month must land in its own calendar quarter."""
    fy, ytd = _pair(fy_end, ytd_end)

    point = kpi_xbrl_module._mint_derived_q4_point(fy, ytd, "2024-Q4", "cell-1")

    assert point["calendar_quarter"] == expected_quarter, (
        f"{filer_shape}: FYE {fy_end} belongs to {expected_quarter}, got "
        f"{point['calendar_quarter']}"
    )
    assert point["calendar_year"] == int(fy_end[:4])


def test_every_month_maps_into_exactly_four_quarters(kpi_xbrl_module):
    """The property behind the table above, so a divisor change cannot pass
    by happening to be right for the four months sampled: twelve months must
    produce exactly Q1..Q4, three months each."""
    seen = []
    for month in range(1, 13):
        fy, ytd = _pair(f"2024-{month:02d}-28", "2023-12-31")
        seen.append(
            kpi_xbrl_module._mint_derived_q4_point(fy, ytd, "p", "c")["calendar_quarter"]
        )

    assert sorted(set(seen)) == ["Q1", "Q2", "Q3", "Q4"]
    assert [seen.count(q) for q in ("Q1", "Q2", "Q3", "Q4")] == [3, 3, 3, 3], (
        f"months did not bin three-per-quarter: {seen}"
    )
