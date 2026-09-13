# Clarify Build implementer dispatch — plan
intent: 2026-09-13-clarify-build-implementer-dispatch@8f8f9d909
charter: 1.0

## Current State Evidence
- Forward: `loom-code/skills/build/SKILL.md` :: `Parallel work is optional` follows TDD steps without requiring an implementer dispatch.
- Reverse: `loom-code/skills/write-plan/SKILL.md` :: the handoff says Build dispatches one implementer per task, but task-wave prose describes parallel execution as automatic.
- Error: the optional-parallel sentence can be read as making delegation optional, allowing the main agent to implement planned tasks itself.
- Data: `loom-code/scripts/test_simplified_station_text.py` already pins cross-station workflow contracts and is the narrow existing test surface.
- Boundary: dispatch-profile routing, reviewer policy, checker rules, attestation schema, and publication behavior remain unchanged.

## Task DAG

### Wave 0 — clarify and pin the dispatch contract

**W0-01 Require implementer dispatch while keeping scheduling optional**  after: none  acceptance: 1, 2, 3
- Files: loom-code/scripts/test_simplified_station_text.py, loom-code/skills/build/SKILL.md, loom-code/skills/write-plan/SKILL.md
- Test: A1 positive: mandatory-dispatch-wording; negative: optional-delegation-wording. A2 positive: unavailable-dispatch-stops; negative: main-agent-substitution. A3 positive: cross-station-contract-pinned; boundary: parallel-scheduling-remains-optional.
- Risk: Similar but non-identical wording could preserve ambiguity; agent-decided — pin explicit mandatory dispatch, optional concurrent scheduling, blocker, and no-substitution semantics in one existing contract test.

## Questions asked

① — what — 請在目前 worktree 完成 Loom Build 階段的 subagent 分派契約修正；每個 implementation task 必須交給 implementer subagent，多個 implementer 是否並行才是 optional，main agent 不可頂替。

## Risks

1. Literal-only assertions can overfit one sentence; the test must independently require the four semantic clauses and reject the known ambiguous phrase.
2. Editing broader orchestration language could create a new mechanism; keep the change to role and scheduling prose only.
