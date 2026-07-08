"""Task 1 acceptance test — the l2-harness dbt-duckdb fixture project must
parse cleanly via `dbt parse` before any trap/filler models are layered on
top of it in later tasks (Tasks 2-7).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "l2-harness"


def test_dbt_project_parses():
    """`dbt parse` must succeed against the skeleton project (duckdb
    adapter, 0 custom models) — proves dbt_project.yml + profiles.yml
    resolve correctly on their own, independent of the shared dbt_build
    fixture in conftest.py. `--project-dir` / `--profiles-dir` grounding:
    see `conftest.py`'s `run_dbt()` docstring (same flags, same source)."""
    result = subprocess.run(
        ["dbt", "parse", "--project-dir", str(FIXTURE_DIR), "--profiles-dir", str(FIXTURE_DIR)],
        cwd=FIXTURE_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"dbt parse failed:\n--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )


def test_dbt_build_fixture_yields_queryable_duckdb_connection(dbt_build):
    """The shared `dbt_build` fixture (conftest.py) must actually execute
    `dbt build` and hand back a usable DuckDB connection — later trap-model
    tasks depend on querying build results through this exact fixture
    rather than re-invoking dbt themselves."""
    assert dbt_build.execute("select 1").fetchone() == (1,)
