# /invest-screen

**Trigger**: `/invest-screen {tickers} [options]`

Routes to `stock-screener` skill.

## Usage

```
/invest-screen AAPL,MSFT,NVDA
/invest-screen AAPL,MSFT,NVDA --preset value
/invest-screen AAPL,MSFT,NVDA,GOOGL,META --preset momentum --top-n 3
/invest-screen 2330.TW,2454.TWO,2317.TW --preset quality
/invest-screen AAPL,MSFT,NVDA --pe-max 40 --above-sma200    # manual criteria
```

## Options

| Option | Description | Example |
|--------|-------------|---------|
| `--preset NAME` | Preset strategy: value, growth, momentum, quality, high-dividend, balanced | `--preset value` |
| `--pe-max N` | Filter: trailing PE ≤ N | `--pe-max 30` |
| `--pb-max N` | Filter: price/book ≤ N | `--pb-max 5` |
| `--rsi-min N` | Filter: RSI ≥ N | `--rsi-min 40` |
| `--rsi-max N` | Filter: RSI ≤ N | `--rsi-max 70` |
| `--above-sma200` | Filter: price above SMA-200 only | — |
| `--min-volume N` | Filter: volume ≥ N shares | `--min-volume 1000000` |
| `--top-n N` | Return top N results (default: 10) | `--top-n 5` |
| `--period P` | Price history lookback (default: 1y) | `--period 2y` |

## Presets

| Preset | Style | Key Filters |
|--------|-------|-------------|
| `value` | Graham deep value | PE ≤ 15, PB ≤ 2.5 |
| `growth` | Growth at reasonable pace | Revenue-YoY > 20% |
| `momentum` | Trend following | RSI 50–80, above SMA200 |
| `quality` | Compounders | ROE > 15%, PE ≤ 30 |
| `high-dividend` | Income | Div yield > 3%, PE ≤ 20 |
| `balanced` | Default baseline | No preset filters |

## Output

Ranked table by composite score (weights vary by preset) + ISQ 5-dimension profile
(Intrinsic / Strength / Quality / Sentiment / Timeliness).

For full analysis of top candidates, use `/invest-memo {ticker}`.
