# Canvas no-plugin advanced patterns — plan
intent: 2026-10-06-canvas-no-plugin-advanced-patterns@4228c056542d8240826576b6149174c9314111d3
spec: docs/loom/2026-10-06-canvas-no-plugin-advanced-patterns/spec.md@67140b6c66042674d9fe091ebf35f2ce4364f856
charter: 1.1

## Task DAG

**W1-01 no-plugin patterns reference**  after: —  acceptance: 1, 3
- Files: obsidian/skills/obsidian-canvas-creator/references/no-plugin-patterns.md
- Test: A1 positive: eight-applications-documented; boundary: bases-1-9-note. A3 positive: drift-section-present; boundary: names-live-dashboard.
- Risk: must stay zero-plugin; a community-plugin technique would violate the intent constraint; agent-decided.

**W1-02 nested workspace template**  after: —  acceptance: 2
- Files: obsidian/skills/obsidian-canvas-creator/assets/template-nested-workspace.canvas
- Test: A2 positive: template-validates-exit-0; boundary: contains-nested-file-node.
- Risk: file node references a child path; validator checks structure not file existence; agent-decided.

**W2-01 SKILL.md routing + docs sync**  after: W1-01, W1-02  acceptance: 4, 5
- Files: obsidian/skills/obsidian-canvas-creator/SKILL.md, obsidian/README.md, obsidian/README.ja.md, obsidian/README.zh-TW.md, obsidian/skills/README.md, obsidian/CHANGELOG.md, obsidian/.claude-plugin/plugin.json, obsidian/.codex-plugin/plugin.json
- Test: A4 positive: skill-routes-to-reference; boundary: existing-six-unchanged. A5 positive: readme-3-23-0; negative: stale-version-absent.
- Risk: repo version-bump gate requires 3.22.0→3.23.0 + codex manifest sync or CI fails; existing sections unchanged; agent-decided.

**W2-02 per-skill READMEs**  after: W1-01, W1-02  acceptance: 5
- Files: obsidian/skills/obsidian-canvas-creator/README.md, obsidian/skills/obsidian-canvas-creator/README.ja.md, obsidian/skills/obsidian-canvas-creator/README.zh-TW.md
- Test: A5 positive: skill-readme-lists-no-plugin; boundary: attribution-retained.
- Risk: per-skill READMEs describe capabilities and were left stale by W2-01 (outside its file list); a one-line capability clause per file closes A5; agent-decided.

**W2-03 graduate Bases probe into standing suite**  after: W1-01, W1-02, W2-01  acceptance: 5
- Files: scripts/test_bases_version_note.py
- Test: A5 positive: probe-runs-in-scripts-suite; boundary: probe-paths-adapted.
- Risk: the Bases probe went RED on this change, so review.probe-graduation requires a copy carried into the suite that runs on every later change (pytest scripts/) before finalize-review; REPO_ROOT/parents and DOCS paths must be adapted for scripts/; agent-decided.

## Simplicity check
- Merge W1-02 (nested template) into W1-01 — declined: merges two test mechanisms (prose assertions vs validator run); removes no file, test, or mechanism
- Fold W1-02 into W2-01 — declined: W2-01 already spans 8 files; the two-wave DAG is the minimum for the genuine routing dependency
- Split no-plugin-patterns.md into per-application references — declined: one file keeps SKILL.md routing to exactly two pattern references (spec decision)

## Questions asked
- capture-intent ① — what — 你要的是把零外掛的較複雜 canvas 應用（上列 8 項）補進 skill，對嗎？
- capture-intent ① — consequence — 確認重述並授權自動發布

## Risks
1. Zero-plugin constraint must hold everywhere in the new reference; one community-plugin technique breaks the intent's constraint.
2. The repo version-bump gate: skill-content change requires the 3.23.0 bump and codex manifest sync, else CI fails at ship.
3. Bases guidance is version-bound (1.9+; the research report's "1.13" was corrected during build — Bases shipped in Obsidian 1.9; the Codex independent review further corrected that direct .base embeds work from 1.9 with 1.9.5 only fixing refresh edge cases); without the note it would silently mislead older-Obsidian users.
