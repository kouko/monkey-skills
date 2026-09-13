# Harden sanitized evidence probe — plan
intent: 2026-09-13-harden-sanitized-evidence-probe@cca4173e7386f7a0f0ad8ecf5fe9c039daedb67b
charter: 1.0

## Current State Evidence
- Forward: `docs/loom/2026-09-12-publish-sanitized-capture-evidence/evidence/probes/test_sanitized_evidence_public_safe.py:19` limits UUID detection to versions 1–5.
- Reverse: `docs/skill-dogfood/2026-09-12-capture-intent/report.md` and the committed sanitized streams contain no current residual identifier, so the probe needs explicit known-bad self-tests to preserve the boundary.
- Error: terminal reviewers independently found that UUIDv7, path substitution, and sensitive metadata-key replacements can evade the present assertions while the probe exits successfully.
- Data: the committed public evidence population contains exactly 79 known relative paths, 5 JSON files, 48 JSONL files, and 232 retained JSONL events.
- Boundary: `docs/loom/intent/2026-09-13-harden-sanitized-evidence-probe.md` permits only verifier coverage changes.

## Task DAG

Wave 0

**W0-01 Close adversarial coverage gaps**  after: none  acceptance: 1, 2, 3
- Files: docs/loom/2026-09-12-publish-sanitized-capture-evidence/evidence/probes/test_sanitized_evidence_public_safe.py
- Test: A1 negative: UUIDv7 is rejected; boundary: version-agnostic UUID. A2 positive: exact path set passes; negative: path substitution fails. A3 negative: every forbidden metadata key fails inside a retained event; boundary: hostile-cwd execution remains green.
- Risk: Keep one stdlib-only executable and encode the fixed path set directly; avoid a second manifest or repository-wide mechanism — agent-decided.

## Questions asked
① — what — 另開一個極小 maintenance intent，只強化 adversarial probe 的 UUIDv7、完整路徑集合與敏感 metadata key 覆蓋，不改 evidence、報告或實驗結論；修正後重新 Review 再合併。（答：ok）

## Risks
1. The fixed path set intentionally makes additions or removals explicit probe edits; this is evidence integrity, not a general artifact schema.
