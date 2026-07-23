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

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_ROOT = _TESTS_DIR.parent
KPI_STORE_SCRIPT = (
    _ROOT / "skills" / "analysis-kpi" / "scripts" / "kpi_store.py"
)


def _load_module():
    """Direct (non-subprocess) import of kpi_store.py — used ONLY to call
    `_canonical_value` for an independent sanity check on the Decimal math
    (Task 2's GREEN condition); the dump subcommand itself is always
    exercised as a real subprocess above, matching this file's convention.
    """
    spec = importlib.util.spec_from_file_location("kpi_store_read_cli", KPI_STORE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_store_read_cli"] = module
    spec.loader.exec_module(module)
    return module

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


def test_dump_groups_vintages_and_flags_disagreement(tmp_path):
    """`dump --company` groups a J&J-shape restatement (first filing scaled
    93,775 x 1e6, later restated to a genuinely different base-scale figure)
    into ONE period entry with `disagreement: true`; a label-only difference
    between the two vintages ("FY2021" vs "2021 comparative") must NOT split
    them into separate periods; a distinct single-observation period stays
    its own entry with `disagreement: false`; `canonical_value` for the
    scaled point is Decimal-correct — it matches `_canonical_value` computed
    directly on an equivalent already-base point (93,775,000,000 x scale 1),
    proving the scale multiply went through Decimal, not float; an unknown
    company dumps an empty payload, exit 0.
    """
    env = {**os.environ, "KPI_STORE_DIR": str(tmp_path)}
    first_filing = {
        "company": "JNJ",
        "kpi_id": "revenue",
        "period": "FY2021",
        "as_of": "2022-02-15",
        "value": "93,775",
        "scale": 1_000_000,
        "source_accession": _ACCESSION,
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
        "period_start": "2021-01-01",
        "period_end": "2021-12-31",
        "period_kind": "duration",
    }
    restated = {
        "company": "JNJ",
        "kpi_id": "revenue",
        "period": "2021 comparative",  # label-only difference — must not split
        "as_of": "2024-02-20",
        "value": 78740000000,
        "scale": 1,
        "source_accession": "0001065280-24-000099",
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
        "period_start": "2021-01-01",
        "period_end": "2021-12-31",
        "period_kind": "duration",
    }
    other_period = {
        "company": "JNJ",
        "kpi_id": "revenue",
        "period": "FY2022",
        "as_of": "2023-02-15",
        "value": 94943000000,
        "scale": 1,
        "source_accession": "0001065280-23-000042",
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
        "period_start": "2022-01-01",
        "period_end": "2022-12-31",
        "period_kind": "duration",
    }
    for point in (first_filing, restated, other_period):
        _append_via_cli(point, env)

    result = _run_cli("dump", "--company", "JNJ", env=env)
    assert result.returncode == 0, (
        f"dump failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    payload = json.loads(result.stdout)

    assert payload["company"] == "JNJ"
    assert payload["warnings"] == []
    assert [s["kpi_id"] for s in payload["series"]] == ["revenue"]

    periods = payload["series"][0]["periods"]
    assert len(periods) == 2, periods  # FY2021 (2 vintages, merged) + FY2022

    fy2021, fy2022 = periods  # ascending _period_sort_key: 2021-12-31 < 2022-12-31

    assert fy2021["disagreement"] is True
    assert len(fy2021["observations"]) == 2
    assert set(fy2021["period_labels"]) == {"FY2021", "2021 comparative"}
    assert fy2021["observations"][0]["canonical_value"] == 93775000000
    assert fy2021["observations"][1]["canonical_value"] == 78740000000
    assert fy2021["latest"]["canonical_value"] == 78740000000  # max as_of

    module = _load_module()
    base_point = {"value": 93775000000, "scale": 1}
    assert (
        module._canonical_value(base_point)
        == fy2021["observations"][0]["canonical_value"]
        == 93775000000
    )

    assert fy2022["disagreement"] is False
    assert len(fy2022["observations"]) == 1
    assert fy2022["observations"][0]["canonical_value"] == 94943000000
    assert fy2022["period_labels"] == ["FY2022"]

    unknown = _run_cli("dump", "--company", "NOPE", env=env)
    assert unknown.returncode == 0, (
        f"dump on unknown company failed: stdout={unknown.stdout!r} "
        f"stderr={unknown.stderr!r}"
    )
    assert json.loads(unknown.stdout) == {
        "company": "NOPE",
        "series": [],
        "warnings": [],
    }


def test_dump_groups_by_equivalence_closure_not_insertion_order(tmp_path):
    """Reviewer counterexample (round-2 finding 1): `same_period` is NOT
    transitive. A=instant (2021-01-01, 2021-12-31); B=duration with the SAME
    exact (start, end) pair as A — matches A via `same_period`'s EXACT branch,
    which ignores `period_kind`; C=duration (2021-01-02, 2021-12-31) — misses
    A's EXACT branch (different start) and misses A's SNAP branch (qtrs 0 vs
    4), but DOES match B via SNAP (same snapped end, both qtrs 4). So the
    correct grouping is ONE group {A, B, C} joined transitively through B —
    anchor-only matching (comparing each point only to `group[0]`) instead
    makes the result depend on insertion order: order (A, B, C) matches C
    against anchor A only (fails) -> 2 groups; order (B, C, A) matches
    everything against anchor B (succeeds) -> 1 group. Appending the SAME
    three points in two different orders to two independent stores must
    yield the SAME grouping (one period, three observations) — proving
    equivalence-closure (not first-member-only) grouping.
    """
    point_a = {
        "company": "ACME",
        "kpi_id": "revenue",
        "period": "A-label",
        "as_of": "2022-01-01",
        "value": 100,
        "source_accession": "0001065280-22-000001",
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
        "period_start": "2021-01-01",
        "period_end": "2021-12-31",
        "period_kind": "instant",
    }
    point_b = {
        "company": "ACME",
        "kpi_id": "revenue",
        "period": "B-label",
        "as_of": "2022-02-01",
        "value": 200,
        "source_accession": "0001065280-22-000002",
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
        "period_start": "2021-01-01",
        "period_end": "2021-12-31",
        "period_kind": "duration",
    }
    point_c = {
        "company": "ACME",
        "kpi_id": "revenue",
        "period": "C-label",
        "as_of": "2022-03-01",
        "value": 300,
        "source_accession": "0001065280-22-000003",
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
        "period_start": "2021-01-02",
        "period_end": "2021-12-31",
        "period_kind": "duration",
    }

    env_abc = {**os.environ, "KPI_STORE_DIR": str(tmp_path / "abc")}
    for point in (point_a, point_b, point_c):
        _append_via_cli(point, env_abc)
    result_abc = _run_cli("dump", "--company", "ACME", env=env_abc)
    assert result_abc.returncode == 0, result_abc.stderr
    periods_abc = json.loads(result_abc.stdout)["series"][0]["periods"]

    env_bca = {**os.environ, "KPI_STORE_DIR": str(tmp_path / "bca")}
    for point in (point_b, point_c, point_a):
        _append_via_cli(point, env_bca)
    result_bca = _run_cli("dump", "--company", "ACME", env=env_bca)
    assert result_bca.returncode == 0, result_bca.stderr
    periods_bca = json.loads(result_bca.stdout)["series"][0]["periods"]

    # Both orders must produce ONE merged period with all three observations
    # — not an order-dependent split.
    assert len(periods_abc) == 1, periods_abc
    assert len(periods_bca) == 1, periods_bca
    assert len(periods_abc[0]["observations"]) == 3
    assert len(periods_bca[0]["observations"]) == 3
    labels_abc = {o["period"] for o in periods_abc[0]["observations"]}
    labels_bca = {o["period"] for o in periods_bca[0]["observations"]}
    assert labels_abc == labels_bca == {"A-label", "B-label", "C-label"}


def test_dump_skips_corrupt_series_file_that_parses_to_non_dict(tmp_path):
    """A store file that parses as valid JSON but is NOT an envelope dict —
    e.g. a truncated write that leaves a bare JSON list — must hit the same
    `warnings` skip path as unparseable JSON, not raise AttributeError out of
    `dump_company` (round-2 finding 2: `_load_series`'s `.get("points")`
    on a list-shaped envelope escapes the documented never-raises promise).
    """
    env = {**os.environ, "KPI_STORE_DIR": str(tmp_path)}
    _append_via_cli(_point("ACME", "revenue", "100"), env)

    corrupt_path = tmp_path / "zzz_corrupt.json"
    corrupt_path.write_text("[]", encoding="utf-8")

    result = _run_cli("dump", "--company", "ACME", env=env)
    assert result.returncode == 0, (
        f"dump failed on corrupt file: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )
    payload = json.loads(result.stdout)
    assert payload["warnings"] == ["skipped corrupt series file: zzz_corrupt.json"]
    assert [s["kpi_id"] for s in payload["series"]] == ["revenue"]
