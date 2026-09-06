# 把實作前與實作中的正式審查縮成風險觸發與分支末一次
originator: kouko
kind: product
needs-design: yes — 審查觸發時機會改變，現有規格仍要求 after-task 與 wave-end checkpoint
status: closed 2026-09-06 — branch 2026-09-06-remove-build-time-reviews

## Problem
Loom 目前不只在個別任務或 wave 後自動啟動正式審查，產品變更也在實作前固定執行多位審閱者、對抗審查與盲跑。即使最後仍要做一次完整分支結束審查，前面仍反覆等待審閱者、處理審查紀錄並重跑驗證，拖慢整體交付。

## Proposed outcome
所有變更在實作前都保留規格準備檢查與正向、負向案例；只有資安、隱私、不可逆資料、公用契約、跨系統架構或明顯歧義等高風險變更，才執行一次聚焦規格審閱，而且不做規格盲跑。實作途中只執行測試與必要整合檢查，不自動啟動正式審查。全部任務完成後，在分支結束做唯一一次完整正式審查。

## Acceptance
1. 實作前的機械檢查會阻擋沒有正向案例、負向或邊界案例、未解決使用者決策，或未說明規格審閱風險判定的計畫。
2. 一般變更不執行正式規格審閱；高風險變更只執行一次由單一獨立審閱者同時檢查規格與對抗面，不執行規格盲跑。
3. 一個多任務變更完成各項 task 時，只執行該 task 所需的測試與整合檢查，不觸發 after-task 或 wave-end 正式審查。
4. 高風險 task 仍由獨立對抗者先產生可執行的攻擊案例，實作者以正向與負向案例進行測試先行開發；這個步驟不產生 review verdict。
5. 全部 task 完成後，branch-end review 仍依現有風險分級執行完整審閱、盲跑與對抗驗證，通過後才能進入 Ship；這次由 Claude 擔任第二家模型審閱者。
6. 除了縮減實作前與實作中的自動正式審查，現有速度模式、角色分離、審查紀錄、證據新鮮度與 Ship gate 行為不改變。
7. 用一個曾觸發中途 checkpoint 的真實多任務變更 replay，新流程的審查派工與流程等待時間少於現行流程，且相同的永久測試與 branch-end finding 仍會被執行或發現。

## Constraints
- 規格審閱風險由規格中的明確宣告承載；舊規格未宣告時維持原本必須審閱的安全預設。
- 不移除或重新設計現有 branch-end 風險分級、速度模式、review.json、盲跑報告、review-only HEAD 或 Ship gate。
- 保留 task 層級 TDD、必要整合測試，以及高風險 task 的 adversary-first 行為。
- 除了高風險規格的一次聚焦審閱，自動流程只在 branch end 呼叫正式 review；使用者明確要求的臨時 review 不受限制。
- 現有進行中 worktree 不強制遷移或修改。
- 不修改既有未追蹤的 work/ 內容。

## Value case
GO。現有實測顯示一次中途 wave review 的修正輪可占約 25 分鐘，而本變更的規格階段也已超過約 45 分鐘。把預設規格審閱改成風險觸發，並刪除 Build 重複 checkpoint，才能避免瓶頸只從實作途中搬到實作之前。

## Out of scope
- 自動理解任意自然語言並判斷風險；風險類別由規格作者明確宣告，分支末仍由既有機械分類保護。
- 刪除速度模式或變更各模式在 branch-end 的驗證強度。
- 取消實作前的正向、負向或對抗測試設計。
- 取消 branch-end review、盲跑、對抗驗證或出貨阻擋。
- 依賴圖驅動的局部證據重用。

## Open questions
- none
