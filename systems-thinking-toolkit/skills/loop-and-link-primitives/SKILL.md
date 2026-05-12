---
name: loop-and-link-primitives
description: |
  Sign every causal arrow first (S = same direction, O = opposite, with reversibility test → Sterman ultimate-test fallback for irreversible flows), then close the loop and count Os: even-O including zero = reinforcing R, odd-O = balancing B — and the classification is purely structural, so vicious and virtuous spin are the SAME loop with opposite triggers. NOT for one-shot decisions with no feedback; NOT for statistical correlation labeling (no claimed direction of causation); NOT for DAG causal-inference edges (unsigned by construction). Triggers: "is this S or O?", "the sign keeps flipping", "variance direction", "vicious cycle", "death spiral", "boom and bust", "why is X accelerating", "we're stuck in a feedback loop", "is this a bubble?", "you can't have negative [births / shipments]". Keywords: causal loop diagram, S link, O link, reversibility test, Sterman ultimate test, uniflow, stock and flow, variance sign convention, regime-dependent link, reinforcing loop, balancing loop, even-O odd-O rule, vicious circle, virtuous circle, R-loop spin trigger, B-loop target delay, 因果ループ図, S/Oラベル付け, スターマン究極テスト, 強化ループ, 均衡ループ, 因果迴路圖, S/O鏈結符號, Sterman 終極檢定, 強化迴路, 均衡迴路, 惡性循環.
source_book: Seeing the Forest for the Trees — Dennis Sherwood
source_chapter: Chapter 4 + Chapter 5 + Chapter 6 + Chapter 12
source_language: en
tags: [systems-thinking, causal-loop-diagram, feedback, link-sign, sterman, diagnosis]
# Tier-3 #6 reverse-link backfill: this skill is the foundational primitives
# layer; the four entries below are the downstream skills that DEPEND on it
# (relation semantics: "is depended on by these"). The merged 9-skill graph
# per spec §3.5 drops intra-merge edges (sk01↔sk02 collapsed inside this
# skill); the four reverse links retained here are the inter-merge edges
# sk01 was the target of in the original 17-relation graph.
related_skills:
  - slug: cld-craft
    relation: depended-on-by
  - slug: limits-to-growth-take-the-brakes-off
    relation: depended-on-by
  - slug: variance-target-action-template
    relation: depended-on-by
  - slug: stakeholder-and-team-thinking
    relation: depended-on-by
---

# Loop and Link Primitives (S/O Sign Discipline + Even-O / Odd-O Loop Classification)

## R — Reading

> "By changing the definition of variance from BUDGET − ACTUAL to ACTUAL − BUDGET we haven't changed reality … What has changed is the location of the Ss and the Os."
>
> — Dennis Sherwood, Chapter 6

> "The reversibility test is not fail-safe; there are a specific set of conditions … when it doesn't work."
>
> — Dennis Sherwood, Chapter 4

> "All closed loops are either reinforcing or balancing — and the test is simple: count the Os. Even (including zero) is reinforcing; odd is balancing."
>
> — Dennis Sherwood, Chapter 5

> "How can the same diagram behave as both a vicious and a virtuous circle?"
>
> — Dennis Sherwood, Chapter 5 (on c01 back-office case)

## I — Interpretation

This is the **primitives layer** for every causal loop diagram: first sign every link (S/O), then close the loop and count Os. The two halves are operationally inseparable — without honest link-signing, loop classification produces arithmetic nonsense; without loop classification, link-signing is bookkeeping with no dynamic payoff. Present them as one layer.

**Layer 1 — Link signing (S vs O).** Every causal arrow carries a sign: **S** when cause and effect move in the same direction, **O** when they move in opposite directions. Assignment has two tiers.

- **Tier 1: Reversibility shortcut.** Ask "if the cause increased, would the effect increase?" If yes, then "if the cause decreased, would the effect decrease?" Both directions consistent → S; both flip → O. If the answers are asymmetric (cause up moves effect, cause down does not), the shortcut has failed.
- **Tier 2: Sterman's ultimate test (fallback).** Re-phrase: "Holding all else equal, when the cause is *above what it would otherwise have been*, is the effect *above what it would otherwise have been*?" This form survives irreversible flows (pouring-in vs pouring-out), one-way physical processes (BIRTHS → POPULATION; you can't have negative births), and stock-and-flow connections where reversibility returns nonsense.

Two further disciplines: (1) **convention audit** — if you redefine variance as ACTUAL − TARGET instead of TARGET − ACTUAL, three of four S/O labels in a variance loop flip. This is a notation change, not a reality change, but the diagram lies if you forget to flip them. (2) **regime check** — if a link's sign is "depends on regime" (generosity → productivity is S until threshold, then O), do *not* pick one label; hand off to the split-fuzzy-variable trick (see `cld-craft`).

**Layer 2 — Loop classification (R vs B).** Every closed feedback loop falls into exactly one of two types. To classify, walk the loop once and tally the O-links. An **even count (including zero)** makes the loop **reinforcing (R)**: it amplifies in whichever direction it is spinning, producing exponential growth or exponential decline. An **odd count** makes the loop **balancing (B)**: it seeks a target and, under delay, oscillates around it.

The non-obvious half of the methodology: a reinforcing loop's *structure* is identical whether it is currently a virtuous circle (spinning up) or a vicious circle (spinning down). They are not opposites; they are the **same loop with opposite spin**, separable only by an external trigger. The diagnostic question is never "is this loop good or bad" but "which way is it spinning and what could flip it." Slow drift is the early-phase signature of an exponential — not noise, not a lagging indicator. The "frogs and lily-pad" intuition (Ch 5) is the calibration: at day 49 the pond is still half-empty, and the visible drift looks tame.

Two integration claims hold the layers together:

- **The arithmetic theorem (even-O / odd-O) holds *only* if every link is a fixed S or O.** Sherwood himself documents that links flip with regime (ce29). The two-type ontology is not a discovered law of nature; it is a useful diagnostic *given* honest sign discipline at Layer 1. Skip Layer 1 and Layer 2 is structurally meaningless.
- **Words are load-bearing for diagram readability, not for system mechanics — but the labels *must* be re-audited when conventions change.** A variance redefinition (ce27) does not change reality but does flip the diagram's verdict between R and B.

## A1 — Past Application

The three cases that calibrate this primitives layer (UK back-office c01 reinforcing-loop spin-direction, Hatfield Rail c05 reverse-spin reputation R-loop, Ratner Jewelry c06 single-utterance spin trigger) together with the link-signing edge cases (BIRTHS → POPULATION uniflow Sterman fallback, ce27 variance sign convention flip, Lake Chad c25 inflow/outflow uniflow discipline) are detailed in `references/cases.md`.

**MANDATORY — READ ENTIRE FILE**: Before signing a link or classifying a loop, you MUST read [`references/cases.md`](references/cases.md) (~100 lines) for the trigger-vs-structure distinction (R-loops), the uniflow Sterman discipline (BIRTHS → POPULATION, Lake Chad), and the convention-flip audit pattern (ce27).

## A2 — Future Trigger ★

### When will the user need this skill?

**Link-signing triggers (Layer 1)**:

1. Building a CLD from scratch and pausing on each arrow asking "is this S or O?"
2. A variance-based KPI (budget vs actual, target vs forecast) has been re-defined and the team isn't sure whether the existing diagram still holds.
3. A causal claim involves a stock and a flow (inventory, population, capital, debt) where the flow is physically one-directional.
4. An economist or analyst has labeled a link based on observed correlation and the predictions are directionally wrong.
5. Two team members assigned the same link opposite signs and the dispute won't resolve.

**Loop-classification triggers (Layer 2)**:

6. A KPI is drifting slowly down (NPS, retention, error rate, share price) and operational reviews can't explain it.
7. Growth is suddenly accelerating non-linearly and the team is debating whether to "ride it" or "be cautious."
8. A company / portfolio just experienced a sharp reversal after a long run, and stakeholders are asking "what changed structurally?"
9. A team is in a "downward spiral" or "death spiral" and wants to know which lever to pull.
10. A bubble narrative (crypto, AI valuations, real estate) needs diagnosis: is this an R-loop in virtuous spin, and what would flip it?

### Language signals (user phrasings that should activate)

- "is this an S link or an O link?" / "the sign flips depending on..." / "variance is now defined as..."
- "the correlation goes the wrong way" / "this is a one-way flow" / "you can't have negative [births / shipments / hires]"
- "vicious cycle" / "death spiral" / "downward spiral" / "things just keep getting worse / better"
- "why is this accelerating?" / "boom and bust" / "the same story every time" / "is this a bubble?"
- "we're stuck in a feedback loop"

### Distinction from neighboring skills

- vs. `cld-craft` (merged sk03+sk04 — 12 rules + fuzzy elevation): This skill is the *ontological primitive layer*; `cld-craft` is the *drawing workflow* that uses these primitives. Always have a diagram before classifying loops; always have signs before counting Os. If you hit a regime-dependent link, this skill hands off to `cld-craft`'s split-fuzzy-variable trick — do not pick a single label for a flipping link.
- vs. `limits-to-growth-take-the-brakes-off` (sk05): That skill is the specific *two-loop coupling* (R braked by B); this skill identifies single-loop type as the primitive on which sk05 builds. Use this first, then escalate to limits-to-growth when you see an R-loop decelerating.
- vs. `variance-target-action-template` (sk06): That skill is a generic B-loop template; you must recognize B-loops here (odd O-count) before applying it.

## E — Execution

```
E flow:
  one link at a time? ── no → halt; isolate single cause-effect pair
        │ yes
        v
  reversibility test (Tier 1)
        │
        ├── symmetric → label S or O, move to next link
        └── asymmetric / uniflow / nonsense → Sterman ultimate test (Tier 2)
                │
                v
        regime-dependent? ── yes → hand off to cld-craft split-fuzzy trick
                │ no
                v
  all links signed? ── no → repeat
        │ yes
        v
  variance convention audited? ── no → flip labels if direction redefined
        │ yes
        v
  closed loop traced? ── no → not applicable (open chain)
        │ yes
        v
  count Os → R (even / zero) or B (odd)
        │
        ├── R: name current spin + plausible flip-trigger
        └── B: name target dangle + delay magnitude
```

When this skill activates, follow these steps:

1. **Isolate one link at a time.** Treat each arrow independently; do not batch.
   - Completion criterion: a single cause node and effect node are named.

2. **Run the reversibility test (Tier 1) on the isolated link.** Ask: "If the cause increases, does the effect increase?" Then: "If the cause decreases, does the effect decrease?"
   - If both answers point the same way → S. If both point opposite → O. Record the label and proceed.
   - Halt condition: if the answers are asymmetric (one direction works, the other doesn't), jump to step 3.

3. **Run Sterman's ultimate test (Tier 2 fallback).** Rephrase: "Holding all else equal, when the cause is above what it would otherwise have been, is the effect above what it would otherwise have been?" Same direction → S; opposite → O.
   - Completion criterion: a single S or O is committed based on the Sterman form.
   - Halt condition (uniflow): if the link represents an inflow or outflow on a stock-and-flow diagram, the Sterman test is *mandatory* — reversibility is not valid for uniflows. Document "uniflow" alongside the label.

4. **Check for regime-dependence.** Ask: "Is there a value of the cause variable at which the sign of the effect would flip?" (Saturation, threshold, inverted-U.)
   - Halt condition: if yes, do NOT pick a single label — hand off to `cld-craft`'s split-fuzzy-variable trick.
   - Completion criterion: regime-dependence ruled out, or split-trick invoked.

5. **Audit for convention dependence.** If the link involves a variance, gap, or signed difference, confirm which direction the variance is defined (TARGET − ACTUAL or ACTUAL − TARGET). If the convention later changes, every S/O label in the loop must be re-audited (ce27).
   - Completion criterion: variance direction documented next to the diagram; relabel triggers identified. Write labels in pen as you draw — never as a cleanup pass.

6. **Confirm a closed loop exists.** Trace the candidate causal chain back to its origin and verify it returns to a node already visited. If it doesn't close, this is an open chain — use dangle-based boundary discipline (`cld-craft`) instead.
   - Completion criterion: at least one node appears twice on the traced path.

7. **Count O-links around the closed loop.** Even (including zero) → reinforcing (R). Odd → balancing (B).
   - Completion criterion: a single integer count is written next to the loop, with R or B label.

8. **For R-loops: identify current spin direction and name a plausible flip-trigger.** Pick one node; ask "is it currently rising or falling?" Trace forward through the labels — an R-loop in virtuous spin pushes everything up; in vicious spin, everything down. Then look for external dangles (input dangles) or fuzzy thresholds (Ratner-style single utterance, Hatfield-style shock) that could flip it.
   - Completion criterion: each node tagged with current trajectory; at least one named, plausible trigger documented.

9. **For B-loops: locate the target dangle and the delay.** Identify the goal the loop is seeking and the time lag between action and effect. If delay is non-trivial, oscillation is the expected behavior — do not over-react (see `variance-target-action-template`).
   - Completion criterion: target named, delay roughly quantified.

10. **State the dynamic prediction in one sentence.** "This is an R-loop currently spinning virtuous; barring trigger X it will continue to compound at roughly Y% per period." OR "This is a B-loop seeking target T with delay D; expect oscillation of amplitude A."

## B — Boundary ★

### Do NOT use this skill when:

- The system has no closed loop — a one-shot decision with no feedback is not a loop, and even-O/odd-O is undefined.
- The relationship is statistical correlation only, with no claimed direction of causation. CLDs encode causal claims; correlation alone is not a link.
- The "loop" you've drawn is actually a chain that returns by an accounting identity (e.g., revenue − costs = profit, profit → cash → revenue is a definitional flow, not a behavioral causal loop).
- The cause and effect are unrelated (no causal connection) — there should be no link at all, not an S or O label.
- You are working on a DAG for causal-inference / counterfactual estimation. DAG edges are directional but unsigned; S/O is a different vocabulary and does not map cleanly.
- The relationships involved are stochastic noise, not causal: weather, exogenous shocks, regulatory events. These are dangles (see `cld-craft`), not loop members.

### Author-warned failure modes (Sherwood's counter-examples)

- **ce09 — Reversibility test on a one-way flow.** Coffee can only be poured *into* the cup; the reversibility shortcut returns "pouring less coffee in lowers the level," which is nonsense. The cure is the Sterman ultimate test; the cost of skipping it is a wrong label in a load-bearing link.
- **ce27 — Variance sign trap (convention flip).** Same diagram, redefined variance direction, *three of four* labels should flip. Forgetting to flip them turns a B-loop into an R-loop on paper, while the physical system is unchanged — and the prediction will be *exactly* wrong.
- **ce29 — Symmetry assumption / S-to-O flip under saturation.** Most real causal links are non-monotonic. A single S or O label on a link that flips sign at threshold (generosity → productivity inverts when over-generous) silently mis-classifies the whole loop. Run the split-fuzzy-variable trick (`cld-craft`) if regime-dependence is plausible.

### Author's blind spots / period limitations

- **The two-type ontology is partially tautological.** The arithmetic proof (even-O / odd-O) holds *only* if every link is a fixed S or O. Sherwood's fix — split into fuzzy intermediaries — preserves the theorem at the cost of letting modelers escape disconfirming evidence by adding nodes. Don't treat the binary as a discovered law of nature; treat it as a useful diagnostic *given* honest sign discipline.
- **Binary labels hide nonlinearity.** Linear, saturating, threshold, lagged, and hysteretic responses all collapse into one bit of information. For high-stakes decisions, augment loop-type diagnosis with response-curve sketches (see `cld-craft` Rule 7c) before acting.
- **No falsifiability discussion.** Sherwood gives no protocol for empirically testing whether an S label is *wrong* once committed. "A good diagram must be recognized as real" (Rule 10) is social validation, not data validation. Augment with data when the decision is high-stakes.
- **Pre-2008 systemic-contagion blindness.** Sherwood's R-loop examples are within a single firm or relationship. Cross-firm contagion loops (2008 financial crisis, supply-chain cascades) need agent-based or network-of-loops thinking that the book does not provide.
- **2002 vintage** means platform-economy R-loops (network effects, two-sided markets, winner-take-most) and modern causal-inference vocabulary (Pearl's do-calculus, structural causal models) are absent. The S/O craft is compatible with those frameworks but not aligned with them; users moving between communities will need translation.

### Easily-confused neighboring methodologies

- **+/− notation in Sterman's textbook.** Equivalent to S/O but Sherwood prefers S/O specifically to avoid the good/bad connotation that creeps in with +/−. They are notational variants; don't treat them as different methods.
- **Pearl-style DAG edges.** DAGs label *whether* X causes Y but not *direction-of-effect*. Don't expect a DAG to give you an S or O; you still need to do the test.
- **Regression coefficient signs.** A positive β does not establish an S-link in any structural sense; β can flip with confounder set, time horizon, or regime. Treat coefficients as evidence about a link's sign, not as the sign itself.
- **Senge's "fixes that fail" / "shifting the burden" archetypes** look similar to R/B loops but are *named compositions* of R and B loops. This skill is the primitive; the archetypes are the patterns built from it. Don't reach for an archetype name before classifying each loop.
- **Causal DAGs in statistical causal inference** label edges but do not enforce sign-of-effect. Don't import DAG vocabulary expecting it to give you R/B classification — it cannot, by construction.
- **Control-theory feedback** is the engineering cousin of B-loops, but uses transfer functions and frequency-domain reasoning that don't translate to qualitative CLD work.

## Related skills

This skill is **foundational** — it has no prerequisites among the 9 skills.
Four downstream skills `depend-on` this primitives layer (see frontmatter
`related_skills` for the machine-readable list; relation key
`depended-on-by` means "this is the foundational layer those skills
build on"):

- `cld-craft` (the 12 hygiene rules + fuzzy elevation merge) — Rule 8 of
  the 12 rules ("Do the S's and O's as you go along, in pen") and the
  split-fuzzy-variable trick both presuppose this signing competence and
  the R/B classification primitive.
- `limits-to-growth-take-the-brakes-off` — the master archetype is a
  coupling of one R-loop and one B-loop; both must be identifiable here
  first.
- `variance-target-action-template` — the template is a generic B-loop;
  you must recognize B-loops (odd O-count) to apply it.
- `stakeholder-and-team-thinking` — uses the R-loop classification for
  the open-system / self-organization conceptual scaffolding when
  diagnosing team-energy dynamics.

## Audit metadata

> Source-unit codes (f01/f02/f03/f21/f23/p06/p28/p29/p34/ce09/ce27/g10/g11/g12/g13/g14/g19/g20/g23/g24/g26/g45) refer to Stage-1.5 verified.md entries. See `<plugin-root>/references/VERIFIED.md`.

- **Verification status**: V1 ✓ / V2 ✓ / V3 ✓
- **Source units merged**: f01, f02, f03, f21, f23, p06 (partial), p28, p29, p34, ce09, ce27, g10, g11, g12, g13, g14, g19, g20, g23, g24, g26, g45
- **Distilled at**: 2026-05-11
- **Merged at**: 2026-05-12 (Profile B merge: sk01 reinforcing-balancing-loop-diagnosis + sk02 s-o-link-assignment; Tier-3 #6 reverse-link backfill applied)
- **Output language**: body — English; metadata — English
