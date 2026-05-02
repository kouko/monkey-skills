#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
pack.py — investing-toolkit data-us facade

Composes multi-source US data pulls (yfinance + SEC EDGAR + FRED) into
structured JSON bundles. Pure I/O / fetch layer — no analysis.

Pack types:
  - snapshot         single ticker, yfinance info + 2y price
  - memo-fetch       single ticker, yfinance + SEC EDGAR (10-K/10-Q/8-K + facts)
  - comps-multiples  single OR batch, yfinance multiples-only fields
  - screener-batch   batch, yfinance lightweight fields (REQUIRES --tickers)
  - regime-pack      no ticker dimension, FRED macro series only

Usage:
  uv run pack.py --ticker AAPL --pack snapshot
  uv run pack.py --ticker NVDA --pack memo-fetch
  uv run pack.py --ticker AAPL --pack comps-multiples
  uv run pack.py --tickers AAPL,MSFT,GOOGL --pack comps-multiples
  uv run pack.py --tickers AAPL,MSFT,GOOGL,META,AMZN --pack screener-batch
  uv run pack.py --pack regime-pack

Environment:
  INVESTING_TOOLKIT_CACHE   passed through to underlying clients (yfinance / sec / fred)

Output: JSON to stdout. Exit 0 on success, non-zero on argparse / shell-out error.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
YF = SCRIPT_DIR / "yfinance_client.py"
SEC = SCRIPT_DIR / "sec_edgar_client.py"
FRED = SCRIPT_DIR / "fred_client.py"


# ---------------------------------------------------------------------------
# Multiples + screener field whitelists
# ---------------------------------------------------------------------------

MULTIPLES_FIELDS = [
    "trailingPE",
    "forwardPE",
    "priceToSales",
    "priceToBook",
    "enterpriseToEbitda",
    "enterpriseToRevenue",
    "marketCap",
    "enterpriseValue",
]

SCREENER_FIELDS = [
    "trailingPE",
    "priceToBook",
    "marketCap",
    "dividendYield",
    "beta",
    "fiftyTwoWeekHigh",
    "fiftyTwoWeekLow",
    "regularMarketPrice",
    "sector",
    "industry",
    "shortName",
]


# ---------------------------------------------------------------------------
# Default FRED series for regime-pack (mirror us-macro core groups)
# ---------------------------------------------------------------------------

REGIME_SERIES_GROUPS = {
    "rates":         ("T10Y2Y,DGS10,DGS2,FEDFUNDS",          24),
    "inflation":     ("CPIAUCSL,CPILFESL",                    24),
    "growth":        ("GDPC1,INDPRO",                         12),
    "nowcast":       ("GDPNOW,CFNAI,USALOLITOAASTSAM",        24),
    "wei":           ("WEI",                                  52),
    "real_rates":    ("T5YIE,T10YIE,DFII5,DFII10",            24),
    "swap_spreads":  ("DGS3MO,SOFR30DAYAVG",                  24),
}


# ---------------------------------------------------------------------------
# Subprocess helper — invoke a client script with current env
# ---------------------------------------------------------------------------

CLIENT_TIMEOUT_SECONDS = 300


def run_client(script: Path, extra_args: list[str], timeout: int = CLIENT_TIMEOUT_SECONDS) -> dict:
    """Run a client script with `uv run`, return parsed JSON.

    Returns a structured error dict on non-zero exit, JSON parse failure, or timeout.
    """
    cmd = ["uv", "run", str(script)] + extra_args
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "error": f"client timeout after {timeout}s",
            "_cmd": cmd,
            "_returncode": -1,
        }
    if proc.returncode != 0:
        return {
            "error": "client_failed",
            "script": script.name,
            "args": extra_args,
            "returncode": proc.returncode,
            "stderr": proc.stderr.strip()[-2000:],
        }
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return {
            "error": "invalid_json",
            "script": script.name,
            "args": extra_args,
            "detail": str(e),
            "stdout_head": proc.stdout[:500],
        }


def filter_fields(info_obj: dict, fields: list[str]) -> dict:
    """Return only whitelisted fields from an info dict (preserve missing as None)."""
    if not isinstance(info_obj, dict):
        return {}
    out = {f: info_obj.get(f) for f in fields}
    # Preserve identifying / provenance keys if present
    for k in ("ticker", "_provenance", "error"):
        if k in info_obj:
            out[k] = info_obj[k]
    return out


# ---------------------------------------------------------------------------
# Pack implementations
# ---------------------------------------------------------------------------

def pack_snapshot(ticker: str) -> dict:
    """yfinance info + 2y price for a single ticker."""
    info = run_client(YF, ["--ticker", ticker, "--action", "info"])
    history = run_client(YF, ["--ticker", ticker, "--period", "2y"])
    rows = history.get("data", []) if isinstance(history, dict) else []
    return {
        "pack": "snapshot",
        "ticker": ticker.upper(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "company_info": info,
        "price_history": history,
        "history": rows,  # T1 canonical OHLCV alias — see docs/normalization-contract.md
    }


def pack_memo_fetch(ticker: str) -> dict:
    """Heavy single-ticker bundle for equity memo: yfinance + SEC EDGAR."""
    info = run_client(YF, ["--ticker", ticker, "--action", "info"])
    history = run_client(YF, ["--ticker", ticker, "--period", "2y"])
    filings = run_client(
        SEC,
        ["--ticker", ticker, "--action", "filings",
         "--forms", "10-K,10-Q,8-K", "--limit", "8"],
    )
    facts = run_client(SEC, ["--ticker", ticker, "--action", "facts"])
    rows = history.get("data", []) if isinstance(history, dict) else []
    return {
        "pack": "memo-fetch",
        "ticker": ticker.upper(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "company_info": info,
        "price_history": history,
        "history": rows,  # T1 canonical OHLCV alias — see docs/normalization-contract.md
        "sec_filings": filings,
        "sec_facts": facts,
    }


def pack_comps_multiples(tickers: list[str]) -> dict:
    """Multiples-only fields. Single or batch."""
    if len(tickers) == 1:
        info = run_client(YF, ["--ticker", tickers[0], "--action", "info"])
        per_ticker = {
            tickers[0].upper(): filter_fields(info, MULTIPLES_FIELDS),
        }
        return {
            "pack": "comps-multiples",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tickers": per_ticker,
            "info": per_ticker,  # T1 canonical multiples alias
        }
    # Batch: use yfinance batch action
    batch = run_client(
        YF,
        ["--tickers", ",".join(tickers), "--action", "info"],
    )
    if isinstance(batch, dict) and isinstance(batch.get("tickers"), dict):
        per_ticker = {
            t: filter_fields(d, MULTIPLES_FIELDS)
            for t, d in batch["tickers"].items()
        }
        return {
            "pack": "comps-multiples",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tickers": per_ticker,
            "info": per_ticker,  # T1 canonical multiples alias
        }
    # Batch failure: surface error at top level, keep tickers map clean
    return {
        "pack": "comps-multiples",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "tickers": {},
        "info": {},  # T1 canonical alias (empty on error)
        "error": batch,
    }


def pack_screener_batch(tickers: list[str]) -> dict:
    """Batch lightweight fields for screener input."""
    batch = run_client(
        YF,
        ["--tickers", ",".join(tickers), "--action", "info"],
    )
    if isinstance(batch, dict) and isinstance(batch.get("tickers"), dict):
        per_ticker = {
            t: filter_fields(d, SCREENER_FIELDS)
            for t, d in batch["tickers"].items()
        }
        return {
            "pack": "screener-batch",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tickers": per_ticker,
        }
    # Batch failure: surface error at top level, keep tickers map clean
    return {
        "pack": "screener-batch",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "tickers": {},
        "error": batch,
    }


def _flatten_regime_series(groups: dict) -> dict:
    """T2 canonical: flatten groups.{group}.series.{fred_id}.observations
    into a flat top-level `series: {fred_id: [float, float, ...]}` block.

    Values are extracted in chronological order (most-recent-last). Missing
    or non-numeric observations are dropped. Empty series (no usable values)
    are omitted from the flat block.

    Per docs/normalization-contract.md Tier 2 — analysis-macro-regime
    (regime_compose.resolve_series) reads `pack.series[fred_id]` directly
    as a list of floats, not the nested fred_client envelope.
    """
    def _extract_values(series_payload: dict) -> list[float]:
        """Extract chronological-order float values from a FRED series payload."""
        if not isinstance(series_payload, dict):
            return []
        obs = series_payload.get("observations") or []
        out: list[float] = []
        for o in obs:
            if not isinstance(o, dict):
                continue
            v = o.get("value")
            if v is None:
                continue
            try:
                out.append(float(v))
            except (TypeError, ValueError):
                continue
        return out

    flat: dict[str, list[float]] = {}
    for group_payload in groups.values():
        if not isinstance(group_payload, dict):
            continue
        nested = group_payload.get("series")
        if isinstance(nested, dict):
            # Multi-series group: {fetched_at, series: {fred_id: payload, ...}}
            for fred_id, series_payload in nested.items():
                values = _extract_values(series_payload)
                if values:
                    flat[fred_id] = values
        elif isinstance(nested, str):
            # Single-series group: the group itself IS the FRED payload, with
            # `series: "WEI"` as the FRED ID and `observations: [...]` alongside.
            fred_id = nested
            values = _extract_values(group_payload)
            if values:
                flat[fred_id] = values
    return flat


def pack_regime() -> dict:
    """FRED macro series only — no ticker dimension."""
    groups: dict[str, dict] = {}
    for group_name, (series_csv, periods) in REGIME_SERIES_GROUPS.items():
        groups[group_name] = run_client(
            FRED,
            ["--series", series_csv, "--periods", str(periods)],
        )
    return {
        "pack": "regime-pack",
        "country": "US",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "groups": groups,
        "series": _flatten_regime_series(groups),  # T2 canonical flat alias
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="data-us pack facade — multi-source US data bundler",
    )
    parser.add_argument("--pack", required=True,
                        choices=["snapshot", "memo-fetch", "comps-multiples",
                                 "screener-batch", "regime-pack"],
                        help="Pack type")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ticker", help="Single US ticker (e.g. AAPL)")
    group.add_argument("--tickers",
                       help="Comma-separated US tickers (e.g. AAPL,MSFT,GOOGL)")
    args = parser.parse_args()

    pack = args.pack
    ticker_list: list[str] = []
    if args.tickers:
        ticker_list = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    elif args.ticker:
        ticker_list = [args.ticker.strip().upper()]

    # Pack-type validation per §4.2 contract
    if pack == "snapshot":
        if len(ticker_list) != 1:
            print("error: --pack snapshot requires --ticker (single)", file=sys.stderr)
            return 2
        result = pack_snapshot(ticker_list[0])
    elif pack == "memo-fetch":
        if len(ticker_list) != 1:
            print("error: --pack memo-fetch requires --ticker (single, heavy)",
                  file=sys.stderr)
            return 2
        result = pack_memo_fetch(ticker_list[0])
    elif pack == "comps-multiples":
        if not ticker_list:
            print("error: --pack comps-multiples requires --ticker or --tickers",
                  file=sys.stderr)
            return 2
        result = pack_comps_multiples(ticker_list)
    elif pack == "screener-batch":
        if len(ticker_list) < 2:
            print("error: --pack screener-batch requires --tickers (>=2)",
                  file=sys.stderr)
            return 2
        result = pack_screener_batch(ticker_list)
    elif pack == "regime-pack":
        if ticker_list:
            print("warning: --pack regime-pack ignores --ticker/--tickers (macro only)",
                  file=sys.stderr)
        result = pack_regime()
    else:
        print(f"error: unknown pack '{pack}'", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
