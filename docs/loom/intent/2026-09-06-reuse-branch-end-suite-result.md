# 讓本機 push gate 單次執行完整測試
originator: kouko
kind: product
needs-design: yes — 完整測試改由 review 後的本機 push gate 單次執行，且失敗後依是否修改 repository 內容決定回到 Build 或重試 push
evidence: [docs/loom/2026-09-06-remove-build-time-reviews/review.json, docs/loom/2026-09-06-remove-build-time-reviews/blind-run-report.md]
status: confirmed 2026-09-06

## Problem
Loom 的 branch-end 會執行完整測試，Ship 又先明確執行 push checker，而實際 `git push` 還會由本機 host hook 再觸發同一個 checker。發布者因此在沒有新實作變更時重複等待，卻沒有得到新的品質資訊；這項成本也會出現在採用 Loom 的其他語言、框架與 repository。

## Proposed outcome
完整審閱、盲跑與對抗驗證先在 branch-end 完成；使用者接受結果後，Ship 直接發出具名分支的 `git push`，由支援的本機 host hook 攔截並讓 deterministic push checker 對最終內容執行 repository 的完整測試唯一一次。checker 觀察到成功才釋放 network push，不信任歷史測試結果；Ship 不再先明確執行同一個 checker。

## Acceptance
1. 完整 branch-end review 與使用者接受完成後，支援的本機 host hook 在實際 push transition 內執行 repository 完整測試唯一一次；成功才允許 network push，Ship 不再另外預跑同一 checker。
2. push checker 仍從 Git 重新確認 branch-end checkpoint、reviewed commit 與 Loom 允許的 review-only／intent-close 紀錄；它只相信當次實際觀察到的完整測試 exit code，不相信 agent 寫入的歷史結果。
3. 這個行為不依賴程式語言、框架、副檔名或 Monkey Skills 專用的原始碼路徑，採用 Loom 且安裝支援 host hook 的其他 repository 也能使用。
4. 完整測試命令維持既有解析結果：明確宣告優先、缺少宣告時可沿用既有偵測、完全無法解析則阻擋、明確 `none` 維持可見的免跑缺口；dirty tree、命令不可執行、逾時、中斷或非零退出都阻擋 push。
5. 完整測試失敗後，若修正會修改 tracked repository 內容，就回到 Build 並重新完成完整 branch-end review；若只修復本機環境且 Git 內容完全不變，可保留 checkpoint 並重試 push gate。
6. 實作途中以同一個已接受 checkpoint 重播從 Ship Push step 到本機 gate 阻擋或釋放 network push 的相同範圍，記錄 baseline 與 candidate 實際完整測試次數及 monotonic 等待秒數；candidate 恰好執行一次、少於 baseline、發布 verdict 相同且實測等待下降。

## Constraints
- 先以最小機制減少重複執行成本，不建立通用測試快取、dependency graph 或 affected-test 分析。
- 不修改 repository 原有的完整測試命令，也不降低 push 前必須由 deterministic checker 實際觀察完整測試通過的要求。
- 不依賴檔案副檔名或人工維護的「程式本體」清單判斷能否重用。
- 不修改 CI；本次只處理 Loom 從 branch-end 到 Ship 的本機流程。
- 加速結論必須來自同一案例的實際 baseline／candidate 計時，不以推估或理論省時取代。
- Git 無法證明仍對應同一個 reviewed 版本時，必須安全地退回 branch-end；push gate 不以 agent 寫入的測試結果取代當次實際執行。
- 不修改既有未追蹤的 `work/` 內容。

## Value case
GO。上一輪實作顯示 Ship 會在 branch-end 已通過後再次等待完整 package suite；先移除這一次完全重複的執行，是目前降低 Loom 成本與提高速度最小且可量測的改動。

## Out of scope
- 建立跨機器或遠端測試快取。
- 依 dependency graph 選擇局部測試。
- 依程式語言或檔案類型推測受影響範圍。
- 改寫各 repository 的測試套件或 CI pipeline。
- 取消 branch-end 的正式審閱、盲跑或對抗驗證，或取消 push gate 對完整測試 exit code 的當次觀察。

## Open questions
- none

## Amendment history
- 2026-09-07 — 原確認版本把完整測試唯一執行點放在 branch-end；pre-build adversarial review 指出 Git 無法證明歷史測試真的執行過。kouko 隨後確認改為在完整 review 與使用者接受後，由支援的本機 push gate 唯一執行完整測試；需要 repository 修改的失敗回到 Build，純環境修復則可直接重試 push gate。
