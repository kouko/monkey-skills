# US Macro Indicators — FRED Series Reference

Comprehensive reference for the 8 FRED series used by the `us-macro` skill.
Each entry covers units, frequency, publication lag, interpretation guidance,
and common pitfalls.

---

## Rates

### T10Y2Y: 10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity

- **Unit**: Percent
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **Source**: Federal Reserve Board of Governors

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

### DGS10: Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity

- **Unit**: Percent
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **Source**: Federal Reserve Board of Governors

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

### DGS2: Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity

- **Unit**: Percent
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **Source**: Federal Reserve Board of Governors

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

### FEDFUNDS: Effective Federal Funds Rate

- **Unit**: Percent
- **Frequency**: Monthly (average of daily values)
- **Publication lag**: ~1 week after month-end
- **Source**: Federal Reserve Bank of New York

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

### CPIAUCSL: Consumer Price Index for All Urban Consumers: All Items in U.S. City Average

- **Unit**: Index (1982-84 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~2-3 weeks after reference month
- **Source**: U.S. Bureau of Labor Statistics (BLS)

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

### CPILFESL: Consumer Price Index for All Urban Consumers: All Items Less Food and Energy in U.S. City Average

- **Unit**: Index (1982-84 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~2-3 weeks after reference month
- **Source**: U.S. Bureau of Labor Statistics (BLS)

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

### GDPC1: Real Gross Domestic Product

- **Unit**: Billions of chained 2017 dollars
- **Frequency**: Quarterly
- **Publication lag**: ~1 month after quarter-end (advance estimate)
- **Source**: U.S. Bureau of Economic Analysis (BEA)

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

### INDPRO: Industrial Production: Total Index

- **Unit**: Index (2017 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **Source**: Federal Reserve Board of Governors

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
