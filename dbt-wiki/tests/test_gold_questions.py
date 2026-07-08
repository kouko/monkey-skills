"""Task 8 acceptance test — gold-questions.yml expected answers.

`gold-questions.yml` (fixture root) holds one blind-agent question per trap
model, each carrying an `expected_answer` and a `required_invariants` list.
Those expected answers must be re-derivable straight from the raw seed CSVs,
NOT copied from a trap model's own output — otherwise a wrong model and a
wrong gold value could agree and the harness would prove nothing.

This test recomputes every gold value independently from the seed CSVs
(plain `csv` module + `Decimal`, never through dbt) and asserts each parsed
`expected_answer` matches. It also asserts every trap is covered exactly
once and every question carries a non-empty `required_invariants` list.
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

import yaml

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "l2-harness"
GOLD_YAML = FIXTURE_DIR / "gold-questions.yml"
SEEDS = FIXTURE_DIR / "seeds"

# The fixture's fixed reference "today" — mirrors fct_amortization_trap.sql,
# which hardcodes date '2026-07-01' because DuckDB has no wall-clock notion of
# the fixture's present.
FIXTURE_TODAY = "2026-07-01"


def _seed_rows(name: str) -> list[dict[str, str]]:
    with (SEEDS / name).open(newline="") as f:
        return list(csv.DictReader(f))


def _recompute_avg_ratio() -> Decimal:
    rows = _seed_rows("seed_avg_ratio.csv")
    numerator = sum(Decimal(r["numerator"]) for r in rows)
    denominator = sum(Decimal(r["denominator"]) for r in rows)
    return numerator / denominator


def _recompute_fanout() -> Decimal:
    line_total_by_order: dict[str, Decimal] = {}
    for item in _seed_rows("seed_fanout_line_items.csv"):
        line_total_by_order[item["order_id"]] = (
            line_total_by_order.get(item["order_id"], Decimal("0"))
            + Decimal(item["quantity"]) * Decimal(item["unit_price"])
        )
    total = Decimal("0")
    for order in _seed_rows("seed_fanout_orders.csv"):
        total += line_total_by_order[order["order_id"]] + Decimal(
            order["shipping_fee"]
        )
    return total


def _recompute_categorical() -> int:
    return sum(
        1 for r in _seed_rows("seed_categorical.csv") if r["status"] == "active"
    )


def _recompute_amortization() -> Decimal:
    # ISO-8601 zero-padded dates sort lexicographically, so string compare is
    # equivalent to date compare here.
    eligible = [
        r
        for r in _seed_rows("seed_amortization.csv")
        if r["as_of_date"] <= FIXTURE_TODAY
    ]
    latest = max(eligible, key=lambda r: r["as_of_date"])
    return Decimal(latest["book_value"])


def _recompute_regional_twins() -> Decimal:
    return sum(
        Decimal(r["amount"])
        for r in _seed_rows("seed_regional_twins.csv")
        if r["entity_id"] == "widget"
    )


RECOMPUTE = {
    "avg_ratio": _recompute_avg_ratio,
    "fanout": _recompute_fanout,
    "categorical": _recompute_categorical,
    "amortization": _recompute_amortization,
    "regional_twins": _recompute_regional_twins,
}


def _load_gold() -> list[dict]:
    with GOLD_YAML.open() as f:
        return yaml.safe_load(f)


def test_gold_values_match_independent_seed_derivation():
    gold = _load_gold()
    assert isinstance(gold, list) and gold, "gold-questions.yml must be a non-empty list"

    traps_seen = [entry["trap"] for entry in gold]
    assert set(traps_seen) == set(RECOMPUTE), (
        f"gold-questions.yml must cover exactly the 5 traps {sorted(RECOMPUTE)}, "
        f"got {sorted(traps_seen)}"
    )
    assert len(traps_seen) == len(set(traps_seen)), "each trap must appear exactly once"

    for entry in gold:
        trap = entry["trap"]

        assert isinstance(entry.get("question"), str) and entry["question"].strip(), (
            f"trap {trap!r}: question must be a non-empty string"
        )

        invariants = entry.get("required_invariants")
        assert isinstance(invariants, list) and invariants, (
            f"trap {trap!r}: required_invariants must be a non-empty list"
        )
        assert all(
            isinstance(inv, str) and inv.strip() for inv in invariants
        ), f"trap {trap!r}: every required_invariant must be a non-empty string"

        recomputed = RECOMPUTE[trap]()
        assert Decimal(str(entry["expected_answer"])) == Decimal(str(recomputed)), (
            f"trap {trap!r}: gold expected_answer {entry['expected_answer']!r} "
            f"does not match value {recomputed} recomputed straight from the seed CSVs"
        )
