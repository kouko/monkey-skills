# China / 中国 — Macro Regime Thresholds & Calibration

**Authority**: 中国人民银行 (PBOC) + 国家统计局 (NBS) + 国务院 (State Council) |
**Currency**: CNY | **Calibration vintage**: 2026-Q2

## Grounding Status (as of 2026-04-19)

**Last full verification**: 2026-04-19 via `../research/grounding-v1.11.0.md`
(cross-country v1.11.0 refresh; CN section). Prior full grounding:
2026-04-18 v1.9.0 (preserved below for historical record).

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

### v1.11.0 full refresh (2026-04-19)

Full re-audit since v1.9.0 (2026-04-18) vintage. **Scope**: 2026-Q1 / 2026-Q2
data that became available after v1.9.0 capture (2025 全年公报、2026 两会
政府工作报告、2026-Q1 PBOC 货币政策委员会例会、2026-03 月度 CPI/PPI、
2026-Q1 GDP 初步核算).

**Structural frame unchanged**: "适度宽松" 货币政策延续、7D 逆回购 = 主政
策利率、CPI 目标 2%、MLF 数量工具、BIS r\* Rees-Sun 2021 2-3% real 估计
仍是 benchmark — 全部无需修订。

🔴 **GDP 目标首次用区间 + 首次低于 5%**：2026 两会《政府工作报告》定
2026 GDP 增长 **4.5-5% 区间** (2024/2025 均为「5% 左右」)。区间值为
2026 首次采用，低于 5% 也是改革开放以来首次。既为「十五五」开局留空
间，亦与 2035 远景目标 (年均 4.17%) 衔接。Source:
https://www.news.cn/politics/20260305/e5c6a09cba0f445b9ee6cc6f8973132a/c.html

🔴 **赤字率 2026 提高至 4% 左右** (2025 为 3% 左右 → 2026 约 4%；规模
5.89 万亿元)。配套专项债 4.4 万亿、超长期特别国债 1.3 万亿、新型政策
性金融工具 8000 亿。Source:
https://www.yicai.com/news/103074560.html

🔴 **2025 全年 GDP = 5.0%** (目标实现)。季度路径: Q1 5.4% → Q2 5.2%
→ Q3 4.8% → Q4 4.5% (明显减速)。Source:
https://www.stats.gov.cn/sj/zxfb/202601/t20260120_1962349.html

🔴 **2026-Q1 GDP = 5.0% YoY** (1-3 月良好开局)。一季度工业增加值
+6.1%、零售 +2.4%、固投 +1.7%、房地产投资 **-11.2%**、住宅投资 **-11.0%**、
新房销售面积 **-10.4%**、销售额 **-16.7%**。房地产仍是单边拖累。Source:
https://www.stats.gov.cn/sj/zxfb/202604/t20260416_1963330.html

🔴 **2026-03 CPI = 1.0% YoY、核心 CPI = 1.1% YoY**，1-3月累计 CPI =
0.9%。核心仍高于总体 (v1.9.0 captured 反转 pattern 延续)。食品 +0.3%
(猪肉 -11.5% 拖累 ~0.22pp)，非食品 +1.2%。Source:
https://www.stats.gov.cn/sj/zxfb/202604/t20260410_1963264.html

🔴 **2026-03 PPI 同比转正 +0.5%**，结束连续 **41 个月下降**，环比 +1.0%
连 6 个月上涨（48 个月最大）。**通缩 tail risk 边际降温的首个硬证据**。
Source: https://www.stats.gov.cn/sj/zxfbhjd/202604/t20260410_1963265.html

🔴 **2026-Q1 城镇调查失业率 = 5.3% 平均 (3月 5.4%)**，31个大城市 5.3%。
2025 全年 5.2% → 2026 Q1 5.3% 小幅上行，但仍低于 5.5% 目标。Source:
https://finance.sina.com.cn/jjxw/2026-04-16/doc-inhuskuh7260825.shtml

⚠️ **RRR 维持 9.0% 未动** — market expected Q1 2026 50bp 降准未落地。
2026-04 中旬 PBOC 副行长邹澜确认法定存款准备金率平均 **6.3%**、加权
6.2%，"5% 隐形下限可能调整或取消"。央行 Q1 缩量续作买断式逆回购、
继续依赖 MLF + 国债买卖净投放 2.05 万亿，**替代降准**。降准/降息可能
延至 Q2/Q3。Source:
https://www.jiemian.com/article/14251219.html

⚠️ **结构性降息 0.25pp (2025-12)** — PBOC 对部分结构性工具利率定向
下调 0.25 pp (支农支小再贷款、碳减排工具、科技创新再贷款等)。**这是
v1.9.0 未捕获但 2025-12 已落地的政策动作**，与 7D OMO 1.40% 保持不动
并行。Source:
https://stcn.com/article/detail/3595664.html

⚠️ **远期售汇外汇风险准备金率 2026-03-02 起降为 0** (从 20%)。**非
RRR，是 FX macroprudential 工具**，意在便利企业远期购汇、减轻人民币
贬值压力的结构性信号。Source:
https://www.chnfund.com/article/AR5f68505b-1eb7-cc1d-8331-3a1fafe738d9

⚠️ **PBOC 2026-Q1 例会语言** (3/26，总第 112 次) 延续「适度宽松」，新
增「加大逆周期和跨周期调节力度」+「使社会融资规模、货币供应量增长
同经济增长、价格总水平预期目标相匹配」。v1.9.0 的「推动价格总水平
由负转正」在 2026-03 PPI 转正后可视为**阶段性兑现**。Source:
https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/2026033115531475919/index.html

⚠️ **CSI 300 2025-12 调样生效** — 信息技术行业样本数量 **+4**、通信
服务 **+2**；权重分别上升 **+1.46%** / **+0.75%**。2026-Q1 结构继续向
新经济倾斜，但 v1.9.0 captured 的 2025 末权重 (金融 22.97%、信息
技术 20.38%) 仍是 best-available 静态快照 — 2026-Q1 完整 factsheet
(季度发布) 在 2026-04 末-05 初更新后再 recalibrate。Source:
https://www.stcn.com/article/detail/1433088.html

**Verified unchanged (14 facts reconfirmed)**:
- PBOC 2024-07 7D OMO 框架 (= 主政策利率 1.40%)
- LPR 1Y 3.0% / LPR 5Y 3.5% (2025-05 下调后连续 11 个月持平；
  2026-04-20 仍持平)
- RRR 大银行 9.0% (未变；加权 6.2%、均值 6.3%)
- MLF 角色 (数量工具，不再为政策利率锚)
- CPI 目标 2% (2026 两会延续)
- 城镇调查失业率目标 5.5%
- 「适度宽松」货币政策基调 (CEWC 2025-12 + PBOC Q1 2026 例会)
- BIS WP No 949 (Rees & Sun 2021) r\* real 2-3% 估计
- CSI300 已转为「四分天下」(金融/消费/新能源/AI)
- 核心 CPI 高于总体 (2026-Q1 延续)
- 房地产投资深度负增长 (Q1 -11.2%)
- 青年失业率 16-18% 区间 (2025 全年 band)
- 20-year CPI 目标轨迹表
- Equity index / property / bond / FX 资产类别 calibration

**New primary-source URLs**:
- 国家统计局 2026-04-16 — 2026 年一季度国民经济实现良好开局:
  https://www.stats.gov.cn/sj/zxfb/202604/t20260416_1963330.html
- 国家统计局 2026-04-17 — 一季度 GDP 初步核算结果:
  https://www.stats.gov.cn/sj/zxfb/202604/t20260417_1963336.html
- 国家统计局 2026-04-10 — 2026 年 3 月 CPI / PPI:
  https://www.stats.gov.cn/sj/zxfb/202604/t20260410_1963264.html
- 国家统计局 2026-04-10 — CPI/PPI 解读 (董莉娟):
  https://www.stats.gov.cn/sj/zxfbhjd/202604/t20260410_1963265.html
- 国家统计局 2026-01-20 — 2025 Q4 + 全年 GDP 初步核算:
  https://www.stats.gov.cn/sj/zxfb/202601/t20260120_1962349.html
- 2026 政府工作报告解读 (新华社 / 第一财经):
  https://www.news.cn/politics/20260305/e5c6a09cba0f445b9ee6cc6f8973132a/c.html
  https://www.yicai.com/news/103074560.html
- PBOC 货币政策委员会 2026 Q1 例会 (3/26):
  https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/2026033115531475919/index.html
- 中央经济工作会议 2025-12-10/11 (新华社):
  https://www.cac.gov.cn/2025-12/11/c_1767178314595543.htm
- 新华社 2026-01-07 — 央行定调 2026 货币政策:
  https://www.news.cn/fortune/20260107/2d78951afc9545b1a3e029687f0b4f31/c.html
- 全国银行间同业拆借中心 2026-04-20 LPR 报价:
  https://cj.sina.com.cn/articles/view/7857141524/1d452771401901t65m

See `../research/grounding-v1.11.0.md` (to be written in follow-up commit)
for consolidated cross-country audit.

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
  - 2026-Q1 实际 (1-3 月累计): **总体 CPI 0.9% / 核心 CPI 1.1-1.3%**
    (食品猪肉 -11.5% 拖累总体, 核心反高于总体)
  - **2026-03 单月**: 总体 CPI **1.0%** YoY、核心 **1.1%** YoY (环比
    -0.7%，春节后回落)
  - **PPI 2026-03 转正 +0.5% YoY** — 结束连续 **41 个月下降**,
    环比 +1.0% 连 6 个月上涨 (48 个月最大)。**通缩 tail risk
    边际降温首个硬证据**
  - PBOC 2026-Q1 例会 (3/26): 「继续实施适度宽松的货币政策」,
    强调「推动价格总水平由负转正」(PPI 转正阶段性兑现)
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
Current (2026-Q1) core CPI **slightly above** headline (核心 1.1% vs
总体 0.9-1.0%) — reversal from 2023-2024 pattern where core < headline.
Reason: 猪肉 -11.5% + 食品 weak 拖累 headline below weak-but-
rebounding core demand. 2026-03 PPI 转正 +0.5% 为 disinflation regime
内首个 supply-side ease，but core CPI 仍远低于 2% 目标 = 需求端
pressure 未释放。

---

## Labor Market Tightness

- **Official target**: **城镇调查失业率 (urban surveyed unemployment
  rate) around 5.5%** (2025 actual 全年: 5.2%; **2026-Q1 平均 5.3%,
  2026-03 单月 5.4%**; 2026 目标 ~5.5%; 城镇新增就业目标 1200 万以上)
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
  - **7 天逆回购**: **1.40%** (2026-04，PBOC 政策利率锚；2025-09 下调
    后连续 **7+ 个月未动**；2026-04-02 固定利率操作仍 1.40% 确认)
  - **LPR 1Y**: **3.0%** (2026-04-20 公告，LPR 自 2025-05 下调后连续
    **11 个月持平**)
  - **LPR 5Y**: **3.5%** (同上，房贷参考)
  - **MLF 1Y**: 约 2.0% (**数量工具，2024 后不再为政策利率**)
  - **RRR**: 大型银行 **9.0%** (2025-11 末调整后未动；2026-Q1 降准
    预期未落地；加权 RRR 6.2% / 平均 6.3%)
  - **结构性政策工具利率** (2025-12): 支农支小再贷款、碳减排工具、
    科技创新再贷款等定向 **下调 0.25pp** — 属"结构性降息"而非全面
    降息；未改 7D OMO / LPR
  - **FX 宏观审慎**: 远期售汇外汇风险准备金率 2026-03-02 起由 20%
    **降为 0** (便利企业远期购汇；非 RRR)
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
Current (2026-03): LPR 1Y **3.0%** − CPI YoY **1.0%** ≈ **+2.0% ex-post
real** (2026-Q1 累计: 3.0% − 0.9% ≈ +2.1%)
— 相对于 BIS r\* 估计 2-3% real, 处于 **中性偏紧** (非 "structurally very
tight"); 但相对于「物价回升诉求」的政策意图仍显不足。**PPI 2026-03 转
正 +0.5% 之后，real financing cost 对企业端 marginal ease** (LPR 1Y
3.0% − PPI 0.5% ≈ 2.5% real vs 2025 年末 LPR 3.0% − PPI ≈ −0.9% 得出
约 3.9% real)。

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
- PBOC 货币政策执行报告: http://www.pbc.gov.cn/zhengcehuobisi/125207/125227/
- PBOC 2026 Q1 例会 (3/26): https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/2026033115531475919/index.html
- 国家统计局 NBS: https://www.stats.gov.cn/
- NBS 数据发布: https://www.stats.gov.cn/sj/zxfb/
- NBS 调查失业率: https://data.stats.gov.cn/
- 中共中央经济工作会议 (CEWC) statements via 新华社: https://www.news.cn/
- 2026 政府工作报告: https://www.news.cn/politics/20260305/e5c6a09cba0f445b9ee6cc6f8973132a/c.html

## Sources (citations)

- 中国人民银行货币政策委员会 2026年第一季度例会 (2026-03-26)
- 新华网 2026-01-06 / 2026-01-07 — 中国人民银行2026年将继续实施好适度宽松的货币政策
- 新华社 2025-12-11 — 中央经济工作会议在北京举行 (CEWC 部署 2026)
- 国家统计局 2026-01-19 — 2025年国民经济运行情况 (全年 GDP 5.0%)
- 国家统计局 2026-01-20 — 2025 年四季度和全年 GDP 初步核算结果
- 国家统计局 2026-01-19 — 2025年就业形势保持总体稳定 (urban surveyed unemployment 5.2%)
- 国家统计局 2026-04-10 — 2026 年 3 月 CPI/PPI 数据 + 董莉娟解读
- 国家统计局 2026-04-16 — 2026 年一季度国民经济实现良好开局 (GDP 5.0%, 失业率 5.3%)
- 国家统计局 2026-04-17 — 2026 年一季度 GDP 初步核算结果
- 2026 政府工作报告 (李强, 2026-03-05) — GDP 4.5-5%, CPI 2%, 赤字率 4%
- 第一财经 2024 — 中国该如何制订今年物价目标 (3% framework discussion)
- 第一财经 2026-03-05 — 政府工作报告解读: GDP 增速设定区间目标
- 中国银行研究院 2026 《经济金融展望报告》
- 中国银河宏观 2026-Q1 货币政策委员会例会解读
- 新华社 2025-12-18 — 解码中央经济工作会议: 货币政策延续「适度宽松」
