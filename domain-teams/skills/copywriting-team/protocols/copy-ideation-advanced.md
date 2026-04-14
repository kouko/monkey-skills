# Protocol: Advanced Copy Ideation — Multi-Method + 谷山 Training Fragments + 小霜 Instinct Lens

**When to use**: When the base ideation protocol (`copy-ideation-parallel.md`) needs reinforcement — either the brief is complex enough to warrant multiple ideation methods in parallel, or the copywriter wants to develop candidates through 小霜's instinct-mapping lens and/or SNS-era audience modeling. Also use when 谷山's 31 training exercises are deployed as warm-up or quality-development tools during ideation.

**Relationship to base protocol**: This protocol is an **overlay**, not a replacement. It extends `copy-ideation-parallel.md` at specific injection points (marked below). The base protocol's Phase 1 (diverge) and Phase 2 (converge) structure remains intact.

**Output**: Same as base protocol — 3-5 winning angles with "なぜ良いか" 3-item rationale. The difference is in the richness and diversity of the candidate pool entering Phase 2.

**Grounds on**:
- `../standards/ideation-mandalart.md` — 曼陀羅 divergence (base)
- `../standards/ideation-kj-convergence.md` — KJ convergence (base)
- `../standards/ideation-taniyama-discipline.md` — 散らかす→選ぶ→磨く + なんかいいよね禁止 + 31 training (base + advanced)
- `../standards/verbalized-sampling.md` — VS probability (base)
- `../standards/kosimo-instinct-analysis.md` — 小霜 本能 lens (advanced)
- `../standards/sns-evolution-aisas-ulssas.md` — ULSSAS seed criteria (advanced)
- `../standards/jp-copy-craft-lineage.md` — voice reference calibration (advanced)

## Pre-Phase: Method Selection

Before entering Phase 1, decide which method combination to use. This decision happens AFTER the intake brainstorming protocol (`copywriting-brainstorming.md`) produces the Understanding Summary, and AFTER the Intake Completeness gate passes.

### Decision matrix

| Brief characteristic | Recommended method combination |
|----------------------|-------------------------------|
| Standard short/mid/long copy, clear target, single channel | Base protocol only (`copy-ideation-parallel.md`) — no need for this overlay |
| Complex brief: multi-channel, ambiguous target, or innovative positioning needed | 曼陀羅 + 小霜 instinct lens (dual-axis divergence) |
| SNS-native campaign, UGC-triggering needed | 曼陀羅 + ULSSAS seed criteria overlay |
| Brand voice development, キャッチコピー for cultural campaign | 曼陀羅 + voice lineage calibration (糸井/岩崎/眞木) |
| All of the above, or brief explicitly requests "explore deeply" | Full combination: 曼陀羅 + 小霜 + ULSSAS + voice |

**Default**: if uncertain, use 曼陀羅 + 小霜 instinct lens (dual-axis). This is the most generally applicable advanced combination.

### Decision output

Record the method selection and rationale as metadata. This feeds into the Phase 2 convergence (evaluator needs to know which methods produced which candidates) and into the handoff (downstream protocols need to know the method context).

## Phase 0.5: 谷山 Training Warm-Up (optional)

When the copywriter (or LLM) is starting a session cold, deploy 1-2 of 谷山's 31 training exercises as warm-up before entering Phase 1 divergence. This is especially useful when:
- The ideation session is the first task of the day
- The copywriter has been working on non-creative tasks and needs to re-engage creative disposition
- The brief is in an unfamiliar domain

### Fragment selection

Select from the 31 exercises based on the brief's needs. Exercises are categorized by the muscle they develop:

| Category | Exercises (reference numbers from `ideation-taniyama-discipline.md`) | Best for |
|----------|-------------------------------------------------------------------|----------|
| Volume production | #4 (20 headlines for one product), #9 (dictionary word → 3 headlines in 1 min) | Cold start, building momentum before divergence |
| Target switching | #5 (child / adult / senior variants), #14 (お題 → 10 headlines) | Multi-persona briefs, when the Understanding Summary identifies multiple targets |
| Constraint training | #15 (3字 / 7字 / 15字 variants), #11 (5 word-order permutations) | Short-form briefs with strict character limits |
| Evaluation muscle | #10 (verbalize "why good" in 3 items for existing copy) | Before entering Phase 2 convergence, sharpening the なんかいいよね禁止 gate |
| Cross-domain | #13 (10 headlines for an unfamiliar product), #12 (novel sentence → ad copy) | Unfamiliar domains, breaking habitual-domain thinking |

### Warm-up rules

- Select 1-2 exercises maximum per session (not more — see `ideation-taniyama-discipline.md` §Anti-Patterns on "attempting all 31 at once")
- Warm-up output is discarded — it is NOT fed into Phase 1 candidates
- Time-box: 5-10 minutes (human) or 1 generation pass (LLM)
- The point is dispositional activation, not candidate production

## Phase 1 Extension A: 小霜 Instinct-Lens Divergence

This extension adds an instinct-mapping divergence axis to the base protocol's 曼陀羅-based divergence. The two axes run **in parallel** — they are independent divergence methods producing independent candidate pools that merge before Phase 2 convergence.

### Injection point

Inject after base protocol Phase 1 step 2 (tool combination decision), before step 4 (subagent prompt components). The instinct-lens subagents launch alongside the 曼陀羅 subagents.

### Instinct-mapping process (per `kosimo-instinct-analysis.md`)

1. **USP extraction**: Extract the product's functional USP from the Understanding Summary. What does this product do that no other product does?

2. **Instinct trigger identification**: Identify 3-5 different 無意識 triggers the USP could activate. Do NOT use the secondary-source sub-categories (貢献欲/承認欲/etc.) as a fixed checklist — use the 無意識 vs 意識 framework as a generative process.

   For each trigger, articulate:
   - The 無意識 drive: what instinctive desire does this activate?
   - The ターゲットインサイト: the "I've always felt this but never said it" moment
   - The 自分事化 hook: how the first line makes the reader feel "this is about me"

3. **Instinct-axis subagent dispatch**: Launch 3-5 subagents (one per instinct trigger). Each subagent produces 8 candidates using VS probability (same as base protocol), but the divergence direction comes from the instinct trigger rather than a 曼陀羅 direction.

   Subagent prompt must contain:
   - The instinct trigger description (無意識 drive + ターゲットインサイト)
   - VS template (8 candidates + probability per `verbalized-sampling.md` §Pattern A)
   - 散らかす principle (no self-censorship, 80% safe + 20% unusual)
   - The 一行で関係を作れるか criterion: every candidate must attempt 自分事化 in the first line

4. **Pool merge**: Instinct-axis candidates (24-40) merge with 曼陀羅-axis candidates (64) into a single pool (88-104 total) before Phase 2 convergence. Tag each candidate with its origin axis (曼陀羅 direction or instinct trigger) for convergence labeling.

### Complementary analysis

The two axes are structurally complementary:

| Dimension | 曼陀羅 axis | 小霜 instinct axis |
|-----------|------------|-------------------|
| Divergence source | External direction (topic angle) | Internal drive (instinct trigger) |
| Candidate character | Varies widely in approach and register | Consistently aims at 無意識 activation |
| Strengths | Breadth, unexpected viewpoints, structural variety | Depth, emotional precision, 自分事化 |
| Weaknesses | May produce structurally diverse but emotionally shallow candidates | May produce emotionally deep but structurally similar candidates |

The merged pool compensates each axis's weakness with the other's strength.

## Phase 1 Extension B: ULSSAS Seed Criteria Overlay

When the Understanding Summary identifies the campaign as SNS-native or UGC-triggering, apply this overlay to ALL Phase 1 subagents (both 曼陀羅 and instinct-axis).

### Injection point

Inject into base protocol Phase 1 step 4 (subagent prompt components) as an additional requirement.

### ULSSAS seed criteria (per `sns-evolution-aisas-ulssas.md`)

Add to each subagent prompt:

> In addition to the standard divergence direction, each candidate must be evaluated against ULSSAS seed criteria. A strong ULSSAS-era candidate is:
> - **Quotable**: short enough to be screenshot-shared or quoted in a tweet/post
> - **Opinion-provoking**: triggers "I agree/disagree" responses that generate discussion
> - **Remixable**: contains hooks that users naturally adapt to their own context
> - **Search-surviving**: discoverable in both SNS search and web search
>
> Not all candidates need to satisfy all 4 criteria. Flag which criteria each candidate addresses. Candidates scoring 0/4 are still valid if they serve a non-SNS touchpoint.

### Audience model tagging

Tag each candidate with its assumed audience behavior model:
- AIDMA: for offline / broadcast touchpoints
- AISAS: for search-driven discovery
- SIPS: for empathy-based social engagement
- ULSSAS: for UGC-flywheel contexts

This tagging feeds into Phase 2 convergence — the KJ grouping can use audience model as one of the axes for spatial placement (A-type diagram).

## Phase 1 Extension C: Voice Lineage Calibration

When the Understanding Summary specifies a JP voice reference (糸井 / 岩崎 / 眞木) or when the brief is for a キャッチコピー cultural campaign, use `jp-copy-craft-lineage.md` voice signatures to calibrate candidate generation.

### Injection point

Inject into base protocol Phase 1 step 4 (subagent prompt components) as voice-calibration instructions.

### Voice calibration instructions

For the specified voice master, add to each subagent prompt the relevant voice signature dimensions from `jp-copy-craft-lineage.md`:

- **糸井 reference**: prioritize semantic openness, 日常語の詩化, fragment structures. Suppress explanatory clauses and adjective-heavy phrasing.
- **岩崎 reference**: prioritize concrete-abstract bridges, observational (not emotional) vocabulary, gentle assertion tone. Suppress motivational-poster generics.
- **眞木 reference**: prioritize 同音異義 with product relevance and emotional undertone. Apply the two-gate test (product relevance + emotional content) to every wordplay candidate.

### LLM gap awareness

Include the relevant LLM reproduction gap warning from `jp-copy-craft-lineage.md` in the subagent prompt. The subagent should attempt mitigation strategies during generation, not rely on post-hoc correction.

## Phase 2 Extensions

### Extended KJ labeling (Stage 4)

When candidates come from multiple methods (曼陀羅 + instinct + ULSSAS), the KJ group editing (Stage 3) and labeling (Stage 4) should:

1. Allow cross-method grouping — a 曼陀羅 candidate and an instinct-axis candidate may belong in the same group if they share affinity
2. Note the method origin in each card's metadata (but do NOT use method origin as a pre-classification — "let the chaos speak" per `ideation-kj-convergence.md`)
3. In the A-type diagram (Stage 5), consider using method origin as one spatial axis (e.g., 曼陀羅 ↔ instinct on X axis, rational ↔ emotional on Y axis) — but only if this reveals useful structure

### Extended なんかいいよね禁止 (Stage 6)

For the 3-5 winners, extend the "なぜ良いか" 3-item rationale with method-specific criteria:

| Method context | Additional criterion (4th item, optional) |
|---------------|------------------------------------------|
| 小霜 instinct-axis candidate | Which 無意識 trigger does it activate, and is the ターゲットインサイト recognizable? |
| ULSSAS-overlay candidate | Which ULSSAS seed criteria does it satisfy (quotable / opinion-provoking / remixable / search-surviving)? |
| Voice-calibrated candidate | Does it pass the voice signature check for the specified master? |

The 4th item is supplementary — the core 3 items from `ideation-taniyama-discipline.md` remain mandatory:
1. What is conveyed to whom
2. What is new relative to existing similar copy
3. What resonates in the target's life / context

## Phase 2.5: 谷山 Training as Quality Development (optional)

After Phase 2 convergence produces 3-5 winners but before handoff, deploy 谷山 training exercises as quality-development tools on the winning candidates:

| Exercise | Application |
|----------|------------|
| #15 (3字/7字/15字) | Generate character-count variants of each winner — reveals which length carries the most impact |
| #11 (5 word-order permutations) | Test word-order variations of each winner — surfaces the optimal rhythm |
| #5 (target switching) | Rewrite each winner for 2-3 different target personas — tests whether the angle is robust or persona-dependent |

Rules:
- Apply 1-2 exercises maximum (not all)
- Output is refinement candidates attached to the winners, not new divergence
- Final selection remains with the human / evaluator checkpoint

## Handoff Extensions

The base protocol's Phase 3 handoff is extended with:

1. **Method metadata**: which methods produced which candidates, and the method selection rationale from Pre-Phase
2. **Instinct mapping summary** (if 小霜 extension used): USP → instinct triggers → ターゲットインサイト for each winner
3. **ULSSAS seed scores** (if ULSSAS extension used): which criteria each winner satisfies
4. **Voice calibration notes** (if voice extension used): which master, whether LLM gap mitigation was applied, voice signature adherence assessment
5. **Training exercise results** (if Phase 2.5 used): character-count variants, word-order alternatives, target-switching results

This extended metadata enables downstream protocols (`write-long-form-copy.md`, `write-short-form-copy.md`, etc.) to make more informed structural decisions.

## Rules

- **This protocol is an overlay**, not a standalone. Always use it in conjunction with `copy-ideation-parallel.md`. The base protocol's Phase 1/2 structure, quantity targets (64-100 candidates), and convergence process (KJ + なんかいいよね禁止) are non-negotiable.
- **Method selection must be recorded** as metadata. Do not mix methods without tracking which method produced which candidate.
- **小霜's instinct triggers are generative, not taxonomic**. Do not use the secondary-source sub-categories (貢献欲/承認欲/etc.) as a fixed checklist. Generate triggers from the USP-target intersection.
- **ULSSAS seed criteria are additive, not gatekeeping**. Candidates scoring 0/4 on ULSSAS criteria are still valid for non-SNS touchpoints.
- **Voice calibration is per-piece, not per-candidate**. All candidates in a voice-calibrated session should target the same master. Do not mix 糸井 and 眞木 candidates in the same pool (see `jp-copy-craft-lineage.md` §Anti-Patterns on mixing voices).
- **谷山 training warm-up output is discarded**. Warm-up candidates do NOT enter the Phase 1 pool.
- **Phase 2.5 training exercises refine winners, not diverge new candidates**. Do not use them to reopen divergence.
- **Do not over-extend**. If the brief is simple and the base protocol suffices, do not add extensions for their own sake. Extensions add richness at the cost of pipeline complexity.

## Anti-Patterns

- **Using all extensions on every brief**. Most briefs need 0-1 extensions. Full combination is for genuinely complex, multi-channel, multi-method briefs.
- **Treating 小霜's instinct triggers as a checklist**. The method is generative (find triggers through analysis), not categorical (pick from a list). See `kosimo-instinct-analysis.md` §Anti-Patterns.
- **Applying ULSSAS seed criteria as hard gates**. They are scoring criteria for SNS-native contexts, not universal requirements. Non-SNS copy does not need to be quotable or remixable.
- **Running warm-up exercises as divergence**. Warm-up output is discarded — using it as candidates bypasses the base protocol's systematic divergence.
- **Mixing voice masters within one pool**. 糸井's ambiguity conflicts with 眞木's precision. One voice per ideation session.
- **Skipping the base protocol's quantity target**. Even with instinct-axis candidates added, the total pool should reach 88-104 (64 曼陀羅 + 24-40 instinct). Do not use the instinct axis as an excuse to reduce 曼陀羅 output.
- **Over-applying Phase 2.5 training exercises**. These are refinement tools, not quality gates. 1-2 exercises per session maximum.
- **Omitting method metadata in handoff**. Downstream protocols need to know the ideation context to make structural decisions. A handoff without method metadata looks identical to a base-protocol handoff, losing the advanced ideation's value.
