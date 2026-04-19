---
name: using-investing-toolkit
description: Router skill for investing-toolkit. You are the entry point — route the user to the right skill or slash command based on their investing intent.
---

# using-investing-toolkit

You are the entry point for investing-toolkit. Route the user to the right skill or slash command. Do not perform analysis yourself; dispatch to the appropriate skill.

---

## Available Skills

Skills are organised in three layers:

- **data** — fetch raw time-series from external sources, no analysis
- **aggregation** — combine / score / transform data from the data layer into a single-purpose output (regime call, composite score, valuation model, P&L)
- **delegation** — bridge to `domain-teams:investing-team` for full research framework with quality gates

| Skill | Layer | Description | Status |
|-------|-------|-------------|--------|
| `us-macro` | data | US macro indicators via FRED (~31 series incl. `pmi` group [OECD CLI proxy for ISM] + `swap-spreads` group new in v1.10.0) | v1.10.0 |
| `japan-macro` | data | Japan macro indicators via BOJ + e-Stat + ECB + MoF auction history (27 presets / 10 groups incl. `real-rates` group new in v1.10.0; C+D+E multi-source framework) | v1.10.0 |
| `taiwan-macro` | data | Taiwan macro indicators via stat.gov.tw + CBC + DGBAS + NDC (32 indicators incl. new `pmi` group — CIER PMI/NMI via NDC 政府資料開放 dataset 6100) | v1.11.0 |
| `korea-macro` | data | Korea macro indicators via FinanceDataReader BOK ECOS-KEYSTAT (54 indicators, 13 groups incl. monthly `industry` activity layer; full KEYSTAT catalogue in `docs/`) | v1.8.1 |
| `china-macro` | data | China macro indicators via NBS new-SPA API + PBOC (akshare) + FRED + yfinance (36 indicators incl. new `pmi` group — Caixin mfg/svc via akshare + NBS mfg/non-mfg/composite via nbs_client) | v1.11.0 |
| `us-stock-snapshot` | data | yfinance price + info snapshot for a US ticker | v1.0.0 |
| `taiwan-stock-snapshot` | data | Taiwan equity data via FinMind (三大法人, 月營收, 融資融券, 董監持股) | v1.1.0 |
| `technical-snapshot` | data | RSI, MACD, Bollinger Bands, ATR, SMA via ta_client.py | v1.2.0 |
| `macro-regime-snapshot` | aggregation | 5-country IC + GIP (US/JP/TW/KR/CN) + Rate Stress Dashboard + v1.11.0 cross-country consistency refresh (Block 1 PMI live 1/5 → 3/5 +CN +TW; 5×9 coverage grid; CN+JP full 2026-Q2 grounding refresh) | v1.11.0 |
| `stock-screener` | aggregation | Batch screener — valuation + momentum + trend composite score | v1.2.0 |
| `dcf-valuation` | aggregation | 3-stage DCF model + sensitivity table | v1.0.0 |
| `invest-portfolio` | aggregation | Portfolio review — P&L snapshot + regime overlay + rebalance | v1.2.0 |
| `investment-memo-writer` | delegation | Full memo pipeline — delegates to domain-teams:investing-team | v1.0.0 |

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
| "Taiwan macro data / CBC / TAIEX / 台灣總經 / 景氣燈號" | `taiwan-macro` |
| "Korea macro data / BOK / KOSPI / 한국 매크로 / 기준금리" | `korea-macro` |
| "China macro data / NBS / PBOC / CSI300 / 中国宏观 / 中國總經 / LPR / 社融" | `china-macro` |
| "What is the macro regime / where are we in the cycle?" | `macro-regime-snapshot` |
| "Give me a quick snapshot on AAPL / stock info" | `us-stock-snapshot` |
| "Write a full investment memo on NVDA" | `investment-memo-writer` |
| "DCF valuation for MSFT" | `dcf-valuation` |
| "Taiwan stock data / 三大法人 / 月營收 / 融資融券 / 董監持股" | `taiwan-stock-snapshot` |
| "Screen stocks by criteria / rank AAPL,MSFT,NVDA" | `stock-screener` |
| "Technical indicators / RSI / MACD for TSLA" | `technical-snapshot` |
| "Review my portfolio / rebalance" | `invest-portfolio` |

All skills through v1.11.0 are now available.

---

## Cross-market Monthly GDP Proxy Framework

As of v1.7.3, all five country-macro skills expose **monthly GDP proxy**
indicators labelled consistently across skills:

| Market | Proxy type | Indicators |
|--------|-----------|------------|
| US | Pre-aggregated Fed nowcasts | `nowcast` group: `GDPNOW`, `CFNAI`, `WEI`, `USALOLITOAASTSAM` (OECD CLI) |
| JP | Pre-aggregated 内閣府 composite | 景気動向指数 CI trio: `coincident-index` (monthly GDP proxy), `leading-index`, `lagging-index` |
| TW | Pre-aggregated NDC + DGBAS | `signal` (五色景氣燈號 — Taiwan 特色), `leading-index`, `coincident-index` |
| KR | Pre-aggregated BOK ECOS | `cycle` group: `coincident-cycle` K253 (the proxy), `leading-cycle` K254 (lagging not in KEYSTAT) |
| CN | Raw components (no authoritative composite) | 三大数据: `industrial-yoy`, `retail-yoy`, `fai-yoy` + `services-production-yoy` companion |

US / JP / TW / KR all serve **pre-aggregated** values from the respective
statistical authorities (Fed / 内閣府 / NDC+DGBAS / BOK ECOS). CN keeps
components raw because there is no market consensus on synthesis
(Li Keqiang Index is obsolete post-2012, SF Fed CAT is quarterly +
standard-deviation units, Goldman / Bloomberg are proprietary).
Composite synthesis belongs in the analysis layer
(`domain-teams:investing-team`) where methodology choice has analytical
accountability. See each skill's `references/indicators-*.md` preamble
for full discussion.

For the **industry-level indicator** counterpart (sector coverage + release
cadence comparison across the 5 markets), see
[`docs/industry-indicator-cadence.md`](../../docs/industry-indicator-cadence.md).

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
