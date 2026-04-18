# US — Macro Regime Thresholds & Calibration

**Authority**: Federal Reserve System | **Currency**: USD | **Calibration vintage**: 2026-Q1

## Grounding Status (as of 2026-04-18)

**Last full verification**: 2026-04-18 via `../research/grounding-v1.9.0.md`
(5-country parallel grounding note; US section).

**Verified (✅)**: DFII5/DFII10 readings, FOMC Dec 2025 SEP arithmetic,
Williams Dec 2025 + Jan 2026 "modestly restrictive" language, 2012
FOMC 2% target adoption.

**Corrected (🔴 in prior draft → fixed below)**:
1. **FAIT retired 2025-08** — Powell Jackson Hole 2025-08-22 dropped
   FAIT "makeup" strategy, returned to **FIT** (Flexible Inflation
   Targeting). Prior draft said FAIT still active.
2. **HLW r\* ≈ 0.75% real** (2025-Q4 NY Fed vintage) — NOT 1.42%.
   Williams maintains r* has not meaningfully risen post-COVID.
3. **Lubik-Matthes r\* = 1.68% real** (2025-Q4, updated 2026-03-10)
   — NOT 2.15%.

**Partial updates (⚠️)**: CBO 2026 forecast = 4.6% unemp (from earlier
4.5-4.6%); FOMC Dec 2025 SEP full specs inserted.

**Next recalibration**: March 2026 (Q1 SEP + CBO Outlook refresh).

---

---

## Inflation Target

- **Official target**: **2%** (PCE headline, adopted 2012-01-25;
  re-affirmed at Aug 2025 Jackson Hole framework review)
- **Framework (current, since Aug 2025)**: **Flexible Inflation
  Targeting (FIT)** — Powell 2025-08-22 framework review DROPPED
  the 2020 FAIT "makeup" strategy, removed ELB-centric language,
  removed employment "shortfalls" language; returned to symmetric FIT.
- **Tolerance band**: no explicit numerical band — FOMC language
  is "symmetric" around 2%. Under FIT (post 2025-08), deviations
  above and below 2% are treated equally (unlike FAIT 2020-2025
  which tolerated moderate overshoot).
- **Current reading**: CPI YoY ~2.5% (2026-Q1); PCE ~2.3%
- **2026 outlook**: Williams (NY Fed Jan 2026 speech) — inflation
  reaches ~2.5% in 2026, peaks 2.75-3.0% H1 2026, 2% goal by 2027
- **Signal**: Above target `> 2.2%` / At target `1.8-2.2%` / Below target `< 1.8%`

---

## Labor Market Tightness (NAIRU / NROU)

- **CBO NROU estimate**: **~4.4%** (CBO renamed "Natural Rate" → "Noncyclical
  Rate of Unemployment", NROU series on FRED)
- **CBO 2026 unemployment forecast**: **4.6%** (2026 year-avg;
  rises from 4.5% end-2025), per CBO Budget & Economic Outlook
  2026-2036 (Feb 2026, publication 61882). Declines to 4.4% by
  2028-29, stabilizing at 4.2% thereafter.
- **Bands (standard ± 0.5 pp from NAIRU)**:
  - `unemp < 3.9%` → **Tight**
  - `3.9% ≤ unemp ≤ 4.9%` → **Balanced**
  - `unemp > 4.9%` → **Slack**
- **Fed framework**: "maximum employment" is a broad assessment;
  single unemployment-rate threshold overstates precision.

---

## Policy Rate Neutrality

- **Current Fed funds target**: **3.50-3.75%** (after 75 bp of cuts in
  2024, 2026-Q1)
- **Nominal neutral estimates (FOMC Dec 10 2025 SEP, Table 1 longer-run row)**:
  - Median: **3.0%**
  - Central tendency: **2.8-3.5%**
  - Full range: **2.6-3.9%** (17-19 dots in Figure 2)
  - PCE longer-run median: 2.0% (all participants)
  - → implied **real median neutral: 1.0%**
- **Implied real neutral (multiple models, 2025-Q4 vintage)**:
  - **HLW (NY Fed, Holston-Laubach-Williams 2023 post-COVID, Q4 2025)**:
    **~0.75% real** (Williams maintains r\* has NOT meaningfully risen
    post-COVID; GDP-weighted r\* for CA+EA+UK+US ~0.5% per Williams
    Aug 2025)
  - **Lubik-Matthes (Richmond Fed, Q4 2025, updated 2026-03-10)**:
    **1.68% real**
  - Dec 2025 SEP longer-run real: **1.0% median**, central tendency
    0.8-1.5%, full range 0.6-1.9%
  - **Cross-method 68% band**: ~**0.5-1.9% real** (post-2020 divergence
    between HLW (unchanged) and market-model-based estimates (risen))
- **Williams' qualitative stance (Dec 2025 / Jan 2026 speeches)**: policy
  **"modestly restrictive"** — moving toward neutral. Speech text
  confirms direct anchor for our "Moderately Restrictive" tier.

---

## Real Rate Decomposition (US-unique)

**Available**: ✅ via `us-macro` `real-rates` group (T5YIE / T10YIE /
DFII5 / DFII10).

**Four-tier signal (applied to DFIIxx, 2025-2026 calibration)**:

| DFII5/10 | Signal |
|----------|--------|
| `< 0%` | Accommodative |
| `0 ≤ x < 1.0%` | Neutral |
| `1.0 ≤ x < 1.75%` | Moderately Restrictive |
| `≥ 1.75%` | Clearly Restrictive |

Full provenance: `investment-clock-cheatsheet.md` § "Threshold provenance".

Current (2026-04-17): DFII5 = 1.31% (Moderately), DFII10 = 1.93% (Clearly).

---

## Structural Regime Notes

- **Fed mandate**: dual mandate (max employment + price stability) —
  single-authority monetary policy
- **Post-COVID r\* debate unresolved**: HLW says r* hasn't risen
  (~0.75%), Lubik-Matthes says it has (1.68%). Affects how aggressive
  "clearly above neutral" should be interpreted.
- **Term premium volatility**: Adrian-Crump-Moench 10Y term premium has
  compressed post-COVID — affects nominal-to-real mapping.
- **Fiscal-monetary interaction**: large deficits + high debt/GDP
  (>120% pre-entitlement reform) keep long-end repricing risk active
  — watch 30Y for fiscal-premium spikes.
- **FAIT → FIT transition (2025-08)**: Under FAIT (2020-2025),
  moderate overshoot tolerated; under current FIT, Fed is symmetric.
  Small deviations above 2% now carry equal weight to deviations below.

### Historical r\* calibration context (grounding-v1.9.0.md, US §20-year trajectory)

- **Pre-GFC baseline (2005-2007)**: HLW r\* ≈ 2.0-2.5% real. Today's
  "Clearly Restrictive" threshold (DFII ≥ 1.75%) would have been
  NEUTRAL in 2006. The 4-tier bands reflect the post-GFC low-r\*
  regime — they implicitly assume secular stagnation has not fully reversed.
- **GFC shock (2008-2009)**: HLW r\* dropped **1.5 pp in 12 months** —
  the largest 1-year move on record. Regime thresholds must be
  re-calibrated when r\* undergoes step-changes.
- **SEP long-run drift (2012 → 2019 → 2025)**: FOMC median longer-run
  nominal dot: 4.25% (2012) → 2.50% (2019) → 3.00% (2025). Real
  neutral drift: 2.25% → 0.5% → 1.0%. Dec 2025 dot represents a
  ~50 bp recovery from 2019 trough, but is still 125 bp below
  pre-GFC anchor.
- **HLW vs Lubik-Matthes post-2020 divergence (~1 pp)**: Unresolved
  structural question for threshold calibration. Toolkit uses BOTH
  endpoints (0.75% HLW, 1.68% LM) with DFII cross-check rather than
  picking one.

---

## Asset-Class Tilt Calibration

- **Equity indices**: S&P 500 — Tech + Communication Services combined
  ~35% weight (Mag-7 drives idiosyncratic risk). Growth / Value split
  tracks real-rate regime closely.
- **Fixed income**: deepest TIPS + nominal curve globally; 2s10s and
  real-rate term structure both useful.
- **Commodities**: USD reserve status → inverse to DXY; crude (DCOILWTICO)
  + natural gas (DHHNGSP) primary in us-macro `energy` group.
- **Credit**: HY OAS (BAMLH0A0HYM2 in us-macro `financials`) — standard
  bands: `< 400 bp` Normal / `400-700` Elevated / `> 700` Stressed.

### IC Sector Tilts (US — applies as-is from cheatsheet)

| IC Phase | Overweight | Underweight |
|----------|------------|-------------|
| Recovery | Consumer Discretionary, IT, Financials | Utilities, Staples |
| Overheat | Energy, Materials, Industrials | Bonds, REITs |
| Stagflation | Energy, Staples, Cash | Consumer Discretionary, IT |
| Reflation | Utilities, Healthcare, Bonds | Energy, Materials |

---

## Primary-Source Verification URLs

- Federal Reserve SEP (dot plot): https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- NY Fed r-star: https://www.newyorkfed.org/research/policy/rstar
- Williams speeches: https://www.newyorkfed.org/newsevents/speeches
- CBO Budget & Economic Outlook: https://www.cbo.gov/publication/62105
- FRED NROU series: https://fred.stlouisfed.org/series/NROU
- FRED DFII10 / T10YIE / DFII5 / T5YIE

## Sources (citations)

- Cleveland Fed 2025-08: Neutral Interest Rates and the Monetary Policy Stance
- Liberty Street Economics 2025-08: Are Financial Markets Good Predictors of R-Star?
- Holston-Laubach-Williams (HLW) 2023 post-COVID paper (NY Fed)
- Lubik-Matthes Richmond Fed natural real rate series
- Williams "Resilience" (2025-12-15), "A Few Words for the New Year" (2026-01-12)
- CBO 2026 update: Current View of the Economy From 2026 to 2028
