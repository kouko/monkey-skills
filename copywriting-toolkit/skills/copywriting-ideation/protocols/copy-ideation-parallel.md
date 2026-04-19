# Protocol: Copy Ideation Parallel（散らかす → 選ぶ 2-stage parallel ideation）

**When to use**: When you need to generate multiple copy angles from a value proposition. Typical cases — landing page headline candidate ideation, キャッチコピー selection workshops, キャンペーン concept divergence, or Phase 0 preparation before running a writing protocol (providing seed material for long- / mid- / short-form copy protocols).

**Output**: 3-5 winning angles converged through KJ method (each angle accompanied by "なぜ良いか" 3 reasons), feeding the Phase 3 seed of subsequent writing protocols (long-form → Affinity seed / mid-form → Benefit seed / short-form → headline seed).

**Grounds on**: `../standards/ideation-mandalart.md`, `../standards/ideation-kj-convergence.md`, `../standards/ideation-taniyama-discipline.md`, `../standards/verbalized-sampling.md`

This protocol represents the ideation layer of copywriting-team. It is invoked as the Phase 0 of writing protocols (write-long / mid / short-form-copy), or executed as an independent ideation workshop.

Role split:
- main worker: dispatch / convergence supervision / human checkpoint proxy (via evaluator agent)
- parallel subagents: 散らかす stage (Phase 1) only, divergence from independent contexts
- KJ convergence (Phase 2) and 谷山 review: handled by main worker + human / evaluator checkpoint
- writing protocols: receive Phase 3 handoff and branch per copy form

## Phase 1: 発散（parallel subagents）

Main worker receives three required inputs, then decides the combination of divergence tools.

1. **Input confirmation**:
   - value proposition / key message (planning-team output, or directly specified by the user)
   - target audience description (persona draft or segment definition)
   - copy form (long / mid / short, medium) — affects the downstream handoff target

2. **Tool combination decision**: `ideation-mandalart.md` §「輔助方向庫」 provides 16+ derivative directions (not 今泉 original canon — free to pick or ignore).
   - Heavy emotion topic / clear cultural context → **Mandal-Art 8 fan-out recommended**. Pick 8 directions from the auxiliary direction library per the "selection strategy".
   - Topic direction still unclear / need large vocabulary variation in short time → **VS single-agent recommended** (skip the Mandal-Art structural layer).
   - If using Mandal-Art, still use VS as vocabulary-layer diversification (`verbalized-sampling.md` §Mandal-Art との補完関係 Pattern B).
   - For long-form Phase 0 use, prefer the layered operation "PASONA stage × independent Mandal-Art per stage" (`ideation-mandalart.md` §應用於 copywriting — long-form has low direct applicability; independent expansion per stage is canonical).

3. **Direction selection (Mandal-Art path only)**: Decide 8 directions following `ideation-mandalart.md` §輔助方向庫 §選擇策略:
   - Emotion-heavy topic → lean toward {情感觸發, 故事開頭, 共通体験, 感官描寫}
   - Reason-heavy topic → lean toward {數字刺激, 比較對照, 権威 / 証拠, 問題解決路徑}
   - Short copy / tagline topic → lean toward {掛詞, 逆説, 余白, 極端化, 疑問句式}
   - Product-oriented topic → lean toward {ベネフィット表達, feature 轉譯, 比較對照}
   - You may mix 8 directions across the 4 axes above, or concentrate on a single axis. Record the selection rationale for downstream verification.
   - In the handoff, explicitly note that the "auxiliary direction library" is a later derivation (not the 今泉 1987 original canon). Do not conflate it with the canon (`ideation-mandalart.md` §Critical Attribution Corrections #1).
   - Do not hard-fix the 8 directions (same 8 every time). Fixing them lowers the emergence rate of "unexpected viewpoints" (`ideation-mandalart.md` §Anti-Patterns).

4. **Subagent prompt components** (each subagent prompt must contain three elements):
   - Single direction theme ("生活情境", "掛詞", etc., taken from `ideation-mandalart.md` §輔助方向庫)
   - Verbalized Sampling template: produce 8 candidates + probability for each (follow `verbalized-sampling.md` §Pattern A)
   - **散らかす principle** (`ideation-taniyama-discipline.md` §階段 1): no self-censorship, quantity over quality, allow "intentionally weird directions" (explicitly state the 80% safe + 20% unusual ratio)

5. **Parallel dispatch**: Use the `dispatching-parallel-agents` pattern, 8 subagents concurrently. Each subagent outputs 8 candidates → 64 total (VS single-agent path outputs 40-80). Main worker performs no quality filtering at this stage.

6. **Mode collapse check**: Check the aggregate output across all subagents; watch for concentration in a high-probability neighborhood. If skewed, mode collapse is not being mitigated (`verbalized-sampling.md` §Pattern C). Instruct re-generation only for the affected subagents.

7. **Canonical candidate quantity target**: Do not advance to Phase 2 until 64-100 candidates are accumulated. Converging under the quantity threshold makes the "selection stage" non-functional and keeps you inside the known safe zone (`ideation-taniyama-discipline.md` §階段 1 量の目安). If subagents cannot produce the quantity, change directions and dispatch additional runs.

## Phase 2: Convergence（KJ 6 stages + 谷山 「なんかいいよね禁止」 review）

Run `ideation-kj-convergence.md` §6 stages definition and `ideation-taniyama-discipline.md` §「なんかいいよね禁止」ルール in parallel.

1. **Theme setting (Stage 1)**: Restate the focal question for this convergence. Example: "Select 3-5 winning LP headlines for product X", "Select 3-5 winning キャッチ candidates for キャンペーン Y". If the theme is vague, return to planning-team to re-confirm the value prop. If the theme granularity is too coarse (e.g., "for the entire product line"), convergence cannot function — narrow to a single product / single appeal axis.

2. **Label creation (Stage 2)**: 64 candidates → 64 cards. **One card, one concept**. Each card records: copy body / Mandal-Art direction / VS probability. Mixing multiple concepts on one card breaks granularity in later grouping (`ideation-kj-convergence.md` §階段 2).

3. **Group editing (Stage 3)**: embedding-assisted initial clusters (10-15 groups) → human (or evaluator agent) checkpoint for "kansei affinity" re-placement.
   - Use embedding as the "initial cluster draft"; do not call full automation "KJ method" (`ideation-kj-convergence.md` §Anti-Patterns).
   - Do not pre-classify using existing taxonomies (persona / AIDMA / 4P) — "let the chaos speak".
   - In the human checkpoint, re-place the 3-5 cards that feel "not close" or "should be split".
   - Hierarchize: small groups (2-5 cards) → medium groups → large groups.

4. **Labeling (Stage 4)**: For each large group, name "the essence this copy group collectively appeals to" in one line.
   - Category names ("number-related", "price-related") are NG.
   - A narrative ("number-appeal group that reassures the rational type", "story-pulled-in group for the emotional type") is canonical.
   - LLM proposes 3-5 candidates → human / evaluator makes the final choice (`ideation-kj-convergence.md` §自動化邊界表).

5. **Diagramming (A-type, Stage 5)**: Spatially place large groups on 2 axes (e.g., rational ↔ emotional × short ↔ long, or action-pushing ↔ state-proposal × individual ↔ shared experience).
   - This task is LLM-ineligible; human / evaluator agent handles it (`ideation-kj-convergence.md` §自動化邊界表).
   - If using LLM, stay at a text hierarchy list (no spatial placement).
   - One value of A-type is visualizing "empty bands" (regions where no group is placed) — discover whitespace to differentiate from competitors.

6. **Narrativization (B-type, Stage 6) + 谷山 review**:
   - Narrativize "core insight → the story of main groups → next action" as 1-2 A4 pages.
   - As the "selection stage", cut out 3-5 winners.
   - Attach to each winner **"なぜ良いか" 3 items** (`ideation-taniyama-discipline.md` §「なんかいいよね禁止」ルール):
     1. What is conveyed to whom
     2. What is new relative to existing similar copy
     3. What resonates in the target's life / context
   - Candidates for which the 3 items cannot be concretized are excluded (description-type not accepted).
   - Self-question whether you are choosing from the writer's perspective: "Does it only look good because you know your own ideation route?" (`ideation-taniyama-discipline.md` §階段 2 tip「自分の最初のお気に入りを疑う」).
   - A reader-perspective re-review is mandatory: judge by what a first-time reader feels, not by the writer's attachment.

## Phase 2b: Organizing the also-rans (optional)

After cutting out the 3-5 winners with KJ B-type, keep a separate list of **3-5 runner-up candidates** from the also-rans. Reusable for A/B tests / variant proposals / Phase 4 rewrite variants (`copy-audit.md` Phase 4).

1. Within each large group, record the "second place" that missed the winner slot as a runner-up.
2. Note the reason briefly ("stopped at description-type", "writer-leaning", "feels derivative", etc.).
3. Attach this runner-up list as an appendix at handoff time.

## Phase 3: Handoff

Pass the 3-5 winning angles + "なぜ良いか" 3-item rationale to the subsequent protocol. Handoff targets branch by copy form: long-form → `write-long-form-copy.md`, mid-form → `write-mid-form-copy.md`, short-form → `write-short-form-copy.md`, existing-copy improvement → `copy-audit.md` (material for Phase 4 rewrite variants).

| Next protocol | Positioning of winning angles |
|---|---|
| `write-long-form-copy.md` | Affinity seed (共感 starting point of 新 PASONA / PASBECONA) + Benefit seed as needed |
| `write-mid-form-copy.md` | Benefit seed (opener line of BEAF stage 1) |
| `write-short-form-copy.md` | headline seed (raw material before polishing to 7-15 字) + pre-selection of 切入点 |
| `copy-audit.md` | Seed for rewrite variants (on user request) |

Handoff must always pass the following:
- 3-5 winning angles (body + Mandal-Art direction)
- "なぜ良いか" 3 items per angle
- Convergence A-type diagram (human-drawn spatial placement; text hierarchy list is acceptable)
- 3-5 "runner-up" candidates from the also-rans (for A/B variants)
- Direction selection rationale recorded in Phase 1 (subsequent protocols / evaluator use this for verification)
- Total candidate count from the divergence stage / VS probability distribution skew summary (evidence that mode collapse does not persist)

The handoff document format is free, but at minimum separate the 3 blocks: `winning angles / 3-item rationale / runner-ups`. A handoff that omits the 3-item rationale causes downstream protocols to write description-type copy.

## Rules

- Main worker sticks to **divergence / convergence pipeline management and human checkpoint proxying**. Divergence by subagents, convergence by KJ process, and human-judgment points (final group editing / labeling / A-type / winner selection) must have explicit checkpoints.
- Always separate the 2 stages of divergence / convergence. Do not mix divergence and convergence in the same subagent (`ideation-taniyama-discipline.md` §Anti-Patterns「散らかす段階で自己審査する」).
- When using Mandal-Art 8 directions, clearly note that the "auxiliary direction library" is a later derivation (not the 今泉 1987 original canon) and is freely swappable (`ideation-mandalart.md` §Critical Attribution Corrections).
- Do not omit the Verbalized Sampling probability field. Probability is the core of the triggering (`verbalized-sampling.md` §Anti-Patterns).
- Group editing and labeling in KJ method require a human / evaluator checkpoint. Do not complete with embedding cosine similarity alone (`ideation-kj-convergence.md` §Anti-Patterns).
- At winner selection, do not allow "なんかいいよね". Do not adopt candidates for which the 3-item rationale cannot be written.
- Do not enter convergence before reaching the 64-100 candidate quantity (`ideation-taniyama-discipline.md` §階段 1 量の目安).
- Default convergence count is **3-5 winners**. Fewer than 2 means selection likely failed; more than 6 means convergence likely failed.
- For long-form Phase 0, prioritize the layered operation "PASONA stage × independent Mandal-Art per stage". Running a single 3×3 once and using it as the material for an entire long-form is a canonical violation (`ideation-mandalart.md` §Anti-Patterns).
- For mid-form Phase 0, consider independent expansion per BEAF stage (B / E / A / F) (`ideation-mandalart.md` §適用度: mid-form is medium fit).
- For short-form Phase 0, either embed the 5 切入点 (`short-form-catchcopy-canon.md` §5 種切入点決策樹) into the 8 directions, or weight 掛詞 / 余白 / 極端化 JP short-form lineages heavily.

## Anti-Patterns

- **Main worker writes all 8 directions alone**: Without parallel subagents, mode collapse is not mitigated + the human's thought habits leak in. Each direction must diverge from an independent subagent's context.
- **1-shot 5 candidates and done**: Writing 5 directly without going through 64-100 candidates. Breeding ground for mode collapse and "なんかいいよね".
- **Treating 大谷翔平 OW64 as 今泉 Mandal-Art**: Ohtani's case is 原田隆史 Method + 松村寧雄 lineage — a different lineage from 今泉 マンダラート (`ideation-mandalart.md` §Critical Attribution Corrections #2).
- **Implementing "What × How four-quadrant" as 谷山 method**: Not in the original book (`ideation-taniyama-discipline.md` §Critical Attribution Corrections #1). Canonical is three stages + なんかいいよね禁止 + 31 training.
- **Completing KJ method with embeddings only**: Kansei-affinity final judgment belongs to human / evaluator. Embedding stays as the "initial cluster draft" (`ideation-kj-convergence.md` §Anti-Patterns).
- **Asking LLM to draw the A-type diagram**: Spatial language requires human cognition. Even a text hierarchy list cannot express spatial placement / opposition.
- **Handoff without "なぜ良いか" 3 items on winners**: Increases the risk that subsequent protocols write description-type copy. Always attach the 3-item rationale.
- **Running Mandal-Art only once for long-form Phase 0**: Long-form prefers the layered "PASONA stage × independent Mandal-Art per stage" (`ideation-mandalart.md` §應用於 copywriting 適用度).
- **Pre-announcing winning candidates in the divergence stage**: Kills divergence freedom. Winners are decided only after Phase 2 KJ + 谷山 review.
- **Immediately deleting also-rans**: The 3-5 runner-ups are reusable for A/B variants / audit rewrites / later campaigns. Keep them in an appendix.
- **Dropping the VS probability field and ending at "list 5"**: Paper §4 Ablation shows the effect vanishes. Probability is the triggering core (`verbalized-sampling.md` §Anti-Patterns).
- **Using category names on labels**: "quality-related", "price-related" does not verbalize the group's narrative. Labels must be the narrative of "what this group is saying".
- **Handoff at narrow KJ (stages 2-3 only)**: For copywriting, you usually need through stage 6 (B-type narrativization + winner selection). Stopping at stages 2-3 is incomplete as decision material.
