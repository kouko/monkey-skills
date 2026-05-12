---
name: simulation-modeling
description: |
  Translate a cld-craft-produced CLD into a quantitative stock-and-flow plumbing diagram AND use the resulting model for learning rather than point-forecast. TEXT-ONLY discipline — produces a labeled plumbing diagram + doubling-time-vs-response-delay arithmetic + graphs-not-numbers framing in prose; no executable simulator or numeric solver bundled (v0.2 candidate). Pipeline: time-freeze classification → stock/flow split → uniflow/biflow detection → lever-to-flow / outcome-to-stock mapping; then doubling-time-vs-response-delay diagnostic on any reinforcing loop, graphs-not-numbers output framing, refusal to extrapolate fuzzy-input simulations as forecasts. NOT for deterministic single-number problems (tax, accounting, regulatory submission, pricing engines), stochastic-shock-dominant systems, or homogeneous-aggregation when customer heterogeneity is load-bearing. Triggers: "model this", "stock and flow", "convert CLD to simulation", "is morale measurable", "what's the right answer", "extrapolate to 2030", "two more decimal places", "the model says", "growing slowly, plenty of time". KEYWORDS: stocks and flows, plumbing diagram, simulation, system dynamics, time-freeze test, uniflow, biflow, learning vs forecasting, doubling time, response delay, exponential growth, false precision, detail vs dynamic complexity. JA: ストック・フロー変換・学習用シミュレーション / zh-TW: 存量流量轉換・學習用模擬.
source_book: Seeing the Forest for the Trees — Dennis Sherwood
source_chapter: Chapter 12 — Turbo-charging your systems thinking; Chapter 13 — Modeling business growth (with Ch 5 support)
source_language: en
tags: [systems-thinking, system-dynamics, stocks-and-flows, simulation, modeling, quantitative, exponential-growth, false-precision]
related_skills:
  - slug: cld-craft
    relation: depends-on
---

# Simulation Modeling (Stock-Flow Translation + Learning-Not-Answers Discipline)

## R — Reading

> "Every variable can be classified as either a stock or a flow."
> — Dennis Sherwood, Chapter 12

> "Most business objectives — and certainly all the most important ones — can be expressed as the optimization of a portfolio of stocks. The only actions that a manager can take are to readjust the flows."
> — Dennis Sherwood, Chapter 12

> "Models can be used for two main purposes — to get answers, or to gain understanding. ... System dynamics models do not promise such precision. ... It is not about answers — it is all about learning."
> — Dennis Sherwood, Chapter 13

> "Exponential growth masquerading as linear!"
> — Dennis Sherwood, Chapter 12

## I — Interpretation

A CLD shows *which variables influence which* but does not distinguish state-variables from rates-of-change. Two disciplines complete the bridge from qualitative loop diagram to defensible quantitative reasoning: (1) **stock-flow translation** — the mechanical craft of classifying every variable, sorting flows by direction, mapping levers to flows, and drawing a simulation-ready plumbing diagram; (2) **learning-not-answers** — the use-of-model discipline that prevents the resulting simulation from being read as a forecast.

**Stock-flow translation.** Sherwood's translation discipline forces every variable to declare itself: **stock** (accumulates over time, measurable at an instant — bathtub water level, customer count, cash, morale) or **flow** (changes a stock over an interval, measurable only as rate — hiring/quarter, churn/month, spending/year). The **time-freeze test** is the diagnostic: if time stops and you can still report the number, it is a stock. If the number is meaningless without "per period," it is a flow. Counter-intuitive consequence: "interest rate" sounds like a flow but is a stock (a state of the financial system at an instant); "births" sounds like a stock but is a flow (births-per-year). P&L items are flows; balance-sheet items are stocks.

Two further moves complete the translation: (a) **uniflow vs biflow** — some flows are physically one-directional (births can only add to population; pouring coffee can only fill) and produce CLD links valid only in their natural direction. Biflows (retained earnings, change-in-price) can go negative. (b) **Levers = flows, outcomes = stocks** — re-states the lever/outcome distinction in stock-flow vocabulary and surfaces inevitable trade-offs (every tap fills one bath while potentially draining another).

**Learning-not-answers.** Sherwood draws a sharp line between two purposes of modeling. *Answer models* operate on hard data with rule-defined logic and produce a number — tax optimization, accounting roll-forwards, pricing engines. Spreadsheets are the right tool. *Learning models* operate on fuzzy variables with mental-model inputs and produce a graph plus sharpened intuition about how the system behaves — strategic planning, scenario testing, policy exploration. System dynamics is the right tool. The two failure modes that follow from confusing them are symmetric: (a) demanding spreadsheet precision from a learning model (the CFO asking for two more decimal places on a 2030 churn projection); (b) using a deterministic spreadsheet where the dynamic complexity demands a feedback model (extrapolating early-stage exponential growth as if it were linear). Both errors flow from confusing *detail complexity* (many static elements) with *dynamic complexity* (a few elements evolving via feedback over time).

The bridge between the two halves: the same plumbing diagram that satisfies the translation discipline is the artifact that gets used wisely (or misused). A stock-flow model built with rigor and then read as a forecast is half-completed work; the discipline below sequences translation first (build the plumbing) then use-of-model second (compute doubling-time vs response-delay, frame output as graphs not numbers, refuse precision beyond one doubling-time horizon).

The point is not to build a forecast. It is to make the structure precise enough to simulate, then use the simulation as a *learning* tool — what scenarios would change what stocks — not as a precision-decimal answer machine.

## A1 — Past Application

The cases that calibrate both translation discipline and learning-not-answers use (Provincial Car Dealership Growth Simulation c24, Lake Chad 95% shrinkage c25, Skandia intellectual-capital reporting c26, frogs and the 50-day pond c03, Caulerpa taxifolia killer algae c04) are detailed in `references/cases.md`.

**MANDATORY — READ ENTIRE FILE**: Before translating a CLD or interpreting a simulation output, you MUST read [`references/cases.md`](references/cases.md) (~100 lines) for the plumbing-diagram worked example, the stock-flow arithmetic at planetary scale, the fuzzy-stock-can-be-reported precedent, and the two canonical exponential-misread cases.

## A2 — Future Trigger ★

### When will the user need this skill?

1. Finance team wants to support a retention-budget decision but says "morale isn't measurable so it's not modelable."
2. Team has a qualitative CLD and wants to upgrade it to a simulation that can run policy experiments.
3. Discussion of "growth strategy" where it's unclear which variables are levers (you can twist them) and which are outcomes (consequences).
4. Project that conflates rates with quantities (e.g., "we need to grow revenue by $5M" — but revenue is a flow; the stock to grow is cumulative paid customers or ARR).
5. Resource depletion problems (water table, talent pool, customer pool) where inflow/outflow framing is missing.
6. CFO/finance team demands more decimal places on a long-horizon forecast driven by fuzzy variables (churn, NPS, market share, saturation).
7. Board extrapolates 60% → 40% → 20% revenue growth as "still positive" without recognizing the deceleration as a balancing-loop signature.
8. A team proposes a 50-tab spreadsheet "to model strategy" — detail complexity dressed up as dynamic complexity.
9. A simulation output is being treated as a forecast: "the model says X."
10. Slow-growth signal: "it's only 1% of the market, plenty of time" applied to an unconstrained reinforcing loop.

### Language signals

- "Model this." / "Convert this CLD to a simulation."
- "Is X measurable? Can we model it?"
- "Stock and flow." / "Plumbing diagram."
- "What's the rate vs the level here?"
- "Levers vs outcomes."
- "What's the right answer?"
- "Extrapolate to 2030." / "Two more decimal places."
- "The model says…"
- "Growing slowly, plenty of time." / "Linear projection."
- "Forecast accuracy."

### Distinction from neighboring skills

- vs. `cld-craft` (sk03 + sk04 merge): `cld-craft` produces the qualitative CLD and elevates fuzzy variables; this skill translates that CLD into a quantitative plumbing diagram AND governs how the resulting simulation's output should be interpreted. Sequential — `cld-craft` first, then this skill.
- vs. `loop-and-link-primitives` (sk01 + sk02 merge): the foundational sk01-style R/B classification is what determines whether a doubling-time-vs-response-delay diagnostic is appropriate at all (only R-loops produce exponentials). This skill applies the diagnostic; the primitives skill names which loop is active.
- vs. `strategy-lever-and-cascade` (sk07 + sk08 merge): the lever / outcome distinction is restated in flow / stock vocabulary here, making it modelable. Use this skill when you need to *model* a strategy decision; use `strategy-lever-and-cascade` when you need to *frame* it.
- **Internal note on the two halves**: stock-flow translation produces the artifact; learning-not-answers governs its use. Skipping the translation half leaves "use models for learning" as rhetoric; skipping the learning half leaves the simulation vulnerable to false-precision misuse.

## E — Execution

```
E flow:
  have a clean CLD? ── no → run cld-craft (sk03+sk04) first
        │ yes
        v
  Stage 1: TRANSLATION (build the plumbing)
    apply time-freeze test to every variable
        │
        v
    cross-check stock-vs-flow with P&L / balance-sheet heuristic
        │
        v
    classify each flow as uniflow or biflow
        │
        v
    map levers → flows, outcomes → stocks
        │
        v
    draw plumbing diagram + add fuzzy response curves
        │
        v
  Stage 2: USE-OF-MODEL (learn, don't forecast)
    classify modeling purpose: one number vs understanding?
        │
        ├── one number → switch to spreadsheet, exit
        └── understanding → continue
        │
        v
    build smallest learning model that captures the question
        │
        v
    run doubling-time vs response-delay diagnostic on every R-loop
        │
        v
    simulate to learn; frame output as graphs not numbers
```

When this skill activates, follow these steps:

### Stage 1 — Translation (sk11 protocol)

1. **Start from an existing CLD** — if no CLD exists, halt and run `cld-craft` first. Translation without a qualitative model produces classification debates with no anchor.

2. **Apply the time-freeze test to every variable** — for each node, ask: "if time stops right now, can I report this number meaningfully?" Yes = stock. No (number needs per-period unit) = flow. Tag every variable.
   - Completion criterion: every node on the CLD has a stock-or-flow tag.

3. **Cross-check with the P&L vs balance-sheet heuristic** — P&L items are flows (revenue/quarter, churn/month). Balance-sheet items are stocks (cash, headcount, customer count). Mismatches surface mis-classifications.

4. **Identify uniflow vs biflow for each flow** — physical or definitional one-direction-only (births, deaths, hires, departures) = uniflow, drawn as one-way pipe. Two-direction-capable (retained earnings, price changes, inventory adjustments) = biflow, drawn as tap-that-can-also-drain.

5. **Map levers to flows, outcomes to stocks** — every direct managerial action should land on a flow (twist a tap). If a "lever" turns out to be a stock, it is misclassified — find the underlying flow you actually control.

6. **Draw the plumbing diagram** — stocks as rectangles, flows as pipes-with-taps, clouds for external boundaries. S-links in CLD become inflows, O-links become outflows.

7. **Add fuzzy response curves where needed** — for non-linear effects (saturation, threshold), use hand-drawn graphs (compose with the fuzzy-variable sub-procedure in `cld-craft`).
   - Halt condition: if the model has no fuzzy curves at all, it is probably over-deterministic — Stage 2 will mislead.

### Stage 2 — Use-of-model (sk12 protocol)

8. **Classify the modeling purpose.** Ask: does the decision need *one number* (tax due, payroll total, contract renewal price) or *understanding of dynamic behavior* (will growth stall? will the loop flip? when does the constraint bind?). Completion: a one-line statement of which purpose this model serves and therefore which tool (spreadsheet or system dynamics) is appropriate.
   - Halt condition: if "one number" — STOP. Use a spreadsheet. Continuing into stock-flow simulation is over-engineering.

9. **For learning models, build the smallest model that captures the question.** Per Sherwood's milk-production parable (p24): start with "cows × milk per cow," not a 50-variable econometric mess. Use hand-drawn graphs for fuzzy response curves (p26) — these are valuable precisely because team members draw them differently and the difference surfaces mental-model disagreements. Completion: a system-dynamics sketch with ≤10 nodes and explicit hand-drawn curves on fuzzy links.

10. **Run the doubling-time-vs-response-delay diagnostic.** For any reinforcing loop suspected of producing exponential behavior, compute (or estimate) the doubling time T and the response-deployment delay D. The last possible action moment is when the threat occupies 1/2^(D/T) of the system. If D ≥ T, the visible-bend point comes *after* it is too late. Completion: explicit T, D, and last-action threshold reported alongside any growth chart.

11. **Frame the output as graphs not numbers.** Present curves with sensitivity ranges. Refuse to quote single-point projections beyond one doubling-time horizon for fuzzy-input models. Use the model to ask "what would have to be true for X to occur?" rather than "what will X be?" Completion: every model output paired with (a) the mental-model it encodes, (b) sensitivity range, (c) explicit "this is for learning, not forecasting" framing.

12. **Simulate to learn, not to forecast** — run multiple scenarios with deliberately uncertain inputs. The output is graphs to learn from, not a single number to plan with.
    - Halt condition: if anyone is asking for "2 more decimal places of precision," you have lost the plot — return to step 8 and re-classify the purpose.

## B — Boundary ★

### Do NOT use when:

- **The system is dominated by stochastic shocks / black swans** — financial-contagion crises, viral pandemics, geopolitical ruptures. Deterministic stock-flow models smooth over the very dynamics that matter.
- **Customer / unit heterogeneity is load-bearing** — if your business has distinct customer cohorts (free vs paid, SMB vs enterprise, cohorts by acquisition date, LTV tiers), aggregating into a single homogeneous stock erases the structure that drives your outcomes.
- **The decision needs a single confident number** — stock-flow simulation is a learning tool; it produces ranges and behavior modes, not point estimates. Tax optimization, accounting close, pricing engine for a known cost structure — a spreadsheet IS the right tool here, and system dynamics is over-engineering.
- **No qualitative CLD exists yet** — classification debates without an anchored qualitative model become semantic warfare. Build the CLD first (`cld-craft`).
- **The decision horizon is short relative to any feedback delay in the system** — a one-day operational decision in a system whose loops take quarters to respond. The loops are effectively constant; spreadsheet arithmetic is correct.
- **The question being asked is genuinely "what is the number?" with a defensible single answer** (regulatory submission, contractually-required forecast). Stock-flow framing here invites overconfidence rather than insight.

### Author-warned failure modes

- **Treating a learning-purposed simulation as a forecast (ce15)**: Sherwood explicitly warns about model-induced overconfidence. The simulation's numerical output looks authoritative; managers anchor on it; the original fuzzy-input nature is forgotten. Decisions justified by "the model says" without disclosure of fuzzy inputs collapse the exploration/prediction distinction.
- **Linear extrapolation of early exponential (ce13)**. A forecast drawn as a straight ruler through the last 3 data points is the signature. Stakeholders who say "it's growing slowly, plenty of time" are the frogs (ce14) — by the time the curve visibly bends, the doubling time has eaten the response window.
- **The "if not on balance sheet not real" fallacy (ce05, ce12)**: refusing to model fuzzy stocks (morale, reputation, knowledge) because they aren't measured. Skandia (c26) proves modeling beats refusing-to-model.
- **Over-applying SD to simple linear problems where a spreadsheet suffices.** The symmetric error to false precision. If the question reduces to deterministic arithmetic on hard data, do not dress it up in stocks and flows — the apparatus adds nothing and signals methodological confusion.
- **Detail complexity masquerading as dynamic complexity (ce22).** Long taxonomies, no loops. Map looks like an org chart or BOM. Behavior over time never sketched. "It's complex" used to mean "lots of things" rather than "evolving feedback." Adding detail rarely illuminates dynamics — it usually hides them.

### Author's blind spots / period limitations

- **Deterministic models hide stochasticity and shocks**: Sherwood's Chapter 13 simulation produces smooth S-curves and oscillations. Real systems are punctuated by shocks (2008, 2020, regime changes, single-utterance reputation flips like Ratner's). The skill's output understates volatility unless explicit stochastic terms are added — which Sherwood does not teach.
- **Homogeneous-stock aggregation loses customer segments / cohorts / lifetime tiers**: Sherwood's car-dealership model (c24) has one customer pool. Real SaaS has cohort-by-cohort retention curves, segment-specific LTVs, channel-specific CAC. Aggregating these into a single CUSTOMER_BASE stock erases the structure that determines profitability. Modern practice cohort-segments; Sherwood's 2002 templates do not.
- **ithink / Stella tooling recommendation is dated**: The book recommends ithink/Stella as the simulation tool. In 2026 the standard practitioner stack includes open-source PySD, BPTK-Py (Python-based), browser-based Insight Maker, Loopy (qualitative-only), Vensim PLE (still relevant), plus integration with operational telemetry and ML response-function fitting. ithink/Stella still works but is no longer the default — and is paid / desktop-bound, hindering adoption.
- **Model-induced overconfidence — running simulation creates false precision**: the act of producing a quantitative output makes the model feel more rigorous than the underlying fuzzy inputs warrant. Sherwood names this risk (ce15) but does not provide a discipline strong enough to prevent it. Practitioners routinely cite "the model says" as if the model were oracle rather than mirror.
- **No falsifiability discussion**: Sherwood gives no procedure for knowing when a stock-flow model is *wrong*. Calibration against historical data, out-of-sample testing, sensitivity analysis to fuzzy-input perturbation are all absent from the book's teaching. "Useful for understanding" is social-validation by stakeholder lightbulb-moment, not empirical. In 2026, causal-inference DAGs + counterfactual reasoning + ABM-validation give learning models a falsifiability discipline Sherwood does not provide.
- **Consultant-rescue arc.** Every Sherwood case ends in the manager having the lightbulb moment and changing policy. No case where the model was correct but ignored, where organizational politics overrode the learning, or where the modeler's framing itself was the problem.
- **Pre-behavioral-economics framing.** The "frogs" / late-detection problem (c03, c04) is framed as cognitive limitation but never anchored in Kahneman/Tversky biases — anchoring, availability, exponential-growth-bias are now better-documented mechanisms than Sherwood's intuition-based explanation.

### Easily-confused neighboring methodologies

- **Discrete-event simulation (DES)**: SimPy, AnyLogic for queueing systems. Stock-flow is continuous; DES models individual entities. Different math, different tooling.
- **Agent-based modeling (ABM)**: NetLogo, Mesa. Heterogeneous-agent simulation; better suited when segment heterogeneity dominates (the homogeneous-stock weakness above). Captures heterogeneity Sherwood's aggregate CLDs explicitly suppress.
- **Spreadsheet projection / financial models**: linear extrapolation of historical rates; the antithesis of system-dynamics — no feedback structure, no fuzzy-variable handling. The right tool for "what is the number?" decisions.
- **Monte Carlo forecasting**. Produces probability distributions over outcomes; treats inputs as random variables. Different from Sherwood's "learning" stance — Monte Carlo still aims at *predicting* (with uncertainty quantified), not at *understanding loop structure*.
- **Causal inference with DAGs (Pearl, Imbens-Rubin)**: probabilistic causal graphs for inference from data; complementary, not competing — DAGs determine *which* causal links exist; stock-flow determines *how* they accumulate. The framing is "what intervention would produce what effect" rather than "what feedback structure produces this behavior over time."
- **Differential equations as taught in physics / engineering**: stock-flow is a managerial UI on top of ODE systems; engineers and physicists may prefer the equations directly.

## Related skills

- **depends-on `cld-craft`** — you cannot translate to stock/flow until a clean qualitative CLD exists; this skill is the precision step that follows. The 12 hygiene rules inside `cld-craft` also enforce the noun-not-verb discipline that makes stock/flow classification possible (verbs in node labels destroy the time-freeze test). The fuzzy-variable elevation half of `cld-craft` provides the response-curve sketches that Stage-1 step 7 here imports into the plumbing diagram.

## Audit metadata

> Source-unit codes (f19/f20/f21/f22/p24/p25/p35/p36/ce13/ce14/ce15/ce22/ce28/c03/c04/c23/c24/c25/c26/g20/g26/g27/g39/g40/g41/g42/g43) refer to Stage-1.5 verified.md entries. See `<plugin-root>/references/VERIFIED.md`.

- **Verification status**: V1 ✓ / V2 ✓ / V3 ✓
- **Source units merged**: f19, f20, f21, f22, p24, p25, p35, p36, ce13, ce14, ce15, ce22, ce28, c03, c04, c23, c24, c25, c26, g20, g26, g27, g39, g40, g41, g42, g43
- **Distilled at**: 2026-05-11
- **Merged at**: 2026-05-12 (Profile B merge: sk11 stock-flow-translation + sk12 models-for-learning-not-answers)
- **Output language**: body — English; metadata — English
