# 縮減 Loom skill descriptions
originator: kouko
kind: engineering
needs-design: no — internal skill metadata and routing refactor with no new user-visible surface
status: confirmed 2026-09-13
publication: automatic — authorized 2026-09-13 by kouko

## Problem

Loom skills 的 descriptions 重複承載跨 skill 路由與流程說明，使初始 skill 清單接近上下文預算上限，也增加每次工作階段都必須載入的文字量。這影響所有安裝 Loom plugins 的使用者，並可能讓其他 skills 從初始清單中被縮短或省略。

## Proposed outcome

Loom plugins 具有精簡且仍能正確觸發的 skill descriptions，並以 plugin 入口集中處理共用路由資訊。

## Acceptance

1. 所有 Loom skill descriptions 的總長度明顯降低，並提供可重現的前後字元與 token 測量。
2. plugin 層級、直接 skill、相鄰 skill 與不應觸發的代表性請求仍會被正確路由。
3. 現有 Loom workflow、輸出契約、直接 skill 呼叫與獨立 plugin 安裝能力維持不變。
4. Loom skills、manifest、交叉引用、邊界與相關 package tests 全部通過。

## Constraints

- 使用 `using-*` 作為每個 Loom plugin 的入口結構，集中共用路由資訊。
- 子 skill descriptions 保留各自獨特的用途與觸發條件，不把完整流程放進 metadata。
- 不變更 skill 的實際工作流程、輸出格式、決策點或 publication 行為。
- 保留 `loom-code`、`loom-design` 與 `loom-workflow` 的獨立安裝邊界。

## Out of scope

- 隱藏、合併或刪除現有子 skills。
- 改變現有 skills 的 implicit invocation policy。
- 重寫 SKILL.md 主體以縮短執行時上下文。
- 修改非 Loom plugins 的 descriptions。

## Open questions

- none
