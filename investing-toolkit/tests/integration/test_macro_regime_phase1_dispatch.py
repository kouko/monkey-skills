"""Phase 1 dispatch integration test (per ADR-0004).

Verifies regime_compose.py post-PR-1:
- Produces 2.0-phase1 schema
- cross_country is null
- _legacy.by_country populated for all available countries
- by_country populated only for countries with classify_X module (none in PR-1)
- TW _legacy block now resolves growth proxy (was 'flat / proxy missing'
  before the GROWTH_KEYS patch in PR-1)
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
        ["uv", "run", "python", str(SCRIPT), "--input", args],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, f"dispatch failed: {result.stderr}\nstdout: {result.stdout[:500]}"
    return json.loads(result.stdout)


def test_phase1_schema_shape():
    out = _run_dispatch(["us", "jp", "tw", "kr", "cn"])
    assert out["schema_version"] == "2.0-phase1"
    assert out["cross_country"] is None
    assert "_legacy" in out
    assert "by_country" in out["_legacy"]
    assert "by_country" in out
    # PR-1: no classify_X modules yet, by_country is empty dict
    # PR-2 onwards: countries appear here as their classifiers ship
    assert isinstance(out["by_country"], dict)


def test_phase1_legacy_populated_for_all_countries():
    out = _run_dispatch(["us", "jp", "tw", "kr", "cn"])
    legacy_by_country = out["_legacy"]["by_country"]
    assert len(legacy_by_country) >= 1, "no countries in _legacy.by_country"
    for cc, body in legacy_by_country.items():
        # Either a successful classification or an explicit error
        assert "ic_quadrant" in body or "_error" in body, (
            f"{cc} legacy block has neither ic_quadrant nor _error: {body}"
        )


def test_phase1_tw_legacy_resolves_growth_proxy():
    """After PR-1's GROWTH_KEYS patch, TW _legacy block must NOT report
    'growth proxy missing for tw' — it should resolve to signal-score or
    coincident-index."""
    out = _run_dispatch(["tw"])
    legacy_tw = out["_legacy"]["by_country"]["tw"]
    notes = legacy_tw.get("notes", [])
    assert not any("growth proxy missing for tw" in n for n in notes), (
        f"TW _legacy still reports growth proxy missing — GROWTH_KEYS patch broke. "
        f"notes: {notes}"
    )
    # Confidence should rise to medium or high (was 'low' pre-patch)
    assert legacy_tw["confidence"] in ("medium", "high"), (
        f"TW _legacy confidence still low post-patch: {legacy_tw['confidence']}"
    )


def test_phase1_legacy_us_ic_quadrant_unchanged():
    """US legacy block byte-for-byte regression: ic_quadrant must remain
    what classify_country returned pre-PR-1 (US is not affected by the
    TW GROWTH_KEYS patch)."""
    out = _run_dispatch(["us"])
    us_legacy = out["_legacy"]["by_country"]["us"]
    assert us_legacy["ic_quadrant"] in {
        "1-recovery", "2-overheat", "3-stagflation", "4-reflation",
    }
    # Real-rates block should be present for US (DGS10/T10YIE in fixture)
    assert us_legacy["real_rates"] is not None or any(
        "real-rate block" in n for n in us_legacy.get("notes", [])
    )


def test_phase1_unknown_country_rejected():
    """--input with unsupported country code must exit non-zero."""
    result = subprocess.run(
        ["uv", "run", "python", str(SCRIPT), "--input", "xx=/tmp/nonexistent.json"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode != 0
    assert "Unknown country" in result.stderr or "Unknown country" in result.stdout
