"""Task 3 acceptance test — compound-key fan-out join trap.

`fct_fanout_trap` pre-aggregates `seed_fanout_line_items` (one-to-many on
order_id) by order BEFORE joining to `seed_fanout_orders`, so each order's
`shipping_fee` (an order-grain attribute) is added exactly once per order.
The naive approach — joining orders to line_items raw, then summing
`quantity * unit_price + shipping_fee` over every joined row — re-adds
`shipping_fee` once per line item, overcounting the grand total for any
order with 2+ line items. This test proves the model avoids that trap by
independently recomputing the naive (wrong) total straight from the seed
CSVs and asserting it differs from (overcounts) the model's correct total.
"""
from __future__ import annotations

import csv
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "l2-harness"
ORDERS_CSV = FIXTURE_DIR / "seeds" / "seed_fanout_orders.csv"
LINE_ITEMS_CSV = FIXTURE_DIR / "seeds" / "seed_fanout_line_items.csv"


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _naive_join_sum_total() -> float:
    """Independently recompute the trap: raw JOIN of every line_item row to
    its order, then SUM(quantity * unit_price + shipping_fee) over every
    joined row — no pre-aggregation. Orders with 2+ line items have their
    shipping_fee counted once per line item, so this overcounts.
    """
    orders_by_id = {row["order_id"]: row for row in _read_csv_rows(ORDERS_CSV)}
    line_items = _read_csv_rows(LINE_ITEMS_CSV)

    total = 0.0
    for li in line_items:
        order = orders_by_id[li["order_id"]]
        total += float(li["quantity"]) * float(li["unit_price"]) + float(order["shipping_fee"])
    return total


def test_grain_correct_total_differs_from_naive_join_sum(dbt_build):
    correct_total = dbt_build.execute(
        "select sum(order_total) from fct_fanout_trap"
    ).fetchone()[0]

    naive_total = _naive_join_sum_total()

    assert naive_total != correct_total, (
        "naive join+sum should overcount relative to the grain-correct model total"
    )
    assert naive_total > correct_total
