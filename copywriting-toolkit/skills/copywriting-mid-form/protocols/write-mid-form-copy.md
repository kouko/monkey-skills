<!--
DIVERGED FROM domain-teams:copywriting-team
Original source: domain-teams/skills/copywriting-team/protocols/write-mid-form-copy.md
Changes in copywriting-toolkit:
  - v1.1.0: ADDED §Inline micro-ideation (谷山 stage-level diverge-select rule)
Original content preserved verbatim below. All divergences are additive;
no deletion or re-order of original prose. Search for "v1.1.0 addition"
markers to locate plugin-specific additions.
-->

# Protocol: Write Mid-Form Copy（BEAF Canon mid-form writing）

**When to use**: Mid-form copy requests. Typical cases — product page body text on 楽天市場 / Yahoo!ショッピング / Amazon JP, store POP (supermarket / electronics retailer / bookstore), briefing / exhibition handout, B2B product catalog single-product-page description, EC site product listing summary text. Word count: tens to hundreds of characters (if exceeding 1,000 characters, consider the long-form protocol instead).

**Output**: A mid-form copy artifact structured in BEAF order. 4-stage construction: opening Benefit / second-stage Evidence / third-stage Advantage / final-stage Feature. CTA stage is excluded since the product page purchase button serves as Action.

**Grounds on**: `../standards/mid-form-beaf-canon.md`, `../standards/voice-and-tone.md`, `../standards/persuasion-ethics.md`

## Phase 1: BEAF Skeleton

Follow `mid-form-beaf-canon.md` §BEAF の 4 段階定義 to **decide the 4-stage skeleton first**. Lock each stage's skeleton before writing prose (writing in reverse order invites the Feature-first temptation).

1. **Benefit skeleton**: How does the reader's life improve after purchase? Describe the "achieved state" in one sentence.
   - Example (weak): "容量 500ml で便利" → this is a Feature translation
   - Example (good): "通勤バッグに入れて 1 日分の水分が賄える" → concrete life change
   - Use the "Benefit seed" from `copy-ideation-parallel.md` Phase 3 as starting material.

2. **Evidence skeleton**: Prepare 3+ types of objective backing for the Benefit.
   - Awards / third-party evaluations / customer reviews / clinical tests / inspection results / numerical data
   - Each Evidence must be described in a **verifiable form** (countermeasure against 景品表示法 優良誤認).

3. **Advantage skeleton**: Differentiation from competitors. Unique strengths compared to other products in the same category.
   - Subjective adjectives ("高品質", "最高") are not Advantage.
   - Concrete numbers / technology / certifications are canonical: "他社比 2 倍の~", "業界唯一の○○認証", "独自技術の○○".

4. **Feature skeleton**: Objective baseline specs — specifications, ingredients, dimensions, colors, materials, bundled items. Functions as the spec list.

## Phase 2: Benefit-First Order Verification

BEAF's core canonical claim is "**give the sugar first, give the proof after**" (`mid-form-beaf-canon.md` §Benefit-first 順序の重要性). Once the skeleton is ready, verify the order.

1. **First-stage check**: Confirm the first stage is **always Benefit**. Product pages that open with Feature fail on two points:
   - Readers do not self-translate Feature into Benefit ("500ml" → "1 day's hydration" connection is not made)
   - A Benefit-absent product page becomes "advertising that does not look like advertising" and fails to form purchase motivation

2. **Inter-stage cognitive flow check**:
   - Interest (Benefit) → Conviction (Evidence) → Differentiation (Advantage) → Confirmation (Feature)
   - This order matches the reader's question sequence: "appeal → is it true → what's different from others → what exactly is it"

3. **Word-count distribution guideline**:
   - Tens-of-characters POP: B 60% / E 20% / A 10% / F 10% (Benefit dominates)
   - Hundreds-of-characters product page: B 25% / E 30% / A 25% / F 20% (balanced)
   - If the copy is trending above 1,000 chars, **switch to the long-form protocol** (consider 新 PASONA in `write-long-form-copy.md`).

## Phase 3: Evidence Specificity Verification + Ethics Boundary

The Evidence stage is in the direct impact zone of 景品表示法 (JP) / FTC Endorsement Guides (US). Apply `persuasion-ethics.md` §景品表示法要點 + §FTC Endorsement Guides 要點.

1. **Prohibited expression check**: The following are **empty claims** and do not function as Evidence.
   - "多くの方にご愛用いただいています" (no concrete numbers)
   - "業界最高品質", "世界初", "No.1" (unsupported superlative claims — 景品表示法 優良誤認)
   - "お客様の声：大満足でした" (suspicion of fabricated testimonial)

2. **Verifiability check**: Self-ask for each Evidence:
   - Is there a source a third party can fact-check (award year / organization name / data source)?
   - Is the testimonial from a real customer, and is the result representative (typical)? (FTC §255.2)
   - For comparative superiority claims ("他社比 2 倍"), are the comparison target and measurement conditions stated?

3. **ステマ告示 compliance** (`persuasion-ethics.md` §ステルスマーケティング告示):
   - Testimonials using influencers require explicit "広告" / "PR" / "Sponsored" labeling
   - Product pages with affiliate links require relationship disclosure

4. **打消し表示 guideline** (Consumer Affairs Agency 2017):
   - Is the "※条件あり" disclaimer effectively negating the main claim?
   - Are the disclaimer's font size, color, and background contrast equally readable as the main claim?

## Phase 4: Voice Alignment

Mid-form copy is functional-persuasion-oriented (objective), but voice remains invariant (`voice-and-tone.md` §Voice vs Tone). Maintain brand voice even in product pages / POPs / catalogs.

1. **Voice 4-axis position check** (`voice-and-tone.md` §Voice 定義の 4 軸): Confirm Formality / Seriousness / Respectfulness / Enthusiasm axis positions are consistent across all stages.

2. **Tone is context-dependent and adjustable** (`voice-and-tone.md` §Tone 情境切換表):
   - Product page body → lean matter-of-fact (excessive enthusiasm sounds like hollow hype)
   - POP → lean enthusiastic (impulse-buy oriented)
   - B2B catalog → lean serious / formal

3. **Ogilvy "respect the reader's intelligence"** (`voice-and-tone.md` §Ogilvy 長文案 voice 經典原則):
   - Do not use condescending tone or hollow hype (amazing / revolutionary / game-changing)
   - Every sentence must earn its place (self-ask whether any sentence can be cut)

## Rules

- Always follow BEAF canonical order (B→E→A→F). Feature-first is the top listed violation in `mid-form-beaf-canon.md` §Anti-Patterns.
- Do not implement BEAF in FAB order (US Feature-Advantage-Benefit 3-stage). BEAF is the reverse of FAB + Evidence insertion (`mid-form-beaf-canon.md` §FAB との差異).
- Do not add CTA as a mandatory stage to BEAF. The product page purchase button serves as Action. Adding a CTA stage blurs the boundary with PASONA.
- If trending above 1,000 chars, consider switching to the long-form protocol (`write-long-form-copy.md`). BEAF is canonical in the tens-to-hundreds-of-characters band.
- Use only verifiable information for Evidence. Fabricated testimonials / unsupported superlative claims / false "as seen on" are prohibited (`persuasion-ethics.md` §Copy 層面的具体反模式).
- Do not use subjective adjectives ("高品質", "最高") as Advantage. Replace with concrete numbers / technology / certifications.
- Do not use 打消し表示 to effectively negate the main claim (Consumer Affairs Agency 2017 guideline).

## Anti-Patterns

- **Starting with Feature**: Canonical order violation. A spec list at the top will not stop the reader from scrolling away (`mid-form-beaf-canon.md` §Anti-Patterns).
- **Omitting the Evidence stage**: Benefit alone looks like "advertising exaggeration". Objective backing is indispensable.
- **Implementing BEAF in FAB order**: Swapping the positions of Evidence and Benefit is a canonical violation.
- **Filling Advantage with subjective adjectives**: "高品質", "最高" are not Advantage. Concrete numbers / technology / certifications are canonical.
- **Writing Benefit as Feature translation**: "500ml 入っているので便利" is merely translating a Feature. Concretize to "通勤バッグに入れて 1 日分の水分が賄える".
- **Adding a CTA stage to BEAF**: BEAF itself has no Action stage. The purchase button serves as Action.
- **Using fabricated testimonials / unsupported superlative claims as Evidence**: 景品表示法 優良誤認 / FTC §255.1 §255.2 violation.
- **Using "業界 No.1", "世界初", "最安値" without evidence**: Frequent violation type for 景品表示法 優良誤認 / 有利誤認 (`persuasion-ethics.md` §Anti-Patterns).
- **Wrecking voice with condescending tone / hollow hype**: Ogilvy "respect the reader" violation (`voice-and-tone.md` §Anti-Patterns).


---

<!-- v1.1.0 addition: inline micro-ideation per BEAF stage (copywriting-toolkit specific) -->

## Inline Micro-Ideation (copywriting-toolkit v1.1.0)

Applies regardless of whether Phase 2 ideation produced external candidates. Purpose: enforce 谷山 「なんかいいよね禁止」at stage level.

### Procedure — BEAF (Benefit → Evidence → Advantage → Feature)

For each stage:

1. Produce **3-5 candidate sentences** for the stage content.
2. Apply 谷山 3-reason test per `standards/ideation-taniyama-discipline.md`:
   - Who is this for / what benefit / how it serves the stage goal
   - Why new vs existing similar product-copy in this category
   - Why resonant — specifically addressing the BEAF stage's purpose:
     - B: abstract benefit (Ogilvy reader-state change)
     - E: concrete evidence (numbers / third-party / spec)
     - A: comparative advantage (vs named / implied competitor)
     - F: explicit feature (component / usage / spec)
3. Select 1 winner per stage.
4. Record rejected candidates in `envelope.draft_inline_ideation.rejected[]` with reason-of-rejection.

### Stage-specific discipline

- **B stage — reject any Feature contamination** in candidate selection. Candidates must be pure reader-state / lifestyle-change expressions.
- **E stage — reject any "empty claim"** candidates ("loved by many" / "chosen by" without source). Minimum concrete-information threshold per stage.
- **A stage — reject absolute superlatives** without substantiation per 景表法 §5-1; prefer relative "vs FAB/plain-product" framing.
- **F stage — reject marketing-copy language**; feature stage reads as spec-sheet prose.

### Trigger

ALWAYS runs inside Phase 4 drafting. If `envelope.ideation_depth == "skipped"`, this is the ONLY diverge-select pass — do NOT skip it.

### Why mandatory

Single-candidate BEAF drafting violates 谷山 canon and typically produces FAB-inverted or Feature-contaminated B stages. Inline micro-ideation + 3-reason test catches these at draft-time, before Phase 8 form gate fires them as 🔴.