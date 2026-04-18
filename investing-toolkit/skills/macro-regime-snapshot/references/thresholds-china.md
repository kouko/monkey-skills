# China / 中国 — Macro Regime Thresholds & Calibration

**Authority**: 中国人民银行 (PBOC) + 国家统计局 (NBS) + 国务院 (State Council) |
**Currency**: CNY | **Calibration vintage**: 2026-Q1

---

## Inflation Target / 通货膨胀目标

- **Official target**: **3% CPI YoY** — set annually by 国务院
  (State Council) in 政府工作报告 Government Work Report
- **Framework**: unlike Fed/BOJ/BOK single-mandate, PBOC is a
  **multi-objective** central bank — 3% CPI is one of several goals
  alongside growth, employment, FX stability, systemic risk.
- **Tolerance band**: no published band; 3% is commonly interpreted
  as an **upper ceiling** rather than a target-center.
- **Current outlook** (2026 forecast):
  - Full-year CPI center expected **≤ 1.5%** (assuming oil $85-100/bbl
    baseline) — deeply below 3% ceiling
  - **Disinflation / deflation risk** is the active 2026 concern,
    not inflation overshoot
  - PBOC 2026-Q1 examples set "适度宽松的货币政策" (moderately loose)
    posture
- **Signal** (using 3% ceiling + disinflation-concern framing):
  - `> 2.5%` Approaching target ceiling (caution)
  - `1.0% ≤ x ≤ 2.5%` Normal range
  - `0% ≤ x < 1.0%` Disinflation watch
  - `< 0%` Deflation regime (Japan-like risk)

### Important framing caveat

China's CPI structure differs fundamentally from G7: food + pork
(猪肉周期) has outsized weight and drives headline gyrations. **Core
CPI (核心CPI, food + energy excluded) is a better demand-pull signal**.
Current (2026-Q1) core CPI trending well below headline, implying
weak domestic demand despite any food-price bounces.

---

## Labor Market Tightness

- **Official target**: **城镇调查失业率 (urban surveyed unemployment
  rate) around 5.5%** (2025 actual: 5.2%; 2026 target ~5.5%)
- **No published NAIRU**: NBS acknowledges "自然失业率 = 摩擦性 +
  结构性 失业" conceptually, but does not publish point estimates.
- **Structural features**:
  - Youth unemployment (16-24 excluding students) was ~14-15% in 2024
    after methodology revision (dropped from 21% pre-revision)
  - Rural-urban migrant worker statistics separately tracked
  - Migrant worker conditions often signal real labor stress before
    official series
- **Bands (using 5.5% government target as anchor)**:
  - `urban surveyed unemp < 5.0%` → Tight (outperforming target)
  - `5.0% ≤ x ≤ 5.5%` → Balanced (on target)
  - `5.5% < x < 6.0%` → Slack (exceeding target)
  - `> 6.0%` → Stressed (major slowdown signal)
- **Caveat**: Chinese urban surveyed unemployment is notoriously
  **understated** relative to underemployment; use direction of
  change + migrant worker anecdotes as cross-checks.

---

## Policy Rate Neutrality

- **Multi-rate system** (PBOC uses several policy rates, not single
  Fed funds analogue):
  - **LPR 1Y**: ~3.1% (2026-Q1, primary lending benchmark)
  - **LPR 5Y**: ~3.6% (mortgage reference)
  - **MLF 1Y**: ~2.5% (PBOC liquidity tool)
  - **RRR**: ~9.5% for large banks (reserve requirement; another
    transmission channel)
  - **7-day reverse repo**: ~1.5% (short-term rate anchor)
- **Nominal neutral rate estimate**: no official r*. Academic
  estimates + IMF models: **nominal ~3.0-3.5%**, implying
  **real r\* ~0.5-1.5%** (higher than US because of EM premium +
  structurally higher growth trend, albeit moderating).
- **Policy stance framework**: PBOC's "适度宽松" (moderately loose) /
  "稳健" (prudent) / "稳健略偏宽松" qualitative language — not numeric
  r* framing. Requires qualitative reading of PBOC 货币政策委员会 statements.

---

## Real Rate Decomposition

**Not available** for v1.9.0 or foreseeable future.

**Why**: China has **no developed inflation-linked government bond
market**. Attempts at issuing linkers have been sporadic; no clean
daily breakeven series.

**Alternative**: **nominal real rate proxy** = LPR 1Y − CPI YoY (rough
estimate of real financing cost). Can be computed manually but lacks
TIPS-market's forward-looking inflation-expectation content.
Current: ~3.1% − 0.5% ≈ **+2.6% ex-post real** — structurally very
tight given disinflation regime.

**Structural view**: China is experiencing **"balance-sheet deflation"
risk** (property sector deleveraging) — high ex-post real rates
despite PBOC's nominal easing is itself a red-flag regime signal.

---

## Structural Regime Notes

- **State-directed economy**: PBOC is NOT fully independent; monetary
  policy coordinates with 国务院 + 财政部. Credit allocation to
  specific sectors (property, SOEs, tech) is policy-driven.
- **Capital account partially closed**: CNY is a **managed-float**,
  not free-float. PBOC fixes daily reference + ± 2% band (in practice
  narrower). Offshore CNH diverges in stress.
- **Property sector overhang** (2021-ongoing):
  - Residential property ~25-30% of GDP (directly + indirectly)
  - 2021-2024 developer defaults + 保交楼 (ensure delivery) crisis
  - Still unwinding in 2026 — background constraint on all regime calls
- **Demographic cliff**: population peaked 2021-2022; working-age
  population declining faster than Japan's 1990s path. Structurally
  lowers growth trend.
- **Policy cycles ≠ market cycles**: NPC (全国人大) March meeting +
  Politburo July/December meetings often drive regime shifts more
  directly than data. Watch "三中全会" (Third Plenum) + CEWC (中央经济
  工作会议) for regime announcements.

---

## Monthly GDP Proxy — Component-Only (v1.7.1 Decision)

Per v1.7.1 research: **no market-consensus composite monthly GDP proxy
for China**. Why not:
- 李克强指数 (Li Keqiang Index: electricity + rail freight + bank loans)
  — obsolete post-2012 as economy shifted to services
- SF Fed CAT (China Activity Tracker) — quarterly, standard-deviation
  units, not level
- Goldman / Bloomberg proprietary composites — closed
- Academic DFM (dynamic factor models) — each paper uses different
  variables, no converged consensus

**Decision**: use **`industrial-yoy` (工业增加值YoY) as primary Growth
proxy** + overlay 3-component panel (`retail-yoy`, `fai-yoy`,
`services-production-yoy`). Flag **component divergence** when > 2%
(e.g. industrial rising but retail falling = external-demand-driven
cycle, different implications than all-four rising).

---

## Asset-Class Tilt Calibration

- **Equity indices** (pick one based on use case):
  - **CSI300**: large-cap, broad — weighted toward financials, SOEs,
    consumer staples. Most tracked by foreign investors (via MSCI EM).
  - **ChiNext / STAR Market (科创板)**: tech-growth; closer to
    NASDAQ analogue.
  - **Hang Seng Index** (HK-listed): includes H-shares of mainland
    names + offshore-listed tech (Tencent, Alibaba); better proxy
    for global-investor-accessible China exposure.
  - **HSCEI (国企指数)**: H-shares pure-play on mainland SOEs.
- **Property sector**: post-2021 crisis, property-linked names should
  be treated with **structural discount** regardless of regime
  — until deleveraging cycle confirms bottom.
- **Fixed income**: CGB (Chinese government bond) 10Y yield ~1.7%
  (2026-Q1, near all-time low) — reflects deflation + policy easing
  expectations. Structurally lower than US 10Y by 250+ bp.
- **FX**: USD/CNY + USD/CNH spread monitoring; CFETS RMB basket as
  PBOC's preferred FX benchmark.

### Sector Tilts (CN-specific adjustments to IC cheatsheet)

| IC Phase | CN-specific Overweight | CN-specific Underweight |
|----------|------------------------|--------------------------|
| Recovery | Consumer discretionary, tech (internet), exporters | State-owned banks, property |
| Overheat | Commodities, upstream materials, energy SOEs | Consumer staples |
| Stagflation | Utilities (regulated SOEs), gold-miners, bonds | Property, consumer discretionary |
| Reflation | CGB, REITs (if policy supports), utilities | Property, cyclicals |

**Cycle framework caveat**: CN rarely spends much time in Phase 1 or
Phase 2 (fits "property-deleveraging + policy-easing-but-not-fast-enough"
→ Phase 3 / Phase 4 regime more often than cyclical recovery). IC
framework can **undershoot capture** of the structural
property-deleveraging regime.

---

## Primary-Source Verification URLs

- 中国人民银行 PBOC: http://www.pbc.gov.cn/
- PBOC 货币政策委员会例会 (quarterly): http://www.pbc.gov.cn/goutongjiaoliu/
- 国家统计局 NBS: https://www.stats.gov.cn/
- NBS 调查失业率: https://data.stats.gov.cn/
- 中共中央经济工作会议 (CEWC) statements via 新华社: https://www.news.cn/

## Sources (citations)

- 中国人民银行货币政策委员会 2026年第一季度例会
- 新华网 2026-01-06 — 中国人民银行2026年将继续实施好适度宽松的货币政策
- 第一财经 2024 — 中国该如何制订今年物价目标 (3% framework discussion)
- 国家统计局 2026-01-19 — 2025年就业形势保持总体稳定 (urban surveyed unemployment 5.2%)
- 国家统计局 — 什么是调查失业率 (concept explainer)
- 中国银行研究院 2026 《经济金融展望报告》
- 中国银河宏观 2026-Q1 货币政策委员会例会解读
