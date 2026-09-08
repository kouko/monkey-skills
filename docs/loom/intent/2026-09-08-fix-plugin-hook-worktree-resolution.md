# 修正 plugin hook 的 worktree 辨識與重複授權

originator: maintenance-loop
kind: engineering
needs-design: yes — hook 需在主 checkout、worktree、明示目錄與 host 授權狀態間正確轉換，目前沒有規格界定這些狀態
status: confirmed 2026-09-08

## Problem
Codex Desktop 從 feature worktree 執行發布命令時，plugin hook 可能仍使用 task 的主 checkout，因而把已驗證的分支誤判成 main 並阻擋操作。使用者也曾被要求手動承認 hook；目前不清楚那是每個 worktree 的重複提示、plugin 更新後的必要授權，或可以消除的重複成本。

## Proposed outcome
發布 hook 以命令真正選取的 repository/worktree 為準，不因 Desktop task 的起始目錄而誤判。可由 plugin 控制的重複授權應被消除；host 強制的安全確認則只在有證據支持時保留並清楚說明，不以修改私有信任資料或停用防護來繞過。

## Acceptance
1. 從主 checkout 啟動的 task 對 feature worktree 執行發布命令時，hook 驗證該 feature worktree，而不是誤報 main 的空 diff。
2. 明示的 `cd`、Git `-C`、正常 task cwd 與不明確的多 repository 命令，各自得到一致且 fail-closed 的 repository 選擇。
3. 一個永久回歸案例能重現本次 Desktop workdir 誤判，並在修正後通過。
4. 已安裝 plugin hook 不會因建立同 repo 的新 worktree 而要求另一份 repo-local Loom 授權。
5. 對 plugin 安裝、版本更新或 hook 定義變更所觸發的手動確認，需以本機觀察與官方可得證據區分：能安全消除就消除；若屬 host 信任邊界，則不得偽裝成 plugin 可關閉。
6. 普通非發布命令不受影響，發布命令仍保留 attestation、目的地與精確 refspec 防護。

## Constraints
- 使用 installed `loom-code` plugin 作為唯一 Codex hook，不恢復 repo-local checker、hook scaffold 或 firing ledger。
- 不修改 Codex 私有信任資料庫，不全域停用 hooks，也不降低發布 fail-closed 保證。
- 解法需適用其他 repository 與 worktree，不得依賴 monkey-skills 的固定路徑。
- 保留主 checkout 未追蹤的 `work/`，不修改或刪除。

## Out of scope
- 重做 attestation、privacy gate、review convergence 或 package-suite 流程。
- 自動核准任意第三方 plugin hook。
- 清理既有 worktree 或全域 Codex 設定。

## Open questions
- 使用者先前看到的手動承認提示，是否能由可重現的 Codex host 行為確定其觸發邊界。
