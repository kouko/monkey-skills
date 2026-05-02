#!/usr/bin/env python3
"""Extract column-level lineage from a compiled dbt SQL file using sqlglot.

dbt-wiki ships this script as a plugin asset. /dbt-wiki:init copies it to
.dbt-wiki/_internal/extract_column_lineage.py for the user's project.
The init/refresh skills invoke it once per model (or in batch mode) to
populate the `columns[].sources` field of model entity pages.

Usage
-----
Single file (preferred for incremental refresh):

    python3 extract_column_lineage.py <compiled_sql_file> [dialect]

Batch over a directory (preferred for first-time init):

    python3 extract_column_lineage.py --batch <compiled_dir> [dialect]

Output (stdout)
---------------
Single mode — JSON object:

    {
        "<output_column_name>": ["<table_or_alias>.<column>", ...],
        ...
    }

Batch mode — JSONL (one record per .sql file under <compiled_dir>):

    {"path": "models/staging/stg_orders.sql",
     "result": {"order_id": ["raw_orders.id"], ...}}
    {"path": "models/marts/fct_orders.sql",
     "result": {"customer_id": ["stg_orders.customer_id", "stg_customers.id"], ...}}

Errors are returned as a special "_error" key inside the result object so
that downstream tooling can keep going (one model failing doesn't kill
the whole init):

    {"_error": "parse failed: ParseError: ..."}

Dialect
-------
Defaults to "redshift" (most common in iCHEF-dbt-pipeline target). sqlglot
supports: redshift, postgres, snowflake, bigquery, databricks, duckdb,
clickhouse, mysql, oracle, spark, sqlite, tsql.

Implementation notes
--------------------
- We always parse `compiled/*.sql` (jinja already expanded by `dbt compile`).
  Do NOT pass raw_code (jinja-laden) to this script.
- We use `sqlglot.lineage.lineage(col_name, ast)` per output column, which
  handles CTEs, joins, set operations, and most aggregations correctly.
- Window functions / lateral joins / unresolved SELECT * may produce
  partial results; the failure mode is "fewer sources than ideal", not
  "wrong sources".
- For SELECT *, we fall back to listing the FROM-clause table names (no
  column-level expansion since we don't know the schema).
- Tested against sqlglot >= 25.0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import sqlglot
    from sqlglot import exp
    from sqlglot.lineage import lineage as sqlglot_lineage
except ImportError:
    print(json.dumps({"_error": "sqlglot not installed; run: pip install 'sqlglot>=25.0'"}))
    sys.exit(1)


def extract_lineage(sql: str, dialect: str = "redshift") -> dict[str, Any]:
    """Parse `sql` and return {output_col: [list of source.column refs]}.

    On failure, returns {"_error": "<reason>"}.
    """
    if not sql.strip():
        return {"_error": "empty SQL"}

    try:
        ast = sqlglot.parse_one(sql, dialect=dialect)
    except Exception as e:  # broad: sqlglot raises various error types
        return {"_error": f"parse failed: {type(e).__name__}: {str(e)[:300]}"}

    select = _find_top_select(ast)
    if select is None:
        return {"_error": "no top-level SELECT found (DDL? DML? CTE-only?)"}

    result: dict[str, Any] = {}
    for proj in select.expressions:
        out_name = _projection_output_name(proj)

        # SELECT * — can't resolve without schema; record as wildcard
        if isinstance(proj, exp.Star) or (
            isinstance(proj, exp.Column) and isinstance(proj.this, exp.Star)
        ):
            from_tables = _from_tables(select)
            result["*"] = [f"{t}.*" for t in from_tables] or ["<unresolved>"]
            continue

        try:
            node = sqlglot_lineage(out_name, ast, dialect=dialect)
            sources = _collect_leaf_refs(node)
        except Exception as e:
            # Lineage API failed for this column; fall back to direct
            # column refs in the projection expression
            sources = _collect_column_refs(
                proj.this if isinstance(proj, exp.Alias) else proj
            )
            if not sources:
                sources = [f"_lineage_failed: {type(e).__name__}"]

        result[out_name] = sorted(set(sources))

    return result


# ----- helpers -----


def _find_top_select(ast: exp.Expression) -> exp.Select | None:
    if isinstance(ast, exp.Select):
        return ast
    # Wrapped in WITH (CTEs) or set ops — find first Select
    found = ast.find(exp.Select)
    return found if isinstance(found, exp.Select) else None


def _projection_output_name(proj: exp.Expression) -> str:
    if isinstance(proj, exp.Alias):
        return proj.alias
    if isinstance(proj, exp.Column):
        return proj.alias_or_name
    # Function call / arithmetic without alias — use its string form, truncated
    name = proj.alias_or_name
    if name:
        return name
    return str(proj)[:40].strip().replace("\n", " ")


def _from_tables(select: exp.Select) -> list[str]:
    """Return alias_or_name for each Table in FROM/JOIN of `select`."""
    names: list[str] = []
    for tbl in select.find_all(exp.Table):
        # Only direct FROM/JOIN tables — skip those nested inside subqueries
        # of OTHER selects (find_all walks all descendants by default)
        parent = tbl.parent
        while parent is not None and not isinstance(parent, exp.Select):
            parent = parent.parent
        if parent is select:
            names.append(tbl.alias_or_name or tbl.name)
    return names


def _collect_leaf_refs(node) -> list[str]:
    """Walk sqlglot lineage Node tree; return ['table.column', ...] at leaves.

    sqlglot's lineage Node.name is already qualified (e.g. "t.a") when the
    leaf has source=exp.Table — we use it as-is to avoid double-prefixing.
    For non-Table leaves (rare; usually a Subquery sqlglot couldn't recurse),
    fall back to scanning Column references in the source expression.
    """
    if node is None:
        return []

    sources: list[str] = []

    if not getattr(node, "downstream", None):
        src = getattr(node, "source", None)
        name = node.name
        if isinstance(src, exp.Table):
            # name is already qualified ('t.a'); use directly. If for some
            # reason name is unqualified, fall back to source's table name.
            if "." in name:
                sources.append(name)
            else:
                table = src.alias_or_name or src.name
                sources.append(f"{table}.{name}")
        elif src is not None:
            # Source is a Subquery / Select that didn't recurse — best effort
            for col in src.find_all(exp.Column):
                t = col.table or "<unqualified>"
                sources.append(f"{t}.{col.name}")
        else:
            sources.append(name)
        return sources

    for child in node.downstream:
        sources.extend(_collect_leaf_refs(child))
    return sources


def _collect_column_refs(expr: exp.Expression | None) -> list[str]:
    """Fallback: list all Column references in the expression."""
    if expr is None:
        return []
    refs = []
    for col in expr.find_all(exp.Column):
        t = col.table or "<unqualified>"
        refs.append(f"{t}.{col.name}")
    return refs


# ----- CLI -----


def _run_single(path: str, dialect: str) -> int:
    try:
        sql = Path(path).read_text()
    except FileNotFoundError:
        print(json.dumps({"_error": f"file not found: {path}"}))
        return 1
    result = extract_lineage(sql, dialect)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if "_error" not in result else 2


def _run_batch(directory: str, dialect: str) -> int:
    root = Path(directory)
    if not root.is_dir():
        print(json.dumps({"_error": f"not a directory: {directory}"}))
        return 1
    failures = 0
    for sql_path in sorted(root.rglob("*.sql")):
        try:
            sql = sql_path.read_text()
            result = extract_lineage(sql, dialect)
        except Exception as e:
            result = {"_error": f"read/parse exception: {type(e).__name__}: {e}"}
        if "_error" in result:
            failures += 1
        print(
            json.dumps(
                {"path": str(sql_path.relative_to(root)), "result": result},
                sort_keys=True,
            )
        )
    return 0 if failures == 0 else 2


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if args[0] == "--batch":
        if len(args) < 2:
            print(json.dumps({"_error": "usage: --batch <dir> [dialect]"}))
            return 1
        return _run_batch(args[1], args[2] if len(args) > 2 else "redshift")
    return _run_single(args[0], args[1] if len(args) > 1 else "redshift")


if __name__ == "__main__":
    sys.exit(main())
