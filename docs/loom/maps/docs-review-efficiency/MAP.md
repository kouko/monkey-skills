---
map-id: docs-review-efficiency
schema_version: 3
state: active
---

## Destination

讓技術文件、商業分析與策略文件的 review 不再是開發流程中主要且不可歸因
的成本：缺陷盡可能在 whole-artifact review 前被預防，必要 review 能以穩定
的弱模型找出 load-bearing 問題，且每次循環的品質、時間與來源都可量測。

user-ratified: kouko, 2026-08-31

- DA-1: 技術文件、商業分析與策略文件都有可重播且人工標註的 baseline evidence，能區分 initial-writing、fix-introduced、reviewer variance 與 review-policy effect | state: open | kind: objective
- DA-2: 相對凍結 baseline，文件到接受狀態所需的 review attempts 與可觀測人工／模型成本下降，且 load-bearing finding rate 不下降 | state: open | kind: objective
- DA-3: 至少一個重複出現的 defect class 能在 whole-artifact review 前被預防，且沒有遮蔽 load-bearing finding | state: open | kind: objective
- DA-4: capability ownership 依量測證據落在既有 authoring/reviewer stage 或新的穩定邊界，並由使用者裁定 | state: open | kind: evaluative

## Notes

- 第一個 delivery arc 是 `docs/loom/2026-08-31-docs-review-baseline/`；它只建立量測地基，不等於 Destination 達成。
- 弱模型是 baseline 的固定測量條件：目前 Claude Code economy=`haiku`、Codex economy=`gpt-5.6-luna`，每個 scored run 仍記錄實際解析身分。
- Map 涵蓋三種文件，但 corpus 代表性尚未成立；不能用歷史 hard cases 宣稱日常平均改善。
- 風險前置結果：目前最高風險皆可由量測或人定門檻回答，不需要 prototype ticket。

## Decisions-so-far

## Not-yet-specified (fog)

- F-1: 三種文件各需要多少、哪些 case mix 才足以代表實際 review 工作，而不只代表歷史 hard cases？
- F-4: 哪一個 repeatable defect class 最適合第一個 pre-review prevention check，且如何證明沒有 masking？
- F-5: 改善後是否仍存在既有 loom skills 無法承接、足以支持 `loom-docs` 的穩定責任邊界？

## Out-of-scope

- 在 baseline evidence 前建立涵蓋所有文件工作的 omnibus `loom-docs` plugin。
- 以最強模型作為 baseline reviewer；本圖的第一輪量測固定使用弱模型 economy cohorts。
- 本輪自動調整 reviewer prompt、實作 pre-review check，或宣稱 production review 已改善。
- 把不同 provider 的不相容 usage 單位強制換算成單一貨幣成本。
