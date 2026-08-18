---
id: carriers_can_carry_inputs
status: open
statement: brief Decision、plan Decision Log、commit Decision trailer、review verdict 四種載體都能長同一個 inputs 欄位而不必重設計
breaks_if: 第一次 spike 發現任一載體（最可能是 commit trailer 或 review verdict）塞不下 ref 清單，得改成另一種形狀
source: sources/2026-08-18-loom-decision-trail-as-dag-view-via-think-orbit-render.md §The gap
branch: b_reuse_render
---
