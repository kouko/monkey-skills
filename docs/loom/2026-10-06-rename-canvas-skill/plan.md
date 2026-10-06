# Rename obsidian-canvas-creator to obsidian-canvas — plan
intent: 2026-10-06-rename-canvas-skill@2decdd8fa280010bb0114cd8e9a13d55b5bb5f8f
charter: 1.1

## Current State Evidence
- Forward: obsidian/skills/obsidian-canvas-creator/SKILL.md:2 — `name:` field is the skill identity.
- Reverse: obsidian/skills/using-obsidian/SKILL.md:39 — router lists the old skill name.
- Error: scripts/test_bases_version_note.py:37-41 — hard-coded skill dir paths.
- Data: obsidian/README.md:110 — plugin README skill table rows.
- Boundary: obsidian/CHANGELOG.md:7 — historical entries must keep the old name.

## Task DAG

**W1-01 rename skill dir and identity**  after: —  acceptance: 1, 4, 5
- Files: obsidian/skills/obsidian-canvas-creator (dir → obsidian-canvas), obsidian/skills/obsidian-canvas-creator/SKILL.md, obsidian/.claude-plugin/plugin.json, obsidian/.codex-plugin/plugin.json
- Test: A1 positive: dir-and-name-are-obsidian-canvas; boundary: templates-references-validator-unchanged. A4 positive: formerly-note-in-skill-description; boundary: plugin-json-description-unchanged. A5 positive: old-name-gone-from-obsidian-skills-tree; boundary: docs-loom-and-worktrees-untouched.
- Risk: pure rename; content byte-identical except SKILL.md name + description formerly-note; manifests bumped 3.23.0→3.24.0 with codex sync; agent-decided.

**W1-02 per-skill READMEs + router + cross-refs**  after: W1-01  acceptance: 2
- Files: obsidian/skills/obsidian-canvas-creator/README.md, obsidian/skills/obsidian-canvas-creator/README.ja.md, obsidian/skills/obsidian-canvas-creator/README.zh-TW.md, obsidian/skills/using-obsidian/SKILL.md, obsidian/skills/obsidian-research/SKILL.md
- Test: A2 positive: cross-refs-point-to-new-name; boundary: attribution-source-links-kept.
- Risk: router and research refs name the skill; keep axtonliu/kepano links; agent-decided.

**W2-01 plugin READMEs + ATTRIBUTION + CHANGELOG**  after: W1-01  acceptance: 2, 5
- Files: obsidian/README.md, obsidian/README.ja.md, obsidian/README.zh-TW.md, obsidian/skills/README.md, obsidian/skills/README.ja.md, obsidian/skills/README.zh-TW.md, ATTRIBUTION.md, obsidian/CHANGELOG.md
- Test: A2 positive: plugin-docs-use-new-name; negative: stale-name-absent-from-obsidian-and-ATTRIBUTION-excluding-docs-loom-docs-skill-dogfood-worktrees. A5 positive: docs-loom-and-worktrees-retain-old-name-unchanged; boundary: git-diff-shows-no-edits-there.
- Risk: repo version-bump gate requires 3.23.0→3.24.0 (bumped in W1-01) + codex manifest sync or CI fails; agent-decided.

**W2-02 test paths + gates**  after: W1-01  acceptance: 3
- Files: obsidian/tests/test_validate_canvas.py, scripts/test_bases_version_note.py
- Test: A3 positive: pytest-suite-passes; boundary: test-paths-resolve-new-dir. A3 boundary: sync-codex-manifests-check-exit-0; boundary: check-version-bump-clean.
- Risk: tests hard-code old dir; update paths, keep assertions; agent-decided.

## Simplicity check
- Single task doing dir rename + all docs — declined: mixes content identity, docs routing, and tests in one diff.
- Merge W2-01 into W1-02 — declined: splits plugin-root docs (READMEs/ATTRIBUTION/CHANGELOG) from per-skill docs.
- Merge W2-02 into W1-01 — declined: keeps test-path updates verifiable against the completed rename.

## Questions asked
- capture-intent ① — consequence — 以上複述（更名範圍、後果、授權）是你要的嗎？

## Risks
1. Version-bump gate: rename touches obsidian/skills/**; both plugin.json must go 3.23.0→3.24.0 and codex manifests sync or ship fails.
2. Old-name survivors outside docs/loom: docs/skill-dogfood/2026-06-17 report and .worktrees keep the name by design — historical records, not live refs.
3. External invokers of `obsidian:obsidian-canvas-creator` break; formerly-note in description is the one-release mitigation (user-decided consequence).
