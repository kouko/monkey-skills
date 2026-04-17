# Sentiment / Cycle / 경기

---

## consumer-sentiment: 소비자심리지수 / Consumer Sentiment Index (CSI)

- **Series code**: K252 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Index (100 = neutral)
- **Frequency**: Monthly
- **Publication lag**: ~1 week after month-end (released around 27th of reference month)
- **History**: From 2008

**What it measures**: A survey-based index reflecting Korean consumers'
confidence about current and future economic conditions. Compiled by the
BOK from a monthly survey of ~2,300 households nationwide.

**How to interpret**:
- Above 100 → Consumers are optimistic. More consumers expect economic
  conditions to improve than worsen. Supports consumption spending.
- Below 100 → Consumers are pessimistic. Weakness in consumption expected.
- The direction of change matters more than the level: rising CSI → improving
  outlook; falling CSI → deteriorating outlook.

**Market significance**: ⭐⭐
A leading indicator for private consumption (~50% of GDP). Sharp drops in
CSI (as seen in 2008, 2020, 2022) precede consumption pullbacks. The BOK
watches CSI as an input to its growth outlook and rate decisions.

**When to use**: Consumption leading indicator, real estate wealth effect gauge, BOK growth outlook input, household spending direction.

**Korea-specific context**:
- Korean consumer sentiment is strongly influenced by: (1) real estate
  prices (housing is the primary household asset), (2) employment conditions,
  (3) stock market performance, and (4) geopolitical risks (North Korea).
- The real estate channel is particularly important. Rising apartment prices
  boost sentiment among homeowners (wealth effect) but depress sentiment
  among young non-owners (affordability anxiety). This creates divergent
  sentiment across demographics.
- North Korea provocations (missile tests, nuclear tests) cause temporary
  CSI dips that typically reverse within 1-2 months.

**Common pitfalls**:
- Data only from 2008. Shorter history than most other macro indicators.
- Sentiment can decouple from actual economic outcomes. Consumers may be
  pessimistic while GDP is growing, or vice versa.
- The survey methodology changed in 2008 when the BOK adopted the current
  CSI framework. Pre-2008 data uses a different methodology and is not
  directly comparable.

---

## economic-sentiment: 경제심리지수 / Economic Sentiment Index (ESI)

- **Series code**: K269 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Index (100 = long-run average)
- **Frequency**: Monthly
- **Publication lag**: ~1 week after month-end
- **History**: From 2008

**What it measures**: A composite sentiment index combining consumer and
business confidence surveys. Provides a broader picture of economic
sentiment than consumer-only or business-only surveys.

**How to interpret**:
- Above 100 → Sentiment above long-run average. Economy perceived as
  performing better than typical.
- Below 100 → Below long-run average. Economic pessimism.
- The ESI combines consumer sentiment (CSI) with the Business Survey
  Index (BSI), giving weight to both household and corporate sectors.

**Market significance**: ⭐⭐
More comprehensive than CSI alone. The composite nature makes it a better
summary statistic for overall economic mood. Useful for cross-country
comparison (similar to EU ESI methodology).

**When to use**: Broad sentiment summary statistic, cross-country comparison (EU ESI methodology), cycle turning point confirmation.

**Korea-specific context**:
- The ESI was introduced to provide a single summary indicator similar to
  the EU's Economic Sentiment Indicator. It follows a broadly similar
  methodology.
- During periods of divergence between consumer and business sentiment
  (e.g., businesses optimistic on exports but consumers pessimistic on
  housing), the ESI can mask important underlying dynamics.

**Common pitfalls**:
- Same limited history as CSI (from 2008).
- The "100 = long-run average" is calibrated to 2003-2017. As the sample
  period extends, the long-run average drifts.
- The weights given to consumer vs. business components are not transparent.

---

## leading-cycle: 선행지수순환변동치 / Leading CI Cyclical Component

- **Series code**: K254 (ECOS-KEYSTAT)
- **Source**: Bank of Korea (Statistics Korea data) via FinanceDataReader
- **Unit**: Index (100 = trend)
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after reference month
- **History**: From 2000

**What it measures**: The cyclical component of the Composite Leading Index,
isolated from the long-run trend. Measures the deviation of leading economic
indicators from their trend — designed to predict turning points in the
business cycle 6-9 months ahead.

**How to interpret**:
- Above 100 → Economy above trend. Leading indicators suggest continued
  expansion.
- Below 100 → Economy below trend. Leading indicators signal potential
  downturn.
- **Turning points are the key signal**: peak (above 100 then turning down)
  signals imminent slowdown; trough (below 100 then turning up) signals
  recovery ahead.
- The cyclical component is more useful than the composite index level
  because it strips out the secular growth trend.

**Market significance**: ⭐⭐⭐
Korea's most important business cycle timing indicator. The leading cyclical
component historically turns 6-9 months before GDP turning points.
Statistics Korea officially announces business cycle reference dates
(경기기준일) based on this and related indicators.

**When to use**: Business cycle turning point prediction (6-9 month lead), recession probability assessment, Investment Clock phase transition signal.

**Korea-specific context**:
- The leading index components include: building permits, machinery orders,
  stock prices (KOSPI), money supply, export L/C arrivals, and consumer
  expectations. These are forward-looking indicators.
- Korea's business cycle is strongly correlated with the global semiconductor
  cycle. The leading index tends to turn around the same time as global
  chip demand indicators.
- Statistics Korea publishes three cyclical indices: leading (선행, K254),
  coincident (동행, K253), and lagging. Together they form the "3-signal
  system" for business cycle analysis.

**Common pitfalls**:
- Cyclical components are subject to revision as new data arrives and
  trend estimates are updated. End-of-sample turning points can be revised.
- The index uses the HP filter (or similar trend extraction) which is
  known to have end-point bias. Recent values are less reliable.
- A single month above/below 100 does not confirm a turning point. Look
  for 3+ months of consistent direction.

---

## coincident-cycle: 동행지수순환변동치 / Coincident CI Cyclical Component

- **Series code**: K253 (ECOS-KEYSTAT)
- **Source**: Bank of Korea (Statistics Korea data) via FinanceDataReader
- **Unit**: Index (100 = trend)
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after reference month
- **History**: From 2000

**What it measures**: The cyclical component of the Composite Coincident
Index. Measures the current state of the business cycle — whether the economy
is currently above or below trend. Coincident indicators move in real-time
with the economy.

**How to interpret**:
- Above 100 → Economy currently expanding (above trend).
- Below 100 → Economy currently contracting (below trend).
- The coincident cyclical component confirms what the leading component
  predicted 6-9 months earlier.

**Market significance**: ⭐⭐
Used to confirm the current phase of the business cycle. Less forward-looking
than the leading component, but more reliable for assessing "where we are
now." Statistics Korea uses coincident indicators to officially date
business cycle peaks and troughs.

**When to use**: Current cycle phase confirmation, recession dating, leading-coincident gap analysis for acceleration vs deceleration diagnosis.

**Korea-specific context**:
- Coincident index components include: IPI, services production, retail
  sales, imports, non-farm employment. These reflect current economic
  activity.
- The gap between leading and coincident cyclical components indicates
  whether the economy is accelerating or decelerating. Leading above
  coincident = acceleration ahead; leading below coincident = deceleration
  ahead.

**Common pitfalls**:
- Same revision and end-point bias issues as the leading component.
- "Coincident" still has a ~2 month publication lag. It's coincident in
  economic timing, not in data release timing.
- The coincident component can show the economy "above trend" even during
  a slowdown if the slowdown hasn't yet brought activity below trend.
