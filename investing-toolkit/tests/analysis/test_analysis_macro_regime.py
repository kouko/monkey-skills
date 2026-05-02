"""Tests for analysis-macro-regime/scripts/regime_compose.py (Phase 1).

Per ADR-0004 PR-7: regime_compose.py is now a thin dispatcher;
classify_X output lives at out["by_country"][cc]. The legacy IC
unified classifier was removed; out["_legacy"] is null.
"""
from __future__ import annotations

import json

import pytest

from conftest import REGIME_SCRIPT, run_script


def test_help_runs(runner):
    res = runner(REGIME_SCRIPT, "--help")
    assert res.returncode == 0


def test_smoke_us_only(runner, fixtures_dir):
    res = runner(
        REGIME_SCRIPT,
        "--input", f"us={fixtures_dir / 'regime_us_fixture.json'}",
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert "by_country" in payload
    assert "us" in payload["by_country"]
    assert payload["_legacy"] is None  # PR-7 cleanup


def test_schema_us(runner, fixtures_dir):
    res = runner(
        REGIME_SCRIPT,
        "--input", f"us={fixtures_dir / 'regime_us_fixture.json'}",
    )
    payload = json.loads(res.stdout)
    us = payload["by_country"]["us"]
    # CountryRegimeCard envelope (per ADR-0004 §"Country regime card shape")
    for key in ("country", "framework_used", "native_verdict",
                "indicators_used", "data_quality", "confidence", "provenance"):
        assert key in us, f"missing envelope key: {key}"
    assert us["country"] == "us"
    assert us["confidence"] in {"low", "medium", "high"}
    nv = us["native_verdict"]
    assert "framework_label" in nv
    assert nv["ic_quadrant"] in {
        "1-recovery", "2-overheat", "3-stagflation", "4-reflation"
    }
    assert nv["gip_regime"] in {"quad1", "quad2", "quad3", "quad4"}
    # Real-rate decomposition (US-specific overlay) — 4-tier band
    rrd = nv.get("real_rate_decomposition")
    if rrd is not None:
        assert rrd["band"] in {
            "accommodative", "neutral",
            "moderately_restrictive", "clearly_restrictive",
        }
    # Provenance
    prov = us["provenance"]
    assert prov["calibration_doc"] == "thresholds-us.md"


def test_missing_input_file(runner):
    res = runner(REGIME_SCRIPT, "--input", "us=/tmp/does_not_exist_xyz.json")
    assert res.returncode != 0


def test_malformed_input_arg(runner, fixtures_dir):
    """--input fragment without `=` should error."""
    res = runner(REGIME_SCRIPT, "--input", "garbage_no_equals")
    assert res.returncode != 0


# ---------------------------------------------------------------------------
# Multi-country dispatch (cross_country deferred to Phase 2 per ADR-0004)
# ---------------------------------------------------------------------------


def test_5_country_dispatch(runner, fixtures_dir):
    """5-country dispatch produces 5 by_country entries; cross_country
    is null in Phase 1 (deferred to Phase 2 ADR-0005)."""
    res = runner(
        REGIME_SCRIPT,
        "--input",
        ",".join([
            f"us={fixtures_dir / 'regime_us_fixture.json'}",
            f"jp={fixtures_dir / 'regime_jp_fixture.json'}",
            f"tw={fixtures_dir / 'regime_tw_fixture.json'}",
            f"kr={fixtures_dir / 'regime_kr_fixture.json'}",
            f"cn={fixtures_dir / 'regime_cn_fixture.json'}",
        ]),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["cross_country"] is None
    assert payload["_legacy"] is None
    by_country = payload["by_country"]
    for cc in ("us", "jp", "tw", "kr", "cn"):
        assert cc in by_country
        assert by_country[cc]["country"] == cc


def test_single_country_phase1_shape(runner, fixtures_dir):
    """Single-country dispatch: cross_country is null (no consensus block)."""
    res = runner(
        REGIME_SCRIPT,
        "--input", f"us={fixtures_dir / 'regime_us_fixture.json'}",
    )
    payload = json.loads(res.stdout)
    assert payload["cross_country"] is None
    assert "cross_country_consensus" not in payload  # legacy v1.x key removed


# ---------------------------------------------------------------------------
# US Fisher real-rate decomposition (4-tier threshold) — Phase 1 native
# ---------------------------------------------------------------------------


def test_us_fisher_real_rate_clearly_restrictive(runner, fixtures_dir):
    """nominal=4.5, breakeven=2.5 → real ~2.0% → 'clearly_restrictive' (≥1.75)."""
    res = runner(
        REGIME_SCRIPT,
        "--input", f"us={fixtures_dir / 'regime_us_fixture.json'}",
    )
    payload = json.loads(res.stdout)
    rrd = payload["by_country"]["us"]["native_verdict"]["real_rate_decomposition"]
    assert rrd is not None, "real_rate_decomposition missing"
    assert abs(rrd["nominal_10y"] - 4.5) < 0.01
    assert abs(rrd["breakeven_10y"] - 2.5) < 0.01
    assert abs(rrd["real_10y"] - 2.0) < 0.01
    assert rrd["band"] == "clearly_restrictive"
