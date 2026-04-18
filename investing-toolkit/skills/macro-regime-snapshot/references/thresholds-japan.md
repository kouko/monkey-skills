# Japan / 日本 — Macro Regime Thresholds & Calibration

**Authority**: 日本銀行 (Bank of Japan, BOJ) | **Currency**: JPY |
**Calibration vintage**: 2026-Q1

---

## Inflation Target / 物価安定の目標

- **Official target**: **2% CPI YoY** (headline 全国CPI, set 2013-01)
- **Tolerance band**: **none published** — BOJ uses qualitative
  "概ね整合的な水準" ("roughly consistent level") rather than a
  numerical band. Academic proposals (Canada-style 1-3%) exist but
  not adopted.
- **Current reading**: Core CPI (除生鮮食品) 2026 見通し中央値 1.9%
  (2025-10 展望レポート)
- **FY outlook (BOJ 展望 2025-10)**:
  - FY2024: 2.5%
  - FY2025: 1.9%
  - FY2026: 1.9%
  - Late in projection horizon: "物価安定の目標と概ね整合的な水準"
- **Signal (using BOJ 2% anchor)**:
  - `> 2.2%` Above target
  - `1.8% ≤ x ≤ 2.2%` At target (this IS BOJ's goal state)
  - `< 1.8%` Below target (historically Japan's default regime)

### Important framing caveat

Japan's **decades-long deflation legacy** means the 2% target is a
**policy goal** rather than an ambient equilibrium. A reading of 1.9%
should be treated as **success** (not "below target"), not as
disinflationary concern — context matters. The regime call for Japan
should give more weight to **direction of change** (rate-of-change) than
level-vs-target gap.

---

## Labor Market Tightness (NAIRU / 均衡失業率)

- **NAIRU estimate**: **~3.5-3.6%** ("3% 台半ば" per JILPT 均衡失業率
  analysis and 第一生命経済研究所 macro research)
- **Current unemployment** (労働力調査 2026-01/02): **2.6-2.7%**
- **Implication**: unemployment is **~1 pp below NAIRU** → structurally
  **Tight** labor market. This has been the default Japan regime
  post-2015.
- **Bands (NAIRU ± 0.4 pp, tighter than US because JP NAIRU is lower)**:
  - `unemp < 3.2%` → Tight (current regime)
  - `3.2% ≤ unemp ≤ 4.0%` → Balanced
  - `unemp > 4.0%` → Slack
- **Wage-inflation signal**: since 2024 春闘 wage rounds, Japan
  transitioning from "tight-but-no-wage-gain" to genuine wage growth —
  watch spring round results as a second labor-tightness dimension.

---

## Policy Rate Neutrality

- **Current BOJ policy rate**: **~0.5%** (post-YCC end, 2024-03 onwards;
  additional hikes 2024-07, 2025 normalization path)
- **Nominal neutral rate estimate**: ~**1.0%** (market consensus /
  NRI, 三井住友DS AM). BOJ themselves do not publish a neutral rate.
- **Real r\* (BOJ Working Paper 24-J-09, 2024)**:
  - Range estimates: **-1.0% to +0.5%**
  - Mean: **-0.25%** (slightly negative!)
  - Much lower than US r* due to demographic decline + low trend growth
- **Nominal hiking path (野村 2026 メインシナリオ)**:
  - 2026 policy rate trajectory: 2 hikes to ~1.0% by late-2026
  - 2027 H1: ~1.25%

---

## Real Rate Decomposition

**Not available** in free data layer for v1.9.0.

**Why**: Japan has JGBi (物価連動国債, inflation-linked bonds) but:
1. BOJ/e-Stat API does not expose clean daily breakeven/TIPS-equivalent
   series in ECOS-like form
2. Would require MoF XLS scraper (月次 発行実績 + 流通市場データ)
3. Market structure differs — JGBi less liquid, BOJ still holds
   substantial inventory

**Current 10Y JP real yield** (approximate, cross-source): **-0.386%**
as of 2026-Q1 (G7's only negative 10Y real yield).

**Deferred to v1.10.0+**: MoF JGBi scraper + thresholds calibrated to
JP r* estimate (probably `< -0.5%` Accommodative / `-0.5% to 0.5%`
Neutral / `> 0.5%` Restrictive — roughly HLW-JP ± 50 bp).

---

## Structural Regime Notes

- **Post-deflation transition** (since 2022-2024): Japan is leaving
  the "2% is aspirational" regime into "2% is achieved". This shifts
  the IC mapping:
  - Pre-2022: Japan was almost always **Phase 4 Reflation** (falling
    growth + falling inflation below target)
  - 2024-2026: first sustained **Phase 2 Overheat** (rising both) in
    decades; regime identification should acknowledge this rare shift.
- **BOJ YCC ended 2024-03**: pre-2024 JGB 10Y curve was artificially
  pinned; post-2024 readings more market-driven.
- **Demographic overhang**: aging population + shrinking workforce
  → structurally low r*, low trend growth (~0.5% real). This
  **caps sustainable policy rate ceiling**.
- **JPY regime**: Japan is a creditor nation with massive FX reserves
  + overseas assets (~3x GDP). JPY appreciation in risk-off is a
  regime-cross-check signal.

---

## Asset-Class Tilt Calibration

- **Equity index**: TOPIX (broad, ~2,100 names) preferred for regime
  mapping over Nikkei 225 (price-weighted, 225 names). Sector
  structure more balanced than KOSPI/TAIEX. Tech weight ~15-20%
  (vs TW ~65%).
- **Corporate governance reform**: post-2023 TSE reform driving P/B
  rerating — **structural re-rating can dominate regime signal** for
  JP equities.
- **Fixed income**: JGB curve post-YCC → finally market-priced;
  10Y yield ~1.5% (2026-Q1). Real yield negative → JGB expensive in
  real terms but defensive.
- **Commodities**: Japan is major commodity importer — commodity
  strength = terms-of-trade drag. Energy (crude) especially critical
  (not self-sufficient).
- **FX**: JPY weakness drives imported inflation directly (Japan CPI
  reacts ~0.4% per 10% JPY depreciation). JPY direction often a
  regime factor, not just a consequence.

### Sector Tilts (JP-specific adjustments to IC cheatsheet)

| IC Phase | JP-specific Overweight | JP-specific Underweight |
|----------|------------------------|--------------------------|
| Recovery | Financials (banks benefit from positive rates), automakers, tech-value | Utilities, defensive staples |
| Overheat | Trading houses (商社), commodity-linked, shippers | Import-heavy consumer, JGB |
| Stagflation | JPY cash, energy, healthcare | Real estate, consumer discretionary |
| Reflation | JGB, REITs (J-REIT), telecoms | Automakers, export-oriented |

---

## Primary-Source Verification URLs

- 日銀 物価安定の目標: https://www.boj.or.jp/mopo/outline/target.htm
- 日銀 経済・物価情勢の展望: https://www.boj.or.jp/mopo/outlook/
- 日銀 WP 自然利子率 WP24-J-09: https://www.boj.or.jp/research/wps_rev/wps_2024/wp24j09.htm
- JILPT 均衡失業率・需要不足失業率: https://www.jil.go.jp/kokunai/statistics/topics/uv/uv.html
- 労働力調査 (e-Stat): https://www.e-stat.go.jp/stat-search/files?tclass=000001226526

## Sources (citations)

- BOJ 物価安定の目標 (2013-01 policy statement)
- BOJ 経済・物価情勢の展望 2025-10 (展望レポート)
- BOJ Working Paper WP24-J-09 (2024) — 自然利子率の計測をめぐる近年の動向
- 日経 参議院 Research Note 2024-12 — 物価安定の目標をめぐる経緯と論点
- 伊藤忠総研 2024 コラム — 自然利子率r*に振り回される日米金融市場
- NRI 木内登英 2025-12-16 — 政府のデフレ完全克服と日銀の2％物価安定
- 野村証券 (森田京平) 2026 メインシナリオ — 日銀追加利上げ予想
- JST 資金運用本部 Research Note 42 (2026-01-29) — 中立金利とタームプレミアム
