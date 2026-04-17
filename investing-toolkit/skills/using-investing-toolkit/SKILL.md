---
name: using-investing-toolkit
description: Router skill for investing-toolkit. You are the entry point — route the user to the right skill or slash command based on their investing intent.
---

# using-investing-toolkit

You are the entry point for investing-toolkit. Route the user to the right skill or slash command. Do not perform analysis yourself; dispatch to the appropriate skill.

---

## Available Skills

| Skill | Description | Status |
|-------|-------------|--------|
| `macro-regime-snapshot` | IC + FRED regime call — diagnose current macro phase | v1.0.0 |
| `us-stock-snapshot` | yfinance price + info snapshot for a US ticker | v1.0.0 |
| `investment-memo-writer` | Full memo pipeline — delegates to domain-teams:investing-team | v1.0.0 |
| `dcf-valuation` | 3-stage DCF model + sensitivity table | v1.0.0 |
| `taiwan-stock-snapshot` | Taiwan equity data via FinMind (三大法人, 月營收, 融資融券, 董監持股) | v1.1.0 |
| `stock-screener` | Batch screener — valuation + momentum + trend composite score | v1.2.0 |
| `technical-snapshot` | RSI, MACD, Bollinger Bands, ATR, SMA via ta_client.py | v1.2.0 |
| `invest-portfolio` | Portfolio review — P&L snapshot + regime overlay + rebalance | v1.2.0 |
| `us-macro` | US macro indicators via FRED (8 series + reference doc) | v1.3.0 |
| `japan-macro` | Japan macro indicators via BOJ + e-Stat (13 series + bilingual reference) | v1.3.0 |

---

## Available Commands

| Command | Description | Status |
|---------|-------------|--------|
| `/invest` | Router — describe your goal and be dispatched | v1.0.0 |
| `/invest-macro` | Fetch FRED data and call the macro regime | v1.0.0 |
| `/invest-memo` | Full investment memo pipeline | v1.0.0 |
| `/invest-screen` | Screen tickers by valuation/momentum/trend criteria | v1.2.0 |
| `/invest-portfolio` | Full portfolio review from holdings CSV or inline list | v1.2.0 |

---

## Intent Routing

| User intent | Route to |
|-------------|----------|
| "US macro data / FRED indicators / US rates" | `us-macro` |
| "Japan macro data / BOJ / JGB yield / 日本のマクロ" | `japan-macro` |
| "What is the macro regime / where are we in the cycle?" | `macro-regime-snapshot` |
| "Give me a quick snapshot on AAPL / stock info" | `us-stock-snapshot` |
| "Write a full investment memo on NVDA" | `investment-memo-writer` |
| "DCF valuation for MSFT" | `dcf-valuation` |
| "Taiwan stock data / 三大法人 / 月營收 / 融資融券 / 董監持股" | `taiwan-stock-snapshot` |
| "Screen stocks by criteria / rank AAPL,MSFT,NVDA" | `stock-screener` |
| "Technical indicators / RSI / MACD for TSLA" | `technical-snapshot` |
| "Review my portfolio / rebalance" | `invest-portfolio` |

All v1.2.0 skills are now available.

---

## Cross-Plugin Note

`investment-memo-writer` is a bridge skill. It:
1. Uses investing-toolkit data agents (yfinance, FRED) to assemble raw inputs
2. Delegates to **domain-teams:investing-team** for analysis, quality gates, and final memo

If the user only needs the analysis framework — not data fetching — invoke `domain-teams:investing-team` directly.

---

## When NOT to Use investing-toolkit

investing-toolkit is a **data and workflow layer**. It fetches, formats, and pipelines data.

For actual investment analysis, verdicts, and research frameworks, go directly to:
- `domain-teams:investing-team` — full analysis with IC/GIP framework, quality gates, memo standards
