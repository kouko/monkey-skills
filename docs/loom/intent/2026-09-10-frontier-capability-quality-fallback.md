# 修復 frontier capability-quality fallback
originator: maintenance-loop
kind: engineering
needs-design: no — 修正既有 resolver 的內部狀態轉移，不改變使用者介面或既有分派政策
evidence: [loom-code/scripts/test_dispatch_profile_resolver.py]
status: confirmed 2026-09-10

## Problem
當 subagent 已經使用 frontier/low，並因 capability-quality 失敗需要再次分派時，resolver 目前錯誤地停止執行，而不是沿用既有政策提高推理 effort。使用 Loom 的 agent 會遇到這個錯誤。

## Proposed outcome
恢復模型已到 frontier 上限時的 effort fallback，讓 capability-quality 失敗依序從 low 升到 medium，同時保留既有的證據門檻、兩次 redispatch 上限與 atomic fallback。

## Acceptance
1. 在乾淨環境中執行永久 regression test 時，可以確認 frontier/low 的 capability-quality 失敗會得到 frontier/medium 的下一次分派。
2. 在乾淨環境中執行既有 resolver 與 adversarial tests 時，可以確認其他模型、effort、fallback 與 redispatch 路徑沒有改變。

## Constraints
- 延續 main-relative、model-first 與五階段 effort 政策。
- 不放寬 high、xhigh 或 max 的生成條件。
- 不新增 routing ledger、設定選項或使用者介入。
- 不 push、不建立 PR、不 merge。

## Out of scope
- 重新設計模型與 effort 分派政策。
- 修改其他已通過 Review 的 Loom 行為。
- 發布分支。

## Open questions
- none
