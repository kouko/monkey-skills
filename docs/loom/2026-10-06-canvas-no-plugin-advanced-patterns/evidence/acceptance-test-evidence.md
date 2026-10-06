# Canvas no-plugin advanced patterns — acceptance test evidence

Tried on 2026-10-06, in a clean copy of the project at `d699d7e5a` (git
worktree `git worktree add ... HEAD`, detached — nothing but the branch's own
commits present). All commands ran from that worktree root. The report that
this evidence backs is at
`docs/loom/2026-10-06-canvas-no-plugin-advanced-patterns/acceptance-test-report.md`.

Setup check (the project's own README instructions): this repo is a plugin
marketplace with no build step; its development entry point is the test runner
(`requirements-dev.txt`: pytest, pytest-xdist, pyyaml, markdown-it-py,
wcwidth). The skill loads as a plain directory under `obsidian/skills/` —
`SKILL.md` + single-level `assets/`, `references/`, `scripts/` subfolders,
which is the structure the repo's own skill-folder-structure gate requires and
which the change's two new files (one in `references/`, one in `assets/`) keep.
The bundled validator runs on any stock Python 3: `python3
<skill>/scripts/validate_canvas.py <canvas>` worked in the clean copy with no
install. The change installs and is usable.

Suite note: the full package suite is run by `finalize-review` (build hand-off:
`python3 -m pytest scripts/ -q` 698 passed; obsidian tests 31 passed), so this
run executed only the tests that cover each criterion, below.

## 1. The skill documents build guidance for each of the eight applications — nested canvas workspace, research dual-canvas, data-pipeline documentation, audit / incident post-mortem / onboarding map, teacher class canvas, worldbuilding basics, Bases-in-canvas, canvas-only / 2D-MOC — using only core Obsidian features; the Bases guidance marks the requirement as Obsidian 1.9+.

- How I tried it: read the new reference
  `obsidian/skills/obsidian-canvas-creator/references/no-plugin-patterns.md`
  in full (297 lines); grepped the whole change for community-plugin names and
  for Bases version markers; ran the adversarial probe
  `docs/loom/2026-10-06-canvas-no-plugin-advanced-patterns/evidence/probes/test_bases_version_note.py`.
- What came back:
  - All eight applications have their own section with build guidance:
    §1 Nested Canvas Workspace (Canvas-in-Canvas), §2 Research Dual-Canvas, §3
    Data-Pipeline Documentation Canvas, §4 Output-as-Deliverable Method
    Canvases (system audit / incident post-mortem / onboarding map), §5 Teacher
    Class Canvas, §6 Worldbuilding Basics, §7 Bases-in-Canvas, §8 Canvas-Only
    Vault / 2D MOC — plus §9 the drift anti-pattern.
  - Zero-plugin: the reference's only plugin mentions are "no community
    plugins" (`no-plugin-patterns.md:4`), "no plugin required"
    (`no-plugin-patterns.md:32`), "Zero-plugin rule … works in a stock
    Obsidian install" (`no-plugin-patterns.md:23`), and "Bases core plugin"
    (core, not community). Grep for `dataview|metadata menu|hover editor|
    kanban sync|advanced canvas|enhanced canvas|caret` over the reference,
    SKILL.md, and the six changed READMEs: no match. The only Excalidraw
    mentions in `obsidian/README*.md` describe the separate
    `obsidian-excalidraw-diagram` skill, pre-existing and unrelated.
  - Bases version: `no-plugin-patterns.md:25` "**requires Obsidian 1.9+
    (Bases core plugin)**"; `no-plugin-patterns.md:205` same marker in §7;
    `no-plugin-patterns.md:207` "shipped in Obsidian 1.9"; `:210` notes the
    direct-embed rendering floor of 1.9.5 and the note-embed workaround. No
    file carries the superseded "1.13" note.
  - Probe: `python3 -m pytest
    docs/loom/2026-10-06-canvas-no-plugin-advanced-patterns/evidence/probes/test_bases_version_note.py
    -q` → `12 passed in 0.12s` (10 docs × the 1.9+ marker, plus accept/reject
    behavior checks). Probe docstring read:
    "every doc that advertises Bases-in-canvas qualifies it" — the 1.9+
    requirement across all ten user-facing docs.
- Evidence: `references/no-plugin-patterns.md` sections 1–8; grep output
  above; probe run output above.

## 2. A usable `.canvas` template demonstrating Canvas-in-Canvas nesting exists and passes the bundled validator (obsidian/skills/obsidian-canvas-creator/scripts/validate_canvas.py).

- How I tried it: located the template at
  `obsidian/skills/obsidian-canvas-creator/assets/template-nested-workspace.canvas`,
  read it, and ran the bundled validator on it from the clean copy:
  `python3 obsidian/skills/obsidian-canvas-creator/scripts/validate_canvas.py
  obsidian/skills/obsidian-canvas-creator/assets/template-nested-workspace.canvas`.
- What came back: exit code 0, no output (validator prints violations only on
  failure). The template's structure: group node first, then a title text
  node, a navigation text node, a file node embedding the child canvas
  (`"file": "Child/child-canvas.canvas"` — the Canvas-in-Canvas node), a file
  node to a linked note with `"subpath": "#Overview"`, an in-file
  "Replace these paths" guidance node (canvas JSON has no comments), and one
  labeled edge `opens in its own tab`. 16-char lowercase-hex IDs
  (`a1b2c3d4e5f60001`…`a1b2c3d4e5f60009`) unique across nodes and edges.
- Also ran the validator's own suite: `python3 -m pytest
  obsidian/tests/test_validate_canvas.py -q` → `9 passed in 0.33s`. That
  module covers the validator's five checks (clean file exits 0, duplicate id,
  dangling edge, missing required field, overlaps); the template itself was
  validated directly above.
- Evidence: `EXIT=0` from the validator run; template file
  `assets/template-nested-workspace.canvas:50` (child-canvas file node) and
  `:81` (path-replacement guidance).

## 3. The skill documents the canvas-drift anti-pattern (do not use canvas as a continuously maintained live dashboard) and what to use instead.

- How I tried it: read §9 "When NOT to Use Canvas (Canvas Drift)" in
  `references/no-plugin-patterns.md` and the "Common Pitfalls to Avoid" list in
  SKILL.md.
- What came back: `no-plugin-patterns.md:270-297` names the anti-pattern
  ("canvas drift": a canvas kept as a continuously maintained live dashboard),
  records the observed failure mode (a live-dashboard canvas failed within
  about two weeks — cards drifted faster than they were updated),
  says "**Never use canvas as a live dashboard.**", and gives the
  replacement in plain words: "For live data use notes, queries, or Bases
  instead — Bases views and file-node embeds refresh, and a note's links and
  backlinks stay truthful" (`:284-285`), plus the two jobs canvas does well
  (spatial reasoning, finished artifacts). SKILL.md's pitfalls now end with
  "Canvas drift — keeping a canvas as a continuously maintained live dashboard
  (use notes, queries, or Bases instead; see `references/no-plugin-patterns.md`)"
  (`SKILL.md:305-306`).
- Evidence: `references/no-plugin-patterns.md:270-297`, `SKILL.md:305-306`.

## 4. SKILL.md routes to the new documentation; the existing six patterns' behavior is unchanged.

- How I tried it: diffed the whole change
  (`git diff 4228c056..HEAD`), listed every file under the skill directory at
  base vs head, and resolved every path SKILL.md points at.
- What came back:
  - Routing: SKILL.md gained a "No-Plugin Advanced Patterns" section routing
    to `references/no-plugin-patterns.md` and the nested-workspace template
    (`SKILL.md:55-65`), a Reference Documents line for the new file
    (`SKILL.md:278`), and the drift pitfall pointer (`SKILL.md:305-306`). All
    seven referenced paths resolve (checked with `[ -f ]`):
    `references/no-plugin-patterns.md`, `assets/template-nested-workspace.canvas`,
    `references/layout-patterns.md`, `references/canvas-spec.md`,
    `references/layout-algorithms.md`, `references/EXAMPLES.md`,
    `scripts/validate_canvas.py`. Inside the new reference, the three
    cross-references (`references/canvas-spec.md`, `references/layout-patterns.md`,
    `assets/template-nested-workspace.canvas`) also resolve.
  - Six patterns unchanged: `git diff 4228c056..HEAD` shows no edits to
    `references/layout-patterns.md`, `references/canvas-spec.md`,
    `references/layout-algorithms.md`, `references/EXAMPLES.md`,
    `scripts/validate_canvas.py`, or any of the six existing templates
    (mindmap-simple, freeform-grouped, kanban, dashboard, research-map,
    moodboard). File-list diff base→head under the skill dir: exactly two
    additions (the new template, the new reference), zero removals. The
    SKILL.md diff is purely additive (frontmatter description extended, one
    new pattern section, one new reference line, one new pitfall bullet) —
    the MindMap / freeform / four-community-patterns sections are byte-identical.
- Evidence: `git diff --stat 4228c056..HEAD` (17 files: 2 new skill files +
  SKILL.md + 9 README/CHANGELOG/manifest lines + loom docs); `git ls-tree`
  diff showing only the two added skill files; `[ -f ]` resolution of all
  routing targets.

## 5. Plugin README / attribution match the new capability; plugin version bumped per the repo's version-bump gate (3.23.0).

- How I tried it: diffed the README/CHANGELOG/manifest files, ran the repo's
  version-bump gate and the Codex manifest sync check against the real
  base..head range, and grepped for the version and the attribution line.
- What came back:
  - Version: `obsidian/.claude-plugin/plugin.json` and
    `obsidian/.codex-plugin/plugin.json` both 3.22.0 → 3.23.0; `obsidian/README.md`,
    `README.ja.md`, `README.zh-TW.md` "Version" lines and the repo-tree
    comment all updated to 3.23.0; `obsidian/CHANGELOG.md` gains a `[3.23.0] —
    2026-10-06` entry listing the new reference, template, and routing.
  - README matches capability: `obsidian/README.md` skill table row for
    `obsidian-canvas-creator` now lists "zero-plugin advanced patterns (nested
    canvas workspaces, research dual-canvas, data-pipeline documentation,
    audit / post-mortem / onboarding, teacher class, worldbuilding,
    Bases-in-canvas 1.9+, canvas-only / 2D MOC)"; the ja and zh-TW rows match;
    the per-skill READMEs (en/ja/zh-TW) each gained the same capability clause
    naming the nested-workspace template; `obsidian/skills/README.md`
    attribution table row updated ("this repo added layout patterns …, a
    `.canvas` output validator, and zero-plugin advanced patterns with a
    nested-workspace template (derivative)").
  - Attribution: MIT attribution retained in the skill table — Axton Liu +
    Steph Ango (json-canvas from kepano) — no attribution removed or edited,
    only the added-capability clause.
  - Gates: `python3 scripts/check_version_bump.py --base 4228c056 --head HEAD`
    → `check_version_bump: OK — every plugin with skill-content changes bumped
    its version.` (exit 0); `python3 scripts/sync_codex_manifests.py --check
    obsidian` → exit 0 (Claude and Codex manifests in sync).
- Evidence: gate outputs above; `plugin.json:3` in both manifests; README
  diff hunks; CHANGELOG `[3.23.0]` entry.

## Re-run

None — first run; no fix cycle.
