# Plan: spec-toolkit MVP — critic-first thin slice (v0.1)

Source brief: docs/spec-toolkit/specs/2026-06-11-spec-toolkit-mvp-critic-first.md
Total tasks: 7 (uncapped; width is fine)
Critical-path depth: 4 (≤5) — longest chain T2 → T3 → T4/T5 → T7
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-11; 13/14, Check 12 N/A — not a BLOCKED-fallback)

## Design notes (resolves brief Open Questions)
- **TDD anchor for prompt-driven skills** = a plugin-level executable validator `spec-toolkit/scripts/validate_spec_output.py` that encodes the hybrid output format (OpenSpec skeleton + additive sections) as the executable SSOT + dogfood gate. This is the one piece of real logic → hard-TDD'd (T2, T3).
- **SKILL.md files are prompt artifacts** — verified by (a) a structural grep-test guarding each skill's *load-bearing instructions* (the buried single-sentence rules the `extract-to-reference` memory warns get lost: "must emit blind spots", ban-the-word-"complete", provenance tagging), and (b) behavioral dogfood (T7). Each skill has its OWN test file so the two skills stay parallel-safe.
- **Fixtures inline** in test files via `tmp_path` (no `scripts/fixtures/` subdir — respects flat-folder rule).
- **Pure config** (plugin.json, marketplace.json) is a tdd-iron-law exemption; presence/validity tests added as cheap regression guards, not iron-law-mandated.

## Dependency levels (for parallel dispatch)
- Level 1: T1, T2 (disjoint, parallel)
- Level 2: T3 (after T2), T6 (after T1) — parallel
- Level 3: T4, T5 (after T3) — parallel
- Level 4: T7 (after T3, T4, T5)

---

## Task 1 — plugin manifest
- Description: Create the spec-toolkit plugin manifest declaring name/version/description/license, modeled on `research-toolkit/.claude-plugin/plugin.json`.
- Module: spec-toolkit plugin skeleton
- Files touched: spec-toolkit/.claude-plugin/plugin.json, spec-toolkit/scripts/test_plugin_manifest.py
- Context paths:
  - research-toolkit/.claude-plugin/plugin.json
- Acceptance:
  - RED: `test_plugin_manifest.py` — `python -m pytest spec-toolkit/scripts/test_plugin_manifest.py` fails (no plugin.json / invalid JSON).
  - GREEN: plugin.json is valid JSON with `name=="spec-toolkit"`, a semver `version`, non-empty `description`, `license=="MIT"`.
- Dependencies: none
- Independent: true
- Brief item covered: "new, agent-portable, key-free plugin … Skeleton model = research-toolkit/" (Decision + Current State Evidence/Forward)

## Task 2 — output validator: OpenSpec skeleton checks
- Description: Write `validate_spec_output.py` validating that a spec-toolkit output directory contains `proposal.md` + `specs/` delta whose markdown carries the OpenSpec skeleton: `## ADDED Requirements` → `### Requirement:` → `#### Scenario:` with GIVEN/WHEN/THEN lines (RFC-2119 keyword on the requirement body line). Exit 0 = valid, non-zero = invalid with an agent-actionable message.
- Module: spec-toolkit output validator (skeleton half)
- Files touched: spec-toolkit/scripts/validate_spec_output.py, spec-toolkit/scripts/test_validate_spec_output.py
- Context paths:
  - docs/spec-toolkit/specs/2026-06-11-spec-toolkit-mvp-critic-first.md (Smallest End State → Output hybrid format)
  - docs/spec-toolkit/research/2026-06-11-spec-toolkit-openspec-research-synthesis.md (§2 OpenSpec delta format)
- Acceptance:
  - RED: `test_validate_spec_output.py::test_skeleton_*` — validator (absent) → import/exec fails; a fixture dir missing `#### Scenario:` must be rejected (non-zero).
  - GREEN: rejects fixtures missing proposal.md / missing `## ADDED Requirements` / missing `#### Scenario:` GIVEN-WHEN-THEN; accepts a well-formed skeleton fixture (exit 0).
- Dependencies: none
- Independent: true
- Brief item covered: "OpenSpec delta format is the skeleton … `openspec validate`-clean (structure-only)" (Output)

## Task 3 — output validator: additive-section checks
- Description: Extend `validate_spec_output.py` to also require the spec-toolkit additive sections: `## Provenance` (each item tagged seeded/inferred/critic-found), `## Blind spots — needs human/field input` (present AND non-empty), `## Path × edge matrix`. Tolerant of extra content (mirrors OpenSpec structure-only validate).
- Module: spec-toolkit output validator (additive half)
- Files touched: spec-toolkit/scripts/validate_spec_output.py, spec-toolkit/scripts/test_validate_spec_output.py
- Context paths:
  - docs/spec-toolkit/specs/2026-06-11-spec-toolkit-mvp-critic-first.md (Output → additive sections)
- Acceptance:
  - RED: `test_validate_spec_output.py::test_additive_*` — a fixture with valid skeleton but missing/empty `## Blind spots` must be rejected.
  - GREEN: rejects fixtures missing any additive section or with an empty Blind-spots section; accepts a complete hybrid fixture (skeleton + 3 additive sections).
- Dependencies: Task 2 completes first (same file, extends skeleton checks)
- Independent: false
- Brief item covered: "spec-toolkit's differentiating richness goes in additive markdown sections … `## Provenance` … `## Blind spots` … `## Path × edge matrix`" (Output)

## Task 4 — spec-expansion SKILL.md
- Description: Author the `spec-expansion` skill. **(Revised 2026-06-11 per user directive:** structured as THREE explicit phases — **① USM** (journey backbone) → **② OOUX** (per-object ORCA + state machines, multi-agent fan-out) → **③ auto-expansion matrix** (`backbone × object × CTA × state` grid + 6-lens prune + emit) — each phase announced during execution and emitting a visible proposal.md section (`## USM backbone` / `## OOUX object model` / `## Path × edge matrix`). The old 5-stage detail nests as substeps, no loss.) Every item tagged provenance; emits the hybrid format; includes the "ban the word 'complete' — use 'coverage relative to seed + N lenses'" guardrail; GENERATE-only boundary.
- Module: spec-expansion skill
- Files touched: spec-toolkit/skills/spec-expansion/SKILL.md, spec-toolkit/scripts/test_spec_expansion_skill.py
- Context paths:
  - docs/spec-toolkit/research/2026-06-11-spec-toolkit-openspec-research-synthesis.md (§3.1 5-stage pipeline, §3.2 hard boundaries)
  - research-toolkit/skills/deep-research/SKILL.md (skill authoring style/structure)
- Acceptance:
  - RED: `test_spec_expansion_skill.py` — grep asserts SKILL.md has YAML frontmatter (name+description), the THREE explicit phases (USM/OOUX/matrix) + per-phase announcements + three visible artifact sections (and that the old "5-stage pipeline" framing is gone), provenance-tagging instruction, the ban-"complete" guardrail, and the hybrid output format. Fails before authoring/restructure.
  - GREEN: all required load-bearing phrases present; file passes the folder-structure hook.
- Dependencies: Task 3 completes first (produces the format contract the skill must target)
- Independent: true
- Brief item covered: "`spec-expansion` — sparse seed → … path/edge matrix + candidate scenarios … tagged provenance" (Smallest End State #1)

## Task 5 — completeness-critic SKILL.md
- Description: Author the `completeness-critic` skill: loop-until-dry over a spec-expansion output; multi-lens fixed interrogation (missing object/actor · state completeness · cross-object/system-layer failures · NFR · policy/legal); **must emit its own blind spots** ("aspects I cannot judge → needs human/field input") into the `## Blind spots` section; re-seeds found gaps. Writer≠judge: critic critiques the SPEC for omissions only — never code, never TDD.
- Module: completeness-critic skill
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md, spec-toolkit/scripts/test_completeness_critic_skill.py
- Context paths:
  - docs/spec-toolkit/research/2026-06-11-spec-toolkit-openspec-research-synthesis.md (§3.1 completeness-critic, §4b Planner-Generator-Evaluator + 要件定義 caution)
- Acceptance:
  - RED: `test_completeness_critic_skill.py` — grep asserts frontmatter, loop-until-dry, the multi-lens checklist, the must-emit-blind-spots instruction, and the "critiques spec not code" boundary. Fails before authoring.
  - GREEN: all required load-bearing phrases present; passes folder-structure hook.
- Dependencies: Task 3 completes first (writes into the format's Blind-spots section)
- Independent: true
- Brief item covered: "`completeness-critic` — loop-until-dry … must emit its own blind spots … the defensible differentiator" (Smallest End State #2)

## Task 6 — marketplace registration
- Description: Add a `spec-toolkit` entry to the root `.claude-plugin/marketplace.json` `plugins[]` array (`name`, `description`, `source: "./spec-toolkit/"`).
- Module: marketplace registration
- Files touched: .claude-plugin/marketplace.json, spec-toolkit/scripts/test_marketplace_entry.py
- Context paths:
  - .claude-plugin/marketplace.json
- Acceptance:
  - RED: `test_marketplace_entry.py` — asserts a plugins[] entry exists with `name=="spec-toolkit"` and `source=="./spec-toolkit/"`. Fails before edit.
  - GREEN: entry present; marketplace.json remains valid JSON.
- Dependencies: Task 1 completes first (plugin must exist to register)
- Independent: true
- Brief item covered: "Only existing tracked file touched: root marketplace.json (one new entry)" (Current State Evidence/Boundary)

## Task 7 — dogfood integration + A/B baseline (DoD)
- Description: Run the **A/B differential dogfood** on ONE real sparse seed (reuse an actual past task seed, e.g. a small feature intent). **Arm A (spec-toolkit):** run spec-expansion then completeness-critic → capture output under `spec-toolkit/examples/<seed-slug>/` (proposal.md + specs/ + additive sections). **Arm B (baseline):** run plain `code-toolkit:brainstorming` on the SAME seed → capture its edge-case/omission list under `spec-toolkit/examples/<seed-slug>/baseline-brainstorm.md`. Then diff the two: list which spec-toolkit-found items the baseline genuinely MISSED. This directly tests the bet (per `feedback_ab_baseline_reveals_marginal_behavioral_delta`): "did the critic find real omissions a well-prompted model misses" — not merely "did the critic output something."
- Module: end-to-end A/B dogfood
- Files touched: spec-toolkit/examples/<seed-slug>/ (Arm A generated output: proposal.md + specs/ + additive sections; Arm B baseline-brainstorm.md; a short A/B-delta.md verdict)
- Context paths:
  - spec-toolkit/skills/spec-expansion/SKILL.md
  - spec-toolkit/skills/completeness-critic/SKILL.md
  - spec-toolkit/scripts/validate_spec_output.py
- Acceptance:
  - RED: before the skills exist, no Arm-A output dir → validator has nothing to pass.
  - GREEN: (1) `python spec-toolkit/scripts/validate_spec_output.py spec-toolkit/examples/<seed-slug>/` exits 0 AND the `## Blind spots` section is non-empty; (2) `A/B-delta.md` records the baseline's omission list AND an explicit verdict on whether spec-toolkit surfaced ≥1 real omission the baseline missed (bet PASS) or did not (bet INCONCLUSIVE/FAIL — a valid, recorded outcome, not a blocker). The build is "done" when the experiment has RUN and its verdict is recorded — the verdict itself may be negative.
- Dependencies: Tasks 3, 4, 5 complete first
- Independent: false
- Brief item covered: "DoD / dogfood: expand one real sparse seed end-to-end → the output's scenarios feed straight into code-toolkit:writing-plans … Proves the critic catches an omission" (Smallest End State)

## Notes
- Worktree: `.worktrees/feat-spec-toolkit-mvp` on branch `feat/spec-toolkit-mvp` (off main 806da6b2).
- All tests run at package level via pytest from repo root (e.g. `python -m pytest spec-toolkit/scripts/`).
- v0.2 deferred (per brief Out of Scope): OpenSpec CLI wiring, spec-discovery, spec-persist, router, knowledge-SSOT share, tiering, cross-host testing.
- **Amendment (2026-06-11, post-PASS):** T7 extended from a single-arm dogfood to an A/B differential dogfood (added baseline-brainstorm arm + A/B-delta verdict). Additive and schema-safe — same task, same module, same dependencies (3,4,5), all required fields intact, no DAG change, depth still 4. Per writing-plans amend rule, plan-document-reviewer re-review skipped (amendment only tightens T7's acceptance; structure unchanged).
