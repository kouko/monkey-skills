# Remove legacy Loom contract compatibility — plan
intent: 2026-09-08-remove-legacy-loom-contract@995cbbcfdd4a96dd647b0e08cf11c91056d199b9
charter: 1.0

## Current State Evidence
- Forward: `loom-code/scripts/loom_checker.py` `cmd_push` selects attestation validation before the legacy branch.
- Reverse: `.github/workflows/loom-workflow-ci.yml` independently discovers workflow tests absent from the declared package command.
- Error: `loom-workflow/skills/git-memory/SKILL.md` still requires an unconditional fresh-context privacy judge.
- Data: `loom-workflow/scripts/test_git_memory_compaction.py` stores whole-file SHA-256 values in `UNCHANGED_CONTRACTS`.
- Boundary: `loom-code/contract/manifest.yaml` declares attestation as the publication contract while legacy checker functions remain reachable fallback code.

## Task DAG

### Wave 0 — close the observed verification gaps

**W0-01 Make one package-test surface authoritative**  after: —  acceptance: 1
- Files: scripts/run_package_tests.py, scripts/test_run_package_tests.py, docs/loom/KICKOFF-DEFAULTS.md, .github/workflows/loom-code-ci.yml, .github/workflows/loom-workflow-ci.yml
- Test: A1 positive: shared-runner-covers-ci-paths; boundary: workflow-cannot-add-unrepresented-loom-suite.
- Risk: CI grouping has distinct pytest configurations; agent-decided — preserve isolated groups behind one declared runner interface.

**W0-02 Make conditional privacy dispatch true at the entrypoint**  after: —  acceptance: 2
- Files: loom-workflow/skills/git-memory/SKILL.md, loom-workflow/scripts/test_git_memory_compaction.py, loom-workflow/skills/git-memory/scripts/test_loom_delegation.py
- Test: A2 positive: ambiguous-private-text-dispatches; negative: public-identifiers-skip-judge-but-scan-runs.
- Risk: Summary prose can accidentally weaken fail-closed handling; agent-decided — retain deterministic blocking and required-judge failure semantics.

**W0-03 Replace contract byte hashes with behavior assertions**  after: —  acceptance: 3
- Files: loom-workflow/scripts/test_git_memory_compaction.py
- Test: A3 positive: required-contract-behaviors-present; negative: whitespace-or-unrelated-prose-change-needs-no-hash-refresh.
- Risk: Weaker assertions could miss contract loss; agent-decided — assert each externally required behavior rather than broad substrings.

### Wave 1 — remove the legacy runtime and prose contract

**W1-01 Delete the legacy checker execution path**  after: W0-01  acceptance: 4, 5
- Files: loom-code/scripts/loom_checker.py, loom-code/scripts/test_loom_attestation.py, loom-code/scripts/test_loom_checker_cli.py, loom-code/contract/manifest.yaml
- Test: A4 positive: attestation-only-push-surface; negative: legacy-options-and-artifacts-rejected. A5 positive: attestation-reviewers-adversarial-pass; boundary: publication-validates-without-replay.
- Risk: Shared helpers may serve non-push rules; agent-decided — prove references before deletion and retain only independently used helpers.

**W1-02 Remove legacy vocabulary from station contracts**  after: W1-01  acceptance: 4
- Files: loom-code/skills/write-plan/SKILL.md, loom-code/skills/build/SKILL.md, loom-code/skills/review/SKILL.md, loom-code/skills/ship/SKILL.md, loom-code/contract/templates/plan.md, loom-code/scripts/test_simplified_station_text.py
- Test: A4 positive: stations-describe-attestation-only-flow; negative: review-ledger-task-accounting-and-replay-terms-absent.
- Risk: Historical records may legitimately name retired behavior; agent-decided — constrain removal to live runtime contracts and tests.

### Wave 2 — integrate and publish the hard cut

**W2-01 Verify the unified contract and release metadata**  after: W0-02, W0-03, W1-02  acceptance: 1, 2, 3, 4, 5
- Files: loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-workflow/CHANGELOG.md, loom-workflow/.claude-plugin/plugin.json, loom-workflow/.codex-plugin/plugin.json, .claude-plugin/marketplace.json
- Test: A1 positive: full-declared-suite-passes; boundary: CI-path-parity. A2 positive: public-carrier-skips-semantic-judge; negative: secret-still-blocks. A3 positive: prose-edit-no-hash-update; boundary: required-behavior-removal-fails. A4 positive: legacy-contract-absent; negative: legacy-input-rejected. A5 positive: attestation-flow-regression-suite-passes; boundary: fast-push-no-executables.
- Risk: Release mirrors can drift; agent-decided — update Claude SSOT first, generate Codex manifests, then run marketplace sync checks.

**W2-memory Memory step — graduated probes and store entries**  after: W2-01
- Files: loom-code/scripts/test_legacy_contract_removed.py, docs/loom/memory/remove-legacy-contract-after-attestation.md
- Test: Run `python3 scripts/check_loom_memory_integrity.py --check`; run the graduated legacy-removal regression test.
- Risk: A task-specific test can duplicate package coverage; agent-decided — graduate only the smallest cross-contract regression that caught real drift.

## Questions asked
① — what — 以上方向對嗎？
① — what — 這次要不要使用 Claude CLI 作為第二位不同供應商的讀者？

## Risks
1. user-decided — old contracts are unsupported; adopting repositories must upgrade instead of receiving a compatibility layer.
2. user-decided — do not use a second-vendor reviewer; closing review uses two fresh-context Codex reviewers.
3. Removing reachable legacy code may expose undocumented consumers; preserve only dependencies proven live by reference and package tests.
4. Suite unification must not collapse pytest groups whose configurations require separate processes.
