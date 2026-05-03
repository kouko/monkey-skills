#!/usr/bin/env python3
"""Smoke test for extract_recursive_column_lineage.py.

Builds synthetic manifest + per-SQL lineage JSONL (no sqlglot needed,
no real dbt project), invokes the script via subprocess, asserts the
recursive walker produces correct ancestor/descendant trees.

Run:

    python3 extract_recursive_column_lineage_test.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent / "extract_recursive_column_lineage.py"


# --- Synthetic dbt project ---
# Three-tier: source → stg → fct → mart
#
# raw_data.orders_raw
#   id, customer_id, status                        (source columns)
#       └→ stg_orders.order_id (← raw.id)
#          stg_orders.customer_id (← raw.customer_id)
#          └→ fct_orders.order_id (← stg_orders.order_id)
#             fct_orders.customer_id
#                  ← stg_orders.customer_id
#                  ← stg_customers.id (COALESCE — multi-source)
#             └→ mart_finance.daily_orders (← fct_orders.order_id)


def build_synthetic_inputs(workdir: Path) -> tuple[Path, Path]:
    manifest = {
        "nodes": {
            "model.proj.stg_orders": {
                "resource_type": "model",
                "name": "stg_orders",
                "alias": "stg_orders",
                "schema": "dbt_stg",
                "database": "dev",
                "original_file_path": "models/staging/stg_orders.sql",
                "depends_on": {"nodes": ["source.proj.raw_data.orders_raw"]},
            },
            "model.proj.stg_customers": {
                "resource_type": "model",
                "name": "stg_customers",
                "alias": "stg_customers",
                "schema": "dbt_stg",
                "database": "dev",
                "original_file_path": "models/staging/stg_customers.sql",
                "depends_on": {"nodes": ["source.proj.raw_data.customers_raw"]},
            },
            "model.proj.fct_orders": {
                "resource_type": "model",
                "name": "fct_orders",
                "alias": "fct_orders",
                "schema": "dbt_marts",
                "database": "dev",
                "original_file_path": "models/marts/fct_orders.sql",
                "depends_on": {
                    "nodes": [
                        "model.proj.stg_orders",
                        "model.proj.stg_customers",
                    ]
                },
            },
            "model.proj.mart_finance": {
                "resource_type": "model",
                "name": "mart_finance",
                "alias": "mart_finance",
                "schema": "dbt_marts",
                "database": "dev",
                "original_file_path": "models/marts/mart_finance.sql",
                "depends_on": {"nodes": ["model.proj.fct_orders"]},
            },
        },
        "sources": {
            "source.proj.raw_data.orders_raw": {
                "name": "orders_raw",
                "identifier": "orders_raw",
                "source_name": "raw_data",
                "schema": "raw",
                "database": "warehouse",
            },
            "source.proj.raw_data.customers_raw": {
                "name": "customers_raw",
                "identifier": "customers_raw",
                "source_name": "raw_data",
                "schema": "raw",
                "database": "warehouse",
            },
        },
    }

    # Per-SQL lineage (what extract_column_lineage.py would produce in batch mode)
    lineage_records = [
        {
            "path": "models/staging/stg_orders.sql",
            "result": {
                "order_id": ["orders_raw.id"],
                "customer_id": ["orders_raw.customer_id"],
                "status": ["orders_raw.status"],
            },
        },
        {
            "path": "models/staging/stg_customers.sql",
            "result": {
                "id": ["customers_raw.id"],
                "email": ["customers_raw.email"],
            },
        },
        {
            "path": "models/marts/fct_orders.sql",
            "result": {
                "order_id": ["stg_orders.order_id"],
                "customer_id": ["stg_orders.customer_id", "stg_customers.id"],
            },
        },
        {
            "path": "models/marts/mart_finance.sql",
            "result": {
                "daily_orders": ["fct_orders.order_id"],
            },
        },
    ]

    manifest_path = workdir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))

    lineage_path = workdir / "lineage.jsonl"
    lineage_path.write_text(
        "\n".join(json.dumps(r) for r in lineage_records) + "\n"
    )

    return manifest_path, lineage_path


def run(manifest: Path, lineage: Path, model: str = None, column: str = None) -> list[dict]:
    args = [
        sys.executable,
        str(SCRIPT),
        "--manifest",
        str(manifest),
        "--lineage",
        str(lineage),
    ]
    if model:
        args += ["--model", model]
    if column:
        args += ["--column", column]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        return [{"_test_error": f"exit={proc.returncode}: {proc.stderr[:300]}"}]
    out = []
    for line in proc.stdout.strip().split("\n"):
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                out.append({"_test_error": f"non-JSON: {e}; raw={line[:200]}"})
    return out


def find(records: list[dict], uid: str, col: str) -> dict | None:
    for r in records:
        if r.get("model_uid") == uid and r.get("column") == col:
            return r
    return None


CASES = [
    # (test_name, model_filter, column_filter, assertion_fn)
    (
        "fct_orders.customer_id ancestors should reach raw.customer_id and raw customers.id",
        "model.proj.fct_orders",
        "customer_id",
        lambda recs: (
            len(recs) == 1
            and "model.proj.stg_orders::customer_id" in recs[0]["ancestors"]
            and "source.proj.raw_data.orders_raw::customer_id"
            in recs[0]["ancestors"]["model.proj.stg_orders::customer_id"]
            and "model.proj.stg_customers::id" in recs[0]["ancestors"]
            and "source.proj.raw_data.customers_raw::id"
            in recs[0]["ancestors"]["model.proj.stg_customers::id"]
        ),
    ),
    (
        "fct_orders.customer_id descendants should NOT include mart_finance.daily_orders (different col)",
        "model.proj.fct_orders",
        "customer_id",
        lambda recs: len(recs) == 1
        and "model.proj.mart_finance::daily_orders" not in recs[0]["descendants"],
    ),
    (
        "fct_orders.order_id descendants SHOULD include mart_finance.daily_orders",
        "model.proj.fct_orders",
        "order_id",
        lambda recs: (
            len(recs) == 1
            and "model.proj.mart_finance::daily_orders" in recs[0]["descendants"]
        ),
    ),
    (
        "stg_orders.customer_id ancestors should reach raw orders_raw.customer_id (single hop)",
        "model.proj.stg_orders",
        "customer_id",
        lambda recs: (
            len(recs) == 1
            and "source.proj.raw_data.orders_raw::customer_id"
            in recs[0]["ancestors"]
        ),
    ),
    (
        "stg_orders.order_id descendants should reach mart_finance.daily_orders (2 hops via fct)",
        "model.proj.stg_orders",
        "order_id",
        lambda recs: (
            len(recs) == 1
            and "model.proj.fct_orders::order_id" in recs[0]["descendants"]
            and "model.proj.mart_finance::daily_orders"
            in recs[0]["descendants"]["model.proj.fct_orders::order_id"]
        ),
    ),
    (
        "Whole-project run produces one record per (model, column)",
        None,
        None,
        lambda recs: len(recs)
        == sum(
            1
            for _ in [
                "stg_orders.order_id",
                "stg_orders.customer_id",
                "stg_orders.status",
                "stg_customers.id",
                "stg_customers.email",
                "fct_orders.order_id",
                "fct_orders.customer_id",
                "mart_finance.daily_orders",
            ]
        ),  # 8 records
    ),
]


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="dbt-wiki-recursive-test-"))
    manifest, lineage = build_synthetic_inputs(workdir)

    failures = 0
    for i, (name, model, col, assertion) in enumerate(CASES, 1):
        recs = run(manifest, lineage, model, col)
        try:
            ok = assertion(recs)
        except Exception as e:  # noqa: BLE001
            ok = False
            print(f"[{i}/{len(CASES)}] FAIL  {name}")
            print(f"         assertion raised: {e}")
            print(f"         records: {json.dumps(recs, indent=2)[:500]}")
            failures += 1
            continue
        if ok:
            print(f"[{i}/{len(CASES)}] OK    {name}")
        else:
            print(f"[{i}/{len(CASES)}] FAIL  {name}")
            print(f"         records: {json.dumps(recs, indent=2)[:500]}")
            failures += 1

    # Cleanup
    import shutil

    shutil.rmtree(workdir, ignore_errors=True)

    print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
