# Sources / 출처 / 資料來源

Primary sources referenced in the korea-macro indicator documentation.

---

## Official Institutional Sources

### Bank of Korea / 한국은행 (BOK)

- **ECOS (Economic Statistics System)**: The BOK's statistical database
  providing comprehensive Korean economic data. The primary data source
  for korea-macro via FinanceDataReader's ECOS-KEYSTAT integration.
  https://ecos.bok.or.kr/

- **ECOS-KEYSTAT**: A curated set of ~100 key economic indicators published
  as KEYSTAT codes (K001-K499). These are the most important headline
  indicators, pre-formatted for easy access. FinanceDataReader uses
  KEYSTAT codes internally via the endpoint
  `https://ecos.bok.or.kr/serviceEndpoint/httpService/request.json`.

- **ECOS Open API**: A documented public API requiring registration with a
  Korean mobile number. Not used by this skill because FinanceDataReader
  provides equivalent access without registration.
  https://ecos.bok.or.kr/api/#/

- **Monetary Policy Committee (금융통화위원회)**: Meets 8 times per year
  (roughly every 6 weeks) to set the base rate. Meeting schedule and
  minutes are published on the BOK website.
  https://www.bok.or.kr/eng/main/main.do

### Statistics Korea / 통계청

- **KOSIS (Korean Statistical Information Service)**: The national statistical
  database. Statistics Korea compiles labor market data (경제활동인구조사),
  CPI/PPI, industrial production indices, and business cycle indicators.
  https://kosis.kr/

- **Business Cycle Reference Dates**: Statistics Korea officially dates
  business cycle peaks and troughs based on the composite leading and
  coincident indices.
  https://kostat.go.kr/

### Korea Customs Service / 관세청

- **Preliminary Trade Statistics**: Monthly trade data (exports, imports)
  released within 15 days of month-end — faster than ECOS data. The
  fastest official trade data, used by market participants for near-
  real-time tracking. Not available via ECOS-KEYSTAT.
  https://unipass.customs.go.kr/

### KB Kookmin Bank / KB국민은행

- **KB Real Estate Statistics**: Housing price indices, jeonse (deposit
  rental) price indices, and real estate market data. KB Kookmin Bank is
  the primary source for Korean housing market statistics (also distributed
  via ECOS for some series like K407).
  https://kbland.kr/

### Korea Appraisal Board / 한국부동산원

- **Real Estate Price Index**: An alternative housing price index with
  longer history than KB's ECOS distribution. Covers apartment, house,
  and land price trends.
  https://www.reb.or.kr/

### FRED (Federal Reserve Bank of St. Louis)

- **DEXKOUS**: KRW/USD exchange rate series from the Federal Reserve Board.
  Used for the `krw-usd` preset because ECOS-KEYSTAT does not provide a
  clean daily KRW/USD series via KEYSTAT codes. No API key required (CSV
  download).
  https://fred.stlouisfed.org/series/DEXKOUS

---

## FinanceDataReader (Data Access Library)

- **PyPI**: `finance-datareader==0.9.90`
- **GitHub**: https://github.com/financedata/FinanceDataReader (1.5k stars)
- **How it works**: FinanceDataReader wraps multiple Korean financial data
  sources (ECOS, KRX, DART, Naver Finance) behind a unified `fdr.DataReader()`
  API. For ECOS-KEYSTAT data, it sends POST requests to BOK's internal
  service endpoint with `usrId=IECOSPC` (the same user ID used by the ECOS
  website itself).
- **Dependencies**: requests, beautifulsoup4, lxml, plotly, pandas, numpy
- **No API key required**: FinanceDataReader accesses ECOS through the
  website's internal endpoint, bypassing the API key requirement.

---

## Korea-Specific Economic Context

### Export-Dependent Structure

Korea's economy is heavily export-dependent (exports ~40-45% of GDP).
The semiconductor industry is the single largest export category (~20%
of total exports), with Samsung Electronics and SK Hynix dominating
global memory chip markets (DRAM ~70% market share combined, NAND ~50%).

### Chaebol (재벌) Dominance

Korea's economy is dominated by large conglomerate groups (chaebols):
Samsung, SK, Hyundai, LG, Lotte, etc. The top 5 chaebols account for
~50% of KOSPI market capitalization and a disproportionate share of
exports, investment, and R&D. This concentration means that a few
companies' strategic decisions (capex, hiring, pricing) are quasi-macro
indicators.

### BOK Monetary Policy Characteristics

- **Rate increments**: 25 bps (same as Fed), occasionally 50 bps for urgency
- **Dual mandate tension**: The BOK targets 2% CPI inflation but also monitors
  financial stability (household debt, real estate). These objectives often
  conflict — household debt concerns prevented rate cuts even when inflation
  was at target.
- **FX sensitivity**: Unlike the Fed, the BOK cannot ignore the exchange rate.
  Excessive KRW weakness triggers capital outflow concerns and import
  inflation. The Korea-US rate differential is a binding constraint.
- **Macroprudential toolkit**: LTV (loan-to-value), DTI (debt-to-income),
  DSR (debt service ratio) regulations are frequently adjusted and are as
  important as the policy rate for credit conditions.

### Household Debt and Real Estate

- Korea's household debt-to-GDP ratio (~105%) is among the highest globally.
- The jeonse (전세) system is unique to Korea: tenants pay a large lump-sum
  deposit (50-80% of property value) instead of monthly rent. This creates
  a leverage chain: tenants borrow deposits from banks → landlords use
  deposits to buy more properties → creating systemic leverage exposure
  to housing price declines.
- Apartment purchases are the primary household savings vehicle. Real estate
  represents ~70% of household wealth (vs. ~30% in the US where equities
  are a larger share).

### Semiconductor Cycle = Korea Cycle

The semiconductor industry's impact on Korea is outsized:
- ~20% of total exports
- ~6% of GDP directly (much more including supply chain)
- Samsung Electronics alone is ~20% of KOSPI market cap
- Memory chip capex decisions affect manufacturing production, capital
  investment, employment, and tax revenue
- Global chip demand downturns (2019, 2023) directly cause Korean GDP
  growth deceleration, trade surplus narrowing, and KRW weakness.

---

## Market Consensus Claims

The following claims reflect broadly held market practitioner consensus:

- **"Korea discount" (코리아 디스카운트)** — KOSPI consistently trades at a
  lower valuation (P/E, P/B) than developed market indices. Attributed to
  chaebol governance (low dividends, complex cross-holdings, minority
  shareholder rights), geopolitical risk (North Korea), and MSCI EM
  classification. The Korean government launched the "Corporate Value-Up"
  program in 2024 to address this discount (modeled on Japan's TSE reforms).

- **"Boxpi" (박스피)** — KOSPI's tendency to trade in a range (2,000-2,700)
  for extended periods. Market participants joke that KOSPI is "trapped in
  a box." This reflects Korea's structural growth deceleration and the
  earnings headwinds from cyclical semiconductor downturns.

- **Market significance ratings** — The relative importance ratings in the
  indicator documentation are editorial assessments based on: BOK policy
  communication emphasis, market participant attention, and frequency of
  citation in financial media. They are not derived from a quantitative study.
