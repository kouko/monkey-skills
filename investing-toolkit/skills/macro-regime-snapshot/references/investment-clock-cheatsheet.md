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
