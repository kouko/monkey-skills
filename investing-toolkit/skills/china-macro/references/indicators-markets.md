# Markets / 市场指数

---

## 000300.SS: 沪深 300 指数 / CSI 300 Index

- **Series code**: yfinance:000300.SS
- **Source**: 上海证券交易所 + 深圳证券交易所; index maintained by 中证指数有限公司 (China Securities Index Co.); mirrored to Yahoo Finance
- **Unit**: Index points
- **Frequency**: Daily (trading days only; SSE/SZSE trading calendar)
- **Publication lag**: Real-time during trading; end-of-day close available same day
- **History**: From April 2005 (4,500+ trading-day observations)

**What it measures**: The CSI 300 index — the largest 300 A-share
listings by market capitalization across Shanghai Stock Exchange (SSE)
and Shenzhen Stock Exchange (SZSE) combined. The institutional
benchmark for Chinese A-share investing.

**How to interpret**:
- Rising → Broad A-share strength; institutional allocation to
  mainland China equities improving. Moves in response to domestic
  policy (PBOC easing, fiscal stimulus) and global risk appetite.
- Falling → Institutional de-risking from A-shares; typically driven
  by growth concerns, policy uncertainty, or global risk-off.
- Relative performance vs MSCI EM and MSCI World frames the "China
  discount" narrative.

**Market significance**: ⭐⭐⭐
The most-tracked A-share index by institutional investors, both
domestic and foreign. CSI 300 futures (on CFFEX) are the deepest
A-share derivatives market. Foreign flows via Stock Connect (Northbound)
concentrate in CSI 300 constituents.

**When to use**: A-share institutional-allocation tracking, China
equity-market regime diagnosis, hedging via CSI 300 futures, "China
discount" framing vs developed markets.

**China-specific context**:
- Unlike the Shanghai Composite (SSE-only, biased toward state banks),
  CSI 300 is balanced across SSE + SZSE and has more sensible sector
  weights — financials, consumer, tech, industrials each meaningful.
- Constituents rebalanced semi-annually by CSI. Tencent-equivalents
  (Alibaba, Tencent themselves) are listed in Hong Kong and **not**
  CSI 300 constituents — the index underrepresents China's big-tech
  platforms.
- Stock Connect (沪深港通 / Shenzhen-HK, Shanghai-HK) enables foreign
  investors to trade CSI 300 constituents. Northbound flow data is
  a watched sentiment gauge.
- Trading hours: 9:30-11:30, 13:00-15:00 Beijing time. Lunch break is
  unique among major global markets.

**Common pitfalls**:
- yfinance provides end-of-day data; no intraday granularity via this
  preset. For intraday, use exchange direct feeds or brokerage APIs.
- A-share market is closed for Chinese New Year and Golden Week
  (October 1-7) — longer holidays than most global exchanges. Gaps in
  daily series are holidays, not data issues.
- The index is price-only (not total-return) in the standard CSI 300
  quote. CSI 300 Total Return is a separate index for performance
  attribution.

---

## 000001.SS: 上证综合指数 / Shanghai Composite Index (SSEC)

- **Series code**: yfinance:000001.SS
- **Source**: 上海证券交易所 SSE; mirrored to Yahoo Finance
- **Unit**: Index points
- **Frequency**: Daily (SSE trading calendar)
- **Publication lag**: Real-time during trading; EOD same day
- **History**: From the early 1990s (8,000+ trading-day observations)

**What it measures**: The Shanghai Composite Index — a market-
capitalization-weighted index of all A-shares and B-shares listed on
the Shanghai Stock Exchange. The retail-watched "大盘" of Chinese
equity markets.

**How to interpret**:
- Rising → Broad SSE strength; often retail-driven narrative signals.
  The 3,000-point level has historically been a psychological anchor
  for retail investors.
- Falling below key levels (3,000, 2,700) → Retail confidence
  erosion; often coincides with calls for "national team" (state-fund)
  buying to stabilize markets.
- Compared to CSI 300, the SSEC has higher financials/state-bank
  weighting and underweights tech — it tends to lag during tech-led
  rallies and outperform during value/defensive rotations.

**Market significance**: ⭐⭐
More retail-watched than institutionally-tracked. Media coverage of
"Chinese stocks" often references SSEC specifically. Moves with
retail sentiment and policy-signal narratives, but foreign-institutional
allocation decisions more often use CSI 300 as reference.

**When to use**: Retail-sentiment gauge, media-narrative framing of
Chinese equities, historical long-horizon equity analysis (longest
continuous A-share index).

**China-specific context**:
- Commonly referred to as "大盘" (the big market) in Chinese financial
  media — the default Chinese-equity reference.
- Heavy state-bank / SOE financials weighting means SSEC moves with
  credit-cycle and PBOC-easing narratives. Tech-led moves are better
  captured by ChiNext (399006).
- The 3,000-point level is a political-psychological anchor —
  extended periods below have historically triggered policy responses
  (national team buying, short-selling restrictions).
- Includes both A-shares (renminbi-denominated, onshore investors +
  Stock Connect foreign investors) and B-shares (USD-denominated,
  originally for foreign investors but now mostly retail onshore).

**Common pitfalls**:
- SSEC ≠ A-shares overall — it excludes SZSE and ChiNext. For broad
  A-share reads, use CSI 300 or CSI All-Share.
- Historical continuity: base value of 100 in December 1990. Very
  long-history comparisons are reliable, but constituent turnover
  (especially SOE listings) changes the index character over decades.
- Market closures: SSE follows mainland holiday calendar, not HK or
  US calendars. Expect ~250 trading days per year.

---

## 399006.SZ: 创业板指 / ChiNext Index

- **Series code**: yfinance:399006.SZ
- **Source**: 深圳证券交易所 SZSE; mirrored to Yahoo Finance
- **Unit**: Index points
- **Frequency**: Daily (SZSE trading calendar)
- **Publication lag**: Real-time during trading; EOD same day
- **History**: From June 2010 (3,500+ trading-day observations)

**What it measures**: The ChiNext Index (创业板指) — a price-weighted
composite of the 100 largest stocks on the ChiNext board of Shenzhen
Stock Exchange. ChiNext is the growth/innovation-focused board,
broadly comparable to NASDAQ. Heavy weighting in tech, new-energy
(EV, solar), biotech, and semiconductor names.

**How to interpret**:
- Rising → Growth/tech-risk-appetite improving. Correlated with global
  NASDAQ moves. Beneficiary of PBOC easing (long-duration growth
  equities) and narrative catalysts (AI, EV, semi).
- Falling → Growth de-rating. Sharp drawdowns during global tech
  selloffs and domestic regulatory tightening cycles.
- Relative performance vs CSI 300 frames growth-vs-value rotation
  within A-shares.

**Market significance**: ⭐⭐⭐
The growth-tech proxy for A-shares. Moves with global growth/risk-on
cycles, PBOC liquidity, and China tech-narrative catalysts (AI,
deepseek-type moments, EV subsidies). High retail participation makes
it more volatile than CSI 300.

**When to use**: Chinese growth-equity allocation, global tech-cycle
beta read, liquidity-driven rally timing, comparison vs NASDAQ.

**China-specific context**:
- ChiNext listing criteria are less stringent than SSE main board —
  the board was designed to host high-growth, innovation-stage firms.
  Many constituents are profitable but higher-volatility tech and
  new-energy names.
- The 20% daily price limit on ChiNext (vs 10% on SSE/SZSE main
  boards) creates faster reprice dynamics — single-day moves can be
  2x main-board moves.
- Heavy weighting in Contemporary Amperex (CATL), EVE Energy,
  new-energy and semiconductor names. Supply-chain linkages to global
  EV and semi cycles are tight.
- Alongside STAR Market (科创板, SSE 688xxx) as the two growth boards.
  STAR is for hard-tech; ChiNext is broader growth. STAR is tracked
  by separate indices (STAR 50, etc.).

**Common pitfalls**:
- 20% daily limit vs 10% on other A-shares — volatility is structurally
  higher. Single-day returns need normalization for cross-market
  comparisons.
- High retail ownership → sentiment-driven squeezes and liquidity
  risk. Institutional positioning can turn against retail flow.
- ChiNext is not the same as STAR Market — distinct boards, distinct
  indices, distinct listing rules.

---

## ^HSI: 恒生指数 / Hang Seng Index

- **Series code**: yfinance:^HSI
- **Source**: 香港交易所 HKEX; index maintained by Hang Seng Indexes Company; mirrored to Yahoo Finance
- **Unit**: Index points
- **Frequency**: Daily (HKEX trading calendar)
- **Publication lag**: Real-time during trading; EOD same day
- **History**: From 1969 (13,000+ trading-day observations)

**What it measures**: The Hang Seng Index — the most widely followed
Hong Kong equity benchmark. Composite of ~80 largest HKEX listings
spanning mainland Chinese firms (H-shares, red chips), Hong Kong local
firms (HSBC, Swire, Jardine), and Chinese big-tech platforms (Tencent,
Alibaba, Meituan, Xiaomi, JD.com).

**How to interpret**:
- Rising → Hong Kong / China risk appetite improving. Moves with
  global risk sentiment, USD direction (HKD pegged to USD so HSI
  sensitive to US rates via valuation), and China-policy narratives.
- Falling → Typically driven by China-growth concerns, tech-regulation
  crackdowns, or US rate-hike cycles (USD-linked discount rates
  compress HK tech valuations).
- Large weight in Tencent and Alibaba means HSI is partly a big-tech
  trade.

**Market significance**: ⭐⭐⭐
The main foreign-accessible proxy for Chinese equity exposure
alongside ADRs. Southbound flow data via Stock Connect (HK-mainland
retail) is a watched sentiment gauge. Moves with MSCI China, MSCI
EM, and global risk.

**When to use**: Foreign-accessible China exposure, HK/mainland
big-tech positioning, "China discount" tracking, Stock Connect
southbound-flow context.

**China-specific context**:
- **Different regulatory regime from A-shares**: HKEX operates under
  Hong Kong's common-law framework, with SFC (Securities and Futures
  Commission) oversight. HSI listings face different disclosure and
  accounting standards than mainland A-shares.
- **VIE structure risk**: Most big-tech names (Alibaba, Tencent,
  Meituan) are listed via Variable Interest Entity structures due to
  mainland restrictions on foreign ownership of internet/tech sectors.
  The VIE structure has periodic regulatory scrutiny from both
  mainland and US regulators.
- **HKD peg to USD** (7.75-7.85 band) means HSI valuations are
  USD-linked — Fed rate cycles directly affect HSI discount rates.
  Divergences between US monetary policy and China monetary policy
  create valuation-flow tensions.
- HSI had major methodology revisions in 2020-2022 (expanded to
  include more China big-tech, weighting caps introduced, number of
  constituents expanded from 50 to 80+). Historical index continuity
  exists but compositional character has shifted.

**Common pitfalls**:
- HSI is neither pure-China nor pure-HK — it is a hybrid. Do not use
  HSI as a clean mainland-China read (use CSI 300 or HSCEI instead)
  or as a pure HK-domestic read.
- Trading-calendar differences: HKEX and mainland exchanges have
  different holiday calendars (e.g., HK trades on some mainland holidays
  and vice versa). Connect-suspension days create asymmetries.
- Post-2020 index reforms mean long-horizon HSI charts don't reflect
  current composition — the index is much more tech-heavy today than
  historically.

---

## ^HSCE: 恒生中国企业指数 / Hang Seng China Enterprises Index (HSCEI / H-Shares)

- **Series code**: yfinance:^HSCE
- **Source**: 香港交易所 HKEX; Hang Seng Indexes Company; mirrored to Yahoo Finance
- **Unit**: Index points
- **Frequency**: Daily (HKEX trading calendar)
- **Publication lag**: Real-time during trading; EOD same day
- **History**: From 1994 (7,500+ trading-day observations)

**What it measures**: The Hang Seng China Enterprises Index — tracks
the performance of mainland Chinese companies listed on HKEX (H-shares
and increasingly red chips and P-chips). A "pure" mainland-China
equity read accessible to foreign investors, excluding HK locals and
conglomerates that sit in HSI.

**How to interpret**:
- Rising → Mainland China names outperforming within HK market.
  Typically reflects China-policy stimulus or sector-specific catalysts.
- Falling → Mainland China de-rating, often while HK locals (HSBC,
  Swire) hold up relatively better.
- HSCEI vs HSI spread → Captures relative performance of mainland-China
  exposure vs the HK-local/conglomerate part of HSI.

**Market significance**: ⭐⭐
Important for investors wanting Chinese-company exposure without HK
locals. The H-shares vs A-shares discount (same company listed both
in HK and mainland often trades at a discount in HK) is a watched
arbitrage signal — HSCEI vs CSI 300 is the relevant comparison.

**When to use**: Pure-mainland-China HK-listed exposure, H-shares vs
A-shares arbitrage analysis, foreign-institution China allocation
(HSCEI is a common benchmark), hedging via HSCEI futures.

**China-specific context**:
- **H-shares (H 股)**: Companies incorporated in mainland China,
  listed on HKEX, denominated in HKD. Typically financials, state-
  owned enterprises, and industrial companies. The "classical" HSCEI
  constituent type.
- **Red chips (红筹股)**: Mainland-operated companies incorporated
  outside mainland (often Cayman/BVI), listed HK. Historical example:
  CITIC Pacific, China Mobile.
- **P-chips**: Private-sector mainland companies, typically tech,
  listed via Cayman/BVI structures. Many big-tech names are P-chips
  (Tencent, Alibaba) — included in expanded HSCEI since 2018-2020
  reforms.
- **A-H discount / premium**: Same company listed both in HK (H-share)
  and mainland (A-share) can trade at different prices. The A-share
  has historically traded at premium (the "A-H premium index" measures
  this). Foreign investors use HSCEI when the A-H discount offers
  better entry valuation.
- HSCEI futures on HKEX are the main hedging instrument for
  mainland-China exposure.

**Common pitfalls**:
- HSCEI composition changed significantly after 2018 reforms — P-chips
  (private-sector, Cayman-incorporated) were added. Pre-2018 HSCEI
  was closer to pure state-owned H-shares. Charts spanning the reform
  have character change.
- HSCEI is not a complete MSCI China replica — MSCI China includes
  A-shares (via Stock Connect), ADRs, and broader names. HSCEI is
  HK-listed only.
- Trading-calendar issues and A-H arbitrage opportunities arise on
  days when mainland exchanges are closed but HK is open (or vice
  versa) — single-leg trades on these days can have wider spreads.

---
