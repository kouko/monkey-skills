# Worktree-safe publication hooks — plan
intent: 2026-09-08-fix-plugin-hook-worktree-resolution@147d13a3e
spec: docs/loom/2026-09-08-fix-plugin-hook-worktree-resolution/spec.md@f19806433
charter: 1.0

## Task DAG

### Wave 0 — Explicit publication identity

**W0-01 Render and verify a worktree-bound direct merge command**  acceptance: 1,2,3,6
- Files: loom-code/skills/ship/SKILL.md, loom-code/scripts/loom_checker.py, loom-code/scripts/test_ship_worktree_merge.py
- Test: A1 positive: absolute-cd-merge; boundary: main-cwd. A2 positive: explicit-selector; negative: relative-selector. A3 positive: captured-payload-shape; negative: main-fallback. A6 positive: ordinary-pass; negative: unsafe-publication.
- Risk: agent-decided — change only Ship's authorized direct-merge rendering; reuse the existing explicit-cd parser and retain every attestation, HEAD, destination, and refspec check.

### Wave 1 — Trust boundary and release

**W1-01 Separate installed Loom trust from repository-local hook trust**  after: W0-01  acceptance: 4,5
- Files: loom-code/skills/write-plan/references/codex-first-contact.md, loom-code/scripts/test_codex_hook_trust_contract.py, docs/loom/evidence/mechanisms.yaml, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md
- Test: A4 positive: plugin-key-stable; negative: repo-key-distinct. A5 positive: new-or-modified-review; negative: no-private-state-or-bypass.
- Risk: agent-decided — document observed Codex 0.153.4 behavior without promising host internals; release as patch 2.0.3 and keep unrelated repository hooks unchanged.

## Questions asked
1 — what — 你要的是：發布檢查永遠辨識命令真正操作的工作目錄；建立同 repo 的新 worktree 不再重複要求 Loom 授權；同時研究安裝或更新 plugin 時的確認能否安全減少，但不能修改私有信任資料、停用 hooks 或降低發布防護。對嗎？
1 — what — 這次要不要繼續用 Claude Code 當第二位讀者？第二 vendor 會多花幾分鐘與 quota；先前基準中，7 個嚴重問題有 5 個只被其中一家發現。

## Risks
1. Codex omits executor workdir from hook stdin, so no plugin parser can recover it; every Loom-rendered direct merge must carry the absolute repository unconditionally.
2. Repository-local PostToolUse hooks can still request trust per absolute worktree path; this change identifies them accurately but does not remove or weaken unrelated repository policy.
3. The real payload capture is version-specific evidence, not a permanent Codex API guarantee; tests pin the safe command shape instead of assuming an undocumented field will appear.
