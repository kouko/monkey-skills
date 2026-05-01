#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas==3.0.2", "numpy>=1.26"]
# ///
"""
ta_client.py — Technical indicator calculator for investing-toolkit

Computes RSI, MACD, Bollinger Bands, ATR, and SMA from yfinance OHLCV JSON.
Formulas follow TraderMonty conventions (EMA-based RSI, standard MACD/BB/ATR).

Input: yfinance_client.py JSON output (via --input file or stdin with --input -)
Output: JSON with latest indicator values + signals

Usage:
  # From file
  uv run ta_client.py --input ohlcv.json

  # From yfinance_client.py pipe
  uv run yfinance_client.py --ticker AAPL --period 1y | uv run ta_client.py --input -

  # Direct ticker fetch + compute (requires yfinance_client.py in same directory)
  uv run ta_client.py --ticker AAPL --period 1y --base-path /path/to/scripts/
"""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Core TA computations
# ---------------------------------------------------------------------------

def ema(series: list[float], period: int) -> list[float]:
    """Exponential moving average. Uses Wilder smoothing (alpha = 1/period)."""
    if not series:
        return []
    k = 1.0 / period
    result = [None] * len(series)
    # Find first non-None starting index
    start = next((i for i, v in enumerate(series) if v is not None), None)
    if start is None:
        return result
    result[start] = series[start]
    for i in range(start + 1, len(series)):
        if series[i] is None:
            result[i] = result[i - 1]
        else:
            result[i] = series[i] * k + result[i - 1] * (1 - k)
    return result


def sma(series: list[float], period: int) -> list[float]:
    """Simple moving average."""
    result = [None] * len(series)
    for i in range(period - 1, len(series)):
        window = [v for v in series[i - period + 1:i + 1] if v is not None]
        if len(window) == period:
            result[i] = sum(window) / period
    return result


def compute_rsi(closes: list[float], period: int = 14) -> list[float | None]:
    """RSI via Wilder EMA of gains and losses."""
    if len(closes) < period + 1:
        return [None] * len(closes)

    gains = []
    losses = []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    avg_gain = ema(gains, period)
    avg_loss = ema(losses, period)

    rsi_vals = [None]  # offset by 1 (no delta for first close)
    for g, l in zip(avg_gain, avg_loss):
        if g is None or l is None:
            rsi_vals.append(None)
        elif l == 0:
            rsi_vals.append(100.0)
        else:
            rs = g / l
            rsi_vals.append(100.0 - 100.0 / (1.0 + rs))

    return rsi_vals


def compute_macd(
    closes: list[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple[list, list, list]:
    """MACD line, signal line, histogram."""
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)

    macd_line = [
        (f - s) if (f is not None and s is not None) else None
        for f, s in zip(ema_fast, ema_slow)
    ]
    signal_line = ema(macd_line, signal)
    histogram = [
        (m - s) if (m is not None and s is not None) else None
        for m, s in zip(macd_line, signal_line)
    ]
    return macd_line, signal_line, histogram


def compute_bollinger(
    closes: list[float],
    period: int = 20,
    std_dev: float = 2.0,
) -> tuple[list, list, list]:
    """Bollinger Bands: upper, mid (SMA), lower."""
    mid = sma(closes, period)
    upper = [None] * len(closes)
    lower = [None] * len(closes)

    for i in range(period - 1, len(closes)):
        window = closes[i - period + 1:i + 1]
        if len(window) == period and all(v is not None for v in window):
            mean = sum(window) / period
            variance = sum((v - mean) ** 2 for v in window) / period
            sd = math.sqrt(variance)
            upper[i] = mean + std_dev * sd
            lower[i] = mean - std_dev * sd

    return upper, mid, lower


def compute_atr(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    period: int = 14,
) -> list[float | None]:
    """Average True Range via EMA."""
    tr_values = [None]
    for i in range(1, len(closes)):
        h, l, pc = highs[i], lows[i], closes[i - 1]
        if h is None or l is None or pc is None:
            tr_values.append(None)
        else:
            tr = max(h - l, abs(h - pc), abs(l - pc))
            tr_values.append(tr)

    return ema(tr_values, period)


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------

def rsi_signal(val: float | None) -> str:
    if val is None:
        return "N/A"
    if val >= 70:
        return "Overbought"
    if val <= 30:
        return "Oversold"
    return "Neutral"


def macd_crossover(macd_val: float | None, signal_val: float | None) -> str:
    if macd_val is None or signal_val is None:
        return "N/A"
    return "Bullish" if macd_val > signal_val else "Bearish"


def bb_signal(close: float | None, upper: float | None, lower: float | None) -> str:
    if any(v is None for v in [close, upper, lower]):
        return "N/A"
    if close >= upper:
        return "Above Upper"
    if close <= lower:
        return "Below Lower"
    mid = (upper + lower) / 2
    if close >= mid:
        return "Upper Half"
    return "Lower Half"


def trend_alignment(
    close: float | None,
    sma20: float | None,
    sma50: float | None,
    sma200: float | None,
) -> str:
    if any(v is None for v in [close, sma20, sma50, sma200]):
        return "N/A"
    if close > sma20 > sma50 > sma200:
        return "Strong Bullish"
    if close > sma200:
        return "Bullish"
    if close < sma20 < sma50 < sma200:
        return "Strong Bearish"
    return "Mixed"


def last(series: list) -> float | None:
    for v in reversed(series):
        if v is not None:
            return round(v, 4)
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def compute_indicators(ohlcv_json: dict) -> dict:
    """Take yfinance_client.py / finmind_client.py / twse_openapi
    stock-day-history output, return indicator JSON.

    v1.16.3: `latest_date` / `latest_close` are auto-computed from the
    last row in `data[]` when absent from the top level — makes ta_client
    portable across the 3 OHLCV sources (yfinance already supplies them;
    FinMind and TWSE /rwd/ do not).
    """
    ticker = ohlcv_json.get("ticker", "UNKNOWN")
    rows = ohlcv_json.get("data", [])

    if not rows:
        return {"ticker": ticker, "error": "No OHLCV data in input"}

    # Auto-compute latest_date / latest_close from the last row if the
    # source didn't supply them at the top level.
    as_of = ohlcv_json.get("latest_date") or rows[-1].get("date") or "N/A"
    latest_close = ohlcv_json.get("latest_close")
    if latest_close is None:
        latest_close = rows[-1].get("Close") or rows[-1].get("close")

    closes = [r.get("Close") or r.get("close") for r in rows]
    highs  = [r.get("High")  or r.get("high")  for r in rows]
    lows   = [r.get("Low")   or r.get("low")   for r in rows]

    # Filter None values check
    closes = [float(v) if v is not None else None for v in closes]
    highs  = [float(v) if v is not None else None for v in highs]
    lows   = [float(v) if v is not None else None for v in lows]

    close = latest_close or last(closes)

    # Compute
    rsi_vals = compute_rsi([v for v in closes if v is not None], 14)
    macd_line, signal_line, histogram = compute_macd(closes)
    bb_upper, bb_mid, bb_lower = compute_bollinger(closes)
    atr_vals = compute_atr(highs, lows, closes)
    sma20_vals  = sma(closes, 20)
    sma50_vals  = sma(closes, 50)
    sma200_vals = sma(closes, 200)

    rsi_val   = last(rsi_vals)
    macd_val  = last(macd_line)
    sig_val   = last(signal_line)
    hist_val  = last(histogram)
    bb_u      = last(bb_upper)
    bb_m      = last(bb_mid)
    bb_l      = last(bb_lower)
    atr_val   = last(atr_vals)
    sma20_val = last(sma20_vals)
    sma50_val = last(sma50_vals)
    sma200_val = last(sma200_vals)

    # %B
    pct_b = None
    if bb_u is not None and bb_l is not None and close is not None and (bb_u - bb_l) != 0:
        pct_b = round((close - bb_l) / (bb_u - bb_l), 4)

    # ATR as % of price
    atr_pct = None
    if atr_val is not None and close and close > 0:
        atr_pct = round(atr_val / close * 100, 2)

    return {
        "ticker": ticker,
        "as_of": as_of,
        "close": close,
        "rsi_14": rsi_val,
        "rsi_signal": rsi_signal(rsi_val),
        "macd": macd_val,
        "macd_signal_line": sig_val,
        "macd_histogram": hist_val,
        "macd_crossover": macd_crossover(macd_val, sig_val),
        "bb_upper": bb_u,
        "bb_mid": bb_m,
        "bb_lower": bb_l,
        "bb_pct_b": pct_b,
        "bb_signal": bb_signal(close, bb_u, bb_l),
        "atr_14": atr_val,
        "atr_pct": atr_pct,
        "sma_20": sma20_val,
        "sma_50": sma50_val,
        "sma_200": sma200_val,
        "price_vs_sma200": (
            "above" if (close and sma200_val and close > sma200_val)
            else "below" if (close and sma200_val)
            else "N/A"
        ),
        "trend_alignment": trend_alignment(close, sma20_val, sma50_val, sma200_val),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute technical indicators from yfinance OHLCV JSON"
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input",
        help="Path to yfinance_client.py JSON output, or '-' for stdin",
    )
    input_group.add_argument(
        "--ticker",
        help="Ticker to fetch and compute (requires --base-path or scripts in CWD)",
    )
    parser.add_argument("--period", default="1y", help="yfinance period (used with --ticker)")
    parser.add_argument(
        "--base-path",
        default=str(Path(__file__).parent),
        help="Directory containing yfinance_client.py (used with --ticker)",
    )
    args = parser.parse_args()

    if args.input:
        if args.input == "-":
            raw = sys.stdin.read()
        else:
            raw = Path(args.input).read_text()
        try:
            ohlcv_json = json.loads(raw)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON input: {e}"}))
            sys.exit(1)
    else:
        # Direct fetch via yfinance_client.py
        script = Path(args.base_path) / "yfinance_client.py"
        try:
            result = subprocess.run(
                ["uv", "run", str(script), "--ticker", args.ticker, "--period", args.period],
                capture_output=True, text=True, check=True,
            )
            ohlcv_json = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(json.dumps({"error": f"yfinance_client.py failed: {e.stderr[:200]}"}))
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"yfinance_client.py returned invalid JSON: {e}"}))
            sys.exit(1)

    output = compute_indicators(ohlcv_json)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
