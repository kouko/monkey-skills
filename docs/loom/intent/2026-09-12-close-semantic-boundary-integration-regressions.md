# 修復語意邊界修改造成的整合契約回歸
originator: kouko
kind: engineering
needs-design: no — only internal skill wording, contract compatibility, and evidence documentation change
evidence: [docs/skill-dogfood/2026-09-12-capture-intent/report.md]
status: confirmed 2026-09-12

## Problem
前一個語意邊界修改已通過聚焦測試與雙模型 dogfood，但最後的完整檢查發現兩個既有跨 plugin 文字契約失敗，研究報告也未說明其中的 raw 路徑只存在於本機，因此目前無法產生有效的 closing-review attestation。

## Proposed outcome
恢復既有共用 intake 與語言政策契約的精確相容性，並清楚標示研究報告中的 raw 執行路徑不是 repository 內容，不改變已確認的語意邊界行為。

## Acceptance
1. `capture-intent` 與 code-only intake 再次使用既有測試要求的同一句必要欄位文字。
2. `capture-intent` 的語言政策再次讓既有 probe 在同一句中辨識 intent 與 English 的關係。
3. 研究報告明示 raw streams 僅存在於作者環境，且聚焦測試、兩項先前失敗的整合測試與既有整合檢查全部通過。

## Constraints
- 保留前一個 intent 已確認的產品語意邊界與雙 host dogfood 結論。
- 只做 reviewer 已指出的相容性與證據敘述修正；不新增 ID、checker rule、gate、station、review loop 或外部 provider 測試依賴。
- 不提交既有未追蹤 raw streams，也不納入既有未提交的 frontmatter description 修改。

## Out of scope
- 重新設計 capture-intent、write-spec 或 write-plan。
- 改變 Acceptance、artifact schema、publication 行為或模型派工規則。
- 修復與本次三個 finding 無關的既有測試問題。

## Open questions
- none
