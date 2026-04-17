---
name: stock-screener
description: >-
  Multi-criteria stock screener. Batch-fetches OHLCV + info for a user-provided
  ticker list via yfinance, computes technical indicators via ta_client.py,
  applies valuation/momentum/trend filters, and ranks by composite score.
  Returns top-N table. US and Taiwan tickers supported.
  銘柄スクリーナー。股票篩選器。
---

# stock-screener

Screens a user-provided list of tickers against valuation, momentum, and trend
criteria. Uses batch yfinance fetching and `ta_client.py` for indicator
computation. Outputs a ranked table with composite scores.

**Scope**: User-provided ticker list (US or Taiwan). Predefined universes
(S&P 500, TW50) are planned for v1.3.0.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `tickers` | yes | — | Comma-separated: `AAPL,MSFT,NVDA` or `2330.TW,2454.TWO` |
| `--pe-max` | no | — | Filter: trailing PE ≤ value |
| `--pb-max` | no | — | Filter: price/book ≤ value |
| `--rsi-min` | no | — | Filter: RSI ≥ value (momentum floor) |
| `--rsi-max` | no | — | Filter: RSI ≤ value (overbought cap) |
| `--above-sma200` | no | false | Filter: price > SMA-200 only |
| `--min-volume` | no | — | Filter: avg daily volume ≥ value (shares) |
| `--top-n` | no | 10 | Return top N ranked results |
| `--period` | no | `1y` | Price history lookback |

---

## Preset Strategies

Use `--preset {name}` instead of manual criteria. Presets apply predefined filter
+ scoring weights. User criteria override preset defaults when both are specified.

**Value strategies** (source: stock-skills screening_presets.yaml)

| Preset | Filters | Scoring Emphasis | Style |
|--------|---------|-----------------|-------|
| `value` | PE ≤ 15, PB ≤ 1.5, div ≥ 2%, ROE ≥ 5% | valuation 60%, trend 25%, momentum 15% | Classic value |
| `deep-value` | PE ≤ 8, PB ≤ 0.5 | valuation 70%, trend 20%, momentum 10% | Contrarian deep discount |
| `quality` | PE ≤ 15, PB ≤ 1.5, ROE ≥ 15%, div ≥ 2% | valuation 40%, quality 35%, trend 25% | Compounders |
| `high-dividend` | div ≥ 3%, PE ≤ 20, ROE ≥ 5% | valuation 55%, trend 25%, momentum 20% | Income |

**Growth strategies**

| Preset | Filters | Scoring Emphasis | Style |
|--------|---------|-----------------|-------|
| `growth` | ROE ≥ 15%, rev-growth ≥ 5%, earnings-growth ≥ 10% | momentum 45%, trend 35%, valuation 20% | Quality growth |
| `growth-value` | PE ≤ 20, ROE ≥ 10%, rev-growth ≥ 5% | valuation 40%, momentum 35%, trend 25% | GARP — growth at reasonable price |

**Tactical strategies**

| Preset | Filters | Scoring Emphasis | Style |
|--------|---------|-----------------|-------|
| `momentum` | RSI 50–80, above SMA200 | momentum 50%, trend 40%, valuation 10% | Trend following |
| `balanced` | (none — default) | valuation 40%, momentum 30%, trend 30% | Baseline — same as no preset |

**Preset usage**:
```
/invest-screen AAPL,MSFT,NVDA,JNJ,KO --preset value
/invest-screen 2330.TW,2454.TWO,2317.TW --preset momentum
/invest-screen AAPL,MSFT,NVDA --preset growth --pe-max 50  ← override preset PE
```

When a preset filter requires data not available via yfinance (e.g. revenue-YoY,
ROE), tickers missing that data pass with a `N/A — data unavailable` note. The
filter is soft: it does not exclude, only penalizes scoring.

---

## How It Works

### Step 1 — Batch data fetch (data-fetcher agent)

Launch `../../agents/data-fetcher.md` with two parallel batch requests:

```
### Fetch Requests
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --tickers {ticker_list} --period {period}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --tickers {ticker_list} --action info
```

Expected output:
```json
{
  "price_batch": {"tickers": {"AAPL": {...}, "MSFT": {...}}},
  "info_batch":  {"tickers": {"AAPL": {...}, "MSFT": {...}}}
}
```

If any ticker fails, continue with `_partial: true` — do not block.

---

### Step 2 — Compute indicators per ticker

Before running scripts directly, verify uv is installed:
```bash
command -v uv || sh ${CLAUDE_SKILL_DIR}/scripts/setup.sh
```

For each ticker with valid OHLCV data, compute indicators:

```bash
# Pipe each ticker's price JSON to ta_client.py
echo '{price_json_for_AAPL}' | INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/ta_client.py --input -
```

Extract from `ta_client.py` output:
- `rsi_14`, `rsi_signal`
- `macd_crossover`
- `sma_200`, `price_vs_sma200`
- `trend_alignment`

---

### Step 3 — Apply filters

For each ticker, evaluate pass/fail against user criteria:

| Filter | Pass condition |
|--------|--------------|
| `--pe-max N` | `trailingPE ≤ N` (or N/A → skip, note in output) |
| `--pb-max N` | `priceToBook ≤ N` |
| `--rsi-min N` | `rsi_14 ≥ N` |
| `--rsi-max N` | `rsi_14 ≤ N` |
| `--above-sma200` | `price_vs_sma200 = "above"` |
| `--min-volume N` | latest volume ≥ N |

Tickers failing any filter are excluded from ranking but listed in a
"Filtered out" section.

---

### Step 4 — Compute composite score

For each passing ticker, compute a 0–100 composite score using weights from the
active preset (or `balanced` default):

```
momentum_score  = normalize(rsi_14, 0, 100)
valuation_score = normalize(1/trailingPE, 0, 1)   ← lower PE = higher score
trend_score     = (1.0 if price_vs_sma200 = "above" else 0.5) + (0.5 if macd_crossover = "Bullish" else 0.0)

composite = (momentum_score × W_m + valuation_score × W_v + trend_score × W_t) × 100
```

Default weights (balanced): W_v=0.40, W_m=0.30, W_t=0.30.
Preset weights override — see Preset Strategies table above.

If `trailingPE` is missing, set valuation_score = 0.20 (neutral) and note in output.

---

### Step 5 — Render ranked table

```markdown
## Screen Results — {date}
**Preset**: {preset_name} | **Universe**: {N} tickers | **Passed**: {M} | **Top {top_n}**

| Rank | Ticker | Price | PE | PB | RSI | SMA200 | MACD | Score |
|------|--------|-------|----|-----|-----|--------|------|-------|
| 1 | NVDA | $890 | 45.2 | 28.1 | 62 Neutral | Above | Bullish | 74.2 |
| 2 | MSFT | $415 | 32.1 | 12.4 | 55 Neutral | Above | Bullish | 68.5 |
| ... |

### Filtered Out
| Ticker | Reason |
|--------|--------|
| XYZ | PE 85.3 > max 15 (value preset) |

_Data via yfinance (unofficial). Scores are relative — not investment recommendations._
_For full analysis, route to `domain-teams:investing-team`._
```

---

## Score Interpretation

Composite score is **relative** within the screened universe, not absolute.
A score of 70 means this ticker ranks well against the others in your list — it
does NOT mean "buy".

**After screening**: route top candidates to:
- `us-stock-snapshot` + `technical-snapshot` for deeper data
- `domain-teams:investing-team` Quick Stock Screen for investment verdict

---

## Example Usage

```
/invest-screen AAPL,MSFT,NVDA,GOOGL,META
/invest-screen AAPL,MSFT,NVDA --preset value
/invest-screen AAPL,MSFT,NVDA,GOOGL,META --preset momentum --top-n 3
/invest-screen 2330.TW,2454.TWO,2317.TW --preset quality
/invest-screen AAPL,MSFT,NVDA --pe-max 40 --above-sma200    ← manual criteria
```

---

## Limitations

- yfinance `trailingPE` and `priceToBook` can be stale (updated ~daily)
- Volume data from yfinance is total volume, not average — screener uses latest day
- Taiwan tickers: PE/PB may be missing for some OTC stocks via yfinance
- No predefined universe (S&P 500, TW50) in v1.2.0 — provide your own ticker list
