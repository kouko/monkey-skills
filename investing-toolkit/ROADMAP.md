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

## v1.1.0 — Taiwan Layer

**Scope**: Taiwan equity data via FinMind. taiwan-stock-snapshot skill.

### New
- [ ] scripts/finmind_client.py (FINMIND_API_TOKEN env, anonymous fallback)
- [ ] skills/taiwan-stock-snapshot/SKILL.md
- [ ] /invest-screen {ticker} with --universe tw50 support
- [ ] CasualMarket MCP installation guide
- [ ] taiwan-local-rigor gate auto-trigger in investment-memo-writer for .TW tickers

---

## v1.2.0 — Screener + Technical Layer

**Scope**: Multi-ticker screening, technical indicators.

### New
- [ ] skills/stock-screener/SKILL.md (criteria-based US screener)
- [ ] skills/technical-snapshot/SKILL.md (RSI, MACD, Bollinger, ATR via yfinance)
- [ ] /invest-screen {criteria} — US universe
- [ ] /invest-portfolio {holdings.csv} — full portfolio review pipeline

---

## v2.0.0 — Quantitative Layer (tentative)

**Scope**: Backtesting integration, factor models.

### Ideas
- [ ] Backtesting workflow (integrates with domain-teams:investing-team standards/backtesting-and-robustness-discipline.md)
- [ ] Factor exposure snapshot (Fama-French 5-factor)
- [ ] Alpha Vantage premium adapter (technical indicators)
- [ ] Portfolio optimizer (risk parity / Kelly allocation)
