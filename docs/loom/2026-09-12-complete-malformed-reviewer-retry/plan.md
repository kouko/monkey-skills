# Complete malformed reviewer retry failure boundaries — plan
intent: 2026-09-12-complete-malformed-reviewer-retry@a7d150294
charter: 1.0

## Current State Evidence
- Forward: explicit `malformed-response` already redispatches the same effective profile.
- Reverse: every other non-conforming kind currently raises `InputError`.
- Error: known non-routing observations are valid execution results, not malformed caller packets.
- Data: `NON_ROUTING_FAILURES` already separates known failures from unknown values.
- Boundary: Review owns its one-retry limit; the shared resolver owns typed transition validity.

## Task DAG

### Wave 1 — Complete the resolver boundary

**W1-01 Separate retry, terminal, and invalid observations**  after: none  acceptance: 1, 2, 3, 4
- Files: loom-code/scripts/test_dispatch_profile_resolver.py, loom-code/scripts/dispatch_profile.py, loom-code/references/dispatch-profile.md, loom-code/scripts/test_dispatch_profile_contract.py, loom-code/CHANGELOG.md
- Test: A1 positive: malformed-same-profile; negative: failure-trigger-no-escalation. A2 positive: known-failure-terminal; boundary: missing-kind-and-incomplete-terminal. A3 positive: unknown-kind-input-error; negative: no-dispatch. A4 positive: all-boundaries-pinned; boundary: exhausted-budget-terminal.
- Risk: agent-decided — branch on known failure identity before routing arithmetic; add no parser, retry state, loop, outcome, schema, or checker rule.

## Questions asked

1 — what — 你要的是：先只完成 malformed retry——只有明確的 malformed response 才用原 model／effort 重試；其他已知失敗、缺少分類與未完成執行都穩定停止，未知類型則拒絕；並補齊所有邊界測試，不擴大到一般 Claude 任務，也不 push、開 PR 或 merge。對嗎？
1 — what — 這次 Closing Review 要再把分支內容傳給 Claude Code，讓它作為第二位 reviewer 嗎？

## Risks

1. Returning `InputError` for a known execution state mislabels runtime evidence as caller misuse; tests must distinguish the observable outcomes.
2. A malformed response carrying an escalation trigger must remain on the original profile because formatting is not capability evidence.
