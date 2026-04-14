---
title: Mandal-Art 曼陀羅発想法 (今泉浩晃 1987/1988)
tier: 3
---

# Mandal-Art 曼陀羅発想法

Tier 3 standard: self-contained. Uses 今泉浩晃's 1987 proposal and 1988
book formalization of the 3×3 曼陀羅 structure as canonical source,
providing a structured divergence tool for copywriting-team's 散らかす
(divergence) stage. This file corrects two common attribution drifts:
(1) the "standard 8-direction taxonomy" is a later-invented derivative,
not from 今泉's original canon; (2) 大谷翔平's OW64 chart belongs to
原田隆史 Method (松村寧雄 1979 マンダラチャート lineage), **not**
今泉's マンダラート. This standard regulates only 今泉's original 3×3
structure and its automation boundaries, and supplements a "direction
library" for the main worker to self-select 8 directions per topic,
explicitly marking the library as a later-derived convenience tool
rather than part of 今泉's canon.

## Primary Sources

- 今泉浩晃 (1987) 「マンダラート」proposal — first appearance as a personal 3×3 memo technique. copywriting-team Tier 3 canonical source.
- 今泉浩晃 (1988) 『創造性を高めるマンダラート発想法』日本実業出版社 — 3×3 structure + 81-cell expansion (72 associated concepts) fully formalized. 今泉 original book.
- Wikipedia 日本語版「マンダラート」 https://ja.wikipedia.org/wiki/マンダラート — secondary dual-verify source: 今泉 1987 proposal, 曼荼羅-derived naming, 3×3 basic structure.
- idea-soken「マンダラート発想法の使い方」 https://www.idea-soken.com/mandal-art — secondary dual-verify source: 9-cell / 81-cell expansion procedure, practical guide citing 今泉's book.

## Critical Attribution Corrections

- **The "standard 8-direction taxonomy" is not from 今泉's original canon.**
  Popular writing attributes categories such as "生活情境／情感トリガー／
  数字刺激／反常識／メタファー対比／ストーリー冒頭／疑問形／ベネフィット
  表達" to 今泉's 1987 work, but these are in fact later derivations by
  Japanese creative-industry mentors and blog authors based on use cases.
  今泉's original canon specifies only **the 3×3 structure + central theme
  + 8 association cells**, with no prescription on classification principle
  of the association content. The §"Direction Library" section below
  explicitly labels this as a derivative tool and must not be cited as
  part of 今泉's 1987/1988 regulation.
- **大谷翔平's OW64 is not 今泉's マンダラート.** The 8-goal achievement
  sheet (OW64, a.k.a. 目標達成マンダラチャート) 大谷 used at 花卷東高校
  originates from **原田隆史's 原田 Method**, whose lineage traces to
  松村寧雄's 1979 proposal of「マンダラチャート」(trademarks held by
  クローバ経営研究所 / マンダラチャート協会). 今泉's「マンダラート」
  and 松村's「マンダラチャート」are **two methods with similar names but
  different origins**, and the 大谷 case must not be used as evidence of
  今泉 grounding.

## Framing

Mandal-Art is a divergence tool whose basic unit is a 3×3 grid (9 cells).
Its core idea is to force all eight cells around a central theme to be
filled, using "fill-in pressure" to elicit non-habitual associations.
The difference from generic brainstorming lies in **spatial closure**:
8 cells are finite and must all be filled. This constraint converts
"free association" into "forced association" — a structural mechanism
for producing unexpected concepts.

Within the copywriting pipeline, this tool belongs to the "散らかす
(divergence)" stage as a representative technique, combined with
Verbalized Sampling (lexical-layer diversity): Mandal-Art is
responsible for **structural-layer** diversity (covering 8 entry
angles), and Verbalized Sampling is responsible for **lexical-layer**
diversity (expression variety within a single angle).

## Original 3×3 structure (今泉 1987/1988 canonical)

**Single-layer Mandal-Art** consists of 9 cells:

```
┌─────┬─────┬─────┐
│  1  │  2  │  3  │
├─────┼─────┼─────┤
│  8  │ 中心 │  4  │
├─────┼─────┼─────┤
│  7  │  6  │  5  │
└─────┴─────┴─────┘
```

- **Center cell**: theme (e.g. product name, key message, core benefit)
- **Surrounding 8 cells**: 8 association results; classification is
  unrestricted, but all cells **must be filled** (the "no blank" rule)

今泉 original canon emphasizes:
- Fill-in mandate is the core mechanism — leaving blanks loses the
  forced-association effect
- The 8 associations **need not be mutually orthogonal**; they may be
  parallel thinking or layered progression
- Center and surrounding cells are in **mutual semantic mapping**
  (borrowed from the「中台八葉」structure of 曼荼羅 iconography)

## Expanded 81-cell version (72 associated concepts)

Each of the 8 association results is expanded as a **new center** with
its own 3×3:

```
[Expansion layer: 8 sub-mandalas × 9 cells = 72 new associated concepts]
                    +
[Central layer: original 9 cells]
                    =
[Total: 81 cells / 72 associated concepts]
```

The 81-cell form is the expansion formalized in 今泉's 1988 book
『創造性を高めるマンダラート発想法』. Output at this layer can flow
directly into the「ラベル作成」stage of KJ法 (`ideation-kj-convergence.md`)
for convergence.

## Automation boundary table

| Task | LLM can do | Semi-auto (human checkpoint) | LLM must not do |
|---|---|---|---|
| Single-layer 9-cell fill-in | ✓ theme + 8 associations in one pass | — | — |
| 81-cell expansion | ✓ batch expand 72 cells from the 8 associations | — | — |
| Drift check (deviation from central theme) | ✓ rule-based check | — | — |
| Verbalized Sampling injection | ✓ each cell's output attaches probability | — | — |
| "Unexpected viewpoint" identification | — | ✓ LLM flags candidates, human confirms | — |
| Selecting valid concepts for convergence from 72 cells | — | ✓ LLM pre-screens Top-N, human decides | — |
| Strategic selection of the central theme itself | — | — | ✗ requires human / planning-team judgment |

**Rule**: in the copywriting subagent pipeline, automation may output
all 81 cells in one pass, but "selecting the 8-12 candidates entering
KJ convergence" must include a human checkpoint (or an evaluator
agent acting as proxy checkpoint).

## Application to copywriting

### Applicability

- **Single-line catch copy ideation**: applicability **high**. The 3×3
  structure is well-suited to generating 8 angles × 9 expressions ≈
  72 candidates for a single key message, then handing over to
  `ideation-kj-convergence.md` to converge to 3–5 winners.
- **Long-form copy ideation**: applicability **low**. Long-form copy
  (PASONA / PASBECONA / QUEST / PASTOR) has fixed stage skeletons, and
  inter-paragraph causality is decided by the framework; Mandal-Art
  offers limited help with "in-paragraph sentence filling", and 81-cell
  output does not directly correspond to narrative coherence of long
  copy. For long copy, prefer a layered approach: "framework stages ×
  per-stage independent Mandal-Art".
- **Mid-form copy (BEAF)**: applicability **medium**. Each of Benefit /
  Evidence / Advantage / Feature can be independently expanded into
  its own 9-cell grid.

### Representative usage flow

```
【Step 1】Theme confirmation
  └── planning-team supplies the key message (center cell)

【Step 2】Select 8 directions
  └── main worker picks 8 directions from the "Direction Library" per topic
  └── or the LLM self-generates 8 associations (bypassing the derivative library)

【Step 3】Fill 9 or 81 cells
  └── LLM fills cells (with Verbalized Sampling probability attached)

【Step 4】Converge candidates
  └── human / evaluator agent checkpoint
  └── proceed to ideation-kj-convergence.md
```

## Direction Library (later-derived, not 今泉 1987 original canon)

> [!warning] This library is a derivative tool
>
> The 16+ directions below are compiled from JP / zh-Hant creative-
> industry practitioner blogs and TCC seminar notes, and are **not**
> part of 今泉浩晃's 1987/1988 original canon. Treat as a convenience
> tool: freely add, remove, or ignore entirely (falling back to LLM
> self-generated 8 associations).

The main worker may pick 8 directions per topic to fill the surrounding
cells:

1. **Life scenarios** (user's daily-life contexts)
2. **Emotional triggers** (fear, surprise, empathy, compassion, relief)
3. **Numerical impact** (quantitative hooks: %, times, time, headcount)
4. **Counter-intuitive** (claims that contradict audience priors)
5. **Metaphor / contrast** (compare product to unrelated objects)
6. **Story opening** (narrative hooks: "ある日、…", "もし…")
7. **Interrogative form** (「〇〇しませんか？」「なぜ…？」)
8. **Benefit translation** (feature → benefit)
9. **Comparison** (before/after, competitor contrast, self vs others)
10. **Paradox** (seemingly contradictory juxtaposition, e.g.「遅いほど速い」)
11. **Time axis** (retrospective, foresight, instantaneous, long-term)
12. **User voice** (first-person confession, testimonial tone)
13. **Problem-solution path** (pain point → resolution)
14. **Sensory description** (visual, auditory, tactile, olfactory, gustatory)
15. **Personification** (product or abstract concept anthropomorphized)
16. **Season / almanac** (節気、年中行事、旬)
17. **掛詞 / phonetics** (homophones, rhyme, リズム;眞木準 lineage)
18. **Extremization** (push to the limit:「最も」「唯一」「誰も」)
19. **Negation / prohibition** (「〜するな」「〜しない方がいい」)
20. **Authority / evidence** (data, 実績、受賞、専門家推薦)
21. **Shared experience** (「あるある」訴求, generational shared memory)
22. **Self-reference** (the product speaks for itself, meta ads)
23. **余白 / omission** (岩崎俊一 lineage: unfinished, unsaid)
24. **Dialogue** (second-person address, questioning)

Selection heuristics:
- Emotion-heavy topic → prefer {emotional triggers, story opening, shared experience, sensory description}
- Rationality-heavy topic → prefer {numerical impact, comparison, authority/evidence, problem-solution path}
- Short slogan / headline → prefer {掛詞, paradox, 余白, extremization, interrogative}
- Product-oriented → prefer {benefit translation, feature conversion, comparison}

## Anti-Patterns

- **Treating the derivative taxonomy as 今泉's original canon**:
  citing the "standard 8-direction taxonomy" as part of 1987/1988
  regulation. The correct practice is to label it as a later-derived
  convenience tool, and permit ignoring it.
- **Using the 大谷 case as 今泉 grounding**: "大谷翔平 used マンダラート"
  belongs to the 原田 Method + 松村寧雄 lineage, a different lineage
  from 今泉. Any citation of the 大谷 case must note that it is the
  松村 lineage, and the two must not be conflated.
- **Rigidly mandating the same 8 directions**: requiring every
  ideation pass to use the same fixed 8 directions. 今泉's original
  canon never prescribed fixed content for the 8 directions; forcing
  a fixed set lowers the emergence rate of "unexpected viewpoints".
- **Skipping the fill-in mandate**: leaving 2–3 cells blank "because
  nothing comes to mind". Fill-in mandate is the core mechanism;
  when stuck, shift viewpoint or inject Verbalized Sampling aid —
  do not leave cells empty.
- **Treating the 81 cells as the final answer**: 81 cells are
  **material**, not **product**. Must be followed by
  `ideation-kj-convergence.md` for convergence, otherwise only noise
  is produced.
- **Forcing a single Mandal-Art onto long copy**: doing only one 3×3
  expansion for 3,000+ character long copy. Long copy should use the
  layered approach "framework stages × per-stage Mandal-Art".
- **Ignoring automation boundaries**: letting the LLM run "theme
  selection + 9-cell fill-in + convergence" in a single pass. Both
  theme selection and convergence require human checkpoints,
  otherwise alignment drift accumulates.
