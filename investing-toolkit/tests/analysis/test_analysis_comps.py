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
    assert "multiples" in anchor
    expected = {"trailingPE", "forwardPE", "evEbitda", "priceToSales", "priceToBook"}
    assert expected <= set(anchor["multiples"].keys()), (
        f"anchor.multiples missing keys; got {set(anchor['multiples'].keys())}"
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
