"""Phase 1 dispatch integration test (per ADR-0004).

Verifies regime_compose.py:
- Produces 2.0-phase1 schema
- cross_country is null
- _legacy is null (PR-7 cleanup removed v1.9.0 fallback)
- by_country populated for all 5 countries (US/JP/TW/KR/CN) via their
  per-country classify_X modules
- TW classifier resolves growth proxy (was 'flat / proxy missing' on
  legacy unified classifier before _helpers.py GROWTH_KEYS patch)
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]  # investing-toolkit/
SKILLS = ROOT / "skills"
FIXTURES = ROOT / "tests" / "data" / "fixtures"
SCRIPT = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"


def _run_dispatch(countries: list[str]) -> dict:
    available = [
        cc for cc in countries
        if (FIXTURES / f"data-{cc}-regime-pack-sample.json").exists()
    ]
    if not available:
        pytest.skip("no fixtures available for requested countries")
    args = ",".join(
        f"{cc}={FIXTURES / f'data-{cc}-regime-pack-sample.json'}"
        for cc in available
    )
    result = subprocess.run(
        ["uv", "run", str(SCRIPT), "--input", args],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, f"dispatch failed: {result.stderr}\nstdout: {result.stdout[:500]}"
    return json.loads(result.stdout)


def test_phase1_schema_shape():
    out = _run_dispatch(["us", "jp", "tw", "kr", "cn"])
    assert out["schema_version"] == "2.0-phase1"
    assert out["cross_country"] is None
    assert out["_legacy"] is None, (
        f"_legacy should be null after PR-7 cleanup; got: {out['_legacy']!r}"
    )
    assert "by_country" in out
    assert isinstance(out["by_country"], dict)


def test_phase1_by_country_populated_for_all_countries():
    out = _run_dispatch(["us", "jp", "tw", "kr", "cn"])
    by_country = out["by_country"]
    for cc in ["us", "jp", "tw", "kr", "cn"]:
        assert cc in by_country, (
            f"by_country missing country {cc} — classify_{cc} module not found "
            f"or raised. by_country keys: {list(by_country.keys())}"
        )
        block = by_country[cc]
        # Either a successful CountryRegimeCard envelope or an explicit error
        assert "_error" not in block, (
            f"{cc} classify_X raised: {block.get('_error')!r}"
        )
        assert block["country"] == cc
        assert "framework_used" in block
        assert "native_verdict" in block
        assert "framework_label" in block["native_verdict"]
        assert block["confidence"] in ("low", "medium", "high")


def test_phase1_tw_classifier_resolves_growth_proxy():
    """TW classifier reads NDC signal-score / coincident-index / leading-index
    from regime-pack via _helpers.GROWTH_KEYS["tw"] (patched in PR-1). Must
    NOT report 'growth proxy missing'. Confidence must be medium or high."""
    out = _run_dispatch(["tw"])
    tw = out["by_country"]["tw"]
    # New schema: native_verdict carries TW signal data, no notes-style
    # "growth proxy missing" message — but data_quality might list missing
    missing = tw.get("data_quality", {}).get("missing", []) or []
    assert not any("growth_proxy" in m for m in missing), (
        f"TW data_quality.missing reports growth proxy gap: {missing}"
    )
    assert tw["confidence"] in ("medium", "high"), (
        f"TW confidence still degraded post-PR-1 patch: {tw['confidence']}"
    )


def test_phase1_us_native_verdict_shape():
    """US classify_us produces ic_quadrant + real_rate_decomposition +
    yield_curve in native_verdict. Acts as a smoke test that the classifier
    chain (regime_compose → classify_us → calibrations/us.yaml) works."""
    out = _run_dispatch(["us"])
    us = out["by_country"]["us"]
    nv = us["native_verdict"]
    assert nv["ic_quadrant"] in {
        "1-recovery", "2-overheat", "3-stagflation", "4-reflation",
    }
    # Real-rate block should be present (DGS10/T10YIE in US fixture)
    rrd = nv.get("real_rate_decomposition")
    assert rrd is None or rrd.get("band") in {
        "accommodative", "neutral",
        "moderately_restrictive", "clearly_restrictive",
    }


def test_phase1_unknown_country_rejected():
    """--input with unsupported country code must exit non-zero."""
    result = subprocess.run(
        ["uv", "run", str(SCRIPT), "--input", "xx=/tmp/nonexistent.json"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode != 0
    assert "Unknown country" in result.stderr or "Unknown country" in result.stdout
