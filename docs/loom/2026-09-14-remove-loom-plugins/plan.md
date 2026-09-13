# Remove Loom plugins from monkey-skills — plan
intent: 2026-09-14-remove-loom-plugins@ad0eb01d9
spec: docs/loom/2026-09-14-remove-loom-plugins/spec.md@62d8036
charter: 1.0

## Current State Evidence
- Forward: `.claude-plugin/marketplace.json` lists Loom plugin entries.
- Reverse: `loom-code/`, `loom-design/`, and `loom-workflow/` are tracked plugin roots.
- Error: `.github/workflows/` contains Loom-specific CI and deleted-path references.
- Data: `scripts/` contains Loom extraction, package-runner, and integrity tooling.
- Boundary: `docs/loom/` is the retained historical record store.

## Task DAG

**W0-01 Remove Loom runtime and publication surfaces**  after: none  acceptance: 1, 2
- Files: loom-code/, loom-design/, loom-workflow/, .claude-plugin/marketplace.json, .github/workflows/, .claude/settings.json
- Test: A1 positive: marketplace-no-loom; boundary: stale-path-scan. A2 positive: loom-only-surfaces-absent; boundary: historical-records-retained
- Risk: A deleted runtime path could remain in CI or hooks; agent-decided choice is to scan current files and validate JSON/YAML-adjacent configs.

**W0-02 Remove Loom-only repository tooling and update documentation**  after: W0-01  acceptance: 2, 4
- Files: scripts/, README.md, README.ja.md, README.zh-TW.md, CLAUDE.md, AGENTS.md, ATTRIBUTION.md, requirements-dev.txt
- Test: A2 positive: repository-test-suite; boundary: docs-loom-preserved. A4 positive: docs-loom-readable; boundary: no-historical-deletion
- Risk: Historical references may be mistaken for runtime dependencies; agent-decided choice is to preserve `docs/loom/` and edit only current surfaces.

**W0-03 Verify remaining plugin contracts**  after: W0-02  acceptance: 3
- Files: scripts/test_check_skill_structure.py, scripts/sync_codex_manifests.py, cross-plugin runtime references
- Test: A3 positive: marketplace-description-sync; boundary: plugin-description-coherence
- Risk: Removing a shared helper could affect non-Loom plugins; agent-decided choice is to run focused repository checks before handoff.

## Questions asked
① — done — 「可以幫我移除 monkey-skills 裡的 loom plugin 嗎」
① — consequence — 「2」確認完整清理 Loom 專屬 CI、hooks、runner、測試與 extraction tooling，並保留歷史紀錄。

## Risks
1. The change is deletion-heavy; the independent `loom-plugins` repository is the recovery source and remains outside this branch.
2. Existing historical documents may mention removed paths; those references are retained as provenance, not treated as executable dependencies.
