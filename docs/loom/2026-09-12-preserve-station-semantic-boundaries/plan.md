# Preserve intent and spec semantic boundaries — plan
intent: 2026-09-12-preserve-station-semantic-boundaries@38c05d53936e3660aac3ee17f62a9d52dbf14bfa
charter: 1.0

## Current State Evidence
- Forward: `loom-design/skills/capture-intent/SKILL.md:143` defines intent-field altitude before writing the artifact.
- Reverse: `loom-design/skills/write-spec/SKILL.md:131` consumes the confirmed intent and authors the specification.
- Error: `docs/skill-dogfood/2026-09-12-capture-intent/report.md:242` records unknown-surface routing and invented-state failures.
- Data: `loom-design/skills/write-spec/SKILL.md:152` maps each numbered Acceptance to an ordered Requirement.
- Boundary: `docs/loom/intent/2026-09-12-preserve-station-semantic-boundaries.md:22` limits changes to two stations and existing tests.

## Task DAG

Wave 0

**W0-01 Preserve station-owned semantics**  after: none  acceptance: 1, 2, 3, 4, 5
- Files: loom-design/skills/capture-intent/SKILL.md, loom-design/skills/write-spec/SKILL.md, loom-design/scripts/spec/test_capture_intent_contract.py, loom-design/scripts/spec/test_write_spec_contract.py
- Test: A1 positive: capture-supported-claims; boundary: publication-carrier. A2 positive: unknown-surface-routes-spec; negative: internal-file-only. A3 positive: acceptance-order-and-temporal-result; negative: invented-state. A4 positive: scope-exclusion-preserved; negative: prohibition-promotion. A5 positive: dual-host-gui-chain; boundary: dual-host-cli-chain.
- Risk: Replace the ineffective generic boundary paragraphs inside existing field rules; add no schema, IDs, checker rule, station, or review loop — agent-decided.

## Questions asked
① — what — 你要避免 Loom 在 capture-intent 與 write-spec 之間自行增加介面、狀態、範圍保證或禁止性需求。完成後，GUI、CLI、API 與使用者依賴的檔案輸出都能以「外部可觀察行為」進入 spec；Acceptance 會逐條保存，未知介面不會被腦補，out-of-scope 也不會變成能力不存在或禁止。同時不修改 write-plan，不新增 ID、checker、station、subagent 或 review loop。對嗎？
① — consequence — 回答同意也會授權通過 Review 與 publication checks 後進行非強制 push 並建立 Ready PR；merge 仍是另一個決定，而且你可以在發布前退出。是否同意？
① — consequence — 這次要不要使用 Codex 作為第二位讀者？

## Risks
1. The original reviewer question named the active host; the user corrected the selected other-vendor reader to sandbox-outside Claude Code.
2. One successful integrated fixture is concept evidence only; GUI and CLI chains on both hosts must pass before claiming the behavior is stable.
3. Static phrase assertions can pass without behavioral improvement; focused tests must encode prohibited and allowed semantic contrasts.
