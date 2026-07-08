"""Task 5 acceptance test — forward-dated amortization MAX(date) trap model.

`seed_amortization.csv` carries real amortization snapshots on/before a fixed
reference "today" (2026-07-01) plus one forward-dated placeholder row
(2099-12-31) that is not a real snapshot. Selecting `MAX(as_of_date)` naively
picks that placeholder — the largest date in the table — instead of the true
as-of-today snapshot. The correct approach filters to `as_of_date <= today`
first, then takes the latest remaining snapshot.

`fct_amortization_trap` must return the as-of-today book_value. This test
independently recomputes both the naive `MAX(as_of_date)` row's value and the
as-of-correct value straight from the seed CSV (not through dbt) and asserts:
  1. the model's output matches the as-of-correct value, and
  2. the naive MAX-date value is numerically different from it — proving the
     forward-dated placeholder actually exercises the trap rather than
     coincidentally producing the same number.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

# Fixed reference "today" — must match the as-of filter hardcoded in
# fct_amortization_trap.sql and the seed's real-row dates.
TODAY = "2026-07-01"

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "l2-harness"
SEED_CSV = FIXTURE_DIR / "seeds" / "seed_amortization.csv"


def _load_seed_rows() -> list[dict[str, str]]:
    with SEED_CSV.open(newline="") as f:
        return list(csv.DictReader(f))


def test_asof_correct_value_differs_from_naive_max_date(dbt_build):
    rows = _load_seed_rows()
    assert rows, "seed_amortization.csv must have at least one data row"

    # Naive trap: the row with the largest as_of_date over ALL raw rows —
    # the forward-dated placeholder wins.
    naive_row = max(rows, key=lambda r: r["as_of_date"])
    naive_value = float(naive_row["book_value"])

    # As-of-correct: the latest snapshot on or before the fixed "today".
    asof_rows = [r for r in rows if r["as_of_date"] <= TODAY]
    assert asof_rows, "seed_amortization.csv has no rows on/before TODAY"
    correct_row = max(asof_rows, key=lambda r: r["as_of_date"])
    correct_value = float(correct_row["book_value"])

    # Trap must be live: the forward-dated placeholder must actually change
    # the answer, otherwise this test would pass even if the model naively
    # took MAX(as_of_date).
    assert naive_value != correct_value, (
        "seed_amortization.csv rows make the naive MAX(as_of_date) value and "
        "the as-of-today value coincide — the trap is not exercised"
    )

    model_result = dbt_build.execute(
        "select book_value from fct_amortization_trap"
    ).fetchone()
    assert model_result is not None, "fct_amortization_trap returned no rows"

    (model_value,) = model_result
    assert float(model_value) == pytest.approx(correct_value, rel=1e-9)
    assert float(model_value) != pytest.approx(naive_value, rel=1e-9)
