#!/usr/bin/env python3
"""Smoke test for validate_sql.py.

Run from repo root or this directory:

    python3 dbt-wiki/skills/to-sql/assets/validate_sql_test.py

Exits 0 if all cases pass; non-zero with a per-case FAIL line otherwise.
Doesn't require pytest — pure stdlib + sqlglot.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Allow running from repo root or from this directory
sys.path.insert(0, str(Path(__file__).parent))

from validate_sql import check_refs_against_manifest, extract_refs  # noqa: E402


# Each entry: (name: str, fn: () -> tuple[bool, str])
CASES: list[tuple[str, object]] = []


def case(name: str):
    """Decorator: append (name, fn) to CASES."""
    def decorator(fn):
        CASES.append((name, fn))
        return fn
    return decorator


# ---------------------------------------------------------------------------
# Case 1: clean single-table SELECT
# ---------------------------------------------------------------------------
@case("single-table SELECT")
def _case_single_table():
    result = extract_refs("SELECT a, b FROM t")
    if not result.get("ok"):
        return False, f"expected ok=True, got: {result}"
    tables = result.get("tables", set())
    if "t" not in tables:
        return False, f"expected 't' in tables, got: {tables}"
    columns = result.get("columns", [])
    col_set = set(columns)
    expected = {("t", "a"), ("t", "b")}
    missing = expected - col_set
    if missing:
        return False, f"missing columns {missing}; got columns: {col_set}"
    return True, "ok"


# ---------------------------------------------------------------------------
# Case 2: two-table JOIN
# ---------------------------------------------------------------------------
@case("two-table JOIN")
def _case_two_table_join():
    sql = """
        SELECT o.id, c.name
        FROM orders o JOIN customers c ON o.customer_id = c.id
    """
    result = extract_refs(sql)
    if not result.get("ok"):
        return False, f"expected ok=True, got: {result}"
    tables = result.get("tables", set())
    # `tables` MUST hold the real model names, not the SQL aliases —
    # check_refs_against_manifest looks these up against manifest-registered
    # model names, so an alias here ('o'/'c') would break manifest validation.
    if tables != {"orders", "customers"}:
        return False, (
            f"expected tables == {{orders, customers}} (real names, not aliases), "
            f"got: {tables}"
        )
    return True, "ok"


# ---------------------------------------------------------------------------
# Case 3: malformed SQL
# ---------------------------------------------------------------------------
@case("malformed SQL returns ok=False")
def _case_malformed():
    result = extract_refs("SELEKT FROM")
    if result.get("ok", True):
        return False, f"expected ok=False for malformed SQL, got: {result}"
    if "error" not in result:
        return False, f"expected 'error' key in result, got: {result}"
    return True, "ok"


# ---------------------------------------------------------------------------
# Helpers: build a synthetic manifest.json for tests 4-8
# ---------------------------------------------------------------------------

_SYNTHETIC_MANIFEST = {
    "nodes": {
        "model.proj.orders": {
            "unique_id": "model.proj.orders",
            "name": "orders",
            "relation_name": "public.orders",
            "schema": "public",
            "columns": {
                "id": {"name": "id"},
                "customer_id": {"name": "customer_id"},
                "amount": {"name": "amount"},
            },
        },
        "model.proj.customers": {
            "unique_id": "model.proj.customers",
            "name": "customers",
            "relation_name": "public.customers",
            "schema": "public",
            "columns": {
                "id": {"name": "id"},
                "name": {"name": "name"},
            },
        },
    }
}


def _write_manifest(tmp_dir: str) -> str:
    """Write _SYNTHETIC_MANIFEST to a tmp file and return its path."""
    path = str(Path(tmp_dir) / "manifest.json")
    with open(path, "w") as f:
        json.dump(_SYNTHETIC_MANIFEST, f)
    return path


# ---------------------------------------------------------------------------
# Case 4: SQL referencing existing model.column → ok: True, no missing
# ---------------------------------------------------------------------------
@case("manifest check — existing table.column → ok")
def _case_manifest_ok():
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_manifest(tmp)
        sql = "SELECT id, customer_id FROM orders"
        refs = extract_refs(sql)
        if not refs.get("ok"):
            return False, f"extract_refs failed: {refs}"
        result = check_refs_against_manifest(refs, manifest_path)
        if not result.get("ok"):
            return False, (
                f"expected ok=True; missing_tables={result.get('missing_tables')}, "
                f"missing_columns={result.get('missing_columns')}"
            )
        if result.get("missing_tables") or result.get("missing_columns"):
            return False, f"unexpected missing items: {result}"
        return True, "ok"


# ---------------------------------------------------------------------------
# Case 5: SQL referencing nonexistent column on existing model → missing_columns
# ---------------------------------------------------------------------------
@case("manifest check — bad column → missing_columns")
def _case_manifest_bad_column():
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_manifest(tmp)
        sql = "SELECT nonexistent_col FROM orders"
        refs = extract_refs(sql)
        if not refs.get("ok"):
            return False, f"extract_refs failed: {refs}"
        result = check_refs_against_manifest(refs, manifest_path)
        if result.get("ok"):
            return False, f"expected ok=False when column missing; got: {result}"
        mc = result.get("missing_columns", [])
        if not mc:
            return False, f"expected missing_columns to be non-empty; got: {result}"
        if ("orders", "nonexistent_col") not in mc:
            return False, f"expected ('orders', 'nonexistent_col') in missing_columns; got: {mc}"
        return True, "ok"


# ---------------------------------------------------------------------------
# Case 6: SQL referencing nonexistent table → missing_tables
# ---------------------------------------------------------------------------
@case("manifest check — bad table → missing_tables")
def _case_manifest_bad_table():
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_manifest(tmp)
        sql = "SELECT id FROM ghost_table"
        refs = extract_refs(sql)
        if not refs.get("ok"):
            return False, f"extract_refs failed: {refs}"
        result = check_refs_against_manifest(refs, manifest_path)
        if result.get("ok"):
            return False, f"expected ok=False when table missing; got: {result}"
        mt = result.get("missing_tables", [])
        if "ghost_table" not in mt:
            return False, f"expected 'ghost_table' in missing_tables; got: {mt}"
        return True, "ok"


# ---------------------------------------------------------------------------
# Case 7: JOIN with table aliases; both real models exist → aliases resolved, ok
# ---------------------------------------------------------------------------
@case("manifest check — JOIN aliases resolved → ok")
def _case_manifest_alias_join():
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_manifest(tmp)
        sql = """
            SELECT o.id, o.customer_id, c.name
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
        """
        refs = extract_refs(sql)
        if not refs.get("ok"):
            return False, f"extract_refs failed: {refs}"
        # Verify that extract_refs now returns an aliases dict
        if "aliases" not in refs:
            return False, "expected 'aliases' key in extract_refs result"
        aliases = refs["aliases"]
        if aliases.get("o") != "orders" or aliases.get("c") != "customers":
            return False, f"expected {{o->orders, c->customers}} in aliases; got: {aliases}"
        result = check_refs_against_manifest(refs, manifest_path)
        if not result.get("ok"):
            return False, (
                f"expected ok=True after alias resolution; "
                f"missing_tables={result.get('missing_tables')}, "
                f"missing_columns={result.get('missing_columns')}"
            )
        return True, "ok"


# ---------------------------------------------------------------------------
# Case 8: extract_refs returns 'aliases' key (regression guard post-refactor)
# ---------------------------------------------------------------------------
@case("extract_refs includes aliases key after refactor")
def _case_extract_refs_aliases_key():
    sql = "SELECT a.x FROM alpha a JOIN beta b ON a.id = b.id"
    result = extract_refs(sql)
    if not result.get("ok"):
        return False, f"expected ok=True; got: {result}"
    if "aliases" not in result:
        return False, f"expected 'aliases' key; got keys: {list(result.keys())}"
    aliases = result["aliases"]
    if aliases.get("a") != "alpha" or aliases.get("b") != "beta":
        return False, f"expected {{a->alpha, b->beta}}; got: {aliases}"
    return True, "ok"


# ---------------------------------------------------------------------------
# Case 9: missing/malformed manifest → structured {ok: False, error}, no raise
# ---------------------------------------------------------------------------
@case("manifest check — missing manifest returns structured error, not raise")
def _case_manifest_missing():
    refs = extract_refs("SELECT id FROM orders")
    if not refs.get("ok"):
        return False, f"extract_refs failed: {refs}"
    # Point at a path that does not exist — must NOT raise.
    result = check_refs_against_manifest(refs, "/nonexistent/manifest.json")
    if result.get("ok") is not False:
        return False, f"expected ok=False on missing manifest; got: {result}"
    if "error" not in result:
        return False, f"expected 'error' key on load failure; got keys: {list(result.keys())}"
    return True, "ok"


# ---------------------------------------------------------------------------
# Case 10: SELECT alias in ORDER BY must NOT be reported as missing column
# ---------------------------------------------------------------------------

_MANIFEST_WITH_MEASURE = {
    "nodes": {
        "model.proj.fct_account_monthly": {
            "unique_id": "model.proj.fct_account_monthly",
            "name": "fct_account_monthly",
            "relation_name": "public.fct_account_monthly",
            "schema": "public",
            "columns": {
                "account_id": {"name": "account_id"},
                "report_month": {"name": "report_month"},
                "a": {"name": "a"},
                "b": {"name": "b"},
            },
        }
    }
}


def _write_measure_manifest(tmp_dir: str) -> str:
    path = str(Path(tmp_dir) / "manifest.json")
    with open(path, "w") as f:
        json.dump(_MANIFEST_WITH_MEASURE, f)
    return path


@case("select alias in ORDER BY is NOT a missing column (false-positive fix)")
def _case_select_alias_order_by():
    """delivery_share is a SELECT alias; ORDER BY delivery_share must not flag it."""
    sql = """
        SELECT account_id,
               a / NULLIF(b, 0) AS delivery_share
        FROM fct_account_monthly
        WHERE report_month = date_trunc('month', CURRENT_DATE) - interval '1 month'
        ORDER BY delivery_share DESC
    """
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_measure_manifest(tmp)
        refs = extract_refs(sql)
        if not refs.get("ok"):
            return False, f"extract_refs failed: {refs}"
        result = check_refs_against_manifest(refs, manifest_path)
        if not result.get("ok"):
            return False, (
                f"expected ok=True — delivery_share is a SELECT alias, not a table col; "
                f"missing_columns={result.get('missing_columns')}"
            )
        return True, "ok"


# ---------------------------------------------------------------------------
# Case 11: truly missing unqualified column still flags (guard against over-suppression)
# ---------------------------------------------------------------------------
@case("truly missing column not in select aliases still flags")
def _case_missing_col_not_suppressed():
    """ghost_col is not a SELECT alias and not in the manifest — must still flag."""
    sql = "SELECT account_id FROM fct_account_monthly ORDER BY ghost_col"
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_measure_manifest(tmp)
        refs = extract_refs(sql)
        if not refs.get("ok"):
            return False, f"extract_refs failed: {refs}"
        result = check_refs_against_manifest(refs, manifest_path)
        if result.get("ok"):
            return False, f"expected ok=False for ghost_col not in manifest; got: {result}"
        mc = result.get("missing_columns", [])
        found = any(col == "ghost_col" for _, col in mc)
        if not found:
            return False, f"expected ghost_col in missing_columns; got: {mc}"
        return True, "ok"


# ---------------------------------------------------------------------------
# Case 12: CTE name must NOT appear in missing_tables; real inner tables must
# ---------------------------------------------------------------------------

_MANIFEST_WITH_MEASURE_AND_DIM = {
    "nodes": {
        "model.proj.measure": {
            "unique_id": "model.proj.measure",
            "name": "measure",
            "relation_name": "public.measure",
            "schema": "public",
            "columns": {
                "account_id": {"name": "account_id"},
                "x": {"name": "x"},
            },
        },
        "model.proj.dim": {
            "unique_id": "model.proj.dim",
            "name": "dim",
            "relation_name": "public.dim",
            "schema": "public",
            "columns": {
                "account_id": {"name": "account_id"},
                "region": {"name": "region"},
            },
        },
    }
}


def _write_measure_dim_manifest(tmp_dir: str) -> str:
    path = str(Path(tmp_dir) / "manifest.json")
    with open(path, "w") as f:
        json.dump(_MANIFEST_WITH_MEASURE_AND_DIM, f)
    return path


@case("CTE name excluded from tables; real inner tables still collected")
def _case_cte_name_excluded():
    """ranked is a CTE — outer FROM ranked must NOT flag as missing_table.
    measure and dim (referenced inside the CTE body) MUST still be in tables.
    """
    sql = """
        WITH ranked AS (
            SELECT d.region, m.account_id, m.x AS plan_mrr,
                   ROW_NUMBER() OVER (PARTITION BY d.region ORDER BY m.x DESC) AS rn
            FROM measure m JOIN dim d ON m.account_id = d.account_id
        )
        SELECT region, account_id, plan_mrr FROM ranked WHERE rn <= 3 ORDER BY region
    """
    # Part A: extract_refs must NOT include 'ranked' in tables
    refs = extract_refs(sql)
    if not refs.get("ok"):
        return False, f"extract_refs failed: {refs}"
    tables = refs.get("tables", set())
    if "ranked" in tables:
        return False, f"CTE name 'ranked' must not be in tables; got: {tables}"
    # Part B: real inner models must still be collected
    for real_model in ("measure", "dim"):
        if real_model not in tables:
            return False, f"inner table '{real_model}' missing from tables; got: {tables}"
    # Part C: manifest check must pass (no missing_tables)
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_measure_dim_manifest(tmp)
        result = check_refs_against_manifest(refs, manifest_path)
        if not result.get("ok"):
            return False, (
                f"expected ok=True — CTE is query-internal; "
                f"missing_tables={result.get('missing_tables')}, "
                f"missing_columns={result.get('missing_columns')}"
            )
    return True, "ok"


# ---------------------------------------------------------------------------
# SQL-internal-names class regression lock (cases 13-16)
# These characterize already-correct behavior (Feathers Ch.13 characterization
# tests). No production code change — they pass immediately and prevent future
# regressions where SQL-internal names (CTE names, derived-table aliases) could
# be false-flagged as missing against the manifest.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Case 13: CTE name must NOT appear in tables when used in a JOIN; real tables
# referenced inside the CTE body MUST be in tables.
# ---------------------------------------------------------------------------
@case("SQL-internal-names: CTE used in JOIN is NOT a table")
def _case_cte_in_join():
    """c is a CTE — JOIN c must not add 'c' to tables; orders and customers must be."""
    sql = (
        "WITH c AS (SELECT id, customer_id FROM orders) "
        "SELECT cu.name FROM customers cu JOIN c ON cu.id = c.customer_id"
    )
    refs = extract_refs(sql)
    if not refs.get("ok"):
        return False, f"extract_refs failed: {refs}"
    tables = refs.get("tables", set())
    if "c" in tables:
        return False, f"CTE name 'c' must not be in tables; got: {tables}"
    for real in ("orders", "customers"):
        if real not in tables:
            return False, f"real table '{real}' missing from tables; got: {tables}"
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_manifest(tmp)
        result = check_refs_against_manifest(refs, manifest_path)
        if not result.get("ok"):
            return False, (
                f"expected ok=True — 'c' is a CTE, not a physical table; "
                f"missing_tables={result.get('missing_tables')}, "
                f"missing_columns={result.get('missing_columns')}"
            )
    return True, "ok"


# ---------------------------------------------------------------------------
# Case 14: multi-CTE where a later CTE references an earlier CTE; only the
# physical table (orders) must appear in tables, not c1 or c2.
# ---------------------------------------------------------------------------
@case("SQL-internal-names: multi-CTE referencing earlier CTE — only physical table collected")
def _case_multi_cte_self_ref():
    """c1 and c2 are CTEs; only orders is a physical model."""
    sql = (
        "WITH c1 AS (SELECT id FROM orders), "
        "c2 AS (SELECT id FROM c1) "
        "SELECT c2.id FROM c2"
    )
    refs = extract_refs(sql)
    if not refs.get("ok"):
        return False, f"extract_refs failed: {refs}"
    tables = refs.get("tables", set())
    if "c1" in tables:
        return False, f"CTE name 'c1' must not be in tables; got: {tables}"
    if "c2" in tables:
        return False, f"CTE name 'c2' must not be in tables; got: {tables}"
    if "orders" not in tables:
        return False, f"real table 'orders' missing from tables; got: {tables}"
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_manifest(tmp)
        result = check_refs_against_manifest(refs, manifest_path)
        if not result.get("ok"):
            return False, (
                f"expected ok=True — c1/c2 are CTEs; "
                f"missing_tables={result.get('missing_tables')}, "
                f"missing_columns={result.get('missing_columns')}"
            )
    return True, "ok"


# ---------------------------------------------------------------------------
# Case 15: nested subquery / derived table in FROM — internal aliases (t, inq)
# must NOT appear in tables; only the physical table (orders) must.
# ---------------------------------------------------------------------------
@case("SQL-internal-names: nested derived-table aliases NOT in tables")
def _case_nested_derived_table():
    """t and inq are derived-table aliases — must not appear in tables."""
    sql = "SELECT t.id FROM (SELECT id FROM (SELECT id FROM orders) inq) t"
    refs = extract_refs(sql)
    if not refs.get("ok"):
        return False, f"extract_refs failed: {refs}"
    tables = refs.get("tables", set())
    if "t" in tables:
        return False, f"derived-table alias 't' must not be in tables; got: {tables}"
    if "inq" in tables:
        return False, f"derived-table alias 'inq' must not be in tables; got: {tables}"
    if "orders" not in tables:
        return False, f"real table 'orders' missing from tables; got: {tables}"
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_manifest(tmp)
        result = check_refs_against_manifest(refs, manifest_path)
        if not result.get("ok"):
            return False, (
                f"expected ok=True — t/inq are derived-table aliases; "
                f"missing_tables={result.get('missing_tables')}, "
                f"missing_columns={result.get('missing_columns')}"
            )
    return True, "ok"


# ---------------------------------------------------------------------------
# Case 16: subquery in WHERE (IN) — both outer and inner physical tables must
# be collected; no internal aliases created.
# ---------------------------------------------------------------------------
@case("SQL-internal-names: subquery in WHERE IN — both physical tables collected")
def _case_subquery_in_where():
    """orders and customers are both physical models referenced here."""
    sql = "SELECT id FROM orders WHERE customer_id IN (SELECT id FROM customers)"
    refs = extract_refs(sql)
    if not refs.get("ok"):
        return False, f"extract_refs failed: {refs}"
    tables = refs.get("tables", set())
    for real in ("orders", "customers"):
        if real not in tables:
            return False, f"real table '{real}' missing from tables; got: {tables}"
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = _write_manifest(tmp)
        result = check_refs_against_manifest(refs, manifest_path)
        if not result.get("ok"):
            return False, (
                f"expected ok=True; "
                f"missing_tables={result.get('missing_tables')}, "
                f"missing_columns={result.get('missing_columns')}"
            )
    return True, "ok"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main() -> int:
    failures = 0
    for name, fn in CASES:
        try:
            ok, msg = fn()
        except Exception as exc:
            ok, msg = False, f"exception: {exc}"
        status = "OK  " if ok else "FAIL"
        print(f"[{CASES.index((name, fn)) + 1}/{len(CASES)}] {status} {name}")
        if not ok:
            print(f"         {msg}")
            failures += 1
    print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
