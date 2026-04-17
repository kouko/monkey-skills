# Sources / 出典 / 資料來源

Primary sources referenced in the taiwan-macro indicator documentation.

---

## Official Institutional Sources

### Central Bank of the Republic of China (Taiwan) / 中央銀行

- **CBC Open Data API**: Statistical data via JSON endpoint. No authentication
  required. Covers interest rates, monetary aggregates, exchange rates, reserve
  money, and financial indicators.
  `https://cpx.cbc.gov.tw/API/DataAPI/Get?FileName={ItemCode}`
  Note: SSL certificate has known issues (missing Subject Key Identifier).

- **CBC Item Code Catalog**: PDF listing all available item codes for the
  Open Data API. Includes rates (EG series), monetary aggregates (EF series),
  balance of payments (BP series), and more.
  https://cpx.cbc.gov.tw

- **Monetary Policy**: CBC board meets quarterly (March, June, September,
  December). Rate adjustments are typically 12.5 bps. The CBC maintains a
  target range for M2 annual growth (e.g., 2.5%–6.5% for recent years).
  https://www.cbc.gov.tw/en/cp-723-2107-B6EC8-2.html

- **Foreign Exchange Reserves**: Taiwan holds ~$570B (2025), among the
  world's largest relative to GDP. The CBC practices "smooth intervention"
  in the FX market.
  https://www.cbc.gov.tw/en/cp-889-2139-7DAC6-2.html

### Directorate-General of Budget, Accounting and Statistics / 行政院主計總處

- **Price Statistics Excel Downloads**: Monthly price indices available as
  .xls files. No authentication required. Uses ROC calendar (民國年).
  Base URL: `https://ws.dgbas.gov.tw/001/Upload/463/relfile/10315/2649/`
  Note: SSL certificate has known issues (unable to get local issuer certificate).

  Available files:
  - `cpispl.xls` — Consumer Price Index (CPI)
  - `cpisplexvfe.xls` — Core CPI (excl. fruits, vegetables, energy)
  - `cpisplsa.xls` — Seasonally adjusted CPI
  - `ppispl.xls` — Producer/Wholesale Price Index (PPI/WPI)
  - `ipispl.xls` — Import Price Index
  - `epispl.xls` — Export Price Index

- **CPI Methodology**: Taiwan's CPI basket is updated every 5 years based on
  the Household Income and Expenditure Survey. Current base year: 105 年
  (2016 = 100). Coverage: ~400 items in 7 major groups.
  https://www.dgbas.gov.tw/point.asp?index=2

- **ROC Calendar Convention**: All DGBAS Excel files use 民國年 (ROC year).
  Conversion: 民國年 + 1911 = 西元年. Example: 民國115年 = 2026.

### National Development Council / 國家發展委員會 (NDC)

- **Business Cycle Monitoring Indicator (景氣對策信號)**: Taiwan's "traffic
  light" business cycle indicator system. Assigns colored lights (red/yellow-red/
  green/yellow-blue/blue) based on a composite score of 9 economic indicators.
  Not currently accessible programmatically (Cloudflare protection).
  https://index.ndc.gov.tw/

### Ministry of Economic Affairs / 經濟部 (MOEA)

- **Industrial Production Index (工業生產指數)**: Monthly index of manufacturing
  and industrial output. Not currently accessible programmatically.
  https://www.moea.gov.tw/MNS/dos/home/Home.aspx

- **Export Orders (外銷訂單)**: Monthly survey of export orders received by
  Taiwan manufacturers. A leading indicator for actual exports. Not currently
  accessible programmatically.

### Chunghwa Institution for Economic Research / 中華經濟研究院 (CIER)

- **Taiwan PMI (製造業採購經理人指數)**: Monthly purchasing managers' index.
  Not available via public API.
  https://www.cier.edu.tw/

---

## Taiwan-Specific Economic Context

### Export-Dependent Structure

Taiwan's economy is heavily export-dependent (exports ~70% of GDP). The
semiconductor industry alone accounts for ~15% of GDP and ~35% of exports.
TSMC's capex decisions and order books are quasi-macro indicators for Taiwan.

### CBC Monetary Policy Characteristics

- **Gradualism**: Rate changes of 12.5 bps (half the standard 25 bps used
  by the Fed, ECB, and BOJ). This reflects Taiwan's preference for stability
  and the CBC's dual focus on price stability and exchange rate stability.
- **FX Intervention**: The CBC actively manages TWD volatility. Taiwan appears
  regularly on the US Treasury's currency monitoring list. FX reserve changes
  are a proxy for intervention magnitude.
- **M2 Targeting**: The CBC is one of the few central banks that still sets
  explicit monetary aggregate growth targets (M2 annual growth target range).

### Price Index Peculiarities

- **Core CPI definition**: Taiwan excludes fruits, vegetables, and energy
  (蔬果及能源). This differs from:
  - US: excludes all food and energy
  - Japan: excludes fresh food only (生鮮食品を除く)
- **Government price controls**: Electricity (台電), water (台水), natural
  gas (中油), and public transportation fares are government-administered.
  These can suppress CPI during commodity price surges, creating delayed
  adjustment spikes.
- **Typhoon-driven food inflation**: Taiwan experiences seasonal produce
  price spikes during typhoon season (July-October). This is why core CPI
  specifically excludes fruits and vegetables.

---

## Market Consensus Claims

The following claims reflect broadly held market practitioner consensus:

- **「央行是最會賺錢的央行」** — The CBC is often called "the most profitable
  central bank" due to its massive FX reserves and the seigniorage from TWD
  creation for FX intervention. The CBC's profits are remitted to the national
  treasury and represent a significant fiscal revenue source. This creates a
  structural incentive to maintain FX reserves, which in turn affects M2 growth.

- **「半導體是台灣的經濟命脈」** — Semiconductors are Taiwan's economic lifeline.
  When global chip demand falters, it affects Taiwan's GDP, exports, employment,
  and tax revenue disproportionately relative to other economies.

- **Market significance star ratings (⭐)** — The relative importance ratings
  are editorial assessments based on: CBC policy communication emphasis, market
  participant attention, and frequency of citation in financial media. They are
  not derived from a quantitative study.
