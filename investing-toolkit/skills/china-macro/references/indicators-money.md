# Money & Credit / 货币与信贷

---

## m2-yoy: M2 同比 / M2 Money Supply YoY

- **Series code**: akshare:macro_china_money_supply (column: 货币和准货币(M2)-同比增长)
- **Source**: 中国人民银行 PBOC via akshare
- **Unit**: Percent (%)
- **Frequency**: Monthly
- **Publication lag**: ~10-15 days after reference month
- **History**: From the 1990s (300+ observations)

**What it measures**: Year-over-year growth in M2 — broad money supply
comprising currency in circulation, demand deposits, savings deposits,
and term deposits. The most-watched Chinese monetary aggregate and a
core monetary-policy indicator.

**How to interpret**:
- Rising → Monetary easing transmitting. Bank credit expanding,
  household/corporate cash holdings growing. Historically associated
  with equity-market rallies (when credit flows to real economy).
- Falling → Tightening or weak credit demand. Sub-9% readings during
  2024-2025 have signalled a combination of PBOC caution on CNY and
  weak corporate credit demand (property, LGFV deleveraging).
- The "M2 growth vs nominal GDP growth" relationship: historical norm
  is M2 growing ~1-2 percentage points faster than nominal GDP. When
  M2 and nominal GDP move together at ~5-6%, credit is "balanced."

**Market significance**: ⭐⭐⭐
A foundational monetary indicator. Moves CSI 300, property-sector
equities, CNY, and CGB yields. Sustained sub-9% M2 prints are
interpreted as restrictive given China's growth ambitions; above-10%
prints signal PBOC is accommodating stimulus demands.

**When to use**: Monetary-stance framing, stimulus-effectiveness
assessment, credit-cycle timing, property-sector liquidity read.

**China-specific context**:
- **PBOC dropped the explicit M2 growth target in 2018** after years
  of setting annual targets (e.g., "M2 growth of ~12%"). Current
  guidance is qualitative: M2 should grow "around nominal GDP growth"
  plus a margin.
- M2 components (household deposits, corporate deposits, non-financial
  institution deposits) each tell a different story. Household
  deposit surges during 2022-2023 reflected precautionary saving, not
  investment — a bearish signal despite surface-level M2 strength.
- M2 is narrower than AFRE (社融) — does not capture bond issuance,
  equity financing, or shadow-banking lending. See `shrzgm` below.
- Base effects can swing YoY readings 1-2 percentage points in a given
  month; use 3-month moving averages for trend.

**Common pitfalls**:
- M2 growth alone is insufficient to assess monetary conditions —
  cross-reference with AFRE growth, new loans, and interbank rates
  (SHIBOR, DR007).
- "Deposit migration" effects: regulatory changes (WMP crackdowns,
  deposit-rate reforms) shift funds between M2 components without
  changing fundamental liquidity.
- M2 is a stock measure of money; it does not equal new credit
  creation. Changes in M2 reflect net flows, not gross lending.

---

## m1-yoy: M1 同比 / M1 Money Supply YoY

- **Series code**: akshare:macro_china_money_supply (column: 货币(M1)-同比增长)
- **Source**: 中国人民银行 PBOC via akshare
- **Unit**: Percent (%)
- **Frequency**: Monthly
- **Publication lag**: ~10-15 days after reference month (jointly with M2)
- **History**: From the 1990s

**What it measures**: Year-over-year growth in M1 — currency in
circulation plus corporate demand deposits (企业活期存款). Narrower than
M2, it captures "transactional money" — funds actively deployable
by corporates for spending and investment.

**How to interpret**:
- Rising → Corporate activity picking up; firms holding more liquid
  deposits, typically for near-term investment or payroll. Historically
  a leading indicator for real-estate sales and industrial investment.
- Falling → Corporate cash-hoarding shifting to term deposits (captured
  in M2 but not M1) or genuinely weak business activity. Persistent
  M1 weakness during 2024-2025 has accompanied the property downturn.
- **M1 - M2 spread (M1 同比 minus M2 同比)** is a classic Chinese
  leading indicator. A widening negative spread (M2 > M1) signals
  household/corporate risk aversion and precautionary saving. A
  narrowing (M1 catching up) signals recovery.

**Market significance**: ⭐⭐⭐
The M1-M2 spread is one of the most-cited Chinese macro indicators
by domestic strategists — often used as the "sentiment gauge" for
corporate animal spirits. A rising M1-M2 spread tends to precede
equity-market rallies by 3-6 months.

**When to use**: Corporate-investment-cycle reading, equity-market
leading-indicator input, property-sales turning-point detection,
precautionary-saving diagnosis.

**China-specific context**:
- **October 2024 M1 methodology revision**: PBOC announced a
  methodology change (effective from 2025) to include personal
  demand deposits and certain non-bank payment-system balances in M1.
  This creates a level-discontinuity in the series; the post-reform
  M1 is structurally higher than the pre-reform series. YoY
  comparisons across the regime change need methodology adjustments.
- M1 in China historically excluded personal demand deposits (unlike
  US M1 which includes checking accounts) — this is why the M1-M2
  spread was such a cleanly "corporate" indicator. The 2024-2025
  methodology update partially narrowed this gap.
- Chinese New Year timing effect: firms pay bonuses and supplier
  settlements pre-Spring Festival, compressing M1 momentarily — a
  seasonal effect.

**Common pitfalls**:
- The October 2024 methodology revision is a major break — always
  check whether a data series spans the break and annotate accordingly.
- The M1-M2 spread is a relative indicator; read it as a trend
  (rolling 6-12 month average) rather than point-in-time.
- Single-month M1 prints are volatile; short-term moves can reflect
  timing of tax payments, IPO subscriptions, or bond issuances rather
  than underlying sentiment.

---

## shrzgm: 社会融资规模增量 / Aggregate Financing to the Real Economy (AFRE Flow)

- **Series code**: akshare:macro_china_shrzgm
- **Source**: 中国人民银行 PBOC via akshare
- **Unit**: 亿元 (hundred-million RMB), typically reported as trillion yuan
- **Frequency**: Monthly
- **Publication lag**: ~10-15 days after reference month (released with M2, new loans)
- **History**: From 2002 (250+ observations)

**What it measures**: Monthly flow of 社会融资规模 (social financing
scale / Aggregate Financing to the Real Economy). The broadest Chinese
credit aggregate — captures new bank loans, shadow-banking credit
(trust loans, entrusted loans, undiscounted bankers' acceptances),
corporate bond issuance net, government bond issuance net, equity
financing, and miscellaneous other categories.

**How to interpret**:
- Higher-than-expected flow → Credit supply meeting demand; stimulus
  transmitting. Supportive of risk assets broadly.
- Lower-than-expected flow → Credit stress or weak demand. During
  2023-2025 the drag has primarily been weak loan demand (households
  and corporates reluctant to borrow) rather than supply constraint.
- Composition matters: government-bond-issuance-driven AFRE flows
  (especially special local-government bonds) reflect fiscal rather
  than monetary stimulus. Bank-loan-driven flows reflect monetary
  transmission.

**Market significance**: ⭐⭐⭐
Often called "the most important Chinese credit indicator." More
comprehensive than M2 (which misses bond/equity issuance) or new
loans (which misses bonds and shadow banking). Moves CSI 300,
property-sector equities, and CNY.

**When to use**: Credit-cycle diagnosis, stimulus-effectiveness
assessment (fiscal vs monetary), property-sector credit-access
monitoring, global commodity-demand framing.

**China-specific context**:
- **AFRE is a uniquely Chinese credit aggregate**, designed by PBOC
  in 2011 to capture China's fragmented credit system (banks, shadow
  banking, corporate bonds, government bonds, equity financing).
  There is no direct US or European equivalent.
- Post-2017 "shadow banking" crackdown shrank the trust-loan and
  entrusted-loan components dramatically — historical AFRE pre-2017
  is not directly comparable to post-2017 AFRE for composition reads.
- Government bond issuance (especially LGFV/special local government
  bonds) has been a major AFRE contributor in 2023-2025 as fiscal
  policy compensated for monetary-transmission weakness.
- AFRE stock (存量社融) vs AFRE flow (增量社融, this series) — the
  flow is the net new financing in the month; the stock is cumulative.
  This preset tracks the flow.

**Common pitfalls**:
- Monthly AFRE flows are highly volatile (2-5 trillion yuan range).
  Use 12-month rolling sums for trend reads.
- Seasonality is pronounced: January tends to be massive (new-year
  loan frontloading); October tends to be weak (post-Golden Week
  window).
- PBOC periodically revises AFRE methodology (e.g., adding asset-
  backed securities, rule changes for specific bond types). Long-
  horizon comparisons need methodology annotations.
- The January Jan-Feb framing: Chinese New Year can shift loan
  booking between January and February, creating volatile single-
  month prints but smooth Jan-Feb combined reads.

---

## new-loans: 新增人民币贷款 / New RMB Loans

- **Series code**: akshare:macro_china_new_financial_credit
- **Source**: 中国人民银行 PBOC via akshare
- **Unit**: 亿元 (hundred-million RMB), typically reported as trillion yuan
- **Frequency**: Monthly
- **Publication lag**: ~10-15 days after reference month (released jointly with M2, AFRE)
- **History**: From the 1990s (300+ observations)

**What it measures**: Monthly flow of new RMB loans extended by
commercial banks to households, corporates, and non-bank financial
institutions. A subset of AFRE — the bank-loan component.

**How to interpret**:
- Strong new-loan print → Bank credit flowing to real economy.
  Composition split matters:
  - Household loans up → Mortgage demand recovering / consumer lending.
  - Corporate short-term loans up → Working-capital demand.
  - Corporate medium/long-term loans up → Capex demand (most bullish).
  - Bill financing (票据) up → Banks padding loan totals without
    genuine credit creation (bearish disguise).
- Weak print → Loan demand soft (typical in 2023-2025 for households
  as property deleveraging persists).

**Market significance**: ⭐⭐⭐
A core monthly indicator for Chinese credit conditions. The release
is market-moving — headline prints and the household-vs-corporate
split both drive narratives. Moves CSI 300, property-sector equities,
and Chinese bank stocks.

**When to use**: Credit-conditions diagnosis, household-deleveraging
tracking, capex-cycle indicator, bank-margin forward-look,
effectiveness-of-easing measurement.

**China-specific context**:
- Household new loans = mortgage + consumer credit + personal
  business loans. The mortgage component is the largest and has
  been the dominant drag during the 2022-2025 property downturn —
  household new loans turned negative in some months of 2024,
  historically extreme.
- Corporate medium/long-term loans (对公中长期) is the "quality
  credit" indicator — reflects capex investment intent. Watched
  closely by infrastructure and industrial analysts.
- "Bill financing" (票据融资) is a low-quality way banks hit lending
  targets without genuine credit creation. A high bill-financing
  share signals banks padding numbers to meet quotas.
- January is massive (frontloading effect) — often 4-5 trillion yuan
  in a single month, ~20-25% of annual total. Seasonality is severe.

**Common pitfalls**:
- Single-month prints are highly seasonal; use Jan-Feb combined for
  the year-start read and 12-month rolling sums for trend.
- Headline number alone is insufficient — always check the
  household-vs-corporate and short-vs-long-term splits in PBOC's
  accompanying press release.
- Historical revisions: PBOC occasionally restates prior-month
  figures as bank reporting updates. Small revisions are normal.
- New loans ≠ AFRE: the two are related but not interchangeable.
  New loans misses bond and equity financing; AFRE captures both.

---
