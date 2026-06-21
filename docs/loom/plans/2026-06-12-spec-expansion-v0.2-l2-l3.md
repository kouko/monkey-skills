# Plan: spec-expansion v0.2 — L2 cross-object combination + L3 journey navigation

Source brief: docs/loom/specs/2026-06-12-spec-expansion-v0.2-l2-l3.md
Total tasks: 7   (width is fine — 4 parallel leaves at wave 1)
Critical-path depth: 4 (≤5)   — longest chain T1 → T2 → T5 → T7
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-12) — 14/14 checks; T3 Independent justified by pinned Shared-Contract. SDD must carry the pinned section-name literals verbatim into the T4/T5 implementer prompts (reviewer execution-fidelity note).

## Shared contract (pinned strings — all implementers use these EXACT bytes)

These resolve the doc-mirrors-code coupling at plan time, so the validator task (T3) and the SKILL.md tasks (T4/T5) parallelize safely:

- L2 proposal.md section header: `## Cross-object combinations`
- L3 proposal.md section header: `## Journey navigation`
- L2 phase announce line: `— Phase ③b cross-object combinations —`
- L3 phase announce line: `— Phase ③c journey navigation —`
- Pairwise script: `spec-toolkit/scripts/pairwise.py`; CLI reads JSON `{"params": {"<Object>": ["<state>", …], …}}` on **stdin**, prints a JSON list of rows (each row = `{"<Object>": "<state>", …}`) to **stdout**.
- Both new sections are **structurally required** (header always emitted, like `## Blind spots`). L2's body MAY state the gate outcome ("no interaction-dense stage — combinations N/A") rather than padding; L3's body states the nav transitions (or "single-stage — no inter-stage navigation").

## Notes

- T3 (validator) is `Independent: true` despite mirroring T4/T5's section names — the names are pinned above, so there is no runtime coupling; both sides hard-code the same bytes. (Disjoint files + pinned contract = safe to parallelize.)
- Token budget: spec-expansion SKILL.md is 255 lines; L2+L3 additions are expected to land it ~330–360 lines, under the <500-line / ~6000-tok ceiling — keep inline (no `references/` extraction) per `feedback_extract_to_reference_load_bearing_rule`. If an implementer finds it exceeds budget, that is a BLOCKED-resplit signal, not a silent extraction.
- Package-suite run (`pytest spec-toolkit/scripts/`) is verification-before-completion's job at branch close, not a plan task.

## Task 1 — pairwise generator core
- Description: Add a pure-function `pairwise(params: dict[str, list[str]]) -> list[dict[str, str]]` that returns a set of rows covering every (object_i=state, object_j=state) pair across all object pairs (greedy all-pairs cover; need not be size-optimal).
- Module: spec-toolkit/scripts/pairwise.py
- Files touched: spec-toolkit/scripts/pairwise.py, spec-toolkit/scripts/test_pairwise.py
- Context paths:
  - spec-toolkit/scripts/validate_spec_output.py  (stdlib-only style reference)
- Acceptance:
  - RED: `test_pairwise.py::test_covers_all_pairs` — for a 4-object × 3-state input, assert every cross-object value-pair appears in ≥1 returned row AND `len(rows) < 3**4` (smaller than full cartesian).
  - GREEN: `pairwise()` returns an all-pairs-covering, sub-cartesian row set.
- External surfaces: stdlib only (`itertools`); no third-party libs.
- Dependencies: none
- Independent: true
- Brief item covered: "a small pairwise generator for wide stages (≥4 objects, which the A/B showed leak under pure in-prompt)"

## Task 2 — pairwise CLI wrapper
- Description: Add a `__main__` CLI to `pairwise.py` that reads `{"params": {...}}` JSON from stdin and prints the pairwise rows as a JSON list to stdout.
- Module: spec-toolkit/scripts/pairwise.py
- Files touched: spec-toolkit/scripts/pairwise.py, spec-toolkit/scripts/test_pairwise.py
- Context paths:
  - spec-toolkit/scripts/pairwise.py  (the core function from T1)
- Acceptance:
  - RED: `test_pairwise.py::test_cli_stdin_stdout_roundtrip` — pipe a JSON `params` object to the script via subprocess; assert stdout parses to a JSON list whose rows cover all pairs.
  - GREEN: CLI round-trips stdin JSON → stdout pairwise rows.
- External surfaces: stdlib only (`json`, `sys`, `subprocess` in test).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "a small pairwise generator … the one genuinely-new code artifact = the pairwise generator script"

## Task 3 — validator enforces L2 + L3 sections
- Description: In `validate_spec_output.py`, add `_SEC_CROSS_OBJECT_COMBINATIONS = "## Cross-object combinations"` and `_SEC_JOURNEY_NAVIGATION = "## Journey navigation"`, extend the additive-section presence check to require both, and extend the inline `_well_formed_additive()` fixture in the test to include them.
- Module: spec-toolkit/scripts/validate_spec_output.py
- Files touched: spec-toolkit/scripts/validate_spec_output.py, spec-toolkit/scripts/test_validate_spec_output.py
- Context paths:
  - spec-toolkit/scripts/validate_spec_output.py  (lines 124-128, existing `_SEC_*` + check pattern)
- Acceptance:
  - RED: `test_validate_spec_output.py::test_rejects_missing_cross_object_and_journey` — a proposal.md with the 5 v0.1 sections but missing the 2 new ones returns `not ok` with problems naming both `Cross-object combinations` and `Journey navigation`.
  - GREEN: validator flags either missing section; well-formed 7-section fixture passes.
- External surfaces: none (internal logic).
- Dependencies: none
- Independent: true
- Brief item covered: "new `## ` proposal.md artifacts for L2 + L3 → matching `_SEC_*` checks in `validate_spec_output.py` + tests"

## Task 4 — spec-expansion SKILL.md: L3 journey navigation
- Description: In `spec-expansion/SKILL.md`, (a) in Phase ① add the instruction to ALSO build the backbone as a navigation graph (nodes=stages; edges=forward/back/skip/abandon/resume_reenter/error_escape/retry_self); (b) add Phase ③c applying 0-switch state-transition coverage to that graph (every nav edge once → required reaction), broadly applied to any ≥2-stage flow, with the `— Phase ③c journey navigation —` announce line; (c) add `## Journey navigation` to the proposal.md visible-sections list; (d) note the critic remains the deep complement for nuanced resume/re-entry landing-points.
- Module: spec-toolkit/skills/spec-expansion/SKILL.md
- Files touched: spec-toolkit/skills/spec-expansion/SKILL.md, spec-toolkit/scripts/test_spec_expansion_skill.py
- Context paths:
  - spec-toolkit/skills/spec-expansion/SKILL.md  (Phase ① + Phase ③ + visible-sections list)
  - docs/loom/design/2026-06-11-L2-ab-validation-results.md  (§7-§8 grounding)
- Acceptance:
  - RED: `test_spec_expansion_skill.py::test_l3_journey_navigation_present` — assert SKILL.md contains the `— Phase ③c journey navigation —` announce, `## Journey navigation`, "navigation graph", and a transition-coverage cue ("0-switch" or "state-transition").
  - GREEN: assertions pass; existing tests stay green.
- External surfaces: none (prompt artifact).
- Dependencies: none
- Independent: true
- Brief item covered: "L3 … in Phase ① also build the backbone as a navigation graph … add Phase ③c = apply 0-switch state-transition coverage"

## Task 5 — spec-expansion SKILL.md: L2 cross-object combinations
- Description: In `spec-expansion/SKILL.md`, add Phase ③b: per stage, identify co-active objects → enumerate their joint state combinations → required reaction; **gated on interaction-density** (run only where a stage's reaction depends on a joint ≥2-object state); full in-prompt enumeration for ≤3-object stages, and for ≥4-object (wide) stages call `spec-toolkit/scripts/pairwise.py`; add the `— Phase ③b cross-object combinations —` announce and `## Cross-object combinations` section; carry the honesty rail (gated-off body states "no interaction-dense stage", never pad; wide-stage residue blind-spotted).
- Module: spec-toolkit/skills/spec-expansion/SKILL.md
- Files touched: spec-toolkit/skills/spec-expansion/SKILL.md, spec-toolkit/scripts/test_spec_expansion_skill.py
- Context paths:
  - spec-toolkit/skills/spec-expansion/SKILL.md  (Phase ③ grid+prune, post-T4 state)
  - spec-toolkit/scripts/pairwise.py  (the wide-stage generator the prose references)
- Acceptance:
  - RED: `test_spec_expansion_skill.py::test_l2_cross_object_combinations_present` — assert SKILL.md contains `— Phase ③b cross-object combinations —`, `## Cross-object combinations`, an interaction-density gate cue ("interaction-density" / "joint state"), and the `scripts/pairwise.py` reference for wide stages.
  - GREEN: assertions pass; existing tests stay green.
- External surfaces: none (prompt artifact; the referenced script is internal).
- Dependencies: Tasks 2, 4 complete first (Task 4 = same SKILL.md file; Task 2 = prose references the pairwise CLI)
- Independent: false
- Brief item covered: "L2 … add Phase ③b … gated on interaction-density … a small pairwise generator for wide stages"

## Task 6 — completeness-critic dual-role note
- Description: In `completeness-critic/SKILL.md`, add a short note that spec-expansion v0.2 now systematizes L2 (cross-object combinations) and L3 (journey navigation), so the critic refocuses its omission hunt on single-object extremes, nuanced resume/re-entry landing-points, and true blind spots — it is NOT merely "lighter".
- Module: spec-toolkit/skills/completeness-critic/SKILL.md
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md, spec-toolkit/scripts/test_completeness_critic_skill.py
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md  (role section)
- Acceptance:
  - RED: `test_completeness_critic_skill.py::test_dual_role_note_present` — assert the critic SKILL.md references the L2/L3 systematization and a refocus cue ("single-object" / "resume" / "landing").
  - GREEN: assertion passes; existing tests stay green.
- External surfaces: none (prompt artifact).
- Dependencies: none
- Independent: true
- Brief item covered: "the completeness-critic SKILL.md role description may need a one-line note that L2/L3 now systematize part of what it used to carry"

## Task 7 — version bump to 0.2.0
- Description: Bump `spec-expansion/SKILL.md` frontmatter `version: 0.1.0` → `0.2.0`, and the spec-toolkit plugin manifest version accordingly.
- Module: spec-toolkit/skills/spec-expansion/SKILL.md
- Files touched: spec-toolkit/skills/spec-expansion/SKILL.md, spec-toolkit/.claude-plugin/plugin.json
- Context paths:
  - spec-toolkit/.claude-plugin/plugin.json  (version field)
- Acceptance:
  - RED: diagnostic `grep -q "version: 0.2.0" spec-toolkit/skills/spec-expansion/SKILL.md` fails before, passes after; plugin.json version updated consistently.
  - GREEN: version reflects v0.2.0; `test_plugin_manifest.py` stays green.
- External surfaces: none (config).
- Dependencies: Task 5 completes first (same SKILL.md file; bump reflects completed L2/L3 content)
- Independent: false
- Brief item covered: "Build spec-expansion v0.2" (the version the brief names)
