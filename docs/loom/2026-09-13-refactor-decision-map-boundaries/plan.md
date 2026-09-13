# Refactor Decision Map boundaries — plan
intent: 2026-09-13-refactor-decision-map-boundaries@a9038ccd4
charter: 1.0

## Current State Evidence
- Forward: `decision-map/SKILL.md` directly names validation and transaction entry points used by the workflow.
- Reverse: `map_store.py` exports models, parsing, persistence, lifecycle helpers, validation, and its CLI from one module.
- Error: `map_store.py::SchemaViolation` and transaction exceptions form observable contracts pinned by existing tests.
- Data: `map-format.md` declares schema-v3 `MAP.md`, ticket, operation, and relation invariants.
- Boundary: `map_lifecycle.py` and `map_transaction.py` call private `map_store` helpers across module boundaries.

## Task DAG

### Wave 1 — characterize and separate read-side responsibilities

**W1-01 Pin the compatibility surface and extract documents**  after: none  acceptance: 1,2
- Files: loom-workflow/skills/decision-map/scripts/test_map_module_boundaries.py, loom-workflow/skills/decision-map/scripts/map_documents.py, loom-workflow/skills/decision-map/scripts/map_store.py
- Test: A1 positive: existing-import-surface; boundary: exception-identity. A2 positive: document-owner; negative: no-parser-definitions-in-facade.
- Risk: Re-export existing symbols from the facade; agent-decided because callers already depend on those names.

**W1-02 Extract persistence and remove private cross-module calls**  after: W1-01  acceptance: 1,2
- Files: loom-workflow/skills/decision-map/scripts/test_map_module_boundaries.py, loom-workflow/skills/decision-map/scripts/map_persistence.py, loom-workflow/skills/decision-map/scripts/map_store.py, loom-workflow/skills/decision-map/scripts/map_lifecycle.py, loom-workflow/skills/decision-map/scripts/map_transaction.py, loom-workflow/skills/decision-map/scripts/migrate_map_v3.py
- Test: A1 positive: atomic-behavior; negative: cas-mismatch. A2 positive: persistence-owner; boundary: no-private-store-io-calls.
- Risk: Preserve exception translation and fault-injection seams; agent-decided to move behavior mechanically before changing callers.

### Wave 2 — separate validation and transaction coordination

**W2-01 Extract validation behind the compatible facade**  after: W1-02  acceptance: 1,2
- Files: loom-workflow/skills/decision-map/scripts/test_map_module_boundaries.py, loom-workflow/skills/decision-map/scripts/map_validation.py, loom-workflow/skills/decision-map/scripts/map_store.py
- Test: A1 positive: valid-store-result; negative: invalid-store-message. A2 positive: validation-owner; boundary: thin-validate-delegation.
- Risk: Preserve validation order and exact diagnostics; agent-decided because consumers may compare user-visible failure text.

**W2-02 Split ticket mutations from close/rechart coordination**  after: W2-01  acceptance: 1,2
- Files: loom-workflow/skills/decision-map/scripts/test_map_module_boundaries.py, loom-workflow/skills/decision-map/scripts/map_ticket_mutations.py, loom-workflow/skills/decision-map/scripts/map_close_transaction.py, loom-workflow/skills/decision-map/scripts/map_transaction.py
- Test: A1 positive: transaction-api-parity; negative: stale-revision-refusal. A2 positive: transaction-owner; boundary: facade-has-no-locked-implementations.
- Risk: Preserve locking and mutation order; agent-decided to retain `map_transaction` as the public compatibility facade.

### Wave 3 — package integration

**W3-01 Verify the full Decision Map package and repository boundary**  after: W2-02  acceptance: 1,3
- Files: loom-workflow/skills/decision-map/scripts/test_map_module_boundaries.py, loom-workflow/CHANGELOG.md
- Test: A1 positive: decision-map-suite; negative: public-api-regression. A3 positive: package-suite; boundary: isolated-plugin-layout.
- Risk: No opportunistic behavior changes; agent-decided to revert any extraction that cannot preserve existing tests exactly.

**W3-02 Align the plugin release metadata**  after: W3-01  acceptance: 3
- Files: loom-workflow/CHANGELOG.md, loom-workflow/.claude-plugin/plugin.json, loom-workflow/.codex-plugin/plugin.json, README.md
- Test: A3 positive: package-suite-version; negative: changelog-manifest-drift.
- Risk: Use the next patch version and manifest sync; agent-decided because this is a compatible internal refactor release.

## Questions asked
1 — what — 第一個變更的 intent 已起草。你要的是：在不改變既有指令、Python 入口、錯誤行為及資料格式的前提下，拆清 Decision Map 的驗證、解析、儲存與交易責任；完成後，各部分可獨立測試，既有套件與整合測試維持通過。對嗎？

## Risks
1. Mechanical moves can still change import identity, monkeypatch seams, diagnostic ordering, or filesystem fault behavior.
2. New modules must reduce responsibility span without creating circular imports or duplicated compatibility wrappers.
3. Performance is not an objective; no optimization claim is made without a separate measurement.
