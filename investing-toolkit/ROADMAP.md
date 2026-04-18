# investing-toolkit Roadmap

## v1.0.0 — US + Macro Layer (current)

**Scope**: US stocks via yfinance + FRED macro data. Core invest* slash commands.

### Skills
- [x] using-investing-toolkit (router)
- [x] macro-regime-snapshot (IC + yield-curve + FRED)
- [x] us-stock-snapshot (yfinance + SEC EDGAR)
- [x] investment-memo-writer (→ domain-teams:investing-team)
- [x] dcf-valuation (3-stage DCF + sensitivity)

### Commands
- [x] /invest (router)
- [x] /invest-macro (regime call)
- [x] /invest-memo (full memo pipeline)

### Data adapters
- [x] scripts/yfinance_client.py
- [x] scripts/fred_client.py
- [x] agents/data-fetcher.md

---

## v1.1.0 — Taiwan Layer (current)

**Scope**: Taiwan equity data via FinMind. taiwan-stock-snapshot skill.

### New
- [x] scripts/finmind_client.py (FINMIND_API_TOKEN env, anonymous fallback)
- [x] skills/taiwan-stock-snapshot/SKILL.md
- [x] CasualMarket MCP installation guide (in scripts/README.md + taiwan-stock-snapshot)
- [x] investment-memo-writer Phase 1: FinMind commands for .TW/.TWO tickers
- [ ] /invest-screen {ticker} with --universe tw50 support (moved to v1.2.0)

---

## v1.2.0 — Screener + Technical Layer

**Scope**: Technical indicators, batch screener, portfolio review.

### New
- [x] scripts/ta_client.py (RSI/MACD/Bollinger/ATR/SMA from OHLCV, no external API)
- [x] scripts/yfinance_client.py --tickers batch mode
- [x] skills/technical-snapshot/SKILL.md (RSI, MACD, Bollinger, ATR, SMA)
- [x] skills/stock-screener/SKILL.md (valuation + momentum + trend composite score)
- [x] skills/invest-portfolio/SKILL.md (P&L snapshot + regime overlay + investing-team delegation)
- [x] /invest-screen {tickers} [--pe-max] [--above-sma200] [--rsi-min/max]
- [x] /invest-portfolio [holdings.csv | inline-list]

---

## v1.3.0 — Country Macro Skills (current)

**Scope**: Country-specific macro data skills with bilingual indicator references.

### New
- [x] scripts/boj_client.py (BOJ Time-Series API, no auth)
- [x] scripts/estat_client.py (統計ダッシュボード API, no auth)
- [x] skills/us-macro/SKILL.md (FRED 8 indicators + reference doc)
- [x] skills/japan-macro/SKILL.md (BOJ + 統計DB 13 indicators + bilingual reference)
- [x] macro-regime-snapshot: region=japan support
- [x] japan-boj-db-catalog.md (40+ DB bilingual catalog)

---

## v1.4.0 — Taiwan Macro

**Scope**: Taiwan macro indicators from 4 government sources.

### New
- [x] scripts/statgov_client.py (stat.gov.tw hidden chart JSON, 17 presets)
- [x] scripts/cbc_client.py (CBC Open Data API, 5 presets)
- [x] scripts/dgbas_client.py (DGBAS Excel .xls, 6 presets)
- [x] scripts/ndc_client.py (NDC ZIP/CSV, 6 presets)
- [x] skills/taiwan-macro/SKILL.md (30 indicators, 8 groups, trilingual references)

---

## v1.5.0 — Korea Macro

**Scope**: Korea macro indicators via FinanceDataReader (BOK ECOS-KEYSTAT).

### New
- [x] scripts/fdr_client.py (FinanceDataReader ECOS-KEYSTAT, 27 presets + 1 FRED)
- [x] skills/korea-macro/SKILL.md (28 indicators, 10 groups, trilingual references)
- [x] Unified indicator reference format across US/JP/TW/KR (93 indicators)
- [x] Cache migration to $CLAUDE_PLUGIN_DATA convention (10 scripts)

---

## v1.6.0 — China Macro

**Scope**: China macro indicators via akshare (NBS + PBOC + SHIBOR),
FRED fallbacks (CNY/USD, FX reserves), and yfinance market indices.

### New
- [x] scripts/akshare_client.py (19 presets: inflation/growth/trade/labor/sentiment/rates/money/credit — 2 Caixin PMI presets removed 2026-04-18, mirror ran 8mo stale)
- [x] skills/china-macro/SKILL.md (26 indicators total: 19 akshare + 2 FRED + 5 yfinance, trilingual references)
- [x] NBS WAF workaround — akshare mirrors (eastmoney, investing.com, chinamoney, shibor.org) remain reachable when `data.stats.gov.cn` blocks foreign IPs
- [x] 10 reference files including 119 indicator sections across US/JP/TW/KR/CN (unified format)
- [x] NBS new-SPA API reverse-engineered (`docs/nbs-indicator-catalog.md`): 2908-leaf indicator tree captured for future `nbs_client.py` work

---

## v1.7.0 — Monthly GDP Proxies for US + JP (current)

**Scope**: Cross-market symmetric monthly GDP tracking. US and Japan gain
the monthly-GDP-proxy indicator packages that china-macro already provides
via 三大數據 + services-production.

**Background**: No major economy publishes official monthly GDP (UK and
Canada are exceptions). For US, the Fed family of nowcasts (GDPNow, CFNAI,
WEI) plus OECD CLI are the industry-standard proxies. For Japan, the
内閣府 景気動向指数 CI trio (先行/一致/遅行) is the canonical proxy, with
一致指数 treated as the definitive "current GDP feel".

### New
- [x] us-macro: +4 presets under new `nowcast` group — `GDPNOW` (Atlanta Fed), `CFNAI` (Chicago Fed), `WEI` (NY Fed), `USALOLITOAASTSAM` (OECD CLI, replacing discontinued USSLIND). 21 → 25 series.
- [x] japan-macro: +2 presets `leading-index` + `lagging-index` completing the 景気動向指数 CI trio. 14 → 16 active indicators.
- [x] references/indicators-growth.md expanded in both skills with full monthly-GDP-proxy documentation.

---

## v2.0.0 — Quantitative Layer (tentative)

**Scope**: Backtesting integration, factor models.

### Ideas
- [ ] Backtesting workflow (integrates with domain-teams:investing-team standards/backtesting-and-robustness-discipline.md)
- [ ] Factor exposure snapshot (Fama-French 5-factor)
- [ ] Alpha Vantage premium adapter (technical indicators)
- [ ] Portfolio optimizer (risk parity / Kelly allocation)
