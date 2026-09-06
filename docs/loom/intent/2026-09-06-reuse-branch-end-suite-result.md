# 重用 branch-end 的完整測試結果
originator: kouko
kind: product
needs-design: yes — Ship 會依多種證據狀態決定重用測試結果或退回 branch-end，目前沒有涵蓋此行為的規格
evidence: [docs/loom/2026-09-06-remove-build-time-reviews/review.json, docs/loom/2026-09-06-remove-build-time-reviews/blind-run-report.md]
status: confirmed 2026-09-06

## Problem
Loom 已在 branch-end 對最終實作版本執行完整測試，Ship 卻會在沒有新實作變更時再次執行相同測試。發布者因此重複等待，卻沒有得到新的品質資訊；這項成本也會出現在採用 Loom 的其他語言、框架與 repository。

## Proposed outcome
branch-end 成為完整測試唯一的執行與判定位置，當場對最終實作 commit 執行 repository 宣告的完整測試，通過後才建立 checkpoint。Ship 不再擁有或重跑同一個 package-test gate，只從 Git 重新確認 checkpoint 合法、要發布的實作 commit 沒有改變，且之後只有 Loom 允許的關閉紀錄；任一條不成立就退回 branch-end 重新驗證。

## Acceptance
1. branch-end 是完整測試唯一的執行與判定位置；它對最終實作 commit 跑完 repository 宣告的完整測試且通過後，Ship 不再執行相同測試。
2. Ship 從 Git 重新確認最新 branch-end checkpoint 合法、受測實作 commit 沒有改變，且之後只有允許的關閉紀錄；任一項缺失、不符或失效時，要求重新執行 branch-end 驗證。
3. 這個行為不依賴程式語言、框架、副檔名或 Monkey Skills 專用的原始碼路徑，採用 Loom 的其他 repository 也能使用。
4. 實作途中在同一個代表性變更上重播 branch-end 到 Ship，分別記錄 baseline 與 candidate 的完整測試執行次數及實際等待秒數；新流程只執行一次完整測試、最終發布阻擋結果與現行流程相同，而且實測等待時間確實下降。

## Constraints
- 先以最小機制減少重複執行成本，不建立通用測試快取、dependency graph 或 affected-test 分析。
- 不修改 repository 原有的完整測試命令，也不降低 branch-end 必須完整通過的要求。
- 不依賴檔案副檔名或人工維護的「程式本體」清單判斷能否重用。
- 不修改 CI；本次只處理 Loom 從 branch-end 到 Ship 的本機流程。
- 加速結論必須來自同一案例的實際 baseline／candidate 計時，不以推估或理論省時取代。
- Git 無法證明仍對應同一個受測實作版本時，必須安全地退回 branch-end；Ship 不以 agent 寫入的測試結果宣稱取代 gate 的重新計算。
- 不修改既有未追蹤的 `work/` 內容。

## Value case
GO。上一輪實作顯示 Ship 會在 branch-end 已通過後再次等待完整 package suite；先移除這一次完全重複的執行，是目前降低 Loom 成本與提高速度最小且可量測的改動。

## Out of scope
- 建立跨機器或遠端測試快取。
- 依 dependency graph 選擇局部測試。
- 依程式語言或檔案類型推測受影響範圍。
- 改寫各 repository 的測試套件或 CI pipeline。
- 取消 branch-end 的完整測試、正式審閱、盲跑或對抗驗證。

## Open questions
- none
