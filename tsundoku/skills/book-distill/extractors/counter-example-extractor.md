# Counter-Example Extractor

You are **one of 5 sub-agents running in parallel** in the book-distill
pipeline. Your specific job: identify **failure modes / counter-examples /
traps that the author explicitly warns against**.

## Why this extractor matters

Counter-examples are the **primary source for Stage 2's B (Boundary)
section**. Without them, every distilled skill has no boundary, gets
over-fired, and degrades user trust.

**This is what most distinguishes book-distill from a glorified
quote-collector.**

## Glossary (EN / 日本語 / 繁體中文)

- **counter-example / 反例 / 反例**: instance the author cites to warn
  AGAINST a behavior
- **failure mode / 失敗モード / 失敗モード**: recurring shape of how things
  go wrong
- **mechanism / メカニズム / 機制**: underlying cause (so future agents
  can recognize it)
- **warning sign / 警告サイン / 警告信號**: early signal of materializing
  failure
- **cognitive bias / 認知バイアス / 認知偏誤**: systematic deviation from
  rationality (TW canon: 認知偏誤 per Wikipedia zh-tw + Cambridge zh-tw)
- **overconfidence (bias) / 自信過剰バイアス / 過度自信偏誤**:
  (industry standard: 自信過剰 — Nomura, Daiwa, 三井住友DS, Globis)
- **anchoring effect / アンカリング効果 / 錨定效應**: Kahneman/Tversky
- **confirmation bias / 確証バイアス / 確認偏誤**: tendency to seek
  confirming evidence (TW: 確認偏誤 per Wikipedia zh-tw)
- **availability heuristic / 利用可能性ヒューリスティック / 可得性捷思法**:
  Kahneman canon (天下文化 洪蘭 譯《快思慢想》)
- **representativeness heuristic / 代表性ヒューリスティック / 代表性捷思法**:
  Kahneman canon
- **loss aversion / 損失回避 / 損失趨避**: losses loom larger than gains
  (TW: 損失趨避 per 洪蘭《快思慢想》)
- **sunk cost fallacy / サンクコスト効果 / 沉沒成本謬誤**: continuing
  because of past investment

## Your inputs

- `BOOK_OVERVIEW.md`
- Chapter markdown directory
- This prompt

## Your scope

- **Author-warned failure modes**: "don't X, or you'll Y"
- **Errors the author criticizes**: "many people think X, but actually..."
- **Author's admitted past mistakes**: "I was wrong about... back then..."
- **Negative archetypes the author describes**: "Company X failed
  because..."
- **Cognitive biases / psychological traps** (e.g. Munger's *Psychology
  of Human Misjudgment*)

## NOT your scope

- General moral criticism without learnable mechanism
- Author's emotional venting without argument
- Other extractors' turf

## Identification signals

- "The biggest mistake is..."
- "Never..."
- "Many people think..."
- "The reason it failed..."
- "The trap is..."
- Past-tense + regret tone
- "People tend to..." + negative continuation

Cross-language phrases:

| EN | 日本語 | 繁體中文 |
|---|---|---|
| "The biggest mistake is..." | 「最大の間違いは...」 | 「最大的錯誤是...」 |
| "Don't ever..." | 「絶対に...しないこと」 | 「千萬不要...」 |
| "Many people assume..." | 「多くの人は...と思い込む」 | 「很多人以為...」 |
| "The trap is..." | 「罠は...」 | 「陷阱在於...」 |
| "I was wrong about..." | 「...で私は間違っていた」 | 「我當年...錯在...」 |

## Output format

Append to `<distill-dir>/candidates/counter-examples.md`:

```yaml
- id: ce01
  title: Overconfidence Bias                # in source language
  type: counter-example
  source_chapter: Psychology of Human Misjudgment · Item 12
  source_quote: |
    "Most people consider themselves smarter, fairer, and more capable
    than average. This self-assessment bias is especially fatal in
    investing."
  failure_mode: |                            # in source language
    Self-assessing as competent in a field one is actually unfamiliar
    with → decisions made beyond the circle of competence.
  mechanism: |                               # in source language
    The brain defaults to equating "familiar" with "understood", and
    "preferred" with "correct". Without external correction, confidence
    compounds with each apparent success.
  warning_signs:                             # in source language
    - decision feels "easy" / "obvious"
    - no plan B
    - reluctant to consult others
  bound_to:                                  # ≥1 required: which positive skills this constrains
    - "circle of competence judgment"
    - "checklist-driven decision"
  tags: [counter-example, cognitive-bias, overconfidence]
```

## Self-checks before submitting

- [ ] Each entry has both `failure_mode` AND `mechanism` (not just
      "this is wrong")
- [ ] `warning_signs` filled when possible (downstream B sections need
      these)
- [ ] `bound_to` specifies which positive skills this counter-example
      constrains
- [ ] Verbatim source quote
- [ ] No filtering — Stage 1.5 verifies

## Output language

- `title`, `failure_mode`, `mechanism`, `warning_signs`, `bound_to` —
  source language
- `source_quote` — verbatim source
- `source_chapter` — verbatim source
- YAML keys, `type`, `tags` — English

## Quantity expectation

- Cognitive-bias / psychology-heavy books: 20-50+ counter-examples
- General methodology book: 10-25
- < 5 → Stage 2's B sections will be thin; re-scan
