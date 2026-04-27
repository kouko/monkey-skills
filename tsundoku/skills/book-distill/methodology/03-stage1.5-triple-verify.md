# Stage 1.5 — Triple verification filter

## Goal

From the candidate pool, filter the units that **truly deserve to become
independent skills**. Failures get demoted to `example` / `quote` /
`term` (still usable downstream as supporting material) but do not
become standalone skills.

This is the quality gate that separates `book-distill` from a glorified
quote-collector.

## The three verification checks (must pass ALL THREE)

### V1 — Cross-domain (本書內獨立佐證 / 横断的検証)

**Question**: does the book independently support this unit in **≥2
distinct contexts**?

- "Distinct" means: NOT the same example rephrased; instead two different
  chapters / different objects of analysis / different conclusions, all
  invoking the same underlying methodology.

- ✅ PASS example: *Poor Charlie's Almanack*'s "inversion thinking"
  appears in: investment decisions (chapter 3), avoiding catastrophe
  (chapter 7), pedagogy (chapter 11) — three independent contexts.

- ❌ FAIL example: A nicely-phrased aphorism appears once, in a single
  paragraph, with no other supporting context. Demote to `quote`, do not
  promote to skill.

**Why**: methodologies repeated in multiple contexts are what the author
genuinely wants to transmit. One-off phrasings are decoration.

### V2 — Predictive power (予測能力 / 預測力)

**Question**: can you use this unit to derive a meaningful answer to
a question the book did NOT explicitly address?

- Design a scenario the book doesn't cover.
- Try to reason it out using only this candidate methodology.

- ✅ PASS: produces a non-trivial, non-platitudinous conclusion.
- ❌ FAIL: produces only "be careful" / "work hard" / "depends on
  context" — the unit has no actual explanatory power. Demote.

**Why**: real methodology must **extrapolate**. If a unit can only
recapitulate the book's own examples, it is description, not method.

### V3 — Exclusivity (独自性 / 獨特性)

**Question**: is this unit "common sense any smart person would say"?

- If you erase the author's name, would a competent stranger to this
  field also reach this idea? Then it's NOT a skill.
- The unit must capture **the author's distinctive viewpoint /
  counter-intuitive insight / specialized vocabulary**.

- ✅ PASS: 段永平's "stop doing list" — actively listing what NOT to do
  is counter-intuitive ranking.
- ❌ FAIL: "Respect time" — too commonsense; nobody needs a skill to
  remind them.

**Why**: Claude already knows common sense. Skills should encode the
**differentiated insights** worth fixing as separate behavioral hooks.

## Verification execution flow

1. Merge the 5 `candidates/*.md` files into a unified candidate pool
2. **Deduplicate**: if multiple extractors caught the same methodology,
   merge into one entry
3. For each candidate, run V1 / V2 / V3, recording the judgment AND the
   reasoning
4. Pass → write to `<distill-dir>/verified.md`, advance to Stage 2
5. Fail → write to `<distill-dir>/rejected/<id>.md` with **explicit reason
   for which check(s) failed**. This audit trail lets the user reconsider
   later, and forces honesty during evaluation.

## Output template (verified.md, per surviving unit)

```yaml
id: f01
title: Inversion Thinking
type: framework
V1_cross_domain:
  passed: true
  evidence:
    - chapter: "Chapter 3"
      context: "investment decision-making"
    - chapter: "Chapter 7"
      context: "engineering design"
    - chapter: "Chapter 11"
      context: "pedagogy"
V2_predictive_power:
  passed: true
  novel_question: |
    "What if an interviewer asks me a question I don't know the answer to?"
  derived_answer: |
    Invert: ask "what's the worst impression I could leave?" — then
    behave to avoid that, rather than trying to construct an answer.
V3_exclusivity:
  passed: true
  why_not_common: |
    Common advice is "think more"; inversion is "think backwards FIRST" —
    a counter-intuitive priority, not a piety.
→ advance to Stage 2
```

## Output template (rejected/<id>.md, per cut unit)

```yaml
id: p17
title: "Be patient"
type: principle
V1_cross_domain:
  passed: false
  reason: |
    Author says it once in chapter 2, and the rest of the book actually
    contradicts it (advocating decisive action under time pressure).
V2_predictive_power: not_evaluated
V3_exclusivity: not_evaluated
disposition: |
  Demote to quote. Reference from no skill.
```

## Output language

- YAML field names — English
- `evidence.context`, `novel_question`, `derived_answer`, `why_not_common`
  — match source book language (so they make sense in context with the
  source quote)
- `chapter` field — verbatim source language
- `disposition` (audit metadata) — English

## Common failure modes (cheating to be aware of)

1. **V1 cheating**: counting "the same example told twice" as two
   contexts. Requirement: different chapters AND different objects AND
   different conclusions.
2. **V2 cheating**: dressing up a question the book actually does
   address as "novel". The novel question should make a fresh reader go
   "huh, I don't know what the book would say about this".
3. **V3 over-laxity**: thinking that any well-phrased statement is
   "non-obvious". Test the substance, not the wording.

## Pass-rate expectation

| Book type | Typical pass rate |
|---|---|
| Methodology-dense (e.g. Munger / *Poor Charlie's*) | 30-50% |
| Practical manual / how-to | 25-40% |
| Narrative non-fiction (e.g. *Sapiens*) | 10-20% |
| Essay collection | 5-10% |
| Memoir / biography | 5-15% |

**< 5%** → suspect extractor quality; consider re-running Stage 1.
**> 80%** → suspect verification standards too lax; re-tighten the
checks.

## Trilingual glossary

| English | 日本語 | 繁體中文 |
|---|---|---|
| cross-domain | 横断的 | 跨域 |
| predictive power | 予測能力 | 預測力 |
| exclusivity | 独自性 | 獨特性 |
| common sense | 常識 | 常識 |
| extrapolate | 外挿 | 外推 |
| audit trail | 監査トレイル | 審計軌跡 |
| disposition | 処分 / 扱い | 處置 |
