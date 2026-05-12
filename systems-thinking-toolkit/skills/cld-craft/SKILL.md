---
name: cld-craft
description: |
  Draw a causal loop diagram (CLD) with workshop discipline AND elevate unmeasured but load-bearing variables (morale, trust, brand strength, ability to cope) to first-class nodes AND classify every closed loop as reinforcing (R, even-O count) or balancing (B, odd-O count) with R-loop spin trigger + B-loop target/delay diagnosis — emits a fully-annotated Mermaid CLD as the deliverable. Enforces 12 hygiene rules + dangle-based boundary discipline (input / target / rate / output / cloud); when Rule 7 fires on a soft variable, names it as a state-noun, sketches a response curve, and splits the link if the sign flips at threshold. Every edge signed S/O via the reversibility test → Sterman ultimate-test fallback for uniflows; vicious and virtuous spin are the SAME R-loop with opposite triggers. NOT for stock-and-flow quantification (use simulation-modeling); NOT for root-cause-of-one-event analysis (use fishbone); NOT a directionless mind-map; NOT for one-shot decisions with no feedback; NOT for statistical correlation without claimed causation; NOT a substitute for substantive analysis; NOT a license to evade quantification when data exists. Triggers: "draw the CLD", "we made a system map", "let's map the system", "how do these connect", "map the dynamics", "this feels like a feedback loop", "the diagram is too cluttered", "where do I stop drawing?", "is this a finished diagram?", "we can't measure it so we can't model it", "soft variable", "you can't manage what you can't measure", "the relationship isn't linear", "too much of a good thing", "is this S or O?", "the sign keeps flipping", "vicious cycle", "death spiral", "boom and bust", "why is X accelerating", "we're stuck in a feedback loop", "is this a bubble?", "you can't have negative [births / shipments]". KEYWORDS: causal loop diagram, CLD, causal map, system map, systems map, feedback diagram, feedback loop, workshop diagram, 12 rules, hygiene rules, wastepaper basket rule, dangle, boundary discipline, cluttered diagram, fuzzy variable, soft variable, intangible, non-monotonic, sign flip, response curve, inverted-U, threshold, ability to cope, morale, intellectual capital, S link, O link, reversibility test, Sterman ultimate test, uniflow, stock and flow, variance sign convention, regime-dependent link, reinforcing loop, balancing loop, even-O odd-O rule, vicious circle, virtuous circle, R-loop spin trigger, B-loop target delay. JA: 因果ループ図・CLD作成・システム図を描く・フィードバックループ図・ファジー変数の昇格・図が散らかる・非線形・S/Oラベル付け・スターマン究極テスト・強化ループ・均衡ループ・悪循環・負のループ・行き詰まり・燃え尽き・モチベーション低下・チーム疲弊・やればやるほど悪化・止まれない / zh-TW: 因果迴路圖・CLD繪製・畫因果圖・迴路圖太亂・模糊變數提升・軟性變數・非線性關係・S/O鏈結符號・Sterman 終極檢定・強化迴路・均衡迴路・惡性循環・做得越多越糟・事倍功半・卡住了・停不下來・下行螺旋・死循環・心不在焉・燒光・職場疲乏・士氣低落・團隊疲乏・做越多越累・撞到天花板.
source_book: Seeing the Forest for the Trees — Dennis Sherwood
source_chapter: Chapter 4 + Chapter 5 + Chapter 6 + Chapter 7 + Chapter 10 + Chapter 12
source_language: en
tags: [systems-thinking, causal-loop-diagram, workshop, craft, fuzzy-variable, modeling, non-monotonic, link-sign, sterman, diagnosis, feedback]
# Tier-3 #6 reverse-link backfill: in v0.4, this skill absorbs the
# foundational `loop-and-link-primitives` (sk01+sk02) into Step 11.
# Per R3-1 / R3-2 restructure, limits-to-growth + variance-target-action
# merged into `cld-archetypes`; stakeholder-and-team-thinking split into
# `cld-overlay` (outward) + `team-mental-model` (inward). All 4 of those
# new skills now depend on this carry-1 foundational skill.
related_skills:
  - slug: cld-archetypes
    relation: composes-with
  - slug: cld-archetypes
    relation: depended-on-by
  - slug: cld-overlay
    relation: depended-on-by
  - slug: team-mental-model
    relation: depended-on-by
---

# CLD Craft (12 Hygiene Rules + Fuzzy Variable Elevation + R/B Loop Classification)

## R — Reading

> "The 12 rules of CLD drawing are not optimization — they are hygiene; the wastepaper basket is the most-used tool."
>
> — Dennis Sherwood, Chapter 7

> "You can if you want to [trace causality forever], but as soon as you start doing this you might never stop. Everything is, quite literally, linked to everything else."
>
> — Dennis Sherwood, Chapter 7

> "Causal loop diagrams aren't accounting spreadsheets … although we rarely talk about such things, they are there, they do drive behavior, and they are important."
>
> — Dennis Sherwood, Chapter 4 (ce12)

> "If you are so generous as to be over the top, wouldn't the staff start taking advantage and slack off?"
>
> — Dennis Sherwood, Chapter 4 (ce29 — the sign-flip insight)

> "All closed loops are either reinforcing or balancing — and the test is simple: count the Os. Even (including zero) is reinforcing; odd is balancing."
>
> — Dennis Sherwood, Chapter 5

> "How can the same diagram behave as both a vicious and a virtuous circle?"
>
> — Dennis Sherwood, Chapter 5 (on c01 back-office case)

> "By changing the definition of variance from BUDGET − ACTUAL to ACTUAL − BUDGET we haven't changed reality … What has changed is the location of the Ss and the Os."
>
> — Dennis Sherwood, Chapter 6 (ce27)

## I — Interpretation

Drawing and classifying a CLD is one craft, not two. Sherwood's twelve rules are **hygiene** that prevent the diagram from becoming useless; the link-signing (S/O) and loop-classification (R/B) primitives are the **dynamics layer** without which a clean diagram has no payoff. v0.4 of this skill absorbs both into one workflow: draw → elevate fuzzies → sign every edge → classify every loop → emit annotated Mermaid.

**Boundary discipline** (Rule 1): know what you're drawing about *before* you draw. The operational tool is the **dangle taxonomy** — variables linked to a loop but not inside it. Five types: **input dangles** (external drivers spinning the loop), **target dangles** (set-points for B-loops), **rate dangles** (controls on flow speed), **output dangles** (results that exit the system), and **clouds** (stock-and-flow boundary markers). Declaring dangles up front anchors the scope; new nodes can only enter as new dangles or by replacing existing ones.

**Variable hygiene** (Rules 5, 6): name nodes as **state nouns**, not verbs ("ERROR RATE", not "INCREASE IN ERROR RATE" or "CUT COSTS"). Action-named nodes presuppose direction and foreclose reversal analysis.

**Link hygiene** (Rule 8): label every arrow with S or O *in pen as you draw*, never in a cleanup pass. An unlabeled diagram is not 90% finished; it is structurally meaningless. Sign every link via the **Tier-1 reversibility test** (cause up → effect up AND cause down → effect down → S; both flip → O); if asymmetric or if the link is a uniflow (BIRTHS → POPULATION, INFLOW → LAKE VOLUME), fall back to the **Tier-2 Sterman ultimate test** ("when the cause is above what it would otherwise have been, is the effect above what it would otherwise have been?"). The full protocol — both tiers, the regime-dependence halt rule, the variance convention audit (ce27), and the per-loop Mermaid annotation format — lives in `references/loop-classification-protocol.md`; read it once before Step 11.

**Process hygiene** (Rules 4, 10, 11, 12): aggressively suppress detail (Rule 4); the diagram is finished only when stakeholders recognize it as real (Rule 10); avoid falling in love with your own draft (Rule 11); use the wastepaper basket — iteration compresses, not expands (Rule 12). Holism is descriptive truth; pragmatism is methodological necessity. The dangle device preserves holism conceptually while bounding the diagram operationally.

**Rule 7 — "Don't be afraid of unusual items" — is the load-bearing rule** that triggers the fuzzy-variable sub-procedure. A **fuzzy variable** is a real, behavior-driving concept that resists measurement (ABILITY TO COPE, MORALE, BRAND STRENGTH, MARKET SATURATION). The accountant's instinct is to exclude it; this is the worst available error because the fuzzy variable typically *is* the binding link. Sherwood's correction: elevate the fuzzy variable to a first-class node, exactly like any measurable variable. Sketch a **hand-drawn response curve** when helpful — not because you have data, but because the shape (linear / saturating / threshold / inverted-U) is itself the modeling decision.

The **split-fuzzy-variable trick** handles non-monotonic links. When a link's sign reverses with regime (generosity → productivity is S when staff feel respected, O when they feel taken-for-granted), do not pick one label. Split the cause into two parallel pathways: EFFECT OF GENEROSITY IN INCREASING PRODUCTIVITY (S, saturating) and EFFECT OF GENEROSITY IN DEPLETING PRODUCTIVITY (O, threshold-triggered). The net effect emerges from their interaction. This preserves the even-O / odd-O classification while admitting the non-monotonicity — keeping Rule 8 honest by replacing one ambiguous arrow with two cleanly-signed ones.

**Loop classification** (Layer 2 of Step 11): every closed feedback loop is either reinforcing or balancing. Walk the loop once and tally the O-links. An **even count (including zero)** → **reinforcing (R)**: amplifies in whichever direction it is spinning; produces exponential growth or decline. An **odd count** → **balancing (B)**: seeks a target and, under delay, oscillates. The non-obvious half: a reinforcing loop's *structure* is identical whether currently virtuous (spinning up) or vicious (spinning down). They are the **same loop with opposite spin**, separable only by an external trigger. The diagnostic question is never "is this loop good or bad" but "which way is it spinning and what could flip it." Slow drift is the early-phase signature of an exponential — not noise. The "frogs and lily-pad" intuition (Ch 5) is the calibration: at day 49 the pond is still half-empty.

Two cautions the modern reader must hold: (1) "if you can't measure it, you can't manage it" is a half-truth Sherwood both endorses and subverts; the resolution is **model the fuzzy variable, accept hand-drawn curves, treat the simulation as learning not forecasting**. (2) The arithmetic theorem holds *only* if every link is a fixed S or O — if regime-dependence is unresolved, the count is meaningless. Split-trick first, classify second.

## A1 — Past Application

The ten cases that calibrate the full draw-classify-emit workflow are detailed in `references/cases.md`:

- **Workshop discipline + R-loop spin** — UK back-office c01 (read twice: drawing AND R-loop classification on same diagram).
- **Workshop discipline** — TV "talent problem" c15 (three-perspective), car dealership c24 (CLD → plumbing translation).
- **Fuzzy elevation** — generosity split-trick ce29, Skandia intellectual capital c26.
- **R-loop trigger naming** — Hatfield Rail c05 (external shock), Ratner Jewelry c06 (single utterance).
- **S/O signing edge cases** — BIRTHS → POPULATION uniflow (Tier 1 → Tier 2 escalation), ce27 variance convention flip, Lake Chad c25 (inflow/outflow uniflow).

**MANDATORY — READ INDEX FIRST**: Before drawing a CLD, elevating a fuzzy variable, or classifying any loop, you MUST read [`references/cases-index.md`](references/cases-index.md) (~40 lines) which maps user-prose symptoms to the matching case in `cases.md`. Load the specific case section(s) from [`references/cases.md`](references/cases.md) on demand by symptom. **For high-stakes diagrams** (legal / financial / public-policy / regulatory) **or first-time use of the split-trick or variance audit**, read `cases.md` end-to-end — the interactions between cases (split-trick × variance audit, Hatfield-style trigger × Skandia-style fuzzy elevation) are themselves load-bearing.

## A2 — Future Trigger ★

### When will the user need this skill?

1. Starting a CLD workshop from scratch and needing structure for the session.
2. Reviewing a CLD someone else drew that "doesn't feel right" but reasons are diffuse.
3. The diagram has grown past 20–30 nodes and is no longer useful.
4. A draft has been polished for hours; the author is reluctant to revise.
5. Stakeholders refuse to engage with the team's diagram.
6. A CFO / finance team says "we can't model X because we can't measure it" about an obviously behavior-driving variable (morale, burnout, customer trust, technical debt).
7. A sales-comp / incentive plan treats effort as monotonically increasing in pay.
8. A model returns directionally wrong predictions because a regime-dependent link was labeled with a single sign.
9. An inverted-U or threshold relationship is suspected (workload, pressure, advertising spend, regulation) but the diagram has a single S or O.
10. Pausing on each arrow asking "is this S or O?" while building a CLD.
11. A variance-based KPI has been re-defined and the diagram may no longer hold.
12. A causal claim involves a stock and a one-directional flow.
13. A KPI is drifting slowly (NPS, retention, error rate) and operational reviews can't explain it.
14. Growth is suddenly accelerating non-linearly; the team is debating "ride it" vs "be cautious."
15. A sharp reversal after a long run; stakeholders ask "what changed structurally?"
16. A bubble narrative (crypto, AI valuations, real estate) needs diagnosis: R-loop in virtuous spin, what would flip it?

### Language signals (user phrasings that should activate)

- Drawing: "draw a CLD" / "build a system map" / "the diagram is too cluttered" / "where do I stop drawing?" / "is this diagram finished?" / "the workshop produced a diagram but nothing happened"
- Fuzzy elevation: "we can't measure it so we can't model it" / "soft variable" / "intangible" / "you can't manage what you can't measure" / "the relationship isn't linear" / "too much of a good thing" / "morale / culture / trust / engagement"
- S/O signing: "is this an S link or an O link?" / "the sign flips depending on..." / "variance is now defined as..." / "the correlation goes the wrong way" / "this is a one-way flow" / "you can't have negative [births / shipments / hires]"
- R/B classification: "vicious cycle" / "death spiral" / "downward spiral" / "why is this accelerating?" / "boom and bust" / "is this a bubble?" / "we're stuck in a feedback loop"

### Distinction from neighboring skills

- vs. `limits-to-growth-take-the-brakes-off`: That skill is one specific R+B archetype this workflow may surface; this skill is the broader drawing + signing + classifying discipline. Archetype recognition happens *after* a clean classified CLD exists.
- vs. `stock-flow-translation`: Once a fuzzy variable is elevated and a response curve sketched, that skill translates it into the quantitative model. Use this skill first.
- vs. `variance-target-action-template`: That skill is a generic B-loop template; you must recognize B-loops here (odd O-count at Step 11) before applying it.
- **Internal note on split-fuzzy-variable trick**: a single S/O label per link is the default; this skill handles the case where a single label is wrong because the link is non-monotonic — split into two intermediates with different signs.

## E — Execution

```
E flow:
  have variables to wire? ── no → exit (no CLD to draw)
        │ yes
        v
  declare purpose + dangle list (Rules 1, 4)
        │
        v
  name nodes as state-nouns (Rules 5, 6)
        │
        v
  any unmeasured but load-bearing variable?
        │
        ├── no → continue
        └── yes → Rule 7a/7b/7c sub-procedure (fuzzy elevation + curve + split-if-sign-flips)
        │
        v
  draw arrows + sign S/O in pen (Rule 8 + Tier-1 reversibility / Tier-2 Sterman)
        │
        v
  verify closed loops (≥ 1) and iterate via wastepaper basket (Rule 12)
        │
        v
  Rule-10 stakeholder recognition test + final boundary audit
        │
        v
  Step 11 — Emit fully-annotated Mermaid CLD with R/B classification + dynamic prediction
```

**MANDATORY — READ BOTH FILES before executing Step 11**:

- [`references/loop-classification-protocol.md`](references/loop-classification-protocol.md) (~400 lines) — Tier-1 reversibility test, Tier-2 Sterman ultimate test, regime-dependence halt rule, variance convention audit (ce27), R-loop spin-direction + flip-trigger naming, B-loop target + delay protocol, per-loop `%%` annotation format, halt conditions.
- [`references/cld-mermaid-emit.md`](references/cld-mermaid-emit.md) (~200 lines) — CLD-specific Mermaid emission convention: S/O edge labels, R/B `%%` annotation, dangle node shapes, R/B color theme, worked prose→CLD example.

Both files are non-optional reading. Every Mermaid block this skill produces must conform to both.

### Language handling policy

When the user input is non-English (Traditional Chinese / Japanese / other):

- **Mermaid node names**: use **English state-nouns** (ASCII; no spaces in node IDs). Downstream `cld-archetypes` / `cld-overlay` / `simulation-modeling` pattern-match against Sherwood's English vocabulary; Chinese / Japanese node names risk silent classification failure.
- **Markdown caption + loop diagnosis + dynamic-prediction sentences**: **match the user's input language**. The user is the audience; preserve their cognitive frame. JA / zh-TW captions are first-class deliverables, not afterthoughts.
- **Loop labels (R / B)**: stay as method-canonical **English single letters** inside the Mermaid block. The caption may use native terms (強化 / 均衡 / 強化型 / バランス型) with R/B in parentheses for cross-reference.
- **S / O edge labels**: stay as **single English capitals**. Method notation, not content.
- **Reversibility test** (Step 5): run the test in the user's language for the user-facing explanation (see `references/loop-classification-protocol.md` Tier 1 zh-TW / JA phrasings). Internal classification anchors to English.
- **Behavioral signature line** (caption first line): use English templates (`deceleration toward asymptote` / `oscillation around target` / `monotone divergence` / `stable`) so downstream `cld-archetypes` Step-0 router fires reliably. Add native-language gloss after if helpful.

**Rule of thumb**: content matches user; method notation stays English. This keeps the downstream contract honest (every consumer expects English nodes + English R/B/S/O) while honoring the user's input language for everything they will read. See the zh-TW worked example in `references/cld-mermaid-emit.md`.

When this skill activates, follow these steps:

1. **Declare the purpose of the diagram in one sentence.** What decision will this diagram inform? Without a stated purpose, Rule 4 (suppress detail) has no criterion.
   - Completion criterion: a single-sentence purpose written at the top of the page.

2. **List the dangles before drawing any internal node.** Name input dangles (external drivers), target dangles (set-points for B-loops), and output dangles (results you care about). 3–6 dangles total for a narrow scope; more is expected for a wide one.
   - Completion criterion: a dangle list exists, with each classified as input / target / rate / output / cloud.
   - Halt condition: the dangle list exceeds 8 **AND** the stated purpose is narrow (single decision / single team / single quarter / single product line). In that case the scope is too wide for the diagram's purpose — return to step 1 and narrow the purpose, or accept a wider purpose. For genuinely wide scopes (cross-functional, multi-year, institutional-level, regulatory-system-level), 8+ dangles is expected and is *not* a halt signal — proceed, and let Rule 4 (aggressive aggregation of internal nodes) carry the simplification load instead.

3. **Draft internal nodes as state-nouns only.** Rule 5: nouns, not verbs. Rule 6: no "increase in" or "decrease in" prefixes. Aggregate ruthlessly per Rule 4 — fuzzy variables are allowed and encouraged.
   - Completion criterion: every internal node is a noun describing a state (e.g. ERROR RATE, MORALE, MARKET SHARE).

4. **Rule 7 — elevate unmeasured load-bearing variables.** Identify any variable that obviously drives behavior but resists measurement (morale, ability-to-cope, brand strength, engagement). For each:
   - **7a. Name as a noun on the diagram.** "ABILITY TO COPE", not "coping with workload". No measurement attached yet.
   - **7b. Counter the "can't measure" objection.** Cite Skandia (c26) as precedent. Reframe: refusing to model is the worse error; modeling imperfectly is recoverable.
   - **7c. Sketch a hand-drawn response curve** between the fuzzy cause and its effect. The shape (linear / saturating / threshold / inverted-U) is the modeling decision, not the numbers. A sketched curve exists with axes labeled; numbers may be absent.
   - Completion criterion: every elevated fuzzy variable is on the diagram as a state-noun with at least a curve-shape declared.

5. **Draw arrows and label each S or O in pen as you go (Rule 8).** Apply the Tier-1 reversibility test (cause up → effect up AND cause down → effect down → S; both flip → O) per link. If Tier 1 returns asymmetric answers, or the link is a uniflow (inflow / outflow / one-way physical process), fall back to the Tier-2 Sterman ultimate test (full protocol in `references/loop-classification-protocol.md`). For each link, also test for sign-flipping: "Is there a value of the cause at which the sign of the effect would flip?" Saturation, threshold, crowding-out, burnout-by-pressure are common patterns.
   - If sign-flipping: **apply the split-fuzzy-variable trick.** Replace the single link with two parallel intermediate fuzzy variables:
     - "EFFECT OF [cause] IN INCREASING [effect]" — S, saturating curve.
     - "EFFECT OF [cause] IN DEPLETING [effect]" — O, threshold-triggered curve.
     - Both connect from the cause to the effect; each carries a single clean S or O.
   - If the diagram contains any variance / signed-difference node, document the variance direction (TARGET − ACTUAL vs ACTUAL − TARGET) — if the convention later changes, all S/O labels in the variance loop must be re-audited (ce27).
   - Completion criterion: zero unlabeled arrows on the page; every ambiguous link replaced by two cleanly-signed pathways; every uniflow flagged "uniflow"; variance convention documented if applicable.

6. **Verify closed loops exist.** A pure tree of dangles is not a system. At least one closed feedback loop must be present, or the diagram is a chain, not a CLD.
   - Completion criterion: at least one loop closes back on a starting node.

7. **Iterate against the wastepaper basket (Rule 12).** Throw out the current draft; redraw from memory; compare. Compression should happen, not expansion. Stop adding nodes — the temptation to add is the failure mode (ce20, ce21).
   - Completion criterion: at least one full redraw has occurred.

8. **Test against Rule 10 — show it to stakeholders.** A diagram is finished only when stakeholders recognize it as real. Watch for phrases like "I see what you mean, but I don't see it that way" (ce25) — these signal incomplete mental-model integration, not stakeholder obstinacy.
   - Completion criterion: at least one external stakeholder has confirmed the diagram "looks right" — or you have documented their objection as a new node / link to add in the next iteration.
   - Halt condition: if no stakeholder recognition is achievable, the diagram encodes only your mental model; do not present it as objective.

9. **Final boundary audit.** Walk every node; if its only causal partner is outside the diagram, it should be a dangle, not an internal node. Promote / demote as needed.

10. **Document response-curve shapes as part of the model.** When this CLD is later translated to a stock-and-flow simulation (`stock-flow-translation`), each curve becomes the input function — accept hand-drawn fuzzy inputs and use the model to *learn*, not to forecast (`models-for-learning-not-answers`).

11. **Emit the fully-annotated Mermaid CLD with R/B classification and dynamic prediction.** Required deliverable. Run the full protocol in [`references/loop-classification-protocol.md`](references/loop-classification-protocol.md):

    - **11a. Classify every closed loop.** Trace each and count O-links. Even (incl. zero) → R. Odd → B. The arithmetic is meaningful only if every link is a fixed S or O — if any regime-dependent link wasn't split in Step 5, return to Step 5.
    - **11b. For each R-loop: name spin + flip-trigger.** Tag each node with current trajectory (↑/↓). Identify a plausible flip-trigger from input dangles, fuzzy thresholds, single-event shocks (Hatfield c05), or single-utterance signals (Ratner c06).
    - **11c. For each B-loop: name target + delay.** Identify target dangle, delay magnitude (short / medium / long), amplitude (small / moderate / large).
    - **11d. Write one dynamic-prediction sentence per loop.** R: "Currently spinning [virtuous/vicious]; barring trigger [X] it will compound at roughly [Y]% per period." B: "Seeking target [T] with delay [D]; expect oscillation of amplitude [A]."
    - **11e. Emit the Mermaid block** per `references/cld-mermaid-emit.md`: `flowchart LR` preferred; every edge `|S|` or `|O|` (capital, single-letter); dangle shapes (`([...])` input, `{{...}}` target, `[/...\]` rate, `((...))` output, `>...]` cloud); R-loop warm palette (`fill:#fff4e6,stroke:#e67700`), B-loop cool palette (`fill:#e3fafc,stroke:#0c8599`), dangles gray.
    - **11f. Annotate every closed loop with `%%`** per `loop-classification-protocol.md`:
      - R: `%% R-loop (<spin>): <path> — O-count = <N> → reinforcing`
      - B: `%% B-loop: <path> — O-count = <N> → balancing; Target is <target dangle>`
      - Coupling: `%% Loop coupling: limits-to-growth archetype — R-loop spinning <spin> braked by B-loop on <braking node>`
    - **11g. Append a Markdown caption below the block** repeating R/B classification + O-count + dynamic prediction (renderers may strip `%%`; the caption guarantees downstream readers see the diagnosis).
    - Completion criterion: self-contained Mermaid + caption; every loop annotated; every R-loop tagged with spin + flip-trigger; every B-loop tagged with target + delay; one prediction sentence per loop. Downstream `limits-to-growth-take-the-brakes-off`, `variance-target-action-template`, `stakeholder-and-team-thinking` consume this directly.

## B — Boundary ★

### Do NOT use this skill when:

- The team needs a *quantitative model* and the qualitative CLD has already served its purpose — switch to stock-and-flow translation. Continuing past the point of insight is detail-pornography.
- The system has no feedback — a pure event chain / workflow is better drawn as BPMN / sequence diagram. A one-shot decision with no closed loop has no R/B classification.
- The relationship is statistical correlation only, with no claimed direction of causation. CLDs encode causal claims; correlation is not a link.
- The "loop" is actually a definitional identity (revenue − costs = profit, profit → cash → revenue), not a behavioral causal loop.
- The dispute is fundamentally about values, not causal structure (e.g. "growth vs sustainability"). A better diagram will not resolve it.
- The variable is *genuinely* irrelevant. Not every soft concept belongs in every diagram (Rule 4 still applies).
- The decision needs a defensible audited number for regulatory / accounting / legal compliance. Hand-drawn response curves don't satisfy SOX / IFRS / due-diligence.
- The "fuzzy" label is being used as a *shield against scrutiny* to keep an inconvenient variable un-falsifiable. A fuzzy variable with no consequence on the diagram should be cut.
- You are working on a DAG for causal-inference. DAG edges are directional but unsigned; S/O does not map cleanly.

### Author-warned failure modes (Sherwood's counter-examples)

- **ce04 — Spreadsheet mentality.** Looking down-and-in at the general ledger instead of up-and-out for fuzzy drivers. Cure: Rule 4 aggregation + welcome fuzzy variables.
- **ce05 — Macho back-office culture refusing fuzzy variables.** Only "hard" measurables get in; the actual binding constraint is excluded.
- **ce09 — Reversibility test on a uniflow.** "Pouring less coffee lowers the level" is nonsense. Cure: Tier-2 Sterman test (mandatory on uniflows).
- **ce12 — Accountant bias.** "Not in the budget pack → not real." Test of inclusion is "does it drive behavior?", not "is it on the trial balance?"
- **ce20 — Falling in love with your diagram (Rule 11).** Sunk-cost → revision resistance. Cure: wastepaper basket.
- **ce21 — Cluttered diagrams (Rule 4).** Capture-everything produces a mesh where the forest is lost in the trees. Cure: ruthless aggregation; fuzzy variables hide detail without losing the link.
- **ce23 — Verb-named variables (Rules 5/6).** "INCREASE IN ERROR RATE" / "CUT COSTS" presupposes directionality. Cure: state-nouns only.
- **ce25 — Politically-neutral diagram (Rule 10).** Author presents the CLD as objective; stakeholders disengage. Cure: actively elicit each mental model; expect to redraw.
- **ce27 — Variance sign trap.** Redefined variance direction flips three of four labels. Forgetting → B-loop misread as R while physical system unchanged. Cure: variance convention audit at Step 5.
- **ce29 — Symmetry assumption.** Single sign on a regime-dependent link silently mis-classifies the loop. Cure: split-fuzzy-variable trick.
- **ce30 — Trace-causality-forever trap (Rule 1).** "Everything is connected to everything else" is methodological poison. Cure: dangle list up front.

### Author's blind spots / period limitations

- **No falsifiability protocol.** Rule 10's "recognized as real" is social validation, not empirical. Sherwood gives no procedure for testing whether a hand-drawn response curve or a committed S/O label is *empirically wrong*. Augment with calibration data for high-stakes decisions.
- **Two-type ontology partially tautological.** The arithmetic proof holds only if every link is a fixed S or O. The split-into-intermediaries fix preserves the theorem at the cost of letting modelers escape disconfirming evidence by adding nodes. Useful diagnostic *given* honest sign discipline, not a discovered law of nature.
- **Binary labels hide nonlinearity.** Linear, saturating, threshold, lagged, and hysteretic responses collapse into one bit (S or O). Augment with response-curve sketches (Rule 7c) for high-stakes decisions.
- **Fuzzy as a shield.** Sherwood treats the "accountant rejects fuzzy" failure heavily but says little about its inverse — fuzzy variables used to dodge scrutiny. Hold *both* failure modes in mind; demand at least a leading indicator before elevating.
- **Split trick as escape hatch.** A modeler under pressure can keep splitting nodes to make classification work. Treat the split as structural admission of non-monotonicity, not a debugging trick.
- **Consultant-rescue narrative.** Every workshop in the book "works." No case where the diagram was correct but politically ignored. Surface your own facilitation choices as authorial.
- **Pre-2008 systemic-contagion blindness.** R-loop examples are within a single firm. Cross-firm contagion (2008 crisis, supply-chain cascades) needs agent-based / network-of-loops thinking not provided here.
- **2002 vintage.** No remote / async workshop tooling (Miro, FigJam), no platform-economy R-loops (network effects, two-sided markets), no AI-assisted layout. Modern fuzzy-stock measurement has matured (NPS, retention cohort analysis, intangibles under IFRS); the "macho refusal" case is rarer.
- **Manager-as-protagonist framing.** Unitary decision-maker assumed. Principal-agent, collective action, coordination-failure dynamics out of frame.

### Easily-confused neighboring methodologies

- **Mind maps** encode association, not causation. Branches are not S/O links; treating one as a CLD silently fabricates causal structure.
- **Service blueprints / customer journey maps** trace sequence and touchpoints, not feedback. Don't draw CLD arrows on a journey-map artifact.
- **Senge's "Five Whys"** drills down a causal chain but does not enforce closed-loop discipline. Useful before a CLD, not a substitute.
- **Soft Systems Methodology rich pictures (Checkland)** are intentionally messy and subjective. Don't apply the 12 rules to one — different artifact, different purpose.
- **Mathematical fuzzy logic (Zadeh).** Sherwood's "fuzzy variable" means "real but unquantified." Zadeh's fuzzy set theory is membership functions and defuzzification — different beast. Don't import the math.
- **Balanced Scorecard / OKRs.** Both insist on measurability; they fight Sherwood's tolerance for fuzzy-but-unmeasured. Use this skill at the modeling layer; BSC / OKR translation is a separate step.
- **+/− notation in Sterman's textbook.** Equivalent to S/O; Sherwood prefers S/O to avoid the good/bad connotation. Notational variants only.
- **Pearl-style DAG edges.** Label *whether* X causes Y, not *direction-of-effect*. Don't expect a DAG to give you S/O; you still need to do the test.
- **Regression coefficient signs.** A positive β does not establish an S-link structurally; β flips with confounder set / regime. Coefficients are evidence about a link's sign, not the sign itself.
- **Senge's "fixes that fail" / "shifting the burden"** archetypes are *named compositions* of R and B loops. R / B are the primitives; archetypes are patterns built from them. Don't reach for an archetype name before classifying each loop.
- **Control-theory feedback** is the engineering cousin of B-loops but uses transfer functions / frequency-domain reasoning that don't translate to qualitative CLD work.

## Related skills

In v0.4 this skill **absorbs** the foundational `loop-and-link-primitives` (sk01 + sk02) as Step 11 of the workflow — drawing and classifying are now one invocation, not two. The three skills below build on this consolidated primitives layer:

- **composes-with `limits-to-growth-take-the-brakes-off`** — when a clean classified CLD surfaces an R-loop braked by a B-loop (the master archetype), this skill produced the diagram on which that archetype recognition becomes possible. The Step-11 loop coupling `%%` annotation is the explicit hand-off.
- **depended-on-by `limits-to-growth-take-the-brakes-off`** — the master archetype is a coupling of one R-loop and one B-loop; both must be identifiable here first.
- **depended-on-by `variance-target-action-template`** — the template is a generic B-loop; you must recognize B-loops (odd O-count) at Step 11 before applying it.
- **depended-on-by `stakeholder-and-team-thinking`** — uses the R-loop classification for the open-system / self-organization conceptual scaffolding when diagnosing team-energy dynamics.

## Audit metadata

> Source-unit codes (f01-f07/p01-p34/ce04-ce30/g10-g45/...) refer to Stage-1.5 verified.md entries. See `<plugin-root>/references/VERIFIED.md`.

- **Verification status**: V1 ✓ / V2 ✓ / V3 ✓
- **Source units merged** (sk03 + sk04 + sk01 + sk02 absorbed at v0.4): f01, f02, f03, f04, f05, f06, f07, f21, f23, p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p20, p26, p28, p29, p34, ce04, ce05, ce09, ce12, ce20, ce21, ce23, ce25, ce27, ce29, ce30, g10, g11, g12, g13, g14, g15, g16, g17, g19, g20, g23, g24, g25, g26, g27, g43, g45
- **Distilled at**: 2026-05-11
- **Merged at**: 2026-05-12 (Profile B merge: sk03 cld-drawing-craft-12-rules + sk04 fuzzy-variable-elevation); 2026-05-12 (v0.4 absorb: sk01 reinforcing-balancing-loop-diagnosis + sk02 s-o-link-assignment moved from standalone `loop-and-link-primitives` into Step 11 + `references/loop-classification-protocol.md`)
- **Output language**: body — English; metadata — English
