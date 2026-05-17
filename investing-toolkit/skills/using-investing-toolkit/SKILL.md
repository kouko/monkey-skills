---
name: using-investing-toolkit
description: Router skill for investing-toolkit v2.0.0. You are the entry point — route the user to the right Layer 1/2/3 skill or slash command based on their investing intent.
---

# using-investing-toolkit

You are the entry point for **investing-toolkit v2.0.0** (three-layer architecture: Data → Analysis → Report). Route the user to the right skill or slash command. Do not perform analysis yourself; dispatch to the appropriate skill.

> **v2.0.0 architecture** (per ADR-0001): Data layer = pure I/O (`data-{country}`); Analysis layer = pure compute (`analysis-{topic}`); Report layer = orchestration + format (`report-{name}`). Cross-skill calls via main agent + temp file. See `docs/adr/0001-data-analysis-report-layers.md`.

---

## Available Skills (16)

### Layer 1 — Data (5 skills, country-bundled, pure I/O)

| Skill | Coverage | Pack types |
|---|---|---|
| `data-us` | yfinance + SEC EDGAR + FRED (US market + macro) | snapshot, memo-fetch, comps-multiples, screener-batch, regime-pack |
| `data-jp` | yfinance + EDINET + TDnet + BOJ + e-Stat + ECB (JP market + macro; EDINET-key tier-routed) | snapshot, memo-fetch, comps-multiples, screener-batch, regime-pack |
| `data-tw` | yfinance + MOPS + TWSE/TPEx OpenAPI + FinMind + CBC + DGBAS + NDC + statgov (TW market + macro) | snapshot, memo-fetch, comps-multiples, screener-batch, regime-pack |
| `data-kr` | yfinance + FinanceDataReader (BOK ECOS-KEYSTAT 54 indicators; DART deferred) | snapshot, memo-fetch, comps-multiples, screener-batch, regime-pack |
| `data-cn` | yfinance + NBS new-SPA + akshare (PBOC/Caixin) + FRED USDCNY | snapshot, memo-fetch, comps-multiples, screener-batch, regime-pack |

### Layer 2 — Analysis (6 skills, pure compute)

| Skill | Compute | Input → Output |
|---|---|---|
| `analysis-dcf` | 3-stage DCF + 3×3 sensitivity (WACC × terminal-g) + verdict thresholds | memo-fetch JSON → intrinsic value JSON |
| `analysis-screener` | 8 presets (value / deep-value / quality / high-dividend / growth / growth-value / momentum / balanced) — filter + composite score + ranking | screener-batch JSON → ranked top-N JSON |
| `analysis-technical` | RSI-14 / MACD-12-26-9 / Bollinger-20 / ATR-14 / SMA-20-50-200 + signal enums (canonical home of `ta_client.py`) | OHLCV JSON → indicators JSON |
| `analysis-portfolio` | Position P&L (fractional `pnl_ratio`) + concentration + top3_weight; JP/KR suffix auto-resolve | holdings + prices JSON → P&L matrix JSON |
| `analysis-macro-regime` | 5-country IC + GIP regime classification + US real-rate decomposition (4-tier) + cross-country consensus | per-country regime-pack JSONs → regime card JSON |

### Layer 3 — Report (4 skills, orchestrator + format)

| Skill | Pipeline | Final output |
|---|---|---|
| `report-equity-memo` | data-{country} memo-fetch + regime-pack → analysis-dcf + analysis-macro-regime → delegate `domain-teams:investing-team` (gates) → optional `domain-teams:docs-team` | Full equity memo (Markdown) |
| `report-stock-snapshot` | Country auto-detect → data-{country} snapshot → snapshot_format.py | Single-page snapshot card (Markdown) |
| `report-portfolio-review` | Parse holdings → group by country → parallel data-{country} screener-batch → analysis-portfolio + optional analysis-macro-regime overlay → review_format.py | Portfolio review (Markdown) |
| `report-screener-list` | Parse ticker list → group by country → parallel data-{country} screener-batch → concat → analysis-screener → screener_format.py | Top-N ranked table (Markdown) |

### Router (1)

| Skill | Role |
|---|---|
| `using-investing-toolkit` | This skill — entry point + intent routing |

---

## Available Commands

| Command | Routes to | Description |
|---|---|---|
| `/using-investing-toolkit` | this router | Describe your goal; we dispatch |
| `/report-equity-memo` | `report-equity-memo` | Full investment memo pipeline |
| `/report-screener-list` | `report-screener-list` | Cross-country stock screener with 8 presets |
| `/report-portfolio-review` | `report-portfolio-review` | Holdings P&L review + optional regime overlay |
| `/report-stock-snapshot` | `report-stock-snapshot` | Single-ticker quick snapshot card |
| `/analysis-macro-regime` | `data-{country}` regime-pack + `analysis-macro-regime` | 5-country macro regime |

---

## Intent Routing

### Standalone data fetch (Layer 1)

| User intent | Route to |
|---|---|
| "US macro data / FRED indicators / US rates" | `data-us --pack regime-pack` |
| "Japan macro / BOJ / JGB yield / 日本のマクロ" | `data-jp --pack regime-pack` |
| "Taiwan macro / CBC / TAIEX / 景氣燈號 / 台灣總經" | `data-tw --pack regime-pack` |
| "Korea macro / BOK / 한국 매크로 / 기준금리" | `data-kr --pack regime-pack` |
| "China macro / NBS / PBOC / CSI300 / 中國總經 / LPR / 社融" | `data-cn --pack regime-pack` |
| "Raw US stock data" | `data-us --ticker X --pack snapshot` |
| "Raw TW stock data with 三大法人 / 月營收" | `data-tw --ticker X --pack memo-fetch` |
| "Raw JP stock data with EDINET filings" | `data-jp --ticker X --pack memo-fetch` (requires EDINET_API_KEY for Tier A; falls back to yfinance Tier 2) |

### Pure compute (Layer 2 — typically chained from Report layer or Layer 1 output)

| User intent | Route to |
|---|---|
| "Compute DCF on this fetched data" | `analysis-dcf --input <data-pack-json>` |
| "Apply screener preset to ticker list" | `analysis-screener --input <data-pack-json> --preset value` |
| "Compute RSI / MACD on OHLCV" | `analysis-technical --input <ohlcv-json>` |
| "Classify macro regime from per-country indicators" | `analysis-macro-regime --input us=...,jp=...,...` |
| "Portfolio P&L from holdings + prices" | `analysis-portfolio --holdings ... --prices ...` |

### Final reports (Layer 3 — most common user-facing entry)

| User intent | Route to |
|---|---|
| "Quick snapshot on AAPL / 2330.TW / 7203" | `report-stock-snapshot` |
| "Write a full investment memo on NVDA" | `report-equity-memo` |
| "DCF valuation for MSFT" | `report-equity-memo` (memo subsumes DCF) — or directly `analysis-dcf` if just the model |
| "Screen stocks by value preset / rank AAPL,MSFT,NVDA / mixed-country list" | `report-screener-list` |
| "Review my portfolio / rebalance" | `report-portfolio-review` |
| "Where are we in the cycle / 5-country macro regime?" | `data-{country}` regime-pack + `analysis-macro-regime` (or use `report-equity-memo` Phase 2 if memo is the goal) |

### Country detection by ticker suffix

`report-*` skills auto-route based on ticker suffix:

| Suffix | Market | Data skill |
|---|---|---|
| `.TW` / `.TWO` | Taiwan (TWSE / TPEx) | `data-tw` |
| `.T` / `.TO` / 4-digit numeric (`7203`) | Japan | `data-jp` |
| `.KS` / `.KQ` | Korea (KOSPI / KOSDAQ) | `data-kr` |
| `.SS` / `.SZ` / `.HK` | China / Hong Kong | `data-cn` |
| else (alphabetic, e.g. `AAPL`) | US | `data-us` |

---

## Cross-market Monthly GDP Proxy Framework

All five `data-{country}` skills expose **monthly GDP proxy** indicators labelled consistently across markets:

| Market | Proxy type | Indicators |
|---|---|---|
| US | Pre-aggregated Fed nowcasts | `nowcast` group: `GDPNOW`, `CFNAI`, `WEI`, `USALOLITOAASTSAM` (OECD CLI) |
| JP | Pre-aggregated 内閣府 composite | 景気動向指数 CI trio: `coincident-index` (monthly GDP proxy), `leading-index`, `lagging-index` |
| TW | Pre-aggregated NDC + DGBAS | `signal` (五色景氣燈號 — Taiwan 特色), `leading-index`, `coincident-index` |
| KR | Pre-aggregated BOK ECOS | `cycle` group: `coincident-cycle` K253 (proxy), `leading-cycle` K254 (lagging not in KEYSTAT) |
| CN | Raw components (no authoritative composite) | 三大数据: `industrial-yoy`, `retail-yoy`, `fai-yoy` + `services-production-yoy` companion |

US/JP/TW/KR serve **pre-aggregated** values from the respective statistical authorities. CN keeps components raw because there is no market consensus on synthesis. Composite synthesis belongs in the analysis layer (`domain-teams:investing-team`) where methodology choice has analytical accountability.

For the **industry-level indicator** counterpart, see [`docs/industry-indicator-cadence.md`](../../docs/industry-indicator-cadence.md).

---

## Cross-Plugin Bridge

`report-equity-memo` (Layer 3) is the canonical bridge to `domain-teams:investing-team`:

1. Uses Layer 1 `data-{country}` to assemble raw memo inputs (memo-fetch + regime-pack)
2. Uses Layer 2 `analysis-dcf` + `analysis-macro-regime` for compute
3. Delegates to **`domain-teams:investing-team`** for full Deep Equity Research Memo protocol + 2 MUST + 4 SHOULD + 1 MAY gates
4. Optionally chains `domain-teams:docs-team` for polished Markdown formatting

If the user only needs the analysis framework — not data fetching — invoke `domain-teams:investing-team` directly.

---

## When NOT to Use investing-toolkit

investing-toolkit is a **data + analysis + report layer** for systematic investment workflows. It does NOT make investment verdicts on its own.

For actual investment analysis, verdicts, gates, and research frameworks, go directly to:
- `domain-teams:investing-team` — full analysis with IC/GIP framework, quality gates, memo standards (typically chained via `report-equity-memo`)
