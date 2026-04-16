# DCF Valuation Template

**Framework**: Damodaran 2012 *Investment Valuation* Ch.12 — 3-stage DCF

## Inputs

```
Revenue (base year):        $_____M
Revenue growth (Yr 1-5):    _____%  (high-growth stage)
Revenue growth (Yr 6-10):   _____%  (transition stage)
Terminal growth rate:        _____%  (perpetuity; ≤ risk-free rate)
EBIT margin (target):       _____%
Tax rate:                   _____%
Reinvestment rate:          _____%  (= CapEx - D&A + ΔNWC) / EBIT(1-t)
WACC:                       _____%
Cash & equivalents:         $_____M
Total debt:                 $_____M
Shares outstanding:         _____M
```

## WACC Build-Up

```
Risk-free rate (10Y Treasury / FRED: DGS10):  _____%
Equity risk premium:                           _____%  (Damodaran country premium)
Beta (regression or sector):                  _____
Cost of equity = Rf + β × ERP:               _____%
Pre-tax cost of debt (YTM or spread):         _____%
After-tax cost of debt = Kd × (1 - t):       _____%
Equity weight (market cap / EV):              _____%
Debt weight:                                  _____%
WACC = Ke × We + Kd(1-t) × Wd:             _____%
```

## Sensitivity Table (2×2)

```
WACC vs. Terminal Growth Rate:

         |  g = 1%  |  g = 2%  |  g = 3%
---------|----------|----------|----------
WACC-1%  |          |          |
WACC     |          |   BASE   |
WACC+1%  |          |          |
```

## Intrinsic Value Range

```
Bear case  (WACC+1%, g-0.5%):  $_____ / share
Base case  (WACC,    g    ):   $_____ / share
Bull case  (WACC-1%, g+0.5%):  $_____ / share

Current price:                 $_____ / share
Margin of safety (base case):  _____% 
  = (Intrinsic - Price) / Intrinsic × 100
```

## Verdict Condition (Graham & Dodd / Klarman)

```
BUY   if price ≤ intrinsic_value × (1 - MoS_factor)
HOLD  if price ≤ intrinsic_value × 1.15
SELL  if price > intrinsic_value × 1.15

MoS_factor: 0.30 (Grade A conviction), 0.40 (Grade B), 0.50 (Grade C)
```

## Attribution Corrections

1. **Terminal growth ≤ risk-free rate**: Terminal growth ≠ GDP growth. Using nominal
   GDP growth (~4-5%) as terminal growth double-counts inflation already in WACC.
   Use real GDP growth or lower.
2. **Reinvestment rate drives growth**: Growth = ROIC × Reinvestment rate.
   High growth with low reinvestment implies capital-light compounding — verify ROIC.
3. **Damodaran's three approaches**: DCF / Relative / Contingent-claim are NOT
   interchangeable. DCF is absolute value; multiples are relative value. A stock
   can be cheap vs. peers (relative) and overvalued vs. intrinsic (DCF).
