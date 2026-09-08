# Bound Loom review convergence — plan
intent: 2026-09-08-bound-review-convergence@377ceb082
spec: docs/loom/2026-09-08-bound-review-convergence/spec.md@ede7dd5a6
charter: 1.0

## Task DAG

### Wave 0 — Make the closing Review episode terminal

**W0-01 Define and test the three-round episode**  after: none  acceptance: 1,2,4,5,6,7
- Files: loom-code/skills/review/SKILL.md, loom-code/agents/reviewer.md, loom-code/scripts/test_review_convergence_contract.py
- Test: A1 positive: three-digest-cap; boundary: same-digest-no-reset. A2 positive: round-roles; boundary: redesign-no-reset. A4 positive: stuck-relook; negative: local-patching. A5 positive: terminal-failure; negative: round-four. A6 positive: agent-decides; negative: technical-user-question. A7 positive: no-ledger; negative: stored-round-schema.
- Risk: Contract-only enforcement may be ignored; agent-decided — run blind cases before admitting the state-free design and stop for a spec amendment on any failure.

**W0-02 Bound executor retry behaviour**  after: W0-01  acceptance: 3
- Files: loom-code/skills/review/SKILL.md, loom-code/agents/reviewer.md, loom-code/scripts/test_review_convergence_contract.py
- Test: A3 positive: one-transient-retry; boundary: same-content-no-round; negative: second-failure-terminal.
- Risk: Retry text could hide semantic re-review; agent-decided — permit one retry only before a conforming verdict exists and keep NEEDS_REVISION on the round path.

### Wave 1 — Prove behaviour and release coherence

**W1-01 Exercise blind convergence cases**  after: W0-02  acceptance: 1,2,3,4,5,6,7
- Files: docs/loom/2026-09-08-bound-review-convergence/adversarial_review_convergence.py, loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Test: A1 positive: capped-sequence; negative: identity-reset. A2 positive: autonomous-replan; boundary: changed-requirement. A3 positive: retry-separation; negative: retry-loop. A4 positive: repeated-blocker; negative: patch-loop. A5 positive: non-convergent-stop; negative: continue-choice. A6 positive: internal-decision; boundary: user-visible-change. A7 positive: package-boundary; negative: ledger-return.
- Risk: Static probes can pass without changing agent behaviour; agent-decided — closing Review runs fresh blind scenarios and rejects this design if any case permits a fourth round.

## Questions asked
① — what — 你要的是：Loom 每個 change 最多進行兩輪正常 review，加一輪由 agent 重新整理技術方案後的最終驗證；agent 自行判斷 blocker、修正與內部設計。第三輪仍有 blocker 時，本輪直接以未收斂結束，不提供 Round 4，也不把技術判斷丟給使用者。暫時性執行錯誤不算新 round，未解決 blocker 也不會被放行。對嗎？
① — what — 這次要不要用 Claude Code 當第二位讀者？

## Risks
1. A prose contract cannot provide process-level persistence; any blind failure stops implementation and triggers the stateful-spec amendment defined by REQ-7.
2. Review and reviewer text can drift; one focused contract test must assert the shared terminal semantics without duplicating a new runtime schema.
3. The third round must remain a quality gate, not forced approval; NON_CONVERGENT preserves blockers and prevents publication.
