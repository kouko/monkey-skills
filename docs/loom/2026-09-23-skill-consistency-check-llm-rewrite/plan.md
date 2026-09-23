# skill-consistency-check LLM rewrite — plan
intent: 2026-09-23-skill-consistency-check-llm-rewrite@8c656586a
spec: docs/loom/2026-09-23-skill-consistency-check-llm-rewrite/spec.md
charter: 1.0

## Task DAG
Wave 1 clears the old implementation and imports the corpus; wave 2 builds the two deterministic scripts; wave 3 writes the skill text and release bookkeeping on top of them.

**W1-01 Remove the Z3 implementation**  after: none  acceptance: 6
- Files: skill-consistency-check/install.sh, skill-consistency-check/skill-consistency-check, skill-consistency-check/scripts/*.py, skill-consistency-check/references/*.md, scripts/adversarial_probe.py, docs/loom/2026-09-22-skill-consistency-check/attestation.json
- Test: A6 positive: T-removed-paths-absent; negative: T-no-reference-to-removed-scripts.
- Risk: agent-decided delete, recoverable from git history; SKILL.md stays for W3-01 rewrite; no existing tests cover these files (spec Current state evidence).

**W1-02 Import regression corpus and scoring helper**  after: none  acceptance: 2
- Files: skill-dev-toolkit/tests/consistency-check-corpus/README.md, single-a/, single-b/, multi/, score.py, test_score.py
- Test: A2 positive: T-score-recorded-round8-union-6of6; negative: T-score-flags-fabricated-high-false.
- Risk: agent-decided location outside skills/ because the corpus has nested folders; the 120k filler package is excluded (spec Design decision, REQ-2).

**W2-01 Grouping planner script**  after: W1-01  acceptance: 3, 5
- Files: skill-consistency-check/scripts/plan_groups.py, skill-consistency-check/scripts/test_plan_groups.py
- Test: A3 positive: T-small-package-single-group; boundary: T-large-package-offset-groups-core-and-uncovered-pairs. A5 positive: T-target-tree-unchanged; boundary: T-core-over-limit-flagged.
- Risk: token estimate is heuristic (CJK one each, else chars/4), agent-decided per spec REQ-3 Design decision; thresholds stay conservative.

**W2-02 Merge and report script**  after: W1-01  acceptance: 1, 4, 5
- Files: skill-consistency-check/scripts/merge_report.py, skill-consistency-check/scripts/test_merge_report.py
- Test: A1 positive: T-high-gives-needs-revision; negative: T-medium-low-only-pass. A4 positive: T-limits-and-models-listed; boundary: T-model-mismatch-warning. A5 positive: T-out-outside-target-written; negative: T-out-inside-target-refused.
- Risk: dedupe window of two lines may merge adjacent distinct findings; agent-decided per spec REQ-1 Design decision.

**W3-01 Skill text, detector specs and skill READMEs**  after: W2-01, W2-02  acceptance: 8
- Files: skill-consistency-check/SKILL.md, references/detector-read.md, references/detector-simulate.md, README.md, README.ja.md, README.zh-TW.md
- Test: A8 positive: T-structure-and-description-checks-pass; negative: T-no-host-only-tool-or-model-id-in-skill-text.
- Risk: detector specs copied from validated experiment text; edits beyond the file field risk invalidating results, so wording changes stay minimal (spec REQ-8 Design decision).

**W3-02 Plugin release bookkeeping**  after: W3-01  acceptance: 7
- Files: skill-dev-toolkit/.claude-plugin/plugin.json, skill-dev-toolkit/.codex-plugin/plugin.json, skill-dev-toolkit/README.md, README.ja.md, README.zh-TW.md, skill-dev-toolkit/CHANGELOG.md, .claude-plugin/marketplace.json
- Test: A7 positive: T-package-suite-passes; negative: T-version-sync-and-description-checks-pass.
- Risk: agent-decided minor bump 0.4.1 to 0.5.0 for a new capability; Codex manifest synced by scripts/sync_codex_manifests.py.

## Questions asked
① — consequence — 你說「對」之後：等最後的審查和發佈前檢查都通過，會自動 push 分支並開一個 Ready 狀態的 PR；合併仍然要你另外同意。（使用者：對）
① — what — 這樣對嗎？（重述需求、三項一旦執行就不易回頭的後果與五條具體規則；使用者先回「每檢查一個 skill 就要跑 2 次 sonnet <- 我們應該不是寫死模型型號吧？ 因為這個 skill 也要用在 codex 歐」，修改後回答：對）

## Risks
1. No CI job runs skill-dev-toolkit script tests; agent-decided not to add one in this change, tests run via pytest on the skill scripts folder and corpus folder.
2. Acceptance 2 and 8 need live model runs; they are proven only by the blind run, not by unit tests.
3. Validation evidence is small (six skills, 27 plants); the report states the reference model and size rather than claiming general accuracy.
4. user-decided — model is not hardcoded and the skill must run on Codex; accuracy is validated only on the reference model.
5. agent-decided — not authorised, took the conservative option: default check runs two detectors; the four-run thorough mode is opt-in only.
6. user-decided — second-vendor selection-confirmed: codex
