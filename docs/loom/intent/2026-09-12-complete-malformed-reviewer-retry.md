# 完成 malformed reviewer retry 的失敗邊界
originator: kouko
kind: engineering
needs-design: no — 只修正內部 dispatch 決策與測試，不改變使用者介面
evidence: [docs/loom/intent/2026-09-12-retry-malformed-reviewer-output.md, loom-code/scripts/dispatch_profile.py, loom-code/references/dispatch-profile.md, loom-code/scripts/test_dispatch_profile_resolver.py]
status: confirmed 2026-09-12

## Problem
前一次修正已讓 malformed reviewer output 可以用同一 profile 重試，但對其他已知失敗類型與缺少類型的處理過度收窄，可能把可判讀的執行失敗誤當成呼叫者輸入錯誤。

## Proposed outcome
讓 malformed response 只使用既有的同 profile 一次重試，同時讓其他合法但不可重試的觀測穩定回傳 execution-failed，不合法的未知類型才拒絕輸入。

## Acceptance
1. 已完成、不合規且明確標記為 `malformed-response` 的回應，在額度尚存時會用原 model 與 effort 重試，不升級 profile。
2. 已知但不屬於 malformed retry 的失敗、缺少足夠分類資訊，以及未完成的執行，都回傳 `execution-failed` 而非重試。
3. 未知的 `failure_kind` 維持輸入錯誤，不被當成可重試或已知失敗。
4. 測試會固定 incomplete execution、無 escalation、已知非 retry failure、缺少 kind 與未知 kind 的邊界。

## Constraints
- 不新增 reviewer loop、retry ledger、checker rule、parser、結果 schema 或持久狀態。
- `claude_reviewer.py` 保持單次執行且不解析 reviewer 內容。
- 只修正 malformed retry，不擴大到一般 Claude 任務的輸出可靠性。
- 不 push、不開 PR、不 merge。

## Value case
GO — 這是現有修正的已知邊界缺口，可以透過少量條件分支與回歸測試完成，無需新機制。

## Out of scope
- 強制 Claude Code 總是回傳特定結構。
- 改變 Review 的最多一次 same-digest retry。
- 變更 model routing 或新增 provider-specific fallback。

## Open questions
- none
