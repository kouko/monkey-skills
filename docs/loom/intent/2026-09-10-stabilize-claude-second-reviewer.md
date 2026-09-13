# 處理 Claude Code review 空輸出與逾時
originator: maintenance-loop
kind: product
needs-design: yes — Closing Review 的第二讀者有成功、空輸出與逾時等多種可見結果，目前沒有完整行為規格
evidence: [loom-code/skills/review/SKILL.md, loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md, loom-code/agents/reviewer.md]
status: confirmed 2026-09-10
publication: automatic — authorized 2026-09-10 by kouko

## Problem
在 Codex 中選擇 Claude Code 擔任第二讀者後，實際審查有時回傳空資料，有時執行到逾時。Loom 因此拿不到 reviewer 結果，使用者等待後仍需改回同一供應商的讀者。

## Proposed outcome
讓 Closing Review 正確辨識 Claude Code 的空輸出與逾時，保留必要診斷並沿用既有的一次重試；不為此增加事前審查或新的重試流程。

## Acceptance
1. Claude Code 回傳有效 review 時，Loom 可以正常取得並使用既有格式的 reviewer verdict。
2. Claude Code 回傳空白資料、缺少結果或無法解析的資料時，Loom 將它辨識為無效輸出，保留程序結束狀態與錯誤輸出，不把它誤認為成功。
3. Claude Code 超過正式 review 的時間上限時，Loom 將它辨識為逾時並保留耗時與可用錯誤資訊，不讓程序無限等待。
4. 空輸出或逾時只沿用 Closing Review 既有的一次重試；第二次仍失敗時停止並顯示具體診斷，不會換身份、重設輪次或無限重跑。

## Constraints
- 不新增 review 輪次、持久狀態、dispatch ledger、背景服務或另一套 retry budget。
- 不在正式 review 前增加另一個會呼叫模型的健康檢查。
- 保留現有 attestation schema 與兩位 fresh-context reviewer 的品質要求。

## Value case
GO — 空輸出與逾時都已在 Closing Review 實際造成中斷，而且可用受控失敗案例固定，不需要擴大成通用外部執行框架。

## Out of scope
- 修改 Claude Code、Codex Desktop、登入、模型權限或帳號本身。
- 更換既有 reviewer 評分維度、輪數上限或 attestation 格式。
- 處理空輸出與逾時以外的 Claude Code 可用性問題。
- 為所有外部 AI CLI 建立通用工作佇列或常駐服務。

## Open questions
- none
