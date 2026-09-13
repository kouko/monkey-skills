# Restore frontier capability-quality fallback — plan
intent: 2026-09-10-frontier-capability-quality-fallback@f44905ed72d94bc1c8204425c3a699fd8e81c758
charter: 1.0

## Current State Evidence
- Forward: `docs/loom/2026-09-09-main-relative-model-dispatch/spec.md:41` requires capability-quality at frontier to use reasoning-depth handling.
- Reverse: `loom-code/scripts/dispatch_profile.py:200` upgrades capability-quality only below frontier.
- Error: `loom-code/scripts/dispatch_profile.py:209` returns no-legal-escalation when no transition matches.
- Data: `loom-code/scripts/test_dispatch_profile_resolver.py:195` captures the failing frontier/low case.
- Boundary: `loom-code/references/dispatch-profile.md:127` permits low-to-medium reasoning escalation on the current model.

## Task DAG

### Wave 1

**W1-01 Restore the frontier ceiling transition**  after: none  acceptance: 1, 2
- Files: `loom-code/scripts/dispatch_profile.py`, `loom-code/scripts/test_dispatch_profile_resolver.py`, `loom-code/references/dispatch-profile.md`, `loom-code/scripts/test_dispatch_profile_contract.py`
- Test: A1 positive: frontier-low-capability-to-medium; boundary: contract-pins-frontier-ceiling. A2 positive: focused-resolver-suite; negative: unsupported-pair-atomic-fallback.
- Risk: A broad condition could bypass expensive-effort gates; agent-decided — change only the low-to-medium ceiling branch and retain every later gate.

## Questions asked

decision point ① — what — 你要的是：修正 `frontier/low` 在 capability-quality 失敗時錯誤停止的問題；完成後，它會自動轉到 `frontier/medium`，而其他模型、effort、fallback 與兩次 redispatch 上限維持不變。這次仍然不 push、不建立 PR、不 merge。對嗎？
decision point ① — consequence — 這次是否要再使用 Claude Code 當第二位讀者？

## Risks

1. The fix could accidentally restore the old dead end for reasoning-depth or permit high without evidence; existing sequential-escalation tests remain mandatory.
