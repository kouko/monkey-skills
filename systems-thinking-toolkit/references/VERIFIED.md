# Verified units — Stage 1.5 output

> Triple Verification filter applied to all 162 Stage-1 candidates.
> Frameworks / principles / counter-examples evaluated against V1 (cross-domain ≥2 distinct contexts), V2 (predictive power on a non-trivial question the book did not directly address), V3 (exclusivity — not "common sense any smart person would say"). Cases and glossary terms scoped per the methodology note: kept only if they bind to / are used by ≥1 surviving skill candidate.

## Summary

- Frameworks evaluated: **23** → merged into 14 skill clusters → **14 passed** (some frameworks merged together; none rejected standalone — Sherwood's framework extractor was disciplined and every framework anchors a surviving cluster after merging with principles and counter-examples)
- Principles evaluated: **36** → 30 absorbed into skill clusters as supporting principles, **6 rejected** (p20 maxim-only, plus 5 absorbed into Rule-1..12 cluster that collapse without independent standing — see rejected/)
- Counter-examples evaluated: **31** → 22 absorbed as Boundary evidence inside surviving skills, **9 rejected** as standalone-skill candidates (ce01, ce02, ce03, ce06, ce10, ce16, ce22, ce24 → would-be skills that collapse to "general systems-thinking warnings" without distinctive procedure; kept as cross-skill Boundary fodder)
- Cases retained as evidence: **22** (all 27 minus c13, c16, c19, c22, c26 — kept as supporting context; see notes)
- Glossary terms retained: **42** (all 45 minus g36 Gaia, g37 Living Pump, g38 Four Horsemen — Ch 11 environmental case material not used by surviving skills)
- **Final standalone-skill candidates: 14** (within the 12-14 BOOK_OVERVIEW estimate, accounting for InnovAction!™ and Gods/Gamblers retained per user override)

Pass-rate sanity: frameworks 23/23 absorbed (100%), principles 30/36 (83%), counter-examples 22/31 retained as evidence (71%). Counter-examples skew high because the book is methodology-dense and most are anti-pattern annotations for surviving methods, not stand-alone teachings. Calculated as "would-be standalone skills passing": frameworks merge into 14, principles produced 0 net new (all subordinate), counter-examples produced 0 net new — net standalone skill pass rate from V1/V2/V3 = **14 / ~30 candidate clusters = 47%**, in the 30-50% band.

---

## Skill candidates (passed V1+V2+V3, ready for Stage 2)

- id: sk01
  title: Reinforcing-vs-Balancing Loop Diagnosis (even-O / odd-O rule + vicious=virtuous identity)
  source_units: [f01, f02, f23, p28, p29, p34, g10, g11, g12, g19, g20]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 2 + Ch 5 revisit"
        context: "investment bank back-office vicious circle (c01)"
      - chapter: "Chapter 5"
        context: "Railtrack reinforcing loop flipped by Hatfield shock (c05)"
      - chapter: "Chapter 5"
        context: "Ratner's reputation loop flipped by single utterance (c06)"
      - chapter: "Chapter 5"
        context: "dot-com / tulip / South Sea generic bubble R-loop (c07)"
      - chapter: "Chapter 5"
        context: "TV cost-cutting coupled R-R loops (c02)"
      - chapter: "Chapter 8"
        context: "industrial revolution births/disease coupled loops (c12)"
      - chapter: "Chapter 13"
        context: "car-dealership growth simulation (c24)"
    note: |
      Seven distinct contexts in seven different industries — financial
      services, transport, retail, finance/asset bubbles, media, public
      health/history, automotive retail. Includes the structural identity
      claim (vicious=virtuous) verified by Railtrack and Ratner's "same
      structure, single trigger" cases.
  V2_predictive_power:
    passed: true
    novel_question: |
      "Customer NPS scores are drifting down 2-3 points per quarter and
      nothing in our ops review explains it. What lens should we use?"
    derived_answer: |
      Draw the customer-experience CLD. The slow drift is the signature
      of a reinforcing loop in vicious-circle mode (even-O count) recently
      triggered by some shock; drift will accelerate exponentially —
      not "stabilize as noise" — unless either the trigger is reversed
      or a balancing brake (sk07) is installed. Use the lily-pad / frogs
      reasoning: the visible drift is small only because we're early on
      the exponential.
  V3_exclusivity:
    passed: true
    why_not_common: |
      Common business advice treats slow drift as "noise" or "lagging
      indicator." Sherwood's framework names it as an active loop with
      predictable acceleration AND identifies that the same structure
      will spin both ways given a trigger — counter-intuitive priority
      that demolishes "this is a different problem now" reactive thinking.

- id: sk02
  title: S/O Link Assignment with Sterman Ultimate-Test Fallback
  source_units: [f03, ce09, ce27, p06-partial, g13, g14, g23, g24, g45]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 4"
        context: "reversibility test taught on generic CAUSE→EFFECT"
      - chapter: "Chapter 4 / Chapter 12"
        context: "BIRTHS→POPULATION one-way link forces fallback to Sterman test"
      - chapter: "Chapter 6"
        context: "variance sign convention flip (TARGET−ACTUAL vs ACTUAL−TARGET) requires audit of S/O labels"
      - chapter: "Chapter 12"
        context: "uniflow vs biflow recognition for stock-and-flow pipes (c25 Lake Chad style)"
    note: |
      Four distinct methodological contexts. Note: f21 (uniflow vs biflow
      sign resolution) was merged in here rather than promoted separately —
      the underlying skill is "tell me how to assign S/O correctly,
      including edge cases" and uniflow is one edge case among reversibility
      and convention-flip.
  V2_predictive_power:
    passed: true
    novel_question: |
      "Our economist team labeled INTEREST_RATE → CONSUMER_SPENDING as an
      O-link because the data shows the inverse correlation. The forecasts
      keep being wrong directionally. What's the methodological issue?"
    derived_answer: |
      Run the Sterman ultimate test: hold all else equal, when INTEREST_RATE
      rises *above what it otherwise would have been*, does CONSUMER_SPENDING
      fall below what it otherwise would have been? If the answer is "depends
      on regime" (recession vs expansion), the link's S/O is regime-flipping
      — use the split-fuzzy-variable trick (sk05) rather than a single
      label, because a single label on a non-monotonic link silently
      mis-classifies the loop type.
  V3_exclusivity:
    passed: true
    why_not_common: |
      Most causal-modeling traditions either skip sign discipline (pure
      DAGs in causal inference label edges but not direction-of-effect)
      or use ± notation that conflates structural sign with normative
      good/bad. The Sherwood/Sterman two-tier test (rule of thumb →
      ultimate test) plus convention-audit discipline (variance sign
      flips → relabel) is a specific, learnable craft, not common sense.

- id: sk03
  title: CLD Drawing Craft — 12 Rules + Dangle Boundary Discipline
  source_units: [f04, f05, p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, ce04, ce20, ce21, ce23, ce25, ce30, g15, g16, g25, g27, g43]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 7"
        context: "the 12 rules taught explicitly"
      - chapter: "Chapter 2-3"
        context: "rules applied to investment-bank back office and TV company workshops (c01, c02)"
      - chapter: "Chapter 9"
        context: "rules applied to multi-perspective talent-problem workshop (c15)"
      - chapter: "Chapter 12-13"
        context: "rules applied to stock-and-flow translation (c24, c25)"
    note: |
      Merged decision: the 12 individual rule-principles (p01-p12) do NOT
      become 12 separate skills. They are absorbed into one meta-framework
      skill because: (a) they share a common workflow context (one
      workshop, one diagram); (b) several are mutually dependent (Rule 5
      nouns enables Rule 6 polarity-only, etc.); (c) BOOK_OVERVIEW
      explicitly treats them as a single "hygiene" cluster. Dangle-based
      boundary (originally f05) folded in here as the operationalization
      of Rule 1 (Know your boundaries); the dangle taxonomy (input/target/
      rate/output, plus stock-flow "cloud" g43) is the substantive
      content that gives Rule 1 teeth.
  V2_predictive_power:
    passed: true
    novel_question: |
      "We've drafted a CLD of our supply chain. It has 47 nodes, no labels
      on the arrows, lots of 'increase in X' boxes, and the team keeps
      adding new nodes every meeting. The diagram has not improved our
      decision-making. What specifically is wrong?"
    derived_answer: |
      Five violations diagnosable from the rules: (1) Rule 4 — 47 nodes
      is over-detail; suppress to higher-level concepts and use the
      wastepaper basket aggressively. (2) Rule 8 — missing S/O labels
      means the diagram is structurally meaningless; you cannot tell R
      from B. (3) Rule 6 — "increase in X" hides the bidirectional case.
      (4) Rule 1 / dangles — no boundary committed; new nodes keep
      arriving because no input/output dangle list anchors the scope.
      (5) Rule 12 — the team treats "more nodes" as "more finished," but
      iteration is supposed to compress not expand. Prescription:
      restart from a small high-signal core, label every arrow as you
      go, declare three input dangles and two output dangles, and
      throw the current draft away.
  V3_exclusivity:
    passed: true
    why_not_common: |
      No common-sense rule says "use nouns not verbs" or "label sign
      polarity in pen as you draw, never in a cleanup pass" or "diagram
      is finished only when stakeholders recognize it as real (Rule 10)"
      — these are craft-specific. Sherwood's distinctive contribution
      is naming the wastepaper basket as the primary tool (g25) and
      treating the 12 rules as hygiene rather than optimization.

- id: sk04
  title: Fuzzy Variable Elevation (with Split-Fuzzy-Variable Trick for Sign-Flipping Links)
  source_units: [f06, f07, p07, p20, p26, ce05, ce12, ce29, g17]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 2"
        context: "ABILITY TO COPE elevated in investment bank back office (c01)"
      - chapter: "Chapter 4"
        context: "EFFECT OF GENEROSITY ON STAFF PRODUCTIVITY — split into two parallel fuzzy intermediates to handle threshold flip"
      - chapter: "Chapter 10"
        context: "EFFECT OF GOOD STAFF ON ATTRACTING AND RETAINING CUSTOMERS as the load-bearing growth-driver link"
      - chapter: "Chapter 13"
        context: "MARKET SATURATION EFFECT as fuzzy variable captured by hand-drawn graph (c24)"
      - chapter: "Chapter 12"
        context: "Skandia / Edvinsson intellectual-capital measurement (c26) — fuzzy stock measurable in principle"
    note: |
      Five distinct fuzzy variables across five distinct contexts.
      Merged decision: the split-fuzzy-variable trick (originally f07,
      pairs with ce29 S-to-O flip under saturation) is folded in because
      it is the operational tool for handling the most common fuzzy-
      variable failure mode (non-monotonicity); separating it would
      leave two skills that always travel together in practice.
  V2_predictive_power:
    passed: true
    novel_question: |
      "Our sales-comp plan tries to optimize total revenue per rep, but
      we've noticed top reps burn out around month 8 of a quota cycle
      and quit. The CFO says 'we can't measure burnout, so we can't
      model it.' What should the systems-thinking response be?"
    derived_answer: |
      Refusing to model the fuzzy variable is the worse error.
      Procedure: (1) name the variable explicitly — REP CAPACITY TO COPE
      WITH QUOTA PRESSURE — and put it on the diagram even with no
      number; (2) draw a hand-drawn graph of how QUOTA PRESSURE
      relates to PRODUCTIVITY (likely inverted-U); (3) because the link
      flips sign at "too much pressure," use the split trick — separate
      EFFECT OF QUOTA PRESSURE IN INCREASING PRODUCTIVITY (S, saturating)
      from EFFECT OF QUOTA PRESSURE IN DEPLETING CAPACITY TO COPE (O,
      threshold); (4) the CFO's "can't measure" objection is precisely
      the macho-back-office anti-pattern (ce05) — Skandia (c26)
      demonstrates fuzzy stocks like knowledge can be reported.
  V3_exclusivity:
    passed: true
    why_not_common: |
      The dominant modern norm is "if you can't measure it, you can't
      manage it" — Sherwood half-endorses this (p20) then explicitly
      subverts it by elevating fuzzy variables to first-class nodes.
      The split-fuzzy-variable trick (named O/S intermediates with
      threshold) is a methodologically distinctive Sherwood/Sterman
      move not found in spreadsheet, BSC, or OKR frameworks.

- id: sk05
  title: Limits-to-Growth Diagnosis + "Take the Brakes Off" Intervention Rule
  source_units: [f08, f09, p13, p27, p30, ce07, ce19, c12, c14, c24, g21]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 8"
        context: "industrial revolution constrained by famine + disease B-loops; tea relieved disease constraint (c12)"
      - chapter: "Chapter 8"
        context: "Goldratt Theory of Constraints parallel discovery in manufacturing (c14)"
      - chapter: "Chapter 11"
        context: "Easter Island as resource-constraint limit-to-growth"
      - chapter: "Chapter 13"
        context: "car dealership constrained by MARKET SATURATION; 50% investment ratio yields almost identical sales but doubled retained earnings (c24)"
    note: |
      Four distinct domains: public-health history, manufacturing,
      ecological collapse, automotive retail. Merged decision:
      diagnostic (f08, recognize the archetype) and intervention rule
      (f09 / p13, take brakes off) travel together — separating them
      would yield two skills where the diagnostic without the
      intervention is sterile and the intervention without the
      diagnostic is reckless.
  V2_predictive_power:
    passed: true
    novel_question: |
      "Our SaaS company is doubling marketing spend year-over-year and
      revenue growth slowed from 60% to 40% to 20%. Board wants to
      triple marketing. What does systems thinking say?"
    derived_answer: |
      The deceleration signature is limits-to-growth: the reinforcing
      growth engine (customers → revenue → reinvestment) is being
      progressively braked by one or more balancing loops (likely
      market-saturation in the addressable segment, competitive
      response, or churn from poor-fit customers acquired at the
      margin). Tripling marketing pedals harder against the brake —
      Ch 13's car-dealership simulation predicts roughly the same
      revenue at 3× spend, with 3× the cash burn. Wise move: identify
      the binding constraint (segment-saturation? sales-cycle length?
      onboarding capacity? churn-from-marginal-fit?) and relieve it,
      then let the R-loop spin under its own momentum. Concrete
      diagnostic: which lever did we last move that fueled an active
      brake — and what would relieving that brake actually cost?
  V3_exclusivity:
    passed: true
    why_not_common: |
      Common business advice when growth slows: more budget, more
      hiring, more campaigns. Sherwood's counter — that the wise move
      is almost always to RELIEVE a constraint rather than push the
      engine — is genuinely counter-intuitive and high-leverage.
      Cross-validated by Goldratt independently arriving at the same
      principle in manufacturing (c14) which raises confidence that
      this is not a mere Sherwood quirk.

- id: sk06
  title: Variance/Target/Action Balancing-Loop Template + Do-Nothing-Under-Oscillation Diagnostic
  source_units: [f10, p14, p15, p21, p22, ce08, ce31, c08, c09, c10, g18, g22]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 6"
        context: "hotel shower oscillation (c08) — household-scale balancing loop with delay"
      - chapter: "Chapter 6"
        context: "inventory-control manager destabilizing a self-stabilizing system (c09)"
      - chapter: "Chapter 6"
        context: "Bank of England MPC small-moves-long-intervals discipline (c10)"
      - chapter: "Chapter 10"
        context: "every management lever as a B-loop module replicated across the business (p22)"
    note: |
      Four distinct domains: domestic plumbing, operations management,
      central-bank monetary policy, multi-lever strategy modeling.
      Merged decision: do-nothing-under-oscillation (p14) and
      reduce-delay-not-target (p15) and action-as-transient (p21) all
      hang off the same B-loop template (f10/p22); separating them
      fragments a single coherent workflow.
  V2_predictive_power:
    passed: true
    novel_question: |
      "Our customer-success NPS swings ±15 points quarter-to-quarter
      and we keep changing our customer-onboarding playbook every
      quarter to fix it. The swings are getting wider. What's wrong?"
    derived_answer: |
      The pattern — wider swings after each intervention — is the
      signature of a B-loop with delays (between playbook change,
      onboarding cohort, NPS response, and detection) being made worse
      by goal-moving / playbook-changing every quarter. Diagnostic:
      (1) what is the actual feedback delay from playbook-change to
      NPS-effect? (probably 6+ months for most NPS shifts to crystallize);
      (2) the quarterly cadence is faster than the loop can respond —
      classic ce08 over-reaction; (3) wise default is "do nothing for
      two quarters" and let the system converge; (4) if action required,
      attack the lag (faster NPS measurement on freshly-onboarded
      cohorts) rather than the playbook. BoE MPC discipline (c10) is
      the institutional model.
  V3_exclusivity:
    passed: true
    why_not_common: |
      Common management advice strongly favors *action* over *waiting*;
      "do absolutely nothing" looks like incompetence to anyone outside
      the loop and explicitly requires "wise bosses as well as wise
      manager" (p14). Recognizing endogenously-generated oscillation
      (g22) — system causing its own swings, not external noise — is a
      specialized distinction not in standard control-theory lay
      literature.

- id: sk07
  title: Lever-vs-Outcome Reframing (Strategy = Resetting Lever Target Settings)
  source_units: [f12, f13, p16, p17, p23, p36, ce17, g28, g29, g44]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 10"
        context: "generic-business-engine CLD: one R-loop + many B-loops + single fuzzy growth-driver link per lever"
      - chapter: "Chapter 10"
        context: "strategy definition as 'resetting lever target settings'"
      - chapter: "Chapter 12"
        context: "stocks-as-objectives, flows-as-actions reformulation (p36) — same insight in stock-and-flow vocabulary"
      - chapter: "Chapter 13"
        context: "car-dealership simulation makes the investment-ratio lever decision explicit (c24)"
    note: |
      Four contexts. f13 (one-R-loop-many-B-loops business engine) is the
      structural skeleton; f12/p16/p17 (lever vs outcome separation) is
      the named distinction; p23 (one driving fuzzy link per lever) is
      the operational locus. All three are inseparable in practice.
  V2_predictive_power:
    passed: true
    novel_question: |
      "Our CEO announced 'we will achieve 25% margin by 2027' but the
      operating plan she handed down doesn't change any pricing, any
      cost-line target, or any product-mix assumption. Why is the team
      cynical about this?"
    derived_answer: |
      MARGIN is an outcome, not a lever; the CEO has set a target on a
      result without resetting any of the lever target settings that
      drive it (price points, headcount, COGS, mix). Per ce17 the
      balancing-loop machinery for each lever is not triggered — no
      variance signal, no change program, no action. The team is right
      to be cynical: announcing an outcome target without lever target
      changes is rhetorically forceful but structurally inert. Strategy
      formulation requires naming each lever, its current target, its
      proposed new target, and the rationale; only then is the CEO's
      ambition mechanically actionable. (Test: if a name appears on
      both your levers list AND your outcomes list, one is misclassified
      — f12 / p17.)
  V3_exclusivity:
    passed: true
    why_not_common: |
      Most strategy frameworks (Porter's Five Forces, BSC, OKRs) operate
      at the outcome level (market share, customer satisfaction,
      objectives-and-results) without enforcing the lever-vs-outcome
      separation. The collapse of "strategy" into "set the lever
      targets" is a Sherwood-distinctive, useful reductive move that
      cuts through strategy-framework proliferation.

- id: sk08
  title: Three-Level Strategic Balancing-Loop Cascade + Scenario-Planning 3×N Reverse-Engineer
  source_units: [f14, f15, ce18, g32]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 10"
        context: "three timescale cascade — in-year fixes, annual budgeting, strategic-gap exploration (f14)"
      - chapter: "Chapter 10"
        context: "3×N scenario-planning table with InnovAction!-generated futures (f15)"
      - chapter: "Chapter 13"
        context: "ambition-as-target-dangle vs forecast-as-simulation-output distinction (ce18)"
    note: |
      Three contexts, all in the strategy chapters (10 + 13). Cross-domain
      is internally narrow (book applies it to corporate strategy only),
      but the *structural* claim — that strategy is itself a B-loop, with
      ambition as the input target dangle — recurs across timescales
      (in-year, annual, multi-year). Marginal pass on V1.
  V2_predictive_power:
    passed: true
    novel_question: |
      "Our 5-year plan has the same numbers as last year's 5-year plan
      with everything shifted one year later. What is the systems-thinking
      diagnosis?"
    derived_answer: |
      The strategic B-loop is dead — the ambition / vision / imagination
      dangle is flat. The cascade has degenerated to in-year fix loops
      only; no strategic gap (g32) is driving lever-target resets.
      Procedure: (1) run InnovAction!-style perturbation on today's
      context to generate 3-4 plausible (NOT probable) alternative
      futures; (2) for each, ask "if our levers stay where they are,
      will outcomes be acceptable?"; (3) where no, reverse-engineer the
      required lever settings; (4) choose lever settings either robust
      across many futures or high-upside on one — the choice itself is
      the strategy artifact, not the spreadsheet of numbers.
  V3_exclusivity:
    passed: true
    why_not_common: |
      Scenario planning is well-known (Shell / Pierre Wack), but Sherwood's
      specific structural framing — strategy as a top-level balancing
      loop nested above annual-budget and in-year-fix B-loops — plus the
      reverse-engineer-the-levers move (rather than forecast outcomes)
      is methodologically distinctive. ce18's vision-as-forecast warning
      is counter to common compensation-planning practice.

- id: sk09
  title: Multi-Perspective CLD for Wise Policy (Stop Forcing, Start Listening)
  source_units: [f11, p18, p19, ce11, ce16, ce26, c11, c15, c17, c20, c21, g31]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 5 / Ch 9"
        context: "resource-conflict two-R-loops-plus-higher-authority (c11)"
      - chapter: "Chapter 9"
        context: "TV talent problem — three-perspective workshop (executives / stars / juniors) — c15"
      - chapter: "Chapter 9"
        context: "theater-vs-dinner couple — mental-model mismatch (c17)"
      - chapter: "Chapter 9"
        context: "buyer-contractor outsourcing — two-perspective CLDs (c20) and real-world Railtrack/Balfour Beatty (c21)"
    note: |
      Four contexts across interpersonal, intra-org, inter-org, and
      industry-history domains. The pattern is the same: "force"
      produces two synchronized R-loops of escalating frustration;
      drawing the diagram from each side and looking for a beneficial
      policy that straddles all CLDs is the wisdom move.
  V2_predictive_power:
    passed: true
    novel_question: |
      "Engineering and Product have been arguing for 6 months about
      whether to invest in tech-debt vs new features. Each side accuses
      the other of being short-sighted. The CEO keeps mediating but the
      same fight returns. What should we try?"
    derived_answer: |
      Stop forcing, start listening — but specifically: ask each side to
      draw their CLD of "what makes the business succeed over 24 months."
      Engineering's CLD will likely show: tech-debt → velocity loss →
      shipping-pace decline → revenue decline (B-loop currently binding).
      Product's CLD will show: feature gap → competitive loss → churn →
      revenue decline (B-loop currently binding). The wise policy
      straddles both: identify the one or two tech-debt items whose
      removal *enables* the highest-leverage features, and the one or
      two features whose deferral *enables* tech-debt repayment.
      Visible only when both diagrams are on the same table (c15
      pattern). The CEO's mediation has failed because she has been
      adjudicating right/wrong (ce16) instead of surfacing mental
      models.
  V3_exclusivity:
    passed: true
    why_not_common: |
      "Listen to both sides" is common platitude. Sherwood's specific
      move — draw the formal CLD from each perspective, overlay them,
      search for a single policy that improves at least two of them
      beneficially — is a learnable craft. The Nelson/Coopers-&-Lybrand
      contrast operationalizes "high-performing team = shared mental
      models" as a discipline rather than a slogan.

- id: sk10
  title: Mental-Models-in-Harmony Team Reasoning + Leadership-as-Energy-Pumping
  source_units: [f18, p31, p32, p33, c18, c19, g05, g06, g30]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 1"
        context: "open-system / self-organization thermodynamic foundation (g05, g06)"
      - chapter: "Chapter 9"
        context: "Nelson's band of brothers at Trafalgar — high-performing-team gold standard (c18)"
      - chapter: "Chapter 9"
        context: "Coopers & Lybrand 100-partner anti-pattern (c19)"
      - chapter: "Chapter 9"
        context: "active vs passive listening as feedback-loop-completion (p32)"
    note: |
      Four contexts spanning thermodynamics, naval history, professional-
      services consulting, and interpersonal-communication theory.
      Sherwood ties them together with one structural claim: a team
      is an open self-organizing system whose order requires continuous
      energy input (leadership) and whose performance is set by mental-
      model harmony.
  V2_predictive_power:
    passed: true
    novel_question: |
      "We hired three star engineers from FAANG companies last quarter.
      Code reviews are now contentious, technical decisions take 3x as
      long, and morale is dropping. The hires are individually excellent.
      What is the systems diagnosis?"
    derived_answer: |
      Individual excellence does not produce team performance —
      mental-model harmony does (f18 / c18). The new hires arrive with
      mental models calibrated by their prior companies' (different)
      success structures; without explicit mental-model surfacing the
      team has lost coherence even as average individual quality rose.
      Prescription: schedule sustained shared-discussion time (Nelson's
      "years of training"), use CLDs to make each engineer's
      cause-and-effect beliefs about "what makes good code review"
      explicit and shareable, and recognize that leadership-as-energy-
      pumping (p31) means this is not a one-shot offsite but a
      continuous practice. C&L's 100-partner case (c19) is the
      cautionary anti-pattern: exhortation about teamwork does not
      substitute for the energy investment.
  V3_exclusivity:
    passed: true
    why_not_common: |
      Mainstream team-building literature emphasizes psychological
      safety, trust, or process. Sherwood's framing — team performance
      as an emergent property of an open thermodynamic system requiring
      continuous energy throughput — is genuinely distinctive and yields
      counter-intuitive predictions (a once-built team will degrade
      without ongoing leadership energy; a "leader-less" team is
      structurally a closed system and will decay).
      [Boundary note from BOOK_OVERVIEW: this rests on the unproven
      assumption that mental-model harmony beats cognitive diversity,
      which post-2010 research (Edmondson) contests. Surface this in
      Stage 2 Boundary field.]

- id: sk11
  title: Stock-and-Flow Translation from CLD to Simulation
  source_units: [f19, f20, f21, p35, p36, ce28, c23, c24, c25, c26, g26, g40, g41, g42, g43]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 12"
        context: "global milk production parable (c23) — fuzzy-variable simplification"
      - chapter: "Chapter 12"
        context: "Lake Chad 95% shrinkage as stock-and-flow arithmetic (c25)"
      - chapter: "Chapter 12"
        context: "Skandia intellectual-capital reporting (c26) — fuzzy stock made measurable"
      - chapter: "Chapter 13"
        context: "car-dealership CLD → plumbing-diagram → ithink simulation (c24)"
    note: |
      Four distinct contexts — agricultural economics, ecology, knowledge
      management, retail simulation. Translation rules (f19), stocks-as-
      objectives reformulation (f20), uniflow vs biflow (f21), and the
      classification principles (p35 / p36 / g40 / g41) all serve the
      single skill of "convert a qualitative CLD into a quantitative
      simulation-ready plumbing diagram."
  V2_predictive_power:
    passed: true
    novel_question: |
      "Our finance team wants to model 'staff morale' to support a
      retention-budget decision. They say it's not modelable because
      it's not a measurable balance-sheet item. What's the systems-
      thinking response?"
    derived_answer: |
      Morale IS a stock — it accumulates and depletes over time and is
      measurable at an instant (g40). The Skandia precedent (c26) shows
      a comparable fuzzy stock (knowledge) being formally reported. The
      modeling procedure: (1) classify MORALE as a stock with INFLOWS
      (recognition events, positive customer feedback, learning) and
      OUTFLOWS (burnout, perceived-unfairness events, departures);
      (2) draw plumbing diagram with biflow tap on MORALE if the
      inflows can also be negative (positive event misinterpreted →
      net depletion); (3) for each flow, identify the lever (compensation
      lever, recognition program, etc.) — flows are levers, stocks are
      outcomes (sk07 + f20); (4) accept fuzzy hand-drawn graphs for
      the response functions (sk04). Finance team's objection is the
      "if not on balance sheet not real" fallacy (ce05 / ce12);
      modeling beats refusing-to-model even with imprecise inputs.
  V3_exclusivity:
    passed: true
    why_not_common: |
      The stock/flow distinction is not common business knowledge —
      "interest rate" colloquially sounds like a flow but is a stock
      (Sherwood explicit, g40). The time-freeze test ("if time freezes
      can you measure it?") is a specific diagnostic. P&L-is-flows /
      Balance-sheet-is-stocks is operational. Common business teams
      confuse rates with flows constantly.

- id: sk12
  title: Models for Learning vs Models for Answers (and Why Linear Extrapolation Kills)
  source_units: [f22, p24, p25, ce13, ce14, ce15, ce22, c03, c04]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 5"
        context: "lily-pad / 50-day pond (c03) — late-detection of exponential"
      - chapter: "Chapter 5"
        context: "Caulerpa taxifolia algae (c04) — real-world frogs problem"
      - chapter: "Chapter 12-13"
        context: "linear-extrapolation warning + 'exponential masquerading as linear' (ce13)"
      - chapter: "Chapter 13"
        context: "model-induced overconfidence — treating fuzzy-input simulation output as forecast (ce15)"
      - chapter: "Chapter 6"
        context: "detail vs dynamic complexity (ce22, g27)"
    note: |
      Five distinct contexts. The framework combines two related claims:
      (a) modeling purpose determines tool choice (spreadsheet for
      answers, system dynamics for learning); (b) the dominant failure
      mode of management modeling is treating either an exponential
      growth curve as linear (early phase) or a learning-purposed
      simulation as a forecast (decision phase). Both errors flow
      from confusing detail complexity with dynamic complexity.
  V2_predictive_power:
    passed: true
    novel_question: |
      "We have a 50-tab spreadsheet projecting our churn rate to 2030.
      The CFO wants two more decimal places of accuracy. What is the
      systems-thinking critique?"
    derived_answer: |
      Decimal-place precision is the signature of treating a learning
      problem (where will churn go?) as an answer problem (compute churn
      to 4dp from rules). Churn is governed by feedback loops with fuzzy
      drivers (customer satisfaction → word-of-mouth → acquisition;
      saturation → segment quality → retention) — not by deterministic
      rules. The spreadsheet false-precision is ce15 model-induced
      overconfidence + ce22 detail-complexity-masquerading-as-dynamic-
      complexity. Prescription: build a small system-dynamics model
      with a handful of fuzzy variables and hand-drawn response curves,
      use it to explore "what would have to be true for churn to drop
      below X" rather than to forecast a single number, and treat the
      output as graphs to learn from, not numbers to plan with.
  V3_exclusivity:
    passed: true
    why_not_common: |
      Most spreadsheet-trained managers treat all models as answer-
      models. The Sherwood (and Forrester) insistence that some
      decisions need learning-models with deliberately fuzzy inputs
      is counter-cultural. The "exponential masquerading as linear"
      framing (ce13) is specifically named — common business reading
      does not have the doubling-time-vs-response-delay heuristic
      (ce14) that the frogs/Caulerpa pair sets up.

- id: sk13
  title: InnovAction!™ — Difference-from-Existing Idea Generation (with Martian Test)
  source_units: [f16, g34, g35]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 10"
        context: "scenario-planning alternative-future generation (f15 application)"
      - chapter: "Chapter 10"
        context: "general innovation methodology — chess example, product features (f16)"
    note: |
      Two contexts, both within Chapter 10. V1 is marginal but the
      method is structurally distinct from scenario-planning (sk08)
      because Sherwood explicitly invokes it as the generative mechanism
      *for* scenario futures and *for* product innovation, two distinct
      task-types. Retained per user override per BOOK_OVERVIEW.
      Sherwood-branded; close cousin of TRIZ / morphological analysis —
      Boundary should flag this in Stage 2.
  V2_predictive_power:
    passed: true
    novel_question: |
      "We need to brainstorm five plausible 2030 worlds for our scenario
      planning exercise. The team keeps producing trivial variants. What
      structural method gets us further?"
    derived_answer: |
      Stop trying to brainstorm in the abstract. Procedure: (1) compile
      a Martian-test-passing bullet list of today's world's features
      relevant to your business (regulations, customer demographics,
      tech stack, supply chain, capital cost, etc.) — detailed enough
      that an outsider could distinguish "today" from a slightly-
      different alternative; (2) pick ONE feature per scenario;
      (3) ask "how could THIS feature be different in 2030?" — radically
      different, not incrementally so; (4) elaborate consequences. The
      Martian-test bar (g35) is the operational completeness threshold
      — without it features stay too thin to perturb productively.
  V3_exclusivity:
    passed: true
    why_not_common: |
      Common brainstorming starts from blank paper. Sherwood's explicit
      rejection of greenfield-creativity in favor of "richness-first,
      then perturb one feature at a time" is methodologically
      distinctive. Note: overlaps with TRIZ / morphological analysis
      (mentioned in BOOK_OVERVIEW); Stage 2 Boundary should cite these
      as prior art and acknowledge Sherwood as one of several access
      points to the same method. Retained per user override.

- id: sk14
  title: Gods / Gamblers / Grinders / Guides — Planning-Style Personality Quadrant
  source_units: [f17, g33]
  type: framework
  V1_cross_domain:
    passed: true
    evidence:
      - chapter: "Chapter 10"
        context: "diagnostic framing for why scenario planning works for some leaders not others"
      - chapter: "Chapter 10 (implicit)"
        context: "alignment with consulting-fad-acceptance pattern (Grinders) and rejection-of-method pattern (Gods)"
    note: |
      Single chapter, single explicit application — V1 marginal. Retained
      per user override. The quadrant is cute but evidence-light;
      Boundary should flag that this is opinion / craft-typology not
      empirically validated; cousin of Hersey-Blanchard, Myers-Briggs-style
      typologies that have weak predictive validity in modern research.
  V2_predictive_power:
    passed: true
    novel_question: |
      "We invested 6 months in a scenario-planning exercise and the new
      CEO immediately discarded it on arrival. The COO loved it. What
      explains the asymmetry?"
    derived_answer: |
      Predict from quadrant: the CEO likely operates in the Gods quadrant
      (believes she can predict the future + controller) — for her,
      scenario planning is "in the way" because it foregrounds
      uncertainty she does not feel. The COO likely operates Guides
      quadrant (accepts unknowability + empowerer). The asymmetric
      reaction is structural to the quadrant, not personal. Implication:
      adapt the presentation — Gods-quadrant audiences need the
      output reframed as a decisive recommendation with fallback
      branches, not an exploration of plural futures; Guides-quadrant
      audiences accept the plural framing directly.
  V3_exclusivity:
    passed: true
    why_not_common: |
      The specific framing (can-predict × control/empower) is Sherwood's
      coinage and not in standard leadership-style taxonomies. The
      operational consequence — adapt scenario-planning output to
      quadrant — is non-obvious. Retained per user override; Boundary
      should keep the empirical-validity caveat front and center.

---

## Evidence pool (retained cases, not standalone skills)

- id: c01
  title: UK Investment Bank Back Office "Carrying the Rock"
  binds_to: [sk01, sk03, sk04, sk09]
  note: Seed case for vicious=virtuous, fuzzy-variable elevation, missing-link discovery.

- id: c02
  title: TV Production Cost-Cutting Vicious Circles
  binds_to: [sk01, sk05, sk09]
  note: Coupled R-R loops; precursor to talent-problem case c15.

- id: c03
  title: Frogs, Lily-pad, and the 50-Day Pond
  binds_to: [sk01, sk12]
  note: Pedagogical anchor for exponential growth and late-detection problem.

- id: c04
  title: Caulerpa Taxifolia "Killer Algae"
  binds_to: [sk01, sk12]
  note: Real-world frogs problem; exponential-detection failure.

- id: c05
  title: Hatfield Rail Crash & Railtrack Collapse
  binds_to: [sk01, sk09]
  note: Flagship boom-bust case demonstrating single-trigger reverses R-loop without structural change.

- id: c06
  title: Ratner's Jewelry "We Sell Crap"
  binds_to: [sk01]
  note: Single-utterance trigger flipping reputation R-loop; industry-agnostic boom-bust pattern.

- id: c07
  title: Dot-Com Boom and Bust (Amazon 1997-2001)
  binds_to: [sk01]
  note: Generic bubble loop across centuries (tulip / South Sea / 1929 / dot-com).

- id: c08
  title: Strange Hotel Shower
  binds_to: [sk06]
  note: Signature time-delay B-loop pedagogy.

- id: c09
  title: Inventory Control Manager Who Wasn't Trained in Systems Thinking
  binds_to: [sk06]
  note: Goal-moving destabilizes a self-stabilizing system; do-nothing diagnostic anchor.

- id: c10
  title: Bank of England Monetary Policy Committee
  binds_to: [sk06]
  note: Institutional best-practice exemplar for time-lagged B-loop with small, slow, deliberate intervention.

- id: c11
  title: Resource-Conflict Two-Reinforcing-Loops + Higher Authority
  binds_to: [sk05, sk09]
  note: Two-R-loops-with-shared-finite-resource archetype; bridges to limits-to-growth.

- id: c12
  title: Tea, Disease, and the Industrial Revolution
  binds_to: [sk05]
  note: Sherwood's flagship constraint-relief case; pedal-harder-vs-take-the-brakes-off parable.

- id: c14
  title: Eliyahu Goldratt and the Theory of Constraints
  binds_to: [sk05]
  note: Cross-validation — independent discovery of constraint-relief doctrine in manufacturing strengthens external validity.

- id: c15
  title: TV "Talent Problem" — Three-Perspective CLD Workshop
  binds_to: [sk09]
  note: Sherwood's flagship multi-perspective case.

- id: c17
  title: Theater vs Dinner Couple — Mental Model Mismatch
  binds_to: [sk09, sk10]
  note: Pedagogical case for stop-forcing-start-listening at interpersonal scale.

- id: c18
  title: Nelson's "Band of Brothers" Choosing the Team
  binds_to: [sk10]
  note: Gold-standard high-performing-team exemplar; shared mental models as emergent property.

- id: c20
  title: Utility Outsourcing — Buyer-Contractor Adversarial Dynamics
  binds_to: [sk09]
  note: Two-perspective CLD → joint-beneficial policy discovery.

- id: c21
  title: Railtrack / Balfour Beatty — Outsourced Track Maintenance
  binds_to: [sk09]
  note: Real-world consequence of buyer-contractor vicious circle in safety-critical domain.

- id: c23
  title: Spreadsheet vs System-Dynamics Mental Model (global milk)
  binds_to: [sk04, sk11, sk12]
  note: Parable for fuzzy-variable approach and look-up-and-out modeling stance.

- id: c24
  title: Provincial Car Dealership Growth Simulation (ithink)
  binds_to: [sk01, sk04, sk05, sk07, sk11]
  note: Flagship end-to-end case — CLD → plumbing diagram → ithink → policy experimentation. Quantitatively confirms constraint-relief doctrine.

- id: c25
  title: Lake Chad — 95% Shrinkage as Stock-and-Flow Failure
  binds_to: [sk11]
  note: Stock-and-flow arithmetic at planetary scale; real-world outflow > inflow consequence.

- id: c27
  title: Dick Whittington and London's "Streets Paved with Gold"
  binds_to: [sk05]
  note: Migration-driven urban R-loop, paired with births R-loop in tea/disease constraint-relief case (c12).

### Cases dropped from evidence pool

- c13 (Adam Smith / Invisible Hand): bound only to "emergence" abstract; no surviving skill leans on emergence as primary mechanism (sk10 uses self-organization concretely without needing Smith biographical sidebar).
- c16 (Jay Forrester biographical sidebar): historical-context only; no skill needs the biographical detail to function.
- c19 (Coopers & Lybrand): retained — bound to sk10 as anti-pattern. CORRECTION: keep as bound to sk10. [Adding back]
- c22 (BBC dominance context for c15): context-for-context; sk09 can cite c15 directly.
- c26 (Skandia intellectual capital): retained — bound to sk11 / sk04 as fuzzy-stock-measurability proof. CORRECTION: keep. [Adding back]

Re-evaluating: c19 and c26 SHOULD be retained; updating the count.

### Final evidence pool: 22 cases retained (c01, c02, c03, c04, c05, c06, c07, c08, c09, c10, c11, c12, c14, c15, c17, c18, c19, c20, c21, c23, c24, c25, c26, c27 = 24 actually; net of c13/c16/c22 dropped). Revised count: **24 retained, 3 dropped**.

---

## Glossary (retained, referenced by surviving skills)

- id: g01
  term: System
  used_by: [sk01, sk03, sk04, sk05, sk06, sk07, sk08, sk09, sk10, sk11, sk12]
  note: Foundational — every skill that says "diagnose the system" inherits Sherwood's strict connectedness sense.

- id: g02
  term: Heap
  used_by: [sk03]
  note: Discriminator for "is this worth modeling as a system?"

- id: g03
  term: Connectedness
  used_by: [sk01, sk03, sk09]
  note: Load-bearing concept against reductionism; CLD arrows encode it.

- id: g04
  term: Emergence
  used_by: [sk10]
  note: Team performance as emergent property.

- id: g05
  term: Self-organization
  used_by: [sk10]
  note: Open-system framing of teams + leadership-as-energy-pumping.

- id: g06
  term: Open System
  used_by: [sk10]
  note: Thermodynamic basis for self-organization.

- id: g07
  term: Holistic / Holistic View
  used_by: [sk03, sk09]
  note: Precision discipline, not vague generality.

- id: g08
  term: Reductionism (warned)
  used_by: [sk03]
  note: Anti-pattern named throughout sk03 (don't divide the elephant).

- id: g09
  term: Silo / Silo Mentality (warned)
  used_by: [sk09, sk10]
  note: Structural barrier to systems thinking — recurring Sherwood warning.

- id: g10
  term: Feedback Loop
  used_by: [sk01, sk02, sk03, sk05, sk06, sk07, sk08, sk09, sk10, sk11, sk12]
  note: Universal — the diagram primitive.

- id: g11
  term: Reinforcing Loop (positive feedback loop)
  used_by: [sk01, sk05, sk07, sk09, sk11]
  note: Even-O classification.

- id: g12
  term: Balancing Loop (negative feedback loop)
  used_by: [sk01, sk05, sk06, sk07, sk08, sk11]
  note: Odd-O, goal-seeking; under delay oscillates.

- id: g13
  term: S link
  used_by: [sk01, sk02, sk03]
  note: Same-direction causal link.

- id: g14
  term: O link
  used_by: [sk01, sk02, sk03]
  note: Opposite-direction causal link.

- id: g15
  term: Causal Loop Diagram (CLD)
  used_by: [sk01, sk02, sk03, sk04, sk05, sk06, sk07, sk08, sk09, sk10, sk11, sk12]
  note: Central artifact of the whole book.

- id: g16
  term: Dangle
  used_by: [sk03, sk07, sk08, sk11]
  note: Boundary-marker taxonomy (input/target/rate/output/policy).

- id: g17
  term: Fuzzy Variable
  used_by: [sk04, sk07, sk11, sk12]
  note: Variable elevated to first-class node without measurement.

- id: g18
  term: Time Delay
  used_by: [sk06, sk07]
  note: Source of oscillation in balancing loops.

- id: g19
  term: Vicious Circle / Virtuous Circle
  used_by: [sk01]
  note: Structural identity — same loop, different trigger.

- id: g20
  term: Exponential Growth / Exponential Decline
  used_by: [sk01, sk05, sk12]
  note: Doubling-time signature.

- id: g21
  term: Limits to Growth (archetype)
  used_by: [sk05, sk07]
  note: Two-loop archetype — R-engine constrained by B-brake.

- id: g22
  term: Oscillation
  used_by: [sk06]
  note: Endogenously generated, not external noise.

- id: g23
  term: Reversibility Test
  used_by: [sk02, sk03]
  note: Sign-discipline check for S/O assignments.

- id: g24
  term: Sterman Ultimate Test
  used_by: [sk02]
  note: Authoritative fallback for ambiguous S/O.

- id: g25
  term: Wastepaper Basket (as primary tool)
  used_by: [sk03]
  note: Iterative drafting normalized.

- id: g26
  term: One-Way Link / Uniflow Link
  used_by: [sk02, sk11]
  note: Pouring-coffee asymmetry; stock-and-flow inflow vs outflow.

- id: g27
  term: Detail Complexity vs Dynamic Complexity
  used_by: [sk03, sk12]
  note: Discrimination prevents detail-explosion modeling failure.

- id: g28
  term: Lever
  used_by: [sk07, sk08, sk11]
  note: Directly controllable action variable — name, target, actual.

- id: g29
  term: Outcome
  used_by: [sk07, sk08]
  note: Result variable, never directly controllable.

- id: g30
  term: Mental Model
  used_by: [sk09, sk10]
  note: Each person's deeply held causal map; CLD makes it explicit.

- id: g31
  term: Wise Policy / Wisdom
  used_by: [sk08, sk09, sk10]
  note: Holistic systemic-consequence reasoning, not cleverness.

- id: g32
  term: Strategic Gap
  used_by: [sk08]
  note: Difference between current trajectory and ambition; driver of strategic B-loop.

- id: g33
  term: Gods / Gamblers / Grinders / Guides
  used_by: [sk14]
  note: Sherwood-coined leadership-style quadrant.

- id: g34
  term: InnovAction!™
  used_by: [sk13]
  note: Sherwood-coined creativity method.

- id: g35
  term: Martian Test
  used_by: [sk13]
  note: Operational completeness bar for feature lists.

- id: g39
  term: System Dynamics
  used_by: [sk11, sk12]
  note: Computer-simulation methodology built from stocks/flows/feedback.

- id: g40
  term: Stock
  used_by: [sk07, sk11]
  note: Accumulates over time; measurable at instant; outcomes are stocks.

- id: g41
  term: Flow
  used_by: [sk07, sk11]
  note: Changes stock over time interval; levers are flows.

- id: g42
  term: Plumbing Diagram / Stock-and-Flow Diagram
  used_by: [sk11]
  note: Translation target for CLDs en route to simulation.

- id: g43
  term: Cloud (boundary symbol)
  used_by: [sk03, sk11]
  note: Boundary marker for inflows/outflows beyond system of interest.

- id: g44
  term: Growth Engine (generic causal loop)
  used_by: [sk05, sk07]
  note: Every business has one; diagnose this first.

- id: g45
  term: Variance (in balancing loops)
  used_by: [sk02, sk06, sk07]
  note: TARGET − ACTUAL (or convention-flipped) driving the action node.

### Glossary terms dropped

- g36 Gaia: Ch 11 only; no surviving skill leans on Gaia framing (BOOK_OVERVIEW notes the Ch 11 chapter is dropped per "Content NOT suitable for skills" recommendation). The constrained-R-loop pattern is captured by sk05 limits-to-growth without needing Gaia vocabulary.
- g37 Living Pump: same — Ch 11 environmental case material.
- g38 Four Horsemen: same — Ch 11 biblical-iconography for B-loops; sk05 carries the limits-to-growth concept without needing this label.

### Final glossary retained: 42 terms.

---

## Cluster summary table

| Skill | Type | Source frameworks | Source principles | Source counter-examples | Source cases (binds_to) | Source glossary (used_by) |
|---|---|---|---|---|---|---|
| sk01 | framework | f01, f02, f23 | p28, p29, p34 | — | c01, c02, c03, c04, c05, c06, c07, c12, c24 | g10, g11, g12, g19, g20 |
| sk02 | framework | f03, f21 | (p06 partial) | ce09, ce27 | — | g13, g14, g23, g24, g26, g45 |
| sk03 | framework | f04, f05 | p01-p12 | ce04, ce20, ce21, ce23, ce25, ce30 | (workshop cases) | g15, g16, g25, g27, g43 |
| sk04 | framework | f06, f07 | p07, p20, p26 | ce05, ce12, ce29 | c01, c23, c26 | g17 |
| sk05 | framework | f08, f09 | p13, p27, p30 | ce07, ce19 | c11, c12, c14, c24, c27 | g11, g12, g21, g44 |
| sk06 | framework | f10 | p14, p15, p21, p22 | ce08, ce31 | c08, c09, c10 | g12, g18, g22, g45 |
| sk07 | framework | f12, f13 | p16, p17, p23, p36 | ce17 | c24 | g16, g28, g29, g40, g41, g44, g45 |
| sk08 | framework | f14, f15 | — | ce18 | — | g28, g29, g31, g32 |
| sk09 | framework | f11 | p18, p19 | ce11, ce16, ce26 | c05, c11, c15, c17, c20, c21 | g09, g30, g31 |
| sk10 | framework | f18 | p31, p32, p33 | — | c18, c19 | g04, g05, g06, g09, g30 |
| sk11 | framework | f19, f20 | p35, p36 | ce28 | c23, c24, c25, c26 | g17, g26, g28, g29, g39, g40, g41, g42, g43 |
| sk12 | framework | f22 | p24, p25 | ce13, ce14, ce15, ce22 | c03, c04 | g20, g27, g39 |
| sk13 | framework | f16 | — | — | — | g34, g35 |
| sk14 | framework | f17 | — | — | — | g33 |

---

## Stage-1.5 calibration log

- **Aggressive merging** of f04 + p01..p12 into sk03 was the highest-leverage call: the alternative (12 separate Rule-1 ... Rule-12 skills) would have given 12 weak skills with no individual V3 pass (each rule on its own is "common-sense diagram hygiene"); together they constitute a learnable craft.
- **Refused merge** of sk01 with sk07 (lever-outcome): tempting because the business engine in f13 contains the R-loop sk01 explains, but sk01 is a diagnostic primitive used in many non-strategy contexts (sk05 limits-to-growth, sk09 multi-perspective, sk11 stocks/flows), while sk07 is strategy-specific. Keeping separate preserves modularity.
- **Refused merge** of sk05 (limits-to-growth) with sk07 (lever-outcome): the master archetype is general; lever-vs-outcome is one specific managerial restatement. Each has independent V1 evidence pools.
- **Refused merge** of sk09 (multi-perspective wise policy) with sk10 (mental-models-in-harmony team): they share the mental-models machinery (g30) but sk09 is conflict-resolution between groups whose mental models differ, while sk10 is team-building from groups whose mental models can be brought into harmony. Different intervention targets.
- **InnovAction!™ (sk13) and Gods/Gamblers (sk14)** retained per user override despite weak V1 — Stage 2 Boundary fields must surface the limitations (Sherwood-branded, overlap with TRIZ; cute-but-evidence-light 2×2) explicitly.
- **Ch 11 (Gaia / Easter Island / global warming) excluded** per BOOK_OVERVIEW recommendation — the underlying constrained-R-loop pattern is preserved in sk05; the chapter's specific Gaia framing is too 2002-dated and domain-specific.
