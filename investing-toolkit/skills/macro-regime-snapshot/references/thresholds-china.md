# China / 中国 — Macro Regime Thresholds & Calibration

**Authority**: 中国人民银行 (PBOC) + 国家统计局 (NBS) + 国务院 (State Council) |
**Currency**: CNY | **Calibration vintage**: 2026-Q1

## Grounding Status (as of 2026-04-18)

**Last full verification**: 2026-04-18 via `../research/grounding-v1.9.0.md`
(5-country parallel grounding note; CN section).

**Verified (✅)**: PBOC 2026-Q1 例会「适度宽松」语言、2025 城镇调查失业率
5.2%、2026 目标 5.5%、房地产 23.6% GDP (直接) / 31% (含基建)。

**Corrected (🔴 in prior draft → fixed below — 大幅改动)**:

1. **🔴 最重要 — CPI 目标 = 2%** (不是 3%)。**2025、2026 政府工作报告
   连续两年**设为「2% 左右」。**2004 年以来首次下调**，从「防过热
   ceiling」转为「促回升 中枢」。整份 "3% ceiling" 假设作废。

2. **🔴 所有利率数字偏高 1 档**：
   - LPR 1Y: 3.0% (prior: 3.1%)
   - LPR 5Y: 3.5% (prior: 3.6%)
   - RRR 大银行: 9.0% (prior: 9.5%, 2025-11 末调整)
   - 7 天逆回购: **1.40%** (prior: 1.5%; 2025-09 下调后未动)

3. **🔴 MLF 不再是政策利率** — PBOC 2024-07 已明确 **7 天逆回购为主要
   政策利率**, MLF 转为数量工具 (利率约 2.0%)。Prior draft 的
   "MLF 1Y 2.5% 政策锚" 框架过时。

4. **🔴 "中国无 r\* 估计" 是错的** — **BIS WP No 949 (Rees & Sun 2021)**
   Bayesian 估计 2019 末 r\* **real 2-3%** (95% CI 1.5-3%)。GFC 后持续
   下行，潜在增速下降贡献 2/3。nominal ≈ r\* + 2% CPI ≈ **3.5-5%**
   (prior draft "0.5-1.5% real" 低估了约 1.5 pp)。

5. **🔴 CSI300 "金融+SOE 主导" 已过时**：
   - 2016: 金融 35.45% / IT 9.22%
   - 2025: 金融 **22.97%** / IT **20.38%**
   - 已转为金融/消费/新能源/AI 四分天下
   - 2026-04 前 10 大: 宁德时代 4.55%、中际旭创 3.66%、茅台 3.41%

6. **🔴 核心 CPI 2026-Q1 反转** — 核心 **高于** 总体 (不是低于):
   - 总体 CPI 0.9% (1-3 月均) vs 核心 CPI 1.1-1.3%
   - 食品 (猪肉 -11.5%) 拖累总体
   - Prior draft "核心低于总体" 在 2023-2024 成立，**2026-Q1 已反转**。

**Partial (⚠️)**: 2026 CPI 预期 ≤1.5% 方向正确但偏保守；中银证券
0.1-0.8% M 型、中银研究院「企稳回升」。

**New discoveries**:
- **PBOC "适度宽松" 是 2010 以来首次回归** — 与 1998-1999、2008-2009
  两段历史同列。语言阶梯: 稳健 → 稳健略偏宽松 → 稳健偏松 → 适度宽松 → 宽松。
- **青年失业率方法论断裂**: 2023-08 暂停 → 2024-01 换「不含在校生」口径。
  2018-2023 vs 2024-2026 不可直接比较。
- **Sun Guofeng (PBOC 前货币政策司长) 2023 因案被判刑**, PBOC 内部 r\*
  研究能见度下降。

**Next recalibration**: March 2027 (全国人大政府工作报告 + PBOC Q1 例会).
鉴于 2025 重大变化 (CPI 3→2%, 7D OMO 取代 MLF)，可能需要更频繁的
partial recalibration。

---

---

## Inflation Target / 通货膨胀目标

- **Official target**: **2% CPI YoY 左右** — 2025、2026 连续两年由国务院
  在《政府工作报告》中设定。**这是 2004 年以来首次低于 3%**（2015-2024
  常态为「3% 左右」，2008 / 2011 / 2012 曾 4%，2020 为 3.5%）
- **Framework**: unlike Fed/BOJ/BOK single-mandate, PBOC 是 **多目标**
  央行 (物价 + 增长 + 就业 + 汇率 + 金融稳定)。2% CPI 只是其中一项。
- **Tolerance band**: no published band; 2% 近年更像**软 ceiling**，且
  被解读为「推动物价温和回升」的目标值 (而非最大值) — 当前 disinflation
  regime 中 **2% 是 aspiration**, 不是 constraint。
- **Current outlook** (2026 forecast):
  - 中银证券: 2026 全年 CPI **0.1-0.8% M 型走势**
  - 中银研究院: 温和回升态势
  - 2026-Q1 实际 (1-3 月均): **总体 CPI 0.9% / 核心 CPI 1.1-1.3%**
    (食品猪肉 -11.5% 拖累总体, 核心反高于总体)
  - PBOC 2026-Q1 例会 (3/26): 「继续实施适度宽松的货币政策」,
    强调「推动价格总水平由负转正」
- **Signal** (使用 2% 软 ceiling + 物价回升诉求 双框架):
  - `> 2.5%` 明显超过目标 (罕见, 2024 后未见)
  - `1.5% ≤ x ≤ 2.5%` 接近目标中枢 (**2026 央行所期望的正常区间**)
  - `0.5% ≤ x < 1.5%` 偏低 (**当前 2026-Q1 实际区**)
  - `0% ≤ x < 0.5%` 明确通缩风险
  - `< 0%` 通缩确认

### 20 年 CPI 目标軌跡 (grounding-v1.9.0.md CN §20-year trajectory)

| 期间 | CPI 目标 | 政策语言 | 背景 |
|------|----------|----------|------|
| 2005-2007 | 3% 左右 | 稳健偏松 | 高速增长 |
| 2008 | **4.8%** | **适度宽松** (GFC) | 四万亿刺激 |
| 2009 | 4% | 适度宽松 | - |
| 2010 | 3% | 稳健 | - |
| 2011-2012 | **4%** | 稳健 | 通胀压力 |
| 2013-2019 | 3-3.5% | 稳健 | 长期稳定 |
| 2020 | 3.5% | 稳健略偏宽松 | COVID |
| 2021-2024 | 3% | 稳健 | 实际均值 0.8%, 目标成虚设 |
| **2025** | **2% (首次下调)** | **适度宽松** (GFC 以来首次) | 通缩 + 房市危机 |
| **2026** | 2% (维持) | 适度宽松 (维持) | 新增「推动由负转正」|

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

- **Multi-rate system** — PBOC 2024-07 已明确 **7 天逆回购为主要政策利率**
  (取代 MLF):
  - **7 天逆回购**: **1.40%** (2026-Q1, PBOC 政策利率锚; 2025-09 下调后未动)
  - **LPR 1Y**: **3.0%** (2026-Q1, 贷款报价基准)
  - **LPR 5Y**: **3.5%** (房贷参考)
  - **MLF 1Y**: 约 2.0% (**数量工具，2024 后不再为政策利率**)
  - **RRR**: 大型银行 **9.0%** (2025-11 末调整)
- **Real neutral rate r\***: **BIS WP No 949 (Rees & Sun 2021)**
  Bayesian 估计 1995Q2-2019Q4: 2019 末 r\* **real 2-3%** (95% CI 1.5-3%).
  自 GFC 以来持续下行，潜在增速下降贡献 2/3. 2020 后房地产危机 + 通缩
  可能进一步下压。**Nominal ≈ r\* + 2% CPI 目标 ≈ 3.5-5%**.
- **Policy stance** (2026-Q1): PBOC 2026-Q1 例会 (3/26) 明确
  "继续实施**适度宽松**的货币政策", **2010 以来首次回到「适度宽松」**
  (与 1998-1999、2008-2009 同列)。PBOC 语言阶梯:
  稳健 → 稳健略偏宽松 → 稳健偏松 → **适度宽松** → 宽松。

---

## Real Rate Decomposition

**Not available** for v1.9.0 or foreseeable future.

**Why**: China has **no developed inflation-linked government bond
market**. Attempts at issuing linkers have been sporadic; no clean
daily breakeven series.

**Alternative**: **nominal real rate proxy** = LPR 1Y − CPI YoY (rough
estimate of real financing cost). Can be computed manually but lacks
TIPS-market's forward-looking inflation-expectation content.
Current (2026-Q1): LPR 1Y **3.0%** − CPI YoY 0.9% ≈ **+2.1% ex-post real**
— 相对于 BIS r\* 估计 2-3% real, 处于 **中性偏紧** (非 "structurally very
tight"); 但相对于「物价回升诉求」的政策意图仍显不足。

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
  - **CSI300**: large-cap 宽基。**2026-Q1 行业结构 (vs 2016 大幅演变)**:
    金融 **~23%** (2016: 35.45%), 信息技术 **~20%** (2016: 9.22%),
    消费 (含食品饮料) ~15%, 新能源/工业 ~12%。**已转为四分天下**
    (金融 / 消费 / 新能源 / AI), 不再是「银行+SOE 主导」。
    前 10 大 (2026-04): 宁德时代 4.55%、中际旭创 3.66% (AI 光模块)、
    贵州茅台 3.41%、中国平安 2.54%、紫金矿业 2.22%。
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
