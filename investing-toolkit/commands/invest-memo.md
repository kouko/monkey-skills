# /invest-memo

**Trigger**: `/invest-memo {ticker} [--scope deep|quick]`

Full investment memo pipeline. Fetches data → regime context → routes to
`domain-teams:investing-team` for primary-source-grounded analysis + quality gates.

Outputs a BUY / HOLD / SELL verdict with position sizing rationale, variant
perception thesis, pre-mortem, and scenario stress-test.

## What This Does

Invokes `skills/investment-memo-writer/SKILL.md`, which orchestrates:

```
data-fetcher (yfinance + FRED)
  ↓
macro-regime-snapshot (IC phase + GIP quadrant)
  ↓
domain-teams:investing-team Deep Equity Research Memo
  ↓  (2 MUST + 3 SHOULD + 1 MAY gates)
Full investment memo
  ↓  (optional)
domain-teams:docs-team (polished formatting)
```

## Examples

```
/invest-memo AAPL
/invest-memo NVDA --scope deep
/invest-memo MSFT --scope quick
/invest-memo 2330.TW
```

## Notes

- **scope=deep** (default): Full 4–8k word memo, all gates, ~5-10 min
- **scope=quick**: 1-page screen card, MUST gates only, ~1-2 min
- **Taiwan tickers (.TW/.TWO)**: yfinance provides price/info only in v1.0.0.
  Full Taiwan data (三大法人, 月營收, 融資融券, 董監持股) requires investing-toolkit v1.1.0 (FinMind adapter).
- Requires Python: `pip install -r investing-toolkit/scripts/requirements.txt`
- For free FRED API key: `export FRED_API_KEY=your_key`
