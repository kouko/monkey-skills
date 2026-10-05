# Canvas skill layout templates + output validator — plan
intent: 2026-10-05-canvas-layout-templates-validator@5138f40a050cde6e04cf7be1993cad76cc62e017
spec: docs/loom/2026-10-05-canvas-layout-templates-validator/spec.md@4f9dc6ad9a09e751a525ef87af5314e4b9a43682
charter: 1.1

## Task DAG

**W1-01 validator script + tests**  after: —  acceptance: 3, 4
- Files: obsidian/skills/obsidian-canvas-creator/scripts/validate_canvas.py, obsidian/tests/test_validate_canvas.py
- Test: A3 positive: valid-canvas-exits-0; negative: duplicate-id-named. A4 positive: suite-passes; boundary: group-overlap-excluded.
- Risk: stdlib-only per constraint; overlap is AABB intersection, group nodes excluded; agent-decided.

**W1-02 pattern docs + templates**  after: —  acceptance: 1
- Files: obsidian/skills/obsidian-canvas-creator/references/layout-patterns.md, obsidian/skills/obsidian-canvas-creator/assets/template-kanban.canvas, obsidian/skills/obsidian-canvas-creator/assets/template-dashboard.canvas, obsidian/skills/obsidian-canvas-creator/assets/template-research-map.canvas, obsidian/skills/obsidian-canvas-creator/assets/template-moodboard.canvas
- Test: A1 positive: four-patterns-documented; boundary: templates-match-documented-rules.
- Risk: templates stay under assets/, off the **/templates/** surface glob; agent-decided.

**W2-01 SKILL.md workflow + docs sync**  after: W1-01, W1-02  acceptance: 2, 5
- Files: obsidian/skills/obsidian-canvas-creator/SKILL.md, obsidian/README.md, obsidian/skills/README.md
- Test: A2 positive: pattern-request-routes-to-doc; boundary: mindmap-freeform-unchanged. A5 positive: capability-listed; negative: stale-version-absent.
- Risk: keeps the existing MindMap/freeform sections intact; README version aligned to plugin.json; agent-decided.

## Simplicity check
- Merge validator script with its tests into one task — taken
- Merge README/attribution sync into the SKILL.md task — taken

## Questions asked
- capture-intent ① — what — 先做哪個方向：版型擴充、驗證腳本、合併、還是上游同步？
- capture-intent ① — consequence — 確認重述內容並授權自動發布

## Risks
1. Divergence from upstream grows with every change; attribution must keep naming the derivative merge (Axton Liu + kepano json-canvas).
2. Acceptance 2 depends on the model following the skill; the validator can prove structure, not layout conformance.
3. Overlap tolerance choices (AABB, groups excluded) may differ from user expectations; documented in spec Design decision.
