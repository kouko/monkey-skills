---
name: taiwan-stock-snapshot
description: Taiwan equity snapshot via FinMind (ships in v1.1.0). Provides 三大法人買賣超、月營收、融資融券、董監持股 data for TWSE and OTC-listed stocks.
---

# taiwan-stock-snapshot

This skill provides Taiwan equity data — 三大法人買賣超、月營收、融資融券、董監持股 — via
the FinMind API. It ships in **investing-toolkit v1.1.0**.

See `../../ROADMAP.md` for the v1.1.0 timeline and planned FinMind adapter details.

---

## Status: Not Yet Available

taiwan-stock-snapshot is planned for v1.1.0 and is not available in the current release.

---

## Interim Options for Taiwan Data (v1.0.0)

Until v1.1.0 ships, use one of these approaches:

**1. Basic price data via us-stock-snapshot**

The `us-stock-snapshot` skill accepts `.TW` and `.TWO` tickers via yfinance. You get
OHLCV price history and basic company info (market cap, PE, PB where available).
No financial statements or institutional flow data.

**2. Full memo with data gap noted — investment-memo-writer**

Use `investment-memo-writer` with your Taiwan ticker. The skill will note the FinMind
gap in Phase 1 and proceed with available yfinance data. The investing-team worker
handles the Taiwan-Specific Diagnosis gate and documents what data is missing.

**3. CasualMarket MCP for live Taiwan quotes**

CasualMarket is an optional external MCP server that provides live TWSE/OTC quotes,
外資動向, and valuation multiples. It is NOT bundled with investing-toolkit.

Install separately:
```bash
claude plugin add casualmarket
```

See `../../scripts/README.md` for setup notes and the CasualMarket GitHub link.

**4. Manual data with domain-teams:investing-team directly**

If you have Taiwan data from another source (export from broker, XQ, CMoney), invoke
`domain-teams:investing-team` with the **Taiwan-Specific Diagnosis** workflow and
supply your data manually as seed context. The workflow runs without this skill.
