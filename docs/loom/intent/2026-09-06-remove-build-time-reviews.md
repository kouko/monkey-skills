# 移除 Build 途中的自動正式審查
originator: kouko
kind: product
needs-design: yes — 審查觸發時機會改變，現有規格仍要求 after-task 與 wave-end checkpoint
status: confirmed 2026-09-06

## Problem
Loom 在實作途中會因個別任務或 wave 自動啟動正式審查。多任務變更因此反覆等待審閱者、處理審查紀錄並重跑驗證，最後仍要再做一次分支結束審查，拖慢整體實作。

## Proposed outcome
保留實作前的正向、負向與高風險對抗案例，實作途中只執行測試與必要的整合檢查，不再自動啟動正式審查。全部任務完成後，在分支結束做一次完整正式審查；其他風險分級、證據與出貨規則維持原樣。

## Acceptance
1. 一個多任務變更完成各項 task 時，只執行該 task 所需的測試與整合檢查，不觸發 after-task 或 wave-end 正式審查。
2. 每條規格在實作前仍有正向與負向案例；高風險 task 仍由獨立對抗者先產生攻擊案例，實作者以這些案例進行測試先行開發。
3. 全部 task 完成後，branch-end review 仍依現有風險分級執行完整審閱、盲跑與對抗驗證，通過後才能進入 Ship。
4. 除了取消 Build 途中的自動正式審查，現有速度模式、角色分離、審查紀錄、證據新鮮度與 Ship gate 行為不改變。
5. 用一個曾觸發中途 checkpoint 的真實多任務變更 replay，新流程的審查派工與流程等待時間少於現行流程，且相同的永久測試與 branch-end finding 仍會被執行或發現。

## Constraints
- 不移除或重新設計風險分級、速度模式、review.json、盲跑報告、review-only HEAD 或 Ship gate。
- 保留 task 層級 TDD、必要整合測試，以及高風險 task 的 adversary-first 行為。
- 自動流程只在 branch end 呼叫正式 review；使用者明確要求的臨時 review 不受限制。
- 現有進行中 worktree 不強制遷移或修改。
- 不修改既有未追蹤的 work/ 內容。

## Value case
GO。現有實測顯示一次中途 wave review 的修正輪可占約 25 分鐘；先只刪除此重複 checkpoint，能以最小改動驗證是否確實縮短多任務實作。

## Out of scope
- 重做整套風險判定或審查證據模型。
- 刪除速度模式或變更各模式在 branch-end 的驗證強度。
- 取消實作前的正向、負向或對抗測試設計。
- 取消 branch-end review、盲跑、對抗驗證或出貨阻擋。
- 依賴圖驅動的局部證據重用。

## Open questions
- none
