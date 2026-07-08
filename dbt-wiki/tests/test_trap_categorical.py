"""Task 4 acceptance test — categorical value_domain trap model.

`seed_categorical.csv` carries a categorical `status` column drawn from a
fixed value_domain (the accepted set {active, churned, trial}) with known
per-category row counts. `fct_categorical_trap` passes the column through
unchanged, and its .yml declares an `accepted_values` generic dbt test on
the column, so `dbt build` fails loudly if any out-of-domain value ever
appears — the categorical trap this fixture guards against, where a silent
transformation (an unmapped CASE branch, a typo) leaks a value outside the
declared domain. This test independently tallies the seed CSV's per-category
counts and asserts the model, grouped by category, reproduces them exactly.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "l2-harness"
SEED_CSV = FIXTURE_DIR / "seeds" / "seed_categorical.csv"


def _seed_category_counts() -> dict[str, int]:
    with SEED_CSV.open(newline="") as f:
        return dict(Counter(row["status"] for row in csv.DictReader(f)))


def test_category_counts_match_seed(dbt_build):
    seed_counts = _seed_category_counts()
    assert seed_counts, "seed_categorical.csv must have at least one data row"

    model_counts = dict(
        dbt_build.execute(
            "select status, count(*) from fct_categorical_trap group by status"
        ).fetchall()
    )

    assert model_counts == seed_counts
