# Extract the Loom repository — plan
intent: 2026-09-13-extract-loom-repository@6dabb0409
charter: 1.0

## Current State Evidence
- Forward: `.claude-plugin/marketplace.json` maps the three public Loom plugin names to monorepo subdirectories.
- Reverse: `scripts/test_loom_plugin_install_layout.py::_install_plugin` reconstructs installed plugin roots from those three source directories.
- Error: `scripts/check_plugin_boundaries.py::find_boundary_violations` rejects runtime references that work only beside sibling plugin directories.
- Data: `loom-code/contract/manifest.yaml` owns the shared artifact and checker contract consumed across the Loom family.
- Boundary: `.github/workflows/loom-code-ci.yml` combines plugin-local suites with repository-level manifests, evidence, and integration gates.

## Task DAG

### Wave 1 — define and prove the extraction boundary

**W1-01 Build a fail-closed history inventory**  after: none  acceptance: 1,2,3,5
- Files: scripts/extract_loom_repository.py, scripts/test_extract_loom_repository.py, scripts/loom_repository_paths.txt
- Test: A1 positive: current-tree-coverage; negative: missing-required-path. A2 positive: metadata-and-map; boundary: rewritten-SHA. A3 positive: mixed-commit-content; negative: non-Loom-content. A5 positive: isolated-target; boundary: existing-destination.
- Risk: Keep an explicit reviewed path manifest and reject unclassified required files; agent-decided because heuristic-only selection would silently lose history.

### Wave 2 — construct an independently testable repository

**W2-01 Generate the filtered repository and bootstrap its root**  after: W1-01  acceptance: 1,2,3,5
- Files: scripts/extract_loom_repository.py, scripts/test_extract_loom_repository.py, scripts/loom-repository-bootstrap/, docs/loom/2026-09-13-extract-loom-repository/evidence/
- Test: A1 positive: clean-source-extraction; negative: stale-source-ref. A2 positive: blame-and-message; boundary: commit-map-roundtrip. A3 positive: mixed-commit-sample; negative: unrelated-path-retained. A5 positive: source-unchanged; negative: remote-configured.
- Risk: Run filter-repo only in a newly created clone and never configure a destination remote; agent-decided to keep every operation reversible and local.

### Wave 3 — restore and verify repository-level development gates

**W3-01 Adapt the minimum root infrastructure and run the package matrix**  after: W2-01  acceptance: 1,4,5
- Files: scripts/loom-repository-bootstrap/, scripts/test_extract_loom_repository.py, docs/loom/2026-09-13-extract-loom-repository/evidence/verification.md
- Test: A1 positive: bootstrap-manifest-complete; negative: monkey-skills-only-plugin. A4 positive: package-and-isolation-matrix; negative: sibling-private-path. A5 positive: no-source-diff; boundary: no-push-or-delete.
- Risk: Port only gates exercised by the three Loom packages; agent-decided because copying monorepo-wide CI would retain unrelated ownership.

## Questions asked
① — what — 你要的是建立一個可獨立維護 Loom 三個 plugin 的候選 repository；完成後可以保留逐檔歷史與 blame、查回原始 commit、確認混合 commit 沒漏掉 Loom 內容，並通過原有安裝與測試。第一階段只建立本機候選，不建立或推送 GitHub repo，也不刪除 monkey-skills 的內容；歷史改寫只發生在 fresh clone，不碰現有 repository。如果回答「是」，也代表完整 Review 與發布檢查通過後，可以自動 push 這次在 monkey-skills 內新增的遷移工具與 Ready PR；不包含建立或推送新的 Loom repository，merge 仍另行決定，也可在發布前取消。以上正確嗎？

## Risks
1. Path filtering rewrites commit identities; the committed map must remain the authoritative old-to-new lookup rather than claiming SHA preservation.
2. More than half of Loom-touching commits also touch other paths, so verification must inspect mixed commits, not only current files.
3. Project-wide `docs/loom/` records cannot be copied wholesale without importing unrelated plugin history and ownership.
4. Historical signatures cannot remain valid after tree rewriting; author identity and messages are preserved, but rewritten commits are unsigned.
