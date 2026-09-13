# 保持 intent 與 spec 的語意邊界
originator: kouko
kind: engineering
needs-design: no — only internal skill instructions and their focused behavioral contract tests change
evidence: [docs/skill-dogfood/2026-09-12-capture-intent/report.md]
status: confirmed 2026-09-12
publication: automatic — authorized 2026-09-12 by kouko

## Problem
Loom 的 intent 與 spec 可能在資訊不足時自行補入未授權的介面、狀態、範圍保證或禁止性行為，讓後續實作忠實完成了一份已經擴張或改變原意的規格。

## Proposed outcome
`capture-intent` 只保存使用者提供的問題、目標、外部可觀察結果與範圍，並把工作流程授權留在既有載體；`write-spec` 只把已確認的 Acceptance 逐條轉成可觀察行為，不把未知介面、持續結果或 out-of-scope 項目升格成新產品決策。

## Acceptance
1. `capture-intent` 不新增未由使用者提供的產品名詞、介面、狀態、範圍維度或保證，且 PR publication 等流程授權不進入產品欄位但仍由既有載體保留。
2. 當已確認結果包含外部可觀察的產品操作而現有規格未涵蓋時，即使 GUI、CLI、API 或檔案輸出介面尚未決定，`capture-intent` 仍以中性理由交給 `write-spec`。
3. `write-spec` 逐條保存上游 Acceptance 的數量、順序與對應，能描述操作後的持續可觀察結果，但不自行命名狀態、生命週期、儲存或持久化方式。
4. `write-spec` 把 out of scope 保持為本次不設計、不實作、不驗證，不轉成能力不存在、禁止、不可逆或單向行為。
5. Codex 與 Claude 的串接 dogfood 都能在 GUI 及至少一種非 GUI 案例中保存上述邊界，現有 contract 與整合測試仍通過。

## Constraints
- 只修改 `capture-intent`、`write-spec` 及其既有測試；用既有段落承載規則，不新增共用 glossary 或 claim 系統。
- 外部可觀察行為包含 GUI、TUI、CLI 參數與輸出、外部 API，以及使用者或外部系統依賴的檔案產物；純內部檔案變更不算。
- 不新增或重編 artifact ID、checker rule、station、subagent、review 節點或持久化來源欄位。
- 保持既有 artifact schema、決策點與 publication 行為。

## Out of scope
- 修改 `write-plan` 或其 task/test ID 契約。
- 提高 skill 自動啟動率或改寫 frontmatter discovery description。
- 恢復舊版 Loom 的完整性矩陣、來源 ledger、Ponytail 式多 agent 階梯或 plan review loop。
- 宣稱單一 dogfood 案例已證明所有模型與需求形狀都穩定。

## Open questions
- none
