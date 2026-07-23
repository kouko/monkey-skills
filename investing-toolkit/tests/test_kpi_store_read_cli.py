"""RED-first tests for kpi_store.py's read-side CLI subcommands (tearsheet
plan, Tasks 1-2: `list-series`, `dump --company`).

The append/query CLI is exercised via real `uv run --script` subprocesses in
tests/analysis/test_kpi_store.py (`test_cli_append_then_query_roundtrip`);
this file mirrors that subprocess + `KPI_STORE_DIR` tmp-dir pattern for the
new read subcommands. Lives at the tests/ top level (not tests/analysis/) per
the plan's Files-touched list, so KPI_STORE_SCRIPT is resolved locally rather
than imported from tests/analysis/conftest.py.

No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-23-kpi-
tearsheet.md) binds tasks by "Brief item covered", not registered loom-spec
REQ-ids, so there is no id in the living-spec namespace to bind to (same
convention as test_kpi_store_enumerate.py).
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_ROOT = _TESTS_DIR.parent
KPI_STORE_SCRIPT = (
    _ROOT / "skills" / "analysis-kpi" / "scripts" / "kpi_store.py"
)

# A real accession so the store's accession-derived as_of guard passes; the
# store rejects a wall-clock or absent as_of.
_ACCESSION = "0001065280-25-000033"


def _point(company: str, kpi_id: str, value: str) -> dict:
    """A minimal store-valid point: full provenance + an accession-derived
    (non-wall-clock) as_of, so `append` accepts it.
    """
    return {
        "company": company,
        "kpi_id": kpi_id,
        "period": "Q4-2024",
        "as_of": "2025-01-30",
        "value": value,
        "source_accession": _ACCESSION,
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
    }


def _run_cli(*args: str, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(KPI_STORE_SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def _append_via_cli(point: dict, env: dict) -> None:
    result = subprocess.run(
        ["uv", "run", "--script", str(KPI_STORE_SCRIPT), "append"],
        input=json.dumps(point),
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    assert result.returncode == 0, (
        f"append fixture setup failed: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )


def test_list_series_prints_pairs_json(tmp_path):
    """`list-series` prints the store's `(company, kpi_id)` pairs as a sorted
    JSON array of 2-element arrays, exit 0 — the CLI read exposure this task
    adds over the library-only `list_series()` (test_kpi_store_enumerate.py).
    """
    env = {**os.environ, "KPI_STORE_DIR": str(tmp_path)}
    _append_via_cli(_point("AMZN", "employees", "1556000"), env)
    _append_via_cli(_point("TSLA", "deliveries", "495570"), env)

    result = _run_cli("list-series", env=env)

    assert result.returncode == 0, (
        f"list-series failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    pairs = json.loads(result.stdout)
    assert pairs == [["AMZN", "employees"], ["TSLA", "deliveries"]], pairs


def test_list_series_empty_store_prints_empty_array(tmp_path):
    """An empty (non-existent) store dir → `[]`, exit 0 — never raises."""
    env = {**os.environ, "KPI_STORE_DIR": str(tmp_path / "does-not-exist")}

    result = _run_cli("list-series", env=env)

    assert result.returncode == 0, (
        f"list-series failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert json.loads(result.stdout) == []
