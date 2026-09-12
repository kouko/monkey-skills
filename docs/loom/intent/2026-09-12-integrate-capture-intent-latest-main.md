# 將 capture-intent 邊界修改整合到最新主線

originator: kouko
kind: engineering
needs-design: no — 只整合既有內部 skill 契約與驗證證據，不改變任何使用者介面或產品行為
evidence: [docs/loom/intent/2026-09-12-capture-intent-explicit-fork-confirmation.md, docs/loom/2026-09-12-capture-intent-explicit-fork-confirmation/plan.md]
status: confirmed 2026-09-12
publication: automatic — authorized 2026-09-12 by kouko

## Problem
capture-intent 的內容邊界修改已完成三個允許的審查摘要，但分支所依據的主線已前進，且新版 Loom 的 reviewer 格式重試修正與本分支修改了部分相同檔案。直接產生 attestation 會讓證據在整合主線後失效；直接追加第四個審查摘要又違反 bounded-review 契約。

## Proposed outcome
把已完成的 capture-intent 邊界修改整合到最新 `origin/main`，保留原本確認的欄位語意與低成本限制，再以整合後的單一內容重新取得 closing evidence。

## Acceptance
1. 整合後的分支包含最新主線的 Loom reviewer 修正，也完整保留已確認的 capture-intent 欄位邊界、gap-driven 訪談與單次作者自檢。
2. 整合不新增 intent 欄位、ID、checker rule、station、subagent 或 review loop，也不擴張原 capture-intent 的需求。
3. 整合後的相關測試、套件檢查與 closing review 以同一份最終內容通過，並產生可供安全 publication 使用的 attestation。

## Constraints
- 以最新 `origin/main` 為整合基線；衝突只保留兩邊已發布的必要語意，不趁機重構。
- 沿用 sandbox 外的官方 Claude runner；不授權 Claude 瀏覽 repository。
- 通過 Review 與 publication checks 後可自動 non-forced push 並建立 Ready PR；merge 仍需另行決定。

## Value case
避免用失效證據發布，也避免為了基線更新違反 Loom 自己的三摘要上限。

## Out of scope
- 改寫 capture-intent 的已確認行為或重新設計 spec、plan。
- 新增 reviewer、review round、追蹤 ID 或額外機械 gate。
- 合併 PR。

## Open questions
- none
