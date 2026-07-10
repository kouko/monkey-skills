# Plan: daily-news-digest multi-viewpoint (多空對照/分歧點) synthesis

Source brief: docs/loom/specs/2026-07-08-daily-news-digest-multiview-synthesis.md
Total tasks: 4
Critical-path depth: 3 (Task 1 → Task 2 → Task 3; Task 4 parallel)
Execution order: parallel-where-possible (Task 1 + Task 4 in wave 1)
Plan-document-reviewer verdict: PASS (2026-07-08)

Note: skill-TEXT engineering — each task's "RED test" is a cold-reader/dogfood
acceptance observable, not a unit test. No test files. Verification is the
STEP-6/dogfood run on the 2026-07-04 semiconductor-correction debate.

## Task 1 — STEP 4: cluster by debate, not only by event
- Description: Extend SKILL.md STEP 4 so clustering groups sources by "the same
  underlying event **OR** the same underlying question/debate" — so opposing
  stances on one question land in ONE cluster instead of separate stories. Add a
  one-line worked example (the 2026-07-04 correction "healthy vs bubble" debate =
  one debate-cluster, not three items).
- Module: obsidian/skills/daily-news-digest/SKILL.md (STEP 4 only)
- Files touched: obsidian/skills/daily-news-digest/SKILL.md
- Context paths:
  - obsidian/skills/daily-news-digest/SKILL.md  (STEP 4 :114-148)
- Acceptance:
  - RED: a cold reader applying STEP 4 to a day where 3 KOLs take bull/bear/neutral
    stances on one question currently clusters them as separate stories (STEP 4
    :117-123 says "same underlying story/event" only).
  - GREEN: STEP 4 text instructs clustering by event OR debate, with the worked
    example; a cold reader groups the bull/bear/neutral trio into one debate-cluster.
- Dependencies: none
- Independent: true
- Brief item covered: "STEP 4 cluster-by-debate: cluster by the same event OR the
  same underlying question/debate, so bull and bear on one question land in one
  cluster instead of separate stories."

## Task 2 — STEP 6: the 多空對照/分歧點 block spec + kill 漏引
- Description: In SKILL.md STEP 6, upgrade the soft "surface the disagreement"
  (:243-246) into a concrete required artifact: when the synthesizer finds ≥2
  sources taking materially-differing stances on the same question (LLM-judged
  trigger; category anchor list is an anchored-open HINT, explicitly NOT a hard
  gate), emit a compact 多空對照/分歧點 block. Make the 分歧點 row mandatory
  (false-balance guard: name the real axis + whether it's a genuine split vs one
  side being consensus). State that EVERY source in a cluster MUST appear in the
  Source Index under that story (kill 漏引). Point rendering detail to
  digest-format.md (Task 3).
- Module: obsidian/skills/daily-news-digest/SKILL.md (STEP 6 only)
- Files touched: obsidian/skills/daily-news-digest/SKILL.md
- Context paths:
  - obsidian/skills/daily-news-digest/SKILL.md  (STEP 6 :222-264; STEP 7 :266-310; Hard rules :388)
- Acceptance:
  - RED: STEP 6 (:243-246) only says "surface the disagreement — that tension is
    signal" with no required output shape; a cold reader produces no structured
    multi-view block and may 漏引 cluster sources.
  - GREEN: STEP 6 specifies (a) LLM-judged trigger + category-as-hint-not-gate,
    (b) mandatory 分歧點 row false-balance guard, (c) all-cluster-sources → Source
    Index; a cold reader on the 2026-07-04 correction debate emits a block and
    cites every clustered source.
- Dependencies: Task 1 completes first (same file; the block operates on the
  debate-cluster Task 1 defines).
- Independent: false
- Brief item covered: "an in-story compact 多空對照/分歧點 block … Trigger = LLM
  judgment, NOT a fixed category gate … The 分歧點 row is mandatory … kill 漏引."

## Task 3 — digest-format.md: news-story template block + shared house-style
- Description: Add the 多空對照/分歧點 block to the news-story Output template in
  references/digest-format.md (a small table when ≥3 stances; the 正方/反方/分歧點
  three-row form when exactly 2), placed after the narrative / before the optional
  visual. Factor ONE shared "多空/分歧 house-style" spec that both the news-tier
  block and the existing knowledge-tier `整合分析` template (:243) reference, so
  the two shapes don't diverge.
- Module: obsidian/skills/daily-news-digest/references/digest-format.md
- Files touched: obsidian/skills/daily-news-digest/references/digest-format.md
- Context paths:
  - obsidian/skills/daily-news-digest/references/digest-format.md  (Output template :105-283; 整合分析 :243; 來源索引 :26-46)
- Acceptance:
  - RED: the Output template (:165-224) has no multi-view block; the 整合分析
    template (:243) lives only in the knowledge tier with no shared spec.
  - GREEN: news-story template shows the block with the ≥3→table / ==2→rows rule,
    and a single house-style spec is referenced by both news + knowledge shapes.
- Dependencies: Task 2 completes first (doc-mirrors-doc: the template renders what
  STEP 6 specifies).
- Independent: false
- Brief item covered: "add the block to the news-story template + share one 多空/
  分歧 house-style spec with the existing knowledge-tier 整合分析 template."

## Task 4 — arc-tracking.md: 機構觀點 → 觀點交鋒 stance tracking
- Description: In references/arc-tracking.md, extend the optional 機構觀點 section
  (:66-95) into 機構觀點/觀點交鋒 so a recurring debate's stance evolution over time
  is captured — dated rows, a 多/空/中性 lean tag per row, and the debate's 分歧點.
  Keep the existing sell-side price-target rows valid (additive, not a replacement).
- Module: obsidian/skills/daily-news-digest/references/arc-tracking.md
- Files touched: obsidian/skills/daily-news-digest/references/arc-tracking.md
- Context paths:
  - obsidian/skills/daily-news-digest/references/arc-tracking.md  (機構觀點 :66-95)
- Acceptance:
  - RED: 機構觀點 (:90-94) holds only sell-side/bank price-target rows; no
    stance-over-time / lean-tagged debate tracking.
  - GREEN: section documents a 觀點交鋒 row shape (date + who + lean 多/空/中性 +
    分歧點), additive to the existing house-view rows; a cold reader records a dated
    bull/bear stance row for a recurring debate.
- Dependencies: none
- Independent: true
- Brief item covered: "Extend the arc book's optional 機構觀點 section so a
  recurring debate's stance evolution over time is captured … A lean tag
  (多/空/中性) per row."

## Notes
- Wave 1 (parallel, disjoint files): Task 1 (SKILL.md STEP 4) + Task 4
  (arc-tracking.md). Wave 2: Task 2 (SKILL.md STEP 6, after Task 1, same file).
  Wave 3: Task 3 (digest-format.md, after Task 2, mirrors it).
- Task 1 & Task 2 share SKILL.md → sequential despite both being "SKILL edits"
  (file-level non-disjoint); declared via Task 2 Dependencies.
