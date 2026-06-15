# Plan: interface-design-toolkit MVP

**Source brief**: docs/interface-design-toolkit/specs/2026-06-14-interface-design-toolkit-mvp.md
**Total tasks**: 12
**Critical-path depth**: 3 (≤5 ✓) — e.g. T8 → T9 → T11
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-14, 14/14 — 1 advisory: T5/T6 missed-parallel)

> **Scope:** SDD-able infra (3 reference docs, plugin scaffold + manifests + router, validator). The two generate
> SKILL.md bodies (`design-system` T11, `interaction-flows` T12) are authored via `dev-workflow:skill-creator-advance`
> (grep/activation RED), not bare TDD. **MVP implements GUI fully; skills written modality-aware so TUI/CLI are
> additive phase-2.** New plugin dir: `interface-design-toolkit/`. Governance: synthetic examples; identifiable-token
> grep before commit; explicit `git add <paths>`.

---

## Task 1 — Author DESIGN.md schema reference (GUI design-system)

- **Description**: Write `interface-design-toolkit/skills/design-system/references/design-md-schema.md` — Google's 8 canonical sections (Overview/Brand · Colors · Typography · Layout · Elevation & Depth · Shapes · Components · Do's & Don'ts) + required YAML token keys per section; note `npx @google/design.md` lint + WCAG-AA. Fetch the authoritative spec to lock token keys.
- **Module**: `interface-design-toolkit/skills/design-system/references/design-md-schema.md`
- **Files touched**: `interface-design-toolkit/skills/design-system/references/design-md-schema.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/interface-design-toolkit/specs/2026-06-14-interface-design-toolkit-mvp.md`
- **Acceptance**:
  - **RED**: `grep -c '^## ' design-md-schema.md` returns <8.
  - **GREEN**: all 8 sections + per-section token keys + source cite + lint/contrast note.
- **External surfaces**:
  - HTTP API: Google DESIGN.md open spec (Apache-2.0) — grounding: WebFetch official spec at build time (capture date); 8 sections pre-verified this session.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "GUI → DESIGN.md in Google's open … 8-section format"

## Task 2 — Author ux-flow checklist reference (modality-aware)

- **Description**: Write `interface-design-toolkit/skills/interaction-flows/references/ux-flow-checklist.md` — the 7 `ui-flows.md` dimensions (screen/panel/command inventory + render-variant flags; user flows mermaid; UI structure ascii; transitions; entry/exit; density; mobile flow), each as a generation prompt, with a note on how each renders per modality (GUI screens / TUI panels+keys / CLI commands+output). Render-variant flag rule (flag-only; full state machine is spec-expansion's).
- **Module**: `interface-design-toolkit/skills/interaction-flows/references/ux-flow-checklist.md`
- **Files touched**: `interface-design-toolkit/skills/interaction-flows/references/ux-flow-checklist.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/interface-design-toolkit/specs/2026-06-14-interface-design-toolkit-mvp.md`
- **Acceptance**:
  - **RED**: `grep -ci 'screen.*inventory\|mobile flow\|entry point\|modality' ux-flow-checklist.md` returns <4.
  - **GREEN**: 7 dimensions present as generation prompts; per-modality rendering noted; render-variant flag rule stated.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "`interaction-flows` (modality-aware) → `ui-flows.md` … a 7-dimension UX-flow checklist"

## Task 3 — Author ascii UI-structure patterns reference

- **Description**: Write `interface-design-toolkit/skills/interaction-flows/references/ascii-ui-patterns.md` — ascii wireframe/layout conventions for `ui-flows.md` (mermaid has no native wireframe, #1184). ≥3 synthetic skeletons (top-nav page, sidebar page, list/detail; optionally a TUI panel). Pointer to `obsidian:obsidian-mermaid-visualizer` for the mermaid flow half.
- **Module**: `interface-design-toolkit/skills/interaction-flows/references/ascii-ui-patterns.md`
- **Files touched**: `interface-design-toolkit/skills/interaction-flows/references/ascii-ui-patterns.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/obsidian/skills/obsidian-mermaid-visualizer/SKILL.md`
- **Acceptance**:
  - **RED**: `grep -c '```' ascii-ui-patterns.md` returns <3.
  - **GREEN**: ≥3 ascii skeletons + pointer to the mermaid-visualizer skill.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "UI structure as ascii layout blocks (mermaid has no native wireframe — issue #1184)"

## Task 4 — Plugin manifest scaffold

- **Description**: Write `interface-design-toolkit/.claude-plugin/plugin.json` — name `interface-design-toolkit`, version `0.1.0`, key-free description ≤1024 chars, standard fields. Mirror `spec-toolkit`. Add `test_plugin_manifest.py`.
- **Module**: `interface-design-toolkit/.claude-plugin/plugin.json`
- **Files touched**: `interface-design-toolkit/.claude-plugin/plugin.json`, `interface-design-toolkit/scripts/test_plugin_manifest.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/.claude-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/test_plugin_manifest.py`
- **Acceptance**:
  - **RED**: `test_plugin_manifest.py::test_manifest_valid` fails.
  - **GREEN**: manifest parses; fields present; description ≤1024; test passes.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "Build a new, separate `interface-design-toolkit` plugin"

## Task 5 — Marketplace entry

- **Description**: Add an `interface-design-toolkit` entry to root `.claude-plugin/marketplace.json` consistent with the manifest. Add `test_marketplace_entry.py`.
- **Module**: `.claude-plugin/marketplace.json`
- **Files touched**: `.claude-plugin/marketplace.json`, `interface-design-toolkit/scripts/test_marketplace_entry.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude-plugin/marketplace.json`
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/test_marketplace_entry.py`
  - `/Users/kouko/GitHub/monkey-skills/interface-design-toolkit/.claude-plugin/plugin.json`
- **Acceptance**:
  - **RED**: `test_marketplace_entry.py::test_entry_matches_manifest` fails.
  - **GREEN**: entry present + matches manifest; test passes.
- **Dependencies**: Task 4 completes first
- **Independent**: false  # mirrors the manifest authored in Task 4
- **Brief item covered**: "root `marketplace.json` entry"

## Task 6 — README

- **Description**: Write `interface-design-toolkit/README.md` — cross-modal interface design station; the design change-folder output (design-system doc + `ui-flows.md`); seam-1 (`ui-flows.md` → spec-expansion); governed by `PRINCIPLES.md`; GUI-first/modality-aware; key-free. Mirror `spec-toolkit/README.md`.
- **Module**: `interface-design-toolkit/README.md`
- **Files touched**: `interface-design-toolkit/README.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/README.md`
  - `/Users/kouko/GitHub/monkey-skills/docs/interface-design-toolkit/specs/2026-06-14-interface-design-toolkit-mvp.md`
- **Acceptance**:
  - **RED**: `test -f interface-design-toolkit/README.md` fails.
  - **GREEN**: README documents the change-folder output + seam-1 + PRINCIPLES governance + modality posture.
- **Dependencies**: Task 4 completes first
- **Independent**: false  # describes the manifest's plugin
- **Brief item covered**: "a new plugin = `.claude-plugin/plugin.json` + `skills/` + `scripts/` + `README.md`"

## Task 7 — Router skill

- **Description**: Write `interface-design-toolkit/skills/using-interface-design-toolkit/SKILL.md` — router that records the product modality (GUI/TUI/CLI) and routes to `design-system` + `interaction-flows`; notes it reads `PRINCIPLES.md` as governing context. Mirror an existing `using-*` router shape.
- **Module**: `interface-design-toolkit/skills/using-interface-design-toolkit/SKILL.md`
- **Files touched**: `interface-design-toolkit/skills/using-interface-design-toolkit/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/using-code-toolkit/SKILL.md`
- **Acceptance**:
  - **RED**: grep diagnostic — router absent OR doesn't name both skills + the modality step + PRINCIPLES governance.
  - **GREEN**: router present; names `design-system` + `interaction-flows`; modality recording step; references PRINCIPLES.md; description ≤1024.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "`using-interface-design-toolkit` (router) — routes to the two skills + records the modality"

## Task 8 — Validator scaffold + change-folder structure check

- **Description**: Write `interface-design-toolkit/scripts/validate_design_output.py` skeleton (check-runner pattern from `validate_spec_output.py`; CLI `python validate_design_output.py <dir>` → exit 0/1) + first check: the change-folder contains the design-system doc (`DESIGN.md` for GUI) + `ui-flows.md`. Add `test_validate_design_output.py` with a GUI fixture.
- **Module**: `interface-design-toolkit/scripts/validate_design_output.py`
- **Files touched**: `interface-design-toolkit/scripts/validate_design_output.py`, `interface-design-toolkit/scripts/test_validate_design_output.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/validate_spec_output.py`
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/test_validate_spec_output.py`
- **Acceptance**:
  - **RED**: `test_validate_design_output.py::test_missing_file_flagged` fails.
  - **GREEN**: validator flags a folder missing DESIGN.md or ui-flows.md; complete GUI fixture passes; CLI exit codes correct.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "A `validate_*` script … validates the emitted change-folder"

## Task 9 — Validator: DESIGN.md 8-section check

- **Description**: Add a check to `validate_design_output.py`: `DESIGN.md` contains the 8 canonical sections (per `design-system/references/design-md-schema.md`). Add the test case.
- **Module**: `interface-design-toolkit/scripts/validate_design_output.py`
- **Files touched**: `interface-design-toolkit/scripts/validate_design_output.py`, `interface-design-toolkit/scripts/test_validate_design_output.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/interface-design-toolkit/skills/design-system/references/design-md-schema.md`
- **Acceptance**:
  - **RED**: `test_validate_design_output.py::test_design_missing_section_flagged` fails.
  - **GREEN**: validator flags a DESIGN.md missing any of the 8 sections; complete fixture passes.
- **Dependencies**: Tasks 8, 1 complete first
- **Independent**: false  # shares validate_design_output.py with Tasks 8/10
- **Brief item covered**: "GUI → DESIGN.md in Google's open … 8-section format"

## Task 10 — Validator: ui-flows.md required-sections check

- **Description**: Add a check: `ui-flows.md` contains the required sections (inventory + user flows + UI structure at minimum, per `interaction-flows/references/ux-flow-checklist.md`). Add the test case.
- **Module**: `interface-design-toolkit/scripts/validate_design_output.py`
- **Files touched**: `interface-design-toolkit/scripts/validate_design_output.py`, `interface-design-toolkit/scripts/test_validate_design_output.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/interface-design-toolkit/skills/interaction-flows/references/ux-flow-checklist.md`
- **Acceptance**:
  - **RED**: `test_validate_design_output.py::test_uiflows_missing_section_flagged` fails.
  - **GREEN**: validator flags a ui-flows.md missing a required section; complete fixture passes; full suite green at package level.
- **Dependencies**: Tasks 8, 2 complete first
- **Independent**: false  # shares validate_design_output.py
- **Brief item covered**: "`interaction-flows` (modality-aware) → `ui-flows.md`"

## Task 11 — Author design-system SKILL.md (via skill-creator-advance)

- **Description**: Author `interface-design-toolkit/skills/design-system/SKILL.md` — modality-aware: GUI → emit `DESIGN.md` (8 sections per `references/design-md-schema.md`); TUI/CLI → emit a conventions stub + phase-2 note. Reads `PRINCIPLES.md` as governing constraint. Runs `scripts/validate_design_output.py`. Flat-skill; relative-path refs. Iterated via `dev-workflow:skill-creator-advance`.
- **Module**: `interface-design-toolkit/skills/design-system/SKILL.md`
- **Files touched**: `interface-design-toolkit/skills/design-system/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/interface-design-toolkit/skills/design-system/references/design-md-schema.md`
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/skills/spec-expansion/SKILL.md`
- **Acceptance**:
  - **RED**: grep diagnostic — SKILL.md absent, OR description >1024, OR body doesn't reference `references/design-md-schema.md` + `scripts/validate_design_output.py` + PRINCIPLES governance, OR not flat-skill.
  - **GREEN**: SKILL.md present; description ≤1024; GUI emits DESIGN.md + TUI/CLI stub noted; references schema + validator + PRINCIPLES; flat-skill; passes activation harness.
- **Dependencies**: Tasks 1, 9 complete first
- **Independent**: false  # consumes the schema ref + validator contract
- **Brief item covered**: "`design-system` (modality-aware) → the design-system artifact"

## Task 12 — Author interaction-flows SKILL.md (via skill-creator-advance)

- **Description**: Author `interface-design-toolkit/skills/interaction-flows/SKILL.md` — modality-aware: emit `ui-flows.md` (7 dims per `references/ux-flow-checklist.md`; ascii per `references/ascii-ui-patterns.md`; mermaid via obsidian skill). Reads `PRINCIPLES.md`. `ui-flows.md` seeds spec-expansion. Runs the validator. Flat-skill; relative-path refs. Iterated via `dev-workflow:skill-creator-advance`.
- **Module**: `interface-design-toolkit/skills/interaction-flows/SKILL.md`
- **Files touched**: `interface-design-toolkit/skills/interaction-flows/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/interface-design-toolkit/skills/interaction-flows/references/ux-flow-checklist.md`
  - `/Users/kouko/GitHub/monkey-skills/interface-design-toolkit/skills/interaction-flows/references/ascii-ui-patterns.md`
- **Acceptance**:
  - **RED**: grep diagnostic — SKILL.md absent, OR description >1024, OR body doesn't reference both `references/*.md` + `scripts/validate_design_output.py` + the spec-expansion seam, OR not flat-skill.
  - **GREEN**: SKILL.md present; description ≤1024; emits ui-flows.md (7 dims); references the 2 ref docs + validator + names the spec-expansion seam + PRINCIPLES; flat-skill; passes activation harness.
- **Dependencies**: Tasks 2, 3, 10 complete first
- **Independent**: false  # consumes both reference docs + validator contract
- **Brief item covered**: "`interaction-flows` (modality-aware) → `ui-flows.md`"

## Notes

- **Parallel leaves (level 1, disjoint files):** Tasks 1, 2, 3, 4, 7, 8 are `Independent: true` with disjoint `Files touched` → may dispatch concurrently. Count as ONE dependency level.
- **Validator content checks (T9, T10)** share `validate_design_output.py` → NOT parallel among themselves (sequential, SDD floor); each depends only on T8 + its reference doc, so they sit at one depth level. Critical-path depth = T8 → T9 → T11 = 3.
- **T11/T12 (SKILL.md bodies) route to `dev-workflow:skill-creator-advance`**, not bare implementers; RED is grep/activation diagnostic.
- **Out of this plan (per brief Out of Scope):** `design-critic` skill (P2), full TUI/CLI modality (phase-2; T11 emits a stub), Stitch/Figma MCP, design-team sync, automated DESIGN→spec seam.
