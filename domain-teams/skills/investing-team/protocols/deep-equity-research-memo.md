---
name: deep-equity-research-memo
description: Full 6-phase equity research memo — regime → sector → valuation → thesis → pre-mortem → verdict+sizing
---

# Deep Equity Research Memo Protocol

Flagship protocol for single-security investment analysis. Produces a structured
research memo grounded in primary-source evidence across all four analytical
layers (L1 macro → L2 sector → L3 security → verdict).

For standalone macro regime diagnosis without a ticker, use
`protocols/macro-regime-diagnosis.md` instead.

## Mode Detection (run before Phase 1)

Read the user's request and classify:

| Signal | Action |
|---|---|
| "quick", "fast", short context, minimal data | Route to Quick Stock Screen (not this protocol) |
| "deep", "full memo", "spare no expense", "research-grade" | This protocol |
| Ticker provided, no mode qualifier | Default to this protocol |

Default to this protocol whenever a specific ticker or company is the subject.

## Primary Sources

Load progressively as phases require:

- `standards/investment-macro-regime.md` — L1: Greetham & Hartnett 2004 IC +
  Dalio 2018 debt cycle + Hedgeye GIP + RAI
- `standards/investment-sector-industry.md` — L2: Fama-French factor models +
  sector rotation by regime
- `standards/strategic-frameworks-investor-lens.md` — L2: Porter barriers-to-entry
  + moat durability (Greenwald & Kahn)
- `standards/investment-security-valuation.md` — L3: Damodaran 3-framework
  taxonomy + Graham margin of safety
- `standards/investment-thesis-structure.md` — Thesis construction + inversion /
  pre-mortem discipline
- `standards/decision-framework-and-verdict.md` — Verdict discipline + bias catalog
- `standards/position-sizing-and-risk.md` — Kelly sizing + risk-budget target weight
- `standards/taiwan-equity-frameworks.md` — Taiwan-specific integrations (.TW tickers)

## Phase 1: L1 Macro Regime Context

Per `standards/investment-macro-regime.md` — Greetham & Hartnett 2004 Investment
Clock (2×2 growth direction × inflation direction):

| Quadrant | Growth | Inflation | Favored Asset Class |
|---|---|---|---|
| Reflation | Decelerating | Decelerating | Bonds |
| Recovery | Accelerating | Decelerating | Stocks |
| Overheat | Accelerating | Accelerating | Commodities |
| Stagflation | Decelerating | Accelerating | Cash |

Do NOT use business-cycle terminology (expansion / slowdown / contraction) —
these describe GDP dynamics, not asset-class regimes.

**Execution:**

1. Identify the current regime quadrant from available data (yield curve, CPI
   trajectory, PMI, industrial production).
2. Note the regime implication for the target company's sector and asset class.
3. If the user provides a regime call: use it and record the source.
4. If regime is ambiguous: note "regime uncertainty" and present two plausible
   scenarios with directional probability weights (not precise %).
5. Brief Dalio debt-cycle cross-check (per `standards/investment-macro-regime.md`
   §Dalio's Debt Cycle Framework): state which of the 6 phases (Early / Bubble /
   Top / Depression / Beautiful Deleveraging / Pushing on a String) applies.
   Dalio is diagnostic only — do not derive asset-allocation prescription from it.
   Asset-class calls come from the Investment Clock.

## Phase 2: L2 Sector and Competitive Landscape

Per `standards/investment-sector-industry.md` +
`standards/strategic-frameworks-investor-lens.md`:

1. Identify the company's GICS sector and industry group.
2. **Factor analysis**: which Fama-French factors dominate returns in this sector?
   Specify model — FF3 (1993), FF5 (2015), or Carhart 4-factor (1997). FF5
   explicitly excludes momentum; Carhart is the canonical momentum source. Quality
   (AQR QMJ) and Low-Vol (Frazzini-Pedersen 2014 BAB) are NOT FF factors. Japan
   exception is load-bearing for .T tickers: FF5 fails in Japan per Kubota-Takehara
   2018.
3. **Porter analysis (investor lens)**: assess moat durability using Greenwald &
   Kahn barriers-to-entry test per `standards/strategic-frameworks-investor-lens.md`.
   Focus on: (a) cost advantages, (b) customer captivity, (c) scale economies
   relative to market size.
4. **Sector position in regime**: is this sector favored, neutral, or disfavored
   given the L1 regime call from Phase 1? Document the bridge explicitly.

## Phase 3: L3 Security Valuation

Per `standards/investment-security-valuation.md` — Damodaran 3-framework discipline.
Apply at least TWO independent valuation frameworks; note which are applicable
given the asset type.

### DCF (Base Case)

- Model: FCFF with WACC, or FCFE with cost of equity for financial firms.
- State explicit assumptions: revenue growth rate, operating margin trajectory,
  WACC components, terminal growth rate.
- Terminal growth rate MUST NOT exceed long-run nominal GDP growth — this is the
  single most common DCF modeling error.
- Output: base-case intrinsic value per share.

### Relative Valuation (Comps)

- Use P/E or EV/EBITDA vs. sector median as primary multiples; add P/B or P/S
  where sector convention warrants.
- Match the comparable set rigorously; adjust for differences in growth, risk,
  and reinvestment rate.
- For cyclical earnings: apply CAPE (Campbell & Shiller 1998, 10-year real-earnings
  smoothing) to eliminate business-cycle noise. Cite BOTH Campbell & Shiller 1998
  — do NOT credit to Shiller alone.

### Contingent Claims (if applicable)

- Apply when the security has meaningful optionality: undeveloped reserves,
  early-stage patents, equity in distressed firms.
- State which option-pricing model is used and why.

### Intrinsic Value Range and Margin of Safety

- Output: low / base / high intrinsic value range.
- Margin of safety check per `standards/investment-security-valuation.md`
  §Graham & Dodd: require a substantial gap between price and intrinsic value
  (canonical 30-50% discount). Derive intrinsic value from fundamentals first,
  then compare to market price — never anchor on price and reason backward.
- Sensitivity table: identify which assumptions shift the range by >15%.
  Typical drivers: terminal growth rate, WACC, near-term revenue CAGR,
  margin normalization timeline.

### Taiwan Check

If the ticker is a .TW / .TWO listed security, also apply
`standards/taiwan-equity-frameworks.md` Phase integrations:
- 月營收 (monthly revenue) trend and YoY momentum
- 三大法人 (institutional investors: foreign, investment trust, proprietary)
  net buy/sell flow
- 董監持股 (director and supervisor shareholding ratio) and recent changes
- 融資融券 (margin lending / short selling) balance trend as sentiment signal

## Phase 4: Investment Thesis Construction

Per `standards/investment-thesis-structure.md` — all 5 elements are required.
Missing any element triggers a SELF-revision before proceeding.

1. **Operative claim**: one sentence. Specific, falsifiable, forward-looking.
   Example: "TSMC will re-rate from 18x to 22x NTM P/E as CoWoS capacity
   constraints resolve in 2H25."

2. **Variant perception delta**: what does this analysis believe that the
   market consensus does not? State it specifically and measurably. If the
   thesis is not variant, it is consensus — sharpen or abandon it.

3. **Catalysts** (1–3): each with approximate timeline and observability
   criterion (i.e., how will you know the catalyst fired?).

4. **Invalidators** (1–3): specific, observable conditions that would falsify
   the operative claim. Each must have a trigger condition precise enough to
   recognize in real time.

5. **Confidence interval on variant perception**: high / medium / low, with
   the primary source of uncertainty stated.

**Second-level thinking check (Marks)**: could a reasonable, informed person
reading this thesis reach the opposite conclusion from the same facts? If not,
the thesis is either trivially obvious or underspecified. Sharpen accordingly.

## Phase 5: Pre-Mortem and Scenario Stress-Test

Per `standards/investment-thesis-structure.md` §Inversion +
`standards/decision-framework-and-verdict.md` §Bias Catalog.

### Pre-Mortem

"Imagine it is 18 months from now and this thesis was wrong. What was the most
likely single cause?" Write one paragraph. This is not a risk list — it is a
forced narrative of failure, designed to surface confirmation bias.

### Three Scenarios

| Scenario | Thesis outcome | Catalyst | Price target | Probability weight | Expected return |
|---|---|---|---|---|---|
| Bull | Thesis right, catalyst fires, market re-rates | [specify] | [price] | [%] | [%] |
| Base | Partial thesis, slow catalyst, modest return | [specify] | [price] | [%] | [%] |
| Bear | Thesis wrong — pick one invalidator | [specify] | [price] | [%] | [%] |

Weights must sum to 100%. Weighted expected return = sum(p_i × r_i).

### Bias Check

Run through the 6 biases in `standards/decision-framework-and-verdict.md`
§Bias Catalog. For each bias that is present, state explicitly how it was
addressed or why it does not materially affect the conclusion:

1. Confirmation bias
2. Anchoring
3. Availability heuristic
4. Narrative fallacy
5. Overconfidence
6. Recency bias

## Phase 6: Verdict and Position Sizing

Per `standards/decision-framework-and-verdict.md` +
`standards/position-sizing-and-risk.md`.

### Verdict

Declare: **BUY / HOLD / SELL**

State the explicit margin-of-safety calculation:
- Intrinsic value (base case): [value]
- Current market price: [price]
- Implied margin of safety: [(IV - P) / IV × 100]%
- Required threshold met: yes / no (canonical 30-50%)

A HOLD verdict on a currently owned position requires a different standard
than a new BUY — state which case applies.

### Conviction Grade

**A / B / C** with justification on three dimensions:

| Dimension | Assessment |
|---|---|
| Variant perception strength | Is the delta specific, measurable, and non-consensus? |
| Method convergence | Do DCF and relative valuation agree directionally? |
| Catalyst visibility | Is the catalyst observable and time-bounded? |

A = all three strong; B = two strong, one weak; C = one or more materially weak.

### Position Sizing

Per `standards/position-sizing-and-risk.md`:
- Fractional Kelly estimate: f* = (edge / odds), where edge = weighted expected
  return and odds = win/loss ratio from the scenario table. Recommended to use
  half-Kelly or quarter-Kelly for robustness.
- OR risk-budget target weight: state the % of portfolio risk budget this
  position should consume given the conviction grade.
- State maximum position size at which the thesis remains risk-appropriate.

### Exit Conditions

**Sell-on-invalidation**: which specific invalidator trigger(s) from Phase 4
would convert this BUY to a SELL immediately?

**Hold-review trigger**: which conditions would prompt a thesis review without
an immediate SELL (e.g., catalyst delayed but not falsified, valuation moved
to fair value but not overvalued)?

**Price target exit**: at what price does the margin of safety compress to zero
(i.e., price = intrinsic value base case)?

## Output Template

```
## Equity Research Memo: {TICKER} — {DATE}

### Macro Regime Context (L1)
[Investment Clock quadrant, supporting data, Dalio phase overlay,
regime implication for this sector/asset class]

### Sector and Competitive Landscape (L2)
[GICS sector/industry, dominant factors, Porter/Greenwald moat assessment,
sector favored/neutral/disfavored in current regime]

### Valuation (L3)

#### DCF
[Assumptions table: growth, margin, WACC, terminal g]
[Intrinsic value output]

#### Relative Valuation
[Comps table: ticker vs. sector median multiples]
[Implied value range]

#### Intrinsic Value Range
| Scenario | Intrinsic Value | Key Driver |
|---|---|---|
| Low | | |
| Base | | |
| High | | |

#### Sensitivity Table
| Assumption | Base | Bear | Bull | IV impact |
|---|---|---|---|---|
| Terminal growth | | | | |
| WACC | | | | |
| Revenue CAGR | | | | |

### Investment Thesis

#### Operative Claim
[One sentence]

#### Variant Perception
[What this analysis believes vs. consensus, measurably stated]

#### Catalysts
| # | Catalyst | Timeline | Observability |
|---|---|---|---|

#### Invalidators
| # | Invalidator | Trigger condition |
|---|---|---|

### Pre-Mortem + Scenarios

#### Pre-Mortem
[Paragraph: most likely failure narrative in 18 months]

#### Bull / Base / Bear
| Scenario | Thesis | Price Target | Weight | Expected Return |
|---|---|---|---|---|

#### Bias Check
[6-item checklist with explicit disposition for each]

### Verdict and Sizing

#### Verdict: {BUY / HOLD / SELL}
[Margin of safety calculation]

#### Conviction Grade: {A / B / C}
[3-dimension justification table]

#### Position Sizing
[Kelly estimate or risk-budget weight, max size]

#### Exit Conditions
[Sell-on-invalidation triggers]
[Hold-review triggers]
[Price-target exit]

### Provenance
[Primary sources cited with as-of dates]
```

## Rules

- Terminal growth rate in DCF must never exceed long-run nominal GDP growth.
- Investment Clock quadrant must use the four named regimes (Reflation /
  Recovery / Overheat / Stagflation) — never business-cycle vocabulary.
- Dalio debt-cycle phases must be named verbatim (Early / Bubble / Top /
  Depression / Beautiful Deleveraging / Pushing on a String). Do not collapse
  to fewer phases or substitute business-cycle vocabulary.
- Intrinsic value must be derived from fundamentals first; never anchor on
  market price and reason backward (Mr. Market discipline).
- Variant perception must be specific and measurable — not "the market
  underestimates growth" but "consensus models 12% revenue CAGR; this
  analysis supports 17% based on [evidence]".
- Every forward-looking claim must carry a confidence level (高/中/低) per
  `standards/confidence-and-claim-language.md`.
- All data must carry an explicit as-of date — stale data invalidates the analysis.
- Cite primary filings (10-K, 有価証券報告書, TWSE MOPS) and central bank
  releases over analyst reports and financial media.
- When citing CAPE: cite BOTH Campbell & Shiller 1998 authors and name the
  10-year real-earnings window. Do not credit to Shiller alone.
- Do NOT cite "Damodaran's macro framework" — no such framework exists.
  Damodaran is bottom-up valuation only.
