"""Tests for analysis-xval/scripts/xval_compute.py (Layer 2 pure compute).

Task 3 (plan: docs/loom/plans/2026-07-13-us-sec-financial-table-xval.md) ships
ONLY the CLI + report-envelope skeleton: `--source-a` (doc-table cells pack)
and `--source-b` (companyfacts pack) resolve to an empty-comparisons report
scaffold. Matching/classification logic lands in later tasks.

Task 4 adds `build_source_b_index` — the Source-B fact index reconstructed
ONLY from a companyfacts pack (independence invariant). Its internal
matching/index-building functions aren't wired into the CLI report yet
(Task 5+), so this module is loaded directly via importlib (same convention
as tests/analysis/test_comps_sector_routing.py's `sector_classifier` fixture)
rather than invoked as a subprocess.
"""
from __future__ import annotations

import importlib.util
import json
import sys

from conftest import XVAL_SCRIPT

import pytest


@pytest.fixture(scope="module")
def xval_module():
    """Load xval_compute.py as an importable module for pure-function unit
    tests of index-building logic not yet surfaced in the CLI's JSON output.
    """
    spec = importlib.util.spec_from_file_location("xval_compute_test", XVAL_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["xval_compute_test"] = module
    spec.loader.exec_module(module)
    return module


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


def test_source_b_index_from_companyfacts(xval_module, fixtures_dir):
    """Given ONLY a Source-B (companyfacts) fixture — no Source-A input at
    all — the built index exposes each concept's value keyed by
    (concept, period) with dimension=None, sourced purely from the
    companyfacts rows (independence invariant, plan Notes
    §Anti-fabrication invariant).
    """
    with (fixtures_dir / "xval_source_b_aapl.json").open(encoding="utf-8") as f:
        source_b_pack = json.load(f)

    index = xval_module.build_source_b_index(source_b_pack)

    # Instant fact (no `start` on the companyfacts row) -> period.type == "instant".
    instant_key = (
        "us-gaap:AccountsReceivableNetCurrent",
        ("instant", "2025-09-27"),
    )
    assert instant_key in index
    fact = index[instant_key]
    assert fact["concept"] == "us-gaap:AccountsReceivableNetCurrent"
    assert fact["period"] == {"type": "instant", "instant": "2025-09-27"}
    assert fact["dimension"] is None
    assert fact["value"] == 39777000000
    assert fact["accn"] == "0000320193-25-000079"

    # Duration fact (has both `start` and `end`) -> period.type == "duration".
    duration_key = (
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        ("duration", "2024-09-29", "2025-09-27"),
    )
    assert duration_key in index
    dur_fact = index[duration_key]
    assert dur_fact["period"] == {
        "type": "duration",
        "start": "2024-09-29",
        "end": "2025-09-27",
    }
    assert dur_fact["dimension"] is None
    assert dur_fact["value"] == 416161000000
    assert dur_fact["accn"] == "0000320193-25-000079"


def test_source_b_index_rejects_source_a_pack(xval_module):
    """Independence guard: handing build_source_b_index a Source-A
    doc-table-cells pack (identified by its top-level `cells` key) raises
    loudly rather than silently building an index from the wrong source.
    Uses an explicit raise (not a bare `assert`, which `python -O` strips),
    matching comps_compute.py::_load_memo_fetch_pack's wrong-pack convention.
    """
    source_a_pack = {"cells": [{"concept": "us-gaap:Assets"}]}
    with pytest.raises(ValueError, match="Source-B companyfacts pack"):
        xval_module.build_source_b_index(source_a_pack)


def test_match_non_dimensional_by_concept_period(xval_module):
    """A non-dimensional Source-A doc cell pairs with the Source-B fact
    sharing (concept, period), dimension=None both sides — matched on the
    (concept, period) key alone, never by row-label text or table position
    (anti-fabrication invariant, plan Notes).

    Two decoys prove the label/row is never consulted:
    1. Two doc cells share the SAME (concept, period) but carry DIFFERENT
       citation labels ("Total net sales" vs "Net sales (decoy label)") —
       both must resolve to the identical Source-B fact, since changing
       only the label must never change the match.
    2. The Source-B index also holds a same-concept fact for a DIFFERENT
       period with a wildly different value — a label- or
       first-same-concept-hit matcher could wrongly grab it; concept+period
       matching must not.
    """
    correct_period = {"type": "duration", "start": "2023-10-01", "end": "2024-09-28"}

    def _doc_cell(label: str) -> dict:
        return {
            "concept": "us-gaap:Revenues",
            "period": correct_period,
            "dimension": None,
            "value_displayed": "391035000000",
            "numeric_value": 391035000000.0,
            "decimals": "-6",
            "citation": {
                "accession": "0000320193-24-000123",
                "statement_name": "IncomeStatement",
                "row": 5,
                "col": "duration_2023-10-01_2024-09-28",
                "label": label,
                "context_ref": "c-1",
                "fact_id": "f-1",
            },
        }

    source_b_pack = {
        "cik": 320193,
        "facts": {
            "us-gaap": {
                "Revenues": [
                    # Decoy listed FIRST (insertion order = index iteration
                    # order): same concept, DIFFERENT period, wildly different
                    # value. A first-same-concept-hit matcher (ignoring period)
                    # would grab THIS entry and the value assertion below would
                    # fail — so this ordering makes the period-load-bearing
                    # property genuinely testable, not vacuously satisfied.
                    {
                        "start": "2022-09-25",
                        "end": "2023-09-30",
                        "value": 1,
                        "accn": "0000320193-23-000106",
                        "form": "10-K",
                        "fy": 2023,
                        "fp": "FY",
                        "filed": "2023-11-03",
                    },
                    {
                        "start": "2023-10-01",
                        "end": "2024-09-28",
                        "value": 391035000000,
                        "accn": "0000320193-24-000123",
                        "form": "10-K",
                        "fy": 2024,
                        "fp": "FY",
                        "filed": "2024-11-01",
                    },
                ]
            }
        },
    }

    index = xval_module.build_source_b_index(source_b_pack)

    for label in ("Total net sales", "Net sales (decoy label)"):
        match = xval_module.match_cell(_doc_cell(label), index)
        assert match is not None
        assert match["concept"] == "us-gaap:Revenues"
        assert match["period"] == correct_period
        assert match["dimension"] is None
        assert match["value"] == 391035000000
        assert match["accn"] == "0000320193-24-000123"
