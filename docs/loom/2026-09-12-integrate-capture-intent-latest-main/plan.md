# Integrate capture-intent boundaries onto current main — plan
intent: 2026-09-12-integrate-capture-intent-latest-main@cd3fcbbb9
charter: 1.0

## Current State Evidence
- Forward: `loom-design/skills/capture-intent/SKILL.md` owns the full intake path and confirmation boundary.
- Reverse: `loom-code/skills/write-plan/SKILL.md` mirrors intake when loom-design is unavailable.
- Error: `git merge-tree HEAD origin/main` reports conflicts in plugin versions, changelog, manifest, and shared contract tests.
- Data: `origin/main` at `6c3d740e9` contains the reviewer malformed-response retry shipped in loom-code 2.2.1.
- Boundary: the prior intent forbids new fields, IDs, checker rules, stations, subagents, and review loops.

## Task DAG

### Wave 0 — Integrate the current baseline

**W0-01 Merge current main without changing capture semantics**  after: none  acceptance: 1,2
- Files: loom-code manifests, loom-code/CHANGELOG.md, loom-code/contract/manifest.yaml, loom-code/scripts/test_simplified_station_text.py, capture-intent branch content
- Test: A1 positive: both-published-semantics; boundary: no-capture-regression. A2 positive: mechanism-count-stable; negative: no-new-schema-or-review-node.
- Risk: agent-decided — merge rather than rewrite reviewed commits; resolve only overlapping released text and retain the higher upstream versions.

### Wave 1 — Re-establish evidence on the integrated tree

**W1-01 Verify and attest the integrated functional tree**  after: W0-01  acceptance: 3
- Files: related Loom test suites, docs/loom/2026-09-12-integrate-capture-intent-latest-main/attestation.json
- Test: A3 positive: package-and-adversarial-pass; boundary: attestation-matches-final-content-digest.
- Risk: agent-decided — start one new bounded Review episode under this confirmed intent; do not reuse pre-integration evidence.

## Questions asked
① — what — 建立一份只授權整合最新 main、保持 capture-intent 行為不變並重新取得 closing evidence 的延續 intent，再自動建立 Ready PR；merge 另行決定。是否繼續？（答：那就繼續吧）

## Risks
1. Conflict resolution could silently restore older plugin versions or discard the newly shipped malformed-response retry.
2. Upstream and branch tests touch the same assertions; passing fragments must not substitute for the repository package suite.
