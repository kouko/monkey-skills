# Rubric: Form-Appropriate Gate

SHOULD gate (qualitative flag-based). Triggers: copy artifact completed
(long / mid / short). The evaluator determines the artifact's form type
first, then evaluates only the dimension set for that form.

## Scope Boundary

This gate reviews:
- **Long-form** (PASONA family): inter-stage flow, drop-off prevention
  design, word-count ratios, PASBECONA mid-stage (B/E/C) persuasion
  depth
- **Mid-form** (BEAF): Benefit-first clarity, Evidence concreteness,
  Advantage comparison clarity
- **Short-form** (キャッチコピー): 3-second land ability, 7-15 字
  discipline, 掛詞 / phonetic technique, 5-type 切入点 clarity

This gate does NOT review:
- Framework stage existence / ordering (binary pass/fail) →
  `../checklists/persuasion-framework-adherence-checklist.md`
- Voice / Tone consistency → `voice-consistency-gate.md`
- Ethics / legal boundaries → `../checklists/ethics-checklist.md`

This gate handles **qualitative assessment of how well a structure is
executed**, not **whether the structure exists** (which is the
checklist's responsibility).

## Primary Sources

- `../standards/long-form-pasona-canon.md` — Word-count ratio rules of
  thumb (旧 PASONA P:A:So:N:A ≒ 2:2:3:2:1, PASBECONA
  P:A:S:B:E:C:O:N:A ≒ 1:1:1:1:2:2:1:0.5:0.5) + inter-stage flow
  design principles (drop-off points) + B/E/C insertion logic
  (abstract → objective → concrete) + Affinity thickness criteria.
- `../standards/mid-form-beaf-canon.md` — Benefit-first ordering
  canonical rationale + Evidence objective-info requirements +
  Advantage concrete comparison requirements.
- `../standards/short-form-catchcopy-canon.md` — 3-second rule
  recommended structure + 7-15 字 golden range + 掛詞 / phonetic
  technique (眞木準 canonical) + 5-type 切入点.
- grounding SSOT: `../research/grounding-v4.12.0.md` §2-3 + §8
  Load-bearing claims (PASONA word counts / BEAF ordering / 7-15 字
  measurements).

## Form Type Determination (evaluator first step)

1. Check artifact word count / medium / declared framework
2. Determine form_type = **long** / **mid** / **short**
3. Evaluate only the dimension set for that form; mark other-form
   dimensions as `not_applicable`

---

## Dimensions — Long-form (PASONA family)

### RUB-CTW-FA-L1: Flow / Progression

Whether inter-stage transitions are smooth. Whether conjunctions /
subheadings / questions provide an explicit "bridge to the next stage."

- 🔴 **Fatal**: Abrupt jumps between stages. For instance, leaping from
  Affinity empathy to Solution with a jarring pivot like "I felt the
  same way → Actually there is a solution." Especially missing
  transitions at the PASBECONA B→E boundary (expectation received by
  evidence) and C→O boundary (concrete to offer). Breaks the reader's
  cognitive inertia.
- 🟡 **Warning**: Overall flow is present but 1-2 inter-stage gaps
  show breaks (abrupt scene changes without conjunctions, logically
  incoherent subheadings).
- 🟢 **Clear**: All inter-stage transitions are natural. Conjunctions /
  questions / subheadings logically preview the next stage.

### RUB-CTW-FA-L2: Drop-off Prevention Design

In long-form copy, readers tend to drop off at stage endings. Whether
each stage ending has a "hook to keep reading the next stage."

- 🔴 **Fatal**: Zero drop-off prevention design. All stage endings are
  plain fact enumeration with no motivation to continue. Especially in
  the mid-section (Solution / Benefit / Evidence), no reader-engaging
  hook — estimated high drop-off rate.
- 🟡 **Warning**: Partially designed. Opening (Problem/Affinity) and
  closing (Action) areas have hooks, but mid-section stage endings
  (Solution/Benefit/Evidence) have weak end-of-stage hooks.
- 🟢 **Clear**: All stage endings have "keep reading" hooks (unresolved
  questions, small surprises, previews of the next stage, unexpected
  connections).

### RUB-CTW-FA-L3: Word-Count Ratios

Whether the artifact follows the canonical ratio guidelines from
`long-form-pasona-canon.md` §段階間 flow 設計原則.
- 旧 PASONA: P:A:So:N:A ≒ 2:2:3:2:1
- PASBECONA (5,000 字): P:A:S:B:E:C:O:N:A ≒ 1:1:1:1:2:2:1:0.5:0.5
- Key proportions: **Problem+Affinity 20-30% / Solution+Offer 40-50% /
  Narrow+Action 10-20%** (in PASBECONA, Evidence + Contents occupy the
  40-50% mid-section)

- 🔴 **Fatal**: Severe deviation from ratios. Examples:
  Problem+Affinity exceeds 50% (reader fatigue), Evidence under 5%
  (thin persuasion in PASBECONA), Narrow+Action over 40% (sales-pushy
  feel).
- 🟡 **Warning**: Minor deviation (within ±10%). Canonical ratios are
  visible in the structure but 1-2 stages are over- or under-weight.
- 🟢 **Clear**: Follows canonical ratios. Or intentional deviation is
  explicitly justified in artifact metadata.

### RUB-CTW-FA-L4: PASBECONA Mid-Stage B/E/C Persuasion Depth

Applies to PASBECONA artifacts only. B (Benefit) / E (Evidence) /
C (Contents) are the 3 stages PASBECONA adds to 新 PASONA; their
persuasion depth is the source of long-form superiority.

- 🔴 **Fatal**: B/E/C are hollow. Benefit is abstract ("your life will
  change") with no concrete vision; Evidence is vague ("loved by many")
  with no objective numbers / third-party testimonials; Contents is
  product-name repetition with no component / usage / inclusions info.
- 🟡 **Warning**: 1 of the 3 stages is thin. Examples: Benefit is vivid
  but Evidence has only 1 data point; Contents merely lists components
  without usage instructions.
- 🟢 **Clear**: B (abstract future vision) → E (objective backing with
  3+ types: authority / track record / customer voice) → C (components
  + usage + inclusions + support) — all stages are substantive,
  preemptively answering the reader's "is this real?" and "what
  exactly is it?"
- **Note**: For 新 PASONA (6 stages) / 旧 PASONA (5 stages) artifacts,
  this dimension is `not_applicable`.

---

## Dimensions — Mid-form (BEAF)

### RUB-CTW-FA-M1: Benefit-first Clarity

Whether the first paragraph / first sentence is purely a Benefit, with
no Feature contamination.

- 🔴 **Fatal**: Feature-first opening ("capacity 500ml, ingredients
  are…"). Reverses BEAF canonical ordering into FAB order (F→A→B).
  Product page scan-reading triggers drop-off.
- 🟡 **Warning**: First paragraph is Benefit-based but mixes in Feature
  ("For those who want X, the 500ml Y"). Not pure Benefit.
- 🟢 **Clear**: First paragraph is purely Benefit ("the resulting
  state" / "how the reader's life changes"). No Feature reference.
  Example: "Covers a full day's hydration in your commuter bag."

### RUB-CTW-FA-M2: Evidence Concreteness

Whether the Evidence stage is composed of verifiable objective
information.

- 🔴 **Fatal**: Empty claims only. "Loved by many," "trending now,"
  "chosen by…" — nothing but unverifiable subjective vague expressions.
  Zero objective numbers / awards / third-party evaluations.
- 🟡 **Warning**: Vague. Numbers exist but without source ("95%
  satisfaction" but no sample size / research organization); or awards
  are mentioned but year / host is unknown.
- 🟢 **Clear**: Concrete numbers + sources. Examples: "Reviews
  4.8/5.0 (2,341 entries / Rakuten)", "XYZ Award 2024 (hosted by XYZ
  Association)", "Clinical trial shows 35% improvement in moisture
  retention (n=120, University of X, 2023)." Verifiable.

### RUB-CTW-FA-M3: Advantage Comparison Clarity

Whether the Advantage stage presents concrete differences from
competitors.

- 🔴 **Fatal**: Advantage missing or only meaningless adjectives ("high
  quality," "the best," "industry-leading class"). Zero competitive
  comparison.
- 🟡 **Warning**: Vague comparison. "Superior to other products in X"
  with unidentified subject, or only 1 comparison axis making it hard
  for the reader to grasp the difference.
- 🟢 **Clear**: Concrete differences. Comparison axis + numbers +
  unique technology / certification combined. Examples: "2x absorption
  vs competitors (XYZ Association test 2024)," "Only product in the
  industry with XYZ patented technology."

---

## Dimensions — Short-form (キャッチコピー)

### RUB-CTW-FA-S1: 3-Second Land Ability

Whether the 3-second rule (1st second: attention grab, 2nd second:
main message, 3rd second: action trigger) is met. Whether it captures
attention at first glance.

- 🔴 **Fatal**: Requires re-reading to understand the meaning.
  Abstraction level is extremely high; target needs several seconds
  to recognize it as relevant. In the SNS-era 1-3 second judgment
  window, certain drop-off.
- 🟡 **Warning**: Meaning can be grasped with effort but an initial "?"
  remains. Intentional ambiguity (糸井 style) is the intent, but
  overestimates the target audience's interpretive capacity.
- 🟢 **Clear**: "What this is and whether it's relevant to me" is
  discernible at first glance. Even when intentional ambiguity is
  used, the ambiguity functions as attraction rather than causing
  drop-off.

### RUB-CTW-FA-S2: 7-15 字 Discipline

Per `short-form-catchcopy-canon.md` §7-15 字 黃金範囲.

- 🔴 **Fatal**: Under 5 字 or over 20 字. Under 5 字 means
  insufficient information content for a copy; over 20 字 means it
  should be classified as a lead / subtitle / body copy rather than a
  キャッチコピー.
- 🟡 **Warning**: 5-6 字 or 16-19 字. Boundary range where
  justification is desirable (e.g., "product name alone functions as
  a short phrase" or "added 1 字 for a complex product").
- 🟢 **Clear**: 7-15 字. Within the measured range of 糸井 7 / 岩崎
  12-14 / 眞木 10 / Yahoo Topics 13.
- **Note**: Unlike the checklist side (CHK-CTW-PFA-006), this dimension
  includes qualitative evaluation of whether "余韻 / readability are
  satisfied even within range."

### RUB-CTW-FA-S3: 掛詞 / Phonetic Technique Recognition

When 眞木準 style (掛詞 / phonetics) or 岩崎 style (seasonal feel /
rhythm) techniques are declared, whether the technique functions
effectively. For artifacts with no technique declaration →
`not_applicable`.

- 🔴 **Fatal**: Technique declared but ineffective. Intended phonetic
  repeat + 掛詞 like「でっかいどぉ／北海道」but the actual result is
  a forced pun or weak phonetic match — falls on the "pun" side
  rather than "wit" (violates 眞木準's「ダジャレではなく、オシャレ」
  principle).
- 🟡 **Warning**: The technique is valid but makes an ordinary
  impression. Rhythm is good but surprise factor is low; 掛詞 works
  but dual-meaning effect is weak.
- 🟢 **Clear**: Skillful. Phonetics flow smoothly and the 掛詞 dual
  meaning brings fresh discovery to the reader. Canonical quality at
  TCC annual level.
- **Note**: For artifacts that do not declare 掛詞 / phonetic technique
  → `not_applicable`.

### RUB-CTW-FA-S4: 5-Type 切入点 Clarity

Whether the adopted approach (利益／願望, 恐怖／痛点, 顛覆常識,
目標呼喚, 提問互動) is discernible from the output.

- 🔴 **Fatal**: Vague. The adopted approach is unreadable from the
  output — "somehow nice" without a defined 切入点. Tends to co-occur
  with 谷山「なんかいいよね禁止」 violation.
- 🟡 **Warning**: Partially discernible. The adopted approach can be
  guessed but execution is half-hearted ("顛覆常識" but the paradigm-
  shift punch is weak; "提問互動" but the reader has insufficient
  incentive to answer, etc.).
- 🟢 **Clear**: The adopted approach is immediately identifiable from
  the output's syntax / vocabulary / speech mode. Approach selection
  and execution are aligned.

---

## Verdict Rules

- Any single 🔴 fatal → `NEEDS_REVISION` (escalate to user)
- **2 or more** 🟡 warnings → `NEEDS_REVISION`
- **1** 🟡 warning (no 🔴) → `PASS_WITH_NOTES` (auto-revise trigger)
- All 🟢 clear → `PASS`
- `not_applicable` dimensions (form not applicable or no technique
  declaration) are excluded from verdict calculation.

## Rules

- Complete form_type determination first. A mis-determination (e.g.,
  judging a PASBECONA artifact as mid) invalidates the entire
  evaluation.
- Respect responsibility split with the checklist: binary existence /
  ordering is the checklist's job; **qualitative execution level** is
  this rubric's job.
- For NEEDS_REVISION, present at least 1 alternative ("improving like
  this would achieve 🟢").
- When evaluating 7-15 字 discipline (S2) at the boundary (5-6 字 /
  16-19 字), assess the copy's standalone quality (do not assign 🔴
  for character count alone; 🔴 only at under 5 字 or over 20 字).

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "form_type": "long | mid | short",
  "framework_declared": "旧 PASONA | 新 PASONA | PASBECONA | BEAF | AIDMA-short",
  "dimensions": [
    {
      "id": "RUB-CTW-FA-L1",
      "name": "Flow / Progression",
      "flag": "red | yellow | green | not_applicable",
      "evidence": "Specific quoted passage + analysis",
      "suggestion": "If red/yellow, concrete improvement suggestion"
    }
  ],
  "summary": "1-3 sentence overall assessment + next-step priority"
}
```
