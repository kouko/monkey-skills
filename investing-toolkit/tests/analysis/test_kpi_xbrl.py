"""Tests for analysis-kpi/scripts/kpi_xbrl.py — XBRL fact -> kpi_store
point adapter (operational-kpi tier-② XBRL pilot, Task 1).

kpi_xbrl.py is PURE-COMPUTE (stdlib only) — it does NOT import `_store_fs`,
resolve a store dir, lock, or persist anything, and does NOT touch the
network or an LLM. No `KPI_STORE_DIR` fixture is needed.

The library function is exercised by loading `kpi_xbrl.py` via importlib
(same convention as test_kpi_parse.py's `kpi_parse_module` fixture),
against the REAL captured fixture `fixtures/xbrl_aapl_factpack.json`.

No `@req` tags: this dispatch's plan (docs/loom/plans/2026-07-14-
operational-kpi-companyfacts-pilot.md) traces work by named plan Tasks,
NOT by registered loom-spec REQ-ids — so `@req` is omitted per the
implementer contract.
"""
from __future__ import annotations

import importlib.util
import json
import sys

from conftest import FIXTURES, KPI_XBRL_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_xbrl_module():
    spec = importlib.util.spec_from_file_location("kpi_xbrl_test", KPI_XBRL_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_xbrl_test"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def fact_pack():
    return json.loads((FIXTURES / "xbrl_aapl_factpack.json").read_text(encoding="utf-8"))


NEW_IPHONE_MATCH = {
    "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
    "axis": "srt:ProductOrServiceAxis",
    "member": "aapl:IPhoneMember",
}

GROSS_PROFIT_MATCH = {"concept": "us-gaap:GrossProfit", "axis": None, "member": None}


def test_facts_to_points_maps_provenance_and_fails_loud(kpi_xbrl_module, fact_pack):
    """Task 1 GREEN: dimensional NEW-era iPhone fact -> provenance-mapped
    point; a fact missing `value` RAISES (never a fabricated 0); a flat
    GrossProfit fact -> companyfacts source_table_id + plain concept
    source_cell_ref (no `|member` suffix).
    """
    # (1) dimensional NEW-era iPhone fact -> full provenance mapping
    points = kpi_xbrl_module.facts_to_points(
        fact_pack, "iphone_revenue", NEW_IPHONE_MATCH, "AAPL", "xbrl-dimensional"
    )
    new_era = [p for p in points if p["period"] == "2025"]
    assert len(new_era) == 1
    point = new_era[0]
    assert point["value"] == 209586000000
    assert point["period"] == "2025"
    assert point["source_accession"] == "0000320193-25-000079"
    assert point["source_table_id"] == "xbrl:srt:ProductOrServiceAxis"
    assert point["source_cell_ref"] == (
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax|aapl:IPhoneMember"
    )
    assert point["as_of"] == "2025-10-31"
    assert point["source_kind"] == "xbrl-dimensional"

    # (2) a fact missing `value` RAISES — never emits a fabricated 0
    mutated = json.loads(json.dumps(fact_pack))
    for fact in mutated["facts"]:
        if fact["concept"] == NEW_IPHONE_MATCH["concept"] and fact["member"] == "aapl:IPhoneMember":
            del fact["value"]
    with pytest.raises(ValueError, match="value"):
        kpi_xbrl_module.facts_to_points(
            mutated, "iphone_revenue", NEW_IPHONE_MATCH, "AAPL", "xbrl-dimensional"
        )

    # (3) flat GrossProfit fact -> companyfacts table id, plain cell_ref
    gp_points = kpi_xbrl_module.facts_to_points(
        fact_pack, "gross_profit", GROSS_PROFIT_MATCH, "AAPL", "xbrl-companyfacts"
    )
    assert len(gp_points) == 2
    for p in gp_points:
        assert p["source_table_id"] == "xbrl:companyfacts"
        assert p["source_cell_ref"] == "us-gaap:GrossProfit"


def test_facts_to_points_period_derives_from_period_end_not_fiscal_year(kpi_xbrl_module, fact_pack):
    """period MUST come from period_end[:4] — edgartools' raw fiscal_year
    column is unreliable for prior-year comparatives (AMENDMENT a). Corrupt
    fiscal_year while leaving period_end correct -> period still follows
    period_end, proving the derivation source, not just the output value.
    """
    mutated = json.loads(json.dumps(fact_pack))
    for fact in mutated["facts"]:
        if fact["concept"] == NEW_IPHONE_MATCH["concept"] and fact.get("member") == "aapl:IPhoneMember" and fact["period_end"] == "2025-09-27":
            fact["fiscal_year"] = 1999  # deliberately wrong; period_end is the source of truth

    points = kpi_xbrl_module.facts_to_points(
        mutated, "iphone_revenue", NEW_IPHONE_MATCH, "AAPL", "xbrl-dimensional"
    )
    matched = [p for p in points if p["value"] == 209586000000]
    assert len(matched) == 1
    assert matched[0]["period"] == "2025"


def test_facts_to_points_missing_period_end_raises(kpi_xbrl_module, fact_pack):
    """A fact missing period_end RAISES naming period_end — never a
    fabricated period "None" (this closes the code-quality 🟡 finding)."""
    mutated = json.loads(json.dumps(fact_pack))
    for fact in mutated["facts"]:
        if fact["concept"] == NEW_IPHONE_MATCH["concept"] and fact.get("member") == "aapl:IPhoneMember":
            del fact["period_end"]
    with pytest.raises(ValueError, match="period_end"):
        kpi_xbrl_module.facts_to_points(
            mutated, "iphone_revenue", NEW_IPHONE_MATCH, "AAPL", "xbrl-dimensional"
        )


def test_facts_to_points_malformed_period_end_raises(kpi_xbrl_module, fact_pack):
    """A fact with a non-YYYY-MM-DD period_end RAISES naming period_end."""
    mutated = json.loads(json.dumps(fact_pack))
    for fact in mutated["facts"]:
        if fact["concept"] == NEW_IPHONE_MATCH["concept"] and fact.get("member") == "aapl:IPhoneMember":
            fact["period_end"] = "not-a-date"
    with pytest.raises(ValueError, match="period_end"):
        kpi_xbrl_module.facts_to_points(
            mutated, "iphone_revenue", NEW_IPHONE_MATCH, "AAPL", "xbrl-dimensional"
        )
