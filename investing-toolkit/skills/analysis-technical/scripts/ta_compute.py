#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
ta_compute.py — Pure-compute technical indicator wrapper (Layer 2).

Reads an OHLCV JSON file produced by Layer 1 data skills
(`data-{country}/pack.py --pack snapshot`) and emits a structured indicator
JSON to stdout. Imports compute functions from the canonical ta_client.py
co-located in this skill.

NO HTTP. NO subprocess fetches. Pure compute.

Usage:
    uv run ta_compute.py --input ohlcv.json
    uv run ta_compute.py --input ohlcv.json --indicators rsi,macd
    cat ohlcv.json | uv run ta_compute.py --input -
"""

import argparse
import json
import sys
from pathlib import Path

# ta_client.py is co-located in this scripts/ directory.
sys.path.insert(0, str(Path(__file__).parent))
from ta_client import (  # noqa: E402
    bb_signal,
    compute_atr,
    compute_bollinger,
    compute_macd,
    compute_rsi,
    last,
    macd_crossover,
    rsi_signal,
    sma,
    trend_alignment,
)


SUPPORTED_INDICATORS = {"rsi", "macd", "bb", "atr", "sma"}


def _row_field(row: dict, *keys: str):
    """Return the first present key (handles capitalised + lower-case aliases)."""
    for k in keys:
        if k in row and row[k] is not None:
            return row[k]
    return None


def compute(ohlcv_json: dict, indicators: set[str]) -> dict:
    ticker = ohlcv_json.get("ticker", "UNKNOWN")
    rows = (
        ohlcv_json.get("history")
        or ohlcv_json.get("data")
        or []
    )

    if not rows:
        return {
            "ticker": ticker,
            "error": "No OHLCV rows in input (expected 'history' or 'data' key)",
        }

    # Build aligned series. Accept both capitalised and lower-case keys.
    closes = [
        float(c) if (c := _row_field(r, "Close", "close")) is not None else None
        for r in rows
    ]
    highs = [
        float(h) if (h := _row_field(r, "High", "high")) is not None else None
        for r in rows
    ]
    lows = [
        float(l) if (l := _row_field(r, "Low", "low")) is not None else None
        for r in rows
    ]

    as_of = (
        ohlcv_json.get("latest_date")
        or _row_field(rows[-1], "date", "Date")
        or "N/A"
    )
    latest_close = ohlcv_json.get("latest_close")
    if latest_close is None:
        latest_close = _row_field(rows[-1], "Close", "close")
    close = float(latest_close) if latest_close is not None else last(closes)

    out_indicators: dict = {}
    out_signals: dict = {}

    sma20_val = sma50_val = sma200_val = None
    bb_u = bb_l = None

    if "rsi" in indicators:
        rsi_vals = compute_rsi([v for v in closes if v is not None], 14)
        rsi_val = last(rsi_vals)
        out_indicators["rsi_14"] = rsi_val
        out_signals["rsi_signal"] = rsi_signal(rsi_val)

    if "macd" in indicators:
        macd_line, signal_line, histogram = compute_macd(closes)
        macd_val = last(macd_line)
        sig_val = last(signal_line)
        hist_val = last(histogram)
        out_indicators["macd"] = {
            "line": macd_val,
            "signal": sig_val,
            "histogram": hist_val,
        }
        out_signals["macd_crossover"] = macd_crossover(macd_val, sig_val)

    if "bb" in indicators:
        bb_upper, bb_mid, bb_lower = compute_bollinger(closes)
        bb_u = last(bb_upper)
        bb_m = last(bb_mid)
        bb_l = last(bb_lower)
        pct_b = None
        if bb_u is not None and bb_l is not None and close is not None and (bb_u - bb_l) != 0:
            pct_b = round((close - bb_l) / (bb_u - bb_l), 4)
        out_indicators["bollinger"] = {
            "upper": bb_u,
            "mid": bb_m,
            "lower": bb_l,
            "pct_b": pct_b,
        }
        out_signals["bb_signal"] = bb_signal(close, bb_u, bb_l)

    if "atr" in indicators:
        atr_vals = compute_atr(highs, lows, closes)
        atr_val = last(atr_vals)
        atr_pct = None
        if atr_val is not None and close and close > 0:
            atr_pct = round(atr_val / close * 100, 2)
        out_indicators["atr_14"] = atr_val
        out_indicators["atr_pct"] = atr_pct

    if "sma" in indicators:
        sma20_val = last(sma(closes, 20))
        sma50_val = last(sma(closes, 50))
        sma200_val = last(sma(closes, 200))
        out_indicators["sma"] = {
            "20": sma20_val,
            "50": sma50_val,
            "200": sma200_val,
        }
        out_signals["price_vs_sma200"] = (
            "above" if (close and sma200_val and close > sma200_val)
            else "below" if (close and sma200_val)
            else "N/A"
        )
        out_signals["trend_alignment"] = trend_alignment(
            close, sma20_val, sma50_val, sma200_val
        )

    return {
        "ticker": ticker,
        "as_of": as_of,
        "close": close,
        "indicators": out_indicators,
        "signals": out_signals,
        "_provenance": {
            "skill": "analysis-technical",
            "ta_client": "canonical (this skill is the master copy)",
            "rows_consumed": len(rows),
            "indicators_requested": sorted(indicators),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Pure-compute technical indicators from OHLCV JSON. "
            "Layer 2 — no network I/O."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to OHLCV JSON file, or '-' for stdin",
    )
    parser.add_argument(
        "--indicators",
        default="rsi,macd,bb,atr,sma",
        help="Comma-separated subset of: rsi,macd,bb,atr,sma",
    )
    args = parser.parse_args()

    requested = {s.strip().lower() for s in args.indicators.split(",") if s.strip()}
    unknown = requested - SUPPORTED_INDICATORS
    if unknown:
        print(
            json.dumps(
                {"error": f"Unknown indicators: {sorted(unknown)}. "
                          f"Supported: {sorted(SUPPORTED_INDICATORS)}"}
            )
        )
        sys.exit(2)

    if args.input == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(args.input).read_text()

    try:
        ohlcv_json = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}))
        sys.exit(1)

    output = compute(ohlcv_json, requested)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
