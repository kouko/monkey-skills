# Canvas skill layout templates + output validator — spec
intent: 2026-10-05-canvas-layout-templates-validator@5138f40a050cde6e04cf7be1993cad76cc62e017
pre-build-review: not-required — additive skill content and a stdlib-only validator; no security/privacy, irreversible data, public contract, or cross-system architecture surface

## Requirements
REQ-1 — Layout pattern documentation
  WHEN the skill covers the four new patterns, the skill shall document each pattern's node composition, grouping, connections, and color semantics → Acceptance #1
REQ-2 — Pattern-conforming output
  WHEN the skill is asked to produce any of the four new patterns, the generated `.canvas` structure shall conform to that pattern's rules → Acceptance #2
REQ-3 — Validator checks
  WHEN the validator runs on a `.canvas` file, it shall report JSON validity, 16-char lowercase-hex unique IDs, edge fromNode/toNode existence, per-type required fields, and node overlap; exit 0 on a clean file and non-zero naming each violation → Acceptance #3
REQ-4 — Validator tests
  WHEN the plugin pytest suite runs, the validator's checks shall be covered by automated tests → Acceptance #4
REQ-5 — Docs sync
  WHEN the change lands, the plugin README and skill attribution table shall match the new capability → Acceptance #5

## Design decision
- Carried detail (user agreed): skill 能產出看板／儀表板／研究地圖／moodboard 四種新版型 → document the four patterns in one new reference file `references/layout-patterns.md`, plus one `.canvas` template per pattern under `assets/`. Agent-decided: keeps SKILL.md scannable (progressive disclosure) and templates double as acceptance fixtures.
- Carried detail (user agreed): 產出的 .canvas 會被程式檢查（ID 唯一、edge 引用、重疊），配 pytest 可回歸 → one stdlib-only script `scripts/validate_canvas.py`, agent-invoked by the skill, exit 0 clean / non-zero listing each violation. Agent-decided: stdlib-only per constraint; standalone entry so the skill can run it at runtime.
- Overlap rule: actual AABB intersection (area > 0) between two non-group nodes is a violation; group nodes are containers and are excluded from overlap checks (children inside a group are expected). Spacing guidance (320/200px) stays advisory and is not machine-checked. Agent-decided.
- Script location `obsidian/skills/obsidian-canvas-creator/scripts/validate_canvas.py`; tests `obsidian/tests/test_validate_canvas.py`, covered by the plugin pytest suite (`testpaths = tests, scripts, skills`). Agent-decided.
- Templates live under `assets/`, not a `templates/` directory, to stay off the interface-surface glob `**/templates/**`. Agent-decided.
- Skill content stays English; attribution notes the repo's derivative merge (Axton Liu + kepano json-canvas). Constraint.

## Alternatives considered
- Prompt-only templates without a validator — declined: the user explicitly chose the combined option (machine validation).
- Validator as pytest-only fixture without a CLI entry — declined: the skill must invoke it at runtime.
- Node/TypeScript validator — declined: repo scripting is Python stdlib; no new runtime dependencies allowed.
- Four patterns written inline in SKILL.md — declined: reference file mirrors kepano progressive disclosure and keeps the skill readable.

## Current state evidence
- Forward: `obsidian/skills/obsidian-canvas-creator/SKILL.md` — "Core Workflow" and "Validation Checklist" show the two current patterns (MindMap/freeform) and a manual checklist with no machine check.
- Reverse: `obsidian/skills/obsidian-canvas-creator/references/layout-algorithms.md` — describes layout algorithms; nothing consumes machine validation today.
- Error: `obsidian/skills/obsidian-canvas-creator/SKILL.md` — "Common Pitfalls to Avoid" lists overlaps and duplicate IDs as pitfalls, detectable only after import into Obsidian.
- Data: `obsidian/skills/obsidian-canvas-creator/assets/template-mindmap-simple.canvas` — the `.canvas` JSON shapes the validator must parse.
- Boundary: `obsidian/skills/obsidian-canvas-creator/references/canvas-spec.md` — defines node types, colors, edges; the boundary the validator enforces.

## UI flows
N/A — engineering change; no user-facing interface surface. The validator is agent-invoked; its output is the exit code and violation list.
