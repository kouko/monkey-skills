# Atomic Claude reviewer dispatch — plan
intent: 2026-09-10-atomic-claude-reviewer-dispatch@f94da57d62c81dc1a382252128055434b8555c5e
spec: docs/loom/2026-09-10-atomic-claude-reviewer-dispatch/spec.md@f29b7fe65
charter: 1.0

## Task DAG

### Wave 1 — Runner boundary

**W1-01 Make runner overrides atomic**  after: none  acceptance: 1, 2
- Files: `loom-code/scripts/test_claude_reviewer.py`, `loom-code/scripts/claude_reviewer.py`
- Test: A1 positive: paired-profile-forwarded; boundary: override-free-host-default. A2 positive: resolver-null-omits-pair; negative: partial-pair-rejected-before-spawn.
- Risk: agent-decided — keep one-attempt execution unchanged; only argv construction and paired-input validation implement spec REQ-1 and REQ-2.

### Wave 2 — Review integration

**W2-01 Align Review contract and package metadata**  after: W1-01  acceptance: 3
- Files: `loom-code/skills/review/SKILL.md`, `loom-code/scripts/test_dispatch_profile_contract.py`, `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`, `loom-code/CHANGELOG.md`
- Test: A3 positive: review-command-carries-atomic-pair; boundary: rejected-fallback-cannot-stack-transient-retry.
- Risk: agent-decided — Review owns resolver feedback and retry separation; the runner remains one subprocess attempt as required by spec REQ-3.

## Questions asked
① — what — 你要修正的是：第二位 Claude reviewer 必須完整遵守動態分派結果；模型與推理強度只能一起指定，任何一項不支援或無法確認時就全部省略並使用預設值。完成後可以用永久測試證明正常配對、fallback、retry 與無需使用者介入的行為都一致。對嗎？
① — what — 這次是否繼續使用 Claude Code 當第二位讀者？

## Risks
1. Claude Code flags can change between installed versions; checked-in help evidence grounds the current pair, while unsupported future combinations must take override-free fallback.
2. Host rejection and transient executor failure share a process boundary; tests must prevent their two retry budgets from being combined into an unintended third invocation.
