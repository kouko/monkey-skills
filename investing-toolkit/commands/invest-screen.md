# /invest-screen

**Trigger**: `/invest-screen {tickers} [options]`

Routes to `stock-screener` skill.

## Usage

```
/invest-screen AAPL,MSFT,NVDA
/invest-screen AAPL,MSFT,NVDA,GOOGL,META --pe-max 40 --above-sma200
/invest-screen 2330.TW,2454.TWO,2317.TW --top-n 3
```

## Options

| Option | Description | Example |
|--------|-------------|---------|
| `--pe-max N` | Filter: trailing PE ≤ N | `--pe-max 30` |
| `--pb-max N` | Filter: price/book ≤ N | `--pb-max 5` |
| `--rsi-min N` | Filter: RSI ≥ N | `--rsi-min 40` |
| `--rsi-max N` | Filter: RSI ≤ N | `--rsi-max 70` |
| `--above-sma200` | Filter: price above SMA-200 only | — |
| `--min-volume N` | Filter: volume ≥ N shares | `--min-volume 1000000` |
| `--top-n N` | Return top N results (default: 10) | `--top-n 5` |
| `--period P` | Price history lookback (default: 1y) | `--period 2y` |

## Output

Ranked table by composite score (momentum 30% + valuation 40% + trend 30%).
Filtered-out tickers listed with reasons.

For full analysis of top candidates, use `/invest-memo {ticker}`.
