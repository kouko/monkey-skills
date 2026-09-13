# Evidence-based modular implementation decisions — plan
intent: 2026-09-13-replaceable-boundary-standard@18e1aacf100b746dddf7a5d43199f09b61155a0b
charter: 1.0

## Current State Evidence
- Forward: `loom-code/skills/write-plan/SKILL.md:404` requires one module boundary but gives no evidence test for choosing that boundary.
- Reverse: `loom-code/agents/implementer.md:27` blocks unplanned boundary crossing and `:34` reports edits outside the planned file set.
- Error: `docs/skill-dogfood/2026-09-12-capture-intent/report.md:140` shows generic boundary prose added prompt cost without measured behavioral improvement.
- Data: `loom-code/skills/review/references/lenses.md:42` already scores architecture, refactoring, cross-task coherence, and deletion-first.
- Boundary: `docs/loom/evidence/mechanisms.yaml:4` requires regression evidence and a non-rising mechanism count unless an exception is declared.

## Task DAG

Wave 0

**W0-01 Make planning and implementation choose meaningful boundaries**  after: none  acceptance: 1, 2, 4
- Files: loom-code/skills/write-plan/SKILL.md, loom-code/agents/implementer.md, loom-code/scripts/test_modular_implementation_contract.py
- Test: A1 positive: separable-responsibility-extracts; negative: dependency-preserving-split. A2 positive: cohesive-long-file-stays; negative: length-only-extraction. A4 positive: existing-stations-own-decision; negative: extra-user-or-skill-route.
- Risk: Replace existing boundary wording with stage-owned decisions; add no score, threshold, skill, artifact, checker rule, or user question — agent-decided.

Wave 1

**W1-01 Make closing review reject shallow file splits**  after: W0-01  acceptance: 3
- Files: loom-code/skills/review/references/lenses.md, loom-code/agents/reviewer.md, loom-code/scripts/test_modular_implementation_contract.py
- Test: A3 positive: independent-boundary-passes; negative: shared-state-or-change-scope-split-fails.
- Risk: Strengthen existing architecture and refactoring dimensions; every finding needs anchored evidence that coupling or change scope remains — agent-decided.

Wave 2

**W2-01 Prove the three decisions with matched cold-read cases**  after: W1-01  acceptance: 1, 2, 3, 4, 5
- Files: docs/skill-dogfood/2026-09-13-replaceable-boundary-standard/cases.md, docs/skill-dogfood/2026-09-13-replaceable-boundary-standard/report.md, loom-code/scripts/test_probes_replaceable_boundary_behavior.py
- Test: A1 positive: extraction-case-improves; negative: coupled-result. A2 positive: cohesive-file-kept; negative: length-only-split. A3 positive: shallow-split-found; negative: false-pass. A4 positive: existing-flow-only; boundary: no-new-mechanism. A5 positive: evidence-and-suite-pass; negative: missing-case-blocks.
- Risk: Compare identical baseline and candidate cases; without required improvement and no new false positives, stop and reshape instead of shipping prompt cost — agent-decided.

## Questions asked
① — what — 你要的是：使用 Loom 開發軟體時，它能根據責任是否混雜、修改能否集中、能否獨立測試，自動判斷應保留完整程式，還是抽出真正獨立的部分；不因檔案行數機械拆檔，也不增加額外的使用者決策。做完後：適合分離的功能會形成可獨立理解與測試的邊界；長但職責一致的檔案不會被強制拆開；只搬動程式、沒有降低依賴的假模組化會在最終檢查中被發現。對嗎？
① — consequence — 回答「對」也代表：完成實作與審查、發布安全檢查通過後，可以自動進行非強制 push 並建立 Ready PR；merge 仍是另一個決定，你也可以在發布前取消自動發布。

## Risks
1. File length remains a warning only; semantic responsibility, dependency direction, test isolation, and change locality decide whether extraction helps.
2. Matched A/B cases prove only this contract and corpus; they cannot establish a universal line, token, language, repository, or model threshold.
3. Commit normalized case outcomes and contract hashes only; raw model streams remain private and cannot substitute for replayable regression evidence.
