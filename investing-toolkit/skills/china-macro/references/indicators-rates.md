# Rates / 利率

---

## lpr-1y: 1 年期 LPR / Loan Prime Rate 1-Year

- **Series code**: akshare:macro_china_lpr (1Y column)
- **Source**: 全国银行间同业拆借中心 NIFC (National Interbank Funding Center) via akshare; panel of 18 commercial banks
- **Unit**: Percent (%)
- **Frequency**: Monthly (fixed on the 20th of each month; daily readings between fixings are unchanged)
- **Publication lag**: Same day as fix (around 9:30am Beijing time)
- **History**: From August 2019 under the current methodology; older history under the superseded "benchmark lending rate" is separate

**What it measures**: The 1-year Loan Prime Rate — the benchmark
lending rate for the majority of corporate and consumer loans in China,
including mortgages prior to 2019. Quoted by 18 panel banks (state-
owned big-four, joint-stock commercial banks, city commercial banks,
and rural commercial banks), published as a trimmed-mean by NIFC.

**How to interpret**:
- Falling → Monetary easing. PBOC is transmitting stimulus to the real
  economy via lower corporate funding costs. Typically follows MLF rate
  cuts by 1-2 months (MLF is the "price guide" for LPR).
- Rising → Tightening. Rare in recent history; last sustained hiking
  cycle was pre-2015.
- Staying flat despite expected cuts → PBOC prioritising CNY stability
  or bank-margin protection (banks resist lower LPR because it
  compresses net interest margins).

**Market significance**: ⭐⭐⭐
The headline rate for Chinese monetary policy in the post-2019 regime.
Moves CSI 300, property-sector equities, CNY, and CGB yields. Any
LPR change is treated as a major policy signal. Cuts of 10 bps are
standard; 25 bps cuts signal stronger easing intent.

**When to use**: Monetary-policy cycle analysis, stimulus-timing
probability, property-sector re-rating signals, corporate-funding-cost
tracking.

**China-specific context**:
- **Replaced the old "benchmark lending rate"** (贷款基准利率) in August
  2019 as part of PBOC's interest-rate-liberalization reform. Before
  2019, the benchmark lending rate was a pure administrative rate;
  LPR is quoted by banks with reference to the MLF rate.
- The 18-bank panel composition is set by PBOC and revised periodically.
- LPR cuts typically lag MLF rate cuts by one fixing cycle (because
  MLF is the policy rate; LPR is the transmission rate).
- Dual-track nature: PBOC also uses quantity tools (RRR, MLF/PSL volume)
  alongside LPR. An RRR cut without an LPR cut is interpreted as
  liquidity support without a policy-rate signal.

**Common pitfalls**:
- LPR prints appear daily in some data feeds but only change on the
  20th of each month. Daily panels repeat the same fix 30 days in a
  row — do not confuse fix-day moves with inter-fixing volatility
  (there is none).
- The LPR is a "floor" benchmark — actual corporate lending rates
  are quoted as "LPR + spread" or "LPR - discount" depending on
  borrower quality. LPR changes affect the reference point, not
  all contracts immediately repricing.
- Historical comparisons with the pre-2019 benchmark lending rate
  are not apples-to-apples; treat the August 2019 break as a regime
  change.

---

## lpr-5y: 5 年期 LPR / Loan Prime Rate 5-Year

- **Series code**: akshare:macro_china_lpr (5Y column)
- **Source**: NIFC panel via akshare
- **Unit**: Percent (%)
- **Frequency**: Monthly (fixed on the 20th; daily readings repeat)
- **Publication lag**: Same day as fix
- **History**: From August 2019 (parallel introduction with 1Y LPR)

**What it measures**: The 5-year Loan Prime Rate — the benchmark
specifically referenced by residential mortgage pricing and longer-
duration corporate loans.

**How to interpret**:
- Falling → Mortgage-cost relief; direct support for property demand
  and household debt-service burden. The most potent single policy
  lever for the property sector.
- Rising → Mortgage tightening; rare post-2020.
- **5Y minus 1Y spread** → Reflects the yield-curve shape embedded in
  the LPR system. Cuts of only 5Y (without 1Y) signal targeted
  property support; cuts of only 1Y signal short-term corporate support.

**Market significance**: ⭐⭐⭐
The property sector's most-watched interest rate. A 5Y LPR cut
triggers rotation into Chinese real-estate equities, property-chain
suppliers (cement, furniture), and property-linked banks. Critical
signal during the 2022-2025 property crisis.

**When to use**: Property-sector cycle timing, mortgage-affordability
analysis, household-deleveraging framing, bank-NIM pressure assessment.

**China-specific context**:
- The 5Y LPR directly prices the vast majority of residential
  mortgages. Mortgage contracts typically reset annually based on
  the 5Y LPR at reset date + contracted spread.
- PBOC has used 5Y-only cuts during the property stress (2022-2024)
  to avoid over-stimulating the broader economy while targeting
  housing. The differential 1Y vs 5Y moves carry policy messages.
- Minimum mortgage rate floors set by PBOC on top of LPR have been
  progressively lowered and ultimately removed — the LPR itself is
  increasingly the binding constraint rather than the floor.

**Common pitfalls**:
- Like 1Y LPR, 5Y LPR only changes on the 20th of each month. Daily
  data repeats.
- The 5Y LPR is not a 5Y government bond yield or a 5Y swap rate —
  it is an administered lending benchmark, distinct from tradable
  fixed-income instruments. Do not chart-overlay with Treasury yields
  without this caveat.
- Not all 5Y+ loans reference the 5Y LPR — some long-duration
  corporate loans reference the 1Y LPR. Mortgage is the clean use case.

---

## rrr-major: 大型金融机构存款准备金率 / Reserve Requirement Ratio (Major Banks)

- **Series code**: akshare:macro_china_reserve_requirement_ratio (column: 大型金融机构-调整后)
- **Source**: 中国人民银行 PBOC via akshare
- **Unit**: Percent (%)
- **Frequency**: Event-driven (changes only on PBOC announcement — typically 1-3 times per year)
- **Publication lag**: Same day as announcement (takes effect ~2 weeks after announcement)
- **History**: From the early 1990s; current calibration range 6.5-11% for major banks

**What it measures**: The required reserve ratio for large deposit-
taking financial institutions — the share of deposits that big banks
(typically the large state-owned banks and joint-stock banks) must
hold as reserves at PBOC rather than lend out. A direct quantity
tool of monetary policy.

**How to interpret**:
- Falling (RRR cut) → PBOC injecting long-term liquidity. A 50 bps RRR
  cut releases roughly 1 trillion yuan of lendable funds into the
  banking system. Bullish for Chinese equities, CNY-neutral-to-
  negative (depending on context), supportive of bonds.
- Rising (RRR hike) → Tightening; absorbing liquidity. Rare
  post-2018.
- Targeted RRR cuts (for specific sectors — SME, rural) are announced
  separately from headline major-bank cuts.

**Market significance**: ⭐⭐⭐
RRR cuts are a major policy signal — often more potent than LPR cuts
because they address liquidity constraints directly. The Chinese
market reads RRR cuts as signalling broader stimulus intent, including
likely fiscal action. Moves CSI 300, CNY, and global risk assets.

**When to use**: Stimulus-regime diagnosis, bank-liquidity-cycle
tracking, Chinese-equity-market turning-point identification.

**China-specific context**:
- China maintains separate RRR tiers for large banks (the "major"
  tier tracked here), small/medium banks, and rural banks. The
  differential is a targeted-easing tool — SME-focused small banks
  often have a 2+ percentage point lower RRR than big banks.
- PBOC's dual-track policy: RRR is a quantity tool, LPR and MLF are
  price tools. Together they form a broader stimulus vocabulary than
  Fed/ECB single-rate regimes.
- Historical high was ~21.5% (2011) — the current ~10% range is a
  structural downshift reflecting lower credit-growth ambitions and
  mature interest-rate transmission.
- PBOC signals RRR moves through State Council communiques 1-2 days
  in advance — rarely a pure surprise.

**Common pitfalls**:
- **Event-driven data**: the "latest" RRR is the last-change date,
  not today. A series that shows a flat line for months simply means
  no change — not stale data. Do not interpret "latest observation
  is 3 months old" as a broken data feed.
- RRR cuts can release different amounts of liquidity per bps
  depending on the deposit base — do not use a simple "50 bps cut =
  X trillion yuan" rule of thumb without checking PBOC's own
  estimate in the announcement.
- akshare's RRR series reports the "major bank" column here;
  small-bank RRR is a separate column and requires different parsing.

---

## shibor-3m: 3 个月 SHIBOR / 3-Month Shanghai Interbank Offered Rate

- **Series code**: akshare:macro_china_shibor_all (3M column)
- **Source**: 全国银行间同业拆借中心 NIFC / shibor.org via akshare
- **Unit**: Percent (%)
- **Frequency**: Daily (business days only; fixed at 11:00am Beijing time)
- **Publication lag**: Same day
- **History**: From October 2006 (4,500+ observations)

**What it measures**: The 3-month Shanghai Interbank Offered Rate —
the rate at which banks lend unsecured funds to other banks in the
Shanghai interbank market for 3 months. Calculated as a trimmed mean
of quotes from 18 panel banks. China's analogue to the pre-reform
USD LIBOR.

**How to interpret**:
- Rising → Interbank funding stress or PBOC tightening liquidity.
  Sustained rises signal credit stress or regulatory tightening of
  wealth-management products (WMPs).
- Falling → Ample interbank liquidity; PBOC easing via open-market
  operations or RRR cuts. Typically precedes broader rate cuts.
- 3M SHIBOR - 3M CGB yield spread is the Chinese equivalent of
  LIBOR-OIS — a measure of bank-credit risk / interbank stress.

**Market significance**: ⭐⭐
Key short-term funding benchmark. Moves Chinese bank NIMs, money-
market fund yields, and short-duration credit pricing. Less
internationally followed than LPR but critical for domestic
fixed-income practitioners.

**When to use**: Interbank liquidity monitoring, WMP/money-market-fund
yield tracking, PBOC liquidity-operation effectiveness assessment,
year-end/quarter-end funding-stress detection.

**China-specific context**:
- SHIBOR panel includes 18 banks across big-four state-owned, joint-
  stock, and foreign-bank categories. Panel composition is publicly
  listed by NIFC.
- Unlike post-reform USD benchmarks (SOFR), SHIBOR remains a
  panel-quotation-based fix; it is not a transaction-derived rate.
  This is a known design weakness but SHIBOR reform has been
  incremental.
- Quarter-end and year-end seasonal spikes are common and large
  (sometimes 50+ bps) due to regulatory ratio requirements
  (LCR/NSFR). These are not "stress" signals but calendar effects.
- Spring Festival effects on SHIBOR are notable — funding demand
  spikes pre-holiday as firms need cash for bonuses and settlement.

**Common pitfalls**:
- SHIBOR is panel-based and can be "managed" — extreme stress may
  not fully reflect in the fix if panel banks avoid extreme quotes.
  The repo rate (7-day, DR007) is often a better real-liquidity read.
- Cross-country interbank-rate comparisons (SHIBOR vs SOFR vs TONAR)
  require accounting for the methodology differences (SHIBOR is
  survey-based; SOFR is transaction-based).
- 3M SHIBOR references the CNY interbank market only — the offshore
  CNH SHIBOR (CNH HIBOR fix) is a different rate for the Hong Kong
  offshore market.

---
