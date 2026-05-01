---
name: analysis-portfolio
description: >-
  Pure-compute portfolio P&L + holdings stats. Input: --holdings <csv-or-json-path>
  --prices <data-pack-json-path>. Output: position P&L matrix + portfolio
  aggregates JSON.
  ポートフォリオ純計算層 — 損益と保有比率。組合純計算層 — 損益與權重。
---

# analysis-portfolio

Layer 2 (Analysis) — pure compute. Given a holdings file and a price data
pack, return per-position P&L plus portfolio-level aggregates as JSON.

This skill does **NO I/O**:
- No price fetch (consumed via `--prices` from a `data-{country}/pack.py
  --pack screener-batch` pull, possibly concatenated cross-country by the
  caller)
- No macro overlay (delegated to `analysis-macro-regime` and composed by
  `report-portfolio-review`)
- No rebalance recommendation (delegated to
  `domain-teams:investing-team` Portfolio Review workflow by the report
  layer)

---

## Contract

### Inputs

| Flag | Required | Format | Notes |
|---|---|---|---|
| `--holdings` | ✅ | path | CSV or JSON (auto-detected by extension) |
| `--prices` | ✅ | path | JSON list/object of `{ticker, price}` records |

**Holdings — CSV** (header row required):
```csv
ticker,quantity,cost_basis
AAPL,100,150.00
MSFT,50,300.00
```
Holdings CSV columns: `ticker`, `quantity` (alias: `shares`),
`cost_basis` (aliases: `avg_cost` / `cost`), `purchase_date` (optional,
ISO `YYYY-MM-DD`; alias: `acquired_at`). `purchase_date` is passed
through to output, not used in compute.

**Holdings — JSON** (equivalent shape):
```json
[
  {"ticker": "AAPL", "quantity": 100, "cost_basis": 150.00},
  {"ticker": "MSFT", "quantity": 50,  "cost_basis": 300.00}
]
```

**Prices — JSON**:
```json
[
  {"ticker": "AAPL", "price": 180.50},
  {"ticker": "MSFT", "price": 420.00}
]
```
Also accepts an object form `{"AAPL": 180.50, ...}` or screener-batch
records with `regularMarketPrice`/`last_price` fields. The script
extracts a price for each ticker present in holdings.

### Output

```json
{
  "positions": [
    {
      "ticker": "AAPL",
      "quantity": 100,
      "cost_basis": 150.00,
      "current_price": 180.50,
      "market_value": 18050.00,
      "pnl_abs": 3050.00,
      "pnl_ratio": 0.2033,
      "weight": 0.32,
      "contribution": 0.0541
    }
  ],
  "totals": {
    "total_cost": 56500.00,
    "total_market_value": 56300.00,
    "total_pnl_abs": -200.00,
    "total_pnl_ratio": -0.00354,
    "position_count": 3,
    "max_weight": 0.37,
    "max_weight_ticker": "MSFT"
  },
  "_provenance": {
    "skill": "analysis-portfolio",
    "computed_at": "<ISO timestamp>",
    "holdings_path": "...",
    "prices_path": "...",
    "missing_prices": []
  }
}
```

**Units** — all ratio fields are fractional (0.0–1.0):
- `pnl_ratio`: position-level return on cost basis (e.g. `0.4033` = +40.33%)
- `total_pnl_ratio`: portfolio return on cost basis
- `weight`: position market value / total portfolio market value
- `contribution`: position pnl / total portfolio cost (signed)
- `max_weight`: largest position weight

**Formulas**:
- `pnl_ratio = pnl_abs / (quantity × cost_basis)`
- `total_pnl_ratio = total_pnl_abs / total_cost` (return on cost basis;
  analogous to time-weighted-return-on-invested-capital)
- `weight = market_value / total_market_value`
- `contribution = pnl_abs / total_cost`

Positions are sorted by descending `weight` in the output array.

Currency is **not converted** — multi-currency portfolios produce a
notional sum and rely on the caller (or report layer) to flag
discrepancies. Provenance carries `missing_prices` for tickers where no
price was found.

---

## Usage

```bash
uv run scripts/portfolio_compute.py \
  --holdings /path/to/holdings.csv \
  --prices /path/to/prices.json
```

Pipe into `report-portfolio-review` (Layer 3) which composes:
1. `data-{country}/pack.py --tickers ... --pack screener-batch` per country group
2. concatenate price packs
3. `analysis-portfolio --holdings ... --prices <combined>`
4. `analysis-macro-regime` overlay
5. `domain-teams:investing-team` Portfolio Review for rebalance memo

---

## Limitations

- Pure point-in-time snapshot; no historical performance tracking.
- No FX conversion across currencies.
- No regime / sector / Kelly-sizing logic — those are deliberately in
  `analysis-macro-regime` and `domain-teams:investing-team`.
- Tickers in `--holdings` without a corresponding price entry are
  surfaced via `_provenance.missing_prices` and excluded from totals.

---

## Cross-Plugin Delegation Contract

This skill is the analysis layer only. Per repo `CLAUDE.md` §Cross-Plugin
Delegation Contract:
- Data fetch lives in `data-{country}` skills (Layer 1).
- Analysis math lives here (Layer 2).
- Orchestration + delegation to `domain-teams:investing-team` lives in
  `report-portfolio-review` (Layer 3).
