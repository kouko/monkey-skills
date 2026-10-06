# Canvas no-plugin advanced patterns — spec
intent: 2026-10-06-canvas-no-plugin-advanced-patterns@4228c056542d8240826576b6149174c9314111d3
pre-build-review: not-required — content-only change (skill reference docs + one template + routing lines); no security/privacy, irreversible data, public contract, or cross-system surface

## Requirements
REQ-1 — No-plugin application guidance
  WHEN the skill covers the no-plugin advanced applications, it shall document each one (nested canvas workspace, research dual-canvas, data-pipeline documentation, audit / incident post-mortem / onboarding map, teacher class canvas, worldbuilding basics, Bases-in-canvas) using only core Obsidian features, with Bases marked as requiring Obsidian 1.13+ → Acceptance #1
REQ-2 — Nested canvas template
  WHEN nesting is documented, a `.canvas` template demonstrating Canvas-in-Canvas nesting shall exist and pass the bundled validator → Acceptance #2
REQ-3 — Drift anti-pattern
  WHEN the skill describes when to use canvas, it shall document the canvas-drift anti-pattern (do not use canvas as a continuously maintained live dashboard) and what to use instead → Acceptance #3
REQ-4 — Routing
  WHEN SKILL.md routes requests, it shall point to the new documentation, leaving the existing six patterns unchanged → Acceptance #4
REQ-5 — Docs and version sync
  WHEN the change lands, plugin README / attribution shall match the new capability and the plugin version shall be bumped per the repo's version-bump gate → Acceptance #5

## Design decision
- Carried detail (user agreed): 「不需要外掛的部分」= the eight built-in-only applications enumerated at decision point ① (nested canvas, research dual-canvas, data-pipeline documentation, audit / post-mortem / onboarding, teacher class canvas, worldbuilding basics, Bases-in-canvas, canvas-only / 2D-MOC caveats); moodboard and programmatic generation were already shipped by the previous change. → document in a new reference file `references/no-plugin-patterns.md`, keeping `layout-patterns.md` focused on the four visual patterns. Agent-decided: one file, so SKILL.md routes to exactly two pattern references.
- Nested template: `assets/template-nested-workspace.canvas` — a parent canvas whose file nodes reference a child `.canvas` and a note, demonstrating Canvas-in-Canvas nesting; must pass the validator (16-hex ids, required fields). Agent-decided.
- Bases-in-canvas: documented as embedding a `.base` file via a file node, marked "requires Obsidian 1.13+ (Bases core plugin)". Agent-decided.
- Drift anti-pattern: a dedicated section in `no-plugin-patterns.md` ("When NOT to use canvas") plus a pointer from SKILL.md. Agent-decided.
- Multi-canvas workflows (research dual-canvas, pipeline, audit / post-mortem / onboarding, teacher, worldbuilding) are documented as methodology with inline JSON examples, not one template each — templates only where a single-file structure is the mechanism (nesting). Agent-decided.
- Version bump 3.22.0 → 3.23.0 + `sync_codex_manifests.py obsidian` + CHANGELOG, per the repo's version-bump gate. Constraint.

## Alternatives considered
- Extend `layout-patterns.md` with the new sections — declined: it would mix visual layout patterns with multi-canvas methodology and push the file past scannable size.
- One template per new application — declined: methodology patterns span multiple canvases; a single-file template would misrepresent them.
- Document Bases integration without a version note — declined: Bases shipped in 1.13; the guidance must not silently break older Obsidian.

## Current state evidence
- Forward: `obsidian/skills/obsidian-canvas-creator/SKILL.md` — routing covers MindMap, freeform, and the four community patterns only; no multi-canvas or nesting guidance.
- Reverse: `obsidian/skills/obsidian-canvas-creator/references/layout-patterns.md` — four visual patterns; nothing about nesting, Bases, or multi-canvas workflows.
- Error: `SKILL.md` "Common Pitfalls to Avoid" — no "when not to use canvas" guidance; the research-recorded canvas-drift failure mode is undocumented.
- Data: `assets/template-freeform-grouped.canvas` — file-node shapes the nesting template builds on.
- Boundary: `references/canvas-spec.md` — `file` node type (with `subpath`) is the mechanism for embedding canvases and Bases.

## UI flows
N/A — engineering change; no user-facing interface surface.
