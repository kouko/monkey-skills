# Growth / 성장

---

## gdp-qoq: GDP 실질 전기비 / GDP Real QoQ SA%

- **Series code**: K258 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Percent (%) — quarter-over-quarter, seasonally adjusted
- **Frequency**: Quarterly
- **Publication lag**: ~8 weeks after quarter-end (advance estimate)
- **History**: From 1960 (263 observations)

**What it measures**: Korea's real GDP growth rate, quarter-over-quarter,
seasonally adjusted. The definitive measure of economic expansion or
contraction at the most granular frequency available.

**How to interpret**:
- Positive → Economy expanding on a sequential basis.
- Negative → Economy contracting. Two consecutive negative quarters is the
  informal definition of a technical recession.
- Korea's trend QoQ growth is approximately 0.5-0.7% (equivalent to ~2-3%
  annualized).

**Market significance**: ⭐⭐⭐
The most important single indicator for Korea's economic health. GDP releases
move KOSPI, KRW/USD, and bond yields. However, quarterly frequency and long
publication lag reduce real-time utility — higher-frequency proxies (IPI,
exports, sentiment) often move markets before GDP confirms.

**When to use**: Investment Clock growth axis, recession dating, cycle positioning, Korea allocation weight decisions.

**Korea-specific context**:
- Korea reports GDP on a QoQ SA basis (same as Japan, EU), unlike the US
  which reports SAAR (seasonally adjusted annualized rate). To compare
  with US GDP: rough approximation is `QoQ * 4 ≈ SAAR`.
- Korea's GDP is heavily driven by exports (~40-45% of GDP) and capital
  investment. Domestic consumption has historically been a smaller GDP driver
  compared to the US.
- The semiconductor cycle is a GDP cycle for Korea. When global chip demand
  drops, Korean GDP contracts disproportionately (as seen in 2019, 2023).
- The BOK publishes advance, revised, and final GDP estimates. ECOS data
  reflects the latest available estimate for each quarter.

**Common pitfalls**:
- QoQ rates are small numbers (typically -1% to +2%). Don't confuse with
  YoY rates or annualized rates.
- Base effects from pandemic quarters can distort comparisons.
- The advance estimate can be significantly revised. The final estimate may
  differ by 0.5 percentage points or more.

---

## gdp-nominal: GDP 명목 / GDP Nominal (시장가격)

- **Series code**: K257 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Billion KRW (조 원 scale)
- **Frequency**: Quarterly
- **Publication lag**: Same as GDP QoQ
- **History**: From 1960

**What it measures**: Korea's nominal GDP in current market prices. Includes
both real output growth and price effects (inflation). Used for computing
ratios like debt-to-GDP, market-cap-to-GDP, and tax-revenue-to-GDP.

**How to interpret**:
- Nominal GDP growth = real GDP growth + GDP deflator. Faster nominal growth
  can reflect either genuine economic expansion or high inflation.
- Nominal GDP level is needed for computing various macro ratios (government
  debt/GDP, household debt/GDP, Buffett indicator).

**Market significance**: ⭐⭐
Less directly market-moving than real GDP growth rates, but essential for
ratio analysis. Korea's nominal GDP is approximately 2,200 trillion KRW
(~$1.7T USD) as of 2025.

**When to use**: Debt-to-GDP ratio computation (household debt, government debt), Buffett indicator (market cap / nominal GDP), fiscal revenue analysis.

**Korea-specific context**:
- Korea's nominal GDP has grown significantly in KRW terms but the KRW/USD
  conversion rate matters for international comparisons. KRW depreciation
  can reduce Korea's GDP ranking in USD terms even when KRW GDP grows.
- Korea's GDP per capita reached ~$35,000 USD, making it a high-income
  economy, but KRW weakness periodically pushes it below this threshold.

**Common pitfalls**:
- Values are in billions of KRW. The numbers are very large. For international
  comparison, convert to USD using the period-average exchange rate.
- Do not compute growth rates from nominal GDP and call them "GDP growth" —
  that conflates real growth and inflation.

---

## ipi: 전산업생산지수 / All-Industry Production Index

- **Series code**: K220 (ECOS-KEYSTAT)
- **Source**: Bank of Korea (Statistics Korea data) via FinanceDataReader
- **Unit**: Index (base year 2020 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after reference month
- **History**: From 2000 (314 observations)

**What it measures**: A composite monthly production index covering all
industries (manufacturing, mining, electricity/gas, services, construction).
Korea's broadest monthly economic activity indicator.

**How to interpret**:
- Rising → Broad-based economic activity expanding. More comprehensive than
  manufacturing alone because it includes services (~60% of GDP).
- Falling → Economic activity contracting across sectors. If services and
  manufacturing fall together, it's a strong recession signal.

**Market significance**: ⭐⭐
The most comprehensive monthly activity indicator. Less watched than
manufacturing production because it's published later and with more
revisions, but provides a better picture of overall economic momentum.

**When to use**: High-frequency growth proxy (monthly vs quarterly GDP), manufacturing cycle tracking, export outlook gauge, Investment Clock growth confirmation.

**Korea-specific context**:
- The all-industry index was introduced in the 2000s to address the
  limitation of manufacturing-only indices for a services-heavy economy.
- Korea's service sector has grown from ~50% to ~60% of GDP over the
  past two decades. The all-industry index captures this structural shift.

**Common pitfalls**:
- Shorter history (from 2000) compared to manufacturing production.
- The index includes seasonal patterns. Use the SA (seasonally adjusted)
  version when available for month-to-month comparisons.
- Revisions to services data can be significant.

---

## manufacturing: 제조업 생산지수 / Manufacturing Production Index

- **Series code**: K201 (ECOS-KEYSTAT)
- **Source**: Bank of Korea (Statistics Korea data) via FinanceDataReader
- **Unit**: Index (base year 2020 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after reference month
- **History**: From 2000

**What it measures**: Monthly index of manufacturing sector output.
Covers factories producing semiconductors, automobiles, ships,
petrochemicals, steel, displays, and other manufactured goods.

**How to interpret**:
- Rising → Manufacturing sector expanding. Positive for Korea's export
  outlook and corporate earnings (manufacturing-heavy KOSPI companies).
- Falling → Manufacturing contraction. Given Korea's export-led model,
  manufacturing weakness typically precedes broader economic slowdown.

**Market significance**: ⭐⭐
Korean manufacturing is ~28% of GDP (one of the highest ratios among
advanced economies) and generates the majority of export revenue.
Manufacturing production trends are highly correlated with KOSPI earnings.

**When to use**: Semiconductor cycle tracking, chaebol production outlook, KOSPI earnings direction indicator, Korea export competitiveness gauge.

**Korea-specific context**:
- Korea's manufacturing sector is dominated by a few mega-industries:
  semiconductors (Samsung, SK Hynix), automobiles (Hyundai, Kia),
  shipbuilding (HD Korea Shipbuilding), petrochemicals (LG Chem),
  and steel (POSCO). These sectors drive the aggregate index.
- The semiconductor cycle creates sharp manufacturing swings. Memory chip
  production ramps and cuts directly impact the index.
- Korea maintained a high manufacturing share of GDP while most advanced
  economies deindustrialized. This makes manufacturing production more
  relevant for Korea than for the US, Japan, or Europe.

**Common pitfalls**:
- Manufacturing production ≠ manufacturing earnings. Companies can increase
  production while margins compress (e.g., during inventory buildup).
- The index covers volume, not value. High production during a price slump
  (e.g., memory chip oversupply) can show rising production with falling
  revenue.

---

## GDP expenditure breakdown (K259 / K260 / K261)

The following three presets break down GDP by expenditure side. All
are quarterly, SA, constant prices, QoQ growth %, published together
with `gdp-qoq` around ~8 weeks after quarter-end.

### private-consumption: 민간소비 / Private Consumption

- **Series code**: K259 (ECOS-KEYSTAT)
- **Unit**: QoQ growth % (SA, real)
- **Share of GDP**: ~50%

**What it measures**: Household final consumption expenditure, the
single largest GDP component. Drives discretionary + staples earnings
(KOSPI consumer sector).

**How to interpret**:
- Structurally weak post-2020 (housing affordability + aging + household
  debt near historical highs). Frequent sub-1% QoQ prints.
- Rare sharp acceleration → often tied to fiscal stimulus (cash handouts)
  or post-crisis rebound.

**Market significance**: ⭐⭐⭐ — determines CSI validity and BOK growth outlook.

### equipment-investment: 설비투자 / Equipment Investment

- **Series code**: K260 (ECOS-KEYSTAT)
- **Unit**: QoQ growth % (SA, real)
- **Share of GDP**: ~10%

**What it measures**: Private-sector fixed capital formation — machinery,
ICT equipment, transportation equipment. Follows the semiconductor capex
cycle closely (Samsung / SK Hynix fab spend).

**How to interpret**:
- Extremely volatile — single-quarter swings of ±10% are common.
- Leading indicator for IPI and goods exports 3-6 months out.

**Market significance**: ⭐⭐ — semiconductor cycle leading indicator.

### construction-investment: 건설투자 / Construction Investment

- **Series code**: K261 (ECOS-KEYSTAT)
- **Unit**: QoQ growth % (SA, real)
- **Share of GDP**: ~12-15%

**What it measures**: Building construction + civil engineering. Includes
residential + commercial + infrastructure.

**How to interpret**:
- Structural headwind since 2022 property-project-finance crisis
  (2022 Legoland 사태 + subsequent developer defaults).
- Government infrastructure stimulus can offset private decline
  (watch 재정보강 fiscal announcements).

**Market significance**: ⭐⭐ — construction chaebol (현대건설, 대우건설) earnings
+ commodity demand (steel, cement) + banking credit quality proxy.

**Common pitfalls (all three)**:
- Quarterly, not monthly. For higher-frequency substitutes: IPI +
  manufacturing for equipment, housing permits (not in skill) for
  construction.
- These are **QoQ** — do not confuse with YoY. QoQ prints of +3% imply
  annualized ~12%, which is the headline GDP growth scale.
