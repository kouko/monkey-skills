# 縮減三個 Loom skill entrypoint
originator: kouko
kind: engineering
needs-design: no — internal skill refactor with no new user-visible surface
status: confirmed 2026-09-13
publication: automatic — authorized 2026-09-13 by kouko

## Problem

`write-plan`、`capture-intent` 與 `independent-advisor` 的 `SKILL.md` 已逼近各自適用的字數門檻，讓後續必要修改容易直接撞上檢查上限，也讓 skill 觸發時載入過多重複或可按需讀取的內容。這影響維護這三個 Loom skill 的人，並提高每次執行的上下文成本。

## Proposed outcome

三個 skill 都有較精簡的 entrypoint 與可維護的內容分層，同時保留現有外部行為與契約。

## Acceptance

1. 三個 `SKILL.md` 都明顯縮短，並對照各自適用的字數門檻提供可重現的前後測量。
2. 三個 skill 的代表性使用情境在重構前後維持等價，且既有契約、必要流程與失敗邊界沒有遺失。
3. 每個 skill package 都分開證明達到既定的實質減量門檻，而不是只把文字搬到另一個檔案。
4. 三個獨立安裝的 Loom plugin 仍通過結構、邊界、交叉引用及相關 package 測試。

## Constraints

- 這是保持行為不變的重構；不新增、刪除或調整 skill 能力與輸出契約。
- 依 `skill-refactor` 的 baseline、等價性、字數減量與 invariant gate 逐一處理三個 skill。
- 保留 `loom-code`、`loom-design` 與 `loom-workflow` 可各自獨立安裝的邊界，不建立跨 plugin 的私有檔案依賴。
- 每個 skill 的重構與證據可獨立判定；其中一個失敗不得以另外兩個的減量抵銷。

## Out of scope

- 重構其他 Loom skills。
- 改變 Loom station、決策點、review、publication 或 second-vendor 政策。
- 以新增功能、輸出調校或重新設計 workflow 取代等價重構。

## Open questions

- none
