#!/usr/bin/env python3
"""Smoke test for extract_column_lineage.py.

Run from this directory:

    python3 extract_column_lineage_test.py

Exits 0 if all cases pass; non-zero with a per-case FAIL line otherwise.
Doesn't require pytest — pure stdlib + sqlglot.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent / "extract_column_lineage.py"

# (sql, dialect, expected_subset)
# expected_subset = dict where each value is a set of expected source refs;
# we assert "expected ⊆ actual" rather than equality so harmless extras
# (e.g. function names sqlglot reports) don't break the test.
CASES = [
    # 1. Trivial select
    (
        "SELECT a, b FROM t",
        "redshift",
        {"a": {"t.a"}, "b": {"t.b"}},
    ),
    # 2. Aliased
    (
        "SELECT a AS x FROM t",
        "redshift",
        {"x": {"t.a"}},
    ),
    # 3. Arithmetic — multiple column refs in one projection
    (
        "SELECT a + b AS c FROM t",
        "redshift",
        {"c": {"t.a", "t.b"}},
    ),
    # 4. JOIN — preserves table aliasing
    (
        """
        SELECT t1.a, t2.b
        FROM t1 JOIN t2 ON t1.id = t2.id
        """,
        "redshift",
        {"a": {"t1.a"}, "b": {"t2.b"}},
    ),
    # 5. CTE — should resolve through the CTE back to base table
    (
        """
        WITH cte AS (SELECT a FROM t)
        SELECT a FROM cte
        """,
        "redshift",
        {"a": {"t.a"}},
    ),
    # 6. COALESCE — multi-source
    (
        """
        SELECT COALESCE(t1.email, t2.email) AS contact_email
        FROM t1 LEFT JOIN t2 ON t1.id = t2.id
        """,
        "redshift",
        {"contact_email": {"t1.email", "t2.email"}},
    ),
    # 7. Snowflake dialect (sanity check that dialect arg works)
    (
        "SELECT a, b FROM t",
        "snowflake",
        {"a": {"t.a"}, "b": {"t.b"}},
    ),
    # 8. dbt `SELECT * FROM final` wrapper pattern — must unwrap to real columns
    # (very common in example-style dbt projects; v1.2.0 added this fallback).
    (
        """
        WITH staging AS (SELECT raw_id, raw_name FROM raw_t),
             final AS (
                 SELECT raw_id AS id, UPPER(raw_name) AS name
                 FROM staging
             )
        SELECT * FROM final
        """,
        "redshift",
        {"id": {"staging.raw_id"}, "name": {"staging.raw_name"}},
    ),
    # 9. Nested wrapper — `SELECT * FROM cte_a` where cte_a is `SELECT * FROM cte_b`.
    # Should drill down to cte_b's projections.
    (
        """
        WITH cte_b AS (SELECT col1, col2 FROM base_table),
             cte_a AS (SELECT * FROM cte_b)
        SELECT * FROM cte_a
        """,
        "redshift",
        {"col1": {"base_table.col1"}, "col2": {"base_table.col2"}},
    ),
]


def run_script(sql: str, dialect: str) -> dict:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
        f.write(sql)
        path = f.name
    # Prefer `uv run` so PEP 723 metadata auto-installs sqlglot in an
    # ephemeral env. Fall back to plain python3 (requires manual sqlglot
    # install) for environments without uv.
    import shutil
    if shutil.which("uv"):
        cmd = ["uv", "run", "--quiet", str(SCRIPT), path, dialect]
    else:
        cmd = [sys.executable, str(SCRIPT), path, dialect]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # uv may need longer on first run for ephemeral install
        )
        if proc.returncode > 1:
            return {"_test_error": f"script exit={proc.returncode}: {proc.stderr[:200]}"}
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            return {"_test_error": f"non-JSON stdout: {e}; raw={proc.stdout[:200]}"}
    finally:
        Path(path).unlink(missing_ok=True)


def check(actual: dict, expected: dict[str, set[str]]) -> tuple[bool, str]:
    """Compare case-insensitively — Snowflake uppercases by spec, Redshift
    folds to lowercase, BigQuery preserves. We don't care about case at the
    column-lineage level; we care that the right SOURCES appear."""
    if "_test_error" in actual:
        return False, actual["_test_error"]
    if "_error" in actual:
        return False, f"script reported _error: {actual['_error']}"

    # Build case-insensitive lookups
    actual_ci = {k.lower(): {v.lower() for v in vs} for k, vs in actual.items()}

    for col, expected_sources in expected.items():
        col_ci = col.lower()
        if col_ci not in actual_ci:
            return False, f"missing column {col!r} (got: {sorted(actual.keys())})"
        expected_ci = {s.lower() for s in expected_sources}
        if not expected_ci.issubset(actual_ci[col_ci]):
            missing = expected_ci - actual_ci[col_ci]
            return False, f"col {col!r}: missing sources {sorted(missing)} (got: {sorted(actual_ci[col_ci])})"
    return True, "ok"


def main() -> int:
    failures = 0
    for i, (sql, dialect, expected) in enumerate(CASES, 1):
        actual = run_script(sql, dialect)
        ok, msg = check(actual, expected)
        status = "OK  " if ok else "FAIL"
        sql_oneline = " ".join(sql.split())[:60]
        print(f"[{i}/{len(CASES)}] {status} ({dialect}) {sql_oneline}")
        if not ok:
            print(f"         {msg}")
            print(f"         actual: {json.dumps(actual, sort_keys=True)}")
            failures += 1
    print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
