"""Task 2 acceptance test — AVG-of-pre-aggregated-ratio trap model.

`seed_avg_ratio.csv` carries a pre-aggregated per-row `ratio` column
alongside its `numerator`/`denominator` components. Naively averaging the
`ratio` column (`AVG(ratio)`) is a well-known analytics trap: it weights
every row equally regardless of its denominator's size, which is
mathematically wrong whenever denominators differ across rows. The correct
aggregate is the weighted ratio `SUM(numerator) / SUM(denominator)`.

`fct_avg_ratio_trap` must compute the correct weighted ratio. This test
independently recomputes both the naive `AVG(ratio)` and the correct
weighted ratio straight from the seed CSV (not through dbt) and asserts:
  1. the model's output matches the correct weighted ratio, and
  2. the naive average is numerically different from that value —
     proving the seed data actually exercises the trap rather than
     coincidentally producing the same number either way.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "l2-harness"
SEED_CSV = FIXTURE_DIR / "seeds" / "seed_avg_ratio.csv"


def _load_seed_rows() -> list[dict[str, float]]:
    with SEED_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        return [
            {
                "numerator": float(row["numerator"]),
                "denominator": float(row["denominator"]),
                "ratio": float(row["ratio"]),
            }
            for row in reader
        ]


def test_weighted_ratio_differs_from_naive_avg(dbt_build):
    rows = _load_seed_rows()
    assert rows, "seed_avg_ratio.csv must have at least one data row"

    naive_avg = sum(r["ratio"] for r in rows) / len(rows)
    correct_weighted_ratio = sum(r["numerator"] for r in rows) / sum(
        r["denominator"] for r in rows
    )

    # Trap must be live: the naive and correct aggregates must actually
    # differ, otherwise this test would pass even if the model computed
    # the wrong thing.
    assert naive_avg != correct_weighted_ratio, (
        "seed_avg_ratio.csv rows make naive AVG(ratio) and the correct "
        "weighted ratio coincide — the trap is not exercised"
    )

    model_result = dbt_build.execute(
        "select weighted_ratio from fct_avg_ratio_trap"
    ).fetchone()
    assert model_result is not None, "fct_avg_ratio_trap returned no rows"

    (model_weighted_ratio,) = model_result
    assert model_weighted_ratio == pytest.approx(correct_weighted_ratio, rel=1e-9)
    assert model_weighted_ratio != pytest.approx(naive_avg, rel=1e-9)
