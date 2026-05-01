# /invest-memo

**Trigger**: `/invest-memo {ticker} [--scope deep|quick]`

Full investment memo pipeline. Fetches data → regime context → analysis → routes to `domain-teams:investing-team` for primary-source-grounded analysis + quality gates. Outputs a BUY / HOLD / SELL verdict with position sizing, variant perception, pre-mortem, and scenario stress-test.

## What This Does

Invokes `skills/report-equity-memo/SKILL.md`, which orchestrates:

```
data-{country}/pack.py --pack memo-fetch       (Layer 1: country auto-route)
  ↓
data-{country}/pack.py --pack regime-pack      (Layer 1: home + US for non-US in deep mode)
  ↓
analysis-macro-regime/regime_compose.py        (Layer 2: IC + GIP)
analysis-dcf/dcf_compute.py                    (Layer 2: 3-stage DCF + 3×3 sensitivity)
  ↓ [PR 2: analysis-comps when integrated]
domain-teams:investing-team                    (Deep Equity Research Memo + 2 MUST + 4 SHOULD + 1 MAY gates)
  ↓
domain-teams:docs-team (optional)              (polished Markdown formatting)
```

## Examples

```
/invest-memo AAPL
/invest-memo NVDA --scope deep
/invest-memo MSFT --scope quick
/invest-memo 2330.TW
/invest-memo 7203               # JP bare 4-digit auto-routed to data-jp
/invest-memo 005930.KS          # KR
/invest-memo 600519.SS          # CN
```

## Notes

- **scope=deep** (default): Full 4–8k word memo, all gates, Phase 1+2+3+4+5 — ~5-10 min
- **scope=quick**: Snapshot data only, MUST gates only, skips Phase 2 regime + Phase 3 DCF — ~1-2 min
- Country auto-routing by ticker suffix: `.TW/.TWO → data-tw`, `.T/4-digit → data-jp`, `.KS/.KQ → data-kr`, `.SS/.SZ/.HK → data-cn`, else → data-us
- JP memo with EDINET Tier A: set `EDINET_API_KEY` env var; without key, falls back to yfinance Tier 2 with explicit provenance label
- All free data sources (no API keys required for core); optional: `FRED_API_KEY`, `EDINET_API_KEY`
