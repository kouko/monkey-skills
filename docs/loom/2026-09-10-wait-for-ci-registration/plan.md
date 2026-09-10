# Faster required-check observation — plan
intent: 2026-09-10-wait-for-ci-registration@a5d0847d04fff8a4e470456fcea805b4a9483f24
spec: docs/loom/2026-09-10-wait-for-ci-registration/spec.md@e5e1e7789e4161b284699f2e010d575cc7d556cb
charter: 1.0

## Task DAG

### Wave 1 — One bounded observation loop

**W1-01 Handle CI registration and pending states in one publisher loop**  acceptance: 1, 2, 3, 4
- Files: loom-code/scripts/loom_checker.py, loom-code/scripts/test_loom_publish.py, loom-code/skills/ship/SKILL.md, loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, .claude-plugin/marketplace.json
- Test: A1 positive: exit-one-no-checks-then-pass; negative: no-second-publish. A2 positive: exact-no-checks-classified; negative: near-match-or-nonblank-blocks. A3 positive: six-waits-then-success; boundary: checks-appear-at-final-observation. A4 positive: pending-then-pass-ten-seconds; boundary: independent-360-wait-timeout.
- Risk: agent-decided — extend the existing publisher loop with separate counters and exact error classification; add no scheduler, state artifact, gate, or background service.

## Questions asked

1 — what — 我把這輪範圍限定為 CI 註冊等待與輪詢週期，對嗎？
2 — behaviour — required checks 每 10 秒重查、註冊最多等 60 秒、pending 最多等 60 分鐘，這就是你預期的行為嗎？

## Risks

1. GitHub CLI shares exit code 1 across unrelated failures; only the exact no-checks shape may enter registration grace, and all ambiguous responses remain blocking.
2. Boundary counters can shorten or extend promised elapsed time; permanent tests pin the final observation after six and 360 ten-second waits independently.
3. Faster polling increases GitHub calls by threefold; the fixed 60-second and 60-minute budgets prevent an unbounded loop.
