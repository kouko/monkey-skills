# /invest-portfolio

**Trigger**: `/invest-portfolio [holdings.csv]`

> **Coming in investing-toolkit v1.2.0.**

In the meantime:
- Provide your holdings list directly and use `domain-teams:investing-team` Portfolio Review workflow

## Planned Capabilities (v1.2.0)

```
/invest-portfolio                    # Interactive holdings entry
/invest-portfolio holdings.csv       # Load from CSV (ticker, shares, avg_cost)
```

Outputs:
- Portfolio snapshot (current weights, PE, PB, beta-weighted)
- Regime overlay (IC phase alignment per position)
- Rebalance suggestions with Kelly-based sizing rationale
- Concentration risk flags

See `ROADMAP.md` for timeline.
