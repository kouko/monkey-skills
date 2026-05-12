# Simulation Modeling — Past Application Cases

Five calibrating cases for the merged simulation-modeling skill: three
from sk11 (stock-flow translation — c24, c25, c26) and two from sk12
(learning-not-answers — c03, c04). Read all five before translating a
CLD or interpreting a simulation output — they encode the plumbing-
diagram worked example, the stock-flow arithmetic at planetary scale,
the fuzzy-stock-can-be-reported precedent, and the two canonical
exponential-misread cases.

## Case 1 — Provincial Car Dealership Growth Simulation (c24)

- **Problem**: Car dealership wants to project growth under different
  reinvestment strategies. Spreadsheet model produces a single confident
  number. Risk of model-induced overconfidence (ce15).
- **Methodology applied (translation half)**: Build CLD → classify
  variables (customer base = stock, sales/month = flow, retained
  earnings = stock, marketing spend = flow) via the time-freeze test.
  Translate to ithink plumbing diagram. Add fuzzy MARKET SATURATION
  EFFECT as response curve. SATISFIED CUSTOMER BASE collapsed to a
  single stock per Rule 4 aggregation; MARKET SIZE as input dangle;
  INVESTMENT RATIO as policy dangle (lever — twists the marketing-
  spend flow).
- **Methodology applied (use-of-model half)**: Sherwood explicitly
  warns that MARKET SATURATION EFFECT is fuzzy by construction; the
  four-decimal-place curves the simulator produces are spurious as
  forecasts but valuable as a vehicle to discover the policy insight
  below. Output framed as graphs over a range of INVESTMENT RATIO
  values, not as a single revenue projection.
- **Conclusion**: 50% reinvestment ratio yields almost identical sales
  to 100%, with doubled retained earnings — the R-loop is binding-
  constrained by saturation; pedaling harder wastes cash. This is a
  *learning* output, not an answer: it tells the manager which side
  of the threshold the lever sits on, not what next quarter's revenue
  will be.
- **Outcome**: Flagship end-to-end case — CLD → plumbing diagram →
  ithink → policy experimentation. Quantitatively confirms the
  constraint-relief doctrine that pure CLDs only suggested. Connects
  to `limits-to-growth-take-the-brakes-off` at the diagnosis layer.

## Case 2 — Lake Chad: 95% Shrinkage as Stock-and-Flow Arithmetic (c25)

- **Problem**: Lake Chad shrank 95% over decades. Single-cause
  explanations (climate alone, irrigation alone) dominated public
  discourse — no stock-flow framing.
- **Methodology applied**: Lake volume is a stock; inflow (rivers,
  rainfall) and outflow (evaporation, irrigation extraction) are
  flows. Time-freeze test trivially distinguishes them. When outflow
  exceeds inflow for sustained periods, stock declines — the
  arithmetic is unambiguous and dominates any rhetoric.
- **Conclusion**: Stock-and-flow framing makes the multi-decade
  decline structurally inevitable rather than mysterious. The
  question is not "what caused it?" (multiple flows contribute) but
  "which flow is most adjustable?" — a lever-vs-outcome question
  re-stated in flow vocabulary.
- **Outcome**: Real-world stock-and-flow arithmetic at planetary
  scale; demonstrates the formalism's portability beyond business.
  Counters the "stocks and flows is just a corporate-finance trick"
  objection.

## Case 3 — Skandia Intellectual-Capital Reporting (c26)

- **Problem**: Knowledge / intellectual capital "isn't on the
  balance sheet, so we can't manage it." Classic accountant-bias
  failure (ce05, ce12).
- **Methodology applied**: Skandia (Edvinsson, 1995) treated
  intellectual capital as a fuzzy stock — accumulates and depletes,
  measurable at an instant even if imprecisely — and built formal
  reporting around it (the *Visualizing Intellectual Capital*
  supplementary annual report).
- **Conclusion**: Fuzzy stocks like knowledge / morale / reputation
  are legitimately modelable; the refusal-to-model is the worse error.
  The time-freeze test still works: at any instant Skandia could
  report "intellectual capital" as a state, even though it had no
  GAAP procedure.
- **Outcome**: Demonstrates that the stock-flow formalism extends to
  fuzzy variables (composing with the fuzzy-elevation half of
  `cld-craft`), not just measured financials. Use this case to defend
  Stage-1 step 2 (time-freeze test) when stakeholders push back on
  classifying a fuzzy variable as a stock.

## Case 4 — Frogs and the 50-Day Pond (Chapter 5, c03)

- **Problem**: Canonical thought-experiment for exponential
  late-detection. Lily-pads double every day, cover the pond at day
  50. Frogs need 10 days to deploy a countermeasure. Question: when
  is the last day they can act?
- **Methodology applied**: Doubling-time-vs-response-delay diagnostic.
  T = 1 day. D = 10 days. The last possible action moment is when
  the pond is 1/2^10 ≈ 0.1% covered — day 40. By day 49 the pond is
  50% covered and visibly alarming, but it is already too late.
- **Conclusion**: Linear extrapolation of an exponential trajectory
  systematically underestimates the urgency until the response window
  has closed. The visible-bend point in an R-loop comes *after* the
  last-action threshold whenever D ≥ T or even D/T is non-trivial.
- **Outcome**: Canonical reference for slow-then-sudden exponential
  behavior. Use this case in step 10 of the Execution flow when
  stakeholders say "growing slowly, plenty of time." The arithmetic
  refutes the intuition in two lines.

## Case 5 — Caulerpa taxifolia "Killer Algae" (Chapter 5, c04)

- **Problem**: Real-world frogs problem. *Caulerpa taxifolia* (a
  fast-growing aquarium-trade alga) escaped Monaco's Oceanographic
  Museum in 1984. Alexandre Meinesz raised the alarm in 1989. By
  ~2001 eradication was declared a "utopian dream."
- **Methodology applied**: Same doubling-time-vs-response-delay
  diagnostic as c03, but in a system where T and D are both fuzzy
  and the reinforcing loop is biological-spread. The visible footprint
  at year 5 was small enough to dismiss; the doubling rate was high
  enough that visible footprint at year 15 was uncontainable.
- **Conclusion**: The reinforcing loop won because human response
  calibrated to *current visible size*, not to *doubling rate × response
  delay*. The Meinesz alarm at year 5 was the last-action moment;
  the public sense of urgency at year 15 was the eulogy.
- **Outcome**: Real-world counterpart to c03. Use this case to
  demonstrate that the exponential-misread failure mode is not a
  toy example — it happens at scale in ecology, public health,
  reputational risk, and platform-network growth. Pairs naturally
  with the "frogs" case as a thought-experiment / live-example pair
  in stakeholder workshops.
