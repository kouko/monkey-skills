# Plan: spec-expansion v0.2.1 — dogfood hardening (F-1 + F-3)

Source brief: docs/spec-toolkit/specs/2026-06-12-spec-expansion-v0.2.1-dogfood-hardening.md
Total tasks: 3
Critical-path depth: 3 (≤5) — T1 → T2 → T3, all touch spec-expansion/SKILL.md (sequential floor)
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-06-12, inline self-review) — 3-task linear prose plan; checks: each ≤5 min ✓, ≤1 module ✓ (all SKILL.md), each has a RED grep-test/diagnostic ✓, both brief items (F-1, F-3) + version covered ✓, no orphans ✓, DAG acyclic (linear) ✓, depth 3 ≤5 ✓. Whole-branch review is the end gate.

## Task 1 — F-1: mandate pairwise-tool use on wide stages
- Description: In `spec-expansion/SKILL.md` Phase ③b "Wide stages (≥4 co-active objects)" paragraph, strengthen the soft "instead call the generator" wording to an imperative: the executor **MUST run `scripts/pairwise.py` and show the invocation**, and **MUST NOT enumerate a ≥4-object stage's combinations inline** (inline enumeration on wide stages is the A/B-validated leak). Keep the ≤3-object in-prompt path unchanged.
- Module: spec-toolkit/skills/spec-expansion/SKILL.md
- Files touched: spec-toolkit/skills/spec-expansion/SKILL.md, spec-toolkit/scripts/test_spec_expansion_skill.py
- Context paths:
  - spec-toolkit/skills/spec-expansion/SKILL.md  (Phase ③b wide-stage para, ~L197-205)
  - docs/spec-toolkit/dogfood/2026-06-12-pip-note-app/proposal.md  (F-1 evidence)
- Acceptance:
  - RED: `test_spec_expansion_skill.py::test_l2_wide_stage_mandates_pairwise_tool` — assert the SKILL.md wide-stage text contains an imperative tool-use cue (`MUST run` near `pairwise.py`) AND a ban on inline enumeration for wide stages (e.g. `do not enumerate` / `not inline`).
  - GREEN: assertions pass; all pre-existing assertions stay green.
- External surfaces: none (prompt artifact).
- Dependencies: none
- Independent: false
- Brief item covered: "F-1: strengthen the Phase ③b wide-stage instruction … MUST run scripts/pairwise.py … do NOT enumerate a ≥4-object stage's combinations inline"

## Task 2 — F-3: allow single-surface backbone collapse
- Description: In `spec-expansion/SKILL.md` Phase ①, add a note that for a **single-surface / utility / floating app with no sequential journey**, the USM backbone may **collapse to ~1 stage node** and the **navigation graph (Phase ③c) carries the structure** — do NOT force a linear multi-stage spine where none exists (forcing one manufactures fiction; respect the seed-adequacy honesty rail).
- Module: spec-toolkit/skills/spec-expansion/SKILL.md
- Files touched: spec-toolkit/skills/spec-expansion/SKILL.md, spec-toolkit/scripts/test_spec_expansion_skill.py
- Context paths:
  - spec-toolkit/skills/spec-expansion/SKILL.md  (Phase ① + nav-graph para, ~L84-101, post-T1 state)
- Acceptance:
  - RED: `test_spec_expansion_skill.py::test_single_surface_backbone_collapse_present` — assert the SKILL.md Phase ① text contains a single-surface/utility cue (`single-surface` / `single surface`) AND a collapse cue (`collapse` near `navigation graph`).
  - GREEN: assertions pass; pre-existing stay green.
- External surfaces: none.
- Dependencies: Task 1 completes first (same file)
- Independent: false
- Brief item covered: "F-3: add a note to Phase ① that for a single-surface / utility / floating app … the backbone may collapse to ~1 stage node and the navigation graph carries the structure"

## Task 3 — version bump to 0.2.1
- Description: Bump `spec-expansion/SKILL.md` frontmatter `version: 0.2.0` → `0.2.1` and the spec-toolkit plugin manifest version to match (PATCH bump — prose hardening, no behavior-contract change).
- Module: spec-toolkit/skills/spec-expansion/SKILL.md
- Files touched: spec-toolkit/skills/spec-expansion/SKILL.md, spec-toolkit/.claude-plugin/plugin.json
- Context paths:
  - spec-toolkit/.claude-plugin/plugin.json  (version field, currently 0.2.0)
- Acceptance:
  - RED: diagnostic `grep -q "version: 0.2.1" spec-toolkit/skills/spec-expansion/SKILL.md` fails before, passes after; plugin.json version updated consistently.
  - GREEN: version reflects 0.2.1; `test_plugin_manifest.py` stays green.
- External surfaces: none (config).
- Dependencies: Task 2 completes first (same SKILL.md file)
- Independent: false
- Brief item covered: "Version → 0.2.1"
