# Simplify Loom publication — plan
intent: 2026-09-08-simplify-loom-publication@efc84ee28
spec: docs/loom/2026-09-08-simplify-loom-publication/spec.md@ed42ec9cd
charter: 1.0

## Task DAG

### Wave 1 — publication boundaries

**W1-01 Validate only the final PR title**  after: none  acceptance: 1, 2
- Files: `.github/workflows/conventional-pr-title.yml`, `.github/workflows/skill-structure.yml`, `scripts/test_conventional_commits_workflow.py`
- Test: A1 positive: valid-title-with-invalid-intermediate; boundary: title-edit-trigger. A2 positive: valid-final-title; negative: invalid-final-title-message.
- Risk: Keep the required-check display name unchanged and pass untrusted title text through env; agent-decided per spec REQ-1.

**W1-02 Add safe idempotent publish orchestration**  after: none  acceptance: 3, 4, 5
- Files: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_publish.py`
- Test: A3 positive: push-create-once; boundary: retry-existing-pr. A4 positive: attestation-only-publish; negative: no-functional-executables. A5 positive: safe-origin-head-base; negative: unsafe-state-matrix.
- Risk: Use trusted argv subprocesses, authenticated origin-derived targeting, sanitized env, non-forced fast-forward, and pre-action HEAD recomputes; agent-decided per spec REQ-2–REQ-5.

### Wave 2 — station adoption and integration

**W2-01 Make Ship use publish and release the plugin**  after: W1-02  acceptance: 3
- Files: `loom-code/skills/ship/SKILL.md`, `loom-code/scripts/test_simplified_station_text.py`, `loom-code/CHANGELOG.md`, `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- Test: A3 positive: ship-names-single-publish; negative: ship-has-no-manual-publication. Integration: manifest-sync-and-plugin-version-gates.
- Risk: Change only loom-code publication instructions and patch version; preserve decision point ③ and raw-command hook fallback, agent-decided per spec REQ-6.

**W2-02 Run package and adversarial integration**  after: W1-01, W2-01  acceptance: 1, 2, 3, 4, 5
- Files: `docs/loom/2026-09-08-simplify-loom-publication/adversarial_publish.py`
- Test: A1 positive: workflow-valid-title; boundary: edited-event. A2 positive: workflow-pass; negative: workflow-fail. A3 positive: wrapper-idempotency; boundary: partial-retry. A4 positive: no-replay; negative: executable-sentinel. A5 positive: safe-matrix; negative: unsafe-matrix.
- Risk: Adversarial program uses isolated temporary repositories and mocked network executables; it never pushes this worktree, agent-decided per spec REQ-1–REQ-6.

## Questions asked
① — what — 你要的是先移除兩個已證實的發布摩擦：CI 只檢查 squash merge 最後會留下的 PR title，以及提供單一安全的 publish wrapper；finalization 只評估、不改。對嗎？
① — what — 這次要不要用 Claude Code 當第二位讀者？會多花幾分鐘和一些 quota；當這套系統自己的 spec 被審查時，七個嚴重問題中有五個只被其中一個供應商發現。

## Risks
1. A push can succeed before PR creation fails; idempotent remote and existing-PR checks must make retry safe without hiding the partial state.
2. GitHub title edits can stale a passing check unless the workflow explicitly includes the `edited` activity while retaining the existing required-check name.
3. Remote identity and default-base discovery require read-only network queries; mutations remain forbidden until every locally and remotely decidable precondition passes.
