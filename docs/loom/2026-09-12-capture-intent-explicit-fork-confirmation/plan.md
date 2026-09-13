# Capture-intent content boundaries — plan
intent: 2026-09-12-capture-intent-explicit-fork-confirmation@a8156f185
charter: 1.0

## Current State Evidence
- Forward: `loom-design/skills/capture-intent/SKILL.md` Step 1 turns interview answers into the seven existing intent sections.
- Reverse: `loom-code/skills/write-plan/SKILL.md` Step 3 duplicates intake when loom-design is absent.
- Error: `loom-design/scripts/spec/test_capture_intent_contract.py` checks shape but not field altitude or unsupported decisions.
- Data: `loom-code/contract/templates/intent.md` and `contract/manifest.yaml` own the shared intent schema and charter.
- Boundary: `loom-design/skills/capture-intent/references/interview.md` currently prescribes question counts and blind-run-level Acceptance detail.

## Task DAG

### Wave 0 — Define the authoring boundary

**W0-01 Define each existing intent field's altitude**  after: none  acceptance: 1,2,3
- Files: loom-design/skills/capture-intent/SKILL.md, loom-design/skills/capture-intent/references/interview.md, loom-design/scripts/spec/test_capture_intent_contract.py
- Test: A1 positive: field-responsibility; boundary: spec-plan-content. A2 positive: product-value; boundary: engineering-value. A3 positive: outcome-evidence; negative: scenario-detail.
- Risk: agent-decided — preserve all seven fields and Acceptance numbering; change guidance only, because new structure would recreate legacy operational cost.

**W0-02 Make interviewing gap-driven and confirmation evidence-bound**  after: W0-01  acceptance: 4,5,6,7
- Files: loom-design/skills/capture-intent/SKILL.md, loom-design/skills/capture-intent/references/interview.md, loom-design/scripts/spec/test_capture_intent_contract.py, loom-design/CHANGELOG.md, loom-design/.claude-plugin/plugin.json, loom-design/.codex-plugin/plugin.json
- Test: A4 positive: sufficient-history; boundary: missing-field. A5 positive: altitude-reducer; negative: silent-promotion. A6 positive: delegated-question; negative: material-open. A7 positive: explicit-fork; negative: restatement-only.
- Risk: agent-decided — use an author self-check with five outcomes; add no IDs, checker rule, reviewer, fixed quota, or iterative review loop.

### Wave 1 — Keep both installation shapes equivalent

**W1-01 Synchronize the shared contract and code-only fallback**  after: W0-02  acceptance: 8
- Files: loom-code/skills/write-plan/SKILL.md, loom-code/contract/templates/intent.md, loom-code/contract/manifest.yaml, loom-code/scripts/test_simplified_station_text.py, loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, docs/loom/2026-09-12-capture-intent-explicit-fork-confirmation/evidence/dogfood.md
- Test: A8 positive: dual-install-parity; boundary: code-only-parity. Run representative product and engineering cases, plugin suites, manifest sync, boundary, cross-reference, and mechanism-count checks.
- Risk: agent-decided — mirror semantics without changing write-spec, plan DAG, Acceptance mapping, blind-run interface, or deterministic checker population.

## Questions asked
① — what — 你是兩項都同意嗎：確認這份 intent 並授權通過後自動建立 Ready PR，同時使用 sandbox 外的 Claude Code 作為第二位讀者？（答：對，都同意）

## Risks
1. Guidance can become another completeness ritual; tests must prove stopping on sufficient evidence and must reject fixed question quotas.
2. Field definitions can still leak scenario detail through examples; dogfood must score unauthorized visible behaviour separately from document length.
3. Claude review must use the approved sandbox-outside runner; sandbox authentication or preflight paths are outside this change.
