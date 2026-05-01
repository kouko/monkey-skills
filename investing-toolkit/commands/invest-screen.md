# /invest-screen

**Trigger**: `/invest-screen {tickers} [--preset NAME] [options]`

Cross-country stock screener with composite scoring. Routes to `report-screener-list` (Layer 3 orchestrator).

## What This Does

Pipeline (main agent dispatches):
1. Parse ticker list → group by country suffix
2. Parallel: `data-{country}/pack.py --tickers ... --pack screener-batch` per country group
3. Concat batch JSONs (with `_partial` propagation)
4. `analysis-screener/screener_compute.py --input combined.json --preset {preset}` → ranked top-N
5. `report-screener-list/screener_format.py --input ranked.json` → 14-column Markdown table

## Usage

```
/invest-screen AAPL,MSFT,NVDA
/invest-screen AAPL,MSFT,NVDA --preset value
/invest-screen AAPL,MSFT,NVDA,GOOGL,META --preset momentum --top-n 3
/invest-screen 2330.TW,2454.TWO,2317.TW --preset quality
/invest-screen AAPL,2330.TW,7203 --preset balanced     # mixed-country
/invest-screen AAPL,MSFT,NVDA --pe-max 40 --above-sma200    # manual criteria
```

## Options

| Option | Description |
|---|---|
| `--preset NAME` | One of 8: `value` / `deep-value` / `quality` / `high-dividend` / `growth` / `growth-value` / `momentum` / `balanced` |
| `--pe-max N` | Filter: trailing PE ≤ N |
| `--pb-max N` | Filter: price/book ≤ N |
| `--rsi-min N` | Filter: RSI ≥ N |
| `--rsi-max N` | Filter: RSI ≤ N |
| `--above-sma200` | Filter: price above SMA-200 only |
| `--min-volume N` | Filter: volume ≥ N shares |
| `--top-n N` | Return top N (default: 10) |

## Presets (8)

| Preset | Style | Key Filters |
|---|---|---|
| `value` | Classic value | PE ≤ 15, PB ≤ 1.5, div ≥ 2%, ROE ≥ 5% |
| `deep-value` | Contrarian | PE ≤ 8, PB ≤ 0.5 |
| `quality` | Compounders | PE ≤ 15, PB ≤ 1.5, ROE ≥ 15%, div ≥ 2% |
| `high-dividend` | Income | Div ≥ 3%, PE ≤ 20, ROE ≥ 5% |
| `growth` | Quality growth | ROE ≥ 15%, rev-growth ≥ 5%, earnings-growth ≥ 10% |
| `growth-value` | GARP | PE ≤ 20, ROE ≥ 10%, rev-growth ≥ 5% |
| `momentum` | Trend following | RSI 50–80, above SMA200 |
| `balanced` | Default (no filters) | — |

## Notes

- **Quality / growth / growth-value** presets rely on `returnOnEquity` / `revenueGrowth` / `earningsGrowth`; US `data-us/pack.py screener-batch` may omit some — falls back to neutral defaults (0.50) with `_warnings` per ticker
- Cross-country mixed lists supported (US + JP + TW + KR + CN auto-grouped)
- For full analysis of top candidates → `/invest-memo {ticker}`
