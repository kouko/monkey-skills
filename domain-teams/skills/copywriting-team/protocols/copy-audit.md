# Protocol: Copy Audit (existing copy review / improvement / A/B variant proposals)

**When to use**: When the user requests review / improvement proposals / A/B variant generation for existing copy. Typical cases — competitor ad performance diagnosis, in-house LP CVR improvement, existing キャッチコピー renewal, ethics inspection for 景品表示法 / FTC compliance, full copy audit upon brand voice refresh. Writing protocols (write-long / mid / short-form-copy) handle **new generation**; this protocol handles **evaluation of existing artifacts**.

**Output**: Audit report (issues + improvement proposals + optional rewrite variants). Issues sorted by severity, improvement proposals include concrete rewrite examples, variants are attached as 2-3 options only on user request.

**Grounds on**: Standards are dynamically referenced based on the copy's form type.
- Long-form: `../standards/long-form-pasona-canon.md`, `../standards/persuasion-psychology-anchor.md`
- Mid-form: `../standards/mid-form-beaf-canon.md`
- Short-form: `../standards/short-form-catchcopy-canon.md`, `../standards/ideation-taniyama-discipline.md`
- Common: `../standards/voice-and-tone.md`, `../standards/persuasion-ethics.md`

## Phase 1: Type Identification

Identify the existing copy's structure and dynamically determine the applicable standards.

1. **Primary judgment by word-count band**:
   - 7-15 chars → short-form (キャッチコピー)
   - Tens to hundreds of chars → mid-form (product page / POP)
   - 1,500+ chars → long-form (LP / sales letter)
   - Boundary values (500-1,500 chars) are determined by medium (LP → long-form category, product page → mid-form category).

2. **Framework identification**:
   - **PASONA series**: Is there a Problem → Agitation/Affinity → Solution → ... stage structure?
     - 5 stages (P/A/So/N/A) → 旧 PASONA
     - 6 stages (P/A/S/O/N/A, Affinity entry) → 新 PASONA
     - 9 stages (P/A/S/B/E/C/O/N/A) → PASBECONA
   - **BEAF**: Is there a Benefit-first → Evidence → Advantage → Feature order?
   - **キャッチコピー**: Standalone 7-15 char sentence. One of 5 approaches (利益 / 恐怖 / 顛覆 / 目標呼喚 / 提問)
   - **No framework**: If no structure is identifiable, record as "frame-less"

3. **Voice lineage identification** (for short-form): Does the copy show any lineage characteristics of 糸井 / 岩崎 / 眞木 / 谷山, or does it lean Anglo headline tradition, or no voice?

4. **Record**: Note type / framework / voice lineage / medium / word count as meta-description at the top of the draft.

## Phase 2: Diagnosis

Apply standard diagnostic items based on the identification results and enumerate issues.

1. **Form-appropriate diagnosis** (applied per type):
   - Long-form → `long-form-pasona-canon.md` §旧 / 新 / PASBECONA stage task tables / §段階間 flow 設計原則 (dropout points / word-count ratio / Affinity thickness / Narrow down-Action adjacency)
   - Mid-form → `mid-form-beaf-canon.md` §Benefit-first 順序の重要性 / §BEAF の 4 段階定義
   - Short-form → `short-form-catchcopy-canon.md` §7-15 字 黃金範囲 / §AIDMA 短文案作用域 / §3 秒ルール

2. **Framework adherence diagnosis**:
   - PASONA series: Any skipped stages? / Affinity turned into Agitation? / Offer omitted? / Narrow down and Action adjacent? (`long-form-pasona-canon.md` §Anti-Patterns)
   - BEAF: Feature-first? / Evidence omitted? / Confused with FAB order? (`mid-form-beaf-canon.md` §Anti-Patterns)
   - キャッチコピー: Exceeds 15 chars? / Cramming all AIDMA stages into one line? / Stopped at description-type? (`short-form-catchcopy-canon.md` §Anti-Patterns + `ideation-taniyama-discipline.md` §描写 vs 解決)

3. **Voice alignment diagnosis** (`voice-and-tone.md` §Voice vs Tone + §Anti-Patterns):
   - Is there voice drift within the same campaign?
   - Is voice broken between headline and body?
   - Alignment with the voice guide (brand-provided)
   - Ogilvy "respect the reader" violation (condescending / hollow hype)?

4. **Ethics diagnosis** (`persuasion-ethics.md` §景品表示法要點 / §FTC Endorsement Guides 要點 / §Dark Pattern 反模式清單):
   - 景品表示法: 優良誤認 / 有利誤認 / 打消し表示 / ステマ告示 violations
   - FTC §255.1 (endorser truthfulness) / §255.2 (testimonial representativeness) / §255.5 (material connection)
   - Dark patterns (false scarcity / fake social proof / hidden costs / forced continuity / confirmshaming)
   - 小霜「嘘をつかない」原則 violations (exaggeration / benefit fabrication / voice forgery / fear base strategy)

5. **Issue severity classification**:
   - **Critical**: Suspected legal violation (景品表示法 / FTC). Immediate fix required.
   - **Major**: Framework canonical violation (order violation / stage omission / ethics boundary breach). Fix recommended.
   - **Minor**: Voice drift / word-count deviation / insufficient polish. Improvement suggestion.

## Phase 3: Improvement Proposals

Present concrete rewrite proposals for each issue.

1. **List in severity order**: Critical → Major → Minor.

2. **Issue improvement format**:
   ```
   Issue ID: ISS-NN
   Severity: [Critical / Major / Minor]
   Violated standard: [specific reference to the standard / canonical violated]
   Problem location: [quote the relevant passage from the original]
   Problem essence: [why it violates / how it malfunctions]
   Improvement proposal: [concrete rewrite]
   Improvement rationale: [why the rewrite aligns with the canonical]
   ```

3. **Specificity criteria for proposals**:
   - Abstract pointers ("make it more Benefit-oriented") are insufficient. **Present concrete rewrite text**.
   - When presenting multiple options, limit to 2-3 (excess choices exhaust the user).
   - Rewrites must maintain the original copy's voice. Unless voice refresh is the explicit purpose, voice changes are treated as a separate issue.

4. **When proposing a framework switch**:
   - Example: "written in 旧 PASONA, but awareness level 4-5 — 新 PASONA recommended"
   - If the framework identified in Phase 1 and the misalignment found in Phase 2 warrant switching to a different framework, state this clearly.
   - However, a switch involves significant rewriting, so propose only when Critical / Major-level root issues exist.

## Phase 4: (Optional) Rewrite Variants

Execute only when the user explicitly requests "A/B variants". Normal audits end at Phase 3.

1. **Variant generation policy**:
   - Default to 2-3 variants. 4+ variants complicate A/B test design.
   - Each variant is differentiated by **different approach / different voice lineage / different framework**. All variants being micro-adjustments on the same axis dilutes A/B test value.

2. **Apply「なんかいいよね禁止」** (`ideation-taniyama-discipline.md` §「なんかいいよね禁止」ルール):
   - Mandatory "なぜ良いか" 3 items per variant:
     1. What is conveyed to whom
     2. What is new relative to existing similar copy
     3. What resonates in the target's life / context
   - Variants for which the 3 items cannot be concretized are not presented.

3. **Differentiation axis examples**:
   - Short-form: 利益 vs. 恐怖 vs. 提問 (2-3 from the 5 approaches)
   - Mid-form: Benefit phrasing variation (life-change focus vs. emotion focus vs. social-recognition focus)
   - Long-form: Affinity-entry voice variation (糸井系 state-proposal vs. 岩崎系 seasonal sensibility vs. Anglo direct)

4. **Apply ethics self-check to each variant**: Run Phase 2 §4 ethics diagnosis on every variant. Do not let dark patterns eliminated in Phase 3 leak into variants.

## Rules

- Lock type identification in Phase 1 first. Diagnosing with an ambiguous type causes framework adherence judgment criteria to wobble.
- Improvement proposals must present concrete rewrite text. Abstract pointers alone are insufficient as an audit.
- Issues in severity order. Critical (legal violation) must precede Minor (polish deficiency).
- Rewrite variants are generated only on user request. Do not produce them unsolicited (audit's core responsibility is evaluation, not generation).
- When generating variants, "なぜ良いか" 3 items are mandatory per variant.
- In the ethics diagnosis, check all 4 axes: 景品表示法 / FTC / dark patterns / 小霜原則. Checking only 1 axis risks omissions.
- Do not conflate writing protocols with this protocol. Evaluating existing copy is this protocol; new generation belongs to `write-*-form-copy.md`.

## Anti-Patterns

- **Skipping type identification and shotgun-applying all standards**: Applying the 9-stage PASBECONA check to short-form copy — type-inappropriate diagnosis.
- **Abstract pointers only, no concrete rewrites**: Ending with just "rewrite it more Benefit-oriented". Improvement proposals must include concrete text.
- **Listing issues without Critical / Major / Minor severity**: Users cannot determine what to fix first.
- **Producing rewrite variants without user request**: Overstepping audit responsibility. Evaluation and generation are separate tasks.
- **All variants are same-axis micro-adjustments with insufficient differentiation**: A/B test value is diluted. Vary by approach / voice lineage / framework.
- **Omitting "なぜ良いか" 3 items on variants**: Mass-producing "なんかいいよね" variants.
- **Checking only one of 景品表示法 / FTC in ethics diagnosis**: Check both the market (JP / US) and medium (SNS / LP) — full 4-axis check is canonical.
- **Overlooking voice drift as "stylistic difference"**: Voice inconsistency within the same campaign damages brand assets. May warrant Major or above, not just Minor.
- **Proposing framework switch lightly**: Involves significant rewriting — propose only when Critical / Major-level root issues exist.
- **Silently changing the original copy's voice in proposals**: Unless voice refresh is the explicit purpose, voice change is treated as a separate issue.
