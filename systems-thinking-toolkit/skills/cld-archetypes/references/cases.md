# CLD Archetypes — Past Application Cases

Seven calibrating cases for `cld-archetypes`: three for the
limits-to-growth archetype (sk05 lineage) and four for the
variance/target/action balancing-loop template (sk06 lineage). Cases are
partitioned by archetype. Read both partitions before classifying a
diagram — diagnosis depends on telling deceleration (limits-to-growth)
apart from oscillation (V/T/A) and on knowing which intervention
philosophy applies on which side.

---

## Part A — Limits-to-Growth archetype (R+B coupling)

Three calibrating cases: one qualitative historical claim
(tea / disease / industrial revolution, c12), one quantitative
simulation confirmation (provincial car dealership, c24, Chapter 13),
and one counter-example showing the cost of *failing* to recognize a
binding constraint (Easter Island c11 + Caulerpa algae c04).

### Case A1 — Tea, disease, and the industrial revolution (c12)

- **Problem**: Pre-1750 England's population was roughly stable — high
  births balanced by high infant mortality (a B-loop on the death-rate
  side braking the births R-loop).
- **Methodology applied**: Sherwood reads the period as
  constraint-relief: tea displaced beer/water for daily drinking;
  boiling water for tea killed waterborne pathogens; infant mortality
  fell; the births R-loop, unchanged in structure, spun freely; labor
  surplus funded industrial take-off.
- **Conclusion**: The "cause" of the industrial revolution was not
  inventing the spinning jenny; it was relieving a previously-binding
  disease constraint that let the existing births R-loop accelerate.
- **Outcome**: Population doubled in ~80 years; urban labor pool
  enabled factory economy. (*See Boundary — Sherwood overreaches on
  single-cause attribution here; tea/sugar/gin-replacement/rising-real-
  wages all covary with disease decline. Use the rule, beware the
  temptation to identify THE single brake where multiple co-bind.*)

### Case A2 — Provincial car dealership growth simulation (c24, Chapter 13)

- **Problem**: Dealership owner wanted to grow sales faster, considered
  doubling reinvestment ratio of profits.
- **Methodology applied**: Sherwood built an ithink stock-and-flow
  model with the central R-loop (cars sold → profit → reinvestment →
  sales staff → cars sold) and a market-saturation B-loop on the
  addressable segment.
- **Conclusion**: At 100% reinvestment, sales plateau within 5 years
  because saturation binds; at 50% reinvestment, sales reach ~the same
  plateau but retained earnings doubled. Pedaling harder delivers
  near-identical revenue at twice the cash burn.
- **Outcome**: Owner kept the surplus; quantitatively confirmed the
  Ch 8 qualitative rule. The brake here is market saturation —
  relieving it requires geographic expansion or segment-broadening,
  not more sales staff. **This case is the quantitative spine of the
  limits-to-growth branch**: when a stakeholder doubts the qualitative
  diagnosis, the ithink simulation result is the receipt.

### Case A4 — Plugin Self-Analysis (v0.8 modern agent-orchestration case)

- **Problem**: systems-thinking-toolkit's own development trajectory.
  Solo developer (kouko) shipped 7 PRs in one day (v0.1.0 → v0.6.0);
  plugin mean evolved 105 → 109.67/A with per-PR delta sequence
  +3.4 → +1.0 → -0.5 → +0.5 → monotone-decreasing. Friction signals
  accumulated: parallel-subagent git index race; Sonnet 1M-context
  billing gate; Opus daily quota; audit subagent catching drift after
  each restructure with diminishing returns.
- **Methodology applied (Branch L)**:
  - L1 signature: deceleration toward asymptote confirmed (4 data
    points; per-cycle delta shrinking from +3.4 to +0.5)
  - L2 central R-loop (compressed from cld-craft Case 11 Mermaid):
    `Iteration Drive → PR Throughput → Iteration Cycle → Audit Catch
    → Plugin Coherence → Plugin Mean Score → Iteration Drive` (O-count
    = 2 → reinforcing; currently spinning virtuous but decelerating)
  - L3 candidate brakes: (a) Anthropic Quota; (b) Developer Cognitive
    Load; (c) Audit Diminishing Returns; (d) Coherence Saturation;
    (e) Score Ceiling at 120
  - L4 binding brake test ("if we doubled [input], would brake absorb
    the gain?"): binding = **Developer Cognitive Load** (kouko at
    attention ceiling within one day; cycle-boundary reset relieves it).
    Queued next: **Audit Diminishing Returns** (will bind once
    cognitive load is reset and PR count grows further).
  - L5 intervention: cycle-boundary cognitive reset + scope
    quantization per PR (≤ 1 archetype restructure per PR). Cost zero;
    timeline overnight; prediction: R-loop spins at +1.0 to +2.0 per
    cycle again post-reset, audit catch rate drops from 5+5 residual
    to ≤ 3 residual. Falsifiable: if next-session v0.5 PR mean delta
    < 0.5 AND audit residue ≥ 5, the binding brake was misidentified.
- **Conclusion**: limits-to-growth in agent-orchestration domain.
  Sherwood's Ch 8 master archetype transfers cleanly to multi-agent
  / human-in-the-loop systems despite the book pre-dating LLM
  agents by 22 years. The fuzzy variables (Cognitive Load, Internal
  Coherence) are agent-orchestration-specific elevations per Rule 7,
  but the limits-to-growth coupling structure is identical to
  industrial-revolution pattern (Case A1).
- **Outcome**: First documented self-application of cld-archetypes
  to plugin's own development. Cross-ref: dogfood audit at
  `docs/superpowers/audits/2026-05-13-systems-thinking-toolkit-dogfood.md`
  Test A. Companion: Case 11 in cld-craft/cases.md carries the
  CLD-construction layer; this case carries the archetype-application
  layer.
- **Calibration value**: fills Sherwood's pre-platform-economy /
  pre-2010 agent-orchestration blind spot. Pattern is recognizable
  in any sustained-iteration-with-human-attention setting (consulting
  engagements, research programs, open-source maintenance, indie-hacker
  product development).

### Case A3 — Easter Island (c11) and Caulerpa algae (c04) — failure to recognize constraint

- **Problem**: Easter Islanders' R-loop of population × statue-building
  ran into a hard B-loop on tree-stock (used for moving moai); they
  did not see the constraint; deforestation continued until collapse.
- **Methodology applied (retrospective)**: A limits-to-growth diagnosis
  in 1500 AD would have named tree-stock as the binding constraint and
  asked which moai-program changes (smaller statues, transport
  alternatives) could relieve it. Without the diagnosis, the islanders
  worked harder at the same R-loop until the brake bound absolutely.
- **Conclusion**: Civilization collapse — a counter-example showing the
  cost of treating an exponential-growth R-loop as boundless.
- **Outcome**: The Caulerpa "killer algae" Mediterranean spread (c04)
  is the same pattern in real time: small visible footprint hides
  exponential acceleration toward a hard limit; the moment when
  intervention is cheap is precisely the moment when the limit is
  invisible. **This case is the warning the limits-to-growth branch
  exists to prevent**: pedaling harder at a R-loop whose B-loop is
  silently approaching bind-point is the dominant failure mode in real
  business systems (it presents as "we just need a bigger push") and
  is best caught at the first sign of growth-rate deceleration, not
  at the bind-point.

---

## Part B — Variance/Target/Action template (single B-loop with delay)

Four calibrating cases: three Sherwood originals (hotel shower,
inventory manager, Bank of England MPC) and one V2 novel-domain
transfer (NPS playbook ping-pong). These encode the delay-vs-target
distinction, the "doing nothing was the right action" precedent, the
institutional small-moves-long-intervals exemplar, and the modern
customer-success analogue.

### Case B1 — Strange Hotel Shower (c08)

- **Problem**: Hotel shower has a long pipe; water adjustment takes
  ~10 seconds to reach the head. The guest turns it hotter, nothing
  happens, turns it hotter more, then suddenly scalding water arrives,
  turns it cold, eventually frozen water arrives.
- **Methodology applied**: The shower is a B-loop with delay. The
  target (comfortable temperature) is fixed, but the action (turn
  knob) feeds back to the actual (water temperature) with a 10-second
  lag. The guest reads variance before the prior action has worked
  through, so each correction overshoots.
- **Conclusion**: The mechanic is identical to corporate
  over-correction. The cure is the same — make a small adjustment,
  *wait one full cycle*, observe, then adjust.
- **Outcome**: Pedagogical anchor for every later B-loop case in the
  book. The hotel shower is the canonical visceral example of why
  acting faster than the loop converges amplifies, not damps,
  oscillation.

### Case B2 — Inventory Control Manager (c09)

- **Problem**: Inventory levels were self-stabilizing under the prior
  policy. A new manager, untrained in systems thinking, reset the
  target inventory level every month based on the previous month's
  variance. Inventory began oscillating with growing amplitude.
- **Methodology applied**: Sherwood diagnoses a moving-target B-loop.
  The system's natural response cycle was longer than monthly, so
  monthly retargeting added a forcing oscillation on top of the
  natural correction. The "fix" was making things worse.
- **Conclusion**: The intervention was to **stop moving the target**
  and let the existing loop converge. The destabilization was 100%
  endogenous — the system was already correct; the manager's
  well-meaning adjustments were the source of the problem.
- **Outcome**: Sherwood's flagship "doing nothing was the right action"
  case. This is the precedent to cite when the organization expects
  visible activity as proof of management; the case proves visible
  restraint can be the correct managerial output.

### Case B3 — Bank of England Monetary Policy Committee (c10)

- **Problem**: How to manage inflation, a metric with very long
  transmission lags from rate-change to price-effect (12-24 months).
- **Methodology applied (retrospective)**: The MPC's institutional
  discipline — meet monthly, change rates by 25bp at most, often do
  nothing for many months — is structurally exactly Sherwood's
  prescription: small moves, long intervals, allow each move to work
  through before the next. The MPC is engineered to resist the
  corporate over-correction reflex.
- **Conclusion**: Long-lag B-loops require institutional commitment to
  restraint that is hard for ad-hoc decision-makers to sustain. The
  MPC's structural arrangement (fixed cadence + bounded move size +
  multi-voter veto) operationalizes the discipline.
- **Outcome**: Held up by Sherwood as the institutional best-practice
  exemplar for managing any long-lag B-loop. *Caveat: period-dated.*
  The Sir Edward George MPC of 1997-2003 predates post-2008
  unconventional policy, post-2021 inflation regime change, and
  central-bank credibility crises. Use the *structural* lesson (small
  moves, long intervals) without inheriting the institutional
  confidence.

### Case B4 — NPS Playbook Ping-Pong (V2 novel-domain transfer)

- **Problem**: A customer-success org changes its onboarding playbook
  every quarter to fix swinging NPS. Each change makes swings wider.
- **Methodology applied**: NPS responds to onboarding cohort experience
  with ~6+ month lag from playbook change to NPS effect; quarterly
  playbook changes act faster than the loop can respond. Classic
  delay-induced amplification, identical to the hotel shower at
  organizational scale.
- **Conclusion**: "Do nothing for two quarters" first — let the loop
  converge. If action is genuinely needed, shorten the *detection* lag
  (run NPS on fresh cohorts at weeks 2, 4, 8) not the target.
  Attacking the lag is structurally legitimate; moving the target is
  not.
- **Outcome**: Demonstrates V/T/A transfers cleanly from 2002
  manufacturing/macro contexts to modern SaaS customer-success. The
  mechanic is the same; only the time-scale and the vocabulary
  changed. This is the case to cite when stakeholders argue "but
  that's old-economy stuff, our metric is different."

### Case B5 — Algorithm-Belief Pseudo-Target (v0.5 modern platform variant)

- **Problem**: A YouTube creator (or SEO marketer, or ad-spend manager)
  anchors behavior to a *belief* about a platform algorithm: "post 3
  videos a week or be punished," "keyword density 1-2% or you tank,"
  "always-on ads above CAC threshold." The belief functions like a
  B-loop target — drives action, takes precedence over direct outcome
  feedback — but the belief itself never updates from results.
- **Methodology applied**: The "target" is a **dangle**, not a node —
  it has no inbound causal arrow from the actual output metric. The
  creator's `Publishing Cadence` increases because of the belief, but
  `Views per Video` does not feed back into `Belief: 3 videos/wk
  required`. So what looks like target-seeking control (B-loop) is
  actually open-loop behavior (a chain into a dangle masquerading as a
  target). The literal O-count test may misfire: agents who assume
  "this is a B-loop because there's a target" will misclassify a
  non-feedback structure as feedback.
- **Diagnostic test**: Trace the alleged target backward. Is there ANY
  edge that updates the target value from observed system output? If
  no — it is a *pseudo-target dangle*, not a true B-loop set-point.
  The "loop" does not close.
- **Conclusion**: Pseudo-target dangles produce **monotone over-action**
  until something else breaks (the actor, the team, the cash). They
  look like B-loops but spin like R-loops because they have no
  corrective feedback. The intervention is NOT "do nothing" (V/T/A) or
  "relieve the brake" (limits-to-growth) — it is **question the
  belief**. Replace the dangle with a real target derived from
  observed output; OR explicitly downgrade the belief to "hypothesis
  under test" and add a learning loop that updates it.
- **Outcome**: Adds a third archetype-adjacent pattern to the Branch L
  / Branch V split. Common in: platform-algorithm folklore (YouTube
  cadence, TikTok hooks, Instagram reels-vs-photo), SEO best-practice
  myths (keyword density, backlink count), conversion-rate
  over-spending (LTV:CAC pseudo-targets that never recalibrate against
  actual cohort behavior). The pattern is **NOT in Sherwood 2002** —
  it is a 2010s+ platform-economy variant. Worth naming because the
  algorithm-folklore version is now extremely common.
- **Hand-off**: After identifying as pseudo-target dangle, the
  appropriate downstream is NOT cld-archetypes intervention but a
  question: "Is the belief verifiable? What evidence would falsify
  it?" If verifiable but never tested, add an observation cadence. If
  unverifiable, treat as a constraint on the actor's psychology
  (sociological problem, not systems problem).
- **Provenance**: surfaced from v0.4 Chinese-input dogfood (PR #274,
  2026-05-13) when subagent diagnosed a YouTube creator's `BeliefTarget
  (3 videos/wk)` as a non-updating dangle masquerading as a B-loop
  set-point. See `docs/superpowers/audits/2026-05-13-systems-thinking-toolkit-dogfood.md`
  appendix.
