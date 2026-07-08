"""conftest.py — shared pytest fixtures for dbt-wiki's tests/ suite.

Registers the `e2e` marker (real, non-mocked headless `claude -p` runs —
Task 11 of the L2 harness plan — must never run unattended; invoke the
suite with `-m "not e2e"` to exclude it, per AGENTS.md's command-surface
entry) and provides `dbt_build`,
the shared harness fixture that runs `dbt build` against the synthetic
dbt-duckdb project at fixtures/l2-harness/ once per test session and hands
back a live DuckDB connection to the result. Trap-model tests added in
later tasks (2-7) query through this fixture rather than each re-running
`dbt build` themselves.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import duckdb
import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "l2-harness"
DB_PATH = FIXTURE_DIR / "target" / "l2_harness.duckdb"


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "e2e: real (non-mocked) headless `claude -p` run — excluded from CI by default",
    )


def run_dbt(*args: str) -> subprocess.CompletedProcess:
    """Run a dbt CLI command against the l2-harness fixture project,
    isolated from the invoking user's own ~/.dbt/profiles.yml.

    `--project-dir` / `--profiles-dir` grounding: captured locally via
    `dbt build --help` (dbt-core, this repo's pinned `dbt-duckdb==1.10.1`
    resolves dbt-core per requirements.txt) — "--profiles-dir PATH: Which
    directory to look in for the profiles.yml file... --project-dir PATH:
    Which directory to look in for the dbt_project.yml file." `parse` and
    `build` are documented dbt CLI subcommands (docs.getdbt.com/reference/
    commands/parse, .../commands/build).
    """
    cmd = [
        "dbt",
        *args,
        "--project-dir", str(FIXTURE_DIR),
        "--profiles-dir", str(FIXTURE_DIR),
    ]
    return subprocess.run(cmd, cwd=FIXTURE_DIR, capture_output=True, text=True)


@pytest.fixture(scope="session")
def dbt_build():
    """Run `dbt build` once per test session, then yield a DuckDB
    connection to the resulting database file. Session-scoped because
    `dbt build` re-runs every seed/model/test and is expensive to repeat
    per test function. Not opened read-only: with 0 models (current
    fixture state — trap/filler models land in later tasks), dbt-duckdb
    never touches the database file, so it does not exist yet on disk;
    a writable connect() creates it on demand. All test functions share
    this single session-scoped connection, so there is no multi-writer
    conflict.
    """
    result = run_dbt("build")
    assert result.returncode == 0, (
        f"dbt build failed against {FIXTURE_DIR}:\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
    conn = duckdb.connect(str(DB_PATH))
    try:
        yield conn
    finally:
        conn.close()
