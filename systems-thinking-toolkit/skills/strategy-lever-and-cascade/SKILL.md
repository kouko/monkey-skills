---
name: strategy-lever-and-cascade
description: |
  Turn ambition statements ("achieve 25% margin", "double ARR by 2030",
  "5-year plan refresh") into a mechanically actionable strategy
  artifact: a list of lever target changes (controllable inputs) that
  reverse-engineer across plausible-not-probable futures. Forces three
  disciplines stacked into one workflow — (1) separate levers from
  outcomes (managers move levers, outcomes emerge), (2) diagnose the
  three-timescale cascade (in-year fix / annual budget / multi-year
  ambition) and identify which loop is dead, (3) build the 3×N
  scenario × lever table and classify each lever as robust /
  scenario-contingent / bet. NOT for tactical or operational decisions
  (use variance-target-action-template at single-loop V/T/A level), NOT
  for vision/mission statements (ambition is genre-appropriate there),
  NOT during crisis-mode firefighting. Triggers: "we will achieve X%",
  "our goal is [outcome]", "set the KPIs", "drive [outcome]", "5-year
  plan", "strategic refresh", "scenario planning", "what if [future]?",
  "long-term vision", "robust strategy", "ambition vs plan". KEYWORDS:
  strategy, OKR critique, levers, outcomes, KPI design, scenario
  planning, 3×N table, plausible-not-probable, target dangle, strategic
  cascade, dead 5-year plan, reverse-engineer levers, robust /
  contingent / bet. JA: 戦略=レバー目標値の再設定・シナリオプランニング・三段カスケード・打ち手vs結果。zh-TW: 策略＝重設槓桿目標值・情境規劃・三層串接・操控變數vs結果指標。
source_book: Seeing the Forest for the Trees — Dennis Sherwood
source_chapter: "Chapter 10 (lever-vs-outcome business engine + three-timescale cascade + 3×N scenario table); Chapter 12 (stocks-as-objectives reformulation); Chapter 13 (car-dealership lever simulation + ambition-as-target-dangle vs forecast)"
source_language: en
tags: [strategy, levers-outcomes, okr-critique, scenario-planning, long-term-planning, systems-thinking]
related_skills:
  - slug: variance-target-action-template
    relation: depends-on
  - slug: innovaction-martian-test
    relation: composes-with
  - slug: manager-personality-quadrant
    relation: composes-with
---

# Strategy = Lever Target Changes, Reverse-Engineered Across the Three-Timescale Cascade

## R — Reading

> "Managers do not directly affect outcomes; they operate levers.
> Strategy is the act of resetting the target settings of those levers."
>
> — Dennis Sherwood, Chapter 10

> "Strategy is itself a balancing loop, with ambition as the input
> target dangle… plausible alternative futures are not probable; they
> exist to test our levers, not to predict the world."
>
> — Dennis Sherwood, Chapter 10

## I — Interpretation

Sherwood stacks two ideas into one workflow. Together they take an
ambition statement and produce a mechanically actionable artifact.

**Idea 1 — Levers vs Outcomes (the reframe).** A **lever** is a variable
a manager can directly move: price, headcount, ad spend, training
hours, payment terms, opening hours, product features. Every lever has
three attributes — name, current actual setting, current target
setting — and sits inside a balancing loop that drives actual toward
target (the V/T/A template; see `variance-target-action-template` (sk06)).
An **outcome** is a result: market share, customer satisfaction,
revenue growth, gross margin, share price. No manager moves these
directly; they emerge downstream from many levers operating through
the business engine. The diagnostic test: **if a name appears on both
your levers list and your outcomes list, one is misclassified.**
"Revenue" cannot be both. Strategy proper is **the act of resetting
lever target settings** — not the act of declaring an outcome target.
"Achieve 25% margin" without specifying which price points, COGS
targets, headcount ratios, or mix shifts produce that margin is a
wish; it leaves all the B-loops at their current settings and changes
nothing mechanically.

**Idea 2 — The Three-Timescale Cascade (the expansion).** Most
organizations run three nested management-control loops at three
different cadences:

1. **In-year fix loop** (weeks-to-months): operational corrections to
   keep current-year actual on current-year target — V/T/A at quarterly
   cadence.
2. **Annual budgeting loop** (one year): sets next year's lever target
   settings based on this year's variance against ambition.
3. **Strategic / multi-year loop** (3-10 years): sets the *ambition*
   itself — the input target dangle for the annual loop. Driven by the
   strategic gap between current trajectory and ambition.

A plan whose numbers are last year's numbers shifted forward by 12
months is the signature of a **dead strategic loop**: the in-year and
annual loops are running, but the strategic loop has no
ambition-perturbing input; the cascade has collapsed to two levels.

**Scenario planning** is the engine for the strategic loop. Sherwood's
specific version (after Pierre Wack / Shell) has three discriminators:

- Scenarios are **plausible, not probable** — no probability weights,
  no expected-value math. Treating scenarios as probability-weighted
  reduces them to a single forecast in disguise.
- Scenarios exist to **test lever settings**, not to predict the
  world. The question is "if this world arrived, would our current
  lever settings produce acceptable outcomes?"
- For each scenario where the answer is no, **reverse-engineer** the
  required lever settings. The 3×N table is the operational form: 3
  (or more) scenarios as columns × N levers as rows. Each cell is the
  lever-target-setting that would produce acceptable outcomes in that
  scenario. Patterns across each row classify the lever as
  **robust** (same setting works in all scenarios → set now),
  **scenario-contingent** (different settings → build optionality,
  define triggers), or **bet** (one scenario's setting is high-upside,
  others acceptable → conscious bet with downside protection).

**The synthesis.** The reframe says *what* a strategy artifact is (a
list of lever target changes, not an outcome announcement). The
cascade says *across what time horizon and uncertainty range* to
choose those changes. Together they make ambition a target dangle
that the system aims at, not a forecast the spreadsheet predicts —
the distinction Sherwood (Ch 13) insists on and that most strategic-
planning processes silently violate.

## A1 — Past Application

Five cases calibrate the workflow — three from `lever-vs-outcome-reframing`
(sk07) at decision and document level (TV "talent problem" c15,
outsourcing-as-bundle-error Ch 9/10, car-dealership lever simulation
c24); two from `strategic-cascade-scenario-planning` (sk08) at
multi-year level (car-dealership scenario reverse-engineering c24, the
dead-5-year-plan diagnosis pattern from Ch 10). They are detailed in
`references/cases.md`.

**MANDATORY — READ ENTIRE FILE**: Before applying lever-vs-outcome
reframing or running the 3×N table, you MUST read
[`references/cases.md`](references/cases.md) (~110 lines) for the
outcome-as-misclassified-lever pattern, the scenario-reverse-
engineering worked example, and the dead-strategic-loop diagnostic.

## A2 — Future Trigger ★

### When will the user need this skill?

1. Reviewing a strategic plan or OKR document and noticing all the
   metrics are outcomes with no corresponding lever changes.
2. CEO announces an ambition ("25% margin by 2027" / "double ARR") and
   the team is cynical — diagnose the missing lever-target changes.
3. Designing OKRs and want to test whether the "Key Results" are
   levers (controllable) or outcomes (results).
4. Coaching a manager who keeps trying to "improve [outcome]"
   directly without identifying which input she controls.
5. Auditing a project charter: which lever settings does this project
   actually change?
6. The board asks for a 5-year strategy refresh and the current plan
   is last year's plan with the dates shifted (dead strategic loop).
7. Designing a strategy workshop and want a structure beyond SWOT or
   Porter's Five Forces.
8. Major capital allocation decision with multi-year payback
   uncertainty (build vs buy, new geography, new product line).
9. Auditing whether the current strategy is robust to scenarios that
   already feel likely (regulatory change, new entrant, AI capability
   shift).
10. Coaching a leader who confuses ambition statements with forecast
    outputs.

### Language signals

- "achieve [outcome] by [date]"
- "our goal is [a result]"
- "we will [outcome verb] [X%]" with no input plan
- "set the KPIs" / "set the targets" / "drive [outcome]"
- "we need to improve [outcome]"
- "the strategy is [an ambition]"
- "5-year plan" / "long-term strategy" / "strategic refresh"
- "scenario planning" / "what if [future condition]?"
- "where will we be in 2030?" / "long-term vision"
- "robust strategy" / "resilience" / "ambition vs plan"

### Distinction from neighboring skills

- vs. `variance-target-action-template` (sk06): V/T/A operates *within*
  a single lever's balancing loop at quarterly cadence. This skill
  operates *above* the loops (which levers' target settings to change)
  and *across* the cascade (which time horizon, which scenario set).
  V/T/A is the prerequisite primitive; this skill is its strategy-
  level rename and multi-year extension.
- vs. `limits-to-growth-take-the-brakes-off`: limits-to-growth
  diagnoses *the current* binding constraint; this skill insists you
  name lever changes at all rather than outcome targets, and asks
  *which constraints might bind across multiple futures*.
- vs. classical forecasting (single curve + confidence interval):
  Sherwood explicitly bans probability-weighted scenarios; classical
  forecasting reduces uncertainty to a number, this skill preserves it
  as plural worlds with reverse-engineered levers per world.
- vs. OKR / BSC / Porter's Five Forces: those operate at the outcome
  level. This skill is corrective — it sits *upstream* of any of them
  and forces lever discipline before adopting their outcome
  vocabulary.
- vs. Shell / Wack scenario planning: same lineage; Sherwood adds the
  explicit structural framing (strategy = B-loop nested above annual
  budget = B-loop nested above in-year fix) and the 3×N reverse-
  engineering operationalization.
- vs. `innovaction-martian-test` (sk13): the perturbation method is
  Sherwood's recommended generator for the "N plausible alternative
  futures" axis. This skill composes with it — sk13 produces the
  scenario column headers, this skill fills the cells with required
  lever settings.
- vs. `manager-personality-quadrant` (sk14): Sherwood pairs the
  cascade with a 2×2 of executive personality to predict audience
  reception. Compose for presentation, not analysis.

## E — Execution

```
E flow:
  ambition / OKR / plan on the table?  ── no → exit (not a strategy task)
        │ yes
        v
  separate levers from outcomes (two columns; CEO-tomorrow-morning test)
        │
        v
  any name on BOTH lists? ── yes → resolve before proceeding
        │ no
        v
  for each lever: name current actual + current target + proposed target
        │
        v
  diagnose cascade state (in-year / annual / strategic loops alive?)
        │
        ├── strategic alive → annual lever-target reset only
        └── strategic dead → run scenario planning (next steps)
                │
                v
        generate 3-4 plausible-NOT-probable scenarios (Martian perturbation)
                │
                v
        build 3×N table: levers × scenarios; fill each cell with required setting
                │
                v
        classify each lever row: robust / scenario-contingent / bet
                │
                v
        adapt presentation for audience (quadrant framing)
```

When this skill activates, follow these steps:

1. **Make two columns — Levers and Outcomes.** Sort every named
   variable in the current plan / OKR / charter into one column. The
   discriminator: **the "could the CEO move this directly tomorrow
   morning?" test** — yes = lever, no = outcome.
   - Completion criterion: every "objective," "goal," "KPI," "metric,"
     "result," and "target" appears in exactly one column.
   - Halt condition: if a name appears on both lists, one is
     misclassified; resolve before proceeding.

2. **For each lever, name three attributes.** (a) current actual
   setting, (b) current target setting, (c) proposed new target
   setting. If the proposed new target equals the current target, this
   lever is not part of the strategy — strike it.
   - Completion criterion: every lever has all three settings written
     down; levers with no proposed change are removed from the
     strategy artifact (they may still appear in operations).

3. **For each outcome, write the mechanism in one sentence.** State
   which lever-target changes plus which fuzzy growth-driver link
   produce it. If you cannot write the mechanism, the outcome is not
   yet operational.
   - Completion criterion: every outcome has a one-sentence mechanism
     traceable to ≥1 lever change. Outcomes without mechanism are
     ambition statements, not strategy — move them to a vision/mission
     section.

4. **Diagnose cascade state.** Confirm the in-year fix loop and annual
   budget loop are running. Then ask: is the multi-year ambition being
   perturbed by anything other than last year's variance? A 5-year
   plan whose numbers are last year's numbers extrapolated, with no
   scenario alternatives considered, is the dead-strategic-loop
   signature.
   - Completion criterion: cascade state is declared (alive / dead /
     two-of-three running). If strategic loop is alive and stable,
     skip to step 9; if dead or facing meaningful environmental shift,
     proceed to step 5.

5. **Generate 3-4 plausible (NOT probable) scenarios.** Each scenario
   is a one-paragraph description of a feature-perturbed future,
   passing the Martian test (`innovaction-martian-test` (sk13)) for
   completeness. Span the *plausible* range. **Probability assignment
   is forbidden — if you feel the urge, you've collapsed back to
   forecasting.**
   - Completion criterion: 3-4 scenario paragraphs exist; no
     probability weights anywhere on the page.
   - Halt condition: if you cannot generate distinct futures (all
     scenarios look like today + ε), you are inheriting the existing
     plan — perturb harder via sk13.

6. **Build the 3×N table.** Rows are levers from step 2 (or candidate
   lever changes); columns are scenarios from step 5. Each cell is
   the lever-target-setting that would produce acceptable outcomes in
   that scenario. Empty cells mean "I haven't done the work."
   - Completion criterion: zero empty cells in the matrix; each cell
     contains a specific setting (number, range, or named state), not
     a hedge.

7. **Classify each lever's pattern across its row.** Each lever is
   one of: (a) **robust** (same setting works in all scenarios → set
   now); (b) **scenario-contingent** (different settings across
   scenarios → build optionality now, set later, define triggers);
   (c) **bet** (one scenario's setting is high-upside, others
   acceptable → conscious bet with named downside protection).
   - Completion criterion: every lever row carries one of the three
     labels; bets are explicitly named as bets with their downside
     protection.

8. **Convert the classified table into the strategy artifact.** A
   list of lever target changes (robust levers set now), a list of
   optionality investments (scenario-contingent levers with trigger
   monitoring), and a list of conscious bets with downside-protection
   plans. This list IS the strategy artifact; no spreadsheet forecast
   of outcomes is required or appropriate.
   - Completion criterion: the document reads "we propose to change
     the target settings of lever X from A to B, lever Y from C to D
     (contingent on trigger T), and lever Z from E to F (bet,
     downside-protected by P); the predicted downstream outcomes are
     P, Q, R."

9. **Adapt presentation to audience quadrant.** For
   `manager-personality-quadrant` (sk14) Gods-quadrant audiences (CEO
   who believes she can predict + controller), reframe output as
   *primary recommendation + branches* (the cascade is preserved
   beneath the recommendation framing); for Guides-quadrant audiences
   (accept-unknowability + empowerer), present plural futures
   directly. *See Boundary on sk14's evidence-light status.*
   - Completion criterion: presentation form chosen and explicit
     about which framing it uses; the underlying 3×N table is
     attached as backup in either case.

## B — Boundary ★

### Do NOT use this skill when:

- **The team is in operational firefighting, not strategy.** A
  production-down incident or building-on-fire crisis is not the
  moment to debate lever-vs-outcome semantics or run a scenario
  workshop. Use `variance-target-action-template` (sk06) or
  limits-to-growth first; scenario-plan after stabilization.
- **Tactical / single-year operational decisions.** This year's
  pricing adjustment doesn't need a 3×N table — use V/T/A at
  quarterly cadence.
- **The lever set is genuinely unknown** (early-stage / exploratory /
  pre-product-market-fit). Forcing the column structure prematurely
  produces false precision. Run a discovery cycle first; revisit
  this skill once you know what your levers are.
- **Compensation conversations.** Comp programs require outcome-
  linked metrics for legal and motivational reasons; lever-only
  metrics often game poorly. This skill is upstream of compensation
  design, not a replacement for it.
- **Vision / mission statements.** A vision is *supposed* to be an
  outcome ambition; demanding lever-decomposition of "be the most
  trusted brand in our category" misunderstands the genre. The skill
  applies once vision descends into strategy.
- **Plan-quality is good and stable.** Don't refresh a working
  strategic loop just to exercise the skill. The trigger is a dead
  loop or a meaningful environmental shift.

### Author-warned failure modes (Sherwood's counter-examples)

- **ce17 — Announcing an outcome target without resetting any lever
  target settings.** The B-loop machinery for each lever is not
  triggered (no variance signal because no target moved); no change
  program activates; the team is correctly cynical. The most common
  form of "fake strategy."
- **ce18 — Treating scenarios as probability-weighted forecasts.** The
  instant a workshop asks "what's the probability of Scenario A?" the
  exercise has degenerated into forecasting. Probabilities collapse
  the plural-futures discipline to a single expected-value curve,
  which is exactly what scenario planning is meant to escape.
- **Lever-target-change confused with steady-state benefit.** A change
  program produces transient disruption (training cost, mix shift,
  customer attrition during transition) that looks like the strategy
  isn't working. Predict the transient and budget for it; otherwise
  the change gets reversed before the new lever setting reaches
  steady state. The transient is often longer than modern OKR cycles
  allow.
- **Over-investment in scenario workshops at expense of execution.**
  Strategy is the *list of lever target changes*, not the workshop
  experience. Workshops that produce beautiful 80-page books with no
  lever decisions have done the analysis half and skipped the
  commitment half. The 3×N table is the commitment device — empty
  cells mean unfinished work, not "scenario-dependent."

### Author's blind spots / period limitations

- **"No manager directly affects any outcome" is partially circular.**
  Sufficiently downstream outcomes are by definition indirect; a
  salesperson closing a deal directly causes a sale. Use the
  lever/outcome distinction pragmatically — "more steps between you
  and it ↔ more like an outcome" — rather than as a hard binary.
- **Treating ambition as forecast.** Sherwood (Ch 10, Ch 13) warns
  that ambition is an *input target dangle*, not a *forecast output*.
  Strategies routinely confuse the two and use ambition to size
  capacity; keep the distinction even after applying this skill.
- **Manager-as-protagonist framing.** The procedure assumes the user
  has authority to reset lever targets and authorize the chosen
  changes. Where levers are owned by other functions / orgs /
  regulators, "reset the target" becomes "negotiate a target change
  with N parties" — a different game. The 3×N table becomes the
  *input* to a political process Sherwood doesn't model.
- **The Gods/Gamblers/Grinders/Guides 2×2 is evidence-light.** The
  quadrant is Sherwood's coinage with single-chapter application —
  cousin to Myers-Briggs / Hersey-Blanchard, which have weak
  predictive validity in modern research. Useful as a facilitator
  heuristic, not as a personality classification claim. See
  `manager-personality-quadrant` (sk14) Boundary for caveats; treat
  step 9 framing as audience-adaptation, not personality typing.
- **Strategic loop running on "ambition" is partially circular.**
  Sherwood positions ambition as a target dangle, but its origin is
  left outside the model. In real organizations, ambition comes from
  founder beliefs / investor pressure / industry comparison —
  political, not analytical. The skill is scaffolding; it doesn't
  explain where the dangle's value comes from.
- **Pre-platform-economy / pre-AI / pre-2008 framing.** The 2002
  examples (classical lever set: price, ad spend, headcount; Shell-
  pattern oil scenarios) under-represent network-effect levers
  (matching quality, supply-side onboarding, trust mechanisms), AI
  capability jumps, and systemic financial contagion. Generate
  scenarios appropriate to 2026; update the lever taxonomy for the
  business model.
- **Consultant-rescue narrative arc.** The book's scenario-planning
  success stories follow "workshop → diagram → lightbulb → adoption."
  Real engagements often produce excellent 3×N tables that are then
  shelved. The skill doesn't include adoption mechanics — pair with
  political-process tooling.

### Easily-confused neighboring methodologies

- **OKRs (Doerr / Grove).** Objectives are outcomes; Key Results are
  *supposed* to be levers but in practice are often outcomes one step
  down. This skill is a useful audit tool for OKRs — separate the two
  columns and check whether KRs are actually controllable.
- **Balanced Scorecard (Kaplan & Norton).** BSC's cascade is similar
  in spirit but accepts metrics at any level. Sherwood is stricter:
  the strategy artifact must be lever changes, not metric targets.
- **Porter's Five Forces / value-chain analysis.** Outcome-level
  framing; useful for positioning, not for action. Compose with
  Sherwood: Porter tells you what *kind* of advantage to seek;
  Sherwood tells you which lever target settings change to get it.
- **Traditional forecasting (single curve + confidence interval).** If
  your audience or culture demands a point forecast, you are not
  doing scenario planning — you are doing forecasting in scenario
  clothes.
- **Shell / Pierre Wack scenario planning** (1970s-onward): same
  intellectual lineage. Sherwood's contribution is the explicit
  structural framing (strategy as B-loop) and the 3×N reverse-
  engineering operationalization.
- **Real-options analysis (finance).** Quantitatively values
  optionality across futures using probability distributions over
  payoffs. Complementary to Sherwood: real-options can price the
  optionality investments that scenario-contingent levers identify,
  *if* you accept the probability assumptions.
- **Wargaming / red-teaming.** Scenario planning's adversarial cousin.
  Wargaming asks "what does an opponent do across scenarios?";
  Sherwood asks "what do *we* do?". Compose for competitive
  industries.

## Related skills

- **depends-on `variance-target-action-template`** — the lever-vs-outcome
  reframe presupposes the V/T/A balancing-loop structure: every lever
  has a name, an actual, and a target, connected to outcomes through
  a B-loop. The three-timescale cascade is three nested V/T/A loops
  at different cadences. Without sk06, "lever" degenerates into
  "thing we want to be true."
- **composes-with `innovaction-martian-test`** — sk13's perturbation
  method is Sherwood's recommended generator for the "N plausible
  alternative futures" axis of the 3×N table; reach for it whenever
  the team is producing trivial variants of today's world.
- **composes-with `manager-personality-quadrant`** — Sherwood claims
  Guides-quadrant audiences find the cascade most natural while Gods-
  quadrant audiences reject it as uncertainty-foregrounding. Use sk14
  to anticipate audience reception and adapt presentation in step 9
  (decisive recommendation framing for Gods, plural-futures framing
  for Guides). See sk14 Boundary for evidence-light caveats.

## Audit metadata

> Source-unit codes (f12/f13/f14/f15/p16/p17/p23/p36/ce17/ce18/c24/g16/g28/g29/g31/g32/g40/g41/g44/g45) refer to Stage-1.5 verified.md entries. See `<plugin-root>/references/VERIFIED.md`.

- **Verification status**: V1 ✓ (7 contexts spanning generic business engine, strategy definition, stock-flow reformulation, simulation, three-timescale cascade, scenario planning, audience adaptation) / V2 ✓ (novel "25% margin announcement" cynicism diagnosis + dead-5-year-plan diagnosis) / V3 ✓ (cuts through strategy-framework proliferation; probability-ban + structural B-loop framing is Sherwood-distinctive beyond Shell/Wack)
- **Source units merged**: f12, f13, f14, f15, p16, p17, p23, p36, ce17, ce18, c24, g16, g28, g29, g31, g32, g40, g41, g44, g45
- **Distilled at**: 2026-05-11
- **Merged at**: 2026-05-12 (Profile B merge: sk07 lever-vs-outcome-reframing + sk08 strategic-cascade-scenario-planning)
- **Output language**: body — English; metadata — English
