# 穩定 Claude Code 第二讀者
originator: maintenance-loop
kind: product
needs-design: yes — Closing Review 的第二讀者有成功、暫時失敗、無效輸出與無法使用等多種可見結果，目前沒有完整行為規格
evidence: [loom-code/skills/review/SKILL.md, loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md, loom-code/agents/reviewer.md]
status: confirmed 2026-09-10
publication: automatic — authorized 2026-09-10 by kouko

## Problem
在 Codex 中選擇 Claude Code 擔任第二讀者後，即使 Claude Code 已安裝並登入，實際審查仍可能連續失敗。現行流程只確認指令能啟動，沒有確保真正的唯讀審查能完成，也沒有清楚區分失敗原因，造成使用者等待後仍需改回同一供應商的讀者。

## Proposed outcome
讓 Closing Review 以一致、唯讀且可診斷的方式呼叫 Claude Code；成功時取得符合既有 reviewer 格式的結果，暫時失敗時只重試既有的一次，無法安全完成時則回報具體原因。

## Acceptance
1. 在 Codex task 選擇 Claude Code 作為第二讀者後，我可以讓它針對指定的真實變更完成一次唯讀審查，並取得可由 Loom 接受的結構化 verdict。
2. 審查開始前使用與正式審查相同的必要執行條件，能分辨未登入、模型不可用、權限阻擋、逾時、程序錯誤與輸出格式不合，而不是只以版本指令成功判定可用。
3. 暫時性執行失敗仍只沿用 Closing Review 既有的一次重試；第二次失敗會停止並顯示具體診斷，不會換身份、重設輪次或無限重跑。
4. 一個乾淨的受控環境可使用已登入的 Claude Code 對最小真實變更完成端到端 dogfood，證明它沒有修改 repository，且輸出的 reviewer 欄位完整有效。

## Constraints
- 同時符合 Claude Code 與 Codex 的官方非互動、權限及 plugin/skill 使用方式。
- 不新增 review 輪次、持久狀態、dispatch ledger、背景服務或另一套 retry budget。
- 不把繞過權限當作預設解法；第二讀者只需要讀取審查輸入與 repository。
- 保留現有 attestation schema 與兩位 fresh-context reviewer 的品質要求。

## Value case
GO — 這是 Closing Review 已實際發生的中斷；一次最小健康探針目前成功，顯示 Claude Code 本身可用，問題集中在 Loom 尚未定義完整的跨供應商審查執行邊界。

## Out of scope
- 修改 Claude Code、Codex Desktop 或帳號本身。
- 更換既有 reviewer 評分維度、輪數上限或 attestation 格式。
- 為所有外部 AI CLI 建立通用工作佇列或常駐服務。
- 保證供應商服務中斷時仍一定取得第二供應商 verdict。

## Open questions
- none
