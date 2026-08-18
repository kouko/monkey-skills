# think-orbit plugin — Part 2（三視圖・編提案・里程碑 commit・SKILL 補完・發佈）— brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff) — **Part 2 of 2**
> **Date**: 2026-08-18
> **Author**: agent (Fable 5) + kouko
> **Umbrella brief**: `docs/loom/specs/2026-08-18-think-orbit-plugin.md`。
> **Sibling / precondition**: `docs/loom/specs/2026-08-18-think-orbit-plugin-part-1.md` — Part 2 **只在**
> Part 1 的真實素材檢查點檔（`docs/loom/dogfood/2026-08-<dd>-think-orbit-real-material.md`）存在後
> 開工；檢查點若推翻 schema，先修訂本 brief 再進 writing-plans。
> **0.1.1 追記（user ruling 2026-08-18）**: plugin 的目的是**思考與規劃**，決策只是其中一種結尾；
> `decision-session` 已更名為 `thinking-session`，入口語彙擴大到「幫我想／想清楚／規劃／整理思路」，
> 且一次坐下不必以 DECISION 收尾。Part 2 的 BI 依此框架複核。
> **STATUS**: DRAFT — 內容於 Part 1 檢查點後複核；BI 編號自本 part 起算。

## Problem

同總覽。Part 2 讓 Part 1 的節點群**可讀、可交付、可回溯**：三張衍生視圖（主線＝這條 CoT 的
可讀版）、把獲勝路徑編成提案、里程碑 commit 讓每次坐下的推進留在 git 歷史裡。

## Users

同 Part 1。

## Smallest End State

- BI-1 — Mainline view (`render mainline`): on top of Part 1's basic full DAG (`views/dag.md`), a collapsed view of the CoT in `seq` order from GOAL to DECISION with each branch folded into one node; regenerated from frontmatter into `views/mainline.md`. [U BI-6]
- BI-2 — Branches view (`render branches --branch <id>`): expands one branch at a time; `exclusive` losers rendered dashed + grey, `complementary` all solid; contradiction between exclusive branches never flagged. [U BI-6, BI-7 render half]
- BI-3 — Assumptions view (`render assumptions --focus <id>`): one assumption at a time with its load-bearing dependents (the impact view of Part 1 becomes this view's focused mode); regenerated, never hand-edited. [U BI-6]
- BI-4 — Proposal outline (`render proposal`): winning mainline node summaries in `seq` order as body skeleton; rejected exclusive branches + the broken assumption / reason as appendix skeleton; SKILL turns the skeleton into prose on request. [U BI-11]
- BI-5 — Git milestones in SKILL.md: commit at GOAL confirmed / each branch opened / assumption confirmed or broken / DECISION written (4–6 per sitting), message carries node/assumption ids; no hash chain. [U BI-10]
- BI-6 — SKILL.md completion: sections for the three views (when to show which, partial rendering, human-only, agent must not read `views/`), compile-proposal flow, milestone flow; body stays ≤4,500 words. [U BI-8 remainder, BI-6]
- BI-10 — Carried debt from Part 1 whole-branch review (first touch of Part 2): frontmatter scalar typing — coerce/validate `id`/`branch`/`branch_type` to str and `seq` to int in the loader, emitting a `problems` line instead of a traceback; plus the 🟢s (three-way mermaid id collision, `seq: 0` truthiness, `claims`/`render_dag` length).
- BI-7 — Release: version bump to 0.2.0 with CHANGELOG entry, tri-language READMEs filled, marketplace description synced, CI green. [U BI-12 release half]

## Current State Evidence

同總覽；Part 2 另加 Part 1 產出的實際路徑（於檢查點後填入 `file:line`）。

- **Forward / Reverse / Error / Data / Boundary**: 見總覽；Part 1 交付後補 `think-orbit/skills/think-orbit/scripts/*.py:line` 的實際接點。
- **Evidence paths**: 總覽 §Evidence paths ＋ Part 1 檢查點檔。

## Decision

Part 2 在 Part 1 驗過的格式上蓋三張視圖、編提案、里程碑 commit，補完 SKILL，正式發佈 0.2.0。
不做的清單同總覽。

- BI-8 — Umbrella (Part 2): three views + proposal outline + milestone flow + SKILL completion + 0.2.0 release land on top of the Part 1 schema.

## Out of Scope

同總覽 §Out of Scope。

## Alternatives Considered

見總覽 §Alternatives Considered。N/A — no additional alternatives for this part: the mechanisms were chosen in the umbrella.

## What Becomes Obsolete

- BI-9 — Part 1's impact-view rendering path is subsumed by `render assumptions --focus` in the same change (deleted, not left as a parallel implementation); Part 1's basic full DAG (`render` → `views/dag.md`) stays as the un-collapsed view.

## Open Questions

- OQ-1 [OPEN] — Does the Part 1 real-material checkpoint change the node/assumption schema? → resolve by reading the checkpoint file before running writing-plans on this part.

## Diagrams

見總覽（兩張圖）。N/A — no new flow beyond the umbrella's diagrams.
