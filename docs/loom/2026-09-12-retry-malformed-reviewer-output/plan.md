# Retry malformed reviewer output without routing escalation — plan
intent: 2026-09-12-retry-malformed-reviewer-output@b04917656
charter: 1.0

## Current State Evidence
- Forward: `review/SKILL.md` allows one same-digest retry before a conforming verdict exists.
- Reverse: `dispatch_profile.py::_after_execution` terminates every non-conforming completed attempt.
- Error: `no-legal-redispatch` prevents the promised malformed-response retry.
- Data: `last_attempt` already carries conformance, failure kind, effective profile, and completed redispatch count.
- Boundary: `claude_reviewer.py` executes once; `reviewer.md` and the orchestrator own output validity.

## Task DAG

### Wave 1 — Align the existing resolver transition

**W1-01 Permit one same-profile malformed-response redispatch**  after: none  acceptance: 1, 2, 3, 4
- Files: loom-code/scripts/test_dispatch_profile_resolver.py, loom-code/scripts/dispatch_profile.py, loom-code/references/dispatch-profile.md, loom-code/scripts/test_dispatch_profile_contract.py, loom-code/skills/review/SKILL.md, loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Test: A1 positive: completed-malformed-response-retries; boundary: exhausted-budget-fails. A2 positive: profile-unchanged-and-count-increments; negative: no-effort-escalation. A3 positive: incomplete-attempt-fails; negative: unknown-kind-rejected. A4 positive: responsibility-contract-pinned; boundary: runner-remains-single-attempt.
- Risk: agent-decided — reuse the existing `dispatch` result and redispatch counter; add no outcome, state file, parser, loop, ledger, or checker rule.

## Questions asked

1 — what — 請在 Monkey Skills 專案中獨立處理這個 Loom maintenance 問題：先使用 `loom-code:maintain` 建立並確認適當 intent，再診斷契約與實作的真正責任邊界，提出最小修正並 test-first 實作。
1 — consequence — 完成前不要 push、開 PR 或 merge，除非該 task 內另取得明確授權。

## Risks

1. A same-profile retry must remain distinct from capability escalation; otherwise malformed formatting could incorrectly buy a stronger model.
2. The resolver budget alone permits two redispatches, so Review must retain ownership of its stricter one-retry same-digest limit.
