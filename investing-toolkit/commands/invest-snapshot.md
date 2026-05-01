# /invest-snapshot

**Trigger**: `/invest-snapshot {ticker} [--lang en|zh-TW|ja]`

Single-ticker quick snapshot card. Routes to `report-stock-snapshot` (Layer 3 orchestrator).

## What This Does

Pipeline (main agent dispatches):
1. Country auto-detection by ticker suffix
2. `data-{country}/pack.py --ticker {ticker} --pack snapshot` → JSON
3. `report-stock-snapshot/snapshot_format.py --input snap.json --country {detected} [--lang ...]` → Markdown card

## Usage

```
/invest-snapshot AAPL
/invest-snapshot 2330.TW
/invest-snapshot 7203                   # JP bare 4-digit auto-routed
/invest-snapshot 005930.KS              # Samsung
/invest-snapshot 600519.SS              # Kweichow Moutai
/invest-snapshot 0700.HK                # Tencent
/invest-snapshot 09988                  # Alibaba HK 5-digit
/invest-snapshot 2330.TW --lang zh-TW   # Force Traditional Chinese rendering
```

## Output

Single-page Markdown card with:
- Header (ticker / name / exchange / sector)
- Price block (current / 52W high-low / 1Y return)
- Valuation block (P/E, Forward P/E, P/B, market cap, EV)
- Returns / dividends
- Recent disclosures (TDnet for JP / MOPS material events for TW / 8-K for US)
- Tier-routing provenance footer

## Notes

- 3 languages supported (en / zh-TW / ja) with auto-detect by ticker suffix; explicit `--lang` overrides
- For full memo with verdict → use `/invest-memo {ticker}`
- For multi-ticker comparison → use `/invest-screen {tickers}`
- KR / CN snapshots are yfinance Tier 2 (DART / cninfo / HKEXnews primary-source deferred to v2.1+)
