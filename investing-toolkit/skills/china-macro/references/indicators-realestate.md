# Real Estate / 房地产

NBS publishes 4 monthly real-estate tables as part of the standard 房地产
release cycle (around the 15th of each month alongside 三大数据). Each
entry below is a cumulative year-to-date YoY reading — NBS rarely
publishes single-month 房地产 YoY due to Spring Festival distortion.

---

## realestate-investment-yoy: 房地产开发投资 累计同比

- **Series code**: NBS cid `9206137ccf03460daa74b7799e0f3c31` / indicator `205e08cba8c2409980db58c98da91b6f`
- **Source**: NBS direct (月度→房地产→房地产开发投资情况)
- **Unit**: Percent (%)
- **Frequency**: Monthly (cumulative YTD)
- **Publication lag**: ~15 days after month-end

**What it measures**: Year-to-date year-over-year percentage change in
real estate development investment (gross capital formation in the real
estate sector). This is the primary Chinese real estate activity gauge.

**How to interpret**:
- Positive → sector expanding; developers still committing capex.
- Sustained negative (as observed 2022+) → structural property downturn.
- Compare with **固定资产投资 YoY** (`fai-yoy`) to gauge whether real
  estate is dragging or leading total FAI.

**Market significance**: ⭐⭐⭐
Single most-watched Chinese real estate indicator after 70-city price
index (which this skill does not cover — see SKILL.md Limitations).
Moves CSI 300 property sub-index and Hong Kong H-shares real estate
names (Country Garden, Longfor, Vanke).

**When to use**: property-sector narrative assessment, FAI decomposition,
wealth-effect transmission to consumption.

**China-specific context**:
- Property has historically been ~25% of GDP including supply-chain
  effects. A sustained -10% in this series signals ~2-3pp drag on
  headline GDP growth.
- **2021+ downturn**: series turned negative in H2 2021 and has stayed
  negative through 2025 — Evergrande / Country Garden / Sunac defaults
  drove developers to halt land purchases.
- The "三条红线" regulatory framework (2020) is the root of the
  downturn. Recent stimulus has targeted existing-home destocking
  (收储) rather than reviving new construction.

**Common pitfalls**:
- Cumulative YoY is a smoothed read; to detect turning points look at
  derived monthly reconstruction (累计_n - 累计_n-1) which NBS does not
  publish directly.
- NBS classifies only 房地产开发投资 (new construction + land purchase);
  existing-home trading volume is not in this series.

---

## housing-sales-area-yoy: 商品住宅销售面积 累计同比

- **Series code**: NBS cid `e9bb62c29eaa49f0b6e88548fc3924aa` / indicator `206c52536182472aae8e01b52aaeb201`
- **Source**: NBS direct (月度→房地产→商品住宅销售面积)
- **Unit**: Percent (%)
- **Frequency**: Monthly (cumulative YTD)

**What it measures**: YTD YoY change in floor area (square meters) of
residential commercial properties sold. Volume-based activity gauge.

**How to interpret**:
- Distinguish volume from value — if area -20% but value -30%, prices
  are falling faster than volume shrinks (weaker prices).
- Leading indicator for 房地产开发投资 by ~6 months (developers react
  to sales volume).

**Market significance**: ⭐⭐⭐
First-read real-estate cycle gauge. Banks cite this when discussing
mortgage demand and asset quality.

**When to use**: property cycle timing, construction demand forecasting.

**China-specific context**: 商品住宅 (commercial residential) excludes
保障房 (public housing) and 小产权房 (informal). Tier-1 cities
(北京/上海/广深) often diverge from Tier-2/3 — this aggregate hides
that dispersion.

---

## housing-sales-value-yoy: 商品住宅销售额 累计同比

- **Series code**: NBS cid `9756d668012e4c96807ef1ea1749319c` / indicator `2de1944906984790bc41d58d7c0cb885`
- **Source**: NBS direct
- **Unit**: Percent (%)

**What it measures**: YTD YoY change in RMB value of residential
properties sold. Combines volume and price effect.

**How to interpret**: Value YoY vs Area YoY divergence = implied price
move.
- Value -30% while Area -20% → ~10% price decline
- Value falls faster than area → deflating market

**Market significance**: ⭐⭐⭐

**When to use**: developer revenue forecasting, mortgage originations
modeling, wealth-effect estimation.

**Common pitfalls**: Mix shift between Tier-1 (expensive) and Tier-3
(cheap) can distort the value series even if underlying prices are
stable. Cross-check with 70-city price index (not in skill — see PDF
at stats.gov.cn/sj/zxfb).

---

## realestate-funding-yoy: 房地产投资本年资金来源 累计同比

- **Series code**: NBS cid `4c5a2c305155451f99abf94e42305ba2` / indicator `e3c3d04b40fc41348a82eb8b6fdcb28b`
- **Source**: NBS direct
- **Unit**: Percent (%)

**What it measures**: YTD YoY change in total funds available to real
estate developers (sum of bank loans + FDI + self-raised + advance
payments from buyers + other).

**How to interpret**:
- Leads investment by 3-6 months — developers spend what they've
  raised.
- Sustained negative → liquidity stress for developers; defaults
  more likely.

**Market significance**: ⭐⭐
Early-warning indicator for developer bankruptcies. Watched alongside
PBOC's real estate loan balance.

**When to use**: credit risk assessment of property developers,
timing of bottom in property cycle.

**China-specific context**:
- **定金及预收款** (deposits + advance payments from buyers) is
  historically the single largest funding source (~40-50%). When
  pre-sales collapse (like in 2022-2024), funding crashes even if
  bank loans hold up.
- This is why 保交楼 (deliver-the-building-at-all-cost) became a
  2022-2023 policy priority — buyers' pre-payments were at risk.

**Common pitfalls**:
- The sub-breakdown (bank loans / FDI / self-raised / deposits) is
  more informative than the aggregate. This skill pins the aggregate
  only; sub-components available in the NBS catalog for cherry-picking.
