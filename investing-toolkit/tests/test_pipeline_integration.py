"""test_pipeline_integration.py — end-to-end cross-skill pipeline tests.

Exercises the full v2.0.0 three-layer pipeline (Data → Analysis → Report)
across multiple skills, asserting the contracts that bind them together.

Three end-to-end flows:

  A. AAPL snapshot card  [@pytest.mark.network]
       data-us/pack.py --pack snapshot
         → report-stock-snapshot/snapshot_format.py
         → Markdown card with ticker + company name + valuation field

  B. US screener list  [@pytest.mark.network]
       data-us/pack.py --pack screener-batch (AAPL, MSFT)
         → analysis-screener/screener_compute.py
         → report-screener-list/screener_format.py
         → Markdown with "Rank" column and ≥2 ranked rows

  C. JP bare-4-digit suffix bug regression  (NO network — synthetic data)
       Holdings CSV with `7203` + prices JSON keyed `7203.T`
         → analysis-portfolio/portfolio_compute.py (must resolve via .T fallback)
         → report-portfolio-review/review_format.py
         → Markdown contains the position (NOT in missing_prices)

Flow C must run on every CI invocation — that is the entire point of the
regression test. Flows A & B are network-marked.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

# Layer 1 — data
PACK_US = SKILLS / "data-us" / "scripts" / "pack.py"

# Layer 2 — analysis
SCREENER_COMPUTE = SKILLS / "analysis-screener" / "scripts" / "screener_compute.py"
PORTFOLIO_COMPUTE = SKILLS / "analysis-portfolio" / "scripts" / "portfolio_compute.py"

# Layer 3 — report
SNAPSHOT_FORMAT = SKILLS / "report-stock-snapshot" / "scripts" / "snapshot_format.py"
SCREENER_FORMAT = SKILLS / "report-screener-list" / "scripts" / "screener_format.py"
REVIEW_FORMAT = SKILLS / "report-portfolio-review" / "scripts" / "review_format.py"


def _uv_run_script(script: Path, *args: str, timeout: int = 180, env: dict | None = None) -> subprocess.CompletedProcess:
    """Invoke a script via `uv run --script` (used for scripts with PEP-723 headers)."""
    cmd = ["uv", "run", "--script", str(script), *args]
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(ROOT),
        env=full_env,
    )


def _python_run(script: Path, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Invoke a pure-stdlib script via current Python (faster than uv for offline use)."""
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(ROOT),
    )


# --------------------------------------------------------------------------- #
# A. AAPL snapshot pipeline (NETWORK)
# --------------------------------------------------------------------------- #


@pytest.mark.network
def test_pipeline_aapl_snapshot(tmp_path):
    """data-us/pack.py --pack snapshot AAPL → snapshot_format → Markdown card."""
    pack_path = tmp_path / "aapl-snap.json"

    cache = os.environ.get("INVESTING_TOOLKIT_CACHE", str(tmp_path / "cache"))
    env = {"INVESTING_TOOLKIT_CACHE": cache}

    fetch = _uv_run_script(
        PACK_US, "--ticker", "AAPL", "--pack", "snapshot",
        timeout=240,
        env=env,
    )
    assert fetch.returncode == 0, (
        f"pack.py snapshot failed (exit {fetch.returncode}):\n"
        f"stderr:\n{fetch.stderr[:2000]}"
    )
    pack_path.write_text(fetch.stdout, encoding="utf-8")
    pack = json.loads(fetch.stdout)
    assert isinstance(pack, dict)

    fmt = _uv_run_script(
        SNAPSHOT_FORMAT,
        "--input", str(pack_path),
        "--country", "us",
        timeout=60,
    )
    assert fmt.returncode == 0, (
        f"snapshot_format failed (exit {fmt.returncode}):\n"
        f"stderr:\n{fmt.stderr[:2000]}"
    )

    md = fmt.stdout
    assert "AAPL" in md, "snapshot Markdown missing ticker AAPL"
    # Yahoo Finance returns "Apple Inc." in info.shortName/longName.
    assert "Apple" in md, "snapshot Markdown missing 'Apple' company name"
    # At least one valuation field — PE / market cap / price label.
    valuation_signals = ["PE", "P/E", "Market Cap", "市值", "時価総額", "Price", "株価", "股價"]
    assert any(sig in md for sig in valuation_signals), (
        f"snapshot Markdown missing any valuation field; got first 500 chars:\n{md[:500]}"
    )


# --------------------------------------------------------------------------- #
# B. Cross-country screener pipeline (NETWORK)
# --------------------------------------------------------------------------- #


@pytest.mark.network
def test_pipeline_us_screener(tmp_path):
    """data-us/pack.py --pack screener-batch → analysis-screener → report-screener-list."""
    cache = os.environ.get("INVESTING_TOOLKIT_CACHE", str(tmp_path / "cache"))
    env = {"INVESTING_TOOLKIT_CACHE": cache}

    batch_path = tmp_path / "us-batch.json"
    fetch = _uv_run_script(
        PACK_US, "--tickers", "AAPL,MSFT", "--pack", "screener-batch",
        timeout=240,
        env=env,
    )
    assert fetch.returncode == 0, (
        f"pack.py screener-batch failed (exit {fetch.returncode}):\n"
        f"stderr:\n{fetch.stderr[:2000]}"
    )
    batch_path.write_text(fetch.stdout, encoding="utf-8")

    ranked_path = tmp_path / "ranked.json"
    compute = _uv_run_script(
        SCREENER_COMPUTE,
        "--input", str(batch_path),
        "--preset", "balanced",
        "--top-n", "5",
        timeout=60,
    )
    assert compute.returncode == 0, (
        f"screener_compute failed (exit {compute.returncode}):\n"
        f"stderr:\n{compute.stderr[:2000]}"
    )
    ranked_path.write_text(compute.stdout, encoding="utf-8")
    ranked = json.loads(compute.stdout)
    # Shape sanity: must contain a ranked list.
    assert any(k in ranked for k in ("ranked", "results", "top")), (
        f"screener_compute output missing ranked field: keys={list(ranked.keys())}"
    )

    fmt = _uv_run_script(
        SCREENER_FORMAT,
        "--input", str(ranked_path),
        timeout=60,
    )
    assert fmt.returncode == 0, (
        f"screener_format failed (exit {fmt.returncode}):\n"
        f"stderr:\n{fmt.stderr[:2000]}"
    )

    md = fmt.stdout
    assert "Rank" in md or "排名" in md or "順位" in md, (
        f"screener Markdown missing Rank column header; got:\n{md[:500]}"
    )
    # Two ranked rows: count Markdown table rows that look ranked.
    table_rows = [
        ln for ln in md.splitlines()
        if ln.startswith("|") and ("AAPL" in ln or "MSFT" in ln)
    ]
    assert len(table_rows) >= 2, (
        f"screener Markdown missing ≥2 ranked rows; rows found: {table_rows}"
    )


# --------------------------------------------------------------------------- #
# C. JP bare-4-digit suffix bug regression (NO network)
# --------------------------------------------------------------------------- #


def test_pipeline_jp_bare_suffix_resolution(tmp_path):
    """Critical regression: holdings CSV row `7203` (bare 4-digit) must
    resolve against prices JSON keyed `7203.T`. The portfolio compute layer
    must apply the .T fallback (analysis-portfolio _resolve_price), and the
    review formatter must render the position in the positions table.

    No network — synthetic CSV + JSON inputs.
    """
    holdings_csv = tmp_path / "holdings.csv"
    holdings_csv.write_text(
        "ticker,shares,avg_cost\n"
        "7203,100,2000\n",
        encoding="utf-8",
    )
    prices_json = tmp_path / "prices.json"
    prices_json.write_text(
        json.dumps({"7203.T": 2800}),
        encoding="utf-8",
    )

    portfolio_json = tmp_path / "portfolio.json"
    compute = _uv_run_script(
        PORTFOLIO_COMPUTE,
        "--holdings", str(holdings_csv),
        "--prices", str(prices_json),
        timeout=60,
    )
    assert compute.returncode == 0, (
        f"portfolio_compute failed (exit {compute.returncode}):\n"
        f"stderr:\n{compute.stderr[:2000]}"
    )
    portfolio_json.write_text(compute.stdout, encoding="utf-8")

    portfolio = json.loads(compute.stdout)
    positions = portfolio.get("positions", [])
    missing = portfolio.get("_provenance", {}).get("missing_prices", [])

    # Critical bug check: the bare 4-digit ticker MUST resolve, NOT end up in
    # missing_prices. This is the entire point of the JP-suffix fallback.
    assert "7203" not in missing, (
        f"REGRESSION: bare 4-digit '7203' fell into missing_prices "
        f"(suffix fallback broken). missing_prices={missing}"
    )
    assert any(p.get("ticker") == "7203" for p in positions), (
        f"position '7203' missing from output. positions={positions}"
    )
    pos = next(p for p in positions if p.get("ticker") == "7203")
    # Compute sanity: 100 * 2800 = 280,000 market value.
    assert pos.get("current_price") == pytest.approx(2800.0)
    assert pos.get("market_value") == pytest.approx(280_000.0)

    fmt = _uv_run_script(
        REVIEW_FORMAT,
        "--portfolio", str(portfolio_json),
        "--lang", "ja",
        timeout=60,
    )
    assert fmt.returncode == 0, (
        f"review_format failed (exit {fmt.returncode}):\n"
        f"stderr:\n{fmt.stderr[:2000]}"
    )
    md = fmt.stdout
    assert "7203" in md, f"review Markdown missing position '7203':\n{md[:500]}"
    # Position appears in a table row with its market value rendered (280,000.00).
    assert "280,000.00" in md or "280000" in md, (
        f"review Markdown missing market value 280,000 for 7203:\n{md[:800]}"
    )
