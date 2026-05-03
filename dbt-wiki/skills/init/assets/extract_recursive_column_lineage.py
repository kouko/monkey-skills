#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Recursive column-level lineage extractor — walks dbt DAG bidirectionally.

Pure stdlib; no third-party deps. PEP 723 block included for consistency
with other dbt-wiki scripts (so `uv run` works identically across all).

dbt-wiki ships this script as a plugin asset. It consumes the per-SQL
column lineage produced by extract_column_lineage.py (in JSONL --batch
mode) PLUS the dbt manifest, and produces full ancestor + descendant
chains for any (model, column) pair.

This is the "Canva-style" recursive lineage Canva-public/dbt-column-
lineage-extractor does, but implemented inside dbt-wiki without a third-
party pip dependency. Same sqlglot-based per-SQL lineage underneath.

Pure stdlib — no third-party deps.

Usage
-----
Whole project (one record per (model, column) — default):

    python3 extract_recursive_column_lineage.py \\
        --manifest target/manifest.json \\
        --lineage /tmp/dbt-wiki-col-lineage.jsonl \\
        > /tmp/dbt-wiki-recursive-lineage.jsonl

Single (model, column) target:

    python3 extract_recursive_column_lineage.py \\
        --manifest target/manifest.json \\
        --lineage /tmp/dbt-wiki-col-lineage.jsonl \\
        --model model.iCHEF.fct_orders \\
        --column customer_id

Output (JSONL — one record per target column)
---------------------------------------------
    {
        "model_uid": "model.iCHEF.fct_orders",
        "column": "customer_id",
        "ancestors": {
            "model.iCHEF.stg_orders::customer_id": {
                "source.iCHEF.raw.orders_raw::customer_id": {}
            },
            "model.iCHEF.stg_customers::id": {
                "_unresolved::dbt_dim.customers::id": {}
            }
        },
        "descendants": {
            "model.iCHEF.dim_orders_summary::customer_id": {
                "model.iCHEF.mart_finance_daily::customer_id": {}
            }
        }
    }

Tree node keys
- `<unique_id>::<column>` — resolved upstream/downstream model + column
- `_unresolved::<table_or_alias>::<column>` — sqlglot reported a table
  name we couldn't map back to a manifest node (CTE, SQL alias not
  back-resolved, dbt_dev schema clash, etc.). Recursion stops here.
- `_cycle` / `_max_depth` — protection markers; stops recursion

Limitations (v1.0)
------------------
- SQL-local aliases (`SELECT f.a FROM stg_orders AS f`) require sqlglot
  to back-resolve `f` → `stg_orders` in its lineage output. If sqlglot
  emits `f.a` literally, we mark `_unresolved::f::a` and stop.
- CTEs in compiled SQL are similar — unless sqlglot's lineage walks
  through them to the base table, we mark unresolved.
- Cross-package macros that generate SQL referring to non-manifest
  tables (e.g. dbt_utils macros doing dynamic SQL) — best effort only.
- max_depth defaults to 10; configurable via --max-depth.

For Redshift specifically: late-binding views (`WITH NO SCHEMA BINDING`)
parse as standard SELECTs, so they work.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ----- alias map: build the lookup from "name as it might appear in
#       compiled SQL" → list of manifest unique_ids -----


def build_alias_map(manifest: dict) -> dict[str, list[str]]:
    """For each model / seed / snapshot / source in manifest, register
    every plausible reference form a downstream's compiled SQL might use.

    Compiled dbt SQL typically uses `database.schema.alias` (fully
    qualified) but sqlglot lineage may emit just the table name or its
    alias. We register all common forms so we can match either way.
    """
    alias_map: dict[str, list[str]] = {}

    def add(key: str | None, uid: str) -> None:
        if not key:
            return
        if uid not in alias_map.setdefault(key, []):
            alias_map[key].append(uid)

    for uid, node in manifest.get("nodes", {}).items():
        if node.get("resource_type") not in ("model", "seed", "snapshot"):
            continue
        name = node["name"]
        alias = node.get("alias") or name
        schema = node.get("schema") or ""
        db = node.get("database") or ""
        # Variants — most specific to least
        for key in {
            name,
            alias,
            f"{schema}.{alias}" if schema else None,
            f"{schema}.{name}" if schema else None,
            f"{db}.{schema}.{alias}" if db and schema else None,
            f"{db}.{schema}.{name}" if db and schema else None,
        }:
            add(key, uid)

    for uid, src in manifest.get("sources", {}).items():
        name = src.get("name")
        identifier = src.get("identifier") or name
        schema = src.get("schema") or ""
        db = src.get("database") or ""
        source_name = src.get("source_name") or ""
        for key in {
            name,
            identifier,
            f"{source_name}.{name}" if source_name else None,
            f"{schema}.{identifier}" if schema else None,
            f"{schema}.{name}" if schema else None,
            f"{db}.{schema}.{identifier}" if db and schema else None,
        }:
            add(key, uid)

    return alias_map


# ----- feeds_into reverse map: uid → [downstream uids] -----


def build_feeds_into(manifest: dict) -> dict[str, list[str]]:
    feeds_into: dict[str, list[str]] = {}
    for uid, node in manifest.get("nodes", {}).items():
        if node.get("resource_type") not in ("model", "snapshot"):
            continue
        for dep in node.get("depends_on", {}).get("nodes", []):
            feeds_into.setdefault(dep, []).append(uid)
    return feeds_into


# ----- per-SQL lineage lookup: uid → {output_col: [source_strs]} -----


def build_lineage_by_uid(
    lineage_jsonl_path: str, manifest: dict
) -> dict[str, dict[str, list[str]]]:
    """Read JSONL output of extract_column_lineage.py --batch and key by
    manifest unique_id (rather than file path).

    The JSONL records are keyed by relative path under target/compiled/
    (e.g. "models/marts/fct_orders.sql"). We map back to unique_id by
    matching against manifest['nodes'][*]['original_file_path'].
    """
    path_to_uid = {
        node.get("original_file_path"): uid
        for uid, node in manifest.get("nodes", {}).items()
        if node.get("resource_type") in ("model", "seed", "snapshot")
        and node.get("original_file_path")
    }

    out: dict[str, dict[str, list[str]]] = {}
    with open(lineage_jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            path = rec.get("path", "")
            result = rec.get("result", {})
            if isinstance(result, dict) and "_error" in result:
                continue
            # Match path against manifest's original_file_path
            uid = path_to_uid.get(path)
            if not uid:
                # Try suffix match (path may be relative differently)
                for op, candidate_uid in path_to_uid.items():
                    if op.endswith(path) or path.endswith(op):
                        uid = candidate_uid
                        break
            if uid:
                out[uid] = result
    return out


# ----- recursive ancestor walker -----


def find_ancestors(
    uid: str,
    col: str,
    lineage_by_uid: dict[str, dict[str, list[str]]],
    alias_map: dict[str, list[str]],
    visited: set[tuple[str, str]] | None = None,
    max_depth: int = 10,
) -> dict[str, Any]:
    if visited is None:
        visited = set()
    if (uid, col) in visited:
        return {"_cycle": True}
    if len(visited) >= max_depth:
        return {"_max_depth": True}
    visited = visited | {(uid, col)}

    sources = lineage_by_uid.get(uid, {}).get(col, [])
    if not sources:
        return {}  # leaf — no further upstream

    result: dict[str, Any] = {}
    for src in sources:
        if "." not in src:
            # Unqualified — mark as unresolved
            result[f"_unresolved::?::{src}"] = {}
            continue
        # rsplit because schema.table.col → ("schema.table", "col")
        table, src_col = src.rsplit(".", 1)

        # Try most-specific match first (strip leading "_unresolved" markers etc.)
        upstream_uids = alias_map.get(table, [])
        if not upstream_uids:
            # Try just the last component (handles "schema.table" → "table")
            short = table.rsplit(".", 1)[-1] if "." in table else table
            upstream_uids = alias_map.get(short, [])

        if not upstream_uids:
            result[f"_unresolved::{table}::{src_col}"] = {}
            continue

        # If multiple uids match (rare — ambiguous name), recurse into each
        for upstream_uid in upstream_uids:
            key = f"{upstream_uid}::{src_col}"
            sub = find_ancestors(
                upstream_uid, src_col, lineage_by_uid, alias_map, visited, max_depth
            )
            result[key] = sub

    return result


# ----- recursive descendant walker -----


def find_descendants(
    uid: str,
    col: str,
    lineage_by_uid: dict[str, dict[str, list[str]]],
    alias_map: dict[str, list[str]],
    feeds_into: dict[str, list[str]],
    manifest: dict,
    visited: set[tuple[str, str]] | None = None,
    max_depth: int = 10,
) -> dict[str, Any]:
    if visited is None:
        visited = set()
    if (uid, col) in visited:
        return {"_cycle": True}
    if len(visited) >= max_depth:
        return {"_max_depth": True}
    visited = visited | {(uid, col)}

    # Get this node's possible reference names (so we can check if a
    # downstream's per-SQL sources point back at us).
    node = manifest.get("nodes", {}).get(uid) or manifest.get("sources", {}).get(uid)
    if not node:
        return {}
    candidate_names = {node.get("name", "")}
    if node.get("alias"):
        candidate_names.add(node["alias"])
    if node.get("identifier"):
        candidate_names.add(node["identifier"])

    result: dict[str, Any] = {}
    for downstream_uid in feeds_into.get(uid, []):
        ds_lineage = lineage_by_uid.get(downstream_uid, {})
        for ds_col, sources in ds_lineage.items():
            for src in sources:
                if "." not in src:
                    continue
                table, src_col = src.rsplit(".", 1)
                # Match: src_col == our col AND table is one of our names
                short_table = table.rsplit(".", 1)[-1] if "." in table else table
                if src_col == col and (
                    table in candidate_names or short_table in candidate_names
                ):
                    key = f"{downstream_uid}::{ds_col}"
                    if key not in result:
                        result[key] = find_descendants(
                            downstream_uid,
                            ds_col,
                            lineage_by_uid,
                            alias_map,
                            feeds_into,
                            manifest,
                            visited,
                            max_depth,
                        )
                    break  # one match per downstream column is enough
    return result


# ----- CLI -----


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--manifest", required=True, help="Path to target/manifest.json")
    p.add_argument(
        "--lineage",
        required=True,
        help="Path to per-SQL lineage JSONL (output of extract_column_lineage.py --batch)",
    )
    p.add_argument(
        "--model", help="Single model unique_id (default: process all models)"
    )
    p.add_argument(
        "--column", help="Single column name (only valid with --model)"
    )
    p.add_argument(
        "--max-depth", type=int, default=10, help="Recursion depth limit (default 10)"
    )
    args = p.parse_args()

    if args.column and not args.model:
        print("--column requires --model", file=sys.stderr)
        return 2

    try:
        manifest = json.loads(Path(args.manifest).read_text())
    except FileNotFoundError:
        print(f"Manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    alias_map = build_alias_map(manifest)
    feeds_into = build_feeds_into(manifest)
    lineage_by_uid = build_lineage_by_uid(args.lineage, manifest)

    targets: list[tuple[str, str]] = []
    if args.model and args.column:
        targets = [(args.model, args.column)]
    elif args.model:
        # All columns for this model from per-SQL lineage
        for col in lineage_by_uid.get(args.model, {}):
            targets.append((args.model, col))
    else:
        # Whole project
        for uid, cols in lineage_by_uid.items():
            for col in cols:
                targets.append((uid, col))

    for uid, col in targets:
        ancestors = find_ancestors(
            uid, col, lineage_by_uid, alias_map, max_depth=args.max_depth
        )
        descendants = find_descendants(
            uid, col, lineage_by_uid, alias_map, feeds_into, manifest, max_depth=args.max_depth
        )
        record = {
            "model_uid": uid,
            "column": col,
            "ancestors": ancestors,
            "descendants": descendants,
        }
        print(json.dumps(record, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
