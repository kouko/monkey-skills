---
name: technical-snapshot
description: Technical indicators snapshot — RSI, MACD, Bollinger Bands (ships in v1.2.0). Computes common momentum and volatility indicators from yfinance price data.
---

# technical-snapshot

This skill computes technical indicators — RSI (14-day), MACD (12/26/9), Bollinger
Bands (20-day, 2σ), and ATR (Average True Range) — from yfinance OHLCV price data.
It ships in **investing-toolkit v1.2.0**.

See `../../ROADMAP.md` for the v1.2.0 timeline and planned implementation details.

---

## Status: Not Yet Available

technical-snapshot is planned for v1.2.0 and is not available in the current release.

---

## Interim Options

**1. us-stock-snapshot for price history**

Use `us-stock-snapshot` to fetch OHLCV price history for a ticker. You can compute
indicators manually from the returned data, or paste the data into a tool that
supports TA computation.

**2. Alpha Vantage for technical indicators**

Alpha Vantage provides a free API with precomputed RSI, MACD, and Bollinger Band
endpoints. Free tier: 25 requests/day. Get a key at https://www.alphavantage.co/support/#api-key

```bash
# Example: RSI for AAPL
curl "https://www.alphavantage.co/query?function=RSI&symbol=AAPL&interval=daily&time_period=14&series_type=close&apikey=YOUR_KEY"
```

**3. Compute manually from us-stock-snapshot output**

The `us-stock-snapshot` skill returns full OHLCV history. Standard RSI, MACD, and
Bollinger Band formulas can be applied to the `data` array in the returned JSON.
