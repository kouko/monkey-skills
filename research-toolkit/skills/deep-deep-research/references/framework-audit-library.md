# Framework Audit Library

> **This is an AUDITOR checklist, NOT a generator.** Use it *after* you have
> already brainstormed an angle set. Frameworks here are tuned to find the
> dimensions you *missed*, not to produce angles from scratch — empirically,
> a free-form brainstorm out-recalls a framework-as-generator; a framework
> used as a completeness *audit* on top of free-form angles catches the
> blind spots the brainstorm left open.

## How to use (3-step walk)

1. **Type → route.** Classify the question's type, look it up in the
   **routing table** below, and pick **2–3 first-line frameworks**
   (add a reinforcement framework only if the route's cells feel thin).
2. **Walk the cells.** For each chosen framework, take every cell/dimension
   and ask: *"Does my existing angle list cover this cell?"* An uncovered
   cell is a candidate gap → propose a gap-fill angle tagged with its
   `framework` + `cell`.
3. **Dedup, then meta-check.** Multiple frameworks overlap (see
   **Cross-framework dedup notes**); walk a shared cell only once. Finally
   run the **7 collective blind-spots** — the dimensions *all* frameworks
   structurally miss — and add any that your angles don't already cover.

Each framework block has the shape:
`name → cells/dimensions → "as auditor" one-liner → blind-spot`.
Cells are the walkable cells; the auditor line is the one question to ask;
the blind-spot is what the framework itself cannot see (so you don't trust
it past its edge).

---

## Routing table (question type → first-line frameworks + reinforcement)

| Question type | First-line frameworks (walk the cells) | Reinforcement |
|---|---|---|
| **Triage first (any question)** | **Cynefin** (judge clear/complicated/complex/chaotic), Wicked Problems | levels of analysis |
| **Any question (general start)** | MECE/issue tree, 5W1H, PMEST, SCQA | Six Thinking Hats, levels of analysis |
| **Investment / single stock** | top-down, economic moat, **DCF + relative valuation (comparables)**, DuPont, bull/bear/base, checklist | Five Forces, margin of safety, equity risk taxonomy, Kelly |
| **Macro / industry** | PESTEL, Five Forces, top-down | first/second-order equilibrium, stock-flow, leverage points |
| **Policy / regulation** | Bardach eightfold path, CBA, stakeholder, first/second-order equilibrium | Kingdon, policy cycle, tax incidence, Overton, game theory |
| **Negotiation / game theory** | BATNA/ZOPA, game theory/payoff matrix, stakeholder | power-interest, second-order, actor mapping |
| **Business strategy / competition** | SWOT, Five Forces, Value Chain, VRIO | BCG, Ansoff, Blue Ocean, Wardley, 7S, Three Horizons, game theory |
| **Business model / startup** | Business Model Canvas / Lean Canvas, JTBD, pains/gains | unit economics (LTV/CAC), AARRR, Blue Ocean |
| **Product / UX** | Double Diamond, JTBD, customer journey, Kano | Nielsen heuristics, HEART, AARRR, pains/gains |
| **Marketing / GTM** | STP, 4Ps/7Ps (with 4C), AIDA | customer journey, JTBD, PESTEL |
| **Medical / diagnosis** | VINDICATE, ACH (competing hypotheses), ABCDE (emergency) | SOAP, base rates, 5 Whys |
| **Tech evaluation / selection** | TRL, SOTA scan, morphological analysis | technology forecasting, CBA, Wardley |
| **Data / ML analysis** | CRISP-DM, error analysis, bias-variance, cross-validation | causal DAG, A/B test, DoE, ablation |
| **Causal / effect evaluation** | causal ladder (association/intervention/counterfactual), DAG, confounding/selection taxonomy | DoE, A/B test, sensitivity |
| **Design / innovation process** | Design Thinking five steps, HMW, desirability-feasibility-viability | Double Diamond, Crazy 8s, JTBD, Kano |
| **Interaction / interface design** | Norman seven stages, Norman six principles, Nielsen heuristics, Fitts/Hick | Laws of UX, SUS, customer journey |
| **Industrial / product design (emotional)** | Kansei engineering, Jordan's four pleasures, Norman six principles | Kano, desirability-feasibility-viability, SUS |
| **Security / threat modeling** | STRIDE, Attack Tree, MITRE ATT&CK, Kill Chain | PASTA, DREAD, FMEA, bowtie |
| **Quality / gemba improvement** | QC seven tools, 5 Whys (naze-naze), cause-and-effect diagram, DMAIC, PDCA | new QC seven tools, QFD, TOC, FMEA, Pareto |
| **Process / bottleneck / capacity** | TOC (Theory of Constraints), DMAIC, stock-flow | CLD, leverage points, value chain |
| **Task / prioritization** | Eisenhower matrix, RICE/ICE, MoSCoW | Kano, Three Horizons, OKR |
| **Quantitative estimation / uncertainty** | Fermi, Monte Carlo, sensitivity, decision tree | scenario, base rates, expected value |
| **Risk / safety** | FMEA, pre-mortem, bowtie, fault tree | HAZOP, STAMP, what-if, equity risk taxonomy |
| **International relations / geopolitics** | Waltz levels, IR three lenses, PMESII-PT, DIME | actor mapping, power-interest, stakeholder |
| **Military / adversarial competition** | OODA, CoG, ends-ways-means, DIME, game theory | PMESII, red teaming, second-order |
| **Root cause / failure** | 5 Whys, Ishikawa, fault tree, ACH | iceberg, CLD, FMEA |
| **Systems / policy backlash** | iceberg, CLD, leverage points, stock-flow | second-order, Bardach |
| **Decision / betting** | expected value, base rates, WRAP, bull/bear/base, Kelly | inversion, pre-mortem, second-order, Cynefin |
| **Argument / writing** | Toulmin, IRAC, MECE, SCQA | devil's advocacy, key assumptions check |
| **Ethics / value trade-off** | consequentialist/deontological/virtue three lenses, stakeholder ethics | CBA, second-order, Overton |
| **Organization / change** | 7S, RACI, stakeholder, power-interest | OKR, MoSCoW, iceberg |
| **Sustainability / ESG** | LCA, ESG three dimensions, planetary boundaries | stakeholder, CBA, second-order |
| **Creativity / divergence** | SCAMPER, morphological, Mandalart, Six Hats | lateral thinking, TRIZ, first-principles, inversion |
| **Self-audit (anti-blind-spot)** | key assumptions check, pre-mortem, devil's advocacy, ACH | inversion, base rates, red teaming |

---

## Framework cell-blocks

Pick the 2–3 from your route, walk the cells, propose gap-fill angles for
uncovered cells. Provenance kept where the source cites it; cells are
stable public knowledge.

### Universal / cross-domain

**MECE / Issue Trees** — Minto, *Pyramid Principle* (1987).
- Cells: split the question into sub-questions where each layer is **M**utually **E**xclusive (no overlap) and **C**ollectively **E**xhaustive (no gap); every branch node is a cell.
- As auditor: *"Do this layer's branches sum to 100% of the parent question? Any overlap?"* — the meta-framework for "did I miss anything".
- Blind-spot: easy to hit *formal* exhaustiveness while missing a substantive branch; doesn't tell you if you picked the right split dimension.

**5W1H / 5W2H** — Five Ws journalism tradition.
- Cells: Who / What / When / Where / Why / How [+ How much / How many].
- As auditor: walk all six; a missing cell = incomplete description. Most-missed: **Why** (motive/causality) and **How much** (magnitude).
- Blind-spot: surface-of-event only; no mechanism, no time evolution, no stakeholder conflict; Why only one layer deep.

**SCQA** — Minto, *Pyramid Principle* (1987).
- Cells: Situation (known context) → Complication (what changed/broke) → Question (the core ask the complication raises) → Answer (your claim).
- As auditor: *"Did I jump to the answer without setting situation + complication? Does the reader know which question I'm answering?"* Most-missed: **Complication**.
- Blind-spot: communication structure only; doesn't guarantee the argument below is correct (pair with MECE).

**Cynefin (problem-type triage)** — Snowden & Boone, *HBR* 2007.
- Cells (5 domains + action mode): **Clear/Obvious** (obvious cause→effect) → sense-categorize-respond / **Complicated** (needs expert analysis) → sense-analyze-respond / **Complex** (causality only visible in hindsight) → probe-sense-respond (experiment) / **Chaotic** (no discernible causality) → act-sense-respond (stop the bleeding) / **Disorder** (don't know which domain).
- As auditor: *"Which domain is this really? Am I mis-applying a linear analytic framework to a complex (experiment-needed) problem?"*
- Blind-spot: domain assignment is subjective, boundaries fuzzy; gives no detailed decomposition per domain (hand off to the matching framework).

### Structured analytic / anti-blind-spot (SATs)

**ACH — Analysis of Competing Hypotheses** — Heuer (CIA, 1999); Heuer & Pherson 2011.
- Cells (8 steps): (1) enumerate **all** hypotheses (not just the likeliest) → (2) list evidence/arguments → (3) build hypothesis×evidence matrix → (4) mark each item consistent/inconsistent per hypothesis → (5) refine → (6) pick the hypothesis with the **fewest** contradictions (not most support) → (7) sensitivity analysis → (8) report relative likelihoods + future indicators.
- As auditor: *"Did I list **all** plausible hypotheses, or only confirm my favorite?"* Missing a hypothesis = confirmation bias.
- Blind-spot: evidence weighting is human-judged; can still miss the unknown-unknown hypothesis entirely.

**Key Assumptions Check** — Heuer & Pherson 2011.
- Cells: list **every** assumption the analysis rests on → for each ask: does it hold? under what conditions would it break? how would the conclusion change if it broke? which assumptions are *unstated but conclusion-determining*?
- As auditor: surface the unspoken premises and stress-test each — most-missed: *"I assumed the status quo continues."*
- Blind-spot: assumptions you can't articulate stay hidden; needs an outside view.

**Pre-mortem** — Klein, *HBR* 2007.
- Cells: imagine "the project has already failed completely" → write out **every** possible cause of death → rank → set a prevention / early indicator for each.
- As auditor: use the "future-failure" stance to force out risks that optimism bias is hiding.
- Blind-spot: covers the *failure* face only; bounded by imagination; doesn't ask "who steals the success".

### Systems thinking

**Systems Iceberg** — systems-thinking tradition (Kim / Senge school).
- Cells (4 layers, shallow→deep): Events (visible phenomena) → Patterns/Trends → Structures (institutions/incentives/feedback) → Mental Models (beliefs/assumptions).
- As auditor: *"Does my analysis stop at the event layer, or did I dig to structure and mental models?"* Most analyses miss the bottom two layers.
- Blind-spot: layer division is subjective; gives no intervention point (pair with Leverage Points).

### Business strategy

**PESTEL / PESTLE** — popularized from Aguilar's *Scanning the Business Environment* (1967; the PEST acronym is a later textbook codification).
- Cells: Political / Economic / Social / Technological / Environmental / Legal [variants: STEEP, +Geographic].
- As auditor: walk all six macro drivers — which class of macro force did I omit? Most-missed: **Legal** and **Environmental**.
- Blind-spot: lists factors but gives no interaction or weighting; no industry-competition layer (pair with Five Forces); no time ordering.

**Porter Five Forces** — Porter, *HBR* 1979 / *Competitive Strategy* (1980).
- Cells: (1) threat of new entrants / (2) supplier bargaining power / (3) buyer bargaining power / (4) threat of substitutes / (5) rivalry among existing competitors [often +6th: complements / government].
- As auditor: walk all five — which pressure did I omit when assessing the industry/company? Most-missed: substitutes and supplier power.
- Blind-spot: static snapshot, ignores dynamics and cooperation (ecosystems/complements); no macro layer (pair with PESTEL). Also misses *platform / external-dependency obsolescence* — a strategy built on a platform you don't control (Wardley-style evolution/commoditization moves a capability you depend on down the value chain) carries the risk that the entitlement / API / capability you rely on is deprecated or cut mid-stream.

### Investment / finance

**DuPont Analysis** — DuPont Co., 1920s (F. Donaldson Brown).
- Cells: ROE = net margin (profitability) × asset turnover (efficiency) × equity multiplier (leverage) [5-factor version further splits tax burden and interest burden].
- As auditor: *"Is this high ROE from profit, efficiency, or leverage?"* Missing the leverage cell = mis-reading risk.
- Blind-spot: accounting numbers are manipulable; excludes cash flow and capex quality.

**Economic Moat** — Buffett concept; Dorsey (Morningstar) systematized.
- Cells (moat sources): intangibles (brand/patent/license) / switching costs / network effects / cost advantage (scale/process/location) / efficient scale (niche monopoly).
- As auditor: *"Which moat type does this company have? Can it be eroded? Width and trend?"* Most-missed: the *time* dimension — "moat narrowing"; and the *key-person* dimension — durability also rests on retaining the key talent/architects who sustain the advantage, so a competitor poaching them erodes the moat.
- Blind-spot: easy to rationalize after the fact; moats vanish (tech disruption); width is hard to quantify.

**Equity Risk Taxonomy** — general investment risk-management taxonomy (CFA-curriculum style).
- Cells: market/systematic / industry / company-specific (operating/financial/governance/key-person concentration) / liquidity / valuation / event (policy/litigation/M&A) / ESG.
- As auditor: *"Which classes hold this name's main risks? Did I miss governance or liquidity?"*
- Blind-spot: classes overlap; tail/unknown risks hard to enumerate; weighting is judgment.

**Bull / Bear / Base Case** — scenario-analysis practice (sell-side / PE).
- Cells: Bull (optimistic) / Bear (pessimistic) / Base, each with its assumptions, target price, probability; compute a probability-weighted expectation.
- As auditor: *"Is my Bear case pessimistic enough? Are the three scenarios' key variables consistent?"* Most-missed: a genuinely harsh bear case.
- Blind-spot: scenarios often artificially symmetric, ignore tails; probabilities subjective.

**DCF + Comparables** — DCF: Williams (1938); Comparables: standard equity-research practice (Damodaran systematized).
- DCF cells: forecast free cash flow (FCF) / discount rate (WACC) / terminal value (perpetual growth) → discounted sum = enterprise value → minus net debt = equity value.
- Comparables cells: P/E, EV/EBITDA, P/B, P/S, PEG, P/FCF, SOTP; steps = pick peers → compute multiples → take median/mean → apply to target.
- As auditor: *"Did I only run DCF? What do peer multiples say? Right peers (growth/risk/accounting-comparable)? Right multiple (don't use P/E on a loss-maker)?"* DCF and comparables are the **complementary two halves** of valuation — running only one is doing valuation half-way.
- Blind-spot: DCF is hyper-sensitive to assumptions (garbage-in; terminal value often dominates); comparables means "if the market is wrong you're wrong too".

### Economics / policy

**Bardach Eightfold Path** — Bardach, *A Practical Guide for Policy Analysis* (2000).
- Cells (8 steps): (1) define the problem → (2) assemble evidence → (3) construct alternatives → (4) select criteria → (5) project outcomes → (6) confront trade-offs → (7) decide → (8) tell your story (communicate).
- As auditor: *"Did I skip 'construct enough alternatives' or 'state explicit criteria'?"* Most-missed: steps 3 and 4.
- Blind-spot: linear flow, weak on political dynamics and power; criteria selection itself carries value judgments.
- *(Route note: if Bardach isn't your fit, the policy route's present alternatives are CBA / stakeholder / first-second-order effects — below.)*

**Cost-Benefit Analysis (CBA)** — Dupuit (1848); US Flood Control Act (1936).
- Cells: list all costs / all benefits (incl. externalities) → monetize → discount to present value → compute NPV / benefit-cost ratio → sensitivity analysis.
- As auditor: *"Did I include externalities and non-monetary effects? Is the discount rate doing too much work?"*
- Blind-spot: assumes the best option gets adopted (ignores politics); aggregates totals (hides distribution — who wins/loses); hard-to-monetize values get dropped.

**First / Second-order & General-equilibrium** — economics tradition (partial vs general equilibrium; Bastiat's "seen and unseen").
- Cells: first-order direct effect → second-order behavioral adjustment (how people change once incentives shift) → general equilibrium (whole-market prices/quantities re-balance) → unintended consequences.
- As auditor: *"Did I only compute the direct (first-order) effect? How will people avoid/substitute (second-order)? What after the whole market re-equilibrates?"*
- Blind-spot: second-order-and-beyond is hard to quantify, high uncertainty; sensitive to model assumptions.

**Stakeholder Analysis** — Freeman, *Strategic Management: A Stakeholder Approach* (1984).
- Cells: identify all stakeholders → each one's stake / power / stance (support/oppose) / channel of influence → corresponding strategy.
- As auditor: *"Did I list everyone who's affected? Did I miss the silent / powerless stakeholders?"* Most-missed: voiceless groups.
- Blind-spot: static snapshot; interests shift; power assessment is subjective.

**Power-Interest Grid** — Mendelow (1991).
- Cells: 2×2 = power (high/low) × interest (high/low) → Manage Closely / Keep Satisfied / Keep Informed / Monitor.
- As auditor: place each stakeholder in a quadrant — *"Am I watching the high-power / low-interest player who could suddenly object?"*
- Blind-spot: only two dimensions; power/interest shift by issue; ignores the relationship network.

---

## Cross-framework dedup notes

Multiple frameworks share the same cell — walk it once. Marking overlaps
prevents double-auditing one dimension and the "two frameworks = wider
coverage" illusion.

- **External environment**: PESTEL ≈ STEEP ≈ PMESII-PT (military) ≈ SWOT's O/T. Walk the macro external drivers once; pick the finest-grained for your domain (business → PESTEL, geopolitics → PMESII-PT).
- **Competition / industry structure**: Five Forces ⊃ the competitive part of SWOT's O/T. SWOT gives a snapshot, Five Forces the structure — don't count the same threat twice.
- **Root cause**: 5 Whys (single line) ⊂ Ishikawa (multi-cause categories) ⊂ Fault Tree (logic gates + probability). For complex problems go straight to Ishikawa/FTA — don't stop at 5 Whys.
- **Systems thinking**: Iceberg (layers), CLD (feedback), Stock-Flow (accumulation), Leverage Points (intervention) are four lenses on one systems view — Iceberg finds structure, CLD finds feedback, Leverage Points finds where to intervene. Use in sequence, no double-walk.
- **Challenge-assumptions cluster**: Key Assumptions Check, Devil's Advocacy, Red Teaming, Pre-mortem, ACH, Inversion overlap heavily — **all ask "where might I be wrong"**. Pick 1–2 (solo decision → pre-mortem + inversion; team → red team + ACH).
- **Stakeholders**: stakeholder analysis (descriptive/power) ≈ power-interest grid (operationalized) ≈ stakeholder ethics (normative/fairness) ≈ actor mapping (conflict version). List the full roster once, then apply different questions as needed.
- **Valuation**: DCF (absolute/intrinsic) + comparables (relative/market) are the complementary two halves, often cross-checked in practice — not redundant; using only one is doing valuation half-way.
- **Second-order**: decision-version (Marks' second-order thinking) ↔ economics-version (first/second-order equilibrium) ↔ systems CLD all capture the same "downstream adjustment" logic — same logic across domains.

---

## Collective blind-spots (7, meta-level)

> Any single framework structurally sees only what its cells encode — the
> chosen lens *is* the blind spot (Maslow's law of the instrument; Munger's
> latticework; multi-framing — Bolman & Deal: "each frame… is a product of …
> blind spots", Morgan's *Images of Organization*, Allison's *Essence of
> Decision*). After the framework walk, two omission classes remain
> *regardless of domain*: **structural / frame omissions** (the lens has no
> cell for it) and **cognitive omissions** (the mind treats present
> information as complete). The recognized **self-applied** completeness
> canons are the Decision Quality six-element chain (Spetzler, Winter & Meyer,
> SDG 2016) and the IC analytic standards (ICD 203); the cognitive layer's
> root is Kahneman's WYSIATI ("what you see is all there is").
>
> Honest notes: this list is **not itself a named canon** — it synthesizes
> the above, so each item carries its own citation and the *category* is not
> claimed as canonical. Items can cross both axes (Cooper, *Curing Analytic
> Pathologies*). The Kahneman-Lovallo-Sibony 2011 checklist is scoped for
> evaluators judging *others'* proposals, so it is referenced only in the
> guardrail's motivation/social note below, not used as the section anchor.
>
> One thing is **not** on this list: questioning the frame itself and
> enumerating alternative frames is the framework walk's own job (MECE /
> issue tree / ACH / SCQA are the general-start frameworks), so it is not
> repeated here.

**Axis A — Structural / frame omissions** (the chosen lens has no cell for it, any domain):

- **A1 — Time & dynamics**: most frameworks are static snapshots, with no cell for evolution, lag, or when the conclusion/premise expires. → Add the time axis: how does this evolve, what is the lag, and when does the conclusion expire? (Systems/CLD delay; Mintzberg's prediction fallacy; Iriyama's theory-vs-framework — a framework's implicit premise is context-dependent and goes obsolete.)
- **A2 — Second-order / reflexivity**: frameworks stop at first-order; others adapt, markets re-equilibrate, and the act of analyzing changes the analyzed thing. → Add second-order / general-equilibrium effects. (Marks' second-order thinking; Soros reflexivity.)
- **A3 — Feasibility, power & reversibility**: analytic frameworks assume the best option is adopted; they miss who vetoes, whether it can actually be executed, and how hard the decision is to undo (one-way vs two-way door). → Add stakeholder/power + an execution check + a reversibility check. (DQ "commitment to action"; Pfeffer & Sutton, *The Knowing-Doing Gap*; Kingdon; Bezos's one-way/two-way doors.)

**Axis B — Cognitive omissions** (the mind treats present information as all there is — WYSIATI — regardless of framework):

- **B1 — Outside view / base rates**: anchored on the case, omitting the reference-class distribution; salient features crowd out absent or unattended ones. → Add base rates / the outside view. (Base-rate neglect, Kahneman & Tversky 1973; reference-class forecasting, Flyvbjerg 2004/2006; outside-view concept, Kahneman & Tversky 1979 / Kahneman & Lovallo 1993; focusing illusion, Kahneman & Schkade 1998.)
- **B2 — Disconfirming evidence & rival hypotheses**: confirmation-seeking; failure to generate or test the alternatives. → List rival hypotheses and seek disconfirming evidence. (Confirmation bias, Wason; Klayman & Ha 1987; ACH.)
- **B3 — Uncertainty & evidence quality**: confidence left unmarked; source independence and reliability unchecked. → Tag each conclusion's confidence and check source independence. (ICD 203 Standard 2 uncertainty + Standard 3 assumptions-vs-judgments; SAT Quality-of-Information Check.)
- **B4 — Unknown-unknowns**: the omission no cell maps to; what kills you isn't on any list. → Run a structured surfacing technique. (WYSIATI's limit case; pre-mortem, Klein 2007; what-if analysis.)

**Demoted to notes** (lower-yield or conditional — *not* numbered slots, but don't lose them):

- *Values / normative (conditional)*: for **high-stakes** / normative questions, add the ethical lenses (consequentialist / deontological / virtue) + stakeholder ethics — the values-and-tradeoffs dimension a positive-analysis framework has no cell for. Conditional, not universal: skip it on a purely descriptive question. (DQ "clear values & tradeoffs".)
- *Distribution / tails (sub-note of B1)*: aggregates hide who-wins-who-loses and the tail — a single expected value or total can be right while the distribution is the whole story. Check the distribution, especially for risk / policy questions. (CBA's distribution blind-spot.)

**Guardrail — audit-as-justification / thought-stopping** (not numbered): an empty gap is a legitimate, honest result — finding nothing missing is a valid outcome, not a failure of the audit. Don't let "I ran the audit" become the goal itself, or a post-hoc rationalization that launders a conclusion you already held. Running the checklist is not the same as covering the space: box-checking is not coverage, the broader-coverage finding for structured techniques is only *preliminary*, and adversarial moves can backfire — devil's advocacy can *heighten* confidence in the preferred hypothesis rather than puncture it (RAND RR-1408). The JP practitioner critique names the same failure: `shikō teishi` (thought-stopping — the checklist substitutes for thinking) and `keigaika` (the practice ossifies into empty form). Motivation / social note: self-interest, affect (loving your own proposal), and groupthink (Kunda's motivated reasoning; the Kahneman-Lovallo-Sibony 2011 evaluator questions) are mostly **out of scope** for a framework-completeness auditor — flag them only when the analyst has a personal stake in the outcome.
