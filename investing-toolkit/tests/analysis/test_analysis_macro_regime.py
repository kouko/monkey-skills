"""Tests for analysis-macro-regime/scripts/regime_compose.py."""
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
    assert "countries" in payload
    assert "us" in payload["countries"]


def test_schema_us(runner, fixtures_dir):
    res = runner(
        REGIME_SCRIPT,
        "--input", f"us={fixtures_dir / 'regime_us_fixture.json'}",
    )
    payload = json.loads(res.stdout)
    us = payload["countries"]["us"]
    for key in (
        "growth_direction", "inflation_direction", "ic_quadrant",
        "gip_regime", "real_rates", "confidence", "notes",
    ):
        assert key in us, f"missing key: {key}"
    # IC quadrant in known set
    assert us["ic_quadrant"] in {"1-recovery", "2-overheat", "3-stagflation", "4-reflation"}
    assert us["gip_regime"] in {"quad1", "quad2", "quad3", "quad4"}
    # Real rates block present + 4-tier signal
    rr = us["real_rates"]
    assert rr is not None
    for key in ("nominal_10y", "breakeven_10y", "real_10y", "signal"):
        assert key in rr
    assert rr["signal"] in {
        "accommodative", "neutral", "moderately-restrictive", "clearly-restrictive",
    }
    # Provenance
    prov = payload["_provenance"]
    assert prov["skill"] == "analysis-macro-regime"


def test_missing_input_file(runner):
    res = runner(REGIME_SCRIPT, "--input", "us=/tmp/does_not_exist_xyz.json")
    assert res.returncode != 0


def test_malformed_input_arg(runner, fixtures_dir):
    """--input fragment without `=` should error."""
    res = runner(REGIME_SCRIPT, "--input", "garbage_no_equals")
    assert res.returncode != 0


# ---------------------------------------------------------------------------
# Multi-country / consensus
# ---------------------------------------------------------------------------


def test_5_country_emits_consensus(runner, fixtures_dir):
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
    assert "cross_country_consensus" in payload
    consensus = payload["cross_country_consensus"]
    assert consensus["ic_alignment"] in {"aligned", "divergent"}
    assert "regimes_present" in consensus


def test_single_country_no_consensus(runner, fixtures_dir):
    """Per spec: single country → no cross_country_consensus block."""
    res = runner(
        REGIME_SCRIPT,
        "--input", f"us={fixtures_dir / 'regime_us_fixture.json'}",
    )
    payload = json.loads(res.stdout)
    assert "cross_country_consensus" not in payload


# ---------------------------------------------------------------------------
# Wave 4 fix: flat-flat → 1-recovery (NOT 4-reflation)
# ---------------------------------------------------------------------------


def test_flat_growth_flat_inflation_is_recovery(runner, fixtures_dir):
    """flat growth + flat inflation → 1-recovery (Wave 4 fix; was 4-reflation)."""
    res = runner(
        REGIME_SCRIPT,
        "--input", f"us={fixtures_dir / 'regime_us_flat.json'}",
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    us = payload["countries"]["us"]
    assert us["growth_direction"] == "flat"
    assert us["inflation_direction"] == "flat"
    assert us["ic_quadrant"] == "1-recovery"


def test_flat_growth_rising_inflation_is_overheat(runner, fixtures_dir):
    """flat growth + rising inflation → 2-overheat."""
    res = runner(
        REGIME_SCRIPT,
        "--input", f"us={fixtures_dir / 'regime_us_overheat.json'}",
    )
    payload = json.loads(res.stdout)
    us = payload["countries"]["us"]
    assert us["growth_direction"] == "flat"
    assert us["inflation_direction"] == "rising"
    assert us["ic_quadrant"] == "2-overheat"


# ---------------------------------------------------------------------------
# US Fisher real-rate decomposition (4-tier threshold)
# ---------------------------------------------------------------------------


def test_us_fisher_real_rate_clearly_restrictive(runner, fixtures_dir):
    """nominal=4.5, breakeven=2.5 → real ~2.0% → 'clearly-restrictive' (≥1.75)."""
    res = runner(
        REGIME_SCRIPT,
        "--input", f"us={fixtures_dir / 'regime_us_fixture.json'}",
    )
    payload = json.loads(res.stdout)
    rr = payload["countries"]["us"]["real_rates"]
    assert abs(rr["nominal_10y"] - 4.5) < 0.01
    assert abs(rr["breakeven_10y"] - 2.5) < 0.01
    assert abs(rr["real_10y"] - 2.0) < 0.01
    assert rr["signal"] == "clearly-restrictive"


# ---------------------------------------------------------------------------
# JP / TW country-specific behaviour
# ---------------------------------------------------------------------------


def test_jp_real_rates_null(runner, fixtures_dir):
    """JP fixture without DGS10/T10YIE → real_rates is null (US-only block)."""
    res = runner(
        REGIME_SCRIPT,
        "--input", f"jp={fixtures_dir / 'regime_jp_no_rates.json'}",
    )
    payload = json.loads(res.stdout)
    jp = payload["countries"]["jp"]
    assert jp["real_rates"] is None


def test_tw_9_45_composite_note(runner, fixtures_dir):
    """TW score in 9-45 band → note text mentions '9-45'."""
    res = runner(
        REGIME_SCRIPT,
        "--input", f"tw={fixtures_dir / 'regime_tw_fixture.json'}",
    )
    payload = json.loads(res.stdout)
    notes = " ".join(payload["countries"]["tw"]["notes"])
    assert "9-45" in notes
