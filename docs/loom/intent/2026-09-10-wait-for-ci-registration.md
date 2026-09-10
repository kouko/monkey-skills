# 更快等待 GitHub required checks
originator: maintenance-loop
kind: product
needs-design: yes — CI 輪詢等待時間從 30 秒改為 10 秒，改變使用者可感受到的 Ship 行為，且現有規格固定為 30 秒
evidence: [loom-code/scripts/test_loom_publish.py, docs/loom/2026-09-09-auto-publish-contextual-pr/spec.md]
status: confirmed 2026-09-10
publication: automatic — authorized 2026-09-10 by kouko

## Problem
Loom 剛建立 PR 時，GitHub 可能暫時以 exit 1 回報尚無 checks；publisher 目前把它當成永久錯誤而立即停止，迫使使用者再次啟動 publish 才能監控 CI。

## Proposed outcome
把 GitHub 明確的「尚無 checks」回應視為 CI 註冊延遲，等待 10 秒後自動重查；所有 pending required checks 也改為每 10 秒檢查，其他查詢錯誤仍立即阻擋。

## Acceptance
1. PR 建立後第一次收到 GitHub 的「尚無 checks」回應時，Loom 會等待 10 秒並自動重查，不需要我再次執行 publish。
2. 權限、網路、格式或其他非「尚無 checks」的失敗仍會立即停止並顯示原始原因。
3. required checks 尚未出現時，Loom 每 10 秒重查並最多等待 60 秒；整段期間仍沒有 checks 才回報未註冊 required checks 並正常結束。
4. required checks 處於 pending 時，Loom 每 10 秒重查一次，且總監控時間仍維持 60 分鐘。

## Constraints
- 將 registration delay 與 pending checks 的輪詢週期統一改為 10 秒；registration grace 為 60 秒，pending checks 的總監控上限仍為 60 分鐘，required-check-only 政策不變。
- 使用 `gh pr checks --required` 的實際 exit code 與錯誤文字建立永久 regression test。
- 不碰 model dispatch、Claude reviewer 或其他 worktree。

## Out of scope
- 改變 GitHub Actions workflow 或 branch protection。
- 重新設計 CI 監控與通知。
- 處理 Claude Code reviewer 自行執行 package suite 的問題。

## Open questions
- none
