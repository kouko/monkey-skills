---
title: Kansei Engineering and SD Method
tier: 3
---

# Kansei Engineering and SD Method

Tier 3 standard: fully self-contained. Cold-query LLMs often describe
感性工学 at a surface level, routinely confuse Osgood's 3-factor
structure with a 5-point rating scale, and misattribute the Semantic
Differential method to secondary aggregators rather than the 1957
primary. This file is designed so that a worker can act correctly on
it without reading the Primary Sources — which is the Tier 3
self-containment test.

## Primary Sources

- 長町三生 (1989) 『感性工学—感性をデザインに活かすテクノロジー』. 海文堂出版. JP-original book that establishes 感性工学 as an academic term.
- Mitsuo Nagamachi (1995) "Kansei Engineering: A new ergonomic consumer-oriented technology for product development". *International Journal of Industrial Ergonomics*, 15(1):3-11. EN peer-reviewed primary introducing Kansei Engineering to the international ergonomics community.
- Charles E. Osgood, George J. Suci, Percy H. Tannenbaum (1957) *The Measurement of Meaning*. University of Illinois Press. Primary source for the Semantic Differential method and the 3-factor Evaluation / Potency / Activity structure.

## Critical Attribution Corrections

- **SD method attribution.** Earlier `visual-gate.md` L54 attributed
  the Semantic Differential to `J-SEMS, J-STAGE (Osgood三因子), AIIT
  東京都立産業技術大学院大学`. Those are Japanese academic conferences,
  a publication portal, and an applied-research university —
  second-level aggregators, **not** the primary source. The correct
  primary is Osgood, Suci & Tannenbaum 1957 *The Measurement of
  Meaning*. The `visual-gate.md` L54 cleanup lands in commit 2/3;
  this standard is the source of truth going forward.

## What is Kansei Engineering?

感性工学 (Kansei Engineering) is the methodology for translating
ユーザーの感性 — subjective impressions, emotional response, and
aesthetic judgment — into measurable design parameters. It is
empirical: candidate designs are rated on structured semantic
instruments, the ratings are clustered and factor-analyzed, and the
gaps between the intended Kansei profile and the evaluated profile
drive parameter-level design decisions (colour, material, form,
proportion, typography).

Kansei Engineering is **complementary** to ISO 9241-11 usability,
not a replacement. ISO 9241-11 answers "can the user complete the
task with acceptable effort?"; Kansei answers "does the artifact
match the user's subjective aesthetic and emotional target?". A
usable product can still fail Kansei; a Kansei-matched product can
still fail usability. Both are design-time and evaluation-time
concerns.

## The 6-Step Kansei → Design Parameter Workflow

Cold-query LLMs rarely recover this workflow with the correct step
count or ordering. The canonical 6-step process:

1. **Collect Kansei words (感性語の収集).** Gather a broad pool of
   subjective adjective pairs in the target domain. Sources: design
   magazines, user interviews, existing reviews, expert elicitation,
   competitor critiques. For an interior-design example, candidates
   include `暖かい / 冷たい`, `広い / 狭い`, `現代的 / 伝統的`,
   `高級 / 親しみやすい`, `落ち着く / にぎやか`. Aim for 100-200
   raw candidates before clustering.
2. **Cluster Kansei words.** Group semantically related terms,
   eliminate redundancy, and retain **30-50 representative adjective
   pairs**. Use card sorting or hierarchical clustering; the goal
   is a non-overlapping, coverage-complete set.
3. **Construct SD scales.** Convert each retained adjective pair
   into a bipolar 7-point Semantic Differential item (see "SD Method
   Full Definition" below). Randomize polarity direction to detect
   inattentive responding.
4. **Evaluate candidate designs.** 10-20 respondents rate each
   candidate on each SD item. Record per-item response per
   respondent; do not aggregate prematurely.
5. **Plot SD profiles.** Compute per-item means and variances across
   respondents; overlay the evaluated profile against the intended
   brand profile (or a competitor baseline) on a single chart. A
   radar chart or a horizontal bar chart is conventional.
6. **Translate Kansei gaps to design parameters.** Where the
   evaluated profile deviates from the intended profile, identify
   the physical and visual parameters that correlate with the
   deviating Kansei dimensions — colour palette, material finish,
   form proportions, typographic weight, layout density — and
   iterate the design. Re-evaluate after each iteration; Kansei
   Engineering is a loop, not a single pass.

## SD Method Full Definition (load-bearing)

The Semantic Differential (SD 法) is a **7-point bipolar** scale
running from -3 to +3, or equivalently 1 to 7 anchored bipolarly.
Each item presents two antonymic adjectives at the poles; the
respondent marks one position per item.

```
冷たい  -3  -2  -1   0  +1  +2  +3  温かい
        □   □   □   □   □   □   □
```

**Never 5-point. Never unipolar.** Both of those formats break the
Osgood factor structure that Kansei Engineering depends on:

- A 5-point scale under-resolves the centre-to-extreme gradient,
  collapsing real differentiation into noise.
- A unipolar scale (e.g., "rate how warm this is from 0 to 7")
  cannot capture the antonymic pole and produces single-factor
  ratings that cannot be decomposed into Osgood's 3 factors.

## Osgood's 3-Factor Structure (load-bearing)

Osgood, Suci & Tannenbaum 1957 showed that the variance in SD data
across diverse concepts consistently decomposes into **three**
orthogonal factors. A valid SD questionnaire must cover all three;
stacking all items on a single factor (usually Evaluation) produces
degenerate data that cannot diagnose Kansei gaps.

- **Evaluation (評価)** — the good / bad dimension. Accounts for
  the largest share of variance in SD data across domains. JP
  examples: `美しい / 醜い`, `好きだ / 嫌いだ`, `高級な / 安っぽい`,
  `心地よい / 不快な`.
- **Potency (力量)** — the strong / weak dimension. JP examples:
  `重厚な / 軽快な`, `強い / 弱い`, `硬い / 柔らかい`,
  `がっしり / 華奢`.
- **Activity (活動)** — the active / passive dimension. JP examples:
  `活発な / 静かな`, `速い / 遅い`, `騒がしい / 穏やかな`,
  `動的 / 静的`.

## Constructing a Valid SD Questionnaire

- **10-20 adjective pairs is typical.** Fewer than 10 under-determines
  the 3-factor structure; more than 20 causes rater fatigue and drops
  data quality.
- **Cover all 3 Osgood factors.** Do not stack all items on
  Evaluation. A reasonable split is ~40-50% Evaluation, ~25-30%
  Potency, ~25-30% Activity.
- **Randomize polarity direction.** Flip pole order for ~half the
  items (`冷たい ← → 温かい` for half, `温かい ← → 冷たい` for the
  other half) to detect acquiescent / inattentive responding.
- **Pilot test with 3-5 people before fielding** to catch ambiguous
  adjective pairs and scale-direction confusions.
- **Use the same respondent pool across candidates** when comparing
  designs; between-subjects comparisons introduce demographic
  confounds that are hard to isolate.

## Reading an SD Profile

- **Per-item mean** = the group's central perception on that
  dimension.
- **Per-item variance** = degree of disagreement. High variance is
  a diagnostic signal: it usually means the design is ambiguous on
  that dimension and reads differently to different respondents,
  which is itself a Kansei failure.
- **Profile comparison** = overlay the evaluated design profile
  against the brand intent profile or a competitor baseline. The
  *gap* between profiles is what drives step 6 of the workflow.

Do not average across items before plotting; the per-item resolution
is where the design insight lives. A single overall "Kansei score" is
not meaningful.

## When to Use in design-team Workflow

- **`design-brainstorming` Phase 1** — when exploring subjective
  brand targets for a new artifact, draft an intended Kansei profile
  as a target before exploring candidate forms.
- **`visual-design` Step 1** — calibrating candidate visuals
  against the brand Kansei target using a lightweight SD instrument
  (internal pilot, 5-10 respondents) before committing to a
  direction.
- **`visual-gate` Section A** — evaluating whether a finalized visual
  matches the intended Kansei profile using a full SD instrument
  (10-20 respondents, all 3 Osgood factors). The gate passes only
  when the evaluated profile tracks the intended profile within an
  agreed tolerance.
