# Cumulative boundary reassessment — plan
intent: 2026-09-13-cumulative-boundary-reassessment@28ab1a85cd39
charter: 1.0

## Current State Evidence
- Forward: `loom-code/skills/write-plan/SKILL.md:404` sizes tasks by an existing module boundary but does not reassess cumulative erosion.
- Reverse: `loom-code/agents/implementer.md:27` already blocks boundary crossing, so Build needs no duplicate fallback.
- Error: `docs/skill-dogfood/2026-09-13-replaceable-boundary-standard/report.md:51` records a baseline-candidate tie from one-shot cases.
- Data: `docs/loom/2026-09-13-cumulative-boundary-reassessment/proposal.md:149` caps metadata at 20 unique commits and `docs/loom/2026-09-13-cumulative-boundary-reassessment/proposal.md:164` permits three target-only diffs.
- Boundary: `docs/loom/evidence/mechanisms.yaml:4` requires every mechanism to retain an evaluation and a non-rising count unless explicitly excepted.

## Task DAG

### Wave 0 — freeze the evidence boundary

**W0-01 Build longitudinal histories and a failing admission probe**  after: none  acceptance: 1, 2, 3, 5
- Files: docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment/cases.md, docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment/report.md, loom-code/scripts/test_probes_cumulative_boundary_reassessment.py
- Test: A1 positive: L1-third-change; boundary: L1-first-two. A2 positive: L2-preserve; negative: churn-split. A3 positive: L4-noise-preserve; negative: L3-shallow-resplit. A5 positive: matched-real-history; negative: missing-baseline-or-real-run.
- Risk: Synthetic histories can encode the desired answer; agent-decided — freeze causal commits, hashes, blind rubric, and the negative baseline requirement before runtime edits.

### Wave 1 — add the planning contract

**W1-01 Add the always-run screen and conditional detailed reference**  after: W0-01  acceptance: 1, 2, 3, 4
- Files: loom-code/skills/write-plan/SKILL.md, loom-code/skills/write-plan/references/cumulative-boundary-reassessment.md, loom-code/scripts/test_cumulative_boundary_contract.py
- Test: A1 positive: warning-extracts; boundary: pre-warning-preserves. A2 positive: cohesive-churn-preserves; negative: proxy-only-split. A3 positive: noise-filtered-and-shallow-corrected; negative: repeated-file-split. A4 positive: conditional-reference; negative: user-or-skill-route.
- Risk: Entrypoint growth is permanent cost; agent-decided — cap it at 60–90 net words, the reference at 250–400, and change no Build or Review contract.

### Wave 2 — execute and enforce admission

**W2-01 Run matched fresh plans and minimal real implementations**  after: W1-01  acceptance: 1, 2, 3, 4, 5
- Files: docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment/cases.md, docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment/report.md, loom-code/scripts/test_probes_cumulative_boundary_reassessment.py
- Test: A1 positive: L1-candidate-improves; negative: L1-tie. A2 positive: L2-no-false-positive; negative: L2-extraction. A3 positive: L3-L4-correct; negative: shallow-or-noise-split. A4 positive: low-load-rate; boundary: always-loaded. A5 positive: real-run-complete; negative: proposal-only.
- Risk: Small matched cases prove bounded behavior only; agent-decided — retain raw streams privately, commit normalized evidence, exact identities, costs, load rate, and real-run measurements.

**W2-02 Keep or revert the runtime contract from the frozen result**  after: W2-01  acceptance: 5
- Files: loom-code/skills/write-plan/SKILL.md, loom-code/skills/write-plan/references/cumulative-boundary-reassessment.md, loom-code/scripts/test_cumulative_boundary_contract.py, docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment/report.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md
- Test: A5 positive: admitted-contract-retained-and-versioned; negative: failed-bar-runtime-reverted.
- Risk: Package metadata must not imply admission early; agent-decided — update versions and changelog only after a pass, otherwise remove runtime changes and publish the negative report.

## Questions asked

① — what — 你要的是：每次 Loom 開始規劃新功能時，先快速檢查這次會修改的範圍，是否因過去不斷累積而已經無法局部理解、修改與測試；只有出現具體警訊才深入檢查，而且只有「不同責任」與「局部性失效」同時成立時才先整理邊界。完成後，真正累積失效的情況會在實作前被發現；修改頻繁但仍一致、rename／格式化與只做表面拆檔的情況不會被誤判；一般功能不會增加額外的使用者問題，若實驗沒有證明效益就還原。對嗎？
① — consequence — 回答「對」也表示：之後若完成實作與 Review、發布安全檢查通過，可自動進行非強制 push 並建立 Ready PR；merge 仍是另一個決定，你也可以在發布前取消。

## Risks

1. Length, token count, churn, and commit count remain warning signals only; responsibility divergence plus an observable locality failure is required before extraction.
2. Conditional loading saves context only when warning frequency stays low; measure load rate and average contract context instead of assuming a separate reference is cheaper.
3. The bounded A/B corpus cannot establish universal repository, language, model, token, or time savings; claims remain limited to the frozen cases and measurements.
4. Full-patch history can overwhelm useful context; Phase A reads metadata only, while Phase B may inspect at most three target-only diffs selected from 20 unique commits.
5. Raw model and tool streams remain private; normalized plans, hashes, commands, verdicts, costs, and real implementation outcomes must be sufficient for public replay.
