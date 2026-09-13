# Modularize the Loom checker — plan
intent: 2026-09-13-checker-modularize@c61b2522d
charter: 1.0

## Current State Evidence
- Forward: `loom-code/scripts/loom_checker.py:COMMANDS` exposes every command through one registry and the `main` dispatch path.
- Reverse: `loom-code/scripts/test_loom_publish.py:import loom_checker` imports checker functions directly, coupling tests to the monolithic entry module.
- Error: `loom-code/scripts/loom_checker.py:main-exception` converts unexpected command failures into the stable exit-2 error contract.
- Data: `loom-code/scripts/loom_checker.py:RULES` stores nineteen public rule identifiers and descriptions in the entry file.
- Boundary: `loom-code/hooks/hooks-codex.json:PreToolUse` invokes `scripts/loom_checker.py`, fixing the executable path while permitting internal packages.

## Task DAG

### Wave 0 — Pin the module contract

**W0-01 Add modularization contract tests**  after: none  acceptance: 1,3,4,5
- Files: loom-code/scripts/test_loom_checker_modules.py, loom-code/scripts/test_check_mechanisms.py
- Test: A1 positive: rule-module-import; boundary: isolated-rule-import. A3 positive: thin-entry; negative: implementation-leak. A4 positive: cli-snapshot; boundary: hook-path. A5 positive: mechanism-rules; negative: missing-rule.
- Risk: Tests may overfit formatting; agent-decided — assert public symbols, process results, and AST ownership rather than source layout trivia.

### Wave 1 — Extract dependency leaves

**W1-01 Extract shared checker foundations**  after: W0-01  acceptance: 1,2,5,6
- Files: loom-code/scripts/loom_checker/__init__.py, loom-code/scripts/loom_checker/rules.py, loom-code/scripts/loom_checker/helpers.py, loom-code/scripts/loom_checker/parsing.py, loom-code/scripts/loom_checker/digest.py, loom-code/scripts/loom_checker/attestation.py, loom-code/scripts/loom_checker/probes.py, loom-code/scripts/loom_checker/artifact_types.py
- Test: A1 positive: rule-direct-import; boundary: no-command-import. A2 positive: shared-module-imports; negative: circular-import. A5 positive: rule-enumeration; negative: absent-rule. A6 positive: helper-suite; boundary: git-exec-unchanged.
- Risk: Shared globals can create cycles; agent-decided — move dependency leaves first and keep direction from commands toward foundations.

### Wave 2 — Extract command handlers

**W2-01 Extract intent and planning commands**  after: W1-01  acceptance: 2,4,6
- Files: loom-code/scripts/loom_checker/commands/__init__.py, loom-code/scripts/loom_checker/commands/intent.py, loom-code/scripts/loom_checker/commands/intake.py, loom-code/scripts/loom_checker/commands/standing.py, loom-code/scripts/loom_checker/commands/contract.py, loom-code/scripts/loom_checker/commands/charter.py, loom-code/scripts/loom_checker/commands/plan.py, loom-code/scripts/test_loom_checker_modules.py
- Test: A2 positive: command-module-imports; boundary: shared-helper-use. A4 positive: command-golden-cases; negative: usage-errors. A6 positive: focused-command-suite; boundary: direct-import-consumers.
- Risk: Intent checks share history helpers; agent-decided — keep rule-specific checks beside their owning command and extract only genuinely shared primitives.

**W2-02 Extract publication and finalization commands**  after: W1-01  acceptance: 2,4,6
- Files: loom-code/scripts/loom_checker/commands/push.py, loom-code/scripts/loom_checker/commands/publish.py, loom-code/scripts/loom_checker/commands/finalize.py, loom-code/scripts/test_loom_publish.py, loom-code/scripts/test_ship_worktree_merge.py, loom-code/scripts/test_loom_attestation.py, loom-code/scripts/test_loom_checker_modules.py
- Test: A2 positive: publication-module-imports; boundary: finalize-separation. A4 positive: publish-contract; negative: fail-closed-paths. A6 positive: publication-suite; boundary: attestation-suite.
- Risk: Monkeypatch targets can silently stop intercepting calls; agent-decided — update tests to patch the module where each dependency is resolved.

### Wave 3 — Replace the monolith and integrate

**W3-01 Reduce the entry point and verify all consumers**  after: W2-01, W2-02  acceptance: 3,4,5,6
- Files: loom-code/scripts/loom_checker.py, loom-code/scripts/check_mechanisms.py, loom-code/scripts/test_loom_checker_cli.py, loom-code/scripts/test_check_mechanisms.py, loom-code/hooks/hooks.json, loom-code/hooks/hooks-codex.json
- Test: A3 positive: entry-registry-main; negative: extra-definition. A4 positive: full-cli-suite; boundary: both-hooks. A5 positive: mechanism-population; negative: rule-loss. A6 positive: integration-suite; boundary: no-new-dependency.
- Risk: Direct imports outside known tests may break; agent-decided — repository-wide search and isolated-install execution close the consumer boundary.

## Questions asked
1 — what — 你要的是把 Loom checker 拆成可獨立測試的規則、共用模組與命令檔，同時完整保留 CLI、輸出、hook、imports 與 mechanism 掃描行為，且不修改 `git_exec.py`。對嗎？
1 — consequence — 請回覆以下其中一項：「是，不使用 Claude」、「是，使用 Claude」或「否：……」。

## Risks
1. User-decided — declined Claude cross-model review for this change; the normal repository reviewer floor remains independently enforced.
2. Moving names changes monkeypatch lookup locations; tests must patch owning modules and preserve observable command behavior.
3. Importing a package beside the executable can differ under direct script execution; integration tests must run from a hostile working directory.
