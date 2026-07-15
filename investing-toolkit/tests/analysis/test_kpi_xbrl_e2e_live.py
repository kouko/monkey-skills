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
segment with real FY2014-2016 OLD-era values is proven OFFLINE by
test_kpi_xbrl.py::test_build_series_with_break_splits_stitched_era_both_segments
against the committed fixture.

TASK 7 (2026-07-15, full-signature rewire): the iphone_revenue binding
below was rewired from the pilot's single {axis, member, fy_min, fy_max}
model to the full-signature `{concept, dimensions}` shape (no fy ranges —
the concept+member signature alone is the era discriminant). A second live
test, `test_nflx_streaming_deconflated_end_to_end_live`, proves live
de-conflation end-to-end: a NFLX streaming_revenue full-signature binding
naming ONLY `{ProductOrService: StreamingMember}` resolves the streaming
TOTAL as one value per period, never the conflated per-region slice
values that share the same ProductOrService member plus an extra
StatementGeographical axis.

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

# The era-specific iphone_revenue binding (Task 7, full-signature shape —
# same shape as test_kpi_xbrl.py's IPHONE_REVENUE_FULL_SIGNATURE_BINDING):
# OLD-era SalesRevenueNet + {ProductOrService: AppleIphoneMember}; NEW-era
# RevenueFromContract... + {ProductOrService: IPhoneMember}. No fy_min/
# fy_max ranges — the concept+member signature alone is the era
# discriminant. Only the NEW-era source matches the reachable live facts
# (a single latest 10-K never carries pre-2018 comparatives); the OLD-era
# source matches nothing live (correctly, not an error).
IPHONE_REVENUE_BINDING = {
    "kpi_id": "iphone_revenue",
    "sources": [
        {
            "concept": "us-gaap:SalesRevenueNet",
            "dimensions": {"ProductOrService": "AppleIphoneMember"},
            "source_kind": "xbrl-dimensional",
        },
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "dimensions": {"ProductOrService": "IPhoneMember"},
            "source_kind": "xbrl-dimensional",
        },
    ],
}

# NFLX streaming_revenue full-signature binding: names ONLY the
# {ProductOrService: StreamingMember} axis — a NFLX 10-K also carries
# per-region streaming slices (StreamingMember + an extra
# StatementGeographical axis) that must NOT match this narrower selector
# (dict-equality on `dimensions` rejects the extra key), proving live
# de-conflation end-to-end.
STREAMING_REVENUE_BINDING = {
    "kpi_id": "streaming_revenue",
    "sources": [
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "StreamingMember"},
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


@pytest.mark.network
def test_nflx_streaming_deconflated_end_to_end_live():
    """Task 7 GREEN: live full-signature de-conflation proof. NFLX's real
    10-K XBRL tags a streaming-revenue TOTAL fact ({ProductOrService:
    StreamingMember}) alongside per-region slice facts that ALSO carry
    ProductOrService=StreamingMember plus an extra StatementGeographical
    axis. A full-signature binding naming ONLY {ProductOrService:
    StreamingMember} (dict-equality on `dimensions` — no extra key allowed)
    must resolve exactly ONE value per period (the TOTAL, > 30e9) — never
    the conflated per-region slice values — proving live de-conflation
    end-to-end. The offline complement is
    test_kpi_xbrl.py::test_resolve_binding_exact_signature_deconflates
    against the committed fixture.
    """
    if str(DATA_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(DATA_SCRIPTS))
    import sec_edgar_client

    sys.modules.pop("kpi_xbrl_e2e_nflx", None)
    kpi_xbrl = _load_module("kpi_xbrl_e2e_nflx", KPI_XBRL_SCRIPT)

    # (1) live dimensional-revenue fact-pack extraction
    pack = sec_edgar_client.extract_dimensional_revenue("NFLX")
    assert "error" not in pack, f"extract_dimensional_revenue failed: {pack}"
    assert pack["company"] == "NFLX"

    # (2) full-signature streaming_revenue binding resolves the live facts
    points = kpi_xbrl.resolve_binding(pack, STREAMING_REVENUE_BINDING, "NFLX")
    assert points, "expected at least one resolved streaming_revenue point from live data"
    assert all(p["kpi_id"] == "streaming_revenue" for p in points)

    # (3) de-conflation invariant: exactly ONE point per period (never a
    # conflated total+slice double-count), and each is the TOTAL magnitude
    # (> 30e9), never a smaller per-region slice value.
    periods = [p["period"] for p in points]
    assert len(periods) == len(set(periods)), (
        f"expected exactly one point per period (de-conflated), got: {periods}"
    )
    for p in points:
        assert p["value"] > 30e9, (
            f"expected the streaming TOTAL (> 30e9), not a conflated/regional "
            f"slice value: {p}"
        )
