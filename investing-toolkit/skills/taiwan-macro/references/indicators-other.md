# Other / 其他 — Forex, Money Supply

---

## twdusd: 新臺幣對美元匯率 TWD/USD Exchange Rate

- **Item Code**: BP01D01
- **Source**: CBC (Central Bank) — **Chinese endpoint** (English version stopped at 2012)
- **Unit**: NTD per 1 USD
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **API**: `https://cpx.cbc.gov.tw/API/DataAPI/Get?FileName=BP01D01`

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

## m2: 貨幣總計數 M2 Monetary Aggregates M2

- **Item Code**: EF15M01en
- **Source**: CBC (Central Bank)
- **Unit**: NTD millions
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **API**: `https://cpx.cbc.gov.tw/API/DataAPI/Get?FileName=EF15M01en`

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

## reserve-money: 準備貨幣 Reserve Money

- **Item Code**: EF11M01en
- **Source**: CBC (Central Bank)
- **Unit**: NTD millions
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **API**: `https://cpx.cbc.gov.tw/API/DataAPI/Get?FileName=EF11M01en`

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

**Common pitfalls**:
- Reserve money changes can reflect required reserve ratio adjustments
  (a policy tool) rather than market operations.
- Seasonal patterns around Lunar New Year (currency demand spike) and
  tax payment dates.

---

## financial-sa: 季調金融指標 Seasonally Adjusted Financial Indicators

- **Item Code**: EF10M01en
- **Source**: CBC (Central Bank)
- **Unit**: NTD millions (seasonally adjusted)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **API**: `https://cpx.cbc.gov.tw/API/DataAPI/Get?FileName=EF10M01en`

**What it measures**: Seasonally adjusted monetary and financial aggregates
published by the CBC. Removes seasonal patterns (Lunar New Year, dividend
season, tax payments) from monetary statistics.

**How to interpret**:
- Use for trend analysis of monetary conditions. Seasonal adjustment makes
  month-to-month comparisons more meaningful than raw M2 data.

**Market significance**: ⭐
Technical complement to raw M2 data. Useful for econometric analysis and
monetary policy assessment when seasonal noise must be removed.

**Common pitfalls**:
- Seasonal adjustment methodology can be revised, creating revisions to
  historical data.
- During structural breaks (pandemic, policy regime changes), seasonal
  adjustment may produce misleading smoothing.
