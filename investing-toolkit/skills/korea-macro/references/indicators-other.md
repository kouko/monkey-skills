# Other / 기타 — Markets, FX, Money, Real Estate

---

## kospi: 코스피지수 / KOSPI Index

- **Series code**: K101 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Index points
- **Frequency**: Daily
- **Publication lag**: 1 business day
- **History**: From 1995 (7,800+ observations)

**What it measures**: The Korea Composite Stock Price Index — the primary
benchmark for the Korean stock market. A market-capitalization-weighted
index of all common stocks listed on the Korea Exchange (KRX) main board.

**How to interpret**:
- Rising → Equity market rally. Reflects optimism about Korean corporate
  earnings, export outlook, or global risk appetite.
- Falling → Market selling. Can reflect domestic concerns (policy, credit),
  global risk-off, or Korea-specific risks (geopolitical, FX).

**Market significance**: ⭐⭐⭐
Korea's benchmark equity index, globally watched as a barometer for:
(1) the global semiconductor cycle (Samsung and SK Hynix are ~30% of KOSPI
by weight), (2) emerging market risk appetite, and (3) Korea's export
economy. KOSPI is included in the MSCI Emerging Markets index (Korea is
currently classified as EM despite being a high-income economy).

**When to use**: Korea equity allocation, semiconductor cycle proxy, EM risk appetite gauge, Korea discount monitoring, Buffett indicator computation.

**Korea-specific context**:
- KOSPI is heavily concentrated: Samsung Electronics alone is ~20% of the
  index by market cap. The top 10 stocks represent ~55%. KOSPI performance
  is essentially Samsung + Hyundai/Kia + SK Hynix + other chaebols.
- The "Korea discount" refers to KOSPI consistently trading at a lower P/E
  ratio than developed market indices (typically 10-12x vs. S&P 500's 20x+).
  Attributed to: chaebol governance, geopolitical risk (North Korea), weak
  shareholder returns, and EM classification.
- Foreign investors hold ~30% of KOSPI by market cap. Foreign flow data
  is published daily and is a key short-term market driver.
- KOSPI has been range-bound around 2,400-2,700 for extended periods (the
  so-called "박스피" / "boxpi" phenomenon), though it reached 3,300 in 2021.

**Common pitfalls**:
- KOSPI is price-only (does not include dividends). Total return indices
  differ, especially for dividend-paying stocks.
- Daily data includes trading days only (Mon-Fri, excluding Korean holidays).
- KOSPI includes all KRX-listed stocks, not just large caps. For large-cap
  only, reference KOSPI 200.

---

## kosdaq: 코스닥지수 / KOSDAQ Index

- **Series code**: K102 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Index points
- **Frequency**: Daily
- **Publication lag**: 1 business day
- **History**: From 1999

**What it measures**: The Korea Securities Dealers Automated Quotation
index — the secondary market for smaller, growth-oriented companies.
Analogous to the US NASDAQ but with more biotech, gaming, and IT services
companies.

**How to interpret**:
- Rising → Risk appetite for growth/small-cap Korean stocks. Often reflects
  retail investor enthusiasm and speculation.
- Falling → Risk-off for growth stocks. KOSDAQ is more volatile than KOSPI.

**Market significance**: ⭐⭐
Less globally watched than KOSPI, but important for understanding Korean
retail investor sentiment and the growth/biotech sector. KOSDAQ has a much
higher retail ownership share than KOSPI.

**When to use**: Retail sentiment gauge, growth and biotech sector tracking, risk appetite assessment, small-cap Korea exposure decisions.

**Korea-specific context**:
- KOSDAQ is dominated by biotech (~20%), IT services, and gaming companies.
  It's more sensitive to retail sentiment than institutional flows.
- Korean retail investors ("개미" / ants) are very active in KOSDAQ. Retail
  participation surged post-COVID and remains structurally higher than pre-2020.
- KOSDAQ tends to outperform during "risk-on" periods and underperform
  during "risk-off" periods, amplifying KOSPI moves.

**Common pitfalls**:
- KOSDAQ is much smaller than KOSPI by total market cap (~1/10).
- Higher volatility and lower liquidity. Daily swings of 2-3% are common.
- Individual stock concentration: a few large KOSDAQ stocks can move the index.

---

## krw-usd: 원달러 환율 / KRW/USD Exchange Rate

- **Series code**: DEXKOUS (FRED)
- **Source**: FRED (Federal Reserve Bank of St. Louis) via CSV
- **Unit**: KRW per 1 USD
- **Frequency**: Daily
- **Publication lag**: 1-2 business days
- **History**: From 2000 (6,500+ observations)

**What it measures**: The KRW/USD spot exchange rate as reported by the
Federal Reserve Board. Higher value = weaker KRW (more won per dollar).

**How to interpret**:
- Rising (KRW depreciating) → Won weakening vs dollar. Positive for
  exporters' KRW revenue. Negative for importers (energy, raw materials).
  Can signal capital outflows, risk-off, or US-Korea rate differential
  widening.
- Falling (KRW appreciating) → Won strengthening. Negative for exporters'
  KRW competitiveness. Positive for importers and consumers. Often reflects
  strong foreign inflows, trade surplus, or global risk-on.

**Market significance**: ⭐⭐⭐
The most important exchange rate for Korea. KRW/USD is:
1. The key price variable for Korea's export-dependent economy
2. A major determinant of KOSPI earnings (via translation effects)
3. A leading indicator for Korean inflation (import price pass-through)
4. A proxy for emerging market risk appetite (KRW is among the most
   liquid EM currencies, often used as a proxy for EM FX)

**When to use**: Korea FX risk monitoring, export competitiveness assessment, EM FX proxy, BOK intervention analysis, Korea-US rate differential impact tracking.

**Korea-specific context**:
- KRW is a "managed float" — the government and BOK intervene to smooth
  excessive volatility. Korea has been on the US Treasury's currency
  monitoring list. The authorities deny targeting a specific level but
  are known to smooth rapid moves.
- Key levels: 1,100 KRW/USD is considered strong KRW, 1,300+ is weak KRW,
  1,400+ triggers policy concern. During the 2022 dollar surge, KRW
  weakened past 1,430 — the weakest since the 2008 financial crisis.
- The National Pension Service (NPS, ~$900B AUM) is a major FX market
  participant. NPS overseas investments create structural KRW selling
  pressure, while repatriation of overseas income creates KRW buying.
- The onshore KRW market (Seoul) has limited trading hours (9am-3:30pm
  KST). Extended trading hours to 2am KST began in 2024.

**Common pitfalls**:
- Higher number = weaker KRW (more won per dollar). This is the opposite
  convention from EUR/USD where higher = stronger EUR.
- FRED data (DEXKOUS) is sourced from the Federal Reserve Board noon buying
  rates. It may differ slightly from Korea's onshore fixing rate.
- FRED data excludes US holidays and weekends. Korean holidays may show
  data if the US market was open.

---

## krw-jpy / krw-eur / krw-cny: KRW cross rates

- **Series codes**: K153 (KRW/JPY per 100 yen), K154 (KRW/EUR), K156 (KRW/CNY)
- **Source**: Bank of Korea via FinanceDataReader (BOK official closing rates)
- **Unit**: KRW per unit of foreign currency (KRW per 100 JPY for K153)
- **Frequency**: Daily (3:30pm KST close)
- **Publication lag**: 1 business day
- **History**: K153/K154 from 2000; K156 from 2015 (direct KRW/CNY quote)

**What they measure**: BOK's official closing FX fixing rates for the
three major KRW cross pairs beyond USD.

**How to interpret**:
- **KRW/JPY** — most-watched cross for competitive exports. Samsung / Hyundai
  compete directly with Sony / Toyota; KRW strength vs JPY compresses
  Korean export margins.
- **KRW/EUR** — matters for EU-bound exports (autos, shipbuilding, semiconductors).
- **KRW/CNY** — reflects China supply-chain dynamics; KRW weakness vs CNY
  often signals 재화수출 to China softening.

**Market significance**: ⭐⭐ (JPY) / ⭐ (EUR / CNY)
KRW/JPY is the most cited after KRW/USD by local brokers. Bank of Korea
also watches the **통화지수** (REER / NEER basket) which uses these.

**When to use**: Competitive-devaluation analysis, chaebol earnings
sensitivity, China-KR trade balance decomposition.

**Common pitfalls**:
- K153 is per **100 yen**, not per 1 yen — read carefully.
- K152 (KRW/USD BOK official) is an alternative to FRED DEXKOUS; we
  continue to use FRED for symmetry with other country skills.

---

## fx-reserves: 외환보유액 합계 / FX Reserves Total

- **Series code**: K155 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Million USD
- **Frequency**: Monthly (end-of-month)
- **Publication lag**: ~5-7 days after month-end
- **History**: From 1990

**What it measures**: Korea's total foreign exchange reserves — USD-denominated
sum of securities, deposits, gold, SDRs, and IMF reserve position held by
the BOK.

**How to interpret**:
- Rising → BOK accumulating FX (often via trade surplus + less intervention).
- Falling → BOK depleting reserves (FX intervention to defend KRW, or USD-
  denominated asset repricing during strong dollar periods).
- Historical peaks: ~$469B in 2022; fell to ~$400B during 2022 USD surge
  when BOK intervened heavily.

**Market significance**: ⭐⭐
Signals BOK's willingness and capacity to intervene in FX. Large monthly
drops (e.g., -$10B) coincide with active smoothing operations.

**When to use**: BOK intervention detection, FX defence capacity
assessment, sovereign credit rating input (S&P / Moody's track reserves/GDP ratio).

**Korea-specific context**:
- Korea sits in the upper tier globally but is dwarfed by JP ($1.2T+) and
  CN ($3.2T+). Reserves/M2 ratio is ~15%, comfortable but not abundant.
- National Pension Service (NPS) holdings are NOT included — only BOK-managed reserves.

**Common pitfalls**:
- The value is in USD; valuation effect (USD strength → EUR/JPY reserve
  components shrink in USD terms) can cause headline swings not reflecting
  policy intervention. Check BOK commentary to separate intervention from
  valuation.

---

## m1: 협의통화 M1 / M1 Narrow Money

- **Series code**: K002 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Billion KRW (average balance, original series)
- **Frequency**: Monthly
- **Publication lag**: ~4 weeks after reference month
- **History**: From 2003

**What it measures**: Narrow money — currency in circulation plus demand
deposits and instantly-withdrawable savings. The most liquid monetary
aggregate; measures transaction balances.

**How to interpret**:
- M1 YoY growth accelerating → Liquidity flowing into transaction
  accounts (rather than term deposits) — typically precedes asset-price
  rallies or consumption pickup.
- M1/M2 ratio falling → Funds moving into longer-maturity deposits,
  suggesting rate-sensitive savers moving away from demand accounts.

**Market significance**: ⭐⭐
M1 leads M2 at turning points — accelerating M1 often signals
imminent risk-asset rallies (KOSPI / real estate). BOK watches M1/M2
spread for policy transmission feedback.

**When to use**: Liquidity regime detection, KOSPI beta rotation timing,
BOK policy transmission check.

**Common pitfalls**: Values in billions of KRW; use YoY growth rather
than level. Not seasonally adjusted — watch for Chuseok / Lunar New
Year distortions.

---

## lf: Lf 금융기관유동성 / Financial Institution Liquidity

- **Series code**: K004 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Billion KRW
- **Frequency**: Monthly
- **Publication lag**: ~6 weeks after reference month
- **History**: From 2003

**What it measures**: Lf (금융기관유동성) — a broader liquidity
aggregate than M2 that adds financial institution bonds and commercial
paper. BOK uses Lf as its "near-M3" tracker since Korea's M3 was
discontinued.

**How to interpret**:
- Lf growth > M2 growth → Liquidity is expanding primarily through
  non-bank financial channels (insurance, securities companies).
- Lf growth < M2 growth → Bank liquidity expansion dominates;
  non-bank FIs deleveraging.

**Market significance**: ⭐
Niche — mainly used in BOK research papers. Less market-moving than M2.

**When to use**: Comprehensive liquidity assessment when analyzing
non-bank FI stress (e.g., 2022 Legoland crisis exposed 증권사 CP
distress that was visible in Lf but not M2).

**Common pitfalls**: Ambiguous release schedule (sometimes bundled
with M2, sometimes separate). Always check latest release date.

---

## m2: 광의통화 M2 / M2 Broad Money

- **Series code**: K003 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Billion KRW
- **Frequency**: Monthly
- **Publication lag**: ~4 weeks after reference month
- **History**: From 2003

**What it measures**: Korea's broad money supply — currency in circulation,
demand deposits, time deposits, savings deposits, money market funds,
and other liquid financial instruments. The broadest standard monetary
aggregate published by the BOK.

**How to interpret**:
- Rising (positive YoY growth) → Liquidity expanding. Supports asset prices
  and economic activity. The BOK monitors M2 growth closely.
- Falling (decelerating YoY growth) → Liquidity tightening. Can signal
  credit contraction or deleveraging.

**Market significance**: ⭐⭐
Important for understanding monetary conditions. The BOK references M2
growth in its policy statements, though Korea no longer has an explicit
M2 growth target (unlike Taiwan's CBC).

**When to use**: Liquidity conditions tracking, asset price support assessment, credit cycle monitoring, BOK monetary stance confirmation.

**Korea-specific context**:
- Korea's M2 growth accelerated sharply during COVID (15%+ YoY in 2020-2021)
  due to aggressive fiscal and monetary easing. This excess liquidity fueled
  the real estate and stock market boom. Post-2022 tightening brought M2
  growth back to 4-5%.
- Korea's household debt-to-GDP ratio is among the highest in the world
  (~105%). M2 trends reflect both genuine economic activity and household
  leverage dynamics.
- Housing-related lending (mortgage loans, jeonse loans) is a major
  component of credit growth in Korea.

**Common pitfalls**:
- Values are in billions of KRW. Focus on YoY growth rates for trend analysis.
- The M2 definition was revised in 2006 (from the old MCT+ framework). Data
  from 2003 onward uses the current definition. Pre-2003 data is not
  directly comparable.

---

## household-credit: 가계신용 / Household Credit

- **Series code**: K007 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Trillion KRW
- **Frequency**: Quarterly
- **Publication lag**: ~6 weeks after quarter-end
- **History**: From 2002

**What it measures**: Total household credit outstanding — the sum of
household loans from all financial institutions plus credit card purchases.
The definitive measure of Korean household indebtedness.

**How to interpret**:
- Rising → Households taking on more debt. Can fuel consumption and real
  estate purchases in the short term, but increases systemic risk. The BOK
  closely monitors household credit growth for financial stability purposes.
- Falling or decelerating → Household deleveraging. Can drag on consumption
  but reduces financial stability risk.

**Market significance**: ⭐⭐⭐
Korea's household debt is a systemically important macro variable. At ~105%
of GDP, it is among the highest in the world and is a key input to BOK
rate decisions. The BOK has explicitly cited household debt concerns as a
reason for maintaining higher rates even when growth weakened.

**When to use**: Financial stability risk monitoring, BOK macroprudential policy input, real estate leverage gauge, consumption outlook assessment, jeonse system risk tracking.

**Korea-specific context**:
- Korea's high household debt is driven by: (1) mortgage loans for apartment
  purchases, (2) jeonse (전세) deposit loans — Korea's unique lump-sum
  rental system requires tenants to borrow large deposits, and (3) self-
  employed business loans (classified as household if the business is
  unincorporated).
- The jeonse system creates unique leverage: tenants borrow ~50-70% of
  apartment value as a deposit, and landlords use received deposits to
  buy more apartments. This creates a leverage chain vulnerable to housing
  price declines.
- The BOK uses macroprudential tools (LTV caps, DTI ratios, DSR limits) to
  manage household credit growth. These tools are frequently adjusted and
  are as important as the policy rate for credit conditions.
- Household credit deceleration is a leading indicator for consumption
  weakness and real estate market softening.

**Common pitfalls**:
- Quarterly frequency — less timely than monthly indicators.
- Household credit includes both loans and credit card purchases. The
  growth rate can be affected by credit card seasonality.
- "Household credit" includes self-employed business loans. The actual
  mortgage-only component is a subset.

---

## housing-price: 주택매매가격지수 / Housing Price Index

- **Series code**: K407 (ECOS-KEYSTAT)
- **Source**: Bank of Korea (KB Kookmin Bank data) via FinanceDataReader
- **Unit**: Index (base month varies)
- **Frequency**: Monthly
- **Publication lag**: ~4 weeks after reference month
- **History**: From 2021 (limited ECOS history)

**What it measures**: A composite index of residential property transaction
prices in Korea, covering apartments (the dominant housing type), detached
houses, and row houses across the nation.

**How to interpret**:
- Rising → Housing prices appreciating. Wealth effect for homeowners,
  affordability pressure for non-owners. Can fuel household leverage
  (borrowing to buy before prices rise further).
- Falling → Housing prices declining. Negative wealth effect, potential
  jeonse deposit losses, stress for leveraged households and developers.

**Market significance**: ⭐⭐⭐
Housing is the single most important asset for Korean households (~70%
of household wealth). Housing price trends are a major input to BOK rate
decisions, government policy (macroprudential regulations, tax policy),
and consumer sentiment. Korea's housing market has been a major political
issue for over a decade.

**When to use**: Wealth effect assessment, jeonse deposit risk monitoring, BOK rate decision input, social policy impact tracking, household asset allocation analysis.

**Korea-specific context**:
- Korean housing = apartments (아파트). Unlike the US or Japan where housing
  types are diverse, Korean urban housing is dominated by apartment complexes.
  ~60% of Korean households live in apartments.
- Seoul and the metropolitan area (수도권) concentrate national wealth and
  economic activity. Seoul apartment prices are the most closely watched
  segment — a few Gangnam (강남) districts can move the national index.
- Korea's jeonse system creates unique housing market dynamics. When housing
  prices fall, jeonse deposit return risk increases (landlords may not have
  funds to return deposits), creating a potential cascade.
- The government frequently changes housing-related tax and regulatory
  policies (acquisition tax, comprehensive real estate tax, LTV limits).
  These policy changes can create sharp market turning points.

**Common pitfalls**:
- ECOS KEYSTAT history for this indicator starts from 2021 — very limited.
  For longer housing price history, Korea Appraisal Board (한국부동산원)
  data or KB Kookmin Bank housing price data (going back to 2003+) are
  needed from other sources.
- National average masks massive regional divergence. Seoul prices can
  surge while regional cities stagnate or decline.
- The index captures transaction prices, which can lag asking prices
  during rapid market turns due to low transaction volume.
