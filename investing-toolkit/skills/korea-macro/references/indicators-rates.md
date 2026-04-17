# Rates / 금리

---

## policy-rate: 기준금리 / BOK Base Rate

- **Series code**: K051 (ECOS-KEYSTAT)
- **Source**: Bank of Korea (한국은행) via FinanceDataReader
- **Unit**: Percent (%)
- **Frequency**: Daily (changes at MPC meetings, 8 per year)
- **Publication lag**: 1 business day
- **History**: From 1999 (6,700+ observations)

**What it measures**: The Bank of Korea's benchmark policy rate — the target
for the overnight call rate. This is Korea's primary monetary policy tool,
analogous to the Fed Funds Rate in the US or the BOJ Policy Rate in Japan.

**How to interpret**:
- Rising → BOK is tightening monetary policy. Higher borrowing costs flow
  through to corporate and consumer lending rates. Typically in response to
  inflationary pressures, FX depreciation (KRW weakness), or overheating
  real estate market.
- Falling → BOK is easing to support growth. Lower borrowing costs encourage
  lending, investment, and consumption.

**Market significance**: ⭐⭐⭐
Korea's most important monetary policy signal. The Monetary Policy Committee
(MPC) meets 8 times per year (roughly every 6 weeks). Rate decisions move
KOSPI, KRW/USD, and Korean government bond yields immediately. Forward
guidance in the BOK Governor's press conference is closely watched.

**When to use**: Investment Clock monetary policy axis, BOK rate cycle analysis, Korea-US rate differential tracking, KRW direction assessment.

**Korea-specific context**:
- The BOK typically moves in 25 bps increments, matching the Fed's convention.
  Occasional 50 bps moves signal urgency (as seen in the 2022 tightening cycle).
- Korea's policy rate is heavily influenced by the Fed's rate cycle due to
  the KRW/USD exchange rate channel. When the Korea-US rate differential
  narrows too much, capital outflow pressure intensifies.
- The BOK faces a structural tension between supporting growth (Korea's
  potential growth rate has been declining) and containing household debt
  (among the highest in OECD relative to GDP).
- The "spread" between Korea's base rate and the US Fed Funds Rate is
  a key metric for FX market participants.

**Common pitfalls**:
- Daily frequency means the same rate value repeats for weeks/months between
  MPC meetings. The data is step-function shaped, not continuously varying.
- The base rate alone does not capture the full monetary stance. The BOK
  also uses macroprudential tools (LTV/DTI ratios) that significantly affect
  credit conditions, especially in the real estate market.

---

## call-rate: 콜금리 1일 / Call Rate Overnight

- **Series code**: K052 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Percent (%)
- **Frequency**: Daily
- **Publication lag**: 1 business day
- **History**: From 1999

**What it measures**: The actual overnight interbank lending rate in Korea's
money market. This is the rate at which financial institutions lend reserves
to each other on an overnight basis.

**How to interpret**:
- Typically trades very close to the BOK base rate (within a few bps).
- Deviations from the base rate signal liquidity stress in the banking system.
  Spikes above the base rate indicate tight liquidity; drops below indicate
  excess liquidity.

**Market significance**: ⭐
Primarily a confirmation indicator. The BOK manages liquidity to keep the
call rate near its target. Significant deviations are rare and newsworthy.

**When to use**: Interbank liquidity monitoring, BOK policy transmission confirmation, money market stress detection.

**Common pitfalls**:
- End-of-quarter and end-of-year spikes are seasonal (window dressing).
- The call rate can be suppressed by BOK open market operations even when
  underlying credit conditions are tight.

---

## cd-91d: CD 91일 / CD 91-Day Rate

- **Series code**: K053 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Percent (%)
- **Frequency**: Daily
- **Publication lag**: 1 business day
- **History**: From 1999

**What it measures**: The yield on 91-day certificates of deposit issued by
Korean banks. A key short-term money market benchmark used for pricing
floating-rate loans and derivatives.

**How to interpret**:
- Rising → Short-term funding costs increasing. Banks paying more for
  deposits, which flows through to loan pricing. Can signal tightening
  financial conditions ahead of or beyond BOK rate moves.
- Falling → Short-term funding easing. Banks can fund more cheaply.

**Market significance**: ⭐⭐
The CD 91-day rate is the primary benchmark for floating-rate mortgages
and corporate loans in Korea. Changes directly affect household and
corporate borrowing costs. When the CD rate rises faster than the base
rate, it signals tightening credit conditions beyond BOK policy.

**When to use**: Mortgage rate forecasting (Korea floating-rate benchmark), corporate loan cost tracking, credit conditions assessment.

**Korea-specific context**:
- Many Korean mortgages are indexed to the CD 91-day rate. This makes the
  CD rate directly relevant to household finances and the real estate market.
- The spread between CD 91-day and the base rate reflects bank funding
  stress and credit risk perceptions.

**Common pitfalls**:
- CD rates can diverge from the base rate during periods of banking system
  stress (as seen in 2008, 2022 Legoland crisis).
- The CD rate does not reflect the full cost of bank funding (which also
  includes bank bond spreads, deposit competition, etc.).

---

## treasury-3y: 국고채 3년 / Treasury Bond 3Y

- **Series code**: K056 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Percent (%)
- **Frequency**: Daily
- **Publication lag**: 1 business day
- **History**: From 1999

**What it measures**: The yield on 3-year Korean Treasury Bonds (KTBs).
The most liquid point on Korea's government bond yield curve and the
primary benchmark for medium-term interest rates.

**How to interpret**:
- Rising → Market expectations for tighter monetary policy or higher
  inflation. Can also reflect fiscal concerns or global rate pressure.
- Falling → Market pricing in rate cuts or slowing growth. Flight to
  quality during risk-off episodes.

**Market significance**: ⭐⭐⭐
The 3-year KTB is the most actively traded government bond in Korea and
serves as the primary benchmark for the bond market. KTB 3Y futures on
the Korea Exchange (KRX) are among the most liquid fixed-income derivatives
globally. The 3Y-base rate spread reflects market expectations for future
BOK rate moves.

**When to use**: Bond market benchmark, BOK rate expectation pricing, credit spread base calculation, duration allocation decisions.

**Korea-specific context**:
- Korea's bond market is heavily influenced by foreign investor flows. Foreign
  holdings of KTBs have grown significantly, making the market sensitive to
  global rate differentials and USD/KRW movements.
- The 3Y point is preferred over 10Y for domestic benchmarking because
  Korea's yield curve is relatively flat and the 3Y tenor has the most
  liquidity.

**Common pitfalls**:
- The KTB 3Y yield can move on global factors (US Treasury yields, risk
  appetite) even when domestic conditions are unchanged.
- Daily data includes trading days only. Gaps on holidays/weekends.

---

## treasury-5y: 국고채 5년 / Treasury Bond 5Y

- **Series code**: K062 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Percent (%)
- **Frequency**: Daily
- **Publication lag**: 1 business day
- **History**: From 1999

**What it measures**: The yield on 5-year Korean Treasury Bonds. The
intermediate point on the KTB yield curve.

**How to interpret**:
- Same directional interpretation as KTB 3Y. The 5Y-3Y spread reflects
  term premium and medium-term growth/inflation expectations.
- 5Y-3Y spread widening → Market expects rates to stay higher for longer.
- 5Y-3Y spread narrowing or inverting → Market expects rate cuts.

**Market significance**: ⭐⭐
Less liquid than 3Y but important for understanding the term structure.
Institutional investors (insurers, pension funds) are active in the 5Y
segment.

**When to use**: Term structure analysis, institutional allocation benchmark, yield curve slope measurement (5Y-3Y spread).

**Common pitfalls**:
- Less liquid than 3Y — larger bid-ask spreads can create noise in daily data.

---

## corp-bond-3y: 회사채 AA- 3년 / Corporate Bond 3Y AA-

- **Series code**: K057 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Percent (%)
- **Frequency**: Daily
- **Publication lag**: 1 business day
- **History**: From 1999

**What it measures**: The yield on 3-year corporate bonds rated AA- by
Korean rating agencies. The benchmark for investment-grade corporate
borrowing costs in Korea.

**How to interpret**:
- Rising → Corporate borrowing costs increasing. Can reflect tighter monetary
  policy (base rate effect), widening credit spreads (credit risk), or both.
- Falling → Corporate funding conditions easing.
- The **credit spread** (corp-bond-3y minus treasury-3y) is the key metric:
  - Widening → Credit stress, risk aversion, potential default concerns.
  - Narrowing → Risk appetite improving, credit conditions benign.

**Market significance**: ⭐⭐⭐
The AA- corporate bond yield is the most cited credit market benchmark in
Korea. The credit spread is a leading indicator for financial conditions and
corporate investment. Spread blowouts (as seen during the 2022 Legoland PF
crisis) signal systemic credit stress.

**When to use**: Credit conditions assessment, corporate funding cost tracking, financial stress detection (AA- spread vs KTB), Legoland-style PF crisis monitoring.

**Korea-specific context**:
- Korea's credit rating scale differs from global conventions. Korean AA-
  is broadly equivalent to global A/A-. Do not directly compare Korean AA-
  spreads with US AA- spreads.
- Korea experienced a severe credit market disruption in late 2022 when the
  Legoland project finance default triggered a credit market freeze. The
  AA- credit spread spiked from ~50 bps to ~170 bps.
- Korean conglomerates (재벌, chaebol) dominate the corporate bond market.
  The AA- benchmark reflects chaebol funding costs.

**Common pitfalls**:
- Korean credit ratings have a different calibration than Moody's/S&P/Fitch.
  Korean agencies tend to rate higher than global agencies for the same issuer.
- The corporate bond market is less liquid than KTBs. Spreads can be
  sticky and may not reflect real-time credit conditions.
