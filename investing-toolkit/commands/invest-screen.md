# /invest-screen

**Trigger**: `/invest-screen {ticker|criteria}`

> **Coming in investing-toolkit v1.2.0.**

In the meantime:
- For a single stock → use `/invest-memo {ticker} --scope quick`
- For manual screening → use `domain-teams:investing-team` Quick Stock Screen workflow

## Planned Capabilities (v1.2.0)

```
/invest-screen AAPL              # Quick screen card on single ticker
/invest-screen --pe-max 20       # US stocks with PE ≤ 20
/invest-screen --universe tw50   # Taiwan top-50 screener (requires v1.1.0 FinMind)
```

See `ROADMAP.md` for timeline.
