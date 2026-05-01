# /invest-portfolio

**Trigger**: `/invest-portfolio [holdings.csv | inline-list]`

Portfolio P&L review with optional macro-regime overlay. Routes to `report-portfolio-review` (Layer 3 orchestrator).

## What This Does

Pipeline (main agent dispatches):
1. Parse holdings (CSV or inline)
2. Group tickers by country suffix
3. Parallel: `data-{country}/pack.py --tickers ... --pack screener-batch` per country group
4. Concat per-country batch JSONs into combined.json
5. `analysis-portfolio/portfolio_compute.py --holdings ... --prices combined.json` → P&L matrix (positions sorted by weight desc; JP `7203` ↔ `7203.T` auto-resolved; KR `.KS`/`.KQ` auto-resolved)
6. (Optional) `data-{country}/pack.py --pack regime-pack` for relevant countries → `analysis-macro-regime/regime_compose.py` → regime card
7. `report-portfolio-review/review_format.py --portfolio ... --regime ...` → Markdown

## Usage

```
# From CSV file
/invest-portfolio holdings.csv

# Inline holdings (ticker:shares:avg_cost)
/invest-portfolio AAPL:100:150.00, MSFT:50:280.00, NVDA:30:420.00

# Cross-country (US + TW + JP)
/invest-portfolio AAPL:100:150.00, 2330.TW:200:550.00, 7203:50:2500.00
```

## CSV Format

```csv
ticker,quantity,cost_basis
AAPL,100,150.00
MSFT,50,280.00
2330.TW,200,550.00
```

Aliases accepted: `shares` (=quantity), `avg_cost` / `cost` (=cost_basis), `acquired_at` (=purchase_date).

## Output

1. **Portfolio summary** — total cost, market value, P&L absolute + ratio (fractional 0.0–1.0)
2. **Positions table** — sorted by weight desc; per-position market value, P&L ratio (rendered as %), weight, contribution
3. **Concentration analysis** — max_weight + top3_weight (>30% triggers concentrated flag)
4. **Macro regime overlay** (optional) — IC + GIP per country, cross-country consensus
5. **Provenance footer** — data sources + missing-price tickers + ticker-suffix resolutions

## Notes

- Multi-currency portfolios (USD + TWD + JPY): P&L per-currency, not converted
- JP/KR ticker suffix mismatch: holdings file `7203` matches data-jp's `7203.T` via `_resolve_price` fallback (logged in `_provenance.ticker_resolutions`)
- For deep analysis of individual positions → `/invest-memo {ticker}`
- For rebalance recommendations → invoke `domain-teams:investing-team` Portfolio Review directly
