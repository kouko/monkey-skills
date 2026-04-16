---
name: macro-regime-diagnosis
description: L1 macro regime diagnosis only — Investment Clock, yield curve, inflation trajectory → asset-class tilt recommendation
---

# Macro Regime Diagnosis Protocol

Standalone L1 protocol. Diagnoses the current macro regime and produces an
asset-class tilt recommendation. Does NOT produce a stock-level verdict —
for single-security analysis use `protocols/deep-equity-research-memo.md`.

## When to Use This Protocol

| Use this protocol | Use deep-equity-research-memo.md |
|---|---|
| "What regime are we in?" | Specific ticker or company |
| "IC call?" | "Should I buy X?" |
| "Macro environment for investing?" | Full investment thesis |
| "Asset allocation tilt?" | Security valuation |
| Regime input for a downstream model | Top-down thesis with stock selection |

## Primary Sources

- `standards/investment-macro-regime.md` — Greetham & Hartnett 2004 IC +
  Dalio 2018 debt cycle + Hedgeye GIP + Kumar & Persaud 2002 RAI

## Phase 1: Data Intake

Accept any combination of the following inputs. Note the as-of date for each.
Missing inputs reduce confidence; do not fabricate data points.

| Indicator | Preferred Source | Signal to Extract |
|---|---|---|
| Yield curve: 10Y-2Y spread | FRED T10Y2Y | Positive / flat / inverted; direction of change |
| CPI / inflation trajectory | FRED CPIAUCSL YoY | Accelerating / decelerating vs. prior 3–6 months |
| Industrial production or PMI | FRED INDPRO; ISM / Markit PMI | Above/below 50; rate of change |
| Credit spreads | FRED BAMLH0A0HYM2 (HY OAS) | Tightening / widening |
| User narrative description | As provided | Extract directional signals |

If the user provides a regime narrative without raw data, extract the implied
directional signals (growth up/down, inflation up/down) and proceed. Note
reliance on narrative vs. primary data in the Provenance section.

## Phase 2: Investment Clock Regime Call

Per `standards/investment-macro-regime.md` — Greetham & Hartnett 2004
Merrill Lynch Investment Clock (2×2 growth direction × inflation direction):

| Quadrant | Growth | Inflation | Favored Asset Class |
|---|---|---|---|
| Reflation | Decelerating | Decelerating | Bonds |
| Recovery | Accelerating | Decelerating | Stocks |
| Overheat | Accelerating | Accelerating | Commodities |
| Stagflation | Decelerating | Accelerating | Cash |

**Execution:**

1. Map each available indicator to a growth signal (accelerating / decelerating)
   or inflation signal (accelerating / decelerating).
2. Assign the dominant quadrant. If signals conflict, note the tension and
   identify the most leading indicators (yield curve and PMI lead; CPI lags).
3. If on a border between two quadrants (transitioning), specify: from/to
   direction and estimated lag before transition completes.
4. State confidence level:
   - High: 3+ indicators consistently point to one quadrant
   - Medium: 2 indicators consistent, 1 conflicting, or data is 1–2 months stale
   - Low: indicators split, or relying primarily on narrative description

Do NOT use business-cycle terminology (expansion / slowdown / contraction /
recovery) when characterizing the Investment Clock result. Business cycles
describe GDP dynamics; the Investment Clock describes relative asset-class
performance across growth × inflation regimes. Conflating them is a fatal
attribution error.

## Phase 3: Dalio Debt Cycle Cross-Check

Per `standards/investment-macro-regime.md` — Dalio 2018 *Principles for
Navigating Big Debt Crises*. Brief diagnostic only — Dalio is a structural
risk overlay, NOT an asset-allocation prescription.

Map current credit conditions to the 6-phase sequence:

1. **Early part of the cycle** — healthy debt growth, debt service manageable
2. **Bubble** — credit decoupling from income growth / fundamentals
3. **Top** — central banks tighten OR debt service costs break borrowers
4. **Depression** — bubble bursts, credit contracts, policy rate hits zero-bound
5. **Beautiful Deleveraging** — coordinated austerity + restructuring +
   money printing while growth stays (just) positive
6. **Pushing on a String / Normalization** — monetary policy loses marginal
   efficacy; cycle resets toward Phase 1

State which phase best describes BOTH:
- Short-term debt cycle (5–8 year credit cycle)
- Long-term debt cycle (50–75 year leverage cycle), if discernible

Cross-check: is the Dalio phase consistent with the IC quadrant from Phase 2?
If not, note the tension explicitly. Example of a tension: IC says
"Recovery → Stocks lead" + Dalio says "Bubble phase of the short-term cycle"
— tactical call is still "stocks lead" per IC, but structural risk overlay
flags credit-overstretch and downstream hedging disciplines apply.

Cite Dalio 2018 for the framework. Where relevant, cite Koo 2008
*The Holy Grail of Macroeconomics* for the balance-sheet-recession
deep-dive on Depression → Beautiful Deleveraging phases.

## Phase 4: Risk Appetite Assessment

Per `standards/investment-macro-regime.md` — Risk Appetite Index (RAI).
Peer-reviewed origin: Kumar & Persaud 2002 *International Finance* 5(3).

Assess whether the current environment shows high or low risk appetite by
examining the relative performance of risky vs. safe assets:

| Signal | Risk Appetite |
|---|---|
| High-beta equities, HY credit outperforming Treasuries, gold | High / Risk-on |
| Mixed signals, unclear leadership | Moderate |
| Treasuries, gold, USD outperforming equities, HY | Low / Risk-off |

**Disambiguation**: do not conflate RAI variants — Goldman Sachs publishes a
Risk-Aversion Index (inverse semantics, NOT an RAI); Citi publishes a
Panic/Euphoria model; BofA publishes a Bull & Bear Indicator (Hartnett), NOT
a "Global Investor Confidence Index"; State Street ICI = Froot & O'Connell
NBER WP 10157. Specify which variant is being used if citing any of these.

Use RAI as a positioning / sentiment indicator to confirm or qualify the IC
regime call — NOT as a primary regime signal.

## Phase 5: Asset-Class Tilt Recommendation

Integrate the IC quadrant (Phase 2), Dalio overlay (Phase 3), and RAI
direction (Phase 4) into a 3-asset-class tilt:

- **Overweight (OW)**: regime systematically favors this asset class; risk
  appetite consistent; structural overlay not contradicting
- **Neutral (N)**: regime ambiguous or mixed signals; or IC favors but Dalio
  overlay flags structural risk
- **Underweight (UW)**: regime disfavors; or structural overlay materially
  qualifies IC tilt

**Taiwan idiosyncratic check**: if the context is Taiwan-focused, note whether
the Taiwan market has a deviation from the global regime — for example, global
Stagflation but Taiwan tech export cycle entering Recovery (driven by AI
capex demand), or global Recovery but Taiwan facing domestic demand headwinds.
Cross-reference `standards/taiwan-equity-frameworks.md` for Taiwan-specific
signals (三大法人 flow, 月營收 trend).

## Output

```
## Macro Regime Diagnosis — {DATE}

### Investment Clock Quadrant: {QUADRANT}

| Signal | Direction | Source | As-of |
|---|---|---|---|
| Growth (PMI / IP) | Accelerating / Decelerating | | |
| Inflation (CPI YoY) | Accelerating / Decelerating | | |
| Yield curve (10Y-2Y) | Positive / Flat / Inverted | | |
| Credit spreads | Tightening / Widening | | |

Confidence: {High / Medium / Low}
[Rationale: which signals agree, which conflict]

Border note (if applicable): [Transitioning from X to Y; expected lag]

### Dalio Debt Cycle Phase: {PHASE}

Short-term cycle (5–8 yr): {Phase name}
Long-term cycle (50–75 yr): {Phase name or "indeterminate"}

IC consistency check: [Consistent / Tension noted]
[If tension: describe the tactical vs. structural divergence and its implications]

### Risk Appetite: {HIGH / MODERATE / LOW}

[Evidence: relative performance of risky vs. safe assets]
[RAI variant used, if specific product cited]

### Asset-Class Tilt

| Asset Class | Tilt | IC Basis | Dalio Qualifier |
|---|---|---|---|
| Equities | OW / N / UW | | |
| Fixed Income | OW / N / UW | | |
| Real Assets / Commodities | OW / N / UW | | |
| Cash | OW / N / UW | | |

### Regime Uncertainty

[If ambiguous: state two plausible scenarios]

| Scenario | Probability Weight | IC Quadrant | Implication |
|---|---|---|---|
| Scenario A | [%] | | |
| Scenario B | [%] | | |

[Weights must sum to 100%]

### Taiwan Deviation (if applicable)

[Global regime vs. Taiwan-specific cycle divergence; sources]

### Provenance

[Data sources, product names, as-of dates; note any reliance on narrative
description vs. primary data]
```

## Rules

- Investment Clock quadrant must use the four named regimes (Reflation /
  Recovery / Overheat / Stagflation) — never business-cycle vocabulary.
- Dalio's 6 phases must be named verbatim when cited. Do not collapse to
  4 or 5 phases or substitute business-cycle vocabulary.
- Dalio is diagnostic only — do NOT derive asset-allocation prescription
  from Dalio phases. Asset-class calls come from the Investment Clock.
- RAI is a sentiment / positioning qualifier, NOT a primary regime signal.
- Every data point must carry an explicit as-of date.
- Confidence level (高/中/低) is required on every forward-looking claim per
  `standards/confidence-and-claim-language.md`.
- Do NOT cite "Damodaran's macro framework" — no such framework exists.
  For regime models: cite Greetham & Hartnett 2004 (IC), Dalio 2018
  (debt cycle), or McCullough 2024 (Hedgeye GIP).
- Hedgeye GIP (McCullough 2024) is a 2-axis + derived policy overlay,
  descended from Dalio's 1996 4-box — NOT a 3-axis framework and NOT a
  refinement of Greetham IC. Add as an optional refinement only when
  requested or when a more granular quadrant read is needed.
