# Cycle / 경기종합지수

---

## Korea 경기종합지수 — Monthly GDP proxy (선행 + 동행 pair)

Korea publishes official GDP quarterly (`gdp-qoq` K258 / `gdp-nominal`
K257). The **선행지수순환변동치 + 동행지수순환변동치** pair, published
monthly by 통계청 (Statistics Korea) via BOK ECOS, collectively proxies
monthly GDP momentum. `coincident-cycle` (K253) is the canonical
"current GDP feel" read; `leading-cycle` (K254) leads it by ~5-7 months.

| Preset | BOK ECOS | 한국어 | Role |
|--------|----------|--------|------|
| `leading-cycle` | K254 | 선행지수순환변동치 | Leads 동행 by ~5-7 months (CI amplitude) |
| `coincident-cycle` | K253 | 동행지수순환변동치 | **Monthly GDP proxy** — coincident |

Cross-market parallels:

- US `nowcast` group (GDPNOW / CFNAI / WEI / OECD CLI) — Fed-aggregated
- JP 景気動向指数 CI trio (先行 / 一致 / 遅行) — 内閣府-aggregated
- TW 景氣對策信號 + leading / coincident index — NDC + DGBAS-aggregated
- **KR 선행 + 동행 CI — BOK ECOS-aggregated**
- CN 三大数据 raw components (no consensus composite)

The lagging CI (후행지수순환변동치) exists at 통계청 KOSIS but is
**not exposed via BOK ECOS KEYSTAT**. Probed K255 / K256 in v1.7.3 —
both map to other series (manufacturing-related, 16 rows). If adding
lagging is needed, would require a direct 통계청/KOSIS scraper
(deferred to v1.9.0 when a BOK ECOS API key is registered).

---

## leading-cycle: 선행지수순환변동치 / Leading CI Cyclical Component

- **Series code**: K254 (ECOS-KEYSTAT)
- **Source**: Bank of Korea (Statistics Korea data) via FinanceDataReader
- **Unit**: Index (100 = trend)
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after reference month
- **History**: From 2000

**What it measures**: The cyclical component of the Composite Leading Index,
isolated from the long-run trend. Measures the deviation of leading economic
indicators from their trend — designed to predict turning points in the
business cycle 6-9 months ahead.

**How to interpret**:
- Above 100 → Economy above trend. Leading indicators suggest continued
  expansion.
- Below 100 → Economy below trend. Leading indicators signal potential
  downturn.
- **Turning points are the key signal**: peak (above 100 then turning down)
  signals imminent slowdown; trough (below 100 then turning up) signals
  recovery ahead.
- The cyclical component is more useful than the composite index level
  because it strips out the secular growth trend.

**Market significance**: ⭐⭐⭐
Korea's most important business cycle timing indicator. The leading cyclical
component historically turns 6-9 months before GDP turning points.
Statistics Korea officially announces business cycle reference dates
(경기기준일) based on this and related indicators.

**When to use**: Business cycle turning point prediction (6-9 month lead), recession probability assessment, Investment Clock phase transition signal.

**Korea-specific context**:
- The leading index components include: building permits, machinery orders,
  stock prices (KOSPI), money supply, export L/C arrivals, and consumer
  expectations. These are forward-looking indicators.
- Korea's business cycle is strongly correlated with the global semiconductor
  cycle. The leading index tends to turn around the same time as global
  chip demand indicators.
- Statistics Korea publishes three cyclical indices: leading (선행, K254),
  coincident (동행, K253), and lagging. Together they form the "3-signal
  system" for business cycle analysis.

**Common pitfalls**:
- Cyclical components are subject to revision as new data arrives and
  trend estimates are updated. End-of-sample turning points can be revised.
- The index uses the HP filter (or similar trend extraction) which is
  known to have end-point bias. Recent values are less reliable.
- A single month above/below 100 does not confirm a turning point. Look
  for 3+ months of consistent direction.

**Monthly GDP proxy role**: This is the **leading companion** of the
`coincident-cycle` monthly GDP proxy (K253). Together they form Korea's
monthly GDP proxy CI pair. See the preamble at the top of this file for
the cross-market comparison.

---

## coincident-cycle: 동행지수순환변동치 / Coincident CI Cyclical Component

- **Series code**: K253 (ECOS-KEYSTAT)
- **Source**: Bank of Korea (Statistics Korea data) via FinanceDataReader
- **Unit**: Index (100 = trend)
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after reference month
- **History**: From 2000

**What it measures**: The cyclical component of the Composite Coincident
Index. Measures the current state of the business cycle — whether the economy
is currently above or below trend. Coincident indicators move in real-time
with the economy.

**How to interpret**:
- Above 100 → Economy currently expanding (above trend).
- Below 100 → Economy currently contracting (below trend).
- The coincident cyclical component confirms what the leading component
  predicted 6-9 months earlier.

**Market significance**: ⭐⭐
Used to confirm the current phase of the business cycle. Less forward-looking
than the leading component, but more reliable for assessing "where we are
now." Statistics Korea uses coincident indicators to officially date
business cycle peaks and troughs.

**When to use**: Current cycle phase confirmation, recession dating, leading-coincident gap analysis for acceleration vs deceleration diagnosis.

**Korea-specific context**:
- Coincident index components include: IPI, services production, retail
  sales, imports, non-farm employment. These reflect current economic
  activity.
- The gap between leading and coincident cyclical components indicates
  whether the economy is accelerating or decelerating. Leading above
  coincident = acceleration ahead; leading below coincident = deceleration
  ahead.

**Common pitfalls**:
- Same revision and end-point bias issues as the leading component.
- "Coincident" still has a ~2 month publication lag. It's coincident in
  economic timing, not in data release timing.
- The coincident component can show the economy "above trend" even during
  a slowdown if the slowdown hasn't yet brought activity below trend.

**Monthly GDP proxy role**: This is **Korea's canonical monthly GDP
proxy** — the CI coincident component plays the same role as Japan's
景気動向指数 一致指数. Pair with `leading-cycle` (K254) for the full
선행-동행 pair. The lagging sibling (후행지수) is not exposed via BOK
ECOS KEYSTAT. See preamble at top of this file for cross-market
comparison.
