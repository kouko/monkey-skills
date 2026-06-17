#!/usr/bin/env python3
"""Smoke test for build_evidence_pages.py.

Run from this directory:

    python3 build_evidence_pages_test.py

Pure stdlib — no third-party deps (the generator is stdlib-only too).
Builds a tiny synthetic manifest + sqlglot JSONL fixtures in a tempdir,
runs the generator, and asserts the emitted evidence pages / index /
lineage match the SCHEMA contract.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent / "build_evidence_pages.py"

PROJECT = "testproj"

MANIFEST = {
    "metadata": {"project_name": PROJECT},
    "nodes": {
        "model.testproj.stg_orders": {
            "resource_type": "model", "name": "stg_orders", "package_name": PROJECT,
            "original_file_path": "models/staging/stg_orders.sql",
            "schema": "stg", "database": "db", "access": "protected", "group": None,
            "config": {"materialized": "view", "tags": []},
            "contract": {"enforced": False},
            "depends_on": {"nodes": ["source.testproj.raw.orders_raw"], "macros": ["macro.testproj.helper"]},
            "sources": [["raw", "orders_raw"]],
            "columns": {"order_id": {"name": "order_id", "description": "order pk", "data_type": "bigint"}},
            "raw_code": "select 1 as order_id",
        },
        "model.testproj.fct_orders": {
            "resource_type": "model", "name": "fct_orders", "package_name": PROJECT,
            "original_file_path": "models/marts/fct_orders.sql",
            "schema": "marts", "database": "db", "access": "protected", "group": None,
            "config": {"materialized": "table", "tags": ["finance"]},
            "contract": {"enforced": False},
            "depends_on": {"nodes": ["model.testproj.stg_orders"], "macros": []},
            "sources": [],
            "columns": {
                "order_id": {"name": "order_id", "description": "pk", "data_type": "bigint"},
                "customer_id": {"name": "customer_id", "description": "fk", "data_type": "bigint"},
            },
            "raw_code": "-- orders fact\nselect order_id, customer_id from {{ ref('stg_orders') }}",
        },
        "seed.testproj.seed_x": {
            "resource_type": "seed", "name": "seed_x", "package_name": PROJECT,
            "original_file_path": "seeds/seed_x.csv", "schema": "stg",
            "config": {}, "depends_on": {"nodes": [], "macros": []},
            "columns": {"k": {"name": "k", "description": "key"}},
        },
        "test.testproj.not_null_fct_orders_order_id": {
            "resource_type": "test", "name": "not_null_fct_orders_order_id",
            "package_name": PROJECT, "original_file_path": "models/marts/schema.yml",
            "column_name": "order_id", "attached_node": "model.testproj.fct_orders",
            "test_metadata": {"name": "not_null"},
            "depends_on": {"nodes": ["model.testproj.fct_orders"], "macros": []},
        },
        "test.testproj.singular_check": {
            "resource_type": "test", "name": "singular_check", "package_name": PROJECT,
            "original_file_path": "tests/singular_check.sql",
            "column_name": None, "attached_node": None, "test_metadata": None,
            "depends_on": {"nodes": ["model.testproj.fct_orders"], "macros": []},
            "raw_code": "select * from {{ ref('fct_orders') }} where order_id is null",
        },
    },
    "sources": {
        "source.testproj.raw.orders_raw": {
            "unique_id": "source.testproj.raw.orders_raw",
            "source_name": "raw", "name": "orders_raw", "schema": "raw", "database": "db",
            "loaded_at_field": None, "freshness": None, "description": "raw orders",
            "columns": {"order_id": {"name": "order_id", "description": "raw id"}},
        }
    },
    "macros": {
        "macro.testproj.helper": {
            "unique_id": "macro.testproj.helper", "name": "helper", "package_name": PROJECT,
            "original_file_path": "macros/helper.sql", "arguments": [], "description": "a helper",
        }
    },
}

COL_LINEAGE = [
    {"path": "models/marts/fct_orders.sql",
     "result": {"order_id": ["stg_orders.order_id"], "customer_id": ["stg_orders.customer_id"]}},
    {"path": "models/staging/stg_orders.sql", "result": {"order_id": ["orders_raw.order_id"]}},
]
COMMENTS = [{"path": "marts/fct_orders.sql", "comments": [{"line": 1, "kind": "line", "text": "orders fact"}]}]
RECURSIVE = [{"model_uid": "model.testproj.fct_orders", "column": "order_id",
              "ancestors": {"model.testproj.stg_orders::order_id": {"source.testproj.raw.orders_raw::order_id": {}}},
              "descendants": {}}]


def write_jsonl(path: Path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def run(tmp: Path):
    dbt = tmp / "dbt"; wiki = tmp / ".dbt-wiki"
    (dbt / "target").mkdir(parents=True)
    for sub in ("_evidence/models", "_evidence/sources", "_evidence/macros",
                "_evidence/seeds", "_evidence/tests"):
        (wiki / sub).mkdir(parents=True)
    (dbt / "target" / "manifest.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
    write_jsonl(tmp / "cl.jsonl", COL_LINEAGE)
    write_jsonl(tmp / "cm.jsonl", COMMENTS)
    write_jsonl(tmp / "rc.jsonl", RECURSIVE)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--manifest", str(dbt / "target" / "manifest.json"),
         "--wiki-dir", str(wiki), "--dbt-dir", str(dbt),
         "--col-lineage", str(tmp / "cl.jsonl"),
         "--comments", str(tmp / "cm.jsonl"),
         "--recursive-lineage", str(tmp / "rc.jsonl"),
         "--today", "2026-06-17"],
        capture_output=True, text=True)
    return wiki, proc


CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


@check("generator exits 0")
def c_exit(wiki, proc):
    return proc.returncode == 0, f"rc={proc.returncode} stderr={proc.stderr[-300:]}"


@check("stats JSON reports 2 models")
def c_stats(wiki, proc):
    try:
        st = json.loads(proc.stdout)
    except Exception as e:
        return False, f"stdout not JSON: {e}: {proc.stdout[:200]}"
    return st.get("written", {}).get("models") == 2, f"stats={proc.stdout[:200]}"


@check("fct_orders model page well-formed")
def c_model(wiki, proc):
    p = wiki / "_evidence/models/fct_orders.md"
    if not p.exists():
        return False, "missing fct_orders.md"
    t = p.read_text(encoding="utf-8")
    need = ["---", "unique_id: model.testproj.fct_orders", "type: model",
            "materialization: table", "path: dbt/models/marts/fct_orders.sql",
            "## Column Sources", "order_id ← stg_orders.order_id",
            "## Column Lineage Chains", "## Tests", "## Cross-references",
            "## Inline Comments", "orders fact"]
    miss = [s for s in need if s not in t]
    return not miss, f"missing tokens: {miss}"


@check("feeds_into reverse lookup on stg_orders")
def c_feeds(wiki, proc):
    t = (wiki / "_evidence/models/stg_orders.md").read_text(encoding="utf-8")
    return "fct_orders" in t.split("feeds_into:")[1][:200], "stg_orders.feeds_into missing fct_orders"


@check("source / macro / seed / singular-test pages emitted")
def c_others(wiki, proc):
    paths = {
        "source": wiki / "_evidence/sources/raw__orders_raw.md",
        "macro": wiki / "_evidence/macros/helper.md",
        "seed": wiki / "_evidence/seeds/seed_x.md",
        "test": wiki / "_evidence/tests/singular_check.md",
    }
    miss = [k for k, p in paths.items() if not p.exists()]
    if miss:
        return False, f"missing pages: {miss}"
    src = paths["source"].read_text(encoding="utf-8")
    mac = paths["macro"].read_text(encoding="utf-8")
    return ("stg_orders" in src and "stg_orders" in mac), "source/macro feeds_into/used_by wrong"


@check("index.md + lineage.md emitted with stats")
def c_index(wiki, proc):
    idx = wiki / "index.md"; lin = wiki / "lineage.md"
    if not idx.exists() or not lin.exists():
        return False, "index.md or lineage.md missing"
    it = idx.read_text(encoding="utf-8"); lt = lin.read_text(encoding="utf-8")
    return ("Total models: 2" in it and "Models: 2" in lt), "stats lines missing"


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as d:
        wiki, proc = run(Path(d))
        for i, (name, fn) in enumerate(CHECKS, 1):
            try:
                ok, msg = fn(wiki, proc)
            except Exception as e:
                ok, msg = False, f"exception: {e}"
            status = "OK  " if ok else "FAIL"
            print(f"[{i}/{len(CHECKS)}] {status} {name}")
            if not ok:
                print(f"         {msg}")
                failures += 1
    print(f"\n{len(CHECKS) - failures}/{len(CHECKS)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
