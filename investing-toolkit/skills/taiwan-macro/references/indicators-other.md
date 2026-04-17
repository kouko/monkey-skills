# Other / 其他 — Forex, Money Supply

---

## twdusd: 新臺幣對美元匯率 / TWD/USD Exchange Rate

- **Series code**: BP01D01 (CBC API)
- **Source**: CBC (Central Bank) — **Chinese endpoint** (English version stopped at 2012)
- **Unit**: NTD per 1 USD
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **History**: From 2000 (daily)

**What it measures**: The TWD/USD spot exchange rate as published by the
Central Bank. This is the most important exchange rate for Taiwan's economy,
reflecting capital flows, trade dynamics, and CBC intervention activity.

**How to interpret**:
- Rising (NTD value rises per USD = TWD depreciating) → NTD weakening against
  USD. Positive for exporters (TSMC, electronics) in NTD revenue terms.
  Negative for importers (energy, raw materials). Can signal capital outflows
  or risk-off sentiment. CBC may intervene to slow depreciation.
- Falling (NTD value falls per USD = TWD appreciating) → NTD strengthening.
  Negative for exporters' NTD revenue. Positive for importers and consumers.
  Can signal capital inflows (e.g., foreign investment in Taiwan tech stocks).

**Market significance**: ⭐⭐⭐
The single most watched price for Taiwan's export-dependent economy. The CBC
actively manages TWD volatility through foreign exchange market intervention
(Taiwan is regularly on the US Treasury's currency monitoring list for this
reason). TWD moves directly affect TAIEX earnings estimates — a 1% TWD
depreciation can add ~0.5-1% to aggregate TAIEX EPS.

**When to use**: TWD FX risk monitoring, export competitiveness assessment, CBC intervention analysis, cross-border capital flow tracking.

**Taiwan-specific context**:
- The CBC does not have an explicit exchange rate target but practices "smooth
  intervention" to prevent excessive volatility. Taiwan's foreign exchange
  reserves (~$570B as of 2025) are among the world's largest relative to GDP.
- TWD is not freely floating — it is a "managed float." The CBC's intervention
  is well-documented by the US Treasury semi-annual FX report.
- The English version of this dataset (`BP01D01en`) stopped updating in 2012.
  Always use the Chinese version (`BP01D01`) for current data.
- TWD is also influenced by semiconductor demand cycles. Strong chip demand →
  foreign capital inflows to buy TSMC → TWD appreciation pressure.

**Common pitfalls**:
- Higher number = weaker TWD (unlike EUR/USD where higher = stronger EUR).
  TWD/USD is quoted as "how many NTD per 1 USD."
- Daily data includes weekdays only. Missing dates are holidays/weekends.
- CBC intervention can create artificial stability that masks underlying
  pressure. Watch foreign reserve changes for intervention signals.
- The data is from the Chinese-language API endpoint. Column headers and
  metadata may be in Chinese.

---

## m2: 貨幣總計數 M2 / Monetary Aggregates M2

- **Series code**: EF15M01en (CBC API)
- **Source**: CBC (Central Bank)
- **Unit**: NTD millions
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **History**: From 2000 (monthly)

**What it measures**: Taiwan's broad money supply (M2), including currency in
circulation, demand deposits, time deposits, savings deposits, and money
market mutual funds. The broadest standard monetary aggregate.

**How to interpret**:
- Rising (positive YoY growth) → Liquidity expanding. Supports asset prices
  and economic activity. The CBC's target zone for M2 growth is typically
  2.5%-6.5% YoY. Growth above the target zone may signal excess liquidity.
- Falling (decelerating YoY growth) → Liquidity tightening. Can signal
  credit contraction or capital outflows. Growth below the target zone
  may prompt CBC easing.

**Market significance**: ⭐⭐
Important for understanding monetary conditions and liquidity. The CBC
explicitly sets an M2 growth target range and references it in policy
statements. However, M2 growth rates have become less predictive of
economic activity in recent decades (similar to global trends).

**When to use**: Liquidity conditions tracking, CBC monetary aggregate target monitoring (2.5%-6.5%), asset price support assessment.

**Taiwan-specific context**:
- The CBC publishes an annual M2 growth target range (e.g., 2.5%-6.5%).
  This is one of the few central banks that still explicitly targets
  monetary aggregates.
- Taiwan's M2 growth is influenced by foreign exchange reserve accumulation
  — CBC intervention to prevent TWD appreciation injects NTD liquidity,
  expanding M2. This creates a structural upward bias in M2 growth that
  does not necessarily reflect domestic credit conditions.
- High savings rate in Taiwan means M2/GDP ratio is very high (~2.5x)
  compared to the US (~0.9x). This reflects household preference for bank
  deposits over equity/bond investment.

**Common pitfalls**:
- M2 level is in NTD millions. The absolute number is large. Focus on
  YoY growth rate for meaningful analysis.
- M2 growth driven by foreign reserve accumulation (CBC intervention) has
  different economic implications than M2 growth driven by domestic credit
  expansion.
- Seasonal patterns exist (Lunar New Year, corporate dividend season).

---

## reserve-money: 準備貨幣 / Reserve Money

- **Series code**: EF11M01en (CBC API)
- **Source**: CBC (Central Bank)
- **Unit**: NTD millions
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **History**: From 2000 (monthly)

**What it measures**: The monetary base — currency in circulation plus
commercial bank reserves held at the CBC. This is the narrow money supply
directly controlled by the central bank.

**How to interpret**:
- Rising → CBC injecting base money into the banking system. Expansionary.
  Provides raw material for credit multiplication.
- Falling → CBC draining reserves. Contractionary.

**Market significance**: ⭐
A technical monetary indicator primarily of interest to banking system
analysts. Less directly market-moving than M2 or the policy rate, but
useful for understanding CBC's balance sheet operations.

**When to use**: CBC balance sheet operations tracking, base money supply analysis, banking system liquidity gauge.

**Common pitfalls**:
- Reserve money changes can reflect required reserve ratio adjustments
  (a policy tool) rather than market operations.
- Seasonal patterns around Lunar New Year (currency demand spike) and
  tax payment dates.

---

## financial-sa: 季調金融指標 / Seasonally Adjusted Financial Indicators

- **Series code**: EF10M01en (CBC API)
- **Source**: CBC (Central Bank)
- **Unit**: NTD millions (seasonally adjusted)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **History**: From 2000 (monthly)

**What it measures**: Seasonally adjusted monetary and financial aggregates
published by the CBC. Removes seasonal patterns (Lunar New Year, dividend
season, tax payments) from monetary statistics.

**How to interpret**:
- Use for trend analysis of monetary conditions. Seasonal adjustment makes
  month-to-month comparisons more meaningful than raw M2 data.

**Market significance**: ⭐
Technical complement to raw M2 data. Useful for econometric analysis and
monetary policy assessment when seasonal noise must be removed.

**When to use**: Seasonally adjusted monetary trend analysis, CBC policy assessment removing seasonal noise.

**Common pitfalls**:
- Seasonal adjustment methodology can be revised, creating revisions to
  historical data.
- During structural breaks (pandemic, policy regime changes), seasonal
  adjustment may produce misleading smoothing.

---

## fx-reserves: 外匯存底 / FX Reserves

- **Series code**: sid=t.10 (stat.gov.tw)
- **Source**: statgov (stat.gov.tw)
- **Unit**: Billions USD
- **Frequency**: Monthly
- **Publication lag**: ~1-2 weeks after reference month

**What it measures**: Taiwan's official foreign exchange reserves held by the
Central Bank. Reflects cumulative CBC intervention in the FX market, trade
surpluses converted into reserves, and valuation changes on reserve assets.
Taiwan consistently ranks among the top 5-6 global reserve holders relative
to GDP.

**How to interpret**:
- Rising → CBC accumulating reserves, likely through FX market intervention
  to slow TWD appreciation. Signals capital inflows and/or trade surpluses
  being sterilized. Positive for TWD stability but may indicate artificially
  suppressed TWD.
- Falling → CBC drawing down reserves, possibly to defend TWD during capital
  outflow episodes. Sustained declines signal external pressure.

**Market significance**: ⭐⭐
Taiwan's ~$570B foreign reserves (as of 2025) serve as a proxy for CBC
intervention activity. Large monthly changes (>$5B) often coincide with
significant TWD moves and are flagged in the US Treasury semi-annual FX
report. Reserves relative to GDP are among the highest globally, providing
a substantial buffer but also drawing scrutiny from trading partners.

**When to use**: CBC intervention magnitude proxy, Taiwan external position assessment, financial stability gauge, TWD support capacity analysis.

**Taiwan-specific context**:
- Taiwan's reserves-to-GDP ratio (~150%) is one of the highest in the world,
  reflecting decades of current account surpluses and CBC intervention.
- The US Treasury monitors Taiwan's reserve accumulation as part of its
  currency manipulation criteria. Net FX purchases exceeding 2% of GDP
  over 12 months is one of three criteria.
- Reserve changes net of valuation effects are a better measure of CBC
  intervention than headline reserve changes. USD strength/weakness affects
  the non-USD portion of reserves.

**Common pitfalls**:
- Monthly reserve changes reflect both intervention and valuation effects.
  A reserve increase during broad USD weakness may reflect mark-to-market
  gains on EUR/JPY-denominated assets, not active intervention.
- The stat.gov.tw data is in billions USD. Do not confuse with NTD-denominated
  figures from other sources.

---

## m2-yoy: M2 年增率 / M2 YoY Growth Rate

- **Series code**: sid=t.10 (stat.gov.tw)
- **Source**: statgov (stat.gov.tw)
- **Unit**: Percent (%) — year-over-year growth rate
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month

**What it measures**: The year-over-year growth rate of Taiwan's broad money
supply (M2), sourced from stat.gov.tw. This is the growth rate version of
the CBC's M2 level data (preset: m2), and is the metric the CBC explicitly
targets with its annual growth target range.

**How to interpret**:
- Above target range (>6.5%) → Excess liquidity. Supports asset prices but
  may signal inflationary risk or excessive capital inflows. CBC may consider
  tightening.
- Within target range (2.5%-6.5%) → Monetary conditions aligned with CBC
  objectives. Neutral signal.
- Below target range (<2.5%) → Tight liquidity. May signal credit contraction,
  capital outflows, or insufficient monetary accommodation. CBC may consider
  easing.

**Market significance**: ⭐⭐
The CBC's explicit M2 growth target makes this metric a direct policy
benchmark. Deviations from the target range are referenced in CBC board
meeting statements and influence market expectations for policy changes.
The YoY format removes level effects and seasonal distortions, making it
the preferred analytical metric over the raw M2 level.

**When to use**: Monetary growth trend analysis, CBC target range monitoring, credit cycle positioning, liquidity expansion/contraction tracking.

**Taiwan-specific context**:
- The CBC is one of the few central banks globally that still explicitly
  targets monetary aggregates. The annual target range (e.g., 2.5%-6.5%)
  is published at the start of each year.
- M2 growth in Taiwan is structurally influenced by CBC FX intervention —
  buying USD to slow TWD appreciation injects NTD, expanding M2. This means
  M2 growth can overstate domestic credit conditions during periods of heavy
  intervention.
- The stat.gov.tw version provides a longer continuous history than
  calculating YoY from the CBC's M2 level data, and avoids base-period
  revision complications.

**Common pitfalls**:
- M2 YoY growth driven by FX reserve accumulation has different implications
  than growth driven by domestic bank lending. Decompose when possible.
- The CBC target range is set annually and may shift. Always check the
  current year's target before interpreting deviations.
- Base effects from unusual periods (pandemic stimulus, large capital flows)
  can distort YoY comparisons for up to 12 months.

---

## taiex: 加權股價指數 / TAIEX Monthly Average

- **Series code**: sid=t.10 (stat.gov.tw)
- **Source**: statgov (stat.gov.tw)
- **Unit**: Index points (monthly average)
- **Frequency**: Monthly
- **Publication lag**: ~1-2 weeks after reference month

**What it measures**: The Taiwan Capitalization Weighted Stock Index (TAIEX)
monthly average, sourced from stat.gov.tw. TAIEX is the primary benchmark
for Taiwan's equity market, covering all listed stocks on the Taiwan Stock
Exchange. The monthly average smooths daily volatility for macro analysis.

**How to interpret**:
- Rising → Equity market appreciating. Signals positive investor sentiment,
  capital inflows, and typically aligns with economic expansion or
  semiconductor upcycle.
- Falling → Equity market declining. Signals risk-off sentiment, capital
  outflows, or deteriorating economic outlook. TAIEX is particularly
  sensitive to global tech/semiconductor demand shifts.

**Market significance**: ⭐⭐⭐
TAIEX is one of the 9 components of Taiwan's official business cycle signal
(景氣燈號) and a leading indicator component. It reflects both domestic
economic conditions and global semiconductor demand (TSMC alone represents
~30% of TAIEX market cap). Foreign investor flows — tracked daily by the
TWSE — are a major driver of both TAIEX direction and TWD movements.

**When to use**: Taiwan equity market benchmark, semiconductor cycle proxy, foreign flow tracking, Buffett indicator computation.

**Taiwan-specific context**:
- TAIEX is heavily concentrated in semiconductors and electronics (~60-70%
  of index weight). TSMC alone is ~30%. This makes TAIEX effectively a
  leveraged bet on the global semiconductor cycle.
- Foreign investors hold ~40% of TWSE market cap. Their net buy/sell flows
  are published daily and directly affect both TAIEX and TWD (foreign
  buying = USD→TWD conversion = TWD appreciation pressure).
- The monthly average from stat.gov.tw is useful for macro analysis (Buffett
  indicator = TAIEX market cap / GDP, cycle analysis) where daily noise is
  unwanted. For real-time market tracking, use daily TAIEX data from other
  sources.
- TAIEX has a daily price limit of ±10%, which can dampen extreme moves
  compared to markets without limits.

**Common pitfalls**:
- The monthly average can mask significant intra-month volatility. A month
  with a sharp V-shaped recovery may show a flat average.
- TAIEX concentration in semiconductors means it may not reflect the broader
  Taiwan economy. Domestic-oriented sectors are underrepresented.
- The stat.gov.tw data is monthly frequency only. Do not use for short-term
  trading analysis.
