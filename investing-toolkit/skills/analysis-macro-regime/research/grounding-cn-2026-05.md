# China Macro Regime — Grounding Delta Refresh 2026-05-02

**Type**: Partial recalibration per [recalibration-protocol.md](../references/recalibration-protocol.md) — short delta from prior vintage; full audits covered separately.

**Prior full grounding**: 2026-04-18 (v1.9.0 capture).
**Prior partial refresh**: 2026-04-19 (v1.11.0 cross-country addendum, embedded at top of [thresholds-china.md](../references/thresholds-china.md)).
**This refresh**: 2026-05-02 (PR-6 of v2.1.0 Phase 1 per ADR-0004).

---

## Status

**No material policy events between 2026-04-19 and 2026-05-02.**
The 13-day window did NOT trigger any of the mandatory recalibration
events listed in `recalibration-protocol.md`:

- ❌ No new PBOC quarterly 货币政策委员会 例会 (next: late June 2026)
- ❌ No new NBS monthly CPI/PPI release (next: 2026-05-09 ~ 2026-05-12)
- ❌ No LPR change (continued at 3.0% / 3.5% per 2026-04-20 fixing)
- ❌ No 7D 逆回购 rate change (continued at 1.40% per 2026-04-28
  operation)
- ❌ No RRR adjustment (continued at 9.0% large-bank)
- ❌ No CEWC / 三中全会 announcement
- ❌ No new BIS r* vintage

**Conclusion**: `thresholds-china.md` 2026-Q2 vintage remains current.
Calibrations carried over verbatim into `calibrations/cn.yaml`.

---

## Calibration carry-over (verbatim from thresholds-china.md)

| Field                                       | Value                            | Source vintage            |
|---------------------------------------------|----------------------------------|---------------------------|
| `inflation_target`                          | 2.0                              | 2025/2026 政府工作报告    |
| `inflation_target_type`                     | central_tendency                 | 2025 起 (从 ceiling 改)   |
| `policy_rate.primary.rate` (7D RR)          | 1.40                             | 2025-09-→2026-04          |
| `policy_rate.quantitative_tools.lpr_1y`     | 3.0                              | 2025-05-→2026-04-20       |
| `policy_rate.quantitative_tools.lpr_5y`     | 3.5                              | 2025-05-→2026-04-20       |
| `policy_rate.quantitative_tools.rrr_large`  | 9.0                              | 2025-11 末调整            |
| `policy_rate_neutrality.bis_real_estimate`  | 2.5 (band 1.5-3.0)               | BIS WP 949 (Rees-Sun 2021)|
| `current_stance`                            | 适度宽松                         | PBOC 2026-Q1 例会         |
| `gdp.target_2026`                           | [4.5, 5.0]                       | 2026 政府工作报告         |
| `growth_components.dispersion_alarm_pp`     | 2.0                              | v1.7.1 research           |
| `property_overlay.gdp_share_direct`         | 0.236                            | thresholds-china.md       |
| `property_overlay.gdp_share_incl_infra`     | 0.31                             | thresholds-china.md       |

---

## Native-language verification (2026-05-02)

Conducted in **简体中文** per CLAUDE.md global instructions.

### 1. PBOC 7天逆回购 政策利率 — VERIFIED 1.40%

> 央行今日开展1462亿元7天逆回购操作，操作利率为1.40%
> — 每日经济新闻 2026-03-27

> 央行今日开展43.5亿元7天逆回购操作，操作利率为1.40%
> — 新浪财经 2026-04-28

Source URLs:
- https://www.nbd.com.cn/articles/2026-03-27/4311288.html
- https://finance.sina.com.cn/wm/2026-04-28/doc-inhwaicu8454678.shtml

**Status**: 1.40% confirmed in active OMO operations through 2026-04-28.
Calibration `policy_rate.primary.rate = 1.40` is current.

### 2. CPI 目标 2% — VERIFIED (2026 政府工作报告)

> 2026年政府工作报告提出，居民消费价格(CPI)涨幅预期目标是2%左右，
> 与去年目标一致。
> — 新华网 2026-03-05 + 知乎专栏综合

> 与2025年相比，2026年进一步明确「将通过改善总供求关系，推动价格
> 总水平由负转正、消费价格合理温和回升」
> — 新华网 2026-03-05

Source URLs:
- https://www.news.cn/politics/20260305/e5c6a09cba0f445b9ee6cc6f8973132a/c.html
- https://wallstreetcn.com/articles/3742381

**Status**: 2% target confirmed; central-tendency framing reinforced
by «推动价格总水平由负转正、消费价格合理温和回升».
Calibration `inflation_target = 2.0` and
`inflation_target_type = central_tendency` are both current.

### 3. 社融存量 同比 — VERIFIED 8.3% (2025-12 end)

> 截至2025年末，中国社会融资规模存量同比增速达到8.3%，比2024年末
> (8.0%) 上升 0.3 个百分点。2025 年全年社融增量 35.6 万亿元，同比
> 多增 3.34 万亿元。
> — 综合 PBOC 2026-01 金融统计数据报告 + 证券时报

Source URLs:
- http://www.pbc.gov.cn/diaochatongjisi/116219/116319/index.html
- https://www.stcn.com/article/detail/3538292.html

**Status**: 信贷脉冲 (TSF stock yoy 12m change) at 2025-12 ≈ +0.3pp
→ tagged **expanding** but only marginally above noise band (0.5pp).
Direction-of-travel is positive, magnitude is modest. **Calibration
threshold `primary_pp_threshold: 0.5` flags this as "neutral" until
2026-Q1 prints push the magnitude wider.**

### 4. LPR + RRR — VERIFIED unchanged

> 2026年4月20日 LPR 报价：1年期3.0%，5年期以上3.5%，连续8个月不变
> — 新华网 2026-04-21

> RRR 大型银行 9.0% (2025-11 末以来未变); PBOC 副行长邹澜指出今年
> 仍有降准降息空间, 预计 50bp 降准 + 10bp LPR
> — 中国基金报 / 东方财富 2025-12-23 银行业 2026 展望

Source URLs:
- https://www.news.cn/money/20260421/7af4278f0f6949219b12e974bf3ea635/c.html
- https://www.chnfund.com/article/ARb6ab0691-444d-f801-bf3c-3a1eeb36986a

**Status**: All three rates confirmed unchanged. Calibration current.

### 5. 房地产 GDP 占比 — PARTIAL (methodology divergence noted)

> 2024年，中国房地产业增加值占GDP的比重为6.3%，比2023年下降0.5
> 个百分点。
> — 国家统计局 / 南方都市报 2025-01

> 2020年房地产及其产业链占中国GDP的17%（完全贡献），其中房地产业
> 增加值占GDP的7.3%（直接贡献），房地产带动产业链占GDP的9.9%
> （间接贡献）
> — 知乎引用 / 用益信托网

Source URLs:
- https://www.stats.gov.cn/sj/zxfb/202604/t20260416_1963327.html
- https://m.mp.oeeee.com/oe/BAAFRD0000202501171045558.html
- https://www.yanglee.com/Information/Details.aspx?i=117838

**Status**: thresholds-china.md uses **23.6% / 31%** which are
broader-chain estimates (含上下游 + 含基建). NBS official narrow
definition (业增加值/GDP) is **6.3%** for 2024 (down from 6.8%/2023).

**Action**: cn.yaml now carries all three perspectives:
- `gdp_share_direct = 0.236` (broad chain, thresholds-china.md value)
- `gdp_share_incl_infra = 0.31` (含基建)
- `gdp_share_nbs_narrow = 0.063` (NBS official 2024)

This avoids over-claiming 23.6% while preserving the regime-relevant
broader-chain figure that captures property's full economic footprint.
**Recommend follow-up**: thresholds-china.md may want a clarifying
note about the methodology divergence.

### 6. 信用脉冲 (Credit Impulse) Methodology — VERIFIED CICC + 中信

> 「信贷脉冲」由德银经济学家 Michael Biggs 提出，定义为新增广义信贷
> 占 GDP 比值的变化。「信贷脉冲」是信贷存量的「二阶变化」，「社融
> 存量同比」是「一阶变化」。
> — 中金大类资产 2022-01-17

> 信贷脉冲拐点领先社融存量拐点 6-9 个月左右
> — 国信证券策略 2023-05-15

Source URLs:
- https://finance.sina.com.cn/stock/stockzmt/2022-01-17/doc-ikyamrmz5618477.shtml
- https://pdf.dfcfw.com/pdf/H3_AP202305151586638635_1.pdf

**Status**: methodology choice in `references/credit-impulse-methodology.md`
(this PR) grounded directly. **Choice**: TSF stock yoy 12-month change
(middle of three flavors); rationale: monthly GDP unavailable for strict
Biggs version, stock-yoy-only is too lagging. Documented thoroughly.

---

## Anchored Quotes (verified currency)

> "继续实施**适度宽松**的货币政策，加大逆周期和跨周期调节力度,
> 使社会融资规模、货币供应量增长同经济增长、价格总水平预期目标相匹配"
> — PBOC 货币政策委员会 2026 年第一季度例会 (2026-03-26)

> "通过改善总供求关系, 推动价格总水平由负转正、消费价格合理温和回升"
> — 2026 年政府工作报告 (李强, 2026-03-05)

These are the qualitative anchors used in `classify_cn.py`'s
`pboc_stance` and `cpi_framing.policy_stance` fields.

---

## Phase 1 PR-6 Implementation Notes

- `calibrations/cn.yaml` extracts `thresholds-china.md` numeric values as
  YAML keys for machine-readable consumption by `classify_cn.py`.
- `classify_cn.py` reads YAML calibration via `load_calibration("cn")`
  and applies CN-specific framework: PBOC reaction (7D 逆回购 primary)
  + credit impulse + 4-component dispersion + property overlay + CPI
  framing.
- **CPI framing key insight**: in disinflation regime with target = 2%
  central-tendency, **rising inflation = supportive recovery signal**,
  not overheat warning. `policy_stance = supportive_recovery_below_target`
  fires when current < 1.5 AND direction == "rising".
- **Credit impulse new computation**: `data-cn/scripts/pack.py` adds
  `_compute_credit_impulse()` helper. Uses akshare `shrzgm` (社融增量
  monthly flow) as input; derives stock-yoy proxy via trailing-12m
  rolling sum. M2 yoy as fallback.
- `native_verdict.ic_quadrant_legacy` mirrors legacy classifier output
  for parity (regression test in `test_chain_cn_classifier_e2e`).

---

## Next Recalibration Triggers

Watch for:

- **PBOC 货币政策委员会 2026-Q2 例会** (~late June 2026; mandatory)
  — refresh PBOC stance language, may signal RRR/LPR cut path.
- **NBS 2026-04 月度 CPI/PPI** (2026-05-09 ~ 2026-05-12) — first
  validation that PPI 由负转正 sustained beyond 2026-03.
- **2026-Q2 GDP 初步核算** (~mid-July 2026) — first read on whether
  Q1 5.0% growth holds; property investment trajectory.
- **PBOC RRR 降准** if it fires (market expects Q2/Q3 50bp) — refresh
  `rrr_large_bank` calibration.
- **PBOC 2026-Q1 货币政策执行报告** (~late May 2026) — quarterly
  policy report; rich qualitative context for next vintage.

If any fires, update `thresholds-china.md` first, then re-extract numeric
values into `calibrations/cn.yaml`. CI drift-detection test (planned
post-PR-7) will catch numeric mismatches.
