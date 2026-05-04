"""Tests for analysis-comps/scripts/comps_compute.py (Layer 2 pure compute).

The script consumes pre-fetched ``comps-multiples`` data packs (one anchor +
N peers) and emits a comps table JSON: median/mean/quartile statistics across
peers, anchor delta vs median, percentile, composite ranking. Pure compute —
no network or yfinance imports.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from conftest import COMPS_SCRIPT


# ---------------------------------------------------------------------------
# Fixture-path helpers
# ---------------------------------------------------------------------------


def _peers_arg(fixtures_dir: Path, *names: str) -> str:
    return ",".join(str(fixtures_dir / n) for n in names)


def _full_peer_set(fixtures_dir: Path) -> str:
    return _peers_arg(
        fixtures_dir,
        "comps_peer_msft.json",
        "comps_peer_googl.json",
        "comps_peer_meta.json",
        "comps_peer_amzn.json",
    )


def _anchor_arg(fixtures_dir: Path) -> str:
    return str(fixtures_dir / "comps_anchor_aapl.json")


# ---------------------------------------------------------------------------
# Smoke
# ---------------------------------------------------------------------------


def test_help_runs(runner):
    res = runner(COMPS_SCRIPT, "--help")
    assert res.returncode == 0
    out = (res.stdout + res.stderr).lower()
    assert "anchor" in out
    assert "peers" in out


def test_smoke_aapl_with_4_peers(runner, fixtures_dir):
    res = runner(
        COMPS_SCRIPT,
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["anchor"]["ticker"] == "AAPL"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


@pytest.fixture
def baseline_payload(runner, fixtures_dir):
    res = runner(
        COMPS_SCRIPT,
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    return json.loads(res.stdout)


def test_schema_top_level_keys(baseline_payload):
    for key in (
        "anchor",
        "peers",
        "statistics",
        "anchor_delta",
        "ranking",
        "_provenance",
    ):
        assert key in baseline_payload, f"missing top-level key: {key}"


def test_schema_anchor_block(baseline_payload):
    anchor = baseline_payload["anchor"]
    assert anchor["ticker"] == "AAPL"
    assert "multiples_direct" in anchor
    expected = {"trailingPE", "forwardPE", "evEbitda", "priceToSales", "priceToBook"}
    assert expected <= set(anchor["multiples_direct"].keys()), (
        f"anchor.multiples_direct missing keys; got {set(anchor['multiples_direct'].keys())}"
    )


def test_schema_peers_block(baseline_payload):
    peers = baseline_payload["peers"]
    assert isinstance(peers, list)
    assert len(peers) == 4
    for p in peers:
        assert "ticker" in p
        assert "multiples" in p
        assert "rationale" in p  # may be null
        # Aliasing: output normalized to evEbitda regardless of input field name
        assert "evEbitda" in p["multiples"]


def test_schema_statistics_block(baseline_payload):
    stats = baseline_payload["statistics"]
    expected_multiples = {"trailingPE", "forwardPE", "evEbitda", "priceToSales", "priceToBook"}
    assert expected_multiples <= set(stats.keys())
    for m in expected_multiples:
        for stat_key in ("median", "mean", "q1", "q3", "min", "max"):
            assert stat_key in stats[m], f"statistics.{m} missing {stat_key}"


def test_schema_anchor_delta_block(baseline_payload):
    delta = baseline_payload["anchor_delta"]
    expected_multiples = {"trailingPE", "forwardPE", "evEbitda", "priceToSales", "priceToBook"}
    assert expected_multiples <= set(delta.keys())
    for m in expected_multiples:
        for k in ("value", "vs_median_pct", "percentile"):
            assert k in delta[m], f"anchor_delta.{m} missing {k}"


def test_schema_ranking_block(baseline_payload):
    ranking = baseline_payload["ranking"]
    assert isinstance(ranking, list)
    assert len(ranking) >= 1
    for entry in ranking:
        assert "ticker" in entry
        assert "composite_rank" in entry


def test_schema_provenance_io_none(baseline_payload):
    prov = baseline_payload["_provenance"]
    assert prov.get("io") == "none", f"Layer 2 must declare io='none', got: {prov.get('io')!r}"


# ---------------------------------------------------------------------------
# Math correctness
# ---------------------------------------------------------------------------


def test_median_of_trailing_pe(baseline_payload):
    """peers' trailingPE [33.1, 24.5, 26.0, 42.0] sorted = [24.5, 26.0, 33.1, 42.0]
    median = (26.0 + 33.1) / 2 = 29.55
    """
    median = baseline_payload["statistics"]["trailingPE"]["median"]
    assert median == pytest.approx(29.55, abs=1e-6)


def test_quartiles_of_trailing_pe(baseline_payload):
    """Linear-interpolation quartiles on [24.5, 26.0, 33.1, 42.0]:
    q1 ≈ 25.625, q3 ≈ 35.325
    """
    stats = baseline_payload["statistics"]["trailingPE"]
    assert stats["q1"] == pytest.approx(25.625, abs=1e-3)
    assert stats["q3"] == pytest.approx(35.325, abs=1e-3)


def test_min_max_of_trailing_pe(baseline_payload):
    stats = baseline_payload["statistics"]["trailingPE"]
    assert stats["min"] == pytest.approx(24.5, abs=1e-6)
    assert stats["max"] == pytest.approx(42.0, abs=1e-6)


def test_anchor_delta_vs_median_pct(baseline_payload):
    """anchor 28.5 vs median 29.55 → ((28.5 - 29.55) / 29.55) * 100 ≈ -3.553%"""
    pct = baseline_payload["anchor_delta"]["trailingPE"]["vs_median_pct"]
    expected = ((28.5 - 29.55) / 29.55) * 100
    assert pct == pytest.approx(expected, abs=1e-3)
    assert pct < 0  # anchor cheaper than median on trailingPE


def test_anchor_delta_value_field(baseline_payload):
    assert baseline_payload["anchor_delta"]["trailingPE"]["value"] == pytest.approx(28.5)


def test_composite_ranking_cheapest_first(baseline_payload):
    """Composite_rank 1 = cheapest by composite multiples.

    Composite ranking aggregates per-multiple ranks via mean (composite_rank_avg
    field), then re-ranks ascending. GOOGL has lowest values across 4 of 5
    multiples (META marginally lower on evEbitda 17.5 vs 18.0), so mean-rank
    ≈ 1.4 → composite_rank=1. If the aggregation method changes (e.g.
    sum-of-ranks, weighted by multiple importance), this test should fail and
    be updated to reflect the new method.

    Hand-checked across 5 multiples (lower = cheaper):
      AAPL: trailingPE 28.5 / forwardPE 25.1 / evEbitda 21.3 / P/S 7.2  / P/B 35.4
      MSFT: 33.1 / 28.5 / 24.5 / 11.0 / 11.2
      GOOGL: 24.5 / 22.0 / 18.0 / 6.5  / 6.8
      META:  26.0 / 23.5 / 17.5 / 8.2  / 7.5
      AMZN:  42.0 / 38.0 / 18.2 / 3.1  / 7.8

    GOOGL has the lowest values across nearly every multiple → composite rank 1.
    """
    ranking = baseline_payload["ranking"]
    # rank 1 should be GOOGL
    by_rank = sorted(ranking, key=lambda r: r["composite_rank"])
    assert by_rank[0]["ticker"] == "GOOGL", (
        f"expected GOOGL cheapest; got {by_rank[0]['ticker']} (full ranking: "
        f"{[(r['ticker'], r['composite_rank']) for r in by_rank]})"
    )
    # composite_rank values are unique 1..N (5)
    ranks = sorted(r["composite_rank"] for r in ranking)
    assert ranks == list(range(1, len(ranking) + 1))


def test_ranking_includes_anchor(baseline_payload):
    tickers = {r["ticker"] for r in baseline_payload["ranking"]}
    assert "AAPL" in tickers


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_missing_multiple_in_one_peer(runner, fixtures_dir):
    """AMZN has forwardPE = null → forwardPE statistics computed across the
    other 3 peers; AMZN's anchor_delta-style entry (in peers list) for
    forwardPE renders as null and does not crash.
    """
    peers = _peers_arg(
        fixtures_dir,
        "comps_peer_msft.json",
        "comps_peer_googl.json",
        "comps_peer_meta.json",
        "comps_peer_missing_fwd_pe.json",
    )
    res = runner(
        COMPS_SCRIPT,
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", peers,
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    # forwardPE statistics: peers [28.5, 22.0, 23.5] (AMZN missing) → median=23.5
    fwd = payload["statistics"]["forwardPE"]
    assert fwd["median"] == pytest.approx(23.5, abs=1e-6)
    assert fwd["min"] == pytest.approx(22.0, abs=1e-6)
    assert fwd["max"] == pytest.approx(28.5, abs=1e-6)
    # AMZN entry in peers should still exist; its forwardPE multiple is null
    amzn_peer = next(p for p in payload["peers"] if p["ticker"] == "AMZN")
    assert amzn_peer["multiples"].get("forwardPE") is None
    # Other AMZN multiples remain non-null
    assert amzn_peer["multiples"].get("trailingPE") == pytest.approx(42.0)


def test_self_as_peer_dedupe(runner, fixtures_dir):
    """Self-as-peer dedupe: anchor file passed as its own peer is filtered.

    Intentionally exercises the script's documented dedupe-by-ticker behavior:
    when a --peers entry resolves to the same ticker as --anchor, it is
    skipped with a warning. This is the only way to reach the "no effective
    peers" branch via the CLI (argparse requires --peers to be non-empty).

    Once de-duped, the script falls back to anchor-only statistics
    (min == max == anchor value) and emits a warning naming the dedupe.
    """
    res = runner(
        COMPS_SCRIPT,
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", _anchor_arg(fixtures_dir),  # anchor as peer → de-duped
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    warnings = payload["_provenance"].get("warnings", [])
    assert isinstance(warnings, list)
    # Some warning about empty peers / single-anchor mode must be present
    joined = " ".join(warnings).lower()
    assert "peer" in joined or "single" in joined or "anchor" in joined, (
        f"expected warning re: empty peers; got: {warnings!r}"
    )
    # statistics fall back to anchor: min == max == anchor's value
    stats_pe = payload["statistics"]["trailingPE"]
    assert stats_pe["min"] == pytest.approx(28.5, abs=1e-6)
    assert stats_pe["max"] == pytest.approx(28.5, abs=1e-6)
    # No peers in the output list
    assert payload["peers"] == []


def test_one_peer_only(runner, fixtures_dir):
    """Single-peer degenerate case: every statistic collapses to the peer's value.

    With N=1 peer, the script's _percentiles helper falls back to (v, v) and
    statistics.median / fmean / min / max all return the lone value. This
    test pins that contract so n=1 doesn't silently start producing different
    aggregates.

    Anchor AAPL trailingPE = 28.5; lone peer MSFT trailingPE = 33.1.
    Expect every stat field for trailingPE to equal 33.1 (peer, not anchor),
    vs_median_pct = (28.5 - 33.1) / 33.1 * 100, percentile per
    _empirical_percentile([33.1, 28.5], 28.5) = 1/2 = 0.5 (anchor cheaper).
    """
    res = runner(
        COMPS_SCRIPT,
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", _peers_arg(fixtures_dir, "comps_peer_msft.json"),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)

    # All trailingPE statistics collapse to the peer's value (33.1), not anchor (28.5)
    stats_pe = payload["statistics"]["trailingPE"]
    for stat_key in ("median", "mean", "q1", "q3", "min", "max"):
        assert stats_pe[stat_key] == pytest.approx(33.1, abs=1e-6), (
            f"trailingPE.{stat_key} expected 33.1; got {stats_pe[stat_key]}"
        )
    assert stats_pe["n"] == 1

    # anchor_delta uses peer's value as the median
    delta = payload["anchor_delta"]["trailingPE"]
    expected_pct = ((28.5 - 33.1) / 33.1) * 100
    assert delta["vs_median_pct"] == pytest.approx(expected_pct, abs=1e-3)
    # Anchor (28.5) cheaper than peer (33.1) → percentile = 1/2 = 0.5
    assert delta["percentile"] == pytest.approx(0.5, abs=1e-6)

    # Same collapse holds for another multiple
    stats_ps = payload["statistics"]["priceToSales"]
    for stat_key in ("median", "mean", "q1", "q3", "min", "max"):
        assert stats_ps[stat_key] == pytest.approx(11.0, abs=1e-6)


def test_all_peers_missing_a_multiple(runner, fixtures_dir):
    """All peers missing forwardPE → forwardPE statistics fall through cleanly.

    When every peer has forwardPE = null, the script's per-multiple peer_values
    list is empty; stats fall through the n=0 fallback (using the anchor's
    value), and anchor_delta short-circuits via the empty-peers branch
    (vs_median_pct = 0.0, percentile = 0.5). Other multiples remain valid.
    """
    peers = _peers_arg(
        fixtures_dir,
        "comps_peer_googl_no_fwd_pe.json",
        "comps_peer_meta_no_fwd_pe.json",
    )
    res = runner(
        COMPS_SCRIPT,
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", peers,
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)

    # forwardPE: peer values empty → n=0; per source contract stats use the
    # anchor-fallback values, but the key invariant is no crash + n=0.
    fwd = payload["statistics"]["forwardPE"]
    assert fwd["n"] == 0

    # anchor_delta.forwardPE must NOT crash; empty-peers branch returns
    # vs_median_pct=0.0 and percentile=0.5 per _anchor_delta source.
    fwd_delta = payload["anchor_delta"]["forwardPE"]
    assert fwd_delta is not None
    assert fwd_delta["value"] == pytest.approx(25.1)  # anchor's forwardPE
    assert fwd_delta["vs_median_pct"] == pytest.approx(0.0, abs=1e-6)
    assert fwd_delta["percentile"] == pytest.approx(0.5, abs=1e-6)

    # Other 4 multiples computed normally — peer set is valid for them.
    # trailingPE peer values [24.5, 26.0]: median = 25.25, n = 2
    tpe = payload["statistics"]["trailingPE"]
    assert tpe["n"] == 2
    assert tpe["median"] == pytest.approx(25.25, abs=1e-6)
    assert tpe["min"] == pytest.approx(24.5, abs=1e-6)
    assert tpe["max"] == pytest.approx(26.0, abs=1e-6)


# ---------------------------------------------------------------------------
# --rationale-map flag
# ---------------------------------------------------------------------------


def test_rationale_map_populates_peers(runner, fixtures_dir):
    res = runner(
        COMPS_SCRIPT,
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
        "--rationale-map", str(fixtures_dir / "comps_rationale_map.json"),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    rationales = {p["ticker"]: p["rationale"] for p in payload["peers"]}
    assert rationales.get("MSFT") == "Direct big-tech cloud competitor"
    assert rationales.get("GOOGL") == "Hyperscaler tier"
    assert rationales.get("META") == "Social/AI scale"
    assert rationales.get("AMZN") == "Marketplace + AWS"


def test_rationale_null_without_map(baseline_payload):
    for p in baseline_payload["peers"]:
        assert p["rationale"] is None, (
            f"peer {p['ticker']} rationale should be null without --rationale-map; got {p['rationale']!r}"
        )


def test_rationale_map_partial_coverage(runner, fixtures_dir):
    """Peer absent from --rationale-map gets rationale=null; mapped peers unaffected.

    Localizes a common user mis-config: typo'd ticker in the rationale map, or
    the user added a 5th peer to --peers but forgot to extend the map. The
    script must populate rationales for tickers that appear in the map and
    leave rationale=null for peers absent from the map (rather than crashing
    or applying a wrong rationale).

    Setup: pass anchor + 5 peers (MSFT, GOOGL, META, AMZN, NVDA) but
    comps_rationale_map.json only covers the first 4. NVDA must come back
    with rationale=null while the other 4 keep their rationale strings.
    """
    peers = _peers_arg(
        fixtures_dir,
        "comps_peer_msft.json",
        "comps_peer_googl.json",
        "comps_peer_meta.json",
        "comps_peer_amzn.json",
        "comps_peer_nvda.json",
    )
    res = runner(
        COMPS_SCRIPT,
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", peers,
        "--rationale-map", str(fixtures_dir / "comps_rationale_map.json"),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    rationales = {p["ticker"]: p["rationale"] for p in payload["peers"]}
    # Mapped peers keep their rationale strings.
    assert rationales.get("MSFT") == "Direct big-tech cloud competitor"
    assert rationales.get("GOOGL") == "Hyperscaler tier"
    assert rationales.get("META") == "Social/AI scale"
    assert rationales.get("AMZN") == "Marketplace + AWS"
    # NVDA absent from map → rationale stays null (not omitted, not a typo'd value).
    assert "NVDA" in rationales, "NVDA peer should still appear in output"
    assert rationales["NVDA"] is None, (
        f"NVDA absent from rationale-map; expected rationale=null, got {rationales['NVDA']!r}"
    )


# ---------------------------------------------------------------------------
# Pure-compute discipline (AST scan — no HTTP / subprocess / yfinance)
# ---------------------------------------------------------------------------


FORBIDDEN_IMPORTS = {
    "requests",
    "urllib",
    "httpx",
    "aiohttp",
    "subprocess",
    "yfinance",
    "socket",
}


def _collect_all_imports(script_path: Path) -> set[str]:
    """Walks every Import / ImportFrom node in the AST, including those nested
    inside functions or conditional blocks (e.g. lazy imports)."""
    tree = ast.parse(script_path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0])
    return names


def test_pure_compute_imports():
    """analysis-comps Layer 2 contract: no network / yfinance / subprocess imports."""
    imports = _collect_all_imports(COMPS_SCRIPT)
    leaked = imports & FORBIDDEN_IMPORTS
    assert not leaked, f"comps_compute.py imports forbidden modules: {leaked}"


# ---------------------------------------------------------------------------
# Compute mode — argparse + memo-fetch loader
# ---------------------------------------------------------------------------


def _anchor_base_arg(fixtures_dir):
    return str(fixtures_dir / "comps_anchor_aapl_memo_fetch.json")


def test_compute_mode_requires_anchor_base(runner, fixtures_dir):
    """--mode compute without --anchor-base must exit with helpful error."""
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 2, f"expected exit 2, got {res.returncode}"
    assert "anchor-base" in res.stderr.lower()


def test_direct_mode_warns_on_unused_anchor_base(runner, fixtures_dir):
    """--mode direct --anchor-base x.json: warn, continue with direct."""
    res = runner(
        COMPS_SCRIPT,
        "--mode", "direct",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", _anchor_base_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    assert "ignored" in res.stderr.lower() or "direct" in res.stderr.lower()
    payload = json.loads(res.stdout)
    assert "multiples_direct" in payload["anchor"]
    assert "multiples_compute" not in payload["anchor"]


def test_anchor_base_wrong_pack_errors(runner, tmp_path, fixtures_dir):
    """--anchor-base file with pack != 'memo-fetch' → exit 1."""
    bad = tmp_path / "wrong.json"
    bad.write_text(json.dumps({"pack": "snapshot", "ticker": "AAPL"}))
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", str(bad),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 1
    assert "memo-fetch" in res.stderr.lower()


def test_anchor_base_ticker_mismatch_errors(runner, tmp_path, fixtures_dir):
    """--anchor ticker AAPL, --anchor-base ticker MSFT → exit 1."""
    mismatch = tmp_path / "mismatch.json"
    mismatch.write_text(json.dumps({
        "pack": "memo-fetch", "ticker": "MSFT",
        "company_info": {}, "current_price": 0.0, "shares_outstanding": 1,
        "income_statement": {"revenue": [1.0], "net_income": [1.0]},
        "balance_sheet": {}, "_provenance": {}
    }))
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", str(mismatch),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 1
    assert "ticker" in res.stderr.lower()


# ---------------------------------------------------------------------------
# Compute mode — multiples recompute
# ---------------------------------------------------------------------------


@pytest.fixture
def compute_payload(runner, fixtures_dir):
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", _anchor_base_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    return json.loads(res.stdout)


def test_compute_mode_recomputes_trailingPE_FY(compute_payload):
    """trailingPE = current_price / (net_income[0] / shares_outstanding) — FY, not TTM."""
    actual = compute_payload["anchor"]["multiples_compute"]["trailingPE"]
    expected = 280.14 / (112010000000.0 / 14667688000)  # 36.6817
    assert actual == pytest.approx(expected, rel=1e-4)


def test_compute_mode_recomputes_priceToSales_FY(compute_payload):
    """priceToSales = marketCap / revenue[0] — FY."""
    actual = compute_payload["anchor"]["multiples_compute"]["priceToSales"]
    expected = 4109006274560 / 416161000000.0  # 9.8736
    assert actual == pytest.approx(expected, rel=1e-4)


def test_compute_mode_forwardPE_passthrough(compute_payload):
    """forwardPE pass-through from --anchor; computed:false in provenance."""
    direct_fwd = compute_payload["anchor"]["multiples_direct"]["forwardPE"]
    compute_fwd = compute_payload["anchor"]["multiples_compute"]["forwardPE"]
    assert compute_fwd == direct_fwd
    assert compute_payload["anchor"]["compute_provenance"]["forwardPE"]["computed"] is False


def test_compute_mode_recomputes_priceToBook_FY(compute_payload):
    """priceToBook = market_cap / total_stockholders_equity[0] — FY (v2.2.0-l)."""
    actual = compute_payload["anchor"]["multiples_compute"]["priceToBook"]
    expected = 4109006274560 / 66790000000.0  # 61.5212
    assert actual == pytest.approx(expected, rel=1e-4)


def test_compute_priceToBook_provenance(compute_payload):
    """priceToBook provenance records numerator/denominator + FY end + accession."""
    prov = compute_payload["anchor"]["compute_provenance"]["priceToBook"]
    assert prov["computed"] is True
    assert prov["numerator_source"] == "memo-fetch.company_info.marketCap"
    assert prov["denominator_source"] == "memo-fetch.balance_sheet.total_stockholders_equity[0]"
    assert prov["fiscal_year_end"] == "2025-09-27"
    assert "10-K filed 2025-10-31" in prov["accession_basis"]


def test_compute_mode_recomputes_evEbitda_FY(compute_payload):
    """evEbitda = (mcap + total_debt[0] - cash[0]) / (operating_income[0] + D&A[0]) — FY (v2.2.0-l)."""
    actual = compute_payload["anchor"]["multiples_compute"]["evEbitda"]
    enterprise_value = 4109006274560 + 90678000000 - 35934000000  # 4,163,750,274,560
    ebitda = 133050000000.0 + 11445000000.0  # 144,495,000,000
    expected = enterprise_value / ebitda  # 28.8160
    assert actual == pytest.approx(expected, rel=1e-4)


def test_compute_evEbitda_provenance(compute_payload):
    """evEbitda provenance records EV + EBITDA derivation + FY end."""
    prov = compute_payload["anchor"]["compute_provenance"]["evEbitda"]
    assert prov["computed"] is True
    assert prov["numerator_source"] == "memo-fetch.company_info.marketCap + balance_sheet.total_debt[0] - balance_sheet.cash[0]"
    assert prov["denominator_source"] == "memo-fetch.income_statement.operating_income[0] + cash_flow.depreciation_amortization[0]"
    assert prov["fiscal_year_end"] == "2025-09-27"
    assert "10-K filed 2025-10-31" in prov["accession_basis"]


def test_compute_provenance_includes_fiscal_year_end(compute_payload):
    """Each computed multiple records FY end date + accession_basis."""
    prov = compute_payload["anchor"]["compute_provenance"]
    for m in ("trailingPE", "priceToSales", "priceToBook", "evEbitda"):
        assert prov[m]["computed"] is True, f"{m} should be computed (v2.2.0-l)"
        assert prov[m]["fiscal_year_end"] == "2025-09-27", f"{m} FY end mismatch"
        assert "10-K filed 2025-10-31" in prov[m]["accession_basis"], f"{m} accession_basis missing"


# ---------------------------------------------------------------------------
# Compute mode — divergence
# ---------------------------------------------------------------------------


def test_divergence_block_present(compute_payload):
    div = compute_payload["anchor"]["divergence"]
    for m in ("trailingPE", "forwardPE", "priceToSales", "priceToBook", "evEbitda"):
        assert m in div


def test_divergence_alert_high_for_trailing_pe_aapl(compute_payload):
    """AAPL: direct=28.5 (fixture) vs compute=36.68 → pct_diff ≈ 28.7% → high."""
    div = compute_payload["anchor"]["divergence"]["trailingPE"]
    assert div["alert"] == "high"
    assert div["pct_diff"] == pytest.approx(28.7, abs=0.5)


def test_divergence_alert_n_a_for_forwardPE(compute_payload):
    """forwardPE pass-through → divergence is exactly 0; alert n/a."""
    div = compute_payload["anchor"]["divergence"]["forwardPE"]
    assert div["alert"] == "n/a"
    assert "pass-through" in div["note"]


def test_divergence_alert_high_for_priceToBook_aapl(compute_payload):
    """AAPL: direct=35.4 (fixture) vs compute≈61.52 → pct_diff ≈ +73.7% → high.
    Wide divergence is expected & informative — large buybacks shrink book equity
    relative to TTM-LTM convention used by yfinance.
    """
    div = compute_payload["anchor"]["divergence"]["priceToBook"]
    assert div["alert"] == "high"
    assert div["pct_diff"] == pytest.approx(73.7, abs=1.0)


def test_divergence_alert_high_for_evEbitda_aapl(compute_payload):
    """AAPL: direct=21.3 (fixture) vs compute≈28.82 → pct_diff ≈ +35.3% → high.
    EBIT+D&A FY-trailing vs LTM-EBITDA convention — gap expected.
    """
    div = compute_payload["anchor"]["divergence"]["evEbitda"]
    assert div["alert"] == "high"
    assert div["pct_diff"] == pytest.approx(35.3, abs=1.0)


def test_divergence_alert_low_at_5_percent_boundary(tmp_path, runner):
    """Synthetic anchor: direct=10.0, compute=10.5 → pct_diff=5.0% → low (≤ inclusive)."""
    anchor = tmp_path / "anchor.json"
    anchor.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": "X",
        "info": {"X": {"trailingPE": 10.0, "forwardPE": 10.0, "priceToSales": 1.0, "priceToBook": 1.0, "enterpriseToEbitda": 1.0}},
        "_provenance": {"skill": "test"}
    }))
    base = tmp_path / "base.json"
    # net_income / shares = 10.5 EPS; price 110.25 → trailingPE compute = 10.5
    base.write_text(json.dumps({
        "pack": "memo-fetch", "ticker": "X",
        "company_info": {"regularMarketPrice": 110.25, "sharesOutstanding": 1, "marketCap": 110.25},
        "current_price": 110.25, "shares_outstanding": 1,
        "income_statement": {"revenue": [105.0], "net_income": [10.5], "_meta": {"revenue": {"fiscal_year_ends": ["2025-12-31"], "filings_used": ["10-K"]}, "net_income": {"fiscal_year_ends": ["2025-12-31"], "filings_used": ["10-K"]}}},
        "balance_sheet": {}, "_provenance": {}
    }))
    peer = tmp_path / "peer.json"
    peer.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": "Y",
        "info": {"Y": {"trailingPE": 12.0}}, "_provenance": {"skill": "test"}
    }))
    res = runner(COMPS_SCRIPT, "--mode", "compute",
                 "--anchor", str(anchor), "--anchor-base", str(base), "--peers", str(peer))
    payload = json.loads(res.stdout)
    div = payload["anchor"]["divergence"]["trailingPE"]
    assert div["pct_diff"] == pytest.approx(5.0, abs=0.01)
    assert div["alert"] == "low"


def test_divergence_alert_medium_at_15_percent_boundary(tmp_path, runner):
    """direct=10.0, compute=11.5 → pct_diff=15.0% → medium (> 15% is high)."""
    anchor = tmp_path / "anchor.json"
    anchor.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": "X",
        "info": {"X": {"trailingPE": 10.0, "forwardPE": 10.0, "priceToSales": 1.0, "priceToBook": 1.0, "enterpriseToEbitda": 1.0}},
        "_provenance": {"skill": "test"}
    }))
    base = tmp_path / "base.json"
    base.write_text(json.dumps({
        "pack": "memo-fetch", "ticker": "X",
        "company_info": {"regularMarketPrice": 11.5, "sharesOutstanding": 1, "marketCap": 11.5},
        "current_price": 11.5, "shares_outstanding": 1,
        "income_statement": {"revenue": [1.0], "net_income": [1.0], "_meta": {"revenue": {"fiscal_year_ends": ["2025-12-31"], "filings_used": ["10-K"]}, "net_income": {"fiscal_year_ends": ["2025-12-31"], "filings_used": ["10-K"]}}},
        "balance_sheet": {}, "_provenance": {}
    }))
    peer = tmp_path / "peer.json"
    peer.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": "Y",
        "info": {"Y": {"trailingPE": 12.0}}, "_provenance": {"skill": "test"}
    }))
    res = runner(COMPS_SCRIPT, "--mode", "compute",
                 "--anchor", str(anchor), "--anchor-base", str(base), "--peers", str(peer))
    payload = json.loads(res.stdout)
    div = payload["anchor"]["divergence"]["trailingPE"]
    assert div["pct_diff"] == pytest.approx(15.0, abs=0.01)
    assert div["alert"] == "medium"


# ---------------------------------------------------------------------------
# Compute mode — missing-data guards (spec §8.2)
# ---------------------------------------------------------------------------


def test_compute_mode_skips_trailingPE_when_net_income_empty(tmp_path, runner, fixtures_dir):
    """net_income[] empty → trailingPE compute null + warning."""
    base = tmp_path / "base.json"
    base.write_text(json.dumps({
        "pack": "memo-fetch", "ticker": "AAPL",
        "company_info": {"regularMarketPrice": 280.14, "sharesOutstanding": 14667688000, "marketCap": 4109006274560},
        "current_price": 280.14, "shares_outstanding": 14667688000,
        "income_statement": {
            "revenue": [416161000000.0],
            "net_income": [],
            "_meta": {"revenue": {"fiscal_year_ends": ["2025-09-27"], "filings_used": ["10-K filed 2025-10-31"]}, "net_income": {"fiscal_year_ends": ["2025-09-27"], "filings_used": ["10-K filed 2025-10-31"]}}
        },
        "balance_sheet": {}, "_provenance": {}
    }))
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", str(base),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["anchor"]["multiples_compute"]["trailingPE"] is None
    assert payload["anchor"]["divergence"]["trailingPE"]["alert"] == "n/a"
    assert any("net_income" in w for w in payload["_provenance"]["warnings"])


def test_compute_mode_skips_priceToSales_when_revenue_empty(tmp_path, runner, fixtures_dir):
    """revenue[] empty → priceToSales compute null + warning."""
    base = tmp_path / "base.json"
    base.write_text(json.dumps({
        "pack": "memo-fetch", "ticker": "AAPL",
        "company_info": {"regularMarketPrice": 280.14, "sharesOutstanding": 14667688000, "marketCap": 4109006274560},
        "current_price": 280.14, "shares_outstanding": 14667688000,
        "income_statement": {
            "revenue": [],
            "net_income": [112010000000.0],
            "_meta": {"revenue": {"fiscal_year_ends": ["2025-09-27"], "filings_used": ["10-K filed 2025-10-31"]}, "net_income": {"fiscal_year_ends": ["2025-09-27"], "filings_used": ["10-K filed 2025-10-31"]}}
        },
        "balance_sheet": {}, "_provenance": {}
    }))
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", str(base),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["anchor"]["multiples_compute"]["priceToSales"] is None
    assert payload["anchor"]["divergence"]["priceToSales"]["alert"] == "n/a"
    assert any("revenue" in w for w in payload["_provenance"]["warnings"])


def test_compute_mode_handles_negative_net_income(tmp_path, runner, fixtures_dir):
    """net_income[0] < 0 → trailingPE compute negative; divergence still computed."""
    base = tmp_path / "base.json"
    base.write_text(json.dumps({
        "pack": "memo-fetch", "ticker": "AAPL",
        "company_info": {"regularMarketPrice": 100.0, "sharesOutstanding": 1000000000, "marketCap": 100000000000},
        "current_price": 100.0, "shares_outstanding": 1000000000,
        "income_statement": {
            "revenue": [50000000000.0],
            "net_income": [-5000000000.0],
            "_meta": {"revenue": {"fiscal_year_ends": ["2025-09-27"], "filings_used": ["10-K"]}, "net_income": {"fiscal_year_ends": ["2025-09-27"], "filings_used": ["10-K"]}}
        },
        "balance_sheet": {}, "_provenance": {}
    }))
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", str(base),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    pe = payload["anchor"]["multiples_compute"]["trailingPE"]
    assert pe is not None
    assert pe < 0  # 100 / (-5/1) = -20
    # divergence is still computed (analyst interprets the negative value)
    div = payload["anchor"]["divergence"]["trailingPE"]
    assert div["alert"] in {"low", "medium", "high"}


def test_compute_evEbitda_handles_zero_ebitda(tmp_path, runner, fixtures_dir):
    """Synthetic anchor where EBIT[0] + D&A[0] == 0 → evEbitda compute null + warning."""
    anchor = tmp_path / "anchor.json"
    anchor.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": "X",
        "info": {"X": {"trailingPE": 10.0, "forwardPE": 10.0, "priceToSales": 1.0, "priceToBook": 1.0, "enterpriseToEbitda": 5.0}},
        "_provenance": {"skill": "test"}
    }))
    base = tmp_path / "base.json"
    # negative EBIT exactly offsets positive D&A → ebitda == 0
    base.write_text(json.dumps({
        "pack": "memo-fetch", "ticker": "X",
        "company_info": {"regularMarketPrice": 100.0, "sharesOutstanding": 1000, "marketCap": 100000.0},
        "current_price": 100.0, "shares_outstanding": 1000,
        "income_statement": {"revenue": [1000.0], "net_income": [10.0], "operating_income": [-50.0],
                             "_meta": {"revenue": {"fiscal_year_ends": ["2025-12-31"], "filings_used": ["10-K"]},
                                       "net_income": {"fiscal_year_ends": ["2025-12-31"], "filings_used": ["10-K"]}}},
        "cash_flow": {"depreciation_amortization": [50.0],
                      "_meta": {"depreciation_amortization": {"fiscal_year_ends": ["2025-12-31"], "filings_used": ["10-K"]}}},
        "balance_sheet": {"total_debt": [10000.0], "cash": [5000.0], "total_stockholders_equity": [50000.0],
                          "_meta": {"total_stockholders_equity": {"fiscal_year_ends": ["2025-12-31"], "filings_used": ["10-K"]}}},
        "_provenance": {}
    }))
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", str(anchor),
        "--anchor-base", str(base),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["anchor"]["multiples_compute"]["evEbitda"] is None
    assert payload["anchor"]["compute_provenance"]["evEbitda"]["computed"] is False
    assert "EBITDA" in payload["anchor"]["compute_provenance"]["evEbitda"]["note"]


# ---------------------------------------------------------------------------
# Compute mode — provenance + warnings
# ---------------------------------------------------------------------------


def test_provenance_anchor_base_source_present_only_in_compute(compute_payload, baseline_payload):
    """_provenance.anchor_base_source is populated in compute mode, absent in direct mode."""
    assert "anchor_base_source" in compute_payload["_provenance"]
    assert "memo-fetch" in compute_payload["_provenance"]["anchor_base_source"]
    assert "anchor_base_source" not in baseline_payload["_provenance"]


def test_warnings_carry_FY_vs_TTM_definitional_note(compute_payload):
    """Every compute-mode run must carry the FY-not-TTM systematic-divergence warning."""
    warnings = compute_payload["_provenance"]["warnings"]
    matched = [w for w in warnings if "TTM" in w and "FY" in w]
    assert matched, f"FY-vs-TTM warning missing from warnings: {warnings}"


# ---------------------------------------------------------------------------
# Direct-mode byte-equal regression (spec §10.1)
# ---------------------------------------------------------------------------


def test_direct_mode_output_shape_v2_0_0_locked(baseline_payload):
    """Direct mode output must have exactly these top-level + anchor keys.
    Locks the v2.0.0 shape (post-Phase-1 rename) against future regression.
    """
    assert set(baseline_payload.keys()) == {"anchor", "peers", "statistics", "anchor_delta", "ranking", "_provenance"}
    # Anchor in direct mode: ONLY ticker + multiples_direct (no compute keys leak)
    assert set(baseline_payload["anchor"].keys()) == {"ticker", "multiples_direct"}
    assert "multiples_compute" not in baseline_payload["anchor"]
    assert "divergence" not in baseline_payload["anchor"]
    assert "compute_provenance" not in baseline_payload["anchor"]
    # Direct-mode _provenance shape — no anchor_base_source key
    assert "anchor_base_source" not in baseline_payload["_provenance"]
    assert baseline_payload["_provenance"]["mode"] == "direct"


# ---------------------------------------------------------------------------
# Tier 1 test-discipline additions (v2.2.0-b follow-up)
# ---------------------------------------------------------------------------


def test_direct_mode_byte_equal_golden_aapl(runner, fixtures_dir):
    """Direct-mode output for the canonical AAPL anchor + 4 peers must match
    a checked-in golden file modulo the computed_at timestamp. Locks the
    v2.0.0-byte-equal contract (post-Phase-1 multiples_direct rename) against
    accidental schema drift in future PRs.

    If this test fails, the change is either intentional (regenerate the golden
    via the command in the assertion message) or an accidental regression.
    """
    res = runner(
        COMPS_SCRIPT,
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr

    actual = json.loads(res.stdout)
    actual["_provenance"].pop("computed_at", None)

    golden_path = fixtures_dir / "comps_compute_direct_golden_aapl.json"
    expected = json.loads(golden_path.read_text())
    expected["_provenance"].pop("computed_at", None)

    assert actual == expected, (
        "Direct-mode output diverged from golden file. If this change is "
        "intentional, regenerate the golden via:\n"
        f"  uv run skills/analysis-comps/scripts/comps_compute.py --mode direct "
        f"--anchor tests/analysis/fixtures/comps_anchor_aapl.json "
        f"--peers tests/analysis/fixtures/comps_peer_msft.json,"
        f"tests/analysis/fixtures/comps_peer_googl.json,"
        f"tests/analysis/fixtures/comps_peer_meta.json,"
        f"tests/analysis/fixtures/comps_peer_amzn.json"
        f" > {golden_path}\n"
        "and remove _provenance.computed_at from the new golden."
    )


# ---------------------------------------------------------------------------
# F — Compute output schema validator (v2.2.0-b Tier 2)
# ---------------------------------------------------------------------------


def test_compute_output_has_documented_shape(compute_payload):
    """Verify the output has all the keys the schema-compute-output.json
    documents. (Full JSON Schema validation requires the jsonschema package;
    this is a manual structural subset check that runs without it.)

    Locks the compute-mode output shape (spec §10) against drift:
    missing fields, renamed keys, wrong enum values in divergence.alert,
    or absent compute_provenance.computed flags.
    """
    anchor = compute_payload["anchor"]
    for k in ("ticker", "multiples_direct", "multiples_compute", "divergence", "compute_provenance"):
        assert k in anchor, f"anchor missing key: {k}"

    for m in ("trailingPE", "forwardPE", "evEbitda", "priceToSales", "priceToBook"):
        assert m in anchor["multiples_direct"], f"multiples_direct missing {m}"
        assert m in anchor["multiples_compute"], f"multiples_compute missing {m}"
        assert m in anchor["divergence"], f"divergence missing {m}"
        assert m in anchor["compute_provenance"], f"compute_provenance missing {m}"
        assert anchor["divergence"][m]["alert"] in {"low", "medium", "high", "n/a"}, (
            f"divergence[{m}].alert has invalid value: {anchor['divergence'][m]['alert']!r}"
        )
        assert "computed" in anchor["compute_provenance"][m], (
            f"compute_provenance[{m}] missing 'computed' flag"
        )

    prov = compute_payload["_provenance"]
    for k in ("skill", "anchor_data_source", "anchor_base_source", "peer_data_sources",
              "computed_at", "io", "mode", "requested_mode", "warnings"):
        assert k in prov, f"_provenance missing key: {k}"
    assert prov["skill"] == "analysis-comps", (
        f"_provenance.skill should be 'analysis-comps', got {prov['skill']!r}"
    )
    assert prov["mode"] == "compute", (
        f"_provenance.mode should be 'compute', got {prov['mode']!r}"
    )
    assert prov["io"] == "none", (
        f"_provenance.io should be 'none' (Layer 2 pure-compute), got {prov['io']!r}"
    )


def test_forwardPE_missing_in_anchor_emits_null_with_alert_n_a(tmp_path, runner, fixtures_dir):
    """When --anchor comps-multiples pack lacks forwardPE, compute mode emits
    null in multiples_compute.forwardPE and divergence.forwardPE.alert == n/a
    via the early-null branch (not the pass-through special-case).

    Closes reviewer M2 gap: the early-null branch in _compute_divergence
    (where compute or direct is None) is correct but unexercised for
    forwardPE specifically. Recently-IPO'd companies hit this path.
    """
    anchor_no_fwd = tmp_path / "anchor_no_fwd.json"
    anchor_no_fwd.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": "AAPL",
        "info": {
            "AAPL": {
                "trailingPE": 28.5,
                # forwardPE intentionally omitted
                "priceToSales": 7.2,
                "priceToBook": 35.4,
                "enterpriseToEbitda": 21.3,
            }
        },
        "_provenance": {"skill": "data-us", "source": "test"},
    }))
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", str(anchor_no_fwd),
        "--anchor-base", _anchor_base_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["anchor"]["multiples_direct"].get("forwardPE") is None
    assert payload["anchor"]["multiples_compute"]["forwardPE"] is None
    assert payload["anchor"]["divergence"]["forwardPE"]["alert"] == "n/a"
