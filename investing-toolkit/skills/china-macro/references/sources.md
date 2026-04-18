# Sources / 出处 / 資料來源

Primary sources referenced in the china-macro indicator documentation.

---

## Official Institutional Sources

### National Bureau of Statistics / 国家统计局 (NBS)

- **NBS Data Portal**: The authoritative source for Chinese macro
  data — CPI, PPI, GDP, industrial production, retail sales, fixed-
  asset investment, surveyed urban unemployment, and the official
  PMI (manufacturing and non-manufacturing). Most presets in the
  china-macro skill ultimately trace back to NBS releases.
  https://www.stats.gov.cn/

- **NBS English Site**: The English-language portal mirrors major
  releases with ~1 day additional lag. Useful for international
  investors; access can be intermittent from some jurisdictions.
  https://www.stats.gov.cn/english/

- **NBS Two-Track Data Releases**: NBS publishes (1) headline press
  releases same-day as the figure at 10:00am Beijing time, and
  (2) detailed data files uploaded to the statistical database over
  following days. Real-time market reactions are driven by (1); deep
  analysis uses (2).

- **Spring Festival (春节) Caveat**: NBS routinely reports January and
  February data as "Jan-Feb combined" (1-2月累计) because Chinese New
  Year timing distorts month-on-month comparisons. This is standard
  practice — the combined Jan-Feb YoY is the clean read.

### People's Bank of China / 中国人民银行 (PBOC)

- **PBOC Website**: Publishes M1, M2, AFRE (社融), new loans, RRR
  announcements, MLF operations, daily CNY/USD fixing (中间价), and
  open-market operation data.
  http://www.pbc.gov.cn/

- **PBOC English Site**: Lagged mirror of the Chinese site.
  http://www.pbc.gov.cn/en/

- **Monetary Policy Reports**: Quarterly 货币政策执行报告 (Monetary
  Policy Implementation Reports) provide PBOC's framework and forward-
  guidance narrative. Closely watched for policy-reaction-function
  reads.

- **Dual-track Monetary Policy**: PBOC uses both quantity tools (RRR,
  MLF volume, PSL, pledged supplementary lending to policy banks) and
  price tools (LPR, MLF rate, 7-day reverse repo rate). This is
  structurally different from Fed/ECB/BOJ single-rate regimes.

### State Administration of Foreign Exchange / 国家外汇管理局 (SAFE)

- **SAFE Website**: Monthly FX reserves data (外汇储备), quarterly
  balance-of-payments, cross-border capital-flow data, and QFII/RQFII
  quotas.
  https://www.safe.gov.cn/

- **SAFE English Site**: Mirror of Chinese site with some lag.
  https://www.safe.gov.cn/en/

### General Administration of Customs / 海关总署 (GAC)

- **GAC Website**: Monthly trade data (exports, imports, trade balance),
  released ~15 days after reference month in both USD and CNY. The
  fastest and most authoritative source for Chinese merchandise trade.
  http://english.customs.gov.cn/

### National Interbank Funding Center / 全国银行间同业拆借中心 (NIFC)

- **NIFC / CFETS (China Foreign Exchange Trade System)**: Publishes
  LPR (Loan Prime Rate) on the 20th of each month. Also operates the
  interbank FX market and the CFETS RMB Index (trade-weighted CNY).
  https://www.chinamoney.com.cn/

- **SHIBOR.org**: Operated by NIFC. Daily SHIBOR fix at 11:00am Beijing
  time for overnight through 1Y tenors, based on panel quotes from
  18 banks.
  http://www.shibor.org/

### Caixin Media + S&P Global

- **Caixin PMI (manufacturing and services)**: Private-sector PMI
  compiled by S&P Global (previously IHS Markit) on behalf of Caixin.
  Covers ~500 manufacturers and ~400 service firms. Smaller sample than
  NBS PMI but skewed toward private, export-oriented, and SME firms —
  the "private economy" cross-check to the SOE-tilted official reading.
  https://www.caixinglobal.com/

- **Release Timing**: Caixin manufacturing PMI on the first business
  day of the following month; Caixin services PMI on the third business
  day. Official NBS PMI releases on the last day of the reference month.

---

## FRED (Federal Reserve Bank of St. Louis)

- **DEXCHUS**: Daily CNY/USD exchange rate from the Fed's H.10
  statistical release, approximating PBOC's daily fix. Used where
  akshare does not provide a clean daily CNY/USD time series accessible
  internationally.
  https://fred.stlouisfed.org/series/DEXCHUS

- **TRESEGCNM052N**: Monthly Chinese FX reserves excluding gold,
  sourced from IMF International Financial Statistics (IFS). Lags
  SAFE's direct release by ~1-2 months but provides internationally
  standardized USD-denominated values.
  https://fred.stlouisfed.org/series/TRESEGCNM052N

- **No API key required**: FRED CSV endpoints are publicly accessible.

---

## yfinance (Market Indices)

- **PyPI**: `yfinance` (community-maintained)
- **Source**: Yahoo Finance public endpoints, which in turn aggregate
  from exchange data feeds (SSE, SZSE, HKEX) with delayed or end-of-day
  cadence. No API key required.
- **Tickers used by china-macro**:
  - `000300.SS` → CSI 300 (Shanghai + Shenzhen 300 largest A-shares)
  - `000001.SS` → Shanghai Composite (SSEC)
  - `399006.SZ` → ChiNext (growth board index)
  - `^HSI` → Hang Seng Index (Hong Kong main index)
  - `^HSCE` → Hang Seng China Enterprises (HSCEI / H-shares)
- **Trading calendar caveats**: mainland SSE/SZSE follow the mainland
  China holiday calendar (longest closures are Spring Festival and
  Golden Week in October). HKEX follows the HK calendar, which differs.
  Cross-market analysis must account for asymmetric holidays.
- **Limitations**: yfinance provides end-of-day data reliably; intraday
  granularity and delisted/historical-index constituents may be
  missing. For intraday or full-constituent history, use exchange
  direct feeds or paid terminals (Bloomberg, Wind, Choice).

---

## akshare (Data Access Library)

- **PyPI**: `akshare==1.18.55` (pinned for reproducibility)
- **GitHub**: https://github.com/akfamily/akshare (9k+ stars)
- **How it works**: akshare is a community-maintained Python library
  that wraps public Chinese financial and macro data feeds behind a
  unified Python API. For china-macro presets, it pulls from:
  - **Eastmoney (东方财富)**: Market data, some macro series
  - **chinamoney.com.cn (CFETS)**: LPR and interbank data
  - **shibor.org**: SHIBOR fixes
  - **NBS mirrors**: CPI, PPI, GDP, M2, industrial production, retail
  - **Investing.com free calendar feed**: Some monthly macro releases
    (industrial YoY, exports/imports, trade balance, Caixin PMI) are
    sourced from this endpoint. This route has a known staleness
    issue — feeds can lag primary sources by up to **~8 months**
    during maintenance gaps.
- **No API key required**: akshare accesses public endpoints
  (exchange websites, government open-data pages, free calendar
  feeds). No registration or billing involved.
- **Dependencies**: pandas, numpy, requests, beautifulsoup4, lxml,
  openpyxl, matplotlib.

### akshare Limitations

- **~8-month staleness for investing.com-mirrored series**:
  `macro_china_industrial_production_yoy`, `macro_china_exports_yoy`,
  `macro_china_imports_yoy`, and `macro_china_trade_balance` source
  from investing.com's free calendar endpoint, which experiences
  periodic gaps. If fresher data is critical, cross-check against
  the primary source (NBS, customs) when accessible.

- **Caixin PMI (excluded 2026-04-18)**: Both
  `macro_china_cx_pmi_yearly` and `macro_china_cx_services_pmi_yearly`
  were the same investing.com-mirrored endpoint and ran consistently
  7-8 months stale since mid-2025. PMI's value is timeliness, so a
  stale Caixin PMI defeats the indicator's purpose. The presets
  `pmi-caixin-manufacturing` and `pmi-caixin-services` were removed
  from `akshare_client.py`. The skill still ships official NBS
  manufacturing + non-manufacturing PMI (fresh ~47d). For a fresh
  Caixin read, consult S&P Global's monthly Caixin PMI release page
  or the Caixin Global news feed directly; a dedicated
  `caixin_client.py` can be revived here if a stable free source
  emerges.

- **MLF rate not directly exposed**: akshare does not provide a clean
  MLF rate time series. LPR is the closest accessible proxy for
  Chinese policy-rate reads via akshare.

- **Blocked-network sensitivity**: Some akshare endpoints pull from
  mainland-China sites directly. From networks that block or throttle
  mainland China traffic (some corporate networks, certain VPN
  configurations), specific presets may fail intermittently.

---

## China-Specific Economic Context

### Chinese New Year (春节) Data Distortion

Chinese New Year falls in late January or February (varies yearly
on lunar calendar). Factory shutdowns, retail spikes, and travel
disruptions distort month-on-month data severely. **Consequences**:
- NBS combines January and February data into "Jan-Feb combined" YoY
  for CPI, industrial production, retail sales, FAI, and others.
- Always use YoY comparisons for Jan-Feb prints, not MoM.
- Trade data (exports/imports) swings wildly in Jan-Feb due to
  pre-holiday production surge and post-holiday pause.
- Analysts commonly work with Jan-Feb combined readings rather than
  single-month Jan or Feb prints.

### PPI Deflation Regime (2023-2025)

China's PPI has been in YoY deflation for most of the 2023-2025
period. Underlying drivers:
- **Property-chain unwind**: steel, cement, glass demand collapse
  following the 2021-2022 property-developer stress (Evergrande,
  Country Garden).
- **EV and solar overcapacity**: domestic manufacturing capacity
  has outrun demand, driving output prices below cost in some
  sub-sectors.
- **Weak export pricing power**: Chinese manufacturers competing on
  price in global markets.

The PPI deflation alongside soft CPI has fueled the "Japanification
of China" debate — comparisons to Japan's post-1990 balance-sheet
recession and deflation trap.

### 社融 (AFRE) Uniqueness

China's Aggregate Financing to the Real Economy (社会融资规模, AFRE)
is a uniquely Chinese credit aggregate designed by PBOC in 2011. It
captures:
- Bank loans (~60-70%)
- Shadow-banking credit (trust loans, entrusted loans, undiscounted
  bankers' acceptances) — materially shrunk post-2017 crackdown
- Net corporate bond issuance
- Net government bond issuance (including LGFV and special bonds)
- Equity financing (IPOs, SPOs)
- Miscellaneous (asset-backed securities, specific policy instruments)

There is no direct US or European equivalent. **AFRE is broader than
M2** and often called "the most important Chinese credit indicator"
by domestic strategists. See `indicators-money.md` for details.

### State vs Private Economy Divergence (NBS PMI vs Caixin PMI)

NBS official PMI surveys 3,000+ firms skewed toward large and state-
owned enterprises. Caixin PMI surveys ~500 firms skewed toward
private, export-oriented, and SME manufacturers.

**Divergences are signal, not noise**:
- NBS > Caixin → State-sector strength (SOE infrastructure demand,
  preferential credit) outpacing private-sector weakness.
- NBS < Caixin → Private export recovery ahead of SOE/infrastructure
  stimulus.

The sustained gap in recent years reflects the dual-track Chinese
economy: state-led investment continuing while private-sector
confidence weakens.

### CNY Onshore (CNY) vs Offshore (CNH) Split

- **Onshore CNY**: Traded in Shanghai, subject to PBOC daily fixing
  (中间价) and ±2% trading band. Governed by capital-account controls.
- **Offshore CNH**: Traded primarily in Hong Kong (and to lesser
  extent London, Singapore). More freely tradable by foreign investors.
  Can diverge from CNY under stress.
- **Divergence signals**: CNH weaker than CNY → offshore speculative
  pressure, capital-outflow expectations, or PBOC-perceived fix
  disconnected from market pricing. CNH stronger than CNY → foreign
  demand exceeding supply (rare).

DEXCHUS (the FRED CNY/USD series used by this skill) tracks the
onshore CNY rate only; CNH is a separate instrument.

### VIE, ADR Delisting, and "China Discount"

Major Chinese internet platforms (Alibaba, Tencent, Meituan, JD.com)
are listed in Hong Kong and/or as US ADRs via Variable Interest Entity
(VIE) structures — a legal workaround to mainland restrictions on
foreign ownership of internet/tech sectors. VIE structure creates:

- **Regulatory risk**: Mainland regulators (CSRC, CAC) have periodically
  signaled scrutiny; US regulators (HFCAA, PCAOB audit access) have
  also scrutinized ADR listings.
- **ADR delisting risk**: Some Chinese ADRs were delisted or
  voluntarily delisted from US exchanges in 2022-2024 following
  regulatory pressure; many added HK secondary listings as hedges.
- **Valuation compression**: MSCI China / HSI trade at persistent
  P/E discounts to developed-market benchmarks.

### SOE / POE Structure — the Chaebol-Equivalent Layer

China does not have Korea-style chaebol conglomerates but has
comparable structural concentration:
- **State-owned enterprises (SOEs, 国企, 央企)**: Large state-
  controlled firms (Sinopec, PetroChina, CRRC, ICBC, state banks).
  Dominate finance, energy, telecoms, rail, construction. ~50% of
  A-share market cap by some measures.
- **Privately-owned enterprises (POEs, 民营企业)**: Tech platforms
  (Tencent, Alibaba), EV/solar (BYD, LONGi, CATL), consumer
  (Moutai, Midea). Innovation and export leadership.

State-led stimulus flows disproportionately to SOEs via policy-bank
lending (CDB, EXIM Bank) and infrastructure-project pipelines. This
creates the NBS PMI > Caixin PMI divergence documented above.

---

## Market Consensus Claims

The following claims reflect broadly held market-practitioner consensus
(as of Q1 2026):

- **"China discount"** — MSCI China / HSI / CSI 300 trade at persistent
  valuation discounts (P/E, P/B) vs developed-market indices.
  Attributed to VIE structure risk, ADR delisting risk, data-
  localization and tech-sector regulatory uncertainty, geopolitical
  (US-China) tensions, opaque government intervention in markets,
  and lagging corporate governance reforms. The Chinese government
  has announced "Value-Up"-style programmes but market reception has
  been mixed.

- **"Japanification of China"** — Parallel drawn between China's
  2023-2025 combination of (1) property-sector deleveraging,
  (2) demographic decline (labor force shrinking from 2022 peak),
  (3) PPI deflation with soft CPI, and (4) households preferring
  deposits over equity/property, to Japan's post-1990 balance-sheet
  recession. Counter-arguments cite China's still-meaningful growth,
  policy-response toolkit, and continued urbanization.

- **"Common prosperity" policy implications** — Xi Jinping's 共同富裕
  framework (emphasized from 2021) has driven crackdowns on education
  (K-12 tutoring ban 2021), gaming (restricted play-time 2021),
  internet platforms (Alibaba fine 2021, Didi delisting 2021), and
  real-estate (the "three red lines" policy 2020-2021). Market
  interpretation: structural cap on tech-platform margins; ongoing
  regulatory risk premium.

- **Evergrande / real-estate overhang** — The collapse of Evergrande
  (default September 2021) and Country Garden (2023) marked the end
  of the property-driven growth model. Property + related sectors
  historically ~25-30% of Chinese GDP. Household net worth is
  ~70% real-estate — the deleveraging is both a demand drag
  (wealth effect) and a credit drag (banks exposed to developer and
  mortgage risk).

- **Semiconductor decoupling** — US CHIPS Act (2022), export controls
  on advanced semis and equipment (ASML EUV, NVIDIA GPUs) have
  accelerated Chinese domestic semi investment. SMIC, Hua Hong,
  YMTC, CXMT are the focal domestic players. The semi-cycle is
  increasingly bifurcated between US-friendly supply chains and
  Chinese self-sufficiency chains.

- **Market significance ratings** — The relative importance ratings
  (⭐⭐⭐, ⭐⭐, ⭐) in the indicator documentation are editorial
  assessments based on: PBOC policy-communication emphasis, market
  participant attention, frequency of citation in financial media,
  and typical market-moving impact. They are not derived from a
  quantitative study.
