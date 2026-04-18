# Trade / 무역

---

## current-account: 경상수지 / Current Account

- **Series code**: K351 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Million USD
- **Frequency**: Monthly
- **Publication lag**: ~6 weeks after reference month
- **History**: From 1980

**What it measures**: Korea's current account balance — the broadest measure
of trade performance, covering goods trade, services trade, primary income
(investment income), and secondary income (transfers). Positive = surplus,
negative = deficit.

**How to interpret**:
- Surplus (positive) → Korea earning more from foreign trade and investment
  than it spends. Structural surplus reflects export competitiveness. Provides
  FX support for KRW.
- Deficit (negative) → Korea spending more abroad than it earns. Puts
  depreciation pressure on KRW. Rare for Korea outside of energy price
  shocks and global recessions.

**Market significance**: ⭐⭐⭐
Korea's current account is a key driver of KRW/USD. Korea has maintained
a current account surplus since 1998 (post-Asian Financial Crisis). The
surplus reflects Korea's export-oriented economic model. When the surplus
narrows significantly or turns to deficit (as briefly in early 2022 during
the energy price spike), KRW depreciates.

**When to use**: KRW fundamental support assessment, export competitiveness tracking, balance of payments analysis, semiconductor cycle impact gauge.

**Korea-specific context**:
- Korea's current account surplus is primarily driven by the goods trade
  balance (merchandise exports - imports). The services balance is typically
  in deficit (travel, transportation, IP royalties paid abroad).
- The goods trade surplus has a strong semiconductor component. When memory
  chip prices are high, Korea's goods surplus expands dramatically. When
  chip prices crash (2019, 2023), the surplus narrows.
- Korea's current account is also affected by: (1) oil imports (~$100B+/year),
  (2) Korean tourists spending abroad (services deficit), and (3) overseas
  investment income.
- The monthly current account data from the BOK is released ~6 weeks after
  the reference month. For a faster signal, watch the Korea Customs Service's
  preliminary trade data (released within 15 days), which is not available
  via ECOS-KEYSTAT.

**Common pitfalls**:
- Current account ≠ trade balance. The current account includes services
  and income, not just goods trade.
- Monthly data is volatile. Look at 3-month or 12-month moving averages
  for trend analysis.
- The USD denomination means that KRW/USD exchange rate fluctuations affect
  the reported value even when underlying trade volumes are stable.

---

## terms-of-trade: 순상품교역조건지수 / Terms of Trade Index

- **Series code**: K360 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Index (base year varies)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **History**: From 1980

**What it measures**: The ratio of export prices to import prices
(export PI / import PI * 100). Measures how many units of imports Korea
can purchase per unit of exports — the country's purchasing power in
international trade.

**How to interpret**:
- Rising (improving terms of trade) → Korea gets more imports per unit
  exported. Either export prices are rising faster than import prices,
  or import prices are falling faster than export prices. Positive for
  national income and corporate profits.
- Falling (deteriorating terms of trade) → Korea gets less per unit
  exported. Negative for national income. Common during oil price spikes
  (import prices surge while export prices lag).

**Market significance**: ⭐⭐
An underappreciated indicator that captures Korea's vulnerability to
commodity price shocks. Deteriorating terms of trade explain why Korea can
have rising export volumes but shrinking trade surplus during commodity
price spikes.

**When to use**: Commodity shock vulnerability assessment, purchasing power analysis, oil price impact proxy for Korea, export margin tracking.

**Korea-specific context**:
- Korea is structurally vulnerable to terms-of-trade shocks because it
  imports nearly all energy and raw materials but exports manufactured goods
  whose prices are more stable or subject to competitive pressure.
- During oil price spikes: import PI rises sharply (crude oil) while export
  PI rises modestly (manufactured goods) → terms of trade deteriorate → trade
  surplus shrinks → KRW pressure.
- Improving semiconductor prices can offset commodity cost pressure because
  semiconductors are a large share of export PI.
- The terms of trade index is inversely correlated with oil prices for Korea.

**Common pitfalls**:
- Terms of trade measures prices, not volumes. A country can have improving
  terms of trade but a declining trade balance if export volumes fall enough.
- The base year for the index varies. Focus on direction and YoY change,
  not absolute level.
- The index is derived from export PI / import PI. If both indices are
  from the same base year, the ratio is straightforward. Check for base
  year consistency.

---

## goods-exports: 재화수출 / Goods Exports (national accounts basis)

- **Series code**: K462 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: QoQ growth % (SA, constant prices)
- **Frequency**: Quarterly
- **Publication lag**: ~8 weeks after quarter-end (national accounts release)
- **History**: From 2000

**What it measures**: Quarterly change in **goods exports** from the
national accounts (GDP decomposition). Distinct from KITA's monthly customs
trade data — this is the expenditure-side GDP component used to calculate
net exports' contribution to GDP growth.

**How to interpret**:
- Positive QoQ SA → Goods exports contributing positively to Q GDP growth
- Negative QoQ SA → Export drag on GDP (seen 2022-2024 during semiconductor
  cycle downturn)
- Trend deceleration → Early signal of KR manufacturing profit squeeze
  (Samsung / SK Hynix earnings)

**Market significance**: ⭐⭐⭐
Korea's export-to-GDP ratio is among the world's highest (~40%). Goods
exports are the single most important cyclical component. Sustained
negative prints historically coincide with KOSPI earnings recessions.

**When to use**: GDP decomposition, semiconductor cycle tracking
(semiconductors = ~20% of goods exports), KOSPI earnings forecasting.

**Korea-specific context**:
- Semiconductors (~20%), autos (~10%), petrochemicals (~10%), ships (~5%),
  display (~5%) dominate goods exports.
- Quarterly national accounts basis differs from KITA monthly customs
  data — NA includes both goods AND services and is seasonally adjusted
  at constant prices.

**Common pitfalls**:
- Quarterly, not monthly — cannot be used for MoM signal. For monthly
  exports, MOTIE/KITA publish customs-based exports not currently in
  our skill (candidate for future addition if direct ECOS API is added).
- The "GDP-basis" export value differs from headline customs exports
  (value + timing + coverage differences).
