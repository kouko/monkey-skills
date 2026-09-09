# 修正命令替換漏判與 plugin 更新說明

originator: maintenance-loop
kind: engineering
needs-design: no — 修正既有 hook 分類器、三語安裝說明與受控驗證，不新增使用者介面或多狀態契約
status: confirmed 2026-09-09

## Problem
Loom 的發布 hook 仍可能漏掉沒有 shell 運算子的 `$()` 命令替換；本輪實際更新也證明 `plugin add` 會清除活躍 task 使用中的舊版 hook 路徑，與目前三語說明暗示的安全性不符。Claude Code 執行含發布字串的 probe 是否仍會被誤擋，也缺少受控結果。

## Proposed outcome
`$()` 內真正的發布命令維持 fail-closed，即使內容沒有管線或其他運算子也能辨識；三語文件明確要求更新後立即重啟，重啟前不再操作；Claude Code 以固定案例驗證 hook，只有重現的分類器缺陷才加入永久測試並修正。

## Acceptance
1. `echo "$(git push origin HEAD)"` 與 `echo "$(gh pr create --fill)"` 都會被辨識為發布命令。
2. 單引號中的 `$()` 與其他純文字搜尋參數不會被判定為發布，PR #810 的案例持續通過。
3. 英文、日文與繁中更新說明都表明安裝會替換版本化快取，要求更新後立即重啟且重啟前不要再操作。
4. Claude Code 對固定的真發布與純文字案例完成受控 dogfood；任何重現的分類缺陷都有先紅後綠的永久測試。

## Constraints
- 不新增 checker rule、hook、launcher、ledger、相容路徑或 merge wrapper。
- 不修改 loom-workflow 或 git-memory。
- 不把 host cache 的未驗證行為寫成保證；文件只描述本輪觀察與安全操作。

## Out of scope
- 讓活躍 task 在安裝後熱切換 plugin 版本。
- 修改 Codex Desktop 或 CLI 的 cache pruning 行為。
- 發布、開 PR、合併或移除 worktree。

## Open questions
- none
