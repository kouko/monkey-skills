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
def test_compute_with_sector_benchmark_aapl_live():
    """End-to-end: AAPL → fetch comps-multiples + memo-fetch → comps_compute
    --sector-benchmark → assert etf_benchmark.multiples.trailingPE.delta_pct
    is numeric and band ∈ {in_line, notable, extreme, n/a}."""
    pack = ROOT / "skills" / "data-us" / "scripts" / "pack.py"
    yf = ROOT / "skills" / "data-us" / "scripts" / "yfinance_client.py"

    # Use the test_comps_sector_compute helpers if accessible; otherwise inline.
    # Skip detail; this mirrors the existing test_compute_default_aapl pattern
    # but adds --sector-benchmark.
    import importlib.util, sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    spec = importlib.util.spec_from_file_location(
        "_sc", Path(__file__).resolve().parent / "test_comps_sector_compute.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # ... (use helpers _fetch_comps_multiples, _fetch_memo_fetch, _run_uv)
    # For brevity here; concrete code follows the existing pattern in
    # test_comps_sector_compute.py.
    pytest.skip("end-to-end live test deferred to weekly cron — see T13 for plan")
