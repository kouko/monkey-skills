---
name: cld-craft
description: |
  Draw a causal loop diagram with workshop discipline AND elevate unmeasured but load-bearing variables to first-class nodes. Enforces 12 hygiene rules + dangle-based boundary discipline (input / target / rate / output / cloud); when Rule 7 fires on a soft variable (morale, ability to cope, trust, brand strength), names it as a state-noun, sketches a hand-drawn response curve, and splits the link into two parallel S/O intermediates if the sign flips at threshold. NOT a substitute for substantive analysis; NOT a license to evade quantification. Triggers: "draw the CLD", "we made a system map", "the diagram is too cluttered", "where do I stop drawing?", "is this a finished diagram?", "we can't measure it so we can't model it", "soft variable", "you can't manage what you can't measure", "the relationship isn't linear", "too much of a good thing". KEYWORDS: causal loop diagram, CLD, system map, feedback diagram, 12 rules, dangle, boundary discipline, fuzzy variable, soft variable, intangible, non-monotonic, sign flip, response curve, inverted-U, threshold, ability to cope, morale, intellectual capital. JA: 因果ループ図・CLD作成・ファジー変数 / zh-TW: 因果迴路圖・CLD繪製・模糊變數提升。
source_book: Seeing the Forest for the Trees — Dennis Sherwood
source_chapter: Chapter 7, Chapter 4 + Chapter 10 + Chapter 12
source_language: en
tags: [systems-thinking, causal-loop-diagram, workshop, craft, fuzzy-variable, modeling, non-monotonic]
related_skills:
  - slug: loop-and-link-primitives
    relation: depends-on
  - slug: limits-to-growth-take-the-brakes-off
    relation: composes-with
---

# CLD Craft (12 Hygiene Rules + Fuzzy Variable Elevation)

## R — Reading

> "The 12 rules of CLD drawing are not optimization — they are hygiene; the wastepaper basket is the most-used tool."
>
> — Dennis Sherwood, Chapter 7

> "You can if you want to [trace causality forever], but as soon as you start doing this you might never stop. Everything is, quite literally, linked to everything else."
>
> — Dennis Sherwood, Chapter 7

> "If you play safe and capture them all, you are likely to end up with a highly cluttered diagram in which everything really is connected to everything else, largely because everything is included! The forest gets lost in the trees."
>
> — Dennis Sherwood, Chapter 7 (ce21)

> "Causal loop diagrams aren't accounting spreadsheets. I agree that you would not expect to find items such as the ABILITY TO COPE in the budget pack, but, although we rarely talk about such things, they are there, they do drive behavior, and they are important."
>
> — Dennis Sherwood, Chapter 4 (ce12)

> "If you are so generous as to be over the top, wouldn't the staff start taking advantage and slack off?"
>
> — Dennis Sherwood, Chapter 4 (ce29 — the sign-flip insight)

## I — Interpretation

Drawing a CLD is a craft, not a science. Sherwood's twelve rules are **hygiene**, not optimization: they prevent the diagram from becoming useless. The rules cluster into four concerns:

**Boundary discipline** (Rule 1): know what you're drawing about *before* you draw. The operational tool is the **dangle taxonomy** — variables linked to a loop but not inside it. Five dangle types: **input dangles** (external drivers spinning the loop), **target dangles** (set-points for B-loops), **rate dangles** (controls on flow speed), **output dangles** (results that exit the system), and **clouds** (stock-and-flow boundary markers for sources/sinks outside scope). Declaring your dangles up front anchors the scope; new nodes can only enter as new dangles or by replacing existing ones.

**Variable hygiene** (Rules 5, 6): name nodes as **nouns describing states**, not verbs ("ERROR RATE", not "INCREASE IN ERROR RATE" or "CUT COSTS"). Action-named nodes presuppose direction and foreclose analysis of reversal.

**Link hygiene** (Rule 8): label every arrow with S or O *in pen as you draw*, never in a cleanup pass. An unlabeled diagram is not 90% finished; it is structurally meaningless (see `loop-and-link-primitives`).

**Process hygiene** (Rules 4, 10, 11, 12): aggressively suppress detail (Rule 4); the diagram is finished only when stakeholders recognize it as real (Rule 10); avoid falling in love with your own draft (Rule 11); use the wastepaper basket as your primary tool — iteration compresses, not expands (Rule 12).

The synthesizing claim of the 12 rules: holism is descriptive truth, but pragmatism is methodological necessity. The dangle device lets you preserve holism conceptually (everything outside is acknowledged) while bounding the diagram operationally.

**Rule 7 — "Don't be afraid of unusual items" — is the load-bearing rule** that triggers the fuzzy-variable sub-procedure. A **fuzzy variable** is a real, behavior-driving concept that resists measurement (ABILITY TO COPE, STRAIN ON MANAGEMENT, EFFECT OF GENEROSITY ON PRODUCTIVITY, MORALE, BRAND STRENGTH, MARKET SATURATION). The accountant's instinct is to exclude it because "we can't put a number on it." This is the worst available error: the fuzzy variable typically *is* the binding link, and excluding it amounts to modeling around the actual driver of behavior. Sherwood's correction: elevate the fuzzy variable to a first-class node, exactly like any measurable variable. Where helpful, sketch a **hand-drawn response curve** showing how the effect varies with the cause — not because you have data, but because the shape (linear / saturating / threshold / inverted-U) is itself a load-bearing modeling decision.

The **split-fuzzy-variable trick** handles non-monotonic links. When a link's sign reverses with regime (generosity → productivity is S when staff feel respected, O when they feel taken-for-granted), do not pick one label. Split the cause into two parallel pathways: EFFECT OF GENEROSITY IN INCREASING PRODUCTIVITY (S, saturating) and EFFECT OF GENEROSITY IN DEPLETING PRODUCTIVITY (O, threshold-triggered). The net effect emerges from their interaction. This preserves the even-O / odd-O classification while admitting the non-monotonicity — keeping Rule 8 honest by replacing one ambiguous arrow with two cleanly-signed ones.

Two cautions the modern reader must hold firmly: (1) "if you can't measure it, you can't manage it" is a half-truth Sherwood both endorses (p20) and subverts; the resolution is **model the fuzzy variable, accept hand-drawn curves, treat the simulation as learning not forecasting** (see `models-for-learning-not-answers`). (2) The Skandia / Edvinsson precedent (c26) proves that fuzzy stocks — knowledge, intellectual capital — can be operationally reported when the organization commits.

## A1 — Past Application

The cases that calibrate CLD workshop discipline and fuzzy-variable elevation (UK back-office c01, TV "talent problem" three-perspective workshop c15, car-dealership CLD→plumbing translation c24, generosity split-fuzzy trick from Chapter 4 ce29, Skandia intellectual capital c26) are detailed in `references/cases.md`.

**MANDATORY — READ ENTIRE FILE**: Before drawing a CLD or elevating a fuzzy variable, you MUST read [`references/cases.md`](references/cases.md) (~85 lines) for the boundary-discipline-via-dangles pattern, the split-fuzzy-variable trick worked example, and the "fuzzy stock can be operationalized" precedent.

## A2 — Future Trigger ★

### When will the user need this skill?

1. Starting a CLD workshop from scratch and needing structure for the session.
2. Reviewing a CLD someone else drew that "doesn't feel right" but the reasons are diffuse.
3. The diagram has grown past 20–30 nodes and is no longer useful.
4. A draft has been polished for hours and the author is reluctant to revise.
5. A team has drawn the diagram but stakeholders refuse to engage with it ("I see what you mean, but...").
6. A CFO or finance team says "we can't model X because we can't measure it" about a variable that obviously drives behavior (morale, burnout, customer trust, technical debt).
7. A sales-comp / incentive plan is being designed and someone proposes treating effort as monotonically increasing in pay.
8. A model returns directionally wrong predictions because it labeled a regime-dependent link with a single sign.
9. A team is dismissing strategic concepts (brand, culture, employee engagement) from a CLD on the grounds that they are not measurable.
10. An inverted-U or threshold relationship is suspected (workload, pressure, advertising spend, regulation) but the existing diagram has a single S or O.

### Language signals (user phrasings that should activate)

- "draw a CLD" / "build a system map" / "feedback diagram"
- "the diagram is too cluttered / too dense / too complex"
- "where do I stop drawing arrows?"
- "what should I name this node?"
- "is this diagram finished?"
- "the workshop produced a diagram but nothing happened"
- "we can't measure it so we can't model it"
- "soft variable" / "intangible" / "qualitative"
- "you can't manage what you can't measure"
- "the relationship isn't linear" / "it depends on the regime" / "too much of a good thing"
- "morale / culture / trust / engagement"

### Distinction from neighboring skills

- vs. `loop-and-link-primitives`: This skill *produces* the diagram and enforces Rule 8 as a discipline; that skill is the *foundational ontology* (R vs B classification + S/O signing test) without which Rule 8 has nothing to enforce. Use both together — never run loop diagnosis on an unlabeled / unbounded diagram.
- vs. `limits-to-growth-take-the-brakes-off`: That skill is one specific R+B archetype this workflow may surface; this skill is the broader drawing-and-elevation discipline. The archetype recognition happens *after* a clean CLD exists.
- vs. `stock-flow-translation`: Once a fuzzy variable is elevated and a response curve sketched, that skill translates it into the quantitative model. Use this skill first.
- **Internal note on split-fuzzy-variable trick**: a single S/O label per link is the default (see `loop-and-link-primitives`); this skill handles the case where a single label is wrong because the link is non-monotonic — split into two intermediates with different signs.

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
  draw arrows + sign S/O in pen (Rule 8)
        │
        v
  verify closed loops (≥ 1) and iterate via wastepaper basket (Rule 12)
        │
        v
  Rule-10 stakeholder recognition test + final boundary audit
```

When this skill activates, follow these steps:

1. **Declare the purpose of the diagram in one sentence.** What decision will this diagram inform? Without a stated purpose, Rule 4 (suppress detail) has no criterion.
   - Completion criterion: a single-sentence purpose written at the top of the page.

2. **List the dangles before drawing any internal node.** Name input dangles (external drivers), target dangles (set-points for B-loops), and output dangles (results you care about). 3–6 dangles total.
   - Completion criterion: a dangle list exists, with each classified as input / target / rate / output / cloud.
   - Halt condition: if the dangle list exceeds 8, the scope is too wide — return to step 1 and narrow the purpose.

3. **Draft internal nodes as state-nouns only.** Rule 5: nouns, not verbs. Rule 6: no "increase in" or "decrease in" prefixes. Aggregate ruthlessly per Rule 4 — fuzzy variables are allowed and encouraged.
   - Completion criterion: every internal node is a noun describing a state (e.g. ERROR RATE, MORALE, MARKET SHARE).

4. **Rule 7 — elevate unmeasured load-bearing variables.** Identify any variable that obviously drives behavior but resists measurement (morale, ability-to-cope, brand strength, engagement). For each:
   - **7a. Name as a noun on the diagram.** "ABILITY TO COPE", not "coping with workload". No measurement attached yet.
   - **7b. Counter the "can't measure" objection.** Cite Skandia (c26) as precedent. Reframe: refusing to model is the worse error; modeling imperfectly is recoverable. The variable survives stakeholder challenge and remains on the diagram.
   - **7c. Sketch a hand-drawn response curve** between the fuzzy cause and its effect. The shape (linear / saturating / threshold / inverted-U) is the modeling decision, not the numbers. A sketched curve exists with axes labeled; numbers may be absent.
   - Completion criterion: every elevated fuzzy variable is on the diagram as a state-noun with at least a curve-shape declared.

5. **Draw arrows and label each S or O in pen as you go (Rule 8).** Do not finish the topology first and label later. For each link, test for sign-flipping: "Is there a value of the cause at which the sign of the effect would flip?" Saturation, threshold, crowding-out, burnout-by-pressure are common patterns.
   - If sign-flipping: **apply the split-fuzzy-variable trick.** Replace the single link with two parallel intermediate fuzzy variables:
     - "EFFECT OF [cause] IN INCREASING [effect]" — S, saturating curve.
     - "EFFECT OF [cause] IN DEPLETING [effect]" — O, threshold-triggered curve.
     - Both connect from the cause to the effect; each carries a single clean S or O.
   - Completion criterion: zero unlabeled arrows on the page; every ambiguous link replaced by two cleanly-signed pathways.

6. **Verify closed loops exist.** A pure tree of dangles is not a system. At least one closed feedback loop must be present, or the diagram is a chain, not a CLD.
   - Completion criterion: at least one loop closes back on a starting node. With any split-fuzzy intermediates in place, the even-O / odd-O rule from `loop-and-link-primitives` (sk01) applies to the augmented diagram — inverted-U behavior emerges from the *interaction* of S and O sub-paths, not from a single oscillating label.

7. **Iterate against the wastepaper basket (Rule 12).** Throw out the current draft; redraw from memory; compare. Compression should happen, not expansion. Stop adding nodes — the temptation to add is the failure mode (ce20, ce21).
   - Completion criterion: at least one full redraw has occurred.

8. **Test against Rule 10 — show it to stakeholders.** A diagram is finished only when stakeholders recognize it as real. Watch for phrases like "I see what you mean, but I don't see it that way" (ce25) — these signal incomplete mental-model integration, not stakeholder obstinacy.
   - Completion criterion: at least one external stakeholder has confirmed the diagram "looks right" — or you have documented their objection as a new node / link to add in the next iteration.
   - Halt condition: if no stakeholder recognition is achievable, the diagram encodes only your mental model; do not present it as objective.

9. **Final boundary audit.** Walk every node; if its only causal partner is outside the diagram, it should be a dangle, not an internal node. Promote / demote as needed.

10. **Document response-curve shapes as part of the model.** When this CLD is later translated to a stock-and-flow simulation (`stock-flow-translation`), each curve becomes the input function — accept hand-drawn fuzzy inputs and use the model to *learn*, not to forecast (`models-for-learning-not-answers`).

## B — Boundary ★

### Do NOT use this skill when:

- The team needs a *quantitative model* and the qualitative CLD has already served its purpose — at that point, switch to stock-and-flow translation. Continuing to refine the CLD past the point of insight is detail-pornography.
- The system has no feedback at all — a pure event chain or workflow diagram is better drawn as a BPMN / sequence diagram, not a CLD.
- The dispute is fundamentally about values, not causal structure. Two parties disagreeing on "should we maximize growth or sustainability" will not be resolved by a better diagram.
- The variable is *genuinely* irrelevant. Sherwood's discipline is to elevate fuzzy variables when they carry a load-bearing link; not every soft concept belongs in every diagram. Rule 4 (suppress detail) still applies.
- The decision needs a defensible audited number for regulatory / accounting / legal compliance. A hand-drawn response curve does not satisfy SOX, IFRS, or due-diligence standards; use this skill to inform the qualitative model only.
- The "fuzzy" label is being used as a *shield against scrutiny* — to keep a politically inconvenient variable un-falsifiable. A fuzzy variable with no consequence on the diagram should be cut.

### Author-warned failure modes (Sherwood's counter-examples)

- **ce04 — Spreadsheet mentality / looking down-and-in.** Burrowing into the general ledger instead of looking up-and-out for fuzzy drivers. Cure: enforce Rule 4 aggregation and welcome fuzzy variables.
- **ce05 — Macho back-office culture refusing fuzzy variables.** Treating only "hard" measurables as legitimate excludes the actual binding constraint. The fuzzy variable is invisible to the management system and remains the binding bottleneck.
- **ce12 — Accountant bias (fuzzy = not real).** Same failure mode, more polite register: items "not in the budget pack" are excluded. CLDs are not accounting spreadsheets; the test of inclusion is "does it drive behavior?" not "is it on the trial balance?"
- **ce20 — Falling in love with your diagram (Rule 11).** Effort invested → sunk-cost → resistance to revision. Cure: aggressively use the wastepaper basket; accept that *every* CLD will be wrong in some respect.
- **ce21 — Cluttered diagrams (Rule 4).** "Capture everything to be safe" produces a mesh where the forest is lost in the trees. Cure: ruthless aggregation; fuzzy variables hide detail without losing the link.
- **ce23 — Naming variables after actions (Rules 5/6).** "INCREASE IN ERROR RATE" or "CUT COSTS" presupposes directionality. Cure: nouns for state, never verbs for action.
- **ce25 — Diagrams treated as politically neutral (Rule 10).** Author presents the CLD as objective truth; stakeholders disengage politely. Cure: actively elicit each stakeholder's mental model; expect to redraw.
- **ce29 — Symmetry assumption (S-to-O flip under saturation).** A single sign on a regime-dependent link silently mis-classifies the entire loop. Cure: the split-fuzzy-variable trick.
- **ce30 — No-boundary / trace-causality-forever trap (Rule 1).** "Everything is connected to everything else" is descriptive truth and methodological poison. Cure: dangle list up front; promote to dangle anything that would otherwise pull you further out.

### Author's blind spots / period limitations

- **No falsifiability protocol.** Rule 10's "recognized as real" is social validation, not empirical validation. Sherwood also gives no procedure for testing whether a hand-drawn response curve is *wrong*. The curve is a hypothesis; for high-stakes decisions, augment with at least anecdotal calibration data.
- **The opposite failure — fuzzy as a shield.** Sherwood spends much more time on "accountant rejects the fuzzy variable" than on its inverse: fuzzy variables used to dodge scrutiny, sustain unfalsifiable claims, or keep favored variables in the diagram regardless of evidence. Hold *both* failure modes in mind; demand at least a leading indicator before elevating.
- **Split trick as escape hatch.** A modeler under pressure can keep splitting nodes to make the loop classification work; this is a legitimate move but also an escape hatch. Treat the split as a structural admission of non-monotonicity, not as a debugging trick.
- **Consultant-rescue narrative.** Every workshop in the book "works" — a lightbulb goes on, a policy changes. No case where the diagram was correct but politically ignored, or where the consultant's facilitation choices encoded a hidden agenda. Treat your facilitation as authorial; surface your own framing choices.
- **2002 vintage.** No treatment of remote / async workshop drawing (Miro, FigJam), no platform-economy examples, no AI-assisted layout. Modern fuzzy-stock measurement has also matured (engagement surveys, NPS, retention cohort analysis, intangibles under IFRS); the "macho refusal" case is rarer than it was. The craft transfers; the tooling and the rhetorical adversary change.
- **Manager-as-protagonist framing.** Every CLD has a unitary decision-maker. Principal-agent, collective action, and coordination-failure dynamics are not in frame.

### Easily-confused neighboring methodologies

- **Mind maps** look superficially similar but encode association, not causation. A mind map's branches are not S/O links; treating one as a CLD silently fabricates causal structure.
- **Service blueprints / customer journey maps** trace sequence and touchpoints, not feedback. Don't draw CLD arrows on a journey-map artifact — different vocabulary.
- **Senge's "Five Whys" laddering** drills down a causal chain but does not enforce closed-loop discipline. Useful before drawing a CLD, but not a substitute.
- **Soft Systems Methodology (Checkland) rich pictures** are intentionally messy and explicitly subjective. Don't apply the 12 rules to a rich picture — different artifact, different purpose.
- **Mathematical fuzzy logic (Zadeh).** Sherwood's "fuzzy variable" is a vernacular term meaning "real but unquantified." Zadeh's fuzzy set theory is a different beast — membership functions, defuzzification rules. Don't import the math; don't claim the math.
- **Balanced Scorecard (Kaplan & Norton).** BSC operationalizes intangibles via leading indicators within a measurement framework; useful, but its insistence on measurability fights Sherwood's tolerance for fuzzy-but-unmeasured. Either is valid; don't blend without thinking.
- **OKRs.** OKRs *require* measurable Key Results; a fuzzy variable will resist OKR framing. Use this skill at the modeling layer; OKR translation is a separate step.

## Related skills

- **depends-on `loop-and-link-primitives`** — you must know how to distinguish R from B loops (even-O / odd-O) and sign each link (S/O reversibility test + Sterman ultimate-test fallback) before drawing one. Rule 8 ("Do the S's and O's as you go along, in pen") and the split-fuzzy-variable trick both presuppose this signing competence.
- **composes-with `limits-to-growth-take-the-brakes-off`** — when a clean CLD surfaces a reinforcing engine braked by a balancing loop (the master archetype), this skill produced the diagram on which that archetype recognition becomes possible.

## Audit metadata

> Source-unit codes (f04/f06/p07/p20/ce20/ce21/ce29/...) refer to Stage-1.5 verified.md entries. See `<plugin-root>/references/VERIFIED.md`.

- **Verification status**: V1 ✓ / V2 ✓ / V3 ✓
- **Source units merged**: f04, f05, f06, f07, p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p20, p26, ce04, ce05, ce12, ce20, ce21, ce23, ce25, ce29, ce30, g15, g16, g17, g25, g27, g43
- **Distilled at**: 2026-05-11
- **Merged at**: 2026-05-12 (Profile B merge: sk03 cld-drawing-craft-12-rules + sk04 fuzzy-variable-elevation)
- **Output language**: body — English; metadata — English
