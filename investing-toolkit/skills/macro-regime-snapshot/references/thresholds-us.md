# US — Macro Regime Thresholds & Calibration

**Authority**: Federal Reserve System | **Currency**: USD | **Calibration vintage**: 2026-Q1

---

## Inflation Target

- **Official target**: **2%** (PCE headline, since 2012; reaffirmed 2020 under
  Flexible Average Inflation Targeting / FAIT framework)
- **Tolerance band**: no explicit band — FOMC uses "symmetric"
  language + allows "moderate overshoot" under FAIT
- **Current reading**: CPI YoY ~2.5% (2026-Q1); PCE ~2.3%
- **2026 outlook**: Williams (NY Fed Jan 2026 speech) — inflation
  reaches ~2.5% in 2026, 2% goal by 2027
- **Signal**: Above target `> 2.2%` / At target `1.8-2.2%` / Below target `< 1.8%`

---

## Labor Market Tightness (NAIRU / NROU)

- **CBO NROU estimate**: **~4.4%** (CBO renamed "Natural Rate" → "Noncyclical
  Rate of Unemployment", NROU series on FRED)
- **CBO 2026 unemployment forecast**: 4.5-4.6% (from Feb 2026 update)
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
- **Nominal neutral estimates (FOMC Dec 2025 long-run dots)**:
  - Range: 2.6-3.9% (19 committee members spread)
  - Median: ~3.0%
- **Implied real neutral**:
  - HLW (2025 vintage): **1.42%**
  - Lubik-Matthes: **2.15%**
  - NY Fed composite: **~1.7%** (68% band: 0.9-2.5%)
  - Itochu / Mizuho: 0.5-1.5%
- **Williams' qualitative stance (Dec 2025 / Jan 2026)**: policy
  **"modestly restrictive"** — moving toward neutral

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
- **Post-COVID r\* debate unresolved**: HLW says r* hasn't risen,
  Lubik-Matthes says it has. Affects how aggressive "clearly above
  neutral" should be interpreted.
- **Term premium volatility**: Adrian-Crump-Moench 10Y term premium has
  compressed post-COVID — affects nominal-to-real mapping.
- **Fiscal-monetary interaction**: large deficits + high debt/GDP
  (>120% pre-entitlement reform) keep long-end repricing risk active
  — watch 30Y for fiscal-premium spikes.

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
