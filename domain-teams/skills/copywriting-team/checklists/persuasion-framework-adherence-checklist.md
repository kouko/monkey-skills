# Checklist: Persuasion Framework Adherence

MUST gate (binary pass/fail). Triggers: copy artifact completed (long /
mid / short). The evaluator determines the artifact's form type first,
then evaluates only the items for that form (non-applicable items are
`N/A`).

## Primary Sources

- `../standards/long-form-pasona-canon.md` — 旧 PASONA (5) / 新 PASONA
  (6) / PASBECONA (9) stage definitions, ordering, word-count ratios,
  Affinity thickness criteria.
- `../standards/mid-form-beaf-canon.md` — BEAF (Benefit → Evidence →
  Advantage → Feature) ordering, Benefit-first canonical rationale,
  cautions against FAB-order reversal.
- `../standards/short-form-catchcopy-canon.md` — 7-15 字 golden range,
  AIDMA short-form (A+I only), 5-type 切入点 decision tree (利益／
  恐怖／顛覆／呼喚／提問).
- `../standards/ideation-taniyama-discipline.md` — 「なんかいいよね
  禁止」 3-reason rule, 描写 vs 解決 boundary.
- grounding SSOT: `../research/grounding-v4.12.0.md` §2 Cluster A /
  §3 Cluster B.

## Form Type Determination (evaluator first step)

1. Check artifact word count and medium:
   - 1,500 字 or more → **long** (PASONA family)
   - Tens to hundreds of chars, product page / POP / catalog → **mid** (BEAF)
   - 7–20 字, headline / catch → **short** (AIDMA short-form)
2. Record `form_type` in the output JSON
3. Only PASS/FAIL the items for the relevant form; mark other-form
   items as `N/A`

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's
output. Give `PASS`, `FAIL_FATAL`, `FAIL_FIXABLE`, or `N/A` for each
item, with specific evidence (quoted line or paragraph reference).
Failure type for each item is defined below — use the type specified.

## Checklist — Long-form (PASONA family)

- [ ] **CHK-CTW-PFA-001 (PASONA stage completeness)** [FATAL]: All
  stages of the declared framework (旧 PASONA / 新 PASONA / PASBECONA)
  are present in the artifact.
  - 旧 PASONA: **P / A (Agitation) / So / N / A** — 5 stages
  - 新 PASONA: **P / A (Affinity) / S / O / N / A** — 6 stages
  - PASBECONA: **P / A (Affinity) / S / B / E / C / O / N / A** — 9 stages
  Any missing stage → FATAL. Stage existence is judged from
  subheadings / paragraph topics. **Grounded in**:
  `../standards/long-form-pasona-canon.md` §旧/新 PASONA/PASBECONA
  definition tables.
- [ ] **CHK-CTW-PFA-002 (Stage ordering correctness)** [FIXABLE]: Stage
  appearance order matches the canonical sequence. Especially check
  the following prohibited orderings:
  - Offer before Solution (新 / PASBECONA)
  - Contents before Benefit (PASBECONA — reverses abstract→objective→concrete)
  - Evidence before Benefit (PASBECONA — violates B/E/C insertion logic)
  - Action before Narrow down (loses urgency)
  1 order violation → FIXABLE. 2 or more → FATAL. **Grounded in**:
  `../standards/long-form-pasona-canon.md` §段階間 flow 設計原則 +
  §Anti-Patterns.
- [ ] **CHK-CTW-PFA-009 (Affinity thickness — 新 / PASBECONA only)**
  [FIXABLE]: In 新 PASONA / PASBECONA, the Affinity stage volume is
  at least equal to the Problem stage. A thin Affinity (only 1-2
  sentences, under 1/3 of Problem) becomes an "empathy-flavored
  line" and violates canon. **Grounded in**:
  `../standards/long-form-pasona-canon.md` §段階間 flow 設計原則.

## Checklist — Mid-form (BEAF)

- [ ] **CHK-CTW-PFA-003 (BEAF Benefit-first)** [FATAL]: The first
  paragraph / first sentence is a Benefit (how the reader's life
  improves, the resulting state), not a Feature (spec) or Advantage
  (competitive comparison). A Feature-first opening reverses BEAF
  canon into FAB order and is FATAL. Spec enumeration such as
  "500ml / ingredients…" at the opening → FATAL. **Grounded in**:
  `../standards/mid-form-beaf-canon.md` §順序の canonical 性 +
  §Benefit-first 順序の重要性.
- [ ] **CHK-CTW-PFA-004 (Evidence concreteness)** [FIXABLE]: An
  Evidence stage exists and is **concrete**. The following are
  unacceptable:
  - Only subjective vague phrasing such as "loved by many" or
    "trending now"
  - Only adjectives such as "high quality" or "the best" with no
    objective info (numbers, awards, customer count, review scores)
  - Uses the label "customer voice" but provides no concrete quote,
    initials, or numbers
  Acceptable examples: "Reviews 4.8/5.0 (2,341 entries)", "XYZ
  Award 2024", "Clinical trial shows 35% improvement in moisture
  retention". **Grounded in**:
  `../standards/mid-form-beaf-canon.md` §BEAF 4 段階定義表 +
  §Anti-Patterns (Evidence stage omission).

## Checklist — Short-form (キャッチコピー)

- [ ] **CHK-CTW-PFA-005 (5-type 切入点 explicit selection)** [FIXABLE]:
  Artifact metadata or candidate description explicitly states which
  of the 5 切入点 was adopted: **利益／願望 / 恐怖／痛点 / 顛覆常識 /
  目標呼喚 / 提問互動**. Unstated or "somehow" → FIXABLE. The 切入点
  must be readable from the finished copy (e.g., "Is this really
  OK?" = 恐怖／痛点). **Grounded in**:
  `../standards/short-form-catchcopy-canon.md` §5 種切入点決策樹.
- [ ] **CHK-CTW-PFA-006 (7-15 字 discipline)** [FIXABLE]: The
  キャッチコピー body falls within the 7-15 字 golden range.
  - Within 7-15 字 → PASS
  - 5-6 字 or 16-20 字 with rational notes → FIXABLE (notes required)
  - Under 5 字 or over 20 字 → FATAL (should be classified as a
    lead / subtitle / body copy, not a キャッチコピー)
  **Grounded in**: `../standards/short-form-catchcopy-canon.md`
  §7-15 字 黃金範囲 + §Anti-Patterns (calling 15 字+ a「キャッチコピー」).
- [ ] **CHK-CTW-PFA-007 (AIDMA short-form A+I only)** [FIXABLE]: The
  キャッチコピー alone does not try to carry Desire/Memory/Action.
  The following are FIXABLE:
  - Includes a concrete CTA ("Call now!", "Click", "Apply") inside
    the short text (forcing D/A)
  - Compresses price / guarantee / deadline into the short text
    (injecting Offer / Narrow down)
  Short-form copy is A (Attention) + I (Interest) only; D/M/A are
  handled by body copy / CTA / repetition under the canonical division
  of labor. **Grounded in**:
  `../standards/short-form-catchcopy-canon.md` §AIDMA 短文案作用域.

## Checklist — All form types

- [ ] **CHK-CTW-PFA-008 (なんかいいよね禁止 — 3-reason concreteness)**
  [FIXABLE]: When the artifact contains multiple candidates, each
  candidate has 3 concrete "why it's good" reasons. Requirements:
  1. **What the line communicates to which reader** — concrete
     communication content
  2. **Novelty versus existing similar copy** — differentiation point
  3. **Resonance within the target's life / context** — concrete
     scene
  A candidate that cannot make all 3 concrete falls into 谷山's
  「なんかいいよね」 category and is FIXABLE. Also, a "descriptive"
  candidate (merely rephrasing product attributes as「〇〇は△△です」
  without reaching resolution / meaning proposal) is FIXABLE.
  **Grounded in**: `../standards/ideation-taniyama-discipline.md`
  §「なんかいいよね禁止」ルール + §描写 vs 解決.
- [ ] **CHK-CTW-PFA-010 (Framework declaration)** [FIXABLE]: The
  artifact metadata explicitly names the adopted framework (旧 PASONA
  / 新 PASONA / PASBECONA / BEAF / AIDMA-short). No declaration →
  FIXABLE (declaration is required for the evaluator to determine
  form type). **Grounded in**:
  `../standards/long-form-pasona-canon.md` §三框架の適用表 +
  `../standards/mid-form-beaf-canon.md` §字數範囲と適用用例 +
  `../standards/short-form-catchcopy-canon.md` §7-15 字 黃金範囲.

## Verdict Rules

- Any single item `FAIL_FATAL` → `NEEDS_REVISION` (escalate to user)
- Only `FAIL_FIXABLE` (no FATAL) with **≤ 2 items** → `PASS_WITH_NOTES`
  (auto-revise trigger)
- `FAIL_FIXABLE` in **≥ 3 items** → `NEEDS_REVISION`
- All items `PASS` or `N/A` → `PASS`
- `N/A` is limited to items that do not apply to the form type
  (e.g., in a long artifact CHK-003 through CHK-007 are `N/A`;
  in a mid artifact 001/002/009/005/006/007 are `N/A`, etc.).
  CHK-008 and CHK-010 apply across all forms.

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "form_type": "long | mid | short",
  "framework_declared": "旧 PASONA | 新 PASONA | PASBECONA | BEAF | AIDMA-short | unknown",
  "items": [
    {
      "id": "CHK-CTW-PFA-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE | N/A",
      "note": "Specific evidence (quoted line or paragraph ref) + fix instruction if FIXABLE"
    }
  ],
  "summary": "1-3 sentence overall assessment"
}
```
