# Strategy Lever-and-Cascade — Past Application Cases

Five calibrating cases for the merged `strategy-lever-and-cascade` skill —
three from sk07 (lever-vs-outcome reframe applied at single-decision and
strategy-document level) and two from sk08 (the multi-year cascade and
the dead-strategic-loop diagnosis). Read all five before applying the
skill — they encode (a) the reframe-of-V/T/A loop primitive that makes
"strategy" mechanically actionable, (b) the three-timescale cascade and
3×N reverse-engineering technique, and (c) the failure modes both
authors warn against (outcome-as-target, scenario-as-forecast,
ambition-as-spreadsheet-output).

## Case 1 — TV "Talent Problem" Reframed as Lever Decisions (c15, sk07 + sk09)

- **Problem**: TV company executives framed their issue as "we have a
  talent problem" — declining quality of on-screen output. The framing
  produced lamentation, not action.
- **Methodology applied (lever-vs-outcome)**: "Talent quality" is an
  *outcome*, not a lever. The actual levers were: compensation policy,
  training investment, hire-vs-build mix, executive time spent with
  juniors, willingness to fire poor performers. Each is a B-loop with a
  current target setting that the executives had not re-examined for
  years.
- **Conclusion**: The "talent problem" dissolved into 4-5 specific lever
  decisions, each with a named current target and proposed new target.
  The frame shift moved the conversation from passive complaint to
  active commitment.
- **Outcome**: Three of the levers were reset; talent flow improved
  within 18 months. The same case appears in the multi-perspective skill
  (sk09) where the diagram surfaced *which* levers — the two skills
  compose naturally.

## Case 2 — Outsourcing as Outcome-as-Lever Error (Ch 9 / 10)

- **Problem**: Companies frame "outsourcing" as a lever — "let's outsource
  IT." The single-binary-lever framing buries the real settings.
- **Methodology applied**: Outsourcing is a *bundle of lever changes*
  (in-house headcount target → near-zero, vendor-relationship target →
  active, contract-management capacity target → up). Treating the bundle
  as one binary lever leaves the implicit sub-settings at their default
  (often zero), which is silently wrong.
- **Conclusion**: Any "strategic decision" worth its name decomposes
  into a list of *named lever target changes*. Decisions that resist
  decomposition are usually ambition statements masquerading as
  strategy.
- **Outcome**: Sherwood's general principle: outsourcing programs that
  fail typically fail at the unnamed sub-levers (vendor-relationship
  capacity left at zero), not at the binary outsource/in-house choice.

## Case 3 — Provincial Car Dealership Lever Simulation (c24, Ch 13, sk07 lever frame)

- **Problem**: Owner wanted to "grow the dealership." The ambition was an
  outcome target with no lever attached.
- **Methodology applied**: Sherwood's ithink simulation made the lever
  explicit — *reinvestment ratio* (% of profits plowed back into sales
  staff) — and parameterized it at 100% / 75% / 50%. The outcome
  (revenue, retained earnings) emerged from running the full engine.
- **Conclusion**: At 50%, revenue is nearly identical to 100%, retained
  earnings doubled. The strategy artifact is "set reinvestment-ratio
  target at 50%," not "grow the dealership."
- **Outcome**: Quantitative confirmation that lever-target changes
  produce outcome differences. The simulation existed to test *lever
  settings*, not to forecast outcomes — preserves the
  models-for-learning-not-answers stance.

## Case 4 — Car Dealership Scenario Reverse-Engineering (c24, Ch 13, sk08 cascade frame)

- **Problem**: Same dealership, but now the owner had to commit to a
  reinvestment ratio for the next 5 years against an uncertain market.
  The annual budget loop alone was insufficient — a strategic loop
  decision was required.
- **Methodology applied**: ithink simulation parameterized
  reinvestment-ratio (lever) against three scenarios (high-growth /
  steady / saturation). The 3×N table tested 25% / 50% / 75% / 100%
  reinvestment across the three futures. No probabilities assigned;
  the question was "if this world arrives, are outcomes acceptable at
  this lever setting?"
- **Conclusion**: 50% was *robust* — best in saturation, near-best in
  high-growth (because saturation bound earlier than expected). The
  100% setting was high-upside only in the unbounded-growth scenario,
  which was the least plausible. The choice was robust-lever-set-now,
  not scenario-weighted-bet.
- **Outcome**: Owner committed to 50% reinvestment with quarterly
  market-saturation monitoring as the trigger to reconsider. The
  strategy artifact was "lever reinvestment-ratio target = 50%,
  contingent on quarterly market-saturation monitoring" — *not*
  "double revenue by 2010" (the original ambition).

## Case 5 — Dead 5-Year Plan (V2 derived, common pattern from Ch 10)

- **Problem**: A large organization's 5-year plan had the same numbers
  as the previous year's 5-year plan, shifted one year forward. Each
  annual budgeting cycle simply slid the curve. The "strategic refresh"
  was theater.
- **Methodology applied**: Diagnose the cascade state. The in-year fix
  loop and annual budget loop were running; the *strategic loop was
  dead* — ambition was not being perturbed by any external input. Run
  scenario perturbation: generate 3-4 plausible 2030 worlds (via
  Step 5 Martian-test feature-perturbation, absorbed in v0.6.0), ask "if
  current lever settings stay where they are, are outcomes acceptable
  in each?" For scenarios where the answer is no, reverse-engineer the
  lever target changes required.
- **Conclusion**: The plan was being treated as a *forecast output*
  rather than an *input target dangle*. Restoring the distinction —
  ambition is something the system aims at, not something the
  spreadsheet predicts — reopens the strategic loop and ends the
  same-numbers-shifted-one-year-later pattern.
- **Outcome**: Plan deliverable changed from "single curve" to "3×N
  scenario table + chosen lever settings + monitoring triggers." The
  CFO initially resisted because the new artifact didn't produce a
  point forecast for the board pack; the resolution was to present a
  primary recommendation with branches for `manager-personality-quadrant`
  (sk14) Gods-quadrant audiences — the cascade is preserved beneath
  the recommendation framing.
