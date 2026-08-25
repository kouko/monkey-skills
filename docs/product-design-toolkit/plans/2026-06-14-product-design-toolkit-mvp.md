> **⛔ SUPERSEDED 2026-06-14 (session 2).** Single-plugin plan split into two plugins (product-principles-toolkit
> + interface-design-toolkit). New plans live under `docs/product-principles-toolkit/plans/` and
> `docs/interface-design-toolkit/plans/`. Kept for the decision trail; do NOT execute this plan.

# Plan: product-design-toolkit MVP

**Source brief**: docs/product-design-toolkit/specs/2026-06-14-product-design-toolkit-mvp.md
**Total tasks**: 12
**Critical-path depth**: 3 (≤5 ✓) — longest chain: T8 → T9/T10/T11 (validator content checks) → T12 (SKILL.md)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-14, 14/14 — see Notes for 1 advisory: T6/T7 missed-parallel)

> **Scope split (per brief Decision):** this plan covers the **SDD-able infra** — the schema/reference docs, the plugin scaffold + manifests, and the `validate_design_output.py` validator (mirrors `spec-toolkit/scripts/validate_spec_output.py`). The **SKILL.md body is authored/iterated via `dev-workflow:skill-creator-advance`** (eval loop), tracked here as T12 with a grep-diagnostic acceptance so the brief item is covered, but its prose is NOT decomposed into TDD implementer tasks. See Notes.
>
> **New plugin dir:** `product-design-toolkit/` (sibling to `spec-toolkit/`, `code-toolkit/`). Output of the skill = a **design change-folder** (`PRINCIPLES.md` + `DESIGN.md` + `ui-flows.md`); the validator validates that folder.
>
> **Governance:** all examples synthetic; no company/customer/other-project names in any file (run an identifiable-token grep — company names, private-repo names, credentials, sibling-project names — before any commit; keep the actual token list out of repo-bound files); explicit `git add <paths>` only, never `-A`.

---

## Task 1 — Author DESIGN.md schema reference

- **Description**: Write `product-design-toolkit/skills/product-design/references/design-md-schema.md` — the 8 canonical DESIGN.md sections (Overview/Brand · Colors · Typography · Layout · Elevation & Depth · Shapes · Components · Do's & Don'ts) + the required YAML token front-matter keys per section. Fetch Google's open Apache-2.0 spec to lock the exact token keys; note the `npx @google/design.md` lint + WCAG-AA contrast rule.
- **Module**: `product-design-toolkit/skills/product-design/references/design-md-schema.md`
- **Files touched**: `product-design-toolkit/skills/product-design/references/design-md-schema.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/product-design-toolkit/specs/2026-06-14-product-design-toolkit-mvp.md`
- **Acceptance**:
  - **RED**: `grep -c '^## ' design-md-schema.md` returns <8 (the 8 sections absent) — diagnostic fails before authoring.
  - **GREEN**: file lists all 8 sections by name + per-section YAML token keys + cites the source spec + lint/contrast note.
- **External surfaces**:
  - HTTP API: Google DESIGN.md open spec (Apache-2.0) — grounding: WebFetch the official spec repo/site at build time (capture date); section list pre-verified this session (designmd.app/what-is-design-md, howaiworks.ai).
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "`DESIGN.md` — the visual *system* (adopt Google's open 8-section Apache-2.0 format)"

## Task 2 — Author ux-flow checklist reference

- **Description**: Write `product-design-toolkit/skills/product-design/references/ux-flow-checklist.md` — the 7 `ui-flows.md` dimensions: screen inventory (+ render-variant flags empty/loading/error/success), user flows (mermaid), UI structure (ascii), transitions (instant/guided/deliberate), entry points, exit points (kill dead-ends), information density, mobile flow. Frame each as a generation prompt (not a post-hoc capture question).
- **Module**: `product-design-toolkit/skills/product-design/references/ux-flow-checklist.md`
- **Files touched**: `product-design-toolkit/skills/product-design/references/ux-flow-checklist.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/product-design-toolkit/specs/2026-06-14-product-design-toolkit-mvp.md`
- **Acceptance**:
  - **RED**: `grep -ci 'screen inventory\|mobile flow\|entry point\|exit point' ux-flow-checklist.md` returns <4 — the dimensions absent.
  - **GREEN**: all 7 dimensions present, each phrased as a generation prompt; render-variant flag rule stated (flag-only, not full state machine — that's spec-expansion's job).
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "`ui-flows.md` — the UX *flow* … a 7-dimension UX-flow checklist"

## Task 3 — Author principles rules reference

- **Description**: Write `product-design-toolkit/skills/product-design/references/principles-rules.md` — the `PRINCIPLES.md` authoring contract: `## North Star` (product goal + success definition) + `## Principles` (3–7 non-negotiable rules, **each MUST carry a falsifiable check**; reject platitudes). Include the constitution/steering grounding (Spec Kit `constitution.md`, Kiro steering `product.md`) and 2–3 synthetic good/bad examples (✅ "primary task ≤3 steps" vs ❌ "be delightful").
- **Module**: `product-design-toolkit/skills/product-design/references/principles-rules.md`
- **Files touched**: `product-design-toolkit/skills/product-design/references/principles-rules.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/product-design-toolkit/specs/2026-06-14-product-design-toolkit-mvp.md`
- **Acceptance**:
  - **RED**: `grep -ci 'falsifiable\|north star\|check' principles-rules.md` returns <3 — the load-bearing rule absent.
  - **GREEN**: North Star + Principles format defined; per-principle falsifiable-check requirement stated; synthetic ✅/❌ examples present; constitution/steering prior art cited.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "`PRINCIPLES.md` — supreme … 3–7 non-negotiable rules, each carrying a falsifiable check"

## Task 4 — Author ascii UI-structure patterns reference

- **Description**: Write `product-design-toolkit/skills/product-design/references/ascii-ui-patterns.md` — conventions for ascii wireframe/layout blocks used in `ui-flows.md` (mermaid has no native wireframe, issue #1184). 3–4 synthetic skeleton patterns (top-nav page, sidebar page, list/detail, form). Point to `obsidian:obsidian-mermaid-visualizer` for the mermaid flow half (reference, don't re-author mermaid rules).
- **Module**: `product-design-toolkit/skills/product-design/references/ascii-ui-patterns.md`
- **Files touched**: `product-design-toolkit/skills/product-design/references/ascii-ui-patterns.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/obsidian/skills/obsidian-mermaid-visualizer/SKILL.md`
- **Acceptance**:
  - **RED**: `grep -c '```' ascii-ui-patterns.md` returns <3 — fewer than 3 ascii skeleton blocks present.
  - **GREEN**: ≥3 ascii layout skeletons + a pointer to the mermaid-visualizer skill for the flow half.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "UI structure (ascii layout blocks — mermaid has no native wireframe, issue #1184)"

## Task 5 — Plugin manifest scaffold

- **Description**: Write `product-design-toolkit/.claude-plugin/plugin.json` — name `product-design-toolkit`, version `0.1.0`, key-free description (≤1024 chars, Codex limit), author/homepage/repo/license/keywords. Mirror `spec-toolkit/.claude-plugin/plugin.json` shape.
- **Module**: `product-design-toolkit/.claude-plugin/plugin.json`
- **Files touched**: `product-design-toolkit/.claude-plugin/plugin.json`, `product-design-toolkit/scripts/test_plugin_manifest.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/.claude-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/test_plugin_manifest.py`
- **Acceptance**:
  - **RED**: `test_plugin_manifest.py::test_manifest_valid` fails (file/fields absent).
  - **GREEN**: manifest parses; required fields present; description ≤1024 chars; test passes.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "Build a new, separate `product-design-toolkit` plugin"

## Task 6 — Marketplace entry

- **Description**: Add a `product-design-toolkit` entry to the root `.claude-plugin/marketplace.json` (name/description/source), consistent with the plugin manifest. Add `test_marketplace_entry.py` asserting the entry exists and matches the manifest name + description.
- **Module**: `.claude-plugin/marketplace.json`
- **Files touched**: `.claude-plugin/marketplace.json`, `product-design-toolkit/scripts/test_marketplace_entry.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude-plugin/marketplace.json`
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/test_marketplace_entry.py`
  - `/Users/kouko/GitHub/monkey-skills/product-design-toolkit/.claude-plugin/plugin.json`
- **Acceptance**:
  - **RED**: `test_marketplace_entry.py::test_entry_matches_manifest` fails (entry absent).
  - **GREEN**: marketplace entry present + name/description match the manifest; test passes.
- **Dependencies**: Task 5 completes first
- **Independent**: false  # semantic dependency — entry mirrors the manifest's name/description
- **Brief item covered**: "a `marketplace.json` entry (`name`/`description`/`source`)"

## Task 7 — README

- **Description**: Write `product-design-toolkit/README.md` — what the plugin does (Station 0 design front-end), the 3-file change-folder output, the `ui-flows.md → spec-expansion` seam, key-free/portable note. Mirror `spec-toolkit/README.md` tone.
- **Module**: `product-design-toolkit/README.md`
- **Files touched**: `product-design-toolkit/README.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/README.md`
  - `/Users/kouko/GitHub/monkey-skills/docs/product-design-toolkit/specs/2026-06-14-product-design-toolkit-mvp.md`
- **Acceptance**:
  - **RED**: `test -f product-design-toolkit/README.md` fails.
  - **GREEN**: README documents the 3-file output + seam-1 + key-free posture.
- **Dependencies**: Task 5 completes first
- **Independent**: false  # describes the manifest's plugin; mirrors manifest metadata
- **Brief item covered**: "a new plugin = `.claude-plugin/plugin.json` + `skills/` + `scripts/` + `README.md`"

## Task 8 — Validator scaffold + change-folder structure check

- **Description**: Write `product-design-toolkit/scripts/validate_design_output.py` skeleton (check-runner pattern from `validate_spec_output.py`: each check = `(root: Path) -> list[str]`; CLI `python validate_design_output.py <dir>` → exit 0/1) + the first check: the change-folder contains `PRINCIPLES.md`, `DESIGN.md`, `ui-flows.md`. Add `test_validate_design_output.py` with a fixture dir.
- **Module**: `product-design-toolkit/scripts/validate_design_output.py`
- **Files touched**: `product-design-toolkit/scripts/validate_design_output.py`, `product-design-toolkit/scripts/test_validate_design_output.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/validate_spec_output.py`
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/scripts/test_validate_spec_output.py`
- **Acceptance**:
  - **RED**: `test_validate_design_output.py::test_missing_file_flagged` fails (no validator yet).
  - **GREEN**: validator flags a folder missing any of the 3 files; passes a complete fixture; CLI exit codes correct.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "a `validate_*` script … validates the whole change-folder (PRINCIPLES + DESIGN + ui-flows present and well-formed)"

## Task 9 — Validator: DESIGN.md 8-section check

- **Description**: Add a check to `validate_design_output.py`: `DESIGN.md` contains the 8 canonical sections (per `references/design-md-schema.md`). Add the test case.
- **Module**: `product-design-toolkit/scripts/validate_design_output.py`
- **Files touched**: `product-design-toolkit/scripts/validate_design_output.py`, `product-design-toolkit/scripts/test_validate_design_output.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/product-design-toolkit/skills/product-design/references/design-md-schema.md`
- **Acceptance**:
  - **RED**: `test_validate_design_output.py::test_design_missing_section_flagged` fails.
  - **GREEN**: validator flags a `DESIGN.md` missing any of the 8 sections; complete fixture passes.
- **Dependencies**: Tasks 8, 1 complete first
- **Independent**: false  # shares validate_design_output.py with Tasks 8/10/11
- **Brief item covered**: "`DESIGN.md` (visual system) … Google 8-section shape"

## Task 10 — Validator: PRINCIPLES.md falsifiable-check rule

- **Description**: Add a check: `PRINCIPLES.md` has `## North Star` + `## Principles`, and every principle bullet carries a falsifiable check marker (per `references/principles-rules.md`). Add the test case.
- **Module**: `product-design-toolkit/scripts/validate_design_output.py`
- **Files touched**: `product-design-toolkit/scripts/validate_design_output.py`, `product-design-toolkit/scripts/test_validate_design_output.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/product-design-toolkit/skills/product-design/references/principles-rules.md`
- **Acceptance**:
  - **RED**: `test_validate_design_output.py::test_principle_without_check_flagged` fails.
  - **GREEN**: validator flags a principle with no falsifiable check + flags a missing North Star/Principles section; complete fixture passes.
- **Dependencies**: Tasks 8, 3 complete first
- **Independent**: false  # shares validate_design_output.py
- **Brief item covered**: "each principle carrying a falsifiable check … enforced by the per-principle check rule"

## Task 11 — Validator: ui-flows.md required-sections check

- **Description**: Add a check: `ui-flows.md` contains the required sections (screen inventory + user flows + UI structure at minimum, per `references/ux-flow-checklist.md`). Add the test case.
- **Module**: `product-design-toolkit/scripts/validate_design_output.py`
- **Files touched**: `product-design-toolkit/scripts/validate_design_output.py`, `product-design-toolkit/scripts/test_validate_design_output.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/product-design-toolkit/skills/product-design/references/ux-flow-checklist.md`
- **Acceptance**:
  - **RED**: `test_validate_design_output.py::test_uiflows_missing_section_flagged` fails.
  - **GREEN**: validator flags a `ui-flows.md` missing a required section; complete fixture passes; full suite green at package level.
- **Dependencies**: Tasks 8, 2 complete first
- **Independent**: false  # shares validate_design_output.py
- **Brief item covered**: "`ui-flows.md` (UX flow) … sections from a 7-dimension UX-flow checklist"

## Task 12 — Author product-design SKILL.md (via skill-creator-advance)

- **Description**: Author `product-design-toolkit/skills/product-design/SKILL.md` — the one skill: sparse idea → **principles-first** → emit the 3-file change-folder. Body procedure: ① elicit + write `PRINCIPLES.md` (North Star + falsifiable principles, per `references/principles-rules.md`) ② derive `DESIGN.md` (8 sections, per `references/design-md-schema.md`) ③ derive `ui-flows.md` (7 dims + ascii/mermaid, per `references/ux-flow-checklist.md` + `references/ascii-ui-patterns.md`) ④ run `scripts/validate_design_output.py`. Flat-skill; references by relative path. **Iterated via `dev-workflow:skill-creator-advance` eval loop** (not a bare TDD task).
- **Module**: `product-design-toolkit/skills/product-design/SKILL.md`
- **Files touched**: `product-design-toolkit/skills/product-design/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/spec-toolkit/skills/spec-expansion/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/product-design-toolkit/skills/product-design/references/` (all 4 refs from T1–T4)
- **Acceptance**:
  - **RED**: grep diagnostic — SKILL.md absent, OR description >1024 chars, OR body doesn't reference all 4 `references/*.md` + `scripts/validate_design_output.py`, OR not flat-skill.
  - **GREEN**: SKILL.md present; description ≤1024; declares the 3-file change-folder output contract; references the 4 ref docs + validator by relative path; flat-skill; passes the skill-creator-advance activation harness.
- **Dependencies**: Tasks 1, 2, 3, 4 complete first; Tasks 9, 10, 11 complete first (validator contract referenced)
- **Independent**: false  # consumes all reference docs + the validator
- **Brief item covered**: "MVP = one skill that turns a sparse idea, principles-first, into a design change-folder"

## Notes

- **Parallel leaves (level 1, disjoint files):** Tasks 1, 2, 3, 4, 5, 8 are all `Independent: true` with disjoint `Files touched` → may dispatch concurrently via `dispatching-parallel-agents`. They count as ONE dependency level.
- **Validator content checks (T9/T10/T11)** share `validate_design_output.py` → NOT parallel among themselves (sequential, SDD floor), but each depends only on T8 (+ its reference doc), so they sit at one depth level. Critical-path depth = T8 → T9 → T12 = 3.
- **T12 (SKILL.md) is the `skill-creator-advance` track**, not a TDD implementer task. It is listed so the brief's central "one skill" item is covered and its dependency edges are explicit. When executing, route T12 through `dev-workflow:skill-creator-advance` (description-optimization + activation eval), NOT a bare implementer. Its RED is a grep/activation diagnostic, consistent with markdown-artifact tasks in this repo.
- **Out of this plan (per brief Out of Scope):** Codex `.codex-plugin/` full compat (only the ≤1024 description constraint applies here), Stitch/Figma MCP, downstream principles-conformance lens (P2 seam), automated DESIGN→spec hand-off.
- **Governance:** synthetic examples only; identifiable-token grep before any commit; explicit `git add <paths>`.
