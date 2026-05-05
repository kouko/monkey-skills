"""Network smoke tests for v2.2.0-c-bench. Marked @pytest.mark.network — skipped
under default `pytest -m 'not network'` filter. Weekly CI runs them.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "analysis-comps" / "scripts"
AGG_SCRIPT = SCRIPTS / "etf_aggregator.py"
COMPS_SCRIPT = SCRIPTS / "comps_compute.py"

ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


@pytest.mark.network
def test_aggregate_xlk_live(tmp_path):
    """Real yfinance + memo-fetch run for XLK; output goes to tmp_path."""
    out_path = tmp_path / "xlk.json"
    proc = subprocess.run(
        ["uv", "run", str(AGG_SCRIPT), "--etf", "XLK", "--output", str(out_path)],
        capture_output=True, text=True, timeout=600, env=ENV, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr[-500:]
    assert out_path.exists()
    payload = json.loads(out_path.read_text())
    assert payload["etf"] == "XLK"
    assert payload["schema_id"] == "tech-saas"
    assert payload["_meta"]["holdings_count"] >= 10
    # tech-saas schema: forwardPE / priceToSales / evRevenue (no trailingPE).
    # Validated 2026-05-05 live: forwardPE often null pre-quarter; evRevenue
    # + priceToSales are reliable signals for SPDR Tech holdings.
    assert payload["multiples"].get("priceToSales") is not None
    assert payload["multiples"].get("evRevenue") is not None


@pytest.mark.network
def test_compute_with_sector_benchmark_aapl_live(tmp_path):
    """End-to-end live: real AAPL fetch + real comps_compute --sector-benchmark
    against the on-main aggregate JSONs (no env override).

    Pipeline exercised:
      data-us pack.py comps-multiples + memo-fetch
        → inject yfinance.info.sector/industry into the comps pack
        → comps_compute --mode compute --sector-benchmark
        → assert etf_benchmark block populated with bands

    AAPL routes through default schema → maps to XLB via inverse map.
    Test passes if AAPL fetch succeeds AND XLB aggregate exists on main.
    Test SKIPS gracefully if either upstream fails (yfinance, EDGAR) or
    the on-main XLB aggregate is missing — matches the pattern from
    test_comps_sector_compute.py for upstream-dependent network tests.
    """
    # Reuse the proven helper from test_comps_sector_compute (same module).
    import importlib.util
    import sys

    test_dir = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(
        "_sc", test_dir / "test_comps_sector_compute.py")
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)

    # 1. Live-fetch AAPL (yfinance + EDGAR through pack.py)
    anchor = sc._fetch_comps_multiples("AAPL", tmp_path)
    base = sc._fetch_memo_fetch("AAPL", tmp_path)
    peer = sc._fetch_comps_multiples("HPQ", tmp_path)  # default-schema peer

    # 2. Run runtime against the ON-MAIN aggregates (no AGGREGATES_DIR override)
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute",
         "--anchor", str(anchor),
         "--anchor-base", str(base),
         "--peers", str(peer),
         "--sector-benchmark"],
        capture_output=True, text=True, timeout=120, env=ENV, cwd=str(ROOT),
    )
    assert proc.returncode == 0, f"comps_compute failed: {proc.stderr[-500:]}"
    payload = json.loads(proc.stdout)
    bench = payload["anchor"].get("etf_benchmark") or {}

    # 3. Two acceptable outcomes:
    if bench.get("status") == "skipped":
        # On-main aggregate not yet committed (first-deploy pre-cron state).
        # Skip is the documented graceful fallback; this is not a test failure.
        pytest.skip(f"on-main aggregate missing: {bench.get('reason', '')[:120]}")

    # Aggregate present → expect populated block
    assert bench.get("etf"), f"etf_benchmark missing 'etf' field: {bench}"
    assert bench.get("schema_id"), f"etf_benchmark missing 'schema_id': {bench}"
    assert "multiples" in bench, f"populated block missing multiples: {bench}"
    assert bench["multiples"], "multiples dict is empty"

    # At least one multiple should be banded with a numeric delta_pct
    banded_count = sum(
        1 for m in bench["multiples"].values()
        if m.get("band") in ("in_line", "notable", "extreme")
        and isinstance(m.get("delta_pct"), (int, float))
    )
    assert banded_count >= 1, (
        f"expected ≥1 banded multiple with numeric delta_pct; got {bench['multiples']}"
    )
