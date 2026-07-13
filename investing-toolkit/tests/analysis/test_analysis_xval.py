"""Tests for analysis-xval/scripts/xval_compute.py (Layer 2 pure compute).

Task 3 (plan: docs/loom/plans/2026-07-13-us-sec-financial-table-xval.md) ships
ONLY the CLI + report-envelope skeleton: `--source-a` (doc-table cells pack)
and `--source-b` (companyfacts pack) resolve to an empty-comparisons report
scaffold. Matching/classification logic lands in later tasks.
"""
from __future__ import annotations

import json

from conftest import XVAL_SCRIPT


def test_cli_emits_report_scaffold(runner, tmp_path):
    source_a = tmp_path / "source_a.json"
    source_b = tmp_path / "source_b.json"
    source_a.write_text("{}", encoding="utf-8")
    source_b.write_text("{}", encoding="utf-8")

    res = runner(XVAL_SCRIPT, "--source-a", str(source_a), "--source-b", str(source_b))

    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["comparisons"] == []
    assert "high_alerts" in payload
    assert "single_source" in payload
    assert "_provenance" in payload


def test_bad_args_exit_2(runner, tmp_path):
    source_a = tmp_path / "source_a.json"
    source_a.write_text("{}", encoding="utf-8")

    # Missing required --source-b arg.
    res_missing = runner(XVAL_SCRIPT, "--source-a", str(source_a))
    assert res_missing.returncode == 2

    # Unreadable (nonexistent) --source-b path.
    res_unreadable = runner(
        XVAL_SCRIPT,
        "--source-a", str(source_a),
        "--source-b", str(tmp_path / "does_not_exist.json"),
    )
    assert res_unreadable.returncode == 2
