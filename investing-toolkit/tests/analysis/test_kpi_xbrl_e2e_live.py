"""test_kpi_xbrl_e2e_live.py — live end-to-end anchor for the operational-kpi
tier-② XBRL pilot (Task 6, docs/loom/plans/2026-07-14-operational-kpi-
companyfacts-pilot.md).

Wires the COMPLETE chain on REAL live Apple data:
  sec_edgar_client.extract_dimensional_revenue("AAPL")
    -> kpi_xbrl.resolve_binding (iphone_revenue era-binding)
    -> kpi_xbrl.build_series_with_break(points, "2018")  (declared break)
    -> shape into kpi_memo_feed's kpi_series arg
    -> kpi_gate.attest_source(company, schema_version, {"xbrl-dimensional"})
    -> kpi_memo_feed.build_memo_feed(...)  -> a TRUSTED feed.

SCOPE AMENDMENT 2 (2026-07-15): a single latest 10-K's XBRL only carries
~3 years of comparatives — all NEW-era (post-2018, srt:ProductOrServiceAxis
/ aapl:IPhoneMember). Apple's pre-2018 OLD-era iPhone tagging
(us-gaap:ProductOrServiceAxis / aapl:AppleIphoneMember) is NOT reachable
from the latest filing, and this extractor is deliberately single-filing
(multi-filing fetch is out of pilot scope). So this live e2e proves the
chain on the REACHABLE data: the live NEW-era facts land in the `recast`
segment (period >= "2018") and `as_reported` is legitimately EMPTY — a
pre-2018 point is NEVER fabricated to fill it. The break-spanning dual
segment with a real FY2016 OLD-era value is proven OFFLINE by
test_kpi_xbrl.py::test_declared_break_splits_series_not_concat against the
committed fixture.

TRUSTED here comes from `kpi_gate.attest_source` (trusted-by-source: XBRL
dimensional provenance is itself the trust signal — no sampled ground-truth
label set), NOT from an evaluate() accuracy run.

Marked @pytest.mark.network (registered in tests/analysis/conftest.py) so
the offline suite (`pytest -m "not network"`) stays green; edgartools /
sec_edgar_client are imported inside the test body so offline collection
stays clean when edgartools is not installed. Run live:
  uv run --with pytest --with edgartools==5.42.0 --with requests \
    pytest investing-toolkit/tests/analysis/test_kpi_xbrl_e2e_live.py \
    -q -m network

No `@req` tags: this dispatch's plan traces work by named plan Tasks, NOT
by registered loom-spec REQ-ids — so `@req` is omitted per the implementer
contract (mirrors test_kpi_xbrl.py's rationale).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from conftest import KPI_GATE_SCRIPT, KPI_MEMO_FEED_SCRIPT, KPI_XBRL_SCRIPT

ROOT = Path(__file__).resolve().parents[2]
DATA_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"

# The era-specific iphone_revenue binding (same shape as
# test_kpi_xbrl.py's IPHONE_REVENUE_BINDING): OLD-era SalesRevenueNet under
# us-gaap:ProductOrServiceAxis / aapl:AppleIphoneMember for fy <= 2017; the
# NEW-era RevenueFromContract under srt:ProductOrServiceAxis /
# aapl:IPhoneMember for fy >= 2018. Only the NEW-era source matches the
# reachable live facts; the OLD-era source matches nothing live (correctly).
IPHONE_REVENUE_BINDING = {
    "kpi_id": "iphone_revenue",
    "sources": [
        {
            "concept": "us-gaap:SalesRevenueNet",
            "axis": "us-gaap:ProductOrServiceAxis",
            "member": "aapl:AppleIphoneMember",
            "fy_min": 2007,
            "fy_max": 2017,
            "source_kind": "xbrl-dimensional",
        },
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "axis": "srt:ProductOrServiceAxis",
            "member": "aapl:IPhoneMember",
            "fy_min": 2018,
            "fy_max": 2099,
            "source_kind": "xbrl-dimensional",
        },
    ],
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.network
def test_apple_iphone_revenue_end_to_end_live(tmp_path, monkeypatch):
    # Isolated store dir — attest_source/is_trusted persist under this tmp
    # path, never the real durable store (mirrors test_kpi_gate.py /
    # test_kpi_memo_feed.py's KPI_STORE_DIR override).
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    if str(DATA_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(DATA_SCRIPTS))
    import sec_edgar_client

    # kpi_gate must be THE module kpi_memo_feed's `import kpi_gate` resolves
    # to, so attest_source writes the gate record build_memo_feed reads
    # (mirrors test_kpi_memo_feed.py's _load_kpi_memo_feed_module).
    scripts_dir = str(KPI_GATE_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_gate", None)
    import kpi_gate  # noqa: E402

    sys.modules.pop("kpi_memo_feed_e2e", None)
    kpi_memo_feed = _load_module("kpi_memo_feed_e2e", KPI_MEMO_FEED_SCRIPT)
    kpi_xbrl = _load_module("kpi_xbrl_e2e", KPI_XBRL_SCRIPT)

    # (1) live dimensional-revenue fact-pack extraction
    pack = sec_edgar_client.extract_dimensional_revenue("AAPL")
    assert "error" not in pack, f"extract_dimensional_revenue failed: {pack}"
    assert pack["company"] == "AAPL"

    # (2) era-binding resolves the live iPhone facts under one kpi_id
    points = kpi_xbrl.resolve_binding(pack, IPHONE_REVENUE_BINDING, "AAPL")
    assert points, "expected at least one resolved iphone_revenue point from live data"
    assert all(p["kpi_id"] == "iphone_revenue" for p in points)

    # (3) declared 2018 structural break -> dual series (NOT a naive concat)
    split = kpi_xbrl.build_series_with_break(points, "2018")

    # as_reported (pre-2018) is legitimately EMPTY: no OLD-era iPhone facts
    # are reachable from the latest 10-K. Assert it explicitly — a pre-2018
    # point is NEVER fabricated to fill it.
    assert split["as_reported"] == [], (
        "as_reported must be EMPTY (no live pre-2018 OLD-era facts reachable "
        f"from the latest 10-K); never fabricate one: {split['as_reported']}"
    )

    # the live NEW-era facts (FY2023/2024/2025) land in recast (period >= "2018")
    recast = split["recast"]
    assert recast, "expected the live NEW-era iPhone facts in the recast segment"
    assert all(p["period"] >= "2018" for p in recast)
    assert all(p["value"] > 100e9 for p in recast), (
        f"expected each recast iPhone revenue value > 100e9: {recast}"
    )
    assert split["break_markers"] == [{"break_period": "2018"}]

    # (4) shape into kpi_memo_feed's kpi_series arg (the recast segment is
    # the live-reachable trend). resolve_binding's points already carry all
    # three provenance fields, so provenance-completeness passes.
    kpi_series = [{"kpi_id": "iphone_revenue", "points": recast}]

    # (5) trusted-by-source attestation — XBRL dimensional provenance is the
    # trust signal; no sampled ground-truth labels, no evaluate() run
    schema_version = "1.0"
    kpi_gate.attest_source(
        "AAPL", schema_version, {"xbrl-dimensional"}, attested_at="2026-07-15T00:00:00Z",
    )
    assert kpi_gate.is_trusted("AAPL", schema_version) is True, (
        "attest_source({xbrl-dimensional}) must make AAPL/1.0 trusted-by-source"
    )

    # (6) memo-feed assembly reads is_trusted -> TRUSTED feed bundling the
    # provenanced series (build_memo_feed does NOT raise = provenance passes)
    feed = kpi_memo_feed.build_memo_feed(
        "AAPL", schema_version, kpi_series, generated_at="2026-07-15T00:00:00Z",
    )
    assert feed["status"] == "TRUSTED", f"expected a TRUSTED feed: {feed}"
    assert "withheld_reason" not in feed
    feed_kpi_ids = [s["kpi_id"] for s in feed["kpi_feeds"]]
    assert "iphone_revenue" in feed_kpi_ids
    feed_iphone = next(s for s in feed["kpi_feeds"] if s["kpi_id"] == "iphone_revenue")
    assert feed_iphone["points"] == recast
    assert all(p["value"] > 100e9 for p in feed_iphone["points"])
