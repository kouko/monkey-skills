# US Macro Indicators — FRED Series Reference

Comprehensive reference for the 21 FRED series used by the `us-macro` skill.
Each entry covers units, frequency, publication lag, interpretation guidance,
and common pitfalls. The first 8 series cover core macro (rates, inflation,
growth). The remaining 13 cover sector-level indicators mapped to sector ETFs.

---

## Rates

## T10Y2Y: 10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity

- **Series code**: T10Y2Y (FRED)
- **Source**: Federal Reserve Board of Governors
- **Unit**: Percent
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **History**: From 1976 (daily)

**What it measures**: The spread between the 10-year and 2-year U.S. Treasury
yields. This is the most widely watched yield curve indicator, reflecting
market expectations for future economic conditions and monetary policy.

**How to interpret**:
- Rising (steepening) → Markets expect stronger growth or higher future
  inflation; long-term rates rising faster than short-term rates. Often seen
  during early recovery phases.
- Falling (flattening) → Markets expect slower growth or anticipate rate cuts;
  short-term rates rising toward or above long-term rates. Precedes economic
  slowdowns.
- Negative (inverted) → Short-term yields exceed long-term yields. Historically
  a reliable recession predictor with a 6-18 month lead time.

**Market significance**: ⭐⭐⭐
The single most watched recession indicator. An inversion (negative spread)
has preceded every U.S. recession since 1970 with only one false positive.
FOMC members, fixed-income desks, and macro strategists monitor this daily.
CPI release days aside, yield curve moves generate more market commentary
than almost any other macro data point.

**When to use**: Yield curve analysis, Investment Clock regime diagnosis,
recession probability assessment, fixed-income allocation decisions.

**Common pitfalls**:
- An inverted curve does not mean an imminent recession — the lag is typically
  6-18 months. The curve often re-steepens before the recession actually begins.
- QE and QT distort the spread by compressing or expanding the term premium,
  so the signal is noisier during periods of active Fed balance sheet operations.
- A single day's reading is meaningless; look at the trend over weeks/months.

**Cross-indicator notes**:
- Campbell Harvey (1986, Duke): discovered yield curve recession prediction in his dissertation. 2022-23 inversion lasted 16 months without recession — possibly the first false signal, or lag extending due to post-pandemic structural changes. Conclusion still open.
- MSCI study (1978-2022, 14 inversions): 36 months after inversion, 10/14 cases showed positive equity returns. Inversion is a recession signal, NOT a market timing signal.
- NY Fed recession probability model uses 10Y-3M spread (not T10Y2Y). When probability exceeds 32%, recession has always followed (except Oct 1966).
  Source: https://www.newyorkfed.org/research/capital_markets/ycfaq

---

## DGS10: Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity

- **Series code**: DGS10 (FRED)
- **Source**: Federal Reserve Board of Governors
- **Unit**: Percent
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **History**: From 1962 (daily)

**What it measures**: The yield on 10-year U.S. Treasury bonds, widely
considered the benchmark risk-free rate. It reflects long-term inflation
expectations, real growth expectations, and the term premium.

**How to interpret**:
- Rising → Markets expect higher inflation, stronger growth, or increased
  government borrowing. Raises discount rates for equity valuations (DCF) and
  tightens financial conditions.
- Falling → Markets expect lower inflation, weaker growth, or flight to safety.
  Lowers discount rates and loosens financial conditions.

**Market significance**: ⭐⭐⭐
The global benchmark risk-free rate. Moves in the 10Y drive mortgage rates,
corporate bond pricing, equity valuations (DCF discount rate), and cross-border
capital flows. Every asset class references this yield directly or indirectly.
When DGS10 moves 10+ bps in a day, it's front-page financial news.

**When to use**: DCF discount rate input, equity valuation sensitivity,
mortgage rate forecasting, financial conditions assessment, cross-asset
allocation.

**Common pitfalls**:
- The 10Y yield conflates multiple factors (inflation expectations + real rate
  + term premium). Use TIPS breakevens to decompose if precision matters.
- During flight-to-quality episodes, yields can fall even as economic
  fundamentals remain strong.
- Comparing across countries requires adjusting for currency hedging costs.

---

## DGS2: Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity

- **Series code**: DGS2 (FRED)
- **Source**: Federal Reserve Board of Governors
- **Unit**: Percent
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **History**: From 1976 (daily)

**What it measures**: The yield on 2-year U.S. Treasury bonds, which closely
tracks expected Federal Reserve policy rate path over the next two years. It
is the most policy-sensitive point on the yield curve.

**How to interpret**:
- Rising → Markets expect Fed tightening (rate hikes or higher-for-longer).
  Often moves ahead of actual policy changes as markets price in forward
  guidance.
- Falling → Markets expect Fed easing (rate cuts). Sharp drops often signal
  imminent policy pivot or recession fears.

**Market significance**: ⭐⭐
The most policy-sensitive yield on the curve. Reacts sharply to FOMC
statements, dot plots, and economic data that shifts Fed expectations.
Traders use DGS2 as a proxy for "what the market thinks the Fed will do."
Less watched by the general public than DGS10, but essential for rate
strategy desks.

**When to use**: Fed policy expectations, short-duration fixed-income
positioning, yield curve spread analysis (paired with DGS10 for T10Y2Y
computation).

**Common pitfalls**:
- DGS2 is heavily influenced by Fed forward guidance. If you want to know
  what the Fed will do next, look at Fed Funds Futures — DGS2 reflects
  expectations over a 2-year horizon, not the next meeting.
- Sudden moves in DGS2 can reflect positioning/liquidity rather than
  fundamental shifts. Confirm with futures pricing.
- The 2Y yield can remain elevated even after the Fed pauses if markets
  expect "higher for longer."

---

## FEDFUNDS: Effective Federal Funds Rate

- **Series code**: FEDFUNDS (FRED)
- **Source**: Federal Reserve Bank of New York
- **Unit**: Percent
- **Frequency**: Monthly (average of daily values)
- **Publication lag**: ~1 week after month-end
- **History**: From 1954 (monthly)

**What it measures**: The volume-weighted average rate at which depository
institutions lend reserve balances to other depository institutions overnight.
This is the primary tool of Federal Reserve monetary policy.

**How to interpret**:
- Rising → Fed is tightening monetary policy to combat inflation or
  overheating. Higher borrowing costs across the economy.
- Falling → Fed is easing to stimulate growth or respond to financial stress.
  Lower borrowing costs encourage lending and spending.

**Market significance**: ⭐⭐⭐
The Fed's primary policy tool. Every FOMC meeting's rate decision is global
headline news. The absolute level of FEDFUNDS sets the floor for all short-term
borrowing costs in the world's largest economy. Changes ripple through mortgages,
corporate credit, emerging market capital flows, and currency markets.

**When to use**: Monetary policy stance assessment, Investment Clock phase
mapping (policy rate vs. inflation), short-term rate environment baseline.

**Common pitfalls**:
- FEDFUNDS is a backward-looking monthly average. For real-time policy rate,
  use the Fed's target range from the latest FOMC statement.
- The effective rate can trade slightly outside the target range due to
  market dynamics, especially around quarter-end.
- A paused Fed Funds rate does not mean neutral policy — the real rate
  (FEDFUNDS minus inflation) is what matters for economic impact.

---

## Inflation

## CPIAUCSL: Consumer Price Index for All Urban Consumers: All Items in U.S. City Average

- **Series code**: CPIAUCSL (FRED)
- **Source**: U.S. Bureau of Labor Statistics (BLS)
- **Unit**: Index (1982-84 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~2-3 weeks after reference month
- **History**: From 1947 (monthly)

**What it measures**: The broadest measure of consumer price inflation in the
U.S., covering food, energy, housing, transportation, medical care, and other
goods and services. Often called "headline CPI."

**How to interpret**:
- Rising (accelerating YoY) → Inflation is broadening or intensifying. Expect
  hawkish Fed response. Negative for duration assets (bonds), mixed for
  equities depending on pricing power.
- Falling (decelerating YoY) → Disinflation in progress. Opens the door for
  dovish Fed pivot. Positive for duration assets.

**Market significance**: ⭐⭐⭐
The most market-moving economic release on the calendar. CPI day routinely
produces 1-2% equity swings and 10+ bps Treasury moves. The Fed's dual mandate
makes inflation control half of its mission. Every basis point of surprise vs.
consensus triggers immediate repricing across all asset classes. Arguably the
single most important macro data point for global markets.

**When to use**: Investment Clock inflation axis (use YoY rate of change, not
level), real return calculations, TIPS breakeven comparison, GIP quadrant
mapping.

**Common pitfalls**:
- CPI is an index level, not a rate. You must compute YoY or MoM percentage
  change yourself. A "falling CPI" (index) means deflation, which is extremely
  rare — usually what falls is the YoY rate (disinflation).
- Headline CPI includes volatile food and energy. For underlying trend, pair
  with CPILFESL (core CPI).
- Shelter costs (OER) have a well-known lag of 12-18 months vs. real-time
  rents. CPI can overstate or understate housing inflation depending on cycle
  position.
- Base effects can distort YoY readings. Always check MoM annualized alongside
  YoY.

**Cross-indicator notes**:
- CPI vs PCE divergence: CPI weights shelter ~2x higher than PCE. During housing inflation cycles (e.g. 2021-2024), CPI can run 50-90 bps above PCE. The Fed targets PCE, not CPI.
  Source: Cleveland Fed infographic, 2024 https://www.clevelandfed.org/collections/infographics/2024/infogr-20241205-cpi-versus-pce-price-index
- Sahm Rule: when unemployment's 3-month average rises >=0.5% above prior 12-month low, recession is underway. 11/11 correct since 1950. Available as real-time FRED series: SAHMREALTIME.
  Source: Claudia Sahm; FRED https://fred.stlouisfed.org/series/SAHMREALTIME

---

## CPILFESL: Consumer Price Index for All Urban Consumers: All Items Less Food and Energy in U.S. City Average

- **Series code**: CPILFESL (FRED)
- **Source**: U.S. Bureau of Labor Statistics (BLS)
- **Unit**: Index (1982-84 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~2-3 weeks after reference month
- **History**: From 1957 (monthly)

**What it measures**: CPI excluding food and energy — the "core CPI." Strips
out the most volatile components to reveal the underlying inflation trend.
This is the measure the Fed watches most closely for sustained inflation
pressure.

**How to interpret**:
- Rising (accelerating YoY) → Underlying inflation pressures are building.
  Strongest signal for sustained hawkish policy because it filters out
  transitory commodity swings.
- Falling (decelerating YoY) → Underlying inflation is cooling. The Fed's
  preferred signal for considering easing.

**Market significance**: ⭐⭐⭐
A critical inflation measure for policy decisions. Note: the Fed's official
2% inflation target uses PCE (Personal Consumption Expenditures), not CPI.
However, CPI releases precede PCE by ~2 weeks and are more widely covered
in media. Core CPI is the market's real-time proxy for underlying inflation
pressure. Market participants scrutinize the core MoM annualized print for
signals about the PCE print to come.

**When to use**: Cross-check against headline CPI to determine if inflation
is broad-based or commodity-driven. Core CPI is the better input for
structural inflation assessment and Fed reaction function modeling.

**Common pitfalls**:
- Same index-vs-rate trap as CPIAUCSL — always compute percentage changes.
- "Core" still includes shelter, which is the largest and most lagging
  component. "Supercore" (core services ex-housing) is an increasingly
  watched alternative, but not available as a single FRED series.
- Excluding food and energy does not mean those costs are unimportant to
  consumers — it means they are too volatile to inform trend analysis.

---

## Growth

## GDPC1: Real Gross Domestic Product

- **Series code**: GDPC1 (FRED)
- **Source**: U.S. Bureau of Economic Analysis (BEA)
- **Unit**: Billions of chained 2017 dollars
- **Frequency**: Quarterly
- **Publication lag**: ~1 month after quarter-end (advance estimate)
- **History**: From 1947 (quarterly)

**What it measures**: The inflation-adjusted total value of goods and services
produced in the U.S. economy. This is the broadest measure of economic output
and the definitive gauge of whether the economy is expanding or contracting.

**How to interpret**:
- Rising (positive QoQ annualized growth) → Economy is expanding. Supportive
  of corporate earnings and risk assets.
- Falling (negative QoQ annualized growth) → Economy is contracting. The
  popular "two consecutive negative quarters = recession" heuristic is
  explicitly rejected by NBER, which uses broader criteria (depth, diffusion,
  duration). The 2001 recession had no two consecutive negative quarters.

**Market significance**: ⭐⭐
The definitive measure of economic output, but its market impact is lower
than CPI because quarterly frequency means markets have already priced in
the trend via higher-frequency proxies (employment, ISM, retail sales).
The advance estimate still moves markets when it surprises significantly.
Revision vintages (second and third estimates) rarely move markets.

**When to use**: Investment Clock growth axis, GIP quadrant mapping (rate of
change), cycle positioning, asset allocation decisions.

**Common pitfalls**:
- GDP is heavily revised. The advance estimate can differ materially from the
  second and third estimates. Always note which vintage you are using.
- Quarterly frequency means GDP is a lagging indicator — by the time a
  contraction shows up in GDP, financial markets have often already priced it.
- GDP can be boosted by inventory accumulation or government spending that
  masks private-sector weakness. Check the composition, not just the headline.
- Chained dollars use a different deflator than CPI. Do not mix GDP deflator
  and CPI for real-return calculations.

---

## INDPRO: Industrial Production: Total Index

- **Series code**: INDPRO (FRED)
- **Source**: Federal Reserve Board of Governors
- **Unit**: Index (2017 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **History**: From 1919 (monthly)

**What it measures**: The real output of U.S. manufacturing, mining, and
electric and gas utilities. While industrial production represents roughly
15-20% of GDP, it is a high-frequency cyclical indicator that leads broader
economic turning points.

**How to interpret**:
- Rising (positive MoM) → Industrial activity expanding. Typically aligns with
  early-to-mid cycle growth. Supportive of cyclical equities and commodities.
- Falling (negative MoM) → Industrial activity contracting. Can signal
  approaching recession, especially if sustained over 3+ months. Favors
  defensive positioning.

**Market significance**: ⭐⭐
A high-frequency cyclical gauge that fills the gap between quarterly GDP
prints. Manufacturing is a small share of GDP (roughly 15-20%, 2015–2024
stable) but is more cyclically sensitive than services, making INDPRO a
useful early warning. ISM Manufacturing PMI gets more headlines, but INDPRO
is the hard data confirmation. Less market-moving than CPI or employment,
but important for cycle-timing and sector rotation.

**When to use**: Investment Clock growth proxy (higher frequency than GDP),
GIP quadrant mapping (rate of change), manufacturing cycle assessment,
cyclical vs. defensive sector allocation.

**Common pitfalls**:
- INDPRO covers manufacturing, mining, and utilities — not services, which
  dominate the modern U.S. economy (~80% of GDP). A services-led expansion
  can coexist with weak INDPRO.
- Weather, strikes, and supply chain disruptions can cause sharp one-month
  swings that do not reflect the underlying trend. Use 3-month moving average
  for trend analysis.
- The index is seasonally adjusted, but holiday timing and calendar effects
  can still create noise.
- INDPRO is revised in subsequent months. Initial prints can be misleading.

**Cross-indicator notes**:
- ISM Manufacturing PMI and INDPRO correlation has declined significantly post-2010. S&P Global data shows 69% correlation over 23 years, but ISM-specific correlation is much weaker since GFC. Soft data (PMI surveys) and hard data (INDPRO) can diverge for extended periods — do not assume PMI predicts INDPRO.
- Conference Board Leading Economic Index (LEI) includes INDPRO-related components (manufacturing hours, new orders) alongside yield spread, stock prices, and building permits — 10 indicators total.
  Source: https://www.conference-board.org/topics/us-leading-indicators/

---

## Nowcast (monthly GDP proxies)

The US publishes official GDP quarterly (`GDPC1`). The 4 series below are
the industry-standard monthly GDP proxies — each viewed independently as a
real-time "GDP feel" by Fed economists, sell-side, and allocators:

| Series | What it captures | Release cadence |
|--------|------------------|-----------------|
| GDPNOW | Atlanta Fed's model-based current-quarter real GDP forecast | 6-7 updates/month within the current quarter |
| CFNAI | Weighted composite of 85 monthly activity indicators | Monthly, lag ~2 months |
| WEI | 10-weekly-indicator composite for real-time GDP | Weekly, lag ~1 week |
| USALOLITOAASTSAM | OECD Composite Leading Indicator for USA (amplitude-adjusted) | Monthly, lag ~1 month |

Cross-market parallels: this group matches china-macro's 三大數據 + services
production (monthly) and japan-macro's 景気動向指数 CI trio (monthly).

## GDPNOW: Atlanta Fed GDPNow Real GDP Nowcast (SAAR %)

- **Series code**: GDPNOW (FRED)
- **Source**: Federal Reserve Bank of Atlanta
- **Unit**: Seasonally adjusted annual rate (%), real GDP growth
- **Frequency**: Quarterly snapshot on FRED; live model updates 6-7 times per
  month on the Atlanta Fed page within the current quarter
- **Publication lag**: Tracks the CURRENT quarter (not the prior one) — the
  GDPNow estimate converges to the BEA advance estimate just before GDPC1
  prints
- **History**: From 2011 Q3

**What it measures**: A model-based forecast of real GDP growth for the
current quarter, assembled from 13 GDP sub-components and updated whenever
one of them is released. Essentially answers: "If BEA released GDP today,
what would it be?"

**How to interpret**:
- Rising → macro consensus tilts toward upside surprise on the next GDPC1
  print. Historically, equity markets track GDPNow revisions more than
  quarterly GDPC1 itself (the latter is already priced).
- Falling → downside surprise probability. A sudden drop in GDPNow often
  precedes growth-scare narratives (e.g., 2022 Q1 flipped negative 3 weeks
  before the GDPC1 print came in at -1.6%).
- Direction of WEEKLY revisions matters more than the absolute level. A
  +3% forecast that was +2% a week ago is more bullish than a static +3%.

**Market significance**: ⭐⭐⭐
The canonical "what is GDP right now" number for US macro traders. Bloomberg
and CNBC cite it by name. Fixed income desks use the GDPNow path to
calibrate rate-cut probabilities; equity desks use it for growth-regime
rotation.

**When to use**: Current-quarter growth nowcast, IC phase dating, pre-FOMC
growth assessment, macro-regime-snapshot input (for the "rate-of-change"
axis).

**Common pitfalls**:
- GDPNow shows EARLY-QUARTER estimates that are statistically noisy because
  few sub-components have printed yet. The first 2-3 weeks of a new quarter
  carry wide error bars.
- FRED's GDPNOW series only snapshots the quarter-level value — it does NOT
  record the live intra-quarter path. For real-time tracking, use Atlanta
  Fed's webpage directly; FRED is adequate for historical comparison only.
- GDPNow is model-driven, not survey-driven, so it does not capture
  qualitative shocks (supply-chain, weather, policy) that surveys might pick
  up. Pair with CFNAI for cross-validation.
- NYFed also publishes a Nowcast (discontinued Aug 2021, reinstated 2023);
  GDPNow is the industry default.

## CFNAI: Chicago Fed National Activity Index

- **Series code**: CFNAI (FRED)
- **Source**: Federal Reserve Bank of Chicago
- **Unit**: Standardized index (mean = 0, stdev = 1)
- **Frequency**: Monthly
- **Publication lag**: ~25-30 days after the reference month (later than most
  monthly macro series because CFNAI waits for all 85 inputs)
- **History**: From 1967

**What it measures**: A weighted composite of 85 monthly activity indicators
across production, employment, personal consumption/housing, and
sales/orders/inventories. Designed to be a coincident indicator of US
economic activity (not leading).

**How to interpret**:
- `CFNAI > 0` → growth above historical trend
- `CFNAI < 0` → growth below trend
- `CFNAI-MA3 < -0.70` for the first time in an expansion → high probability
  of recession onset (Chicago Fed's canonical threshold)
- `CFNAI-MA3 > +0.20` for the first time in a recession → high probability
  of recovery onset

**Market significance**: ⭐⭐
Less market-moving than GDPNow or ISM PMI (because of the ~30-day lag) but
academically preferred as the cleanest single-number US macro coincident.
Cited by NBER, IMF, and Conference Board as a dating tool for cycles.

**When to use**: Recession probability assessment, cycle-dating, IC phase
confirmation, CFNAI-MA3 threshold monitoring.

**Common pitfalls**:
- The `-0.70` threshold is a first-time trigger during expansions; recurring
  dips below -0.70 within the same cycle do not re-signal recession.
- CFNAI is a coincident indicator, not a leader. Use GDPNow or the yield
  curve for forward-looking signals.
- Single-month readings are noisy. Chicago Fed explicitly publishes CFNAI-MA3
  (3-month moving average) and recommends it for analysis — FRED also
  provides `CFNAIMA3` as a separate series if needed.

## WEI: NY Fed Weekly Economic Index

- **Series code**: WEI (FRED)
- **Source**: Federal Reserve Bank of New York
- **Unit**: Scaled to match 4-quarter GDP growth (%), SAAR
- **Frequency**: Weekly (ending Saturdays)
- **Publication lag**: ~4-7 days after the reference week
- **History**: From 2008-01

**What it measures**: A composite of 10 weekly indicators (unemployment
claims, retail sales, electricity usage, steel production, consumer
confidence, etc.) scaled so that the WEI level approximates the 4-quarter
real GDP growth rate. Created by Lewis, Mertens, and Stock during COVID to
fill the quarterly-GDP visibility gap.

**How to interpret**:
- WEI ≈ current pace of 4-quarter real GDP growth
- WEI crossing 0 → economy shifting between expansion and contraction
- A week-over-week drop of 1pp+ in a non-holiday week → meaningful
  deceleration signal
- Seasonal patterns: WEI is seasonally adjusted, but still noisy around
  Thanksgiving / Christmas weeks

**Market significance**: ⭐⭐
Preferred high-frequency GDP tracker for cross-asset strategists. Widely
cited by FX / rates desks during policy-pivot periods. Less commonly on
equity-desk dashboards than GDPNow.

**When to use**: Weekly macro update, bond-market reaction gauging,
event-window analysis (war, pandemic, banking stress), supplement to GDPNow.

**Common pitfalls**:
- WEI conflates level and rate. A stable but low WEI (e.g., +0.5 for weeks)
  does NOT mean economy is at risk — it just means slow steady growth.
- Holiday weeks introduce noise; Atlanta Fed and NY Fed sometimes annotate
  these weeks.
- The 10-indicator basket was last revised in 2022; data-construction
  methodology changes can cause historical splices. Check NY Fed's
  methodology notes when splicing pre-2022 data.

## USALOLITOAASTSAM: OECD Composite Leading Indicator (USA)

- **Series code**: USALOLITOAASTSAM (FRED)
- **Source**: OECD (Organisation for Economic Co-operation and Development)
- **Unit**: Index, amplitude-adjusted (long-term trend = 100)
- **Frequency**: Monthly
- **Publication lag**: ~1 month after the reference month (OECD releases on
  the ~10th of each month)
- **History**: From 1960 (US series)

**What it measures**: OECD's composite leading indicator for the United
States, combining multiple forward-looking series (building permits, stock
prices, money supply, yield spread, consumer confidence) designed to signal
turning points in business-cycle activity 6-9 months ahead.

**How to interpret**:
- Index > 100 and rising → expansion, above long-term trend
- Index > 100 and falling → expansion, but decelerating (pre-peak)
- Index < 100 and falling → contraction, below trend
- Index < 100 and rising → recovery, still below trend (pre-trough)
- Crossing 100 upward → typically leads GDP peaks/troughs by 6-9 months

**Market significance**: ⭐⭐
Primary international-comparable leading indicator. OECD releases align
across G20, enabling cross-country cycle-dating. Less popular in US-only
dashboards because GDPNow + CFNAI already cover the domestic cycle, but
essential for global-macro allocation decisions.

**When to use**: Turning-point detection, international cycle comparison
(pair with OECD CLIs for EU / JP / CN to see cycle de-synchronization),
6-9-month-ahead forward view.

**Common pitfalls**:
- REPLACEMENT NOTE: The old FRED series `USSLIND` (Leading Index for the
  United States, Philadelphia Fed) was discontinued in February 2020. OECD
  CLI is the closest actively-maintained substitute; methodology differs
  (OECD uses different basket weights + amplitude adjustment) so historical
  splicing with USSLIND is not clean.
- OECD CLI is heavily revised. Recent 6 months are provisional and can
  revise 0.3-0.5 points.
- Amplitude-adjusted version (suffix `AASTSAM`) is smoother but damps
  magnitude of extreme events; normalized version (`NOSTSAM`) preserves
  magnitude but is harder to interpret around 100.

---

## Real Rates (TIPS + Breakeven Inflation)

The real-rates block decomposes nominal Treasury yields into inflation
expectations (breakeven) and inflation-adjusted market yields (TIPS).
Fed policy stance reads off this: negative real yields = accommodative,
positive and rising = restrictive.

Identity: `Nominal (DGSxx) ≈ Breakeven (TxxYIE) + Real (DFIIxx)`.

### T5YIE: 5-Year Breakeven Inflation Rate

- **Series code**: T5YIE (FRED)
- **Source**: Federal Reserve Bank of St. Louis (computed: DGS5 − DFII5)
- **Unit**: Percent, annualised
- **Frequency**: Daily (business days)
- **Publication lag**: ~1-2 business days
- **History**: From 2003

**What it measures**: Market-implied average annual CPI inflation
expected over the next 5 years. Computed as the yield spread between
5-year nominal Treasuries (DGS5) and 5-year TIPS (DFII5).

**How to interpret**:
- Above Fed 2% target → markets expect above-target inflation.
- Below 2% → markets expect below-target inflation (disinflation or
  deflation risk).
- Sharp moves (±25 bp intraday) typically around CPI releases, FOMC
  statements, or inflation-surprise events.

**Market significance**: ⭐⭐⭐ — the cleanest daily read on inflation
expectations. Watched by FOMC (Fed dot-plot framing), TIPS desks, and
macro PMs.

**Pitfalls**:
- Contains a liquidity premium (TIPS less liquid than nominal) — real
  expectations are typically ~15-30 bp lower than the headline
  breakeven.
- Short-tenor breakevens (<2Y) are very noisy — use 5Y/10Y as the
  benchmarks.

---

### T10YIE: 10-Year Breakeven Inflation Rate

- **Series code**: T10YIE (FRED)
- **Source**: Federal Reserve Bank of St. Louis (computed: DGS10 − DFII10)
- **Unit**: Percent, annualised
- **Frequency**: Daily (business days)
- **Publication lag**: ~1-2 business days
- **History**: From 2003

**What it measures**: Market-implied average annual CPI inflation over
the next 10 years. The standard long-term inflation-expectations
benchmark.

**How to interpret**:
- 10Y breakeven is stickier than 5Y — slower to react, more reflective
  of long-run regime expectations.
- Fed watches the **5Y5Y forward** (derived from 5Y + 10Y breakevens)
  as its preferred long-run inflation anchor.

**Market significance**: ⭐⭐⭐ — cross-checked with survey measures
(UMich 1Y / 5-10Y, NY Fed SCE) for inflation-expectations regime
diagnosis.

---

### DFII5: 5-Year Treasury Inflation-Indexed Security (5Y TIPS yield)

- **Series code**: DFII5 (FRED)
- **Source**: U.S. Treasury via FRED
- **Unit**: Percent, annualised
- **Frequency**: Daily (business days)
- **Publication lag**: ~1-2 business days
- **History**: From 2003

**What it measures**: Market real yield on 5-year TIPS. Unlike the
breakeven (an expectation), this is the **actual yield investors can
lock in above inflation** — the market price of capital in real terms.

**How to interpret** (signal thresholds used by the regime skill — four-tier):
- `DFII5 < 0%` → **Accommodative** (real cost of capital negative;
  favours risk assets, gold, duration).
- `0% ≤ DFII5 < 1.0%` → **Neutral** (around HLW r* minus term premium).
- `1.0% ≤ DFII5 < 1.75%` → **Moderately Restrictive** (matches Williams'
  Dec 2025 "modestly restrictive" qualitative guidance).
- `DFII5 ≥ 1.75%` → **Clearly Restrictive** (above FOMC long-run-dot
  upper range; full headwind for equity multiples / credit / REITs).

Post-COVID r* is contested in the literature: HLW (2025) = 1.42%;
Lubik-Matthes = 2.15%; NY Fed composite ~1.7% real. The 1.0/1.75%
two-tier split respects this disagreement. See
`investing-toolkit/skills/macro-regime-snapshot/references/investment-clock-cheatsheet.md`
§ "Threshold provenance" for the full calibration audit.

**Market significance**: ⭐⭐⭐ — the single best summary of Fed policy
stance in real terms. Rising DFII5 → tightening financial conditions;
falling DFII5 → loosening.

---

### DFII10: 10-Year Treasury Inflation-Indexed Security (10Y TIPS yield)

- **Series code**: DFII10 (FRED)
- **Source**: U.S. Treasury via FRED
- **Unit**: Percent, annualised
- **Frequency**: Daily (business days)
- **Publication lag**: ~1-2 business days
- **History**: From 2003

**What it measures**: Market real yield on 10-year TIPS. The long-end
real-rate benchmark.

**How to interpret**:
- Same four-tier threshold as DFII5 (`<0` Accommodative, `0-1.0%` Neutral,
  `1.0-1.75%` Moderately Restrictive, `≥1.75%` Clearly Restrictive) —
  in practice DFII10 tracks DFII5 with a ~30-60 bp term premium.
- Rising DFII10 with falling DFII5 → curve steepening in real terms
  (long-end bear-steepener), often associated with growth repricing.

**Market significance**: ⭐⭐⭐ — long-duration equity valuations
(especially growth / tech / unprofitable-tech) are highly sensitive
to DFII10 moves; each +25 bp in DFII10 typically compresses Nasdaq
PE multiples.

---

## Housing / REIT (-> XLRE, XHB)

## PERMIT: New Privately-Owned Housing Units Authorized (Building Permits)

- **Series code**: PERMIT (FRED)
- **Source**: U.S. Census Bureau
- **Unit**: Thousands of units (seasonally adjusted annual rate)
- **Frequency**: Monthly
- **Publication lag**: ~2-3 weeks after reference month
- **History**: From 1960 (monthly)

**What it measures**: The number of new privately-owned housing units
authorized by building permits. A leading indicator for residential
construction activity — permits must be obtained before construction begins,
making this a forward-looking signal for housing starts, construction
employment, and building materials demand.

**How to interpret**:
- Rising -> Increasing construction pipeline. Builders expect strong demand
  and favorable economics (affordable rates, rising home prices). Leads
  housing starts by 1-2 months. Positive for homebuilders (XHB), REITs
  (XLRE), and construction-related equities.
- Falling -> Builders pulling back. Signals weakening demand, affordability
  constraints (often rising rates), or oversupply concerns. Negative for
  housing-related sectors with 4-6 week lead on housing ETF performance.

**Market significance**: ⭐⭐⭐
The strongest leading indicator in the housing complex. Building permits
represent committed capital decisions by developers who have done local
demand analysis. Permits -> construction employment -> lumber/materials demand
-> XLRE/XHB. Conference Board includes permits in the Leading Economic Index
(LEI), confirming its predictive value for the broader economy.

**Sector ETF mapping**: XLRE (Real Estate Select Sector SPDR), XHB (SPDR S&P
Homebuilders ETF)

**When to use**: Housing cycle analysis, construction sector outlook,
homebuilder earnings forecasting, LEI component tracking, XLRE/XHB allocation
timing.

**Common pitfalls**:
- Multi-family permits (5+ units) are lumpy and can distort the total.
  Single-family permits are a cleaner signal for housing demand.
- Regional variation is significant — national permits can mask diverging
  Sun Belt vs. Rust Belt trends.
- Permits do not guarantee starts. In downturns, permit holders may delay
  or cancel construction.

---

## HOUST: New Privately-Owned Housing Units Started (Housing Starts)

- **Series code**: HOUST (FRED)
- **Source**: U.S. Census Bureau
- **Unit**: Thousands of units (seasonally adjusted annual rate)
- **Frequency**: Monthly
- **Publication lag**: ~2-3 weeks after reference month
- **History**: From 1959 (monthly)

**What it measures**: The number of new privately-owned housing units on which
construction has actually begun. Confirms what permits signaled and represents
real economic activity — labor deployed, materials purchased, capital committed.

**How to interpret**:
- Rising -> Construction activity expanding. Confirms permit signals and adds
  GDP contribution through residential fixed investment. Supportive of
  building materials, labor, and housing-adjacent sectors.
- Falling -> Construction activity contracting. When starts fall below
  permits, builders are hesitating despite having approval — a bearish
  divergence signal.

**Market significance**: ⭐⭐
Less leading than permits but more definitive — starts represent actual
shovels in the ground. The permit-to-start conversion rate provides an
additional signal about builder confidence.

**Sector ETF mapping**: XLRE, XHB

**When to use**: Confirming permit trends, GDP residential investment
forecasting, construction employment outlook, housing supply pipeline
analysis.

**Common pitfalls**:
- Weather effects are significant, especially January-March in northern
  states. Seasonally adjusted data helps but does not fully eliminate this.
- Starts include both single-family and multi-family. Multi-family starts
  are driven by different economics (rental market, institutional capital).
- Revisions can be substantial. The initial print is preliminary.

---

## CSUSHPISA: S&P/Case-Shiller U.S. National Home Price Index

- **Series code**: CSUSHPISA (FRED)
- **Source**: S&P Dow Jones Indices (via FRED)
- **Unit**: Index (January 2000 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~2 months after reference month
- **History**: From 1987 (monthly)

**What it measures**: A composite measure of U.S. residential housing prices
using the repeat-sales methodology — tracking price changes of the same
properties over time. This eliminates composition bias (unlike median price,
which shifts with the mix of homes sold).

**How to interpret**:
- Rising (positive YoY) -> Home prices appreciating. Increases household
  wealth (wealth effect), supports consumer spending, and raises REIT net
  asset values. Can signal affordability erosion if rising faster than
  incomes.
- Falling (negative YoY) -> Home prices declining. Reduces household
  wealth, pressures consumer confidence, and can trigger negative equity
  for recent buyers. Bearish for XLRE and mortgage lenders.

**Market significance**: ⭐⭐
The gold standard for home price measurement but heavily lagging (2-month
reporting delay plus 3-month rolling average methodology). By the time
Case-Shiller confirms a trend, real-time indicators (Redfin, Zillow) have
already moved. Important for wealth effect analysis and REIT NAV
calculations.

**Sector ETF mapping**: XLRE, XHB

**When to use**: Housing wealth effect on consumer spending, REIT net asset
value analysis, long-term housing cycle positioning, affordability
assessment (paired with income data).

**Common pitfalls**:
- The 2-month lag plus 3-month rolling average means this series reflects
  conditions from 3.5 months ago. Do not treat it as current.
- National index masks regional divergence. The 10-City and 20-City
  composites plus individual metro indices provide more granularity.
- Repeat-sales methodology excludes new construction. In markets with
  heavy new supply, Case-Shiller may not capture the full price picture.

---

## MORTGAGE30US: 30-Year Fixed Rate Mortgage Average

- **Series code**: MORTGAGE30US (FRED)
- **Source**: Freddie Mac (Primary Mortgage Market Survey)
- **Unit**: Percent
- **Frequency**: Weekly (Thursday release)
- **Publication lag**: ~1 week
- **History**: From 1971 (weekly)

**What it measures**: The average interest rate on 30-year fixed-rate
mortgages in the U.S., the dominant mortgage product. Directly determines
monthly payment affordability for homebuyers and refinancing economics for
existing homeowners.

**How to interpret**:
- Rising -> Reduced housing affordability. Higher monthly payments constrain
  purchase demand, slow home price appreciation, and reduce refinancing
  activity. Negative for XHB and mortgage origination revenue (XLF). Also
  signals tighter financial conditions broadly.
- Falling -> Increased housing affordability. Lower payments expand the
  buyer pool, support home prices, and trigger refinancing waves. Positive
  for XHB, XLRE, and bank mortgage revenue.

**Market significance**: ⭐⭐⭐
Directly controls housing affordability for ~65% of U.S. homebuyers who use
30-year fixed mortgages. Weekly frequency provides high-resolution tracking
of financial conditions. Mortgage rates closely follow the 10-year Treasury
yield (DGS10) plus a spread that reflects credit and prepayment risk.
Movements of 50+ bps over a month are front-page housing news.

**Sector ETF mapping**: XHB, XLRE, XLF (mortgage origination revenue)

**When to use**: Housing affordability analysis, homebuilder outlook,
refinancing wave detection, financial conditions assessment, XHB/XLRE timing.

**Common pitfalls**:
- Mortgage rates track DGS10 but the spread varies. During stress periods,
  the mortgage-Treasury spread widens, so rates can rise even if Treasuries
  are stable.
- The Freddie Mac survey reflects rates offered, not rates locked. Actual
  effective rates depend on borrower credit, LTV, and points paid.
- Affordability is a function of rates AND prices AND incomes. Rates alone
  do not determine housing demand.

---

## Industrials (-> XLI)

## DGORDER: Manufacturers' New Orders: Durable Goods

- **Series code**: DGORDER (FRED)
- **Source**: U.S. Census Bureau
- **Unit**: Millions of dollars (seasonally adjusted)
- **Frequency**: Monthly
- **Publication lag**: ~4 weeks after reference month
- **History**: From 1992 (monthly)

**What it measures**: Total new orders received by manufacturers of durable
goods (items designed to last 3+ years) — including computers, appliances,
aircraft, machinery, and defense equipment. A proxy for business capital
expenditure intentions and industrial activity.

**How to interpret**:
- Rising -> Businesses are investing in equipment and capacity. Signals
  confidence in future demand and economic expansion. Positive for
  industrials (XLI), capital goods makers, and cyclical sectors.
- Falling -> Businesses are pulling back on capex. Signals caution about
  future demand. Negative for industrials with 6-8 week lead on XLI
  performance.

**Market significance**: ⭐⭐⭐
The single best capex proxy available monthly. Core durable goods (excluding
defense and aircraft) is the cleanest signal for underlying business
investment trends. Total durable goods is volatile due to lumpy aircraft and
defense orders — always examine the ex-transportation and ex-defense
sub-components. Markets react most to core capital goods orders (non-defense
ex-aircraft), which feeds directly into GDP equipment investment estimates.

**Sector ETF mapping**: XLI (Industrial Select Sector SPDR)

**When to use**: Capex cycle analysis, industrial sector earnings
forecasting, GDP equipment investment nowcasting, XLI allocation timing.

**Common pitfalls**:
- Total durable goods is extremely volatile due to large aircraft orders
  (Boeing). A single month's swing of +/-10% is common and meaningless.
  Always use ex-transportation for trend analysis.
- Defense orders are politically driven, not economically driven. Exclude
  for business cycle analysis.
- Orders are not shipments. A large order backlog can coexist with weak
  current shipments if production is capacity-constrained.
- Nominal dollars — not inflation-adjusted. In periods of high goods
  inflation, rising orders may reflect price increases, not volume growth.

**Cross-indicator notes**:
- INDPRO (in growth group) is the production counterpart to DGORDER's demand signal. Orders lead production — rising orders with flat INDPRO suggests a production ramp is coming. Falling orders with stable INDPRO suggests a pipeline drawdown.
- ISM New Orders sub-index is a survey-based leading indicator that often moves 1-2 months before DGORDER hard data confirms the direction.

---

## Energy (-> XLE)

## DCOILWTICO: Crude Oil Prices: West Texas Intermediate (WTI)

- **Series code**: DCOILWTICO (FRED)
- **Source**: U.S. Energy Information Administration (EIA)
- **Unit**: Dollars per barrel
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **History**: From 1986 (daily)

**What it measures**: The spot price of West Texas Intermediate crude oil, the
primary U.S. benchmark for oil pricing. WTI is a light, sweet crude traded at
Cushing, Oklahoma, and serves as the reference price for U.S. oil production,
refining margins, and energy sector earnings.

**How to interpret**:
- Rising -> Increased energy costs across the economy. Positive for energy
  producers (XLE) and energy-exporting countries. Negative for airlines (within
  XLI), consumer discretionary (gasoline costs), and inflation expectations.
  Persistent oil price rises feed through to CPI within 4-8 weeks.
- Falling -> Reduced energy costs. Negative for XLE but positive for consumer
  purchasing power, airlines, and manufacturing input costs. Can signal demand
  destruction (bearish for growth outlook) or supply expansion (neutral to
  positive).

**Market significance**: ⭐⭐⭐
The most watched commodity price globally. Directly drives XLE sector earnings
(energy is ~4% of S&P 500 but highly volatile). Oil moves affect inflation
expectations, central bank policy, geopolitical risk premiums, and consumer
sentiment. Daily moves of $2+ trigger cross-market repricing. Oil is also the
single largest input cost for the global transportation sector.

**Sector ETF mapping**: XLE (Energy Select Sector SPDR)

**When to use**: XLE sector analysis, inflation forecasting (oil -> CPI energy
component), consumer spending power assessment, geopolitical risk monitoring,
cross-sector margin impact (airlines, chemicals, logistics).

**Common pitfalls**:
- WTI vs Brent spread matters for global context. WTI reflects U.S. supply
  dynamics (Permian Basin output, Cushing storage levels). Brent reflects
  global marginal pricing. Divergence signals U.S.-specific supply events.
- Oil prices are driven by geopolitics (OPEC+ decisions, Middle East risk) as
  much as fundamentals. Supply disruption risk creates fat-tailed price
  distributions.
- Spot price vs. futures curve shape matters. Backwardation (spot > futures)
  signals tight current supply. Contango (spot < futures) signals surplus.

---

## DHHNGSP: Henry Hub Natural Gas Spot Price

- **Series code**: DHHNGSP (FRED)
- **Source**: U.S. Energy Information Administration (EIA)
- **Unit**: Dollars per million BTU
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **History**: From 1997 (daily)

**What it measures**: The spot price of natural gas at Henry Hub, Louisiana,
the primary U.S. natural gas pricing point. Henry Hub is the delivery point for
NYMEX natural gas futures and the reference price for ~80% of U.S. natural gas
transactions.

**How to interpret**:
- Rising -> Higher energy costs for utilities (XLU), residential/commercial
  heating, and chemicals/fertilizer production. Natural gas is the largest fuel
  source for U.S. electricity generation (~40%). Rising prices squeeze utility
  margins (regulated utilities cannot immediately pass through costs) and
  increase chemicals input costs.
- Falling -> Lower energy input costs. Positive for gas-intensive industries
  (utilities, chemicals, fertilizers). Can reflect oversupply (U.S. shale
  production growth) or weak demand (warm weather, industrial slowdown).

**Market significance**: ⭐⭐
Less globally significant than oil (natural gas markets are regional due to
LNG transport costs), but critical for U.S. utilities, chemicals, and
residential heating costs. Extreme seasonal spikes (winter heating demand)
can move utility stocks significantly. Growing LNG export capacity is
gradually connecting U.S. gas prices to global markets.

**Sector ETF mapping**: XLE (Energy Select Sector SPDR)

**When to use**: Utility cost analysis (XLU), chemicals sector input costs,
heating cost impact on consumer spending, energy sector earnings forecasting,
seasonal energy demand patterns.

**Common pitfalls**:
- Natural gas is heavily seasonal. Winter heating demand and summer cooling
  demand create predictable price cycles that are not economic signals.
- Storage levels (EIA weekly report) drive short-term price moves more than
  production data. Always check storage vs. 5-year average.
- U.S. gas prices can decouple from global LNG prices. The U.S. has
  abundant domestic supply, keeping prices structurally lower than European
  or Asian gas benchmarks.
- Weather forecasts (cold snaps, heat waves) move gas prices more than
  macroeconomic data.

---

## Financials (-> XLF)

## BAMLH0A0HYM2: ICE BofA US High Yield Index Option-Adjusted Spread

- **Series code**: BAMLH0A0HYM2 (FRED)
- **Source**: ICE Data Indices, LLC (via FRED)
- **Unit**: Percent (spread over Treasury)
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **History**: From 1997 (daily)

**What it measures**: The option-adjusted spread (OAS) of the ICE BofA US High
Yield Corporate Bond Index over the risk-free Treasury curve. This represents
the additional yield investors demand to hold below-investment-grade corporate
bonds versus Treasuries, after adjusting for embedded options (call features).
It is the single most watched credit risk indicator in U.S. fixed income.

**How to interpret**:
- Rising (widening spreads) -> Risk aversion increasing. Investors demanding
  more compensation for credit risk. Signals deteriorating credit conditions,
  potential defaults ahead, or broader risk-off sentiment. Widening spreads
  lead equity drawdowns by 2-4 weeks. A rapid widening of 100+ bps in days is
  a stress event.
- Falling (tightening spreads) -> Risk appetite improving. Investors
  comfortable with credit risk, often reflecting strong earnings, low default
  expectations, and abundant liquidity. Supportive of equities and risk assets
  broadly.

**Market significance**: ⭐⭐⭐
The single most important cross-sector risk signal. High yield spreads
aggregate thousands of credit analyst opinions into one number. Historically,
spread levels above 500 bps signal recession risk; above 800 bps signal credit
crisis. Spread widening leads equity corrections — credit markets often "see"
stress before equity markets react. Essential for financial sector analysis
(bank loan losses correlate with spread levels) and cross-sector risk
assessment.

**Sector ETF mapping**: XLF (Financial Select Sector SPDR), but this is a
cross-sector risk barometer affecting all equity sectors.

**When to use**: Risk appetite assessment, financial sector stress analysis,
credit cycle positioning, equity drawdown early warning, cross-asset allocation
decisions. Should be checked alongside T10Y2Y for a complete risk picture.

**Common pitfalls**:
- Spread levels are not absolute — the "normal" range has shifted over
  decades due to index composition changes and structural market evolution.
  Compare to 5-year and 10-year average rather than fixed thresholds.
- OAS adjusts for callable bonds but does not adjust for liquidity risk,
  which can widen spreads during market stress beyond pure credit risk.
- The index composition changes as bonds are upgraded/downgraded. Spread
  changes can reflect index rebalancing, not market sentiment.
- Very tight spreads (below 300 bps) can signal complacency rather than
  health — peak tights often precede spread widening.

---

## Technology (-> XLK)

## CES3133440001: All Employees, Semiconductor and Other Electronic Component Manufacturing

- **Series code**: CES3133440001 (FRED)
- **Source**: U.S. Bureau of Labor Statistics (BLS)
- **Unit**: Thousands of persons (seasonally adjusted)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **History**: From 1985 (monthly)

**What it measures**: Total employment in the U.S. semiconductor and
electronic component manufacturing sector (NAICS 334400). Tracks the labor
force engaged in chip fabrication, packaging, testing, and related component
manufacturing. A proxy for the health and capacity utilization of the domestic
semiconductor supply chain.

**How to interpret**:
- Rising -> Sector expanding hiring to meet demand or build new capacity
  (e.g., CHIPS Act-driven fab construction). Positive for semiconductor
  equities and supply chain health. Employment growth during fab buildout
  phases can persist for years.
- Falling -> Sector reducing headcount due to demand slowdown or
  productivity gains. Semiconductor employment tends to decline during
  inventory correction cycles (typically every 3-4 years).

**Market significance**: ⭐⭐
Employment is a lagging indicator for the semiconductor cycle — hiring
decisions follow order trends by months. However, employment data tracks
the structural capacity buildout that affects long-term supply-demand balance.
The CHIPS Act (2022) is creating a multi-year U.S. semiconductor employment
expansion that is historically unprecedented.

**Sector ETF mapping**: XLK (Technology Select Sector SPDR)

**When to use**: Semiconductor supply chain health assessment, CHIPS Act
impact monitoring, tech sector labor market analysis, long-term capacity
buildout tracking.

**Common pitfalls**:
- This measures manufacturing employment only, not the broader semiconductor
  ecosystem (design, EDA tools, equipment). NVIDIA and AMD design employees
  are not in this series.
- U.S. semiconductor manufacturing is a small fraction of global production.
  TSMC, Samsung, and other Asian fabs dominate global output. This series
  reflects U.S. domestic trends, not global semiconductor health.
- Employment changes slowly. A semiconductor downturn typically shows up in
  orders and revenue 6-12 months before layoffs appear in this series.

---

## PCUAINFOAINFO: Producer Price Index by Industry: Information Services

- **Series code**: PCUAINFOAINFO (FRED)
- **Source**: U.S. Bureau of Labor Statistics (BLS)
- **Unit**: Index (December 2009 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~2-3 weeks after reference month
- **History**: From 2007 (monthly)

**What it measures**: Producer prices for the information services sector
(NAICS 5112, 5182, 5191, etc.), covering software publishing, data processing,
hosting, and information services. Tracks input cost pressure on the
technology sector from a producer (B2B) perspective.

**How to interpret**:
- Rising -> Input cost inflation in the tech sector. Can compress margins for
  tech companies that cannot fully pass through costs. Signals pricing power
  across the software and services supply chain.
- Falling -> Deflationary pressure in tech inputs. Can reflect competitive
  dynamics, productivity gains, or demand softening. Generally positive for
  tech sector margins.

**Market significance**: ⭐
A niche indicator with limited direct market-moving impact. Useful as
supplementary context for tech sector margin analysis but rarely watched
by market participants in isolation. More valuable when combined with
sector-specific earnings data.

**Sector ETF mapping**: XLK (Technology Select Sector SPDR)

**When to use**: Tech sector cost structure analysis, software pricing
trend monitoring, margin pressure assessment for tech companies.

**Common pitfalls**:
- The information services PPI covers a narrow definition of tech. Cloud
  infrastructure, SaaS pricing, and AI compute costs are partially but not
  fully captured.
- Services price indices are methodologically challenging — quality
  adjustment for software and digital services is an open problem in
  economic measurement.
- Small absolute moves in this index matter less than the YoY rate of change.

---

## Consumer (-> XLY, XLP)

## RSAFS: Advance Retail Sales: Retail and Food Services, Total

- **Series code**: RSAFS (FRED)
- **Source**: U.S. Census Bureau
- **Unit**: Millions of dollars (seasonally adjusted)
- **Frequency**: Monthly
- **Publication lag**: ~2 weeks after reference month
- **History**: From 1992 (monthly)

**What it measures**: Total monthly retail and food services sales, the
broadest available measure of consumer spending activity. Consumer spending
represents ~68% of U.S. GDP, making retail sales the most important real-time
spending indicator.

**How to interpret**:
- Rising (positive MoM) -> Consumer spending expanding. Positive for
  consumer discretionary (XLY) and the broader economy. Sustained strong
  retail sales support GDP growth expectations and corporate revenue
  forecasts.
- Falling (negative MoM) -> Consumer spending weakening. Negative for XLY.
  Persistent weakness signals consumer pullback, which given the ~68% GDP
  share of consumption, threatens broader economic growth. When discretionary
  spending weakens while staples hold, it signals XLY -> XLP rotation.

**Market significance**: ⭐⭐⭐
One of the most market-moving monthly releases. Retail sales provide the
first hard data on consumer spending each month, predating the more
comprehensive PCE spending data by several weeks. Strong/weak prints
trigger immediate repricing of consumer sector equities and GDP nowcasts.
The "control group" (excluding autos, gas, building materials, food services)
feeds directly into GDP consumption estimates.

**Sector ETF mapping**: XLY (Consumer Discretionary Select Sector SPDR),
XLP (Consumer Staples Select Sector SPDR)

**When to use**: Consumer spending trend analysis, XLY vs XLP sector
rotation, GDP nowcasting (control group -> PCE goods), retailer earnings
forecasting, consumer health assessment.

**Common pitfalls**:
- Retail sales are nominal (not inflation-adjusted). During high-inflation
  periods, rising nominal sales may reflect price increases rather than
  volume growth. Deflate by CPI to get real spending trends.
- Auto sales are lumpy and can distort the headline. Always check
  ex-auto for underlying trend.
- Retail sales exclude services (~65% of consumer spending). A strong
  service economy can coexist with weak retail sales.
- Revisions to prior months are common and can be substantial. The
  advance estimate is just that — advance.

---

## UMCSENT: University of Michigan Consumer Sentiment Index

- **Series code**: UMCSENT (FRED)
- **Source**: University of Michigan, Surveys of Consumers
- **Unit**: Index (1966Q1 = 100)
- **Frequency**: Monthly (preliminary mid-month, final end-of-month)
- **Publication lag**: ~2 weeks (preliminary), ~4 weeks (final)
- **History**: From 1952 (monthly)

**What it measures**: A composite index of consumer confidence based on
telephone surveys of ~500 U.S. households, covering assessments of personal
finances, business conditions, and buying conditions. The forward-looking
expectations component leads actual spending by 1-2 months.

**How to interpret**:
- Rising -> Consumers feel better about their financial situation and the
  economy. Typically leads increases in discretionary spending (XLY). The
  expectations sub-index is the more leading component.
- Falling -> Consumers are pessimistic. Leads pullbacks in big-ticket
  discretionary purchases (autos, appliances, vacations). Sustained declines
  below 70 historically correlate with recession or near-recession conditions.

**Market significance**: ⭐⭐
The preliminary reading (released mid-month) moves markets because it
precedes most hard data releases. The inflation expectations component
(1-year and 5-10 year ahead) is closely watched by the Federal Reserve as
an input to monetary policy decisions. Sentiment surveys are "soft data"
that can diverge from hard spending data for extended periods.

**Sector ETF mapping**: XLY, XLP

**When to use**: Forward-looking consumer spending outlook, inflation
expectations tracking (Fed monitors this), XLY vs XLP rotation timing,
recession probability assessment (sustained readings below 70).

**Common pitfalls**:
- Sentiment-spending disconnect: consumers can feel bad but spend anyway
  (and vice versa). The correlation between sentiment and actual spending
  has weakened post-2020 as excess savings decoupled the two.
- Political partisanship increasingly influences responses. Republican
  sentiment rises sharply after Republican election wins (and vice versa),
  independent of economic fundamentals.
- Small sample size (~500) means margin of error is substantial. Do not
  over-interpret month-to-month changes of 2-3 points.
- The Conference Board Consumer Confidence Index (based on 3,000+ responses
  and mailed surveys) often diverges from Michigan. Different methodology,
  different signal. Neither is strictly better.

---

## Producer Prices (cross-sector)

## PCUOMFGOMFG: Producer Price Index by Industry: Total Manufacturing Industries

- **Series code**: PCUOMFGOMFG (FRED)
- **Source**: U.S. Bureau of Labor Statistics (BLS)
- **Unit**: Index (December 2003 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~2-3 weeks after reference month
- **History**: From 1985 (monthly)

**What it measures**: Producer prices for the total manufacturing sector,
covering the prices received by domestic producers for their output across all
manufacturing industries. PPI Manufacturing measures upstream price pressure —
what producers charge before goods reach consumers. It is the broadest
manufacturing-specific price gauge.

**How to interpret**:
- Rising (accelerating YoY) -> Upstream inflation pressure building.
  Manufacturers are paying more for inputs and/or passing through higher
  prices. Leads CPI goods inflation by 3-6 months as producer costs flow
  through to consumer prices. Signals potential margin compression for
  downstream companies that cannot pass through costs.
- Falling (decelerating YoY) -> Upstream disinflation. Input costs easing
  for manufacturers. Leads CPI goods disinflation. Positive for downstream
  margins and signals reduced inflation pressure for the Fed.

**Market significance**: ⭐⭐
PPI Manufacturing is an important leading indicator for CPI goods inflation
and corporate margin trends. While less market-moving than CPI itself, PPI
provides the earliest signal of pipeline inflation pressure. The PPI -> CPI
transmission typically takes 3-6 months, giving investors advance notice of
inflation trends. Margin analysts use PPI vs CPI divergence to assess pricing
power across industries.

**Sector ETF mapping**: Cross-sector. Not mapped to a single ETF. Relevant
for all goods-producing sectors (XLI, XLB, XLK hardware) and as a leading
indicator for CPI-sensitive positioning.

**When to use**: Inflation pipeline analysis (PPI -> CPI transmission),
corporate margin pressure assessment, manufacturing cost environment,
Fed policy outlook (PPI often previews CPI trends), cross-sector input cost
monitoring.

**Common pitfalls**:
- PPI measures prices received by producers, not prices paid by producers.
  For input cost pressure, look at PPI for intermediate demand or commodity
  price indices.
- Like CPI, PPI is an index level. You must compute YoY or MoM percentage
  change for meaningful analysis.
- The PPI -> CPI transmission lag varies by industry. Food and energy pass
  through quickly (weeks). Durable goods pass through slowly (months).
  Services PPI-to-CPI transmission is weakest.
- PPI excludes imports. In a globalized supply chain, import prices (tracked
  by BLS Import Price Index) can matter more than domestic PPI for some
  sectors.

---

## Sources

Primary sources referenced in this document:

### Yield Curve & Recession Prediction
- Estrella, A. & Mishkin, F.S. "The Yield Curve as a Predictor of U.S. Recessions." Federal Reserve Bank of New York, Current Issues in Economics and Finance, Vol. 2, No. 7. https://www.newyorkfed.org/research/current_issues/ci2-7.html

### Macro Announcement Market Impact
- Andersen, T.G., Bollerslev, T., Diebold, F.X., & Vega, C. "Micro Effects of Macro Announcements: Real-Time Price Discovery in Foreign Exchange." NBER Working Paper No. 8959. https://www.nber.org/papers/w8959
- Fleming, M.J. & Remolona, E.M. "Price Formation and Liquidity in the U.S. Treasury Market." Federal Reserve Bank of New York Staff Reports, 1999.

### Treasury as Global Benchmark
- IMF Global Financial Stability Report, October 2024, Chapter 1. https://www.imf.org/en/Publications/GFSR

### Fed Policy & Inflation Target
- Federal Reserve Board. "Why does the Federal Reserve aim for inflation of 2 percent over the longer run?" https://www.federalreserve.gov/faqs/economy_14400.htm
- Note: The Fed's official 2% target uses PCE inflation, not CPI. CPI is widely monitored but is not the policy target.

### Federal Funds Rate Global Spillovers
- BIS Working Papers No. 757, "Explaining Monetary Spillovers: The Matrix Reloaded." https://www.bis.org/publ/work757.pdf
- BIS Working Papers No. 719, "Channels of US Monetary Policy Spillovers." https://www.bis.org/publ/work719.pdf

### NBER Recession Dating
- NBER Business Cycle Dating Committee. "Business Cycle Dating Procedure: Frequently Asked Questions." https://www.nber.org/research/business-cycle-dating
- Note: NBER explicitly rejects the "two consecutive negative GDP quarters" heuristic.

### Industrial Production
- Federal Reserve Board. "Industrial Production and Capacity Utilization — G.17 Release." https://www.federalreserve.gov/releases/g17/current/default.htm

### GDP Composition
- U.S. Bureau of Economic Analysis. "GDP by Industry." https://www.bea.gov/data/gdp/gdp-industry

### Sector-Level Indicators
- FRED Housing Data: https://fred.stlouisfed.org/categories/97
- FRED Producer Price Indexes: https://fred.stlouisfed.org/categories/31
- ICE BofA Credit Spreads: via FRED (sourced from ICE Data Indices, LLC)
- University of Michigan Consumer Sentiment: https://fred.stlouisfed.org/series/UMCSENT
- Freddie Mac Primary Mortgage Market Survey: https://www.freddiemac.com/pmms
- U.S. Census Bureau, New Residential Construction: https://www.census.gov/construction/nrc/index.html
- U.S. Census Bureau, Advance Monthly Retail Trade Survey: https://www.census.gov/retail/index.html
- S&P/Case-Shiller Home Price Indices: https://www.spglobal.com/spdji/en/index-family/indicators/sp-corelogic-case-shiller/
- U.S. Energy Information Administration: https://www.eia.gov/petroleum/ and https://www.eia.gov/naturalgas/
