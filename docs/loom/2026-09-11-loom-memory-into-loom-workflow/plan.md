# loom-memory into loom-workflow — plan
intent: 2026-09-11-loom-memory-into-loom-workflow@3e136a4de

## Current State Evidence

- Forward: `.claude-plugin/marketplace.json` under the last `plugins[]` entry declares `loom-memory` with `"source": "./loom-memory/"`, the packaging surface this change removes.
- Reverse: `scripts/run_package_tests.py` under `loom_family_commands` globs `loom-workflow/skills/*/scripts` for `test_*.py`, so a skill placed there is discovered with no runner edit, while the sibling `memory` group hard-codes `loom-memory/scripts/`.
- Error: `.claude/hooks/check-memory-store-integrity.sh` under `VALIDATOR=` resolves `loom-memory/scripts/loom_memory.py` and fails open when absent, so a move without a repoint silently stops guarding the store.
- Data: `docs/loom/memory/` holds the 293 migrated lesson concepts plus `README.md` and the generated `index.md`; this change must leave every byte of it unchanged.
- Boundary: `CLAUDE.md` under `Skill Structure` forbids a subfolder inside a skill subfolder, so `templates/memory-store/` cannot move under the skill unchanged.

## Task DAG

### Wave 1 — Relocate the capability

**W1-01 Move the skill, its references, its scripts and the store template**  after: --  acceptance: 1
- Files: loom-workflow/skills/loom-memory/SKILL.md, loom-workflow/skills/loom-memory/references/okf-profile.md, loom-workflow/skills/loom-memory/references/operations.md, loom-workflow/skills/loom-memory/scripts/loom_memory.py, loom-workflow/skills/loom-memory/scripts/migrate_legacy_store.py, loom-workflow/skills/loom-memory/scripts/test_loom_memory.py, loom-workflow/skills/loom-memory/scripts/test_migrate_legacy_store.py, loom-workflow/skills/loom-memory/scripts/test_skill_contract.py, loom-workflow/skills/loom-memory/templates/memory-store-README.md, loom-workflow/skills/loom-memory/templates/memory-store-index.md
- Test: A1 positive: four-operations-available-with-only-loom-workflow; negative: no-nested-subfolder-under-the-skill.
- Risk: Agent-decided: per-skill `scripts/` because six loom-workflow skills already use it and the runner discovers it by glob; the two-level template directory flattens to single-level filenames because the skill-folder rule forbids the nesting.

**W1-02 Repoint every command that names the old validator path**  after: W1-01  acceptance: 4
- Files: .claude/hooks/check-memory-store-integrity.sh, .claude/hooks/test_check_memory_store_integrity.py, AGENTS.md, docs/loom/memory/README.md
- Test: A4 positive: hook-and-docs-run-the-relocated-validator; negative: no-runnable-reference-to-the-retired-path.
- Risk: Agent-decided: the hook test pins its remediation strings verbatim, so hook and test move in one commit; the fail-open guard stays so a repo without loom-workflow still no-ops rather than reporting a phantom violation.

### Wave 2 — Retire the standalone plugin

**W2-01 Delete the plugin and its packaging surfaces**  after: W1-02  acceptance: 2
- Files: loom-memory/, .claude-plugin/marketplace.json, scripts/sync_codex_manifests.py, scripts/run_package_tests.py, scripts/test_run_package_tests.py, scripts/fixtures/loom-memory/, README.md, README.ja.md, README.zh-TW.md
- Test: A2 positive: no-loom-memory-plugin-anywhere; negative: marketplace-and-codex-eligible-stay-valid-json-after-the-last-entry-is-removed.
- Risk: Agent-decided: the `memory` test group goes away entirely rather than being repointed, because the destination is already covered by the `workflow-python` glob; the entry is last in both lists, so removing it must fix the preceding separator.

**W2-02 Remove the plugin's CI steps and repoint the store-integrity job**  after: W2-01  acceptance: 2, 4
- Files: .github/workflows/loom-code-ci.yml, .github/workflows/skill-structure.yml
- Test: A2 positive: no-workflow-step-names-the-retired-plugin; boundary: store-integrity-job-still-validates-the-real-store. A4 positive: relocated-validator-runs-in-ci; negative: no-ci-path-filter-for-a-directory-that-no-longer-exists.
- Risk: Agent-decided: keep the store-integrity job and repoint it rather than folding it into another job, because branch protection pins required checks by display name and renaming one silently drops its protection.

### Wave 3 — Consumers, standing documents and the store itself

**W3-01 Rewrite the isolation proofs for the new shape**  after: W2-02  acceptance: 5
- Files: scripts/test_loom_plugin_install_layout.py, scripts/check_plugin_boundaries.py, scripts/test_check_plugin_boundaries.py, loom-code/scripts/check_contract_citations.py, loom-workflow/scripts/test_skill_count.py
- Test: A5 positive: absent-workflow-failure-set-identical-before-and-after; negative: no-test-still-asserts-a-standalone-memory-plugin.
- Risk: Agent-decided: the absence case changes meaning — it was "loom-memory absent", it becomes "loom-workflow absent" — so those assertions are rewritten to the new property rather than deleted, and the citation-scan root moves with the skill.

**W3-02 Standing documents, versions, and proof the store did not move**  after: W3-01  acceptance: 2, 3
- Files: PRINCIPLES.md, loom-workflow/.claude-plugin/plugin.json, loom-workflow/.codex-plugin/plugin.json, loom-workflow/CHANGELOG.md, docs/loom/maps/family-relocation/MAP.md, docs/loom/backlog/2026-07-22-loom-memory-store-hardening-deferred-f2-f3-f5-f6.md, docs/loom/backlog/2026-08-07-mechanize-loom-memory-prune-pretriage.md
- Test: A2 positive: principles-names-three-loom-family-plugins; negative: no-standing-document-still-claims-a-fourth. A3 positive: store-byte-identical-to-trunk; negative: store-still-validates-under-the-relocated-validator.
- Risk: Agent-decided: the ratification line gained a same-day amendment for the four-plugin wording, so this reverts that clause and records the second amendment rather than overwriting the first silently. The two closed/amnestied backlog records above are edited only for the stale `loom-pipeline/` → `loom-workflow/` path in text they already carried — the frozen `status: closed` verdict and body are otherwise untouched.

## Questions asked

- 1 — what — 你要的是：記憶變成 loom-workflow 工具箱裡的一把工具，跟 git-memory、handoff、decision-map 並排；那個獨立的 loom-memory plugin 退掉。對嗎？
- 1 — consequence — 退掉一個已經發佈的 plugin：任何已經裝了它的人會失去更新、安裝會壞掉。
- 1 — consequence — 這把工具的名字打算叫 loom-workflow:loom-memory；名字一旦上線就會被打進肌肉記憶和別的腳本，之後改名等於破壞相容。
- 1 — what — 這次要不要用 Codex 當第二位讀者？

## Risks

1. user-decided — kouko chose the toolbox shape over a standalone plugin, because memory is one tool he reaches for beside git-memory rather than something a repository installs on its own.
2. user-decided — kouko declined a second vendor for this change, so the closing review runs with same-vendor readers only; the previous change's second-vendor findings are already fixed and shipped.
3. The store is the one thing this change must not touch, and it sits one directory away from everything being moved; the byte-identity proof against trunk is what separates a relocation from an accidental rewrite.
4. Running pytest inside a skill directory writes `__pycache__`, which this repo's skill-folder hook rejects; the destination is a skill directory, so the test invocation has to suppress bytecode or the hook blocks unrelated edits afterwards.
5. A live decision map ticket already tracks this relocation, so leaving it open after the change ships would make the map disagree with the repository.
