# /invest-portfolio

**Trigger**: `/invest-portfolio [holdings.csv | inline-list]`

Routes to `invest-portfolio` skill.

## Usage

```
# From CSV file
/invest-portfolio holdings.csv

# Inline holdings (ticker:shares:avg_cost)
/invest-portfolio AAPL:100:150.00, MSFT:50:280.00, NVDA:30:420.00

# Mixed US + Taiwan
/invest-portfolio AAPL:100:150.00, 2330.TW:200:550.00
```

## CSV Format

```csv
ticker,shares,avg_cost
AAPL,100,150.00
MSFT,50,280.00
2330.TW,200,550.00
```

## Output

1. **Portfolio snapshot** — current value, P&L, weights, IC regime alignment
2. **Regime overlay** — IC phase alignment per position
3. **Rebalance recommendations** — from `domain-teams:investing-team` Portfolio Review
4. **Gate verdicts** — MUST + SHOULD gates from investing-team

## Notes

- Multi-currency portfolios (USD + TWD) show P&L per currency, not converted
- Taiwan positions require FinMind (`FINMIND_API_TOKEN` optional, see `scripts/README.md`)
- For deep analysis of individual positions, use `/invest-memo {ticker}`
