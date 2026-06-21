---
name: analysis-screener
description: |
  Pure-compute screener: filter + composite score + ranking on pre-batched ticker data. Input: a data-pack JSON from data-{country}/pack.py --pack screener-batch (single or multi-country). Output: ranked top-N JSON.
---

# analysis-screener

> **Layer 2 contract (v2.0.0)**: Pure compute. **NO** I/O. **NO** network.
> **NO** yfinance / requests / urllib / httpx imports. Reads pre-batched
> ticker data JSON from disk, applies preset filters + composite scoring +
> ranking, emits ranked top-N JSON. Orchestration (parse ticker list,
> group by country, parallel `data-{country}/pack.py --pack screener-batch`,
> concatenate batches) is **`report-screener-list`**'s job (Phase 2).

Replaces the compute portion of legacy `stock-screener`. The fetch portion
moved to `data-{country}/pack.py --pack screener-batch`.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--input` | yes | — | Path to JSON file containing pre-batched ticker data (list of records, see below). Pass `-` to read stdin. |
| `--preset` | no | `balanced` | One of: `value`, `deep-value`, `quality`, `high-dividend`, `growth`, `growth-value`, `momentum`, `balanced` |
| `--top-n` | no | 10 | Return top N ranked results |
| `--pe-max` | no | preset | Override: trailing PE ≤ value |
| `--pb-max` | no | preset | Override: price/book ≤ value |
| `--rsi-min` | no | preset | Override: RSI ≥ value |
| `--rsi-max` | no | preset | Override: RSI ≤ value |
| `--above-sma200` | no | preset | Override: require price > SMA-200 |
| `--min-volume` | no | preset | Override: avg daily volume ≥ value |
| `--div-min` | no | preset | Override: dividend yield ≥ value (decimal, 0.02 = 2%) |
| `--roe-min` | no | preset | Override: ROE ≥ value (decimal) |
| `--w-valuation` | no | preset | Override valuation weight |
| `--w-momentum` | no | preset | Override momentum weight |
| `--w-trend` | no | preset | Override trend weight |
| `--w-quality` | no | preset | Override quality weight |

### Override semantics

Overrides **add to or replace** preset filter values, but cannot
**remove** an existing preset filter. To disable a preset filter,
either:

1. Use the `balanced` preset (no filters) and add only the filters
   you want via overrides, or
2. Pass a permissive sentinel value (e.g. `--pe-max 99999`,
   `--roe-min -1`) as a soft disable.

---

## Input JSON Schema

`--input` accepts either:

1. **Bare list** (testing / minimal):
   ```json
   [
     {"ticker": "AAPL", "trailingPE": 28.5, "priceToBook": 35.4,
      "returnOnEquity": 1.5, "dividendYield": 0.005},
     ...
   ]
   ```

2. **Wrapped pack** (production — concatenated `data-{country}/pack.py
   --pack screener-batch` output):
   ```json
   {
     "tickers": [
       {"ticker": "AAPL",
        "info": {"trailingPE": 28.5, "priceToBook": 35.4,
                 "returnOnEquity": 1.5, "dividendYield": 0.005,
                 "regularMarketPrice": 175.4, "twoHundredDayAverage": 165.2},
        "technicals": {"rsi_14": 62.3, "macd_crossover": "Bullish",
                       "price_vs_sma200": "above"},
        "volume": 50000000},
       ...
     ],
     "_provenance": [...]
   }
   ```

Per-record fields (all optional except `ticker`):
- `trailingPE`, `priceToBook`, `returnOnEquity`, `dividendYield`,
  `revenueGrowth`, `earningsGrowth`, `regularMarketPrice`,
  `twoHundredDayAverage`, `volume`
- `rsi_14`, `macd_crossover`, `price_vs_sma200` (from
  `analysis-technical` if pack stitches it; otherwise inferred from
  price vs `twoHundredDayAverage`)

Missing fields are handled gracefully: filters become **soft** (do not
exclude, only penalize scoring) and are noted in `_warnings`.

---

## Preset Strategies

User-supplied flags override preset defaults when both are specified.

### Value strategies

| Preset | Filters | Scoring Emphasis | Style |
|--------|---------|-----------------|-------|
| `value` | PE ≤ 15, PB ≤ 1.5, div ≥ 2%, ROE ≥ 5% | valuation 60%, trend 25%, momentum 15% | Classic value |
| `deep-value` | PE ≤ 8, PB ≤ 0.5 | valuation 70%, trend 20%, momentum 10% | Contrarian deep discount |
| `quality` | PE ≤ 15, PB ≤ 1.5, ROE ≥ 15%, div ≥ 2% | valuation 40%, quality 35%, trend 25% | Compounders |
| `high-dividend` | div ≥ 3%, PE ≤ 20, ROE ≥ 5% | valuation 55%, trend 25%, momentum 20% | Income |

### Growth strategies

| Preset | Filters | Scoring Emphasis | Style |
|--------|---------|-----------------|-------|
| `growth` | ROE ≥ 15%, rev-growth ≥ 5%, earnings-growth ≥ 10% | momentum 45%, trend 35%, valuation 20% | Quality growth |
| `growth-value` | PE ≤ 20, ROE ≥ 10%, rev-growth ≥ 5% | valuation 40%, momentum 35%, trend 25% | GARP |

### Tactical strategies

| Preset | Filters | Scoring Emphasis | Style |
|--------|---------|-----------------|-------|
| `momentum` | RSI 50–80, above SMA200 | momentum 50%, trend 40%, valuation 10% | Trend following |
| `balanced` | (none) | valuation 40%, momentum 30%, trend 30% | Baseline |

---

## Scoring Algorithm

For each passing ticker, compute 0–100 composite score with active preset
weights:

```
momentum_score  = clamp(rsi_14 / 100, 0, 1)              # rsi_14 ∈ [0, 100]
valuation_score = clamp(1 / max(trailingPE, 1), 0, 1)    # lower PE → higher
trend_score     = (1.0 if price_vs_sma200 == "above" else 0.5)
                + (0.5 if macd_crossover == "Bullish" else 0.0)
                # then clamped to [0, 1]
quality_score   = clamp(returnOnEquity / 0.30, 0, 1)     # anchors 30% ROE = excellent

composite = (W_v * valuation + W_m * momentum + W_t * trend + W_q * quality) * 100
```

Defaults when data missing:
- `trailingPE` missing → `valuation_score = 0.20` (neutral, noted)
- `rsi_14` missing → `momentum_score = 0.50` (neutral)
- `price_vs_sma200` missing → infer from `regularMarketPrice` vs
  `twoHundredDayAverage`; if both missing → `trend_score = 0.50`
- `returnOnEquity` missing → `quality_score = 0.50`

Weights that aren't part of a preset default to 0. Weights are always
normalized to sum to 1 before scoring (defensive against floating-point
drift and partial overrides).

`quality_score` formula: `clamp(ROE / 0.30, 0, 1)` — anchors 30% ROE
as "excellent quality". The 5–25% ROE band (most non-saturated
companies) spreads across 0.17–0.83, leaving headroom above for
top-tier compounders (e.g. Apple, Costco) that all saturate at 1.0.

---

## Output JSON Schema

```json
{
  "preset_used": "value",
  "filters_applied": {
    "pe_max": 15.0, "pb_max": 1.5, "div_min": 0.02, "roe_min": 0.05
  },
  "weights_applied": {"valuation": 0.60, "trend": 0.25, "momentum": 0.15, "quality": 0.0},
  "ranked": [
    {
      "rank": 1,
      "ticker": "BRK-B",
      "composite_score": 74.2,
      "breakdown": {
        "valuation": 0.71, "momentum": 0.55, "trend": 1.0, "quality": 0.43
      },
      "metrics": {
        "trailingPE": 14.1, "priceToBook": 1.42, "rsi_14": 55.0,
        "price_vs_sma200": "above", "macd_crossover": "Bullish"
      },
      "warnings": []
    }
  ],
  "filtered_out": [
    {"ticker": "XYZ", "reason": "trailingPE 85.3 > pe_max 15.0"}
  ],
  "universe_size": 50,
  "passed": 12,
  "returned": 10,
  "_provenance": {
    "skill": "analysis-screener",
    "version": "2.0.0",
    "input_path": "/path/to/batch.json",
    "computed_at": "2026-05-01T..."
  }
}
```

---

## Usage

```bash
# Bare list (mock / smoke test)
uv run scripts/screener_compute.py --input /tmp/screener-mock.json --preset value

# Production — multi-country pack concatenated by report-screener-list
uv run scripts/screener_compute.py --input /tmp/combined-pack.json --preset momentum --top-n 20

# Manual override on top of preset
uv run scripts/screener_compute.py --input /tmp/pack.json --preset value --pe-max 20 --w-valuation 0.5
```

---

## Score Interpretation

Composite score is **relative within the screened universe**, not absolute.
Score 70 means "this ticker ranks well against the others in your input";
it does NOT mean "buy". Route top candidates to:

- `report-stock-snapshot` for deeper data card
- `report-equity-memo` (which delegates to `domain-teams:investing-team`)
  for an investment verdict

---

## Limitations

- Pure compute: garbage-in-garbage-out. Stale or partial input data is
  surfaced via `warnings` per ticker, not corrected.
- `rsi_14` / `macd_crossover` / `price_vs_sma200` are expected from the
  upstream pack (data layer + analysis-technical). When absent,
  conservative neutral defaults apply.
- Cross-country group orchestration (parsing tickers, dispatching per
  country, concatenating batches) is **not** this skill's job — see
  `report-screener-list`.

---

<!-- i18n -->
日本語: 純計算のスクリーナー — 事前バッチ済みのティッカーデータ JSON を入力に、
プリセットフィルタ + 複合スコア + ランキングで Top-N JSON を出力する。
I/O・ネットワーク呼び出しは含まない。

繁體中文：純計算的選股篩選器 — 接收已預先批次取得的個股資料 JSON，
套用預設策略過濾條件、計算複合評分並排序，輸出 Top-N JSON。
不含任何 I/O 或網路呼叫。
