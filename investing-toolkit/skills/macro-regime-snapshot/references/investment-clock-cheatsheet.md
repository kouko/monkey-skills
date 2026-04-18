# Investment Clock Cheatsheet

**Source**: Greetham & Hartnett 2004 (Merrill Lynch Investment Clock)

## 2×2 Phase Grid

```
                  GROWTH RISING
                       │
         RECOVERY      │   OVERHEAT
          (Phase 1)    │   (Phase 2)
                       │
INFLATION ─────────────┼───────────── INFLATION
FALLING                │               RISING
                       │
         REFLATION     │   STAGFLATION
          (Phase 4)    │   (Phase 3)
                       │
                  GROWTH FALLING
```

## Phase Characteristics

| Phase | Growth | Inflation | Bonds | Equities | Commodities | Cash |
|-------|--------|-----------|-------|----------|-------------|------|
| 1 Recovery | Rising | Falling | ✅ Best | ✅ Good | ❌ Weak | ❌ Weak |
| 2 Overheat | Rising | Rising | ❌ Weak | ✅ Good | ✅ Best | ❌ Weak |
| 3 Stagflation | Falling | Rising | ❌ Weak | ❌ Weak | ✅ Good | ✅ Best |
| 4 Reflation | Falling | Falling | ✅ Good | ❌ Weak | ❌ Weak | ✅ Good |

## Proxy Indicators (FRED series)

| Indicator | FRED Series | Phase Signal |
|-----------|-------------|--------------|
| GDP growth direction | GDPC1 (QoQ) | Rising = Phase 1 or 2; Falling = 3 or 4 |
| CPI direction | CPIAUCSL (YoY MoM trend) | Rising = Phase 2 or 3; Falling = 1 or 4 |
| 10Y–2Y yield spread | T10Y2Y | Positive + widening → Recovery; Inverted → Stagflation risk |
| Industrial production | INDPRO | Leading growth proxy |
| ISM Manufacturing PMI | MANEMP proxy | >50 = expansion |

## Hedgeye GIP Refinement (McCullough 2024)

Hedgeye's GIP model uses **Growth / Inflation / Policy** on a 4-quadrant grid,
refined from IC's 2×2:

- **Quad 1**: Growth ↑, Inflation ↑ → Risk-on; Equities + Commodities
- **Quad 2**: Growth ↑, Inflation ↓ → Goldilocks; Equities strongest
- **Quad 3**: Growth ↓, Inflation ↓ → Deflation risk; Bonds, Cash
- **Quad 4**: Growth ↓, Inflation ↑ → Stagflation; Commodities, Cash

**Key difference from IC**: GIP uses rate-of-change (2nd derivative), not level.
A decelerating expansion is Quad 3 even if GDP is still positive.

## Attribution Corrections

1. **IC phase names vary by source**: Merrill Lynch uses Recovery/Overheat/Stagflation/Reflation;
   Bloomberg uses Expansion/Slowdown/Contraction/Recovery. These are NOT the same mapping.
   Always state which naming convention you use.
2. **IC is a 12–18 month framework**, not a daily/weekly signal. Do not apply to short-term trades.
3. **GIP quadrant ≠ IC phase**: They overlap but differ in timing inputs (rate-of-change vs. level).

## Sector Tilts by IC Phase

| IC Phase | Overweight | Underweight |
|----------|-----------|-------------|
| Recovery | Consumer Discretionary, IT, Financials | Utilities, Staples |
| Overheat | Energy, Materials, Industrials | Bonds, REITs |
| Stagflation | Energy, Staples, Cash | Consumer Discretionary, IT |
| Reflation | Utilities, Healthcare, Bonds | Energy, Materials |

---

## Per-Country Proxy Mapping (v1.9.0)

Which series to read for each country's Growth and Inflation axes. All
use the v1.7.0+ monthly GDP proxy work — not raw IPI.

| Country | Growth proxy | Inflation proxy | Source skill / preset |
|---------|--------------|-----------------|-----------------------|
| **US** | `nowcast.CFNAI` (primary), `nowcast.WEI` (secondary weekly cross-check) | CPIAUCSL YoY, CPILFESL YoY for core | `us-macro` → `nowcast`, `inflation` |
| **JP** | `coincident-index` CI (景気動向指数 DI+CI trio from e-Stat) | 全国CPI YoY | `japan-macro` → `growth`, `inflation` |
| **TW** | `cycle.signal` 五色景氣燈號 score (NDC, 1-9 pre-aggregated) | CPI YoY | `taiwan-macro` → `cycle`, `inflation` |
| **KR** | `coincident-cycle` K253 (동행지수순환변동치 BOK ECOS) | K401 CPI YoY | `korea-macro` → `cycle`, `inflation` |
| **CN** | `industrial-yoy` (primary NBS), overlay `retail-yoy`/`fai-yoy`/`services-production-yoy` | CPI YoY (NBS) | `china-macro` → `growth`, `inflation` |

### Direction-classification rule

For each Growth + Inflation series:

1. Compute latest reading (`x_t`) and trailing 3-month average
   (`mean(x_{t-3..t-1})`).
2. Compute recent-3m standard deviation (`σ_3m`).
3. Classify:
   - **Rising** if `x_t > mean + 0.5 × σ_3m` (or `x_t - mean > 0.1` for
     normalised indices like CFNAI)
   - **Falling** if `x_t < mean - 0.5 × σ_3m`
   - **Flat / Stagnation** otherwise (note in Signal column)

For pre-aggregated indices (Taiwan signal score, Korea K253), thresholds
are published by the source authority:

- **TW signal**: 紅燈 (≥38), 黃紅 (32-37), 綠 (23-31), 黃藍 (17-22),
  藍 (≤16). Score ≥ 32 → Rising; < 23 → Falling; 23-31 → Flat.
- **KR K253 CI**: BOK publishes the index with `>100` expansion,
  `<100` contraction. Direction = MoM trend (≥ 3 consecutive up → Rising).

---

## Real-Rate Interpretation (US only, v1.9.0)

Real rate = DFII (TIPS yield) ≈ Nominal (DGSxx) − Breakeven (TxxYIE).

### Signal thresholds

| DFII5 / DFII10 | Signal | Fed-policy framing |
|----------------|--------|--------------------|
| `< 0%` | **Accommodative** | Real cost of capital negative → favours risk assets, gold, duration. Historically associated with ZIRP or active QE regimes. |
| `0% ≤ x < 1.5%` | **Neutral** | Around Fed r* (0.5-1.0%) plus small term premium. Typical mid-cycle. |
| `≥ 1.5%` | **Restrictive** | Real cost of capital elevated. Headwind for equity multiples (particularly long-duration tech), credit, real estate. |

### Why 1.5%?

Fed estimates of the neutral real rate (r*) cluster around 0.5-1.0% post-GFC.
The SEP median long-run dot has floated 0.5-1.5%. 1.5% is the defensible
"clearly above neutral" threshold given term premium and model uncertainty.

### Anchoring cross-check

If `|Nominal − Breakeven − Real| > 5 bp`, note possible **TIPS liquidity
premium** — the breakeven overstates pure inflation expectations by
~15-30 bp in stressed markets. Don't overfit Fed narrative in those
regimes.

---

## Signal-Label Glossary (LSEG absorption)

Use these labels in Block 1 `Signal` column instead of bare
Rising/Falling:

| Axis | Labels | Trigger |
|------|--------|---------|
| Growth | Expansion / Stagnation / Contraction | Direction Rising / Flat / Falling |
| Inflation | Above target / At target / Below target | vs country target (US 2%, JP 2%, KR 2%, TW ~2%, CN 3%) |
| Labor | Tight / Balanced / Slack | Unemployment < NAIRU / ≈ NAIRU / > NAIRU |
| Policy rate | Accommodative / Neutral / Restrictive | vs estimated neutral (Fed r*, BOJ, etc.) |
| Real rate (US) | Accommodative / Neutral / Restrictive | see thresholds above |
| PMI (if available) | Expansion / Contraction | > 50 / < 50 |
| Credit spread (HY) | Normal / Elevated / Stressed | < 400 bp / 400-700 / > 700 bp |

These labels are **neutral diagnostic** — they describe the read, not
the trade recommendation. Asset-class tilts (Block 5) are where we
translate signals into positioning.

Source: the LSEG partner-built `macro-rates-monitor` skill in Anthropic's
`financial-services-plugins` uses similar labels; we port the pattern
to free FRED data.
