# Plan: loom living-spec slice 3 (E-core) — persistent intent layer

Source brief: docs/loom/specs/2026-06-23-loom-living-spec-slice3-intent-layer.md
Total tasks: 5
Critical-path depth: 3 (≤5)   ← longest chains: T1→T2→T3 and T1→T4→T5
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-23; 14/14)

Resolved open-Qs:
- **Validator home = a NEW sibling `loom-spec/scripts/validate_intent_layer.py`** (NOT an
  extension of `validate_spec_output.py`): the intent layer (`docs/loom/spec/`) is a
  different artifact at a different root than the change-folder (`docs/loom/<change-id>/`)
  that `validate_spec_output.py` validates; one validator = one root = single responsibility.
- **Canonical TOP `MODEL.md` required sections** (the SSOT both the validator and the SKILL
  doc use): `## Invariants`, `## Object state machines`, `## Out of scope`.
- **Persistent layer shape**: `docs/loom/spec/MODEL.md` (TOP) + `docs/loom/spec/<capability>/README.md` (MID).

## Task 1 — validator: TOP MODEL.md structural check
- Description: create `loom-spec/scripts/validate_intent_layer.py` with
  `check_top_model(spec_dir) -> list[str]`: when `spec_dir/MODEL.md` exists, return one
  problem per MISSING required section (`## Invariants`, `## Object state machines`,
  `## Out of scope`); a well-formed MODEL.md → `[]`. (Absent MODEL.md is handled in Task 3,
  not here — this check only grades a MODEL.md that exists.) Mirror the
  `_section_body`/whole-header-line matching + `list[str]`-problems contract of
  `validate_spec_output.py`.
- Module: loom-spec/scripts/validate_intent_layer.py
- Files touched: loom-spec/scripts/validate_intent_layer.py, loom-spec/scripts/test_validate_intent_layer.py
- Context paths:
  - loom-spec/scripts/validate_spec_output.py  (the `_section_body` helper + check contract to mirror)
- Acceptance:
  - RED: test_validate_intent_layer.py::test_top_model_missing_section_reported fails (check_top_model undefined)
  - GREEN: a MODEL.md missing `## Object state machines` yields exactly one problem naming that section; a MODEL.md with all three sections yields []
- Dependencies: none
- Independent: false
- Brief item covered: "Structural validator — checks ... TOP MODEL.md present + has the required top-level sections"

## Task 2 — validator: MID per-capability README check
- Description: add `check_mid_readmes(spec_dir) -> list[str]` to
  `validate_intent_layer.py`: for each immediate sub-directory of `spec_dir` (a capability
  dir), return a problem if it lacks a `README.md`; capability dirs that have one → no
  problem. (`spec_dir` having no capability subdirs → `[]`.)
- Module: loom-spec/scripts/validate_intent_layer.py
- Files touched: loom-spec/scripts/validate_intent_layer.py, loom-spec/scripts/test_validate_intent_layer.py
- Context paths:
  - loom-spec/scripts/validate_intent_layer.py  (the module Task 1 created; add a sibling function)
- Acceptance:
  - RED: test_validate_intent_layer.py::test_mid_capability_without_readme_reported fails (check_mid_readmes undefined)
  - GREEN: a `spec_dir` with capability dir `order/` lacking README.md yields one problem naming `order`; a capability dir WITH README.md yields none
- Dependencies: Task 1 completes first (same module file)
- Independent: true
- Brief item covered: "Structural validator — checks ... each capability dir has a MID README.md"

## Task 3 — validator: aggregator + absent-layer tolerance + CLI
- Description: add `validate(spec_dir) -> tuple[bool, list[str]]` aggregating
  check_top_model + check_mid_readmes, a `main(argv)` CLI (exit 0 ok / exit 1 + problems on
  stderr, mirroring validate_spec_output.py's main), and the **absent-layer tolerance**: if
  `spec_dir` does not exist OR is empty (no MODEL.md AND no capability subdirs), `validate`
  returns `(True, [])` — a mid-adoption repo with no intent layer yet is NOT an error (mirror
  the ui-flows-seam "if absent, ignore" stance). The check fires only once the layer exists.
- Module: loom-spec/scripts/validate_intent_layer.py
- Files touched: loom-spec/scripts/validate_intent_layer.py, loom-spec/scripts/test_validate_intent_layer.py
- Context paths:
  - loom-spec/scripts/validate_spec_output.py  (validate()/main() shape + exit-code convention to mirror)
- Acceptance:
  - RED: test_validate_intent_layer.py::test_absent_layer_is_ok fails (validate undefined)
  - GREEN: validate() on a non-existent/empty spec_dir → (True, []); on a layer with a defective MODEL.md → (False, [...]); main exits 0 on clean, 1 on problems. New runnable verb: if loom-spec declares validators in a command surface (AGENTS.md / CI / Makefile), add `validate_intent_layer.py` there and verify it runs; if no such surface exists, note that in the implementer report.
- Dependencies: Task 2 completes first (same module file; aggregator composes both checks)
- Independent: true
- Brief item covered: "LAYER-ABSENT IS TOLERATED (mid-adoption repo has no intent layer yet — fire only when it exists)"

## Task 4 — SKILL.md authoring convention for the intent layer
- Description: add a new section to `loom-spec/skills/spec-expansion/SKILL.md` (e.g.
  "Authoring the persistent intent layer") documenting: the TOP `docs/loom/spec/MODEL.md`
  (with the three canonical sections `## Invariants` / `## Object state machines` /
  `## Out of scope`) + MID `docs/loom/spec/<capability>/README.md` locations; **cut rule #4**
  ("remove this capability — does this content get deleted?" YES→MID, NO→TOP); and the
  **anti-pattern** that MID MUST NOT restate behavior a test owns (human-reviewed discipline,
  not CI-gated). Section names MUST match Task 1's enforced canonical sections.
- Module: loom-spec/skills/spec-expansion/SKILL.md
- Files touched: loom-spec/skills/spec-expansion/SKILL.md
- Context paths:
  - loom-spec/skills/spec-expansion/SKILL.md  (§Consuming a ui-flows.md seed = the existing doc-convention style to match; §The hybrid output format)
  - loom-spec/scripts/validate_intent_layer.py  (Task 1 — the enforced section names this doc must mirror)
- Acceptance:
  - RED: test_spec_expansion_skill.py::test_skill_documents_intent_layer fails (the new section/paths/cut-rule text absent)
  - GREEN: SKILL.md contains the intent-layer section naming `docs/loom/spec/MODEL.md`, `README.md`, the three canonical TOP sections, cut rule #4, and the MID-no-restate anti-pattern
- Dependencies: Task 1 completes first (doc mirrors the validator's canonical section names — doc-mirrors-code)
- Independent: true
- Brief item covered: "Authoring convention — a new section in spec-expansion/SKILL.md: how to author TOP vs MID via cut rule #4 + the anti-pattern"

## Task 5 — behavioral test for the SKILL convention
- Description: add `test_skill_documents_intent_layer` to
  `loom-spec/scripts/test_spec_expansion_skill.py` (if Task 4 didn't already place it there)
  asserting the spec-expansion SKILL.md carries the intent-layer convention: the MODEL.md +
  per-capability README.md paths, the three canonical TOP sections, cut rule #4, and the
  MID-no-restate anti-pattern. Follows the existing behavioral-test style in that file.
- Module: loom-spec/scripts/test_spec_expansion_skill.py
- Files touched: loom-spec/scripts/test_spec_expansion_skill.py
- Context paths:
  - loom-spec/scripts/test_spec_expansion_skill.py  (existing behavioral-test style to match)
  - loom-spec/skills/spec-expansion/SKILL.md  (the doc under test, written by Task 4)
- Acceptance:
  - RED: test_spec_expansion_skill.py::test_skill_documents_intent_layer fails before Task 4's text lands / before this assertion exists
  - GREEN: the test passes against the Task-4 SKILL.md and is part of the package suite
- Dependencies: Task 4 completes first (tests the doc Task 4 writes)
- Independent: true
- Brief item covered: "Tests — ... a behavioral test for the SKILL convention"

## Notes
- Post-PASS amendment (2026-06-23, additive/schema-safe — re-review skipped): flipped
  Task 3 + Task 5 `Independent: false` → `true` per the reviewer's Check-15 advisory (both
  at L2, disjoint files [validate_intent_layer.py vs test_spec_expansion_skill.py], no
  mutual dep). All `Independent: true` tasks (T2/T3/T4/T5) remain pairwise file-disjoint at
  their level, so Check 14 still holds (T2∥T4 at L1; T3∥T5 at L2).
- Dependency levels: L0 = {T1}; L1 = {T2, T4} (both depend on T1, disjoint files
  [validate_intent_layer.py vs SKILL.md], no mutual semantic dep → Independent pair);
  L2 = {T3 (after T2), T5 (after T4)}. Critical-path depth = 3.
- Canonical TOP section names (`## Invariants` / `## Object state machines` /
  `## Out of scope`) are the shared contract between Task 1 (enforces) and Task 4
  (documents); Task 4 depends on Task 1 so the doc mirrors the executable truth (no drift).
- Out of scope (from brief): active/deferred status (capstone G), F closed loop (next
  slice), relocating spec-expansion's change-folder output, repo-wide index wiring, and a
  CI check that MID restates behavior (human review per parent brief §Residual rot surface).
- Test command: `cd loom-spec/scripts && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q`.
