# Refresh checker rule-count pins — plan
intent: 2026-09-12-refresh-checker-rule-count-pins@a5c8c74ec5cfd93c9c88e833b1a9dda693fbbc81
charter: 1.0

## Current State Evidence
- Forward: `loom-code/scripts/loom_checker.py` :: `RULES` emits twenty registered rule descriptions.
- Reverse: `loom-code/scripts/test_loom_checker_cli.py` :: `EXPECTED_RULE_IDS` omits the new standing rule.
- Error: `loom-code/scripts/test_loom_checker_cli.py` :: `test_the_rule_population_is_nineteen` fails on twenty lines.
- Data: `docs/loom/evidence/mechanisms.yaml` :: `standing.second-vendor-valid` is registered and recomputes successfully.
- Boundary: `loom-code/scripts/test_probes_language_policy.py` :: the cold-read probe still pins nineteen lines.

## Task DAG

### Wave 0 — synchronize test expectations

**W0-01 Refresh the checker rule population pins**  after: none  acceptance: 1,2,3
- Files: loom-code/scripts/test_loom_checker_cli.py, loom-code/scripts/test_probes_language_policy.py
- Test: A1 positive: exact-rule-set; boundary: missing-new-rule. A2 positive: twenty-lines; negative: stale-nineteen. A3 positive: tests-only-diff; boundary: checker-unchanged.
- Risk: Mechanical counts can drift silently; agent-decided — derive the expected member from the registered rule and change only the three failing assertions.

## Questions asked
① — what — 你要的是：只把 3 個過期的 checker 規則測試從 19 同步為 20，納入 `standing.second-vendor-valid`；不修改 checker、`suggest` 行為、plugin 版本或前輪非阻擋 nit。你回答「對」後，也會授權 Review 通過時自動 non-forced push 並建立 Ready PR；merge 仍由你另外決定。這樣正確嗎？

## Risks
1. This repair starts a new Review episode because the preceding episode exhausted its three functional digests before finalization exposed the stale counts.
2. agent-decided — Keep the prior Review nits out of scope so this recovery remains a mechanical test-expectation correction.
