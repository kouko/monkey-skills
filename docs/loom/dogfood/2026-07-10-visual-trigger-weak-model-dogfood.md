# Weak-model dogfood: ascii-graph trigger card + loom visual-defaults preload

Date: 2026-07-10 · Model under test: claude-haiku-4-5 (headless `claude -p`)
Method: docs/loom/memory/headless-branch-plugin-testing-recipe.md
(--plugin-dir onto unpushed branches, neutral empty cwd, probe-before-battery)
Branches: more-visualization (ascii-graph-toolkit 0.5.0, PR1) ·
loom-visual-preload (loom-pipeline 0.7.0, PR2)
Plan under test: docs/loom/plans/2026-07-10-ascii-graph-trigger-fix.md

## Arms and results

Prompt A (PR1): "用純文字幫我畫一張架構圖：使用者 → API 閘道 → 三個後端服務…全部用中文標籤，我要貼到 PR 描述裡。"
Prompt B (PR2/combined): "我在幫新專案選資料庫：PostgreSQL 還是 SQLite？幫我比較兩者，然後畫一張選擇流程圖，我會貼到 PR 描述裡。"

| Arm | Config | Runs | Skill invoked | Notes |
|---|---|---|---|---|
| PR1 probe | 0.5.0 card | 1 | — | card text quoted verbatim (injection confirmed) |
| PR1 branch | 0.5.0 card | 2 | **2/2 TOOL** | Skill(ascii-graph) with CJK node spec |
| PR1 baseline | installed 0.4.0, no card | 2 | **0/2** (hand-drawn) | box chars in text; visible arrow/width drift in one run |
| PR2 probe | 0.7.0 preload | 1 | — | §(b) bullet quoted verbatim (preload confirmed live) |
| PR2 branch alone | 0.7.0 preload, NO PR1 card | 2 | **0/2** | 1× hand-drawn (violates loaded rule), 1× deferred to clarifying Qs |
| PR2 baseline | installed 0.6.1 | 2 | 0/2 | 1× mermaid, 1× hand-drawn; markdown table already 2/2 at baseline |
| Combined (= production) | PR1 card + PR2 preload | 2 | **2/2 TOOL** | run 2 exercised the verify-loop (align.py, 3 iterations) |

## Findings

1. **PR1 trigger card: validated.** Flips weak-model behavior 2/2 vs 0/2.
2. **PR2 preload alone: mechanism works, behavior doesn't move.** The rule
   text is provably in context (probe) yet haiku ignored it 2/2 — the
   preload fixes "rule never read" (1/216 sessions), not "rule read but
   not obeyed". Imperative action-moment phrasing (the PR1 card) is what
   moves behavior; descriptive relay-discipline prose does not.
3. **Combined arm (what actually ships): 2/2 tool usage.** Trigger
   behavior is carried by the PR1 card; the PR2 preload's residual value
   is loom-contract visibility (relay/rollup discipline for orchestrators),
   not weak-model triggering. Table-axis showed no measurable delta
   (baseline already renders markdown tables 2/2).
4. Sample sizes are small (2/arm); treat as directional gate-check, not
   a measured rate. Post-ship telemetry re-run (same scripts as the
   2026-07-10 analysis session) is the real A/B.

Distilled practice: docs/loom/memory/imperative-trigger-cards-beat-descriptive-preloads.md
