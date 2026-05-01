---
name: analysis-technical
description: >-
  Pure-compute technical indicators (RSI-14 / MACD-12-26-9 / Bollinger-20 /
  ATR-14 / SMA-20-50-200). Input: --input <ohlcv-json-path> from
  data-{country}/pack.py --pack snapshot. Output: indicators JSON.
  テクニカル指標の純粋計算層。技術指標純計算層。
---

# analysis-technical

Pure-compute technical indicator skill (Layer 2 — Analysis). Takes an OHLCV
JSON file produced by Layer 1 data skills (`data-{country}/pack.py --pack
snapshot`) and emits a structured indicator JSON. **No network, no fetch, no
HTTP** — all I/O happens in Layer 1.

This skill is the **canonical home** of `ta_client.py`. Other analysis skills
that need TA computations (e.g. `analysis-screener`) embed a functional copy
of the same file; CI enforces MD5 equality across copies.

---

## Layer 2 contract

- **Input**: `--input <path-to-ohlcv-json>` produced by `data-{country}/pack.py
  --pack snapshot` (or any source emitting the same `{ticker, history: [...]}`
  shape — yfinance / FinMind / TWSE `/rwd/` are all supported).
- **Output**: indicator JSON to stdout.
- **No I/O**: this skill does NOT make HTTP calls, does NOT shell out to
  fetchers, does NOT read environment-driven cache directories. Pure compute
  only.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--input` | yes | — | Path to OHLCV JSON, or `-` for stdin |
| `--indicators` | no | `rsi,macd,bb,atr,sma` | Comma-separated subset |

OHLCV JSON shape (any of the following keys per row work):

```json
{
  "ticker": "AAPL",
  "history": [
    {"date": "2025-01-02", "open": 100.1, "high": 101.0, "low": 99.5, "close": 100.7, "volume": 1234567},
    ...
  ]
}
```

Aliases: `data` instead of `history`, capitalised `Open / High / Low / Close`
all work (matches yfinance / FinMind / TWSE conventions). Minimum 200 rows
needed for SMA-200.

---

## Usage

```bash
# Verify uv (one-time)
command -v uv || sh ${CLAUDE_SKILL_DIR}/scripts/setup.sh

# All indicators (default)
uv run ${CLAUDE_SKILL_DIR}/scripts/ta_compute.py --input ohlcv.json

# Subset
uv run ${CLAUDE_SKILL_DIR}/scripts/ta_compute.py --input ohlcv.json --indicators rsi,macd

# Stdin
cat ohlcv.json | uv run ${CLAUDE_SKILL_DIR}/scripts/ta_compute.py --input -
```

---

## Output schema

```json
{
  "ticker": "AAPL",
  "as_of": "2025-12-31",
  "close": 195.42,
  "indicators": {
    "rsi_14": 58.3,
    "macd": {"line": 1.42, "signal": 1.18, "histogram": 0.24},
    "bollinger": {"upper": 198.7, "mid": 192.1, "lower": 185.5, "pct_b": 0.74},
    "atr_14": 3.21,
    "atr_pct": 1.64,
    "sma": {"20": 192.1, "50": 188.4, "200": 175.8}
  },
  "signals": {
    "rsi_signal": "neutral",
    "macd_crossover": "bullish",
    "bb_signal": "upper_half",
    "trend_alignment": "strong_bullish",
    "price_vs_sma200": "above"
  },
  "_provenance": {
    "skill": "analysis-technical",
    "ta_client_version": "v1.16.3",
    "ta_client_role": "canonical-master",
    "rows_consumed": 252,
    "indicators_requested": ["rsi", "macd", "bb", "atr", "sma"],
    "warnings": []
  }
}
```

### Provenance fields

| Field | Description |
|-------|-------------|
| `skill` | Always `"analysis-technical"` (the producing skill). |
| `ta_client_version` | Version tag matching the MD5 of canonical `ta_client.py`. Bumped whenever the canonical is edited so consumers can detect TA-logic changes. |
| `ta_client_role` | Role of this skill's local `ta_client.py` copy. `"canonical-master"` here; sibling skills (e.g. `analysis-screener`) embed a `"functional-copy"` with MD5 enforced equal. |
| `rows_consumed` | Number of OHLCV rows received from the input. |
| `indicators_requested` | Sorted list of indicator slugs requested via `--indicators`. |
| `warnings` | List of human-readable strings naming any indicator that returned `None` because the input had fewer rows than the indicator's lookback (e.g. `"sma_200 unavailable: rows_consumed=50 < 200"`). Empty list when all requested indicators computed cleanly. |

### Signal vocabulary (closed enums)

All signal values are lowercase snake_case. Signal-name → allowed values:

| Signal | Allowed values |
|--------|----------------|
| `rsi_signal` | `"oversold"` / `"neutral"` / `"overbought"` / `"n/a"` |
| `macd_crossover` | `"bullish"` / `"bearish"` / `"n/a"` |
| `bb_signal` | `"above_upper"` / `"upper_half"` / `"lower_half"` / `"below_lower"` / `"n/a"` |
| `price_vs_sma200` | `"above"` / `"below"` / `"n/a"` |
| `trend_alignment` | `"strong_bullish"` / `"bullish"` / `"neutral"` / `"bearish"` / `"strong_bearish"` / `"n/a"` |

`ta_client.py` (canonical) emits Title-Case strings; `ta_compute.py` translates
them to this closed enum at the output boundary so consumers get a stable
vocabulary without modifying the canonical source.

---

## Indicator reference

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
| ATR | EMA of True Range | period=14 |
| ATR % | ATR-14 as % of latest close (volatility normalised to price) | derived from `atr_14` and `close` |
| SMA | Simple moving average | 20, 50, 200 |

Signal interpretation:

| Indicator | Signal | Meaning |
|-----------|--------|---------|
| RSI < 30 | `oversold` | Potential reversal up |
| RSI > 70 | `overbought` | Potential reversal down |
| MACD line > signal | `bullish` | Upward momentum |
| MACD line < signal | `bearish` | Downward momentum |
| %B > 1.0 | `above_upper` | Statistically extended |
| %B < 0.0 | `below_lower` | Statistically compressed |
| close > SMA20 > SMA50 > SMA200 | `strong_bullish` | Full uptrend stack |

---

## Canonical ta_client.py

`scripts/ta_client.py` in this skill is the **master copy**. CI enforces MD5
equality between this file and:

- `investing-toolkit/scripts/ta_client.py` (toolkit-level shared lib)
- Any other `analysis-*/scripts/ta_client.py` that uses TA (e.g. screener)

To update TA logic: edit this file first, then `scripts/sync-scripts.sh` from
the toolkit root propagates the change. CI fails the PR if MD5s drift.

---

## Limitations

- ≥ 200 rows required for SMA-200 (use `period=1y` or longer at the data layer)
- Lagging by nature — indicator extremes do not guarantee reversal without
  fundamental + regime context (route synthesis to `report-equity-memo` or
  `domain-teams:investing-team`)
- Pure compute — does not fetch data; upstream Layer 1 skill must supply
  split/dividend-adjusted prices (yfinance default) or raw prices (TWSE
  `/rwd/`) per the report's needs

---

## i18n

- 中文（繁體）: 純計算技術指標層。輸入由 Layer 1 資料層提供的 OHLCV JSON，
  輸出 RSI / MACD / 布林通道 / ATR / SMA 指標 JSON，不做任何網路 I/O。
- 日本語: 純粋計算のテクニカル指標層。Layer 1 のデータスキルが生成した
  OHLCV JSON を入力に、RSI / MACD / ボリンジャー / ATR / SMA を計算した
  指標 JSON を返す。ネットワーク I/O は行わない。
