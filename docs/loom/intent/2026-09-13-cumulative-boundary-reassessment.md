# 在新功能規劃時重評累積後的程式邊界
originator: kouko
kind: engineering
needs-design: no — only internal Loom planning behavior changes
status: confirmed 2026-09-13
publication: automatic — authorized 2026-09-13 by kouko

## Problem
使用 Loom 持續開發同一區域時，每次單獨看都合理的小改動，可能逐步把不同責任、依賴、共享狀態與測試範圍疊進同一個程式邊界。現有 Write Plan 主要沿用既有邊界，缺少在新功能開始時利用現況與變更歷史主動重評的步驟，因此可能直到 Build 被迫越界或 Closing Review 看完整體差異時才發現。

## Proposed outcome
每次新功能開始規劃時，Write Plan 只對預計修改的區域做一次小型、受限的歷史累積檢查，判斷現有邊界是否仍能讓本次功能局部理解、修改與測試。只有「出現不同責任」且「已有具體局部性失效後果」同時成立時，才先規劃保護現有行為與抽取；否則保留現況。

## Acceptance
1. 面對前幾次修改各自合理、但最新功能開始加入獨立責任與依賴後果的連續歷史，fresh Write Plan 會在功能實作前辨認邊界失效，並安排先用測試保護現況、再抽取、最後實作功能。
2. 面對修改頻繁但責任一致、依賴與測試仍可局部處理的歷史，不會因檔案長度、churn 或 commit 數量而拆分。
3. 面對 rename、格式化、大量同步修改等歷史雜訊，不會誤判；面對已經拆檔但共享狀態、依賴與共同修改範圍未縮小的情況，也不會把再次拆檔當成改善。
4. 每次新功能規劃都執行短篩選，只有出現具體警訊才讀取完整判斷指引；一般案例不增加使用者決策或要求獨立 skill。
5. 提交的縱向 A/B 評估使用相同的真實 Git 歷史，證明 candidate 在累積責任案例優於 baseline、在一致責任與雜訊案例沒有新增誤判，量測深入指引的載入比例與額外 context，並至少以一個最小真實實作驗證修改範圍、依賴與測試隔離；若未達標就還原 runtime contract。

## Constraints
- 歷史、churn、檔案長度與 token 數只能觸發檢查，不能單獨形成抽取判決。
- 檢查限於本次功能可能修改的區域、直接呼叫者、狀態擁有者、相關測試與受限的近期歷史；不掃描整個 repository。
- 判斷使用原始碼、依賴、呼叫者、測試與 Git 歷史的具體證據；不建立跨語言的萬用程式品質分數。
- 快速篩選留在 Write Plan 的主入口；完整判斷放在 bundled reference，只有快速篩選出現警訊時才載入。既有 Implementer 與 Closing Review contract 不重複這套邏輯。
- 決定寫入既有 Current State Evidence、task 與 Risk 欄位，不新增永久記錄載體。
- 第一版 runtime contract 淨增加目標不超過 150 words，session-start 注入、skill 數、gate 數、checker rule 數與 artifact type 數不增加。

## Out of scope
- 自動重構整個 repository 或定期背景掃描。
- 通用的 LOC、token、function、file、churn 或 commit 閾值。
- 重構與本次已確認功能無關的舊程式。
- 建立獨立的模組化 skill，或要求使用者選擇程式邊界。
- 從小型評估宣稱所有 repository 或所有模型都能節省固定比例 token 或時間。

## Open questions
- none
