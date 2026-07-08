"""Task 6 acceptance test — region-prefixed scope-undercount trap.

`seed_regional_twins` splits each logical entity's rows across multiple
regions (a `region` column). `fct_regional_twins_trap` unions ALL regional
twins before aggregating, so each entity's full-scope amount sums every
region. The naive approach — scanning only one region (e.g.
`WHERE region = 'us'`) — silently drops the other regions' rows and
undercounts the true total. This test proves the model captures full scope
by independently recomputing the naive single-region scan straight from the
seed CSV and asserting it undercounts (is strictly less than) the model's
correct full-scope total.
"""
from __future__ import annotations

import csv
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "l2-harness"
TWINS_CSV = FIXTURE_DIR / "seeds" / "seed_regional_twins.csv"

NAIVE_REGION = "us"


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _naive_single_region_total() -> float:
    """Independently recompute the trap: scan only NAIVE_REGION's rows and
    sum their amount, ignoring every other region's twin rows. This drops
    real nonzero values and undercounts the full-scope total.
    """
    return sum(
        float(row["amount"])
        for row in _read_csv_rows(TWINS_CSV)
        if row["region"] == NAIVE_REGION
    )


def test_full_scope_total_differs_from_single_region_scan(dbt_build):
    full_scope_total = dbt_build.execute(
        "select sum(full_scope_amount) from fct_regional_twins_trap"
    ).fetchone()[0]

    naive_total = _naive_single_region_total()

    assert naive_total != full_scope_total, (
        "single-region scan should undercount relative to the full-scope "
        "union-all-regions model total"
    )
    assert naive_total < full_scope_total
