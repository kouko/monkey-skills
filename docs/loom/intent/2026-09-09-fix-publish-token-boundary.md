# 修正發布命令的 shell token 邊界

originator: maintenance-loop
kind: engineering
needs-design: no — 修正既有 hook 分類器、安裝說明與已交付 intent 狀態，不新增使用者介面或多狀態契約
evidence: [docs/loom/2026-09-08-fix-plugin-hook-worktree-resolution/evidence/codex-hook-input-and-trust.md]
status: confirmed 2026-09-09

## Problem
Loom 的發布 hook 會把唯讀搜尋參數裡的 shell 運算子和發布命令文字切成可執行片段，誤擋完全不會發布的命令。這輪安裝過程也證明先移除舊 plugin 會讓活躍 task 的版本化 hook 路徑失效，而數個已交付 intent 仍標成 confirmed，造成目前工作清單失真。

## Proposed outcome
發布分類只在 shell 真正可執行的 token 邊界辨識 push 與 PR 動作；實際發布的保守攔截不變。Codex 更新文件採 marketplace upgrade 後直接 add、不得先 remove。已由 PR #803、#805、#806、#807、#808、#809 交付的 intents 改為 closed。

## Acceptance
1. 唯讀命令的引號參數即使包含 `|`、`&&`、`gh pr create` 或 `gh pr merge` 文字，也不會被判定為發布。
2. 真正的直接 push、PR create、PR merge、巢狀 shell 與動態執行仍依既有 fail-closed 規則被辨識或阻擋。
3. Codex plugin 更新說明要求先刷新 marketplace、再直接 add 並驗證版本，且明確禁止活躍 task 更新時先 remove。
4. 六個已有合併證據的 intents 標為對應 PR 的 closed，不改動尚未交付的 intent。

## Constraints
- 不新增 checker rule、hook、launcher、ledger 或相容 contract。
- 不修改或刪除主 checkout 的未追蹤 `work/`。
- 不把 host 快取生命週期推測寫成 Loom 保證。

## Out of scope
- 修改 Codex Desktop 的 plugin cache 或 hook 重新載入行為。
- 清理已完成 worktree。
- 合併或發布本 change。

## Open questions
- none
