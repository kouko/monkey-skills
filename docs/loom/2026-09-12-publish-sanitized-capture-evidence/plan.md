# Publish sanitized capture-intent evidence — plan
intent: 2026-09-12-publish-sanitized-capture-evidence@0c91b22ae85f2d6fcc62fe34605d9505daae8fee
charter: 1.0

## Current State Evidence
- Forward: `docs/skill-dogfood/2026-09-12-capture-intent/report.md:307` names the raw evidence as local-only.
- Reverse: the 79 author-local files under `docs/skill-dogfood/2026-09-12-capture-intent/raw-private/` are the source population and remain excluded from Git.
- Error: unsanitized JSONL system events expose host paths, session identifiers, connector state, tool inventory, and thinking signatures.
- Data: the source population contains 79 files totaling about 3.1 MB; the sanitized population contains the same 79 paths and 48 parseable JSONL streams.
- Boundary: `docs/loom/intent/2026-09-12-publish-sanitized-capture-evidence.md` permits evidence publication but no skill, station, checker, or experiment-result change.

## Task DAG

Wave 0

**W0-01 Publish sanitized evidence**  after: none  acceptance: 1, 2, 3
- Files: docs/skill-dogfood/2026-09-12-capture-intent/raw/, docs/skill-dogfood/2026-09-12-capture-intent/report.md
- Test: A1 positive: 79-path population match; boundary: JSON and JSONL parse. A2 negative: privacy scan and residual-pattern scan find no excluded metadata; boundary: zero system or rate-limit events. A3 positive: report names committed sanitized evidence and private originals separately.
- Risk: Preserve all model-visible experiment content while deleting only executor-environment metadata; keep the source directory locally excluded — agent-decided.

## Questions asked
① — what — 建議產生可公開的 sanitized raw evidence，保留 prompts、模型回答、評分與測試結果，移除本機與 session metadata，原始 79 份繼續留在本機；完成後再合併入 main。（答：好）

## Risks
1. Sanitization is intentionally lossy for executor-environment diagnostics; the private source remains available locally for that purpose.
