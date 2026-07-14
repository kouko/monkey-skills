"""Tests for analysis-kpi/scripts/kpi_series.py — split a period-ordered
series into as-reported/recast lineages by its applied breaks
(operational-kpi capability, slice 7, Task 2).

kpi_series.py is PURE-COMPUTE (stdlib only) — it does NOT import
`_store_fs`, resolve a store dir, lock, or persist anything; `split_series`
takes `points` + `applied_breaks` as plain arguments. No `KPI_STORE_DIR`
fixture is needed.

The library function is exercised by loading `kpi_series.py` via importlib
(same convention as test_kpi_validate.py's `kpi_validate_module` fixture).

No `@req` tags: this dispatch's plan/spec trace work by named change-folder
Requirements (operational-kpi / "Dual as-reported/recast series with visible
break flag"), NOT by registered loom-spec REQ-ids — so `@req` is omitted per
the implementer contract.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

from conftest import KPI_BREAK_SCRIPT, KPI_SERIES_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_series_module():
    """Load kpi_series.py as an importable module for unit tests of its
    library surface (split_series).
    """
    spec = importlib.util.spec_from_file_location("kpi_series_test", KPI_SERIES_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_series_test"] = module
    spec.loader.exec_module(module)
    return module


def test_split_series_partitions_by_break(kpi_series_module):
    """Task 2: split_series(points, applied_breaks) partitions a
    period-ordered series into as_reported (periods before the earliest
    break_period) and recast (periods AT/after it), plus one break_marker
    per applied break. No applied_breaks → all points in as_reported,
    recast and break_markers both empty.
    """
    points = [
        {"period": "FY2022", "value": 100},
        {"period": "FY2023", "value": 110},
        {"period": "FY2024", "value": 120},
        {"period": "FY2025", "value": 130},
    ]
    applied_breaks = [{"break_period": "FY2024"}]

    result = kpi_series_module.split_series(points, applied_breaks)

    assert result["as_reported"] == [
        {"period": "FY2022", "value": 100},
        {"period": "FY2023", "value": 110},
    ]
    assert result["recast"] == [
        {"period": "FY2024", "value": 120},
        {"period": "FY2025", "value": 130},
    ]
    assert result["break_markers"] == [{"break_period": "FY2024"}]

    # No applied breaks → nothing to split; all points stay as_reported.
    no_break_result = kpi_series_module.split_series(points, [])
    assert no_break_result["as_reported"] == points
    assert no_break_result["recast"] == []
    assert no_break_result["break_markers"] == []

    # MULTIPLE (out-of-order) applied breaks: the two-way split uses the
    # EARLIEST break_period as the boundary, and EVERY break is surfaced in
    # break_markers (a regression to latest-boundary or dropped markers must fail here).
    multi_breaks = [{"break_period": "FY2024"}, {"break_period": "FY2023"}]
    multi = kpi_series_module.split_series(points, multi_breaks)
    assert [p["period"] for p in multi["as_reported"]] == ["FY2022"], (
        "split must use the EARLIEST break_period (FY2023) as the boundary"
    )
    assert [p["period"] for p in multi["recast"]] == ["FY2023", "FY2024", "FY2025"]
    assert len(multi["break_markers"]) == 2, "every applied break must be surfaced"

    # Empty points → empty partitions, no crash.
    empty = kpi_series_module.split_series([], applied_breaks)
    assert empty["as_reported"] == []
    assert empty["recast"] == []


def test_series_view_requires_basis_across_break(kpi_series_module):
    """Task 3: series_view(points, applied_breaks, basis) refuses a naive
    concatenation across an applied break — basis=None with >=1 applied
    break MUST raise, forcing the caller to pick a lineage explicitly.
    With NO applied break, basis is immaterial (nothing to disambiguate):
    None or any recognized basis string returns the flat as_reported
    series. An unrecognized basis string is always rejected loud.

    Why this matters: silently concatenating as-reported and recast
    points across a definition change would present a chart/table that
    looks continuous but mixes two incompatible measurement bases — the
    exact naive-concatenation bug this capability exists to prevent.
    """
    points = [
        {"period": "FY2022", "value": 100},
        {"period": "FY2023", "value": 110},
        {"period": "FY2024", "value": 120},
        {"period": "FY2025", "value": 130},
    ]
    applied_breaks = [{"break_period": "FY2024"}]

    with pytest.raises(ValueError):
        kpi_series_module.series_view(points, applied_breaks, basis=None)

    as_reported_view = kpi_series_module.series_view(points, applied_breaks, basis="as-reported")
    assert as_reported_view == [
        {"period": "FY2022", "value": 100},
        {"period": "FY2023", "value": 110},
    ]

    recast_view = kpi_series_module.series_view(points, applied_breaks, basis="recast")
    assert recast_view == [
        {"period": "FY2024", "value": 120},
        {"period": "FY2025", "value": 130},
    ]

    dual_view = kpi_series_module.series_view(points, applied_breaks, basis="dual")
    assert dual_view == {
        "as_reported": [
            {"period": "FY2022", "value": 100},
            {"period": "FY2023", "value": 110},
        ],
        "recast": [
            {"period": "FY2024", "value": 120},
            {"period": "FY2025", "value": 130},
        ],
        "break_markers": [{"break_period": "FY2024"}],
    }

    with pytest.raises(ValueError):
        kpi_series_module.series_view(points, applied_breaks, basis="unknown-basis")

    # No applied break → nothing to disambiguate; basis=None returns the
    # flat series without raising.
    no_break_view = kpi_series_module.series_view(points, [], basis=None)
    assert no_break_view == points


def test_cli_apply_and_view_roundtrip(tmp_path):
    """Task 4: the kpi_series.py CLI's `apply`/`view` subcommands round-trip
    a confirmed break through real subprocess invocations — `apply` is a
    thin wrapper over kpi_break.apply_break (not a reimplementation, mirrors
    test_kpi_break.py::test_cli_detect_flag_confirm_roundtrip), and `view`
    is a thin wrapper over series_view.

    flag+confirm (via the kpi_break CLI, same KPI_STORE_DIR) -> apply (via
    the kpi_series CLI) -> break record APPLIED. `view --basis dual` (a
    {points, applied_breaks} JSON payload on stdin) -> the dual dict. A
    `view` across that applied break with NO --basis -> exit 1 (the
    refuse-naive-concatenation ValueError from series_view, mapped to the
    same fail-loud exit-code convention as every other kpi_* CLI, no raw
    traceback). Malformed JSON -> exit 2. `--help` lists both subcommands.
    """
    env = {**os.environ, "KPI_STORE_DIR": str(tmp_path)}

    candidate = {
        "trigger": "resegmentation",
        "detail": {"prev_segments": ["iPhone"], "curr_segments": ["iPhone", "Wearables"]},
    }
    flag_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_BREAK_SCRIPT), "flag",
            "--company", "SERIESCO", "--schema-version", "v1",
            "--review-item-id", "ri-series-1",
        ],
        input=json.dumps(candidate),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert flag_result.returncode == 0, (
        f"flag subcommand failed: stdout={flag_result.stdout!r} stderr={flag_result.stderr!r}"
    )
    break_id = json.loads(flag_result.stdout)["break_id"]

    mapping = {"iPhone": "iPhone", "Wearables": "Wearables (new)"}
    confirm_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_BREAK_SCRIPT), "confirm",
            "--company", "SERIESCO", "--break-id", break_id, "--by", "alice",
        ],
        input=json.dumps(mapping),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert confirm_result.returncode == 0, (
        f"confirm subcommand failed: stdout={confirm_result.stdout!r} "
        f"stderr={confirm_result.stderr!r}"
    )

    # apply: no request body; wraps kpi_break.apply_break and prints the
    # updated (now APPLIED) break record.
    apply_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_SERIES_SCRIPT), "apply",
            "--company", "SERIESCO", "--break-id", break_id, "--break-period", "FY2024",
        ],
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert apply_result.returncode == 0, (
        f"apply subcommand failed: stdout={apply_result.stdout!r} stderr={apply_result.stderr!r}"
    )
    applied_record = json.loads(apply_result.stdout)
    assert applied_record["status"] == "APPLIED"
    assert applied_record["break_period"] == "FY2024"

    points = [
        {"period": "FY2022", "value": 100},
        {"period": "FY2023", "value": 110},
        {"period": "FY2024", "value": 120},
        {"period": "FY2025", "value": 130},
    ]
    applied_breaks = [{"break_period": "FY2024"}]
    payload = json.dumps({"points": points, "applied_breaks": applied_breaks})

    # view --basis dual -> the full dual dict.
    view_dual_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_SERIES_SCRIPT), "view",
            "--company", "SERIESCO", "--basis", "dual",
        ],
        input=payload,
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert view_dual_result.returncode == 0, (
        f"view subcommand failed: stdout={view_dual_result.stdout!r} "
        f"stderr={view_dual_result.stderr!r}"
    )
    assert json.loads(view_dual_result.stdout) == {
        "as_reported": [
            {"period": "FY2022", "value": 100},
            {"period": "FY2023", "value": 110},
        ],
        "recast": [
            {"period": "FY2024", "value": 120},
            {"period": "FY2025", "value": 130},
        ],
        "break_markers": [{"break_period": "FY2024"}],
    }

    # view with an applied break and NO --basis -> exit 1 (fail-loud, the
    # naive-concatenation ValueError from series_view), no raw traceback.
    view_no_basis_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_SERIES_SCRIPT), "view",
            "--company", "SERIESCO",
        ],
        input=payload,
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert view_no_basis_result.returncode == 1, view_no_basis_result.stdout
    assert "Traceback" not in view_no_basis_result.stderr, (
        "a series across a break with no --basis must fail cleanly, not with a raw traceback"
    )

    # Malformed JSON -> exit 2 (view).
    malformed_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_SERIES_SCRIPT), "view",
            "--company", "SERIESCO", "--basis", "dual",
        ],
        input="{not valid json",
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert malformed_result.returncode == 2, malformed_result.stderr
    assert "Traceback" not in malformed_result.stderr

    # --help lists both subcommands.
    help_result = subprocess.run(
        ["uv", "run", "--script", str(KPI_SERIES_SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert help_result.returncode == 0
    for subcommand in ("apply", "view"):
        assert subcommand in help_result.stdout, (
            f"--help must list the {subcommand!r} subcommand"
        )
