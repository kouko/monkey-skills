# CI 失敗後在同一個 task 接續修正
originator: kouko
kind: product
needs-design: yes — Ship 的可見行為新增 CI 失敗後的診斷與多狀態接續流程，目前沒有對應規格
evidence: [loom-code/skills/ship/SKILL.md, loom-code/skills/maintain/SKILL.md, loom-code/scripts/test_simplified_station_text.py]
status: confirmed 2026-09-10
publication: automatic — authorized 2026-09-10 by kouko

## Problem
Loom 已能自動開 PR 並監控 CI，但 required CI 真的失敗時會停止；即使問題可由 Agent 判斷和修正，使用者仍可能需要再次要求繼續。

## Proposed outcome
讓同一個仍在執行的 Codex task 自動讀取失敗檢查與 log，依問題性質沿用既有 Ship、Build 與 Review 路徑接續，不增加新的指令、狀態檔或 gate。

## Acceptance
1. required CI 失敗時，同一個仍在執行的 task 會自動取得失敗 check 與可用 log，不把 publish 的失敗回傳當成整個 task 的終點。
2. 功能或測試問題留在原 change，依 Build 的 test-first 規則做最小修復；既有測試無法覆蓋根因時才新增永久 regression case。Functional digest 改變後重新執行 Closing Review，再次 Ship。
3. PR 標題、PR 說明或其他未寫入 repository 的發布資料可直接修正並沿用仍匹配的 attestation；任何 committed file 變更，包括版本檔，都重新執行 Closing Review。
4. 只有需求或保證需要改變、缺少必要權限、無法取得診斷資料，或外部故障持續存在時，才停止並向使用者說明具體 blocker。

## Constraints
- 只擴寫 Ship、Maintain 與既有契約測試；不修改 publisher 或 checker runtime。
- 不新增 recovery script、failure classifier、結果 schema、ledger、scheduler、checker rule 或持久狀態。
- 監控與自動接續只存在於同一個活躍 Codex task；Desktop 或 task 結束後不恢復。
- 沿用 Closing Review 的最多三個 functional-content digest，不新增另一套 retry 上限。

## Value case
GO — 這是目前 PR 發布後最明顯的人工中斷，而且可透過小幅契約修改完成；若不做，CI 可修復失敗仍會反覆要求使用者手動下達「繼續」。

## Out of scope
- 新增 `loom recover`、`loom repair` 或任何常駐服務。
- 自動重跑無法歸因的 flaky CI。
- 改變 GitHub Actions workflow、branch protection、CI 輪詢週期或 merge 授權。
- 處理已合併 change 的新事故；這類事故仍走 Maintain intake。

## Open questions
- none
