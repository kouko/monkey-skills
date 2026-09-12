# Close semantic-boundary integration regressions — plan
intent: 2026-09-12-close-semantic-boundary-integration-regressions@823e64e37557a06e6f87afd059992047b433789d
charter: 1.0

## Current State Evidence
- Forward: `loom-design/skills/capture-intent/SKILL.md:106` carries the intake instruction consumed by the code-only compatibility test.
- Reverse: `loom-code/scripts/test_simplified_station_text.py` compares capture-intent wording with write-plan's shared intake contract.
- Error: `loom-code/scripts/test_probes_language_policy.py` rejects a capture-intent sentence that does not relate intent and English together.
- Data: `docs/skill-dogfood/2026-09-12-capture-intent/report.md:304` introduces the raw-output appendix whose paths are local-only.
- Boundary: `docs/loom/intent/2026-09-12-close-semantic-boundary-integration-regressions.md` limits work to three compatibility and evidence findings.

## Task DAG

Wave 0

**W0-01 Restore integration compatibility**  after: none  acceptance: 1, 2, 3
- Files: loom-design/skills/capture-intent/SKILL.md, docs/skill-dogfood/2026-09-12-capture-intent/report.md
- Test: A1 positive: shared-required-field-phrase; boundary: code-only-intake. A2 positive: intent-english-sentence; negative: split-language-policy. A3 positive: raw-local-disclaimer; boundary: focused-and-integration-suite.
- Risk: Preserve all semantic-boundary rules; make only word-neutral wording fixes and one evidence disclaimer, with no new mechanism — agent-decided.

## Questions asked
① — what — 建議另開一個很小的 maintenance intent，只處理兩個相容性修正與 report 的 raw-evidence 說明，不重新設計本次機制。（答：修正吧）

## Risks
1. The prior review episode is closed as NON_CONVERGENT; this newly confirmed intent owns only the remaining compatibility regressions and starts a separate bounded review episode.
