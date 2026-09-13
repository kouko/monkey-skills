# 留存可公開的 capture-intent dogfood 原始證據
originator: kouko
kind: engineering
needs-design: no — only archived experiment evidence and its documentation change
evidence: [docs/skill-dogfood/2026-09-12-capture-intent/report.md]
status: confirmed 2026-09-12
publication: automatic — authorized 2026-09-12 by kouko

## Problem
先前的 capture-intent dogfood 原始執行紀錄只留在本機，無法由 repository 的後續讀者核對；但原檔包含本機環境、session 與 connector metadata，不能直接公開。

## Proposed outcome
在 repository 留存仍可重讀實驗輸入、模型輸出、評分與必要統計的清理版證據，同時讓未清理原檔只留在本機。

## Acceptance
1. 79 份清理版證據可從 repository 讀取，JSON 與 JSONL 全部仍可解析，且檔案集合與本機原檔一致。
2. 公開證據不包含 system/hook/rate-limit 環境事件、thinking signature、session/request identifiers、絕對本機路徑、email、connector 狀態或工具與 plugin inventory。
3. 研究報告清楚區分已提交的清理版證據與未提交的本機原檔，並說明清理內容。

## Constraints
- 不修改原始實驗結論、評分或模型可見回答。
- 未清理原檔留在本機且不進 Git。
- 不新增 Loom station、gate、checker rule、ID 或 review loop。

## Out of scope
- 重新執行 dogfood。
- 修改 capture-intent、write-spec 或 write-plan 行為。
- 將本機環境 metadata 留作公開研究資料。

## Open questions
- none
