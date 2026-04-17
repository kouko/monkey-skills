# FX / 外汇

---

## DEXCHUS: 人民币兑美元中间价（FRED 口径）/ Chinese Yuan per USD (CNY/USD)

- **Series code**: FRED:DEXCHUS
- **Source**: Federal Reserve Board (Board of Governors of the Federal Reserve System) via FRED — ultimate source is typically PBOC's daily fixing (中间价) transmitted via the Fed's H.10 release
- **Unit**: CNY per USD (i.e., 7.20 = 7.20 yuan per 1 USD)
- **Frequency**: Daily (business days only; skips US Federal Reserve holidays and some Chinese holidays)
- **Publication lag**: 1 business day (T+1)
- **History**: From 1981 (11,000+ observations); floating-regime structure since 2005

**What it measures**: The CNY/USD exchange rate as reported in the
Federal Reserve's H.10 statistical release. Approximates the PBOC
daily midpoint fix (中间价), around which the onshore CNY is allowed
to trade within a ±2% band.

**How to interpret**:
- Rising (higher yuan-per-USD number) → CNY depreciation vs USD.
  Typically driven by capital outflow pressure, growth concerns,
  PBOC easing that widens US-China rate differentials, or USD
  strength broadly.
- Falling → CNY appreciation. Driven by trade-surplus inflows, capital
  return from risk-off, Fed rate cuts narrowing differentials, or
  policy signals of "stable CNY."
- The 7.00 and 7.30 levels have been psychological-political anchors.
  PBOC-perceived "defense" around 7.30-7.35 has been evident during
  2023-2025 episodes.

**Market significance**: ⭐⭐⭐
The CNY/USD is a core EM-FX and global-risk indicator. Moves Chinese
equities (weaker CNY = valuation compression for USD-linked metrics),
Asian currencies via regional anchoring, and commodity prices. Major
CNY moves feed directly into global risk-sentiment reads.

**When to use**: CNY regime diagnosis, EM FX positioning, Chinese-
equity valuation adjustments, US-China rate-differential analysis.

**China-specific context**:
- **Managed float with daily fix**: PBOC publishes the CNY/USD
  midpoint (中间价) each morning at 9:15am Beijing time. The onshore
  CNY (CNY) is allowed to trade ±2% around this fix during the day.
  Repeated wider-band pressure prompts PBOC verbal intervention or
  direct FX operations.
- **Onshore CNY vs offshore CNH**: CNY trades onshore (Shanghai); CNH
  trades offshore (primarily HK). Under stress, CNH can diverge
  meaningfully from CNY (wider CNH depreciation reflects offshore
  speculative pressure). DEXCHUS tracks the onshore CNY rate.
- **2015 August devaluation**: PBOC's unexpected ~3% CNY devaluation
  in August 2015 was a regime-shift event that introduced more
  market-determined fixing methodology. The "counter-cyclical factor"
  in the fix has been adjusted several times since.
- **Trade-weighted basket (CFETS RMB Index)**: PBOC also publishes a
  trade-weighted CNY index (CFETS 指数) — often more relevant than
  CNY/USD for competitiveness analysis. The index-focused narrative
  ("stable against the basket, flexible vs USD") has framed several
  PBOC statements.

**Common pitfalls**:
- **FRED DEXCHUS approximates but does not exactly equal PBOC's fix**.
  FRED uses the Fed's H.10 methodology which may reference a specific
  NY-observed rate, not the Beijing AM fix. Small discrepancies are
  normal.
- Series skips both US Federal Reserve holidays and certain Chinese
  holidays — daily data has gaps.
- CNH (offshore) is not captured by this series. When CNY/CNH diverge
  sharply, DEXCHUS tells only half the story — cross-check with CNH
  quotes (e.g., USDCNH on Bloomberg/Reuters).
- Historical pre-2005 data reflects the fixed-peg regime; post-2005
  data is the floating (managed) regime. The break is well documented
  but creates discontinuity in long-horizon analytics.

---

## TRESEGCNM052N: 中国外汇储备（剔除黄金）/ China FX Reserves Excluding Gold

- **Series code**: FRED:TRESEGCNM052N
- **Source**: International Monetary Fund (IMF) International Financial Statistics (IFS); ultimate source is 国家外汇管理局 SAFE (State Administration of Foreign Exchange) + PBOC; mirrored by FRED from IMF data
- **Unit**: USD millions (typically reported as USD billions or trillions)
- **Frequency**: Monthly
- **Publication lag**: ~2-3 months (IMF IFS pipeline — slower than SAFE's direct monthly release by ~1-2 months)
- **History**: From the 1970s (600+ monthly observations)

**What it measures**: China's official foreign-exchange reserves
excluding monetary gold, denominated in USD. Comprises holdings of
foreign currencies, deposits at foreign central banks and BIS,
foreign-government securities (primarily US Treasuries, JGBs, European
sovereigns), and IMF-related claims.

**How to interpret**:
- Rising → Either trade-surplus inflows accumulating, or valuation
  effects (USD weakness vs EUR/JPY lifts USD-reported value of
  non-USD reserves), or both. Typically a modestly positive signal
  for CNY stability.
- Falling → Either PBOC FX intervention (selling USD to defend CNY),
  capital outflows, or valuation effects (USD strength compressing
  USD-reported non-USD reserves).
- Level ranges: China's FX reserves peaked near $4 trillion in 2014,
  trough near $3 trillion in early 2017 after capital-outflow episode,
  and have stabilized in the $3.1-3.3 trillion range through 2025.

**Market significance**: ⭐⭐
Watched for signals about PBOC FX intervention and capital-flow
dynamics. Declines below $3 trillion trigger market attention as a
"de facto defense line." Moves CNY via signaling channel more than
via flow-mechanics.

**When to use**: PBOC intervention detection, capital-outflow
diagnosis, CNY fundamental-anchor analysis, geopolitical / de-
dollarization narrative framing.

**China-specific context**:
- **World's largest FX reserve holder** by a wide margin (approximately
  $3.2-3.3 trillion vs next-largest Japan at ~$1.2 trillion as of
  Q1 2026).
- **Composition is not fully disclosed**, but estimates suggest
  ~60-65% USD, ~20-25% EUR, 5-10% JPY, and smaller allocations to
  GBP/CAD/AUD. The exact composition is a PBOC state secret.
- **Valuation effects dominate monthly moves** — the reserves are
  reported in USD, but ~35-40% is non-USD, so USD-basket moves
  mechanically change the USD-reported value even if PBOC took no
  action. Strategists decompose monthly moves into
  valuation-vs-intervention components.
- **Separate from PBOC's balance sheet directly**: reserves are
  SAFE-managed, but PBOC's "Other Foreign Assets" on its balance
  sheet can reflect off-balance-sheet FX operations (policy-bank FX
  deposits, CIPS-related flows) not captured in the headline reserves.
- SAFE publishes the reserve data monthly (usually around the 7th of
  following month); IMF's IFS pipeline (which FRED mirrors) lags
  SAFE's direct release by 1-2 months.

**Common pitfalls**:
- **FRED TRESEGCNM052N via IMF IFS lags SAFE's direct release** by
  ~1-2 months. For fresher data, check SAFE's English-language
  release (safe.gov.cn) when accessible, or use a Bloomberg/Reuters
  terminal.
- Monthly moves are heavily distorted by valuation effects. A
  "$100 billion decline" during a strong-USD month may be entirely
  valuation, not intervention. Always check the EUR/USD and USD/JPY
  moves alongside.
- The reserves figure excludes gold, while PBOC's gold holdings
  (separately reported) have been steadily growing in 2023-2025 as
  part of reserve-diversification strategy. Combined "reserves +
  gold" is a separate aggregate.
- FRED's series code stability: TRESEGCNM052N has been stable
  historically but IMF series codes occasionally change during
  methodology updates — verify series code freshness periodically.

---
