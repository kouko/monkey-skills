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

## v1.2.0 — Screener + Technical Layer (current)

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

## v2.0.0 — Quantitative Layer (tentative)

**Scope**: Backtesting integration, factor models.

### Ideas
- [ ] Backtesting workflow (integrates with domain-teams:investing-team standards/backtesting-and-robustness-discipline.md)
- [ ] Factor exposure snapshot (Fama-French 5-factor)
- [ ] Alpha Vantage premium adapter (technical indicators)
- [ ] Portfolio optimizer (risk parity / Kelly allocation)
