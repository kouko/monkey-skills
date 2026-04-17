---
name: dcf-valuation
description: >-
  Interactive 3-stage DCF valuation model. Collects financial inputs from the
  user (or from a us-stock-snapshot fixture), computes intrinsic value range,
  renders a 3x3 sensitivity table (WACC vs. terminal growth), and applies
  Graham-Dodd-Klarman verdict conditions. Does NOT fetch data — inputs must be
  provided. Reference: references/dcf-template.md.
  DCF 内在価値試算。DCF 內在價值估算。
---

# DCF Valuation

Interactive intrinsic value model based on Damodaran 2012 *Investment Valuation*
Ch.12 (3-stage DCF). This skill does **not fetch data** — all financial inputs
must be supplied by the user or passed in from a `us-stock-snapshot` fixture or
SEC EDGAR financials.

Reference template: `references/dcf-template.md`

## When to Use

- You have revenue, margin, and reinvestment data for a company
- You want an absolute intrinsic value (not relative multiples)
- You want to stress-test assumptions via sensitivity analysis

## When NOT to Use

- You need financial statements first → fetch from SEC EDGAR, then return here
- You want relative valuation (P/E vs. peers) → that is a multiples analysis,
  not DCF (see Attribution Corrections below)

## Inputs

Step through each input with the user. Accept a `us-stock-snapshot` card as a
starting point for market cap and shares outstanding.

### Stage 1 — Revenue and Growth

```
Revenue (base year):        $_____M
Revenue growth (Yr 1–5):    _____%   ← high-growth stage
Revenue growth (Yr 6–10):   _____%   ← transition stage
```

### Stage 2 — Profitability and Reinvestment

```
Target EBIT margin:         _____%
Tax rate:                   _____%
Reinvestment rate:          _____%
  (= (CapEx - D&A + ΔNWC) / EBIT × (1 - tax))
```

### Stage 3 — Discount Rate (WACC)

Accept a user-supplied WACC directly, or guide them through the WACC build-up:

```
Risk-free rate (10Y Treasury / FRED DGS10):   _____%
Equity risk premium (Damodaran country ERP):  _____%
Beta (regression or sector):                  _____
Cost of equity = Rf + β × ERP:               _____%
Pre-tax cost of debt (YTM or spread):         _____%
After-tax cost of debt = Kd × (1 - t):       _____%
Equity weight (market cap / EV):              _____%
Debt weight:                                  _____%
WACC = Ke × We + Kd(1-t) × Wd:             _____%
```

To fetch current DGS10, run (verify uv first: `command -v uv || sh ${CLAUDE_SKILL_DIR}/scripts/setup.sh`):
`INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series DGS10 --periods 1`

### Stage 4 — Terminal Growth

```
Terminal growth rate (g):   _____%
```

**Warn the user if g > risk-free rate.** See Attribution Corrections.

### Stage 5 — Capital Structure

```
Cash & equivalents:         $_____M
Total debt:                 $_____M
Net debt = Total debt - Cash: $_____M
Shares outstanding:         _____M
```

## Computation

### FCF per year (t = 1 to 10)

```
Revenue_t = Revenue_{t-1} × (1 + growth_t)
EBIT_t    = Revenue_t × EBIT_margin
FCF_t     = EBIT_t × (1 - tax_rate) × (1 - reinvestment_rate)
PV(FCF_t) = FCF_t / (1 + WACC)^t
```

Stage 1 uses growth Yr 1–5; Stage 2 uses growth Yr 6–10.

### Terminal value (Stage 3, year 10+)

```
TV        = FCF_10 × (1 + g) / (WACC - g)
PV(TV)    = TV / (1 + WACC)^10
```

### Equity value and intrinsic price

```
Equity value          = Σ PV(FCF_t) + PV(TV) - Net debt
Intrinsic value/share = Equity value / Shares outstanding
```

## Sensitivity Table (3×3)

Compute 9 scenarios varying WACC ±1% and terminal growth ±0.5%:

```
                  g − 0.5%    g (base)    g + 0.5%
WACC − 1%      |  $___      |  $___      |  $___
WACC   (base)  |  $___      |  $BASE     |  $___
WACC + 1%      |  $___      |  $___      |  $___
```

Label the base case cell as `$BASE`.

## Verdict Condition

From `references/dcf-template.md` (Graham & Dodd / Klarman):

```
BUY   if current_price ≤ intrinsic_value × (1 - MoS_factor)
HOLD  if current_price ≤ intrinsic_value × 1.15
SELL  if current_price > intrinsic_value × 1.15

MoS_factor:
  Grade A conviction → 0.30  (require 30% margin of safety)
  Grade B conviction → 0.40  (require 40% margin of safety)
  Grade C conviction → 0.50  (require 50% margin of safety)
```

Conviction grade is set by the investing-team analyst, not by this skill.
Report all three thresholds so the user can apply their own grade.

## Attribution Corrections

From `references/dcf-template.md`:

1. **Terminal growth must be ≤ risk-free rate**: Terminal growth ≠ nominal GDP
   growth. Using nominal GDP (~4–5%) as terminal growth double-counts inflation
   already embedded in WACC. Use real GDP growth or lower (typically 1–3%).

2. **Reinvestment rate drives growth**: The internal consistency constraint is
   `growth = ROIC × reinvestment_rate`. High revenue growth paired with a low
   reinvestment rate implies capital-light compounding — verify ROIC is high
   enough to support this assumption.

3. **DCF ≠ multiples**: DCF produces absolute intrinsic value. Multiples
   (P/E, EV/EBITDA) produce relative value vs. peers. A stock can be cheap vs.
   peers (relative) and overvalued vs. DCF intrinsic simultaneously. Do not
   use DCF output to validate or calibrate a multiples screen.

## Cross-Plugin Handoff

After intrinsic value is computed, hand off to `domain-teams:investing-team`
for full investment memo:

```
Workflow: dcf-valuation (this skill) → domain-teams:investing-team
                                       → investment-memo-writer
```

Pass to investing-team:
- The completed DCF output (intrinsic value, sensitivity table, verdict)
- The `us-stock-snapshot` card (if available)
- The macro regime snapshot (if available from `macro-regime-snapshot`)

The investing-team will layer in variant perception thesis, pre-mortem
analysis, and conviction grade to produce the full investment memo.
