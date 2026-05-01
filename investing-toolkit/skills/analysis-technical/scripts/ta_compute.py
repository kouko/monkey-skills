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

# ---------------------------------------------------------------------------
# Signal normalization
#
# ta_client.py (canonical, MD5-locked) emits human-readable Title-Case strings.
# This skill's contract emits a closed lowercase snake_case enum so downstream
# consumers can rely on a stable vocabulary. We translate ta_client's output
# here without modifying the canonical source.
# ---------------------------------------------------------------------------

_RSI_SIGNAL_MAP = {
    "Overbought": "overbought",
    "Oversold": "oversold",
    "Neutral": "neutral",
    "N/A": "n/a",
}

_MACD_CROSSOVER_MAP = {
    "Bullish": "bullish",
    "Bearish": "bearish",
    "N/A": "n/a",
}

_BB_SIGNAL_MAP = {
    "Above Upper": "above_upper",
    "Below Lower": "below_lower",
    "Upper Half": "upper_half",
    "Lower Half": "lower_half",
    "N/A": "n/a",
}

_TREND_ALIGNMENT_MAP = {
    "Strong Bullish": "strong_bullish",
    "Bullish": "bullish",
    "Mixed": "neutral",
    "Strong Bearish": "strong_bearish",
    # Note: ta_client does not currently emit a plain "Bearish" tier, but
    # we map it defensively in case the canonical evolves.
    "Bearish": "bearish",
    "N/A": "n/a",
}


def _normalize(value: str, mapping: dict, fallback: str = "n/a") -> str:
    if value is None:
        return fallback
    return mapping.get(value, fallback)


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
    warnings: list[str] = []

    if "rsi" in indicators:
        rsi_vals = compute_rsi([v for v in closes if v is not None], 14)
        rsi_val = last(rsi_vals)
        out_indicators["rsi_14"] = rsi_val
        out_signals["rsi_signal"] = _normalize(rsi_signal(rsi_val), _RSI_SIGNAL_MAP)
        if rsi_val is None:
            warnings.append(f"rsi_14 unavailable: rows_consumed={len(rows)} < 14")

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
        out_signals["macd_crossover"] = _normalize(
            macd_crossover(macd_val, sig_val), _MACD_CROSSOVER_MAP
        )
        if macd_val is None:
            warnings.append(f"macd unavailable: rows_consumed={len(rows)} < 26")

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
        out_signals["bb_signal"] = _normalize(
            bb_signal(close, bb_u, bb_l), _BB_SIGNAL_MAP
        )
        if bb_u is None:
            warnings.append(f"bollinger unavailable: rows_consumed={len(rows)} < 20")

    if "atr" in indicators:
        atr_vals = compute_atr(highs, lows, closes)
        atr_val = last(atr_vals)
        atr_pct = None
        if atr_val is not None and close and close > 0:
            atr_pct = round(atr_val / close * 100, 2)
        out_indicators["atr_14"] = atr_val
        out_indicators["atr_pct"] = atr_pct
        if atr_val is None:
            warnings.append(f"atr_14 unavailable: rows_consumed={len(rows)} < 14")

    if "sma" in indicators:
        sma20_val = last(sma(closes, 20))
        sma50_val = last(sma(closes, 50))
        sma200_val = last(sma(closes, 200))
        out_indicators["sma"] = {
            "20": sma20_val,
            "50": sma50_val,
            "200": sma200_val,
        }
        if close and sma200_val and close > sma200_val:
            out_signals["price_vs_sma200"] = "above"
        elif close and sma200_val:
            out_signals["price_vs_sma200"] = "below"
        else:
            out_signals["price_vs_sma200"] = "n/a"
        out_signals["trend_alignment"] = _normalize(
            trend_alignment(close, sma20_val, sma50_val, sma200_val),
            _TREND_ALIGNMENT_MAP,
        )
        if sma20_val is None:
            warnings.append(f"sma_20 unavailable: rows_consumed={len(rows)} < 20")
        if sma50_val is None:
            warnings.append(f"sma_50 unavailable: rows_consumed={len(rows)} < 50")
        if sma200_val is None:
            warnings.append(f"sma_200 unavailable: rows_consumed={len(rows)} < 200")

    return {
        "ticker": ticker,
        "as_of": as_of,
        "close": close,
        "indicators": out_indicators,
        "signals": out_signals,
        "_provenance": {
            "skill": "analysis-technical",
            # Version tag matching MD5 of canonical ta_client.py — bump when
            # the canonical is edited so consumers can detect TA-logic changes.
            "ta_client_version": "v1.16.3",
            # Role of this skill's local ta_client.py copy. This skill is the
            # canonical master; sibling skills (e.g. analysis-screener) embed
            # a "functional-copy" with MD5 enforced to match.
            "ta_client_role": "canonical-master",
            "rows_consumed": len(rows),
            "indicators_requested": sorted(indicators),
            "warnings": warnings,
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
