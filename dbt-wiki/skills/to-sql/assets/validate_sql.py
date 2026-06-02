#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["sqlglot>=25.0"]
# ///
"""Static SQL validator — parse-only, never executes SQL.

Parses a SQL string with sqlglot and returns:
  - the set of referenced table names
  - (table_or_alias, column) pairs found in column references
  - a dict mapping alias → real table name

Used by dbt-wiki:to-sql to validate NL2SQL output before it is shown
to the user. This module is a library; it has no CLI entry point.

Output schema
-------------
Success::

    {
        "ok": True,
        "tables": {"orders", "customers"},           # set of str — real table names
        "aliases": {"o": "orders", "c": "customers"},  # alias → real table name
        "columns": [("orders", "id"), ("customers", "name"), ...]  # list of (table, col)
    }

Parse error::

    {
        "ok": False,
        "error": "<human-readable parse error message>"
    }

Where a column reference cannot be tied to a specific table/alias,
the table slot is recorded as "?" rather than dropped.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import sqlglot
    from sqlglot import exp
except ImportError as _exc:
    raise ImportError(
        "sqlglot not installed; run: pip install 'sqlglot>=25.0'"
    ) from _exc


# ---------------------------------------------------------------------------
# extract_refs helpers
# ---------------------------------------------------------------------------

def _build_alias_map(ast: exp.Expression) -> dict[str, str]:
    """Return {alias: real_table_name} for every aliased Table in the AST."""
    alias_map: dict[str, str] = {}
    for tbl in ast.find_all(exp.Table):
        real_name = tbl.name
        alias = tbl.alias
        if alias and real_name and alias != real_name:
            alias_map[alias] = real_name
    return alias_map


def _build_select_default_table_map(
    ast: exp.Expression,
    alias_map: dict[str, str],
) -> dict[int, str | None]:
    """Map each Select node id → default table name for unqualified columns.

    A Select gets a default table only when it has exactly one FROM table
    and no JOINs.  The name stored is the real table name (alias resolved).
    """
    select_default: dict[int, str | None] = {}
    for sel in ast.find_all(exp.Select):
        from_clause = sel.args.get("from") or sel.args.get("from_")
        joins = sel.args.get("joins") or []
        if from_clause and not joins:
            from_tables = list(from_clause.find_all(exp.Table))
            if len(from_tables) == 1:
                raw = from_tables[0].alias_or_name or from_tables[0].name or None
                # resolve alias → real name
                resolved = alias_map.get(raw, raw) if raw else None
                select_default[id(sel)] = resolved
            else:
                select_default[id(sel)] = None
        else:
            select_default[id(sel)] = None
    return select_default


def _enclosing_select(node: exp.Expression) -> exp.Select | None:
    parent = node.parent
    while parent is not None:
        if isinstance(parent, exp.Select):
            return parent
        parent = parent.parent
    return None


def _build_select_output_aliases(ast: exp.Expression) -> dict[int, set[str]]:
    """Return {Select-node-id -> set of output alias names} for every Select.

    An output alias is the name given to a SELECT-list expression via AS
    (e.g. ``a / NULLIF(b, 0) AS delivery_share``).  A bare column reference
    in ORDER BY / GROUP BY / HAVING that matches one of these names is an
    *output reference*, not a table-column reference, and must not be
    collected as a column dependency.
    """
    result: dict[int, set[str]] = {}
    for sel in ast.find_all(exp.Select):
        aliases: set[str] = set()
        for projection in sel.expressions:
            if isinstance(projection, exp.Alias):
                alias_name = projection.alias
                if alias_name:
                    aliases.add(alias_name.lower())
        result[id(sel)] = aliases
    return result


def _collect_column_refs(
    ast: exp.Expression,
    alias_map: dict[str, str],
    select_default: dict[int, str | None],
    select_output_aliases: dict[int, set[str]],
    cte_names: set[str] | None = None,
) -> list[tuple[str, str]]:
    """Return deduped list of (real_table_or_sentinel, column_name) pairs.

    Unqualified column references that match a SELECT-list output alias of
    their enclosing Select are skipped — they are output references (legal in
    ORDER BY / GROUP BY / HAVING), not table-column dependencies.

    Columns qualified to a CTE name (e.g. ``ranked.col``) are also skipped —
    CTE names are query-internal, not manifest models.
    """
    if cte_names is None:
        cte_names = set()

    columns: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for col in ast.find_all(exp.Column):
        col_name = col.name or col.alias_or_name
        if not col_name:
            continue
        if col.table:
            # Explicitly qualified (e.g. t.col) — never an output alias ref.
            table_ref = alias_map.get(col.table, col.table)
            # Skip columns qualified to a CTE name — CTE output is
            # query-internal, not a manifest-checkable table.
            if table_ref.lower() in cte_names:
                continue
        else:
            sel = _enclosing_select(col)
            # Skip if this unqualified name is a SELECT-list output alias.
            if sel is not None:
                aliases = select_output_aliases.get(id(sel), set())
                if col_name.lower() in aliases:
                    continue
            table_ref = (
                select_default.get(id(sel)) if sel is not None else None
            ) or "?"
        pair = (table_ref, col_name)
        if pair not in seen:
            seen.add(pair)
            columns.append(pair)

    return columns


# ---------------------------------------------------------------------------
# Public: extract_refs
# ---------------------------------------------------------------------------

def extract_refs(sql: str, dialect: str | None = None) -> dict[str, Any]:
    """Parse *sql* and return referenced tables, aliases, and (table, column) pairs.

    Parameters
    ----------
    sql:
        SQL string to parse (may be any SELECT / DML). Never executed.
    dialect:
        sqlglot dialect name (e.g. "redshift", "snowflake"). ``None`` lets
        sqlglot use its generic parser, which handles most ANSI SQL.

    Returns
    -------
    dict with either:
      ``{"ok": True, "tables": set[str], "aliases": dict[str,str],
         "columns": list[tuple[str, str]]}``
      ``{"ok": False, "error": str}``
    """
    if not sql or not sql.strip():
        return {"ok": False, "error": "empty SQL"}

    try:
        ast = sqlglot.parse_one(sql, dialect=dialect)
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {str(exc)[:300]}"}

    if ast is None:
        return {"ok": False, "error": "sqlglot returned None (unparseable input)"}

    alias_map = _build_alias_map(ast)

    # Collect CTE names — these are query-internal relations, not physical tables.
    cte_names: set[str] = {
        cte.alias.lower()
        for cte in ast.find_all(exp.CTE)
        if cte.alias
    }

    # tables: use real names (resolve aliases for the table-name set);
    # exclude CTE names — they are not manifest models.
    tables: set[str] = set()
    for tbl in ast.find_all(exp.Table):
        name = tbl.name  # always the real table name (not alias)
        if name and name.lower() not in cte_names:
            tables.add(name)

    select_default = _build_select_default_table_map(ast, alias_map)
    select_output_aliases = _build_select_output_aliases(ast)
    columns = _collect_column_refs(
        ast, alias_map, select_default, select_output_aliases, cte_names
    )

    return {"ok": True, "tables": tables, "aliases": alias_map, "columns": columns}


# ---------------------------------------------------------------------------
# Public: check_refs_against_manifest
# ---------------------------------------------------------------------------

def _load_manifest_index(
    manifest_path: str,
) -> tuple[dict[str, set[str]], set[str]]:
    """Load manifest.json and return (model_columns, known_names).

    model_columns: {model_name -> set of column names}
    known_names:   flat set of all model names + relation_name aliases
    """
    with open(manifest_path) as f:
        manifest = json.load(f)

    model_columns: dict[str, set[str]] = {}
    known_names: set[str] = set()

    for node in manifest.get("nodes", {}).values():
        raw_name: str = node.get("name", "")
        if not raw_name:
            continue

        # Collect column names (lower-cased for case-insensitive match)
        col_set: set[str] = {
            c["name"].lower()
            for c in node.get("columns", {}).values()
            if c.get("name")
        }
        model_columns[raw_name.lower()] = col_set
        known_names.add(raw_name.lower())

        # Also register the relation_name alias (e.g. "public.orders" → "orders")
        relation_name: str = node.get("relation_name", "")
        if relation_name:
            # strip schema prefix if present: "schema.table" → "table"
            short = relation_name.split(".")[-1].strip('"').lower()
            known_names.add(short)
            if short not in model_columns:
                model_columns[short] = col_set

    return model_columns, known_names


def _enrich_with_catalog(
    model_columns: dict[str, set[str]],
    catalog_path: str,
) -> None:
    """Mutate model_columns in-place, adding catalog column names."""
    try:
        with open(catalog_path) as f:
            catalog = json.load(f)
    except (OSError, json.JSONDecodeError):
        return  # catalog is optional; skip silently on error

    for _node_id, node in catalog.get("nodes", {}).items():
        raw_name: str = (
            node.get("metadata", {}).get("name", "")
            or node.get("name", "")
        )
        if not raw_name:
            continue
        key = raw_name.lower()
        if key not in model_columns:
            model_columns[key] = set()
        for col_name in node.get("columns", {}).keys():
            model_columns[key].add(col_name.lower())


def check_refs_against_manifest(
    refs: dict[str, Any],
    manifest_path: str,
    catalog_path: str | None = None,
) -> dict[str, Any]:
    """Validate extract_refs output against manifest.json.

    Parameters
    ----------
    refs:
        Return value of ``extract_refs`` (must have ``ok: True``).
    manifest_path:
        Absolute or relative path to a dbt ``manifest.json``.
    catalog_path:
        Optional path to a dbt ``catalog.json``. If provided and the file
        exists, its column list enriches the known columns per model.

    Returns
    -------
    ``{"ok": bool, "missing_tables": list[str], "missing_columns": list[tuple[str,str]]}``

    ``ok`` is True only when both lists are empty. If the manifest cannot be
    loaded (missing file / malformed JSON), returns
    ``{"ok": False, "missing_tables": [], "missing_columns": [], "error": <msg>}``
    rather than raising — the validator always returns a structured result.
    """
    if not refs.get("ok"):
        return {
            "ok": False,
            "missing_tables": [],
            "missing_columns": [],
        }

    try:
        model_columns, known_names = _load_manifest_index(manifest_path)
    except (OSError, ValueError) as exc:  # ValueError covers json.JSONDecodeError
        return {
            "ok": False,
            "missing_tables": [],
            "missing_columns": [],
            "error": f"could not load manifest: {type(exc).__name__}: {str(exc)[:200]}",
        }

    if catalog_path and Path(catalog_path).exists():
        _enrich_with_catalog(model_columns, catalog_path)

    # Tables referenced in the SQL (real names — aliases already resolved by extract_refs)
    sql_tables: set[str] = {t.lower() for t in refs.get("tables", set())}
    missing_tables: list[str] = sorted(t for t in sql_tables if t not in known_names)

    # Column refs — only check columns on tables that ARE in the manifest
    missing_columns: list[tuple[str, str]] = []
    for table_ref, col_name in refs.get("columns", []):
        if table_ref == "?":
            continue  # cannot resolve table → skip
        tbl_key = table_ref.lower()
        col_key = col_name.lower()
        if tbl_key not in known_names:
            continue  # already captured as missing_table
        col_set = model_columns.get(tbl_key, set())
        if col_set and col_key not in col_set:
            missing_columns.append((table_ref, col_name))

    ok = not missing_tables and not missing_columns
    return {
        "ok": ok,
        "missing_tables": missing_tables,
        "missing_columns": missing_columns,
    }
