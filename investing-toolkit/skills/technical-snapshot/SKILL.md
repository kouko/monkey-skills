---
name: technical-snapshot
description: >-
  Compute technical indicators (RSI-14, MACD-12/26/9, Bollinger Bands-20,
  ATR-14, SMA-20/50/200) from yfinance OHLCV data via ta_client.py. Outputs a
  structured indicator card with trend alignment and signal interpretation.
  テクニカル指標スナップショット。技術指標快照。
---

# technical-snapshot

Computes common technical indicators from OHLCV price data and outputs a
structured snapshot card. This skill uses `scripts/ta_client.py` for all
indicator calculations — no external API or manual computation required.

**Data**: yfinance (unofficial) — price/volume only, no financial statements.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | e.g. AAPL, NVDA, 2330.TW |
| `period` | no | `1y` | yfinance period: 6mo, 1y, 2y |

Minimum 200 trading days needed for SMA-200. Use `period=1y` or longer.

---

## How It Works

### Step 1 — Fetch OHLCV (data-fetcher agent)

Launch `../../agents/data-fetcher.md` with:

```
### Fetch Requests
- uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --period {period}
```

Expected output: JSON with `data` array (OHLCV rows) and `latest_close`.

---

### Step 2 — Compute indicators (ta_client.py)

Before running scripts directly, verify uv is installed:
```bash
command -v uv || sh ${CLAUDE_SKILL_DIR}/../../scripts/setup.sh
```

Pass the JSON from Step 1 to `ta_client.py`:

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/ta_client.py --input {ohlcv_json_path}
```

Or as a direct pipe:

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --period {period} | \
  uv run ${CLAUDE_SKILL_DIR}/scripts/ta_client.py --input -
```

`ta_client.py` computes and returns:

| Indicator | Formula | Parameters |
|-----------|---------|------------|
| RSI | Wilder EMA of gains/losses | period=14 |
| MACD line | EMA(12) − EMA(26) | fast=12, slow=26 |
| MACD signal | EMA(9) of MACD line | signal=9 |
| MACD histogram | MACD − signal | — |
| Bollinger Upper | SMA(20) + 2σ | period=20, std=2 |
| Bollinger Mid | SMA(20) | — |
| Bollinger Lower | SMA(20) − 2σ | — |
| %B | (close−lower)/(upper−lower) | — |
| ATR | EWM of True Range | period=14 |
| SMA | Simple moving average | 20, 50, 200 |

---

### Step 3 — Render snapshot card

Extract from `ta_client.py` output and render:

```markdown
## {TICKER} Technical Snapshot — {as_of}

**Price**: {close}
**Trend**: {trend_alignment} | vs SMA-200: {price_vs_sma200}

### Momentum
**RSI(14)**: {rsi_14} — {rsi_signal}
**MACD**: {macd} | Signal: {macd_signal_line} | Hist: {macd_histogram} — {macd_crossover}

### Volatility
**Bollinger(20,2σ)**: Upper {bb_upper} / Mid {bb_mid} / Lower {bb_lower}
**%B**: {bb_pct_b} — {bb_signal}
**ATR(14)**: {atr_14} ({atr_pct}% of price)

### Moving Averages
| SMA | Value | vs Price |
|-----|-------|---------|
| 20  | {sma_20} | {above/below} |
| 50  | {sma_50} | {above/below} |
| 200 | {sma_200} | {above/below} |

_Data via yfinance (unofficial). Price only — no financial statements._
```

**Signal interpretation**:

| Indicator | Signal | Meaning |
|-----------|--------|---------|
| RSI < 30 | Oversold | Potential reversal up |
| RSI > 70 | Overbought | Potential reversal down |
| MACD Bullish crossover | MACD > Signal | Upward momentum |
| MACD Bearish crossover | MACD < Signal | Downward momentum |
| %B > 1.0 | Above Upper Band | Statistically extended |
| %B < 0.0 | Below Lower Band | Statistically compressed |
| trend_alignment = Strong Bullish | price > SMA20 > SMA50 > SMA200 | Full uptrend |

---

## Multi-Timeframe Confirmation

When `--multi-timeframe` is specified (or by default for `investment-memo-writer`
handoff), compute indicators at two timeframes and produce a confirmation signal:

### Fetch

```
### Fetch Requests
- uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --period 2y --interval 1d
- uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --period 2y --interval 1wk
```

### Compute

Run `ta_client.py` on both outputs → daily indicators + weekly indicators.

### Confirmation Matrix

| Daily Signal | Weekly Signal | Confirmation | Meaning |
|-------------|-------------|-------------|---------|
| RSI > 50 + MACD Bullish | RSI > 50 + MACD Bullish | **Confirmed Bullish** | Strong trend, aligned |
| RSI > 50 + MACD Bullish | RSI < 50 or MACD Bearish | **Unconfirmed** | Daily strength, weekly weakness |
| RSI < 50 + MACD Bearish | RSI < 50 + MACD Bearish | **Confirmed Bearish** | Strong downtrend, aligned |
| RSI < 50 + MACD Bearish | RSI > 50 or MACD Bullish | **Unconfirmed** | Daily weakness, weekly still up |

### Output (appended to snapshot card)

```markdown
### Multi-Timeframe Confirmation

| Indicator | Daily (D1) | Weekly (W1) | Aligned? |
|-----------|-----------|------------|---------|
| RSI(14) | {d_rsi} {signal} | {w_rsi} {signal} | ✓ / ✗ |
| MACD | {d_macd_cross} | {w_macd_cross} | ✓ / ✗ |
| vs SMA200 | {d_sma200} | {w_sma200} | ✓ / ✗ |
| Trend | {d_trend} | {w_trend} | ✓ / ✗ |

**Verdict**: {Confirmed Bullish / Confirmed Bearish / Unconfirmed}
_Unconfirmed = daily and weekly disagree. Higher conviction when both align._
```

Multi-timeframe reduces false signals: a daily RSI overbought that contradicts
a weekly downtrend suggests a bear-market rally, not a genuine reversal.

**Attribution note**: TraderMonty uses a Minervini 7-Point Stage 2 Trend Template
(Price > SMA150 > SMA200, SMA200 up ≥ 22 days, RS rank > 70, etc.) — a single-
timeframe multi-criteria gate, not a D1/W1 cross-check. Our approach compares
the same indicators at two timeframes (daily vs weekly) for directional agreement.
Different method, same goal: reduce false signals.

---

## Cross-Plugin Handoff

Pass the snapshot card to `domain-teams:investing-team` for full analysis:

```
Workflow: technical-snapshot → us-stock-snapshot → domain-teams:investing-team
```

Technical indicators are one input layer. Do not make buy/hold/sell verdicts
from technical signals alone — route to investing-team for full memo with
fundamental + regime + technical synthesis.

---

## Limitations

- Requires ≥ 200 trading days of data for SMA-200 (use `period=1y` or `period=2y`)
- yfinance is unofficial — data may have gaps or lags on Taiwan (.TW) tickers
- Technical indicators are lagging by nature; high %B or RSI extremes do not
  guarantee reversal without fundamental/regime context
