---
name: decision-framework-and-verdict
description: Grammar for Buy/Hold/Sell verdicts — margin of safety, conviction grades, bias catalog
tier: 2
layer: verdict
---

# Decision Framework and Verdict

Fully self-contained Tier 2 standard covering the **verdict layer** of
investing-team's analysis workflow: the grammar for translating completed
analysis into a Buy / Hold / Sell decision, the margin of safety discipline
that constrains that grammar, the conviction grading system that qualifies it,
and the bias catalog that guards against distortion.

Tier 2 because LLMs correctly understand the broad shape of Graham's margin
of safety concept and the common cognitive biases, but routinely confuse
(a) margin of safety with stop-loss orders, (b) BUY verdicts with general
approval of a company's business, (c) Damodaran's bias catalog as normative
("valuations are always biased") rather than descriptive, and (d) conviction
grade with the verdict itself — treating a high-conviction position as
synonymous with BUY. Body spells out the distinctions that LLMs most
frequently collapse.

**Scope**: Verdict grammar, margin-of-safety computation, conviction grading,
and bias catalog → publishable investment conclusion. Intrinsic value
computation belongs in `investment-security-valuation.md`; thesis structure
and invalidation logic belong in `investment-thesis-structure.md`; position
sizing downstream of the verdict belongs in `position-sizing-and-risk.md`.

## Primary Sources

- Graham, B. & Dodd, D. (1934, 6th ed. 2008) *Security Analysis*. McGraw-Hill.
  Ch.20 "The Concept of the Margin of Safety" — canonical definition: purchase
  is warranted only when intrinsic value substantially exceeds market price; the
  gap between the two IS the margin of safety, not a risk management overlay.

- Klarman, S. (1991) *Margin of Safety: Risk-Averse Value Investing Strategies
  for the Thoughtful Investor*. HarperCollins. Ch.4 "The Difficulty of
  Determining Intrinsic Value" + Ch.6 "The Margin of Safety Concept" —
  operationalizes Graham: intrinsic value is an estimated range, not a point;
  the required discount must absorb both market uncertainty and estimation error.

- Damodaran, A. (2012, 3rd ed.) *Investment Valuation: Tools and Techniques for
  Determining the Value of Any Asset*. Wiley. Ch.35 "Closing Thoughts on
  Valuation" — descriptive bias catalog for valuation: anchoring, confirmation,
  narrative bias, recency bias, overconfidence / inside-view. Each bias is
  identified by its observable signature in the output, not by the analyst's
  intentions.

- Kahneman, D. (2011) *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
  Ch.12 "The Science of Availability" + Ch.24 "The Engine of Capitalism" —
  overconfidence in forecasts; inside vs. outside view; reference class
  forecasting as the de-biasing mechanism; base-rate neglect as the dominant
  failure mode in investment forecasting.

- Mauboussin, M.J. & Callahan, D. (2014) "A Checklist for Superforecasters."
  Credit Suisse Global Financial Strategies, 2014-12-17. — Operationalizes
  Kahneman's outside view into a decision-checklist: identify the reference
  class, establish base rates, update from company-specific evidence, distinguish
  skill from luck, and calibrate confidence to evidence weight.

## Critical Attribution Corrections

### Margin of safety is not a stop-loss

Graham Ch.20 defines margin of safety as the **spread between intrinsic value
and purchase price at the time of purchase**. It is an entry-price discipline,
not a post-purchase risk management tool. A stop-loss order triggers when
price falls; margin of safety requires that price is already below intrinsic
value before purchase. The two concepts operate at different points in time
with different mechanics. Do NOT describe stop-losses as "implementing the
margin of safety principle."

### BUY does not mean "I like this company"

A BUY verdict is a claim that the current market price is meaningfully below
the estimated intrinsic value range — typically by at least 30% to the central
estimate (Graham Ch.20 working threshold). A company can be operationally
excellent, competitively durable, and well-managed and still not be a BUY if
the market has already priced in that excellence. Equally, a mediocre business
trading at a large discount to its liquidation value can be a BUY. Quality and
BUY verdict are **orthogonal assessments**. The verdict is about price vs.
value; quality is an input to the value estimate.

### Damodaran's bias catalog is descriptive, not normative

Damodaran Ch.35 documents biases that **appear in actual valuations** as an
empirical observation. It does NOT claim that all valuations are biased, that
quantitative analysis is inherently unreliable, or that analysts are incapable
of objectivity. The catalog is a **diagnostic tool**: check your output for the
observable signatures listed, and if you find them, revise. Do NOT invoke
Damodaran to dismiss DCF analysis as "subjective by definition" or to argue
that fundamental valuation is no better than guessing.

### Conviction grade is separate from verdict

A Grade A conviction BUY is a high-confidence purchase signal. A Grade C
conviction BUY is a speculative position that is still undervalued — but the
uncertainty demands smaller size (see `position-sizing-and-risk.md`). The two
dimensions are independent: you can have Grade A conviction that a stock is
fully valued (Grade A HOLD) or Grade C conviction that a stock is undervalued
(Grade C BUY). Merging conviction grade with verdict direction produces
incorrect sizing and portfolio construction. Do NOT conflate high conviction
with BUY.

## Verdict Grammar

The verdict is the final output of the investing-team analysis pipeline. It
summarizes where the current market price sits relative to the estimated
intrinsic value range and whether the price-to-value relationship warrants
a position change.

### Three-Level Taxonomy

| Verdict | Price Condition | MoS Floor |
|---|---|---|
| **BUY** | Price ≤ (central intrinsic value estimate × 0.70) | ≥ 30% discount to central estimate |
| **HOLD** | Price within ±15% of intrinsic value range | Within range; no strong catalyst for change |
| **SELL** | Price ≥ intrinsic value upper bound OR a thesis invalidator triggered | Overvalued relative to range, or thesis broken |

The 30% MoS floor is Graham's Ch.20 working threshold for general equities.
Klarman (Ch.6) argues for a **wider discount in high-uncertainty situations**:
when the intrinsic value range is wide (e.g., 2× between low case and high
case), the required discount must grow to compensate for the estimation
uncertainty itself — a 30% discount to a point estimate is not equivalent
to a 30% discount to a wide range. Size the discount to account for both
market risk and estimation error.

### Verdict Constraints

- **BUY requires an intrinsic value estimate**: you cannot issue a BUY
  verdict without a completed valuation (see `investment-security-valuation.md`).
  Price momentum alone is not a BUY signal.
- **SELL on thesis invalidation does not require price overvaluation**: if a
  thesis invalidator is triggered (see `investment-thesis-structure.md`), issue
  SELL regardless of where price sits relative to the intrinsic value estimate.
  The estimate itself becomes unreliable once the thesis breaks.
- **HOLD is an active verdict, not default**: HOLD means the current
  price-to-value relationship does not create sufficient margin of safety for a
  new purchase, but the thesis remains intact and no trigger for exit has fired.
  It is NOT the verdict to issue when analysis is incomplete.

### HOLD Band Calibration

The ±15% HOLD band is a practical boundary, not a bright line. Factors that
tighten the band (require tighter price-to-value alignment before holding):

- High uncertainty in the intrinsic value estimate (wide low-to-high range)
- Recent material changes in business fundamentals not yet reflected in the estimate
- Elevated position concentration in the portfolio

Factors that widen the band (tolerate more deviation before triggering BUY or SELL):

- High frictional costs (taxes, spreads) on the security
- High-quality business with durable competitive advantage (Klarman Ch.4: the
  intrinsic value range narrows for predictable cash flows, justifying smaller
  required discount)
- Catalyst not yet identified (unclear what would unlock value)

## Intrinsic Value as Range, Not Point

Klarman (Ch.4, Ch.6) establishes this as a first principle: intrinsic value is
an estimate with inherent uncertainty, not a calculation yielding a precise
number. The verdict grammar requires that intrinsic value always be expressed
as a **three-scenario range**:

| Scenario | Description |
|---|---|
| **Low case** | Conservative assumptions: slowest plausible growth, widest plausible discount rate, stressed margin profile |
| **Base case** | Central assumptions: management guidance, peer comparables, normalized macro |
| **High case** | Optimistic assumptions: best-case growth, operational leverage, favorable macro |

The verdict emerges from where the current price sits relative to the range:

```
     Low      Base     High
      |---------|---------|
 ↓                              → price well below low case → strong BUY signal
          ↓                     → price at base, below high → HOLD territory
                        ↓       → price above high case     → SELL territory
```

**Sensitivity table (required)**: identify the 2–3 assumptions that move the
range most. Tie to the valuation model in `investment-security-valuation.md`.
If a single assumption (e.g., terminal growth rate) can swing the range by
> 40%, that assumption must be flagged as a key uncertainty and the conviction
grade must reflect it (see Grade C below).

## Conviction Grading

Conviction grade is a **separate dimension** from the Buy / Hold / Sell
verdict. It qualifies certainty and drives position sizing; it does not alter
the direction of the verdict.

### Grade Definitions

| Grade | Required Conditions | Position Sizing Signal |
|---|---|---|
| **A** | Strong variant perception + multiple independent valuation methods converge + identifiable catalyst with timeline | Full position size per `position-sizing-and-risk.md` |
| **B** | Partial variant perception OR single valuation method converges OR catalyst unclear | Half or partial position; add on evidence accumulation |
| **C** | High estimation uncertainty (wide range); speculative thesis; catalyst not identified | Starter / exploratory position only; size must reflect uncertainty |

**Variant perception** (Klarman, implied throughout): the investor holds a view
on intrinsic value that differs from the market consensus, and can articulate
why the market is wrong. Without variant perception, there is no expected edge
— the market price already reflects the consensus view.

**Multiple independent methods converge**: for Grade A, at least two of the
following methods produce estimates within 20% of each other:
- DCF (see `investment-security-valuation.md`)
- Comparable company multiples
- Precedent transactions
- Asset-based / liquidation value
- Dividend discount model (where applicable)

**Identifiable catalyst with timeline**: Grade A requires not only that the
security is undervalued but that there is a reason to believe the market
will recognize the value within a foreseeable horizon (12–36 months). Without a
catalyst, a security can remain undervalued indefinitely. Note: Klarman (Ch.6)
explicitly acknowledges that the absence of a catalyst does not invalidate the
investment case — it extends the timeline and lowers Grade to B or C.

### Conviction Grade Anti-Patterns

- Using Grade A as a proxy for "I like this management team."
- Assigning Grade A without checking whether variant perception exists —
  if the thesis matches sell-side consensus, there may be no edge even if the
  valuation math is correct.
- Conflating high analyst confidence in the model with Grade A — model
  precision is not the same as variant perception or catalyst identification.

## Bias Catalog

The following biases are drawn from Damodaran (2012) Ch.35 and Kahneman (2011)
Ch.12 and Ch.24. For each: the observable signature in a verdict or valuation
output, and the de-biasing action to apply before publishing.

### Anchoring Bias

**Description**: The verdict or valuation is pulled toward a salient reference
point — typically the analyst's cost basis, a recent high/low, or a round-number
target — rather than computed from current intrinsic value.

**Observable signature in output**:
- "The stock is attractive because it has fallen 40% from its high."
- Intrinsic value estimate happens to closely match the original purchase price.
- HOLD verdict issued on a position that would be a SELL if freshly evaluated.

**De-biasing action**: Perform the "fresh eyes" test — if you did not already
own the stock and had no prior price history, what would your verdict be given
only the current intrinsic value estimate and current price? If the fresh-eyes
verdict differs from the current verdict, anchor is likely present.

### Confirmation Bias

**Description**: Evidence supporting the thesis is weighted heavily; evidence
contradicting it is discounted or not sought. Invalidators are
under-documented.

**Observable signature in output**:
- Thesis invalidator section (see `investment-thesis-structure.md`) is short,
  vague, or absent.
- Cited sources are exclusively management guidance, sell-side bulls, or
  company press releases.
- Bear case in the sensitivity table is not genuinely stressed — low case
  is only modestly below base case.

**De-biasing action**: Actively seek and document the strongest bear case.
Identify the 2–3 analysts or investors with the highest-profile short thesis
and steelman their argument in the deliverable. Apply Mauboussin & Callahan's
(2014) checklist: "What would make me wrong?" before publishing.

### Narrative Bias

**Description**: A compelling qualitative story replaces quantitative analysis.
The verdict is driven by the attractiveness of the story rather than the
price-to-value relationship.

**Observable signature in output**:
- Valuation section is thin or absent; most of the deliverable is qualitative
  business description.
- BUY verdict issued with the intrinsic value range either missing or
  suspiciously close to the current price (i.e., constructed to justify the
  conclusion rather than derived independently).
- "This company is going to change the world" as the operative investment
  rationale.

**De-biasing action**: Require the intrinsic value range and margin of safety
calculation to be completed before writing the qualitative narrative. The
numbers must lead; the story explains them. If the math doesn't support BUY,
the story doesn't override it.

### Recency Bias

**Description**: The most recent quarter's results dominate the base case,
with insufficient weight given to longer-term base rates.

**Observable signature in output**:
- The base case revenue or earnings growth rate is approximately equal to the
  last 1–2 quarters' annualized rate.
- Positive earnings surprises produce upward estimate revisions proportionally
  larger than the earnings beat itself (over-reaction to recent data).
- Reference class / base-rate analysis absent from the estimate derivation.

**De-biasing action**: Apply reference class forecasting (see section below)
before accepting inside-view estimates. Anchor on 5–10 year normalized metrics
and update from current data, rather than extrapolating current data forward.

### Overconfidence / Inside-View Bias

**Description**: The analyst constructs an intrinsic value estimate from the
bottom up (detailed model of this specific company) without checking whether
the implicit forecasts are plausible in base-rate terms. Point estimates replace
ranges. Uncertainty is systematically underestimated.

**Observable signature in output**:
- Intrinsic value expressed as a single number, not a range.
- Low case and base case are nearly identical (low case is not genuinely stressed).
- Revenue growth projections in the base case exceed the base rate for the
  industry without explicit justification for why this company is an outlier.
- Margin improvement assumptions that have no comparable precedent in the
  company's own history or peer group.

**De-biasing action**: Express intrinsic value as a three-scenario range (see
above). Validate all quantitative assumptions against Mauboussin & Callahan's
(2014) reference class: "What % of companies with this profile and this starting
base achieved the projected metric over this time horizon?"

### Endowment Effect

**Description**: Reluctance to issue SELL on a position because the analyst
already owns it. The position creates psychological attachment that distorts
the price-to-value assessment.

**Observable signature in output**:
- HOLD verdict issued on a stock trading above the intrinsic value upper bound,
  with rationale centering on non-fundamental factors ("I've held this for 3
  years," "the management team is excellent").
- SELL threshold is systematically higher for owned positions than for the same
  stock evaluated fresh.
- Thesis has been revised upward repeatedly to accommodate rising prices, rather
  than the rising price being recognized as overvaluation.

**De-biasing action**: Apply the "fresh eyes" test (same as anchoring
de-biasing). Separately, apply the **replacement test**: "If I did not own this
stock, would I buy it at this price given my current assessment of intrinsic
value?" If the answer is no, the default verdict should be SELL.

## Reference Class Forecasting

Kahneman (Ch.12, Ch.24) identifies **base-rate neglect** as the dominant
systematic error in investment forecasting: analysts construct detailed
inside-view models of a specific situation while ignoring the statistical
distribution of outcomes for similar situations. Mauboussin & Callahan (2014)
operationalize the correction into a step-by-step protocol for investment
decisions.

### Protocol (Required Before Publishing Base-Case Estimates)

1. **Identify the reference class**: define the population of companies or
   situations that are structurally similar to the subject. Criteria: same
   industry, similar starting revenue base, similar competitive position, similar
   macro regime. Be specific — "tech companies" is not a reference class;
   "SaaS companies with $200–500M ARR, NRR > 110%, and EBITDA margins of
   −10% to +5% transitioning to profitability" is a reference class.

2. **Establish the base rate**: for the projected outcome (e.g., "revenue
   growth of 25% CAGR over 5 years"), what % of the reference class actually
   achieved that outcome? Cite data source.

3. **Start with the outside-view estimate**: set the base-case projection at
   the reference class median, not the bottom-up model output. This is
   Kahneman's "outside view first" discipline.

4. **Update from inside-view evidence**: identify specific, verifiable,
   quantified reasons why this company should deviate from the base rate — and
   in which direction. Reasons must be facts, not narratives. ("This company's
   NRR of 127% exceeds the reference-class median of 108% — historically,
   companies with NRR > 120% show 15pp higher 5-year CAGR than the reference
   class median" is an update. "This company has an exceptional management team"
   is not.)

5. **Document the adjustment and its size**: state explicitly what adjustment
   was applied to the outside-view base rate and why. This creates an auditable
   record that can be checked against outcome data later.

### Reference Class Calibration Check

Per Mauboussin & Callahan (2014): before publishing, ask "What is the base rate
for the precise outcome this thesis requires?" If the required outcome has a
base-rate frequency of < 10% in the reference class, the position must be
(a) assigned Grade C conviction and (b) sized at the exploratory level. The
thesis can still be directionally correct — but the base rate is a hard
constraint on conviction grade regardless of the inside-view model quality.

## Verdict Checklist

Five binary checks required before publishing a verdict. The deliverable
cannot be marked complete until all five are satisfied.

| # | Check | Pass condition |
|---|---|---|
| 1 | Intrinsic value expressed as a range? | Low / base / high case all populated with distinct values |
| 2 | Margin of safety explicitly stated vs. the range? | MoS % computed against the central estimate; floor requirement met (≥30% for BUY, or justified exception documented) |
| 3 | Conviction grade assigned (A / B / C)? | Grade documented with rationale: variant perception assessed, method convergence checked, catalyst reviewed |
| 4 | Bias catalog reviewed — any red flags acknowledged? | Each of the 6 biases explicitly checked; any flags noted with de-biasing action taken or documented as limitation |
| 5 | Thesis invalidators listed? | Link to `investment-thesis-structure.md` deliverable; at least 2 invalidators documented with observable triggers |

A verdict with any check failing must be marked **DRAFT — NOT FOR PUBLICATION**
until the gap is resolved.

## Relationship to Other Standards

This file is the **terminus** of the investing-team analysis pipeline:

```
investment-security-valuation.md    → intrinsic value range input
investment-thesis-structure.md      → thesis + invalidators input
         ↓                                     ↓
         └────────── decision-framework-and-verdict.md ──────────┐
                              verdict, conviction grade            │
                                                                   ↓
                                              position-sizing-and-risk.md
                                              (sizing downstream of verdict)
```

- **`investment-security-valuation.md`**: performs the DCF, comps, and asset-
  based valuation work that produces the intrinsic value range. This file
  consumes that range; it does not replicate the valuation methodology.
- **`investment-thesis-structure.md`**: defines the thesis structure including
  invalidation triggers. This file requires that thesis invalidators be
  documented before a verdict is publishable; it does not define how to write
  them.
- **`position-sizing-and-risk.md`**: takes the verdict (Buy / Hold / Sell)
  and conviction grade (A / B / C) as inputs and translates them into position
  size as a fraction of portfolio. This file does not determine position size.

A worker who has completed the valuation (per `investment-security-valuation.md`)
and documented the thesis (per `investment-thesis-structure.md`) uses this file
to issue the final verdict. A worker who has not completed those upstream steps
cannot satisfy Checklist items 1, 2, and 5, and therefore cannot publish.

## JP Terminology Note

No distinct Japanese verdict-grammar tradition parallels the Graham-Klarman
framework for Buy / Hold / Sell + margin of safety. Japanese securities analysis
practice (日本証券アナリスト協会 / SAAJ certification) uses equivalent directional
labels (買い推奨 / 中立 / 売り推奨) with similar price-target logic but does not
formalize the margin-of-safety floor as a required entry discipline in the way
Graham Ch.20 does. The framework in this file is drawn from the Anglo-American
value investing canon and applies globally. No JP-specific overlay is added;
no symmetry is forced.
