# Sources / 出典

Primary sources referenced in the japan-macro indicator documentation.

---

## Official Institutional Sources

### Bank of Japan (日本銀行)

- **TANKAN Methodology**: BOJ, "Explanation of the Short-term Economic Survey of Enterprises in Japan (Tankan)." DI = favorable% − unfavorable%. 0 = balanced sentiment. Enterprise categories: Large (≥¥1B capital), Medium (¥100M–¥1B), Small (¥20M–¥100M) × 17 manufacturing + 14 non-manufacturing sectors. Approx. 210,000 enterprises surveyed.
  https://www.boj.or.jp/en/statistics/outline/exp/tk/extk.htm

- **BOJ Time-Series Data Search API Manual** (2026-02-18): Official API specification for programmatic data access. 3 endpoints (getDataCode, getDataLayer, getMetadata), JSON/CSV output, no authentication required.
  https://www.stat-search.boj.or.jp/info/api_manual_en.pdf

- **Monetary Policy Framework**: Price stability target of 2% (CPI YoY), set January 2013. Policy Board decides at MPMs held 8 times yearly.
  https://www.boj.or.jp/en/mopo/outline/index.htm

- **Negative Interest Rate Policy**: Introduced January 29, 2016 (−0.1% on excess reserves). Ended March 19, 2024 (raised to 0.0–0.1% range).
  BOJ Statements on Monetary Policy, 2016-01-29 and 2024-03-19.

- **Yield Curve Control (YCC)**: Introduced September 21, 2016 (targeting 10Y JGB yield at ~0%). Band widened July 2023 (±0.5% → ±1.0%). Effectively abandoned October 2023 (changed from "cap" to "reference"). Formally ended March 2024.
  BOJ Statements on Monetary Policy, 2016-09-21, 2023-07-28, 2023-10-31, 2024-03-19.

- **Corporate Goods Price Index (CGPI)**: BOJ-managed wholesale/corporate price index. Measures price changes of goods traded between companies. Distinct from CPI (consumer prices, managed by Statistics Bureau).
  https://www.boj.or.jp/en/statistics/pi/cgpi_2020/index.htm

### Cabinet Office / Economic and Social Research Institute (内閣府 / ESRI)

- **Composite Indexes (景気動向指数) Methodology**: 30 component indicators — 11 leading, 10 coincident, 9 lagging. Uses interquartile range normalization and symmetric percentage change. Coincident Index tracks current business cycle; Leading Index anticipates by several months.
  https://www.esri.cao.go.jp/en/stat/di/di2e.html

- **Machine Orders (機械受注統計)**: "Orders Received for Machinery" survey. "Private-sector excluding volatile orders" (民需、船舶・電力を除く) is the headline figure and is considered a leading indicator of business fixed investment (capex), typically leading GDP by 6–9 months.
  https://www.esri.cao.go.jp/en/stat/juchu/juchu-e.html

### Ministry of Internal Affairs and Communications / Statistics Bureau (総務省統計局)

- **Consumer Price Index (CPI)**: Statistics Bureau manages consumer CPI. Japan's "core CPI" (コアCPI) = All items less fresh food (生鮮食品を除く総合). This differs from the US definition where "core" = less food AND energy. Japan's "core-core CPI" (コアコアCPI) = less food and energy, equivalent to US core.
  https://www.stat.go.jp/english/data/cpi/index.html

- **Labour Force Survey (完全失業率)**: Unemployment rate based on monthly survey. Japan also uses 有効求人倍率 (Job-to-applicant ratio) from Ministry of Health, Labour and Welfare, which is often more closely watched by market participants due to Japan's structural labor shortage.
  https://www.stat.go.jp/english/data/roudou/index.html

### Statistics Dashboard API (統計ダッシュボード)

- **API Documentation**: Free, no-auth API providing ~6,000 indicators from multiple government agencies. Covers CPI, GDP, employment, industrial production, JGB yields, and more.
  https://dashboard.e-stat.go.jp/static/api

### Ministry of Economy, Trade and Industry (経済産業省 / METI)

- **Industrial Production Index (鉱工業生産指数)**: Measures real output of manufacturing, mining, and utilities. Published monthly, ~3-4 weeks lag.
  https://www.meti.go.jp/english/statistics/tyo/iip/index.html

- **Tertiary Industry Activity Index (第3次産業活動指数)**: Measures real output of service sector activities. Real terms (price-adjusted), complementary to IP.
  https://www.meti.go.jp/english/statistics/tyo/sanzi/index.html

### Ministry of Finance (財務省)

- **JGB Yields**: 10-year Japanese Government Bond yields published monthly.
  https://www.mof.go.jp/english/jgbs/reference/interest_rate/index.htm

- **Balance of Payments (経常収支)**: Japan's current account structure: persistent trade deficit (goods) offset by investment income surplus, resulting in net positive current account.
  https://www.mof.go.jp/english/policy/international_policy/reference/balance_of_payments/index.htm

### World Bank

- **Japan Services Sector GDP Share**: Services value added as % of GDP. Approximately 70-71% (2015–2024, stable). Indicator: NV.SRV.TOTL.ZS.
  https://data.worldbank.org/indicator/NV.SRV.TOTL.ZS?locations=JP

---

## Academic and Research References

- **Yield Curve and Recession**: Estrella, A. & Mishkin, F.S. "The Yield Curve as a Predictor of U.S. Recessions." Federal Reserve Bank of New York, Current Issues in Economics and Finance, Vol. 2, No. 7. (US-focused but framework applied globally.)
  https://www.newyorkfed.org/research/current_issues/ci2-7.html

- **Japan Phillips Curve**: Gregor Smith (2008), "Japan's Phillips Curve Looks Like Japan." Journal of Money, Credit and Banking 40(6).

- **Exchange Rate Pass-Through (Japan)**: RIETI, "Exchange Rate Pass-Through and Domestic Prices." https://www.rieti.go.jp/jp/publications/nts/19e078.html

- **Money-GDP Divergence (Japan)**: RIETI column analysis. https://www.rieti.go.jp/jp/columns/s15_0010.html

- **Sahm Rule**: Sahm, Claudia (2019). "Direct Stimulus Payments to Individuals." Brookings Hamilton Project. FRED series: SAHMREALTIME.

---

## Market Consensus Claims

The following claims in the indicator documentation reflect broadly held market practitioner consensus rather than a single citable source. They are marked here for transparency:

- **「機械受注は日本市場で最も注目される先行指標」** — Machine orders is widely regarded as Japan's most market-moving leading indicator. This is practitioner consensus, confirmed by its prominence in ESRI's Composite Leading Index components and coverage in major financial media (Nikkei, Reuters, Bloomberg Japan coverage of monthly machine orders releases).

- **「有効求人倍率は失業率より重視される」** — The job-to-applicant ratio is more watched than unemployment in Japan. This reflects Japan's structural labor shortage context where unemployment stays structurally low (~2.5%) and offers limited cyclical signal. The job ratio provides more granular cyclical information. Source: general market practice, confirmed by BOJ Outlook Reports which regularly reference 有効求人倍率 alongside other labor metrics.

- **「実質賃金が日銀の利上げ判断に影響」** — Real wages influenced BOJ's 2024 rate hike decision. BOJ Governor Ueda's press conferences in 2024 repeatedly cited the importance of a "virtuous cycle between wages and prices" (賃金と物価の好循環) as a precondition for policy normalization. Source: BOJ press conference transcripts, 2024-03-19.

- **Market significance star ratings (⭐)** — The relative importance ratings are editorial assessments based on: publication calendar market impact, trading desk attention, and frequency of citation in central bank communications. They are not derived from a quantitative study.
