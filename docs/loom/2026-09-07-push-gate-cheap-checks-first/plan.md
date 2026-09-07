# Cheap checks before push executables — plan
intent: 2026-09-07-push-gate-cheap-checks-first@7d1ec6a6
spec: docs/loom/2026-09-07-push-gate-cheap-checks-first/spec.md@e0ddf5b3
charter: 1.0

## Task DAG

### Wave 0 — One deterministic preflight boundary

**W0-01 Short-circuit executable probes after deterministic blockers**  acceptance: 1,2,3,4
- Files: loom-code/scripts/loom_checker.py, docs/loom/2026-09-07-push-gate-cheap-checks-first/evidence/probes/test_push_preflight_before_executables.py
- Test: A1 positive: blocked-zero-executables; negative: late-blocker-runs-today. A2 positive: valid-runs-once; boundary: package-skip-keeps-adversarial. A3 positive: stable-releases; negative: mutation-blocks. A4 positive: generic-fixture; boundary: no-path-classification.
- Risk: agent-decided — move every existing non-executable recompute before one early return; preserve accumulated failures, executable order, command resolution, rule text, and post-execution state comparison from spec REQ-1 through REQ-4.

**W0-memory Memory step — graduated probes and store entries**  after: W0-01
- Files: loom-code/scripts/test_push_preflight_before_executables.py, docs/loom/memory/
- Test: python3 scripts/check_loom_memory_integrity.py --check; python3 -m pytest loom-code/scripts/test_push_preflight_before_executables.py -q
- Risk: agent-decided — graduate only repository-neutral phase-boundary cases and one durable ordering lesson; leave change-specific review evidence under this change.

## Questions asked
1 — what — 這次要不要用 Claude 當第二位讀者？

## Risks
1. Moving a check across the executable boundary can change failure ordering; retain accumulated deterministic output and assert rule identifiers rather than incidental line order.
2. An executable can mutate HEAD, worktree, index, or effective Git configuration; keep one before/after snapshot around both executable classes.
