# OKF-compatible loom-memory — plan
intent: 2026-09-10-okf-compatible-loom-memory@c3d0dc26e884ef9ddd4f6bfd366f27df0d28bf52
spec: docs/loom/2026-09-10-okf-compatible-loom-memory/spec.md@648a6d09c3cb2e0a27d80208be6810b44e6210c4
charter: 1.0

## Task DAG

### Wave 1 — Independent package and profile core

**W1-01 Scaffold the standalone plugin**  after: --  acceptance: 4
- Files: loom-memory/.claude-plugin/plugin.json, loom-memory/.codex-plugin/plugin.json, loom-memory/README.md, loom-memory/README.zh-TW.md, loom-memory/README.ja.md, .claude-plugin/marketplace.json, scripts/sync_codex_manifests.py
- Test: A4 positive: memory-plugin-installs-alone; boundary: code-design-manifests-have-no-memory-dependency.
- Risk: Agent-decided: mirror existing dual-host manifest conventions; add no dependency or hook, because the skill-only mechanism is complete and no hook need is measured.

**W1-02 Build the OKF profile validator and generated index**  after: W1-01  acceptance: 1, 2, 6
- Files: loom-memory/scripts/loom_memory.py, loom-memory/scripts/test_loom_memory.py, loom-memory/templates/memory-store/README.md, loom-memory/templates/memory-store/index.md, scripts/fixtures/loom-memory/okf-v0.2/
- Test: A1 positive: valid-profile; negative: malformed-reserved-file. A2 positive: bounded-index; negative: drifted-index. A6 positive: all-offenders; boundary: unrelated-command-unblocked.
- Risk: Agent-decided: one parser serves validation and regeneration; preserve unknown metadata and restrict rewrites to index.md to avoid lossy round trips.

### Wave 2 — Public memory behavior

**W2-01 Implement Recall, Record, Reconcile, and Retire**  after: W1-02  acceptance: 3
- Files: loom-memory/skills/loom-memory/SKILL.md, loom-memory/skills/loom-memory/references/okf-profile.md, loom-memory/skills/loom-memory/references/operations.md, loom-memory/scripts/test_skill_contract.py
- Test: A3 positive: four-operations-contract; boundary: absent-store-empty-recall-and-retire-approval.
- Risk: Agent-decided: expose one public skill across hosts; require explicit approval only for deletion and keep truth checks outside structural validation.

### Wave 3 — Data transition and ownership transfer

**W3-01 Add explicit legacy migration and migrate the repository store**  after: W2-01  acceptance: 5
- Files: loom-memory/scripts/migrate_legacy_store.py, loom-memory/scripts/test_migrate_legacy_store.py, docs/loom/memory/README.md, docs/loom/memory/index.md, docs/loom/memory/*.md, scripts/check_loom_memory_integrity.py, scripts/test_check_loom_memory_integrity.py
- Test: A5 positive: lesson-count-body-description-origin-fingerprints; negative: no-implicit-migration-and-no-legacy-writer.
- Risk: Agent-decided: transform metadata only, preserve lesson bodies and descriptions byte-for-byte, and compare guide and lesson populations separately before retiring the legacy reader.

**W3-02 Remove Ship-owned memory coupling**  after: W3-01  acceptance: 4
- Files: loom-code/contract/manifest.yaml, loom-code/contract/templates/memory-README.md, loom-code/contract/README.md, loom-code/scripts/test_contract_manifest.py, loom-code/scripts/test_probes_charter_charter.py, docs/loom/evidence/mechanisms.yaml, loom-code/skills/ship/SKILL.md
- Test: A4 positive: code-design-operate-without-memory; negative: no-retired-action-template-routing-glob-or-mechanism-pin.
- Risk: Agent-decided: remove repository-memory ownership atomically after migration; retain only the public git-memory declaration and its commit-carrier behavior.

### Wave 4 — Isolation and repository integration

**W4-01 Prove the complete optional integration**  after: W3-02  acceptance: 1, 2, 3, 4, 5, 6
- Files: scripts/test_loom_plugin_install_layout.py, scripts/check_plugin_boundaries.py, scripts/test_check_plugin_boundaries.py, .github/workflows/loom-code-ci.yml, .github/workflows/skill-structure.yml, loom-memory/CHANGELOG.md, loom-code/CHANGELOG.md
- Test: A1 positive: valid-install; negative: invalid-okf. A2 positive: indexed-recall; boundary: bounded-load. A3 positive: operations; negative: unauthorized-retire. A4 positive: consumers-work; boundary: absent-plugin. A5 positive: migrated-corpus; negative: fingerprint-loss. A6 positive: valid-store; negative: corrupt-fixture.
- Risk: Agent-decided: extend existing boundary and install harnesses rather than add a new gate; run one final repository-wide contradiction sweep before closing review.

## Questions asked

None — decision point 1 and the required spec review were completed upstream before this station.

## Risks

1. The migrated corpus is large; fingerprint evidence must be captured before any rewrite so a green post-migration validator cannot conceal lost text.
2. Removing a contract action has scattered prose and test pins; the final sweep must distinguish operative runtime contracts from frozen historical records.
3. Plugin publication surfaces span manifests, marketplace, CI, and versioning; isolated-install success alone does not prove every distribution registry includes loom-memory.
