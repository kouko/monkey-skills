# Plan: PRINCIPLES.md three-jurisdiction sections (Product / Design / Engineering)

**Source brief**: docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
**Total tasks**: 12
**Critical-path depth**: 4 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-07-03, round 2 — round 1 NEEDS_REVISION fixed by splitting oversized Tasks 4/5 into 4-6/7-8 and grounding Task 12's brief referent)

## Task 1 — Rename validator required heading to `## Product Principles`

- **Description**: In `validate_principles_output.py`, rename the `_PRINCIPLES` constant from `"## Principles"` to `"## Product Principles"` and update every validator error message that names the section; update ALL existing fixtures in `test_validate_principles_output.py` to the new heading so the suite stays green.
- **Module**: `loom-product-principles/scripts/validate_principles_output.py`
- **Files touched**: `loom-product-principles/scripts/validate_principles_output.py`, `loom-product-principles/scripts/test_validate_principles_output.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/validate_principles_output.py
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/test_validate_principles_output.py
- **Acceptance**:
  - **RED**: `test_validate_principles_output.py::test_accepts_product_principles_heading` (a file with `## North Star` + `## Product Principles` carrying 3 marked entries validates OK) fails — the validator still requires the legacy heading.
  - **GREEN**: new heading accepted; no fixture in the file still uses a bare `## Principles` section as a VALID case; full test file green.
- **Dependencies**: none
- **Independent**: true  # disjoint from every other Independent-true task; Tasks 2–3 join AFTER it via Dependencies
- **Brief item covered**: Smallest End State item 1 — "`## Principles` → `## Product Principles` — hard rename, same rules (3–7 top-level ordered entries…)"

## Task 2 — Legacy-heading detection with targeted migration message

- **Description**: Add a validator check that detects a whole-line legacy `## Principles` heading and reports an actionable migration message naming `## Product Principles`. Must not false-positive on `## Product Principles` itself (whole-heading-line match, same style as `_section_body`).
- **Module**: `loom-product-principles/scripts/validate_principles_output.py`
- **Files touched**: `loom-product-principles/scripts/validate_principles_output.py`, `loom-product-principles/scripts/test_validate_principles_output.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/validate_principles_output.py
- **Acceptance**:
  - **RED**: `test_validate_principles_output.py::test_legacy_heading_gets_migration_message` (a file with legacy `## Principles` is invalid AND at least one problem message contains `## Product Principles` as the rename target) fails.
  - **GREEN**: legacy file exits 1 with the migration message; a valid `## Product Principles` file emits no legacy warning.
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: Smallest End State item 1 — "The validator detects the legacy `## Principles` heading and emits a targeted migration message"

## Task 3 — Optional `## Design Principles` / `## Engineering Principles` section checks

- **Description**: Add conditional validator checks for the two optional sections: absent = valid; present = 1–7 top-level ordered entries, EVERY entry carrying the literal `— check:` marker; present with 0 entries = invalid. Implement generically (one rule applied to both headings), reusing `_section_body` / `_principle_entries` / `_CHECK_MARKER`.
- **Module**: `loom-product-principles/scripts/validate_principles_output.py`
- **Files touched**: `loom-product-principles/scripts/validate_principles_output.py`, `loom-product-principles/scripts/test_validate_principles_output.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/validate_principles_output.py
- **Acceptance**:
  - **RED**: `test_validate_principles_output.py::test_optional_jurisdiction_section_rules` (parametrized over both optional headings: absent→valid, 1 marked entry→valid, 8 entries→invalid, 0 entries→invalid, entry missing `— check:`→invalid) fails — the validator currently ignores the sections entirely, so the invalid cases pass validation.
  - **GREEN**: all parametrized cases pass; a file combining all three sections validates OK.
- **Dependencies**: Task 1 completes first
- **Independent**: false  # same files as Tasks 1–2; SDD sequences it after Task 2 (shared write set)
- **Brief item covered**: Smallest End State item 2 — "OPTIONAL sections, 1–7 entries each … A present-but-empty section is invalid"

## Task 4 — Contract: rename required section + add the jurisdiction table

- **Description**: In `principles-rules.md`, rename the required-section contract from `## Principles` to `## Product Principles` (heading, format blocks, prose) and add the jurisdiction table: Product = what/for whom/success trade-offs; Design = interaction posture, feedback/error stance, density, accessibility floor, checkable tone; Engineering = stack, dependency posture, style dial, test-rigor CEILING above the iron-law floor, explicit negative decisions.
- **Module**: `loom-product-principles/skills/product-principles/references/principles-rules.md`
- **Files touched**: `loom-product-principles/skills/product-principles/references/principles-rules.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/references/principles-rules.md
- **Acceptance**:
  - **RED**: diagnostic `grep -q '## Product Principles' loom-product-principles/skills/product-principles/references/principles-rules.md` exits 1 (the contract still uses the legacy section name and has no jurisdiction table).
  - **GREEN**: grep exits 0; a jurisdiction table naming all three jurisdictions with their content scopes is present; no format block still shows a bare `## Principles` section as the required shape.
- **Dependencies**: none  # mirrors the brief directly; validator-behavior sync is Task 6's job
- **Independent**: true  # disjoint from every other Independent-true task; Tasks 5–6 join AFTER it via Dependencies
- **Brief item covered**: Smallest End State item 3 — "The authoring contract (`principles-rules.md`) gains a jurisdiction table — Product = what/for whom/success trade-offs; Design = …; Engineering = …"

## Task 5 — Contract: optional-section rules + re-sorted and new ✅/❌ examples

- **Description**: In `principles-rules.md`, add the optional-section rules (both new sections: 1–7 entries, same `— check:` lexeme, never emitted empty — a jurisdiction with no committed clauses emits no section) and re-sort the existing ✅/❌ examples under their correct jurisdictions, adding ≥1 new synthetic ✅/❌ pair for Design and ≥1 for Engineering.
- **Module**: `loom-product-principles/skills/product-principles/references/principles-rules.md`
- **Files touched**: `loom-product-principles/skills/product-principles/references/principles-rules.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/references/principles-rules.md
- **Acceptance**:
  - **RED**: diagnostic `grep -q '## Design Principles' loom-product-principles/skills/product-principles/references/principles-rules.md` exits 1 (no optional-section contract exists yet).
  - **GREEN**: grep exits 0 for both optional section names; each new section carries ≥1 synthetic ✅/❌ pair; the never-empty rule is stated.
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Brief item covered**: Smallest End State item 3 — "with the existing ✅/❌ examples re-sorted per jurisdiction, new synthetic examples for the two new sections"

## Task 6 — Contract: sync the Validator-contract summary + engineering guardrails

- **Description**: In `principles-rules.md`, update the "Validator contract (summary)" section to mirror the implemented validator checks one-for-one (renamed required heading, legacy-heading migration message, optional-section rules) and state the engineering guardrails: clauses minted only from decisions the user actually commits to; test-rigor clauses set a per-project CEILING above the TDD iron-law floor, never below.
- **Module**: `loom-product-principles/skills/product-principles/references/principles-rules.md`
- **Files touched**: `loom-product-principles/skills/product-principles/references/principles-rules.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/references/principles-rules.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/validate_principles_output.py (as modified by Tasks 1–3)
- **Acceptance**:
  - **RED**: diagnostic `grep -q 'migration' loom-product-principles/skills/product-principles/references/principles-rules.md` exits 1 (the summary still describes only the two legacy checks).
  - **GREEN**: the summary's numbered rules match the validator's implemented checks one-for-one (heading, entry counts per section, marker, migration message); the iron-law-ceiling guardrail sentence is present.
- **Dependencies**: Tasks 2, 3 complete first
- **Independent**: false  # same file as Tasks 4–5; SDD sequences it after them (shared write set)
- **Brief item covered**: Smallest End State item 3 — "its 'Validator contract (summary)' section updated to mirror the new validator checks (rename, migration message, optional-section rules) one-for-one"

## Task 7 — SKILL.md: heading rename, project-constitution framing, frontmatter description

- **Description**: In `SKILL.md`, rename the section format blocks and step prose from `## Principles` to `## Product Principles`; widen the "product-level constitution" framing to "project constitution" (product jurisdiction retained for the Product section); update the frontmatter description to the three-jurisdiction scope while keeping en + zh-TW + ja trigger phrasings and the ≤1024-char Codex limit. Update the existing heading assert in `test_product_principles_skill.py` (the body-procedure structural test asserting `"## Principles" in text`, ~line 116) to `## Product Principles` in the same task.
- **Module**: `loom-product-principles/skills/product-principles/SKILL.md`
- **Files touched**: `loom-product-principles/skills/product-principles/SKILL.md`, `loom-product-principles/scripts/test_product_principles_skill.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/references/principles-rules.md (as modified by Task 4)
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/test_product_principles_skill.py
- **Acceptance**:
  - **RED**: the updated heading assert in `test_product_principles_skill.py` (body-procedure structural test, `## Product Principles` replacing the `## Principles` assert at ~line 116) fails against the current SKILL.md.
  - **GREEN**: that test passes; the description-limit and frontmatter tests in the same file stay green; no SKILL.md format block still shows `## Principles` as the emitted section name.
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Brief item covered**: Decision — "its 'product-level' framing prose widens to 'project constitution', with per-jurisdiction content guidance"

## Task 8 — SKILL.md: design + engineering posture elicitation steps + structural test

- **Description**: In `SKILL.md`, add the optional elicitation steps for design posture and engineering posture (emit a section ONLY for clauses the user commits to; never emit an empty section; engineering test-rigor clauses set a ceiling above the TDD iron-law floor). Add one new structural test `test_skill_defines_three_jurisdiction_sections` to `test_product_principles_skill.py` asserting the three jurisdiction headings and both posture-elicitation steps are present in the SKILL body.
- **Module**: `loom-product-principles/skills/product-principles/SKILL.md`
- **Files touched**: `loom-product-principles/skills/product-principles/SKILL.md`, `loom-product-principles/scripts/test_product_principles_skill.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/references/principles-rules.md (as modified by Tasks 4–6)
- **Acceptance**:
  - **RED**: `test_product_principles_skill.py::test_skill_defines_three_jurisdiction_sections` fails — the SKILL has no design/engineering elicitation steps yet.
  - **GREEN**: the new test passes AND every pre-existing test in the file passes.
- **Dependencies**: Task 7 completes first
- **Independent**: false
- **Brief item covered**: Smallest End State item 4 — "elicitation extends to BOTH engineering posture and design posture … only clauses the user actually commits to are emitted … a jurisdiction with no committed clauses emits no section"

## Task 9 — D8 jurisdiction note in loom-code code-reviewer

- **Description**: In `code-reviewer.md` §D8 (Principles Conformance), add a one-line jurisdiction note: clauses in ALL of PRINCIPLES.md's jurisdiction sections (Product / Design / Engineering) are judged under the existing subject-matter severity rule — a supply-chain-bearing engineering clause violation is 🔴, a dependency-count clause violation is 🟡; no new severity tier. Bump loom-code plugin version (patch) in both manifests.
- **Module**: `loom-code/agents/code-reviewer.md`
- **Files touched**: `loom-code/agents/code-reviewer.md`, `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
  - /Users/kouko/GitHub/monkey-skills/loom-code/agents/code-reviewer.md
  - /Users/kouko/GitHub/monkey-skills/scripts/sync_codex_manifests.py
- **Acceptance**:
  - **RED**: diagnostic `grep -q 'Engineering Principles' loom-code/agents/code-reviewer.md` exits 1 (D8 today names only PRINCIPLES.md generically).
  - **GREEN**: grep exits 0 within the D8 section; severity calibration lines (:410-415 region) otherwise unchanged; both loom-code manifests carry the same bumped version.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State item 5 — "loom-code D8: one-line jurisdiction note … no new severity tier"

## Task 10 — loom-product-principles metadata: version, descriptions, README, CHANGELOG

- **Description**: Bump loom-product-principles 0.2.0 → 0.3.0 in `.claude-plugin/plugin.json` AND `.codex-plugin/plugin.json` (use `scripts/sync_codex_manifests.py` if it owns the mirroring); widen both `description` fields and the codex `interface` texts from "product PRINCIPLES.md" to the project-constitution / three-jurisdiction framing; update `README.md` framing likewise (keep the README's existing language structure as found); add a CHANGELOG entry describing the rename + new sections + migration message.
- **Module**: `loom-product-principles/.claude-plugin/plugin.json`
- **Files touched**: `loom-product-principles/.claude-plugin/plugin.json`, `loom-product-principles/.codex-plugin/plugin.json`, `loom-product-principles/README.md`, `loom-product-principles/skills/product-principles/CHANGELOG.md`, `.claude-plugin/marketplace.json` (only if the description-sync check requires it)
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/.claude-plugin/plugin.json
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/.codex-plugin/plugin.json
  - /Users/kouko/GitHub/monkey-skills/scripts/check-marketplace-description-sync.py
  - /Users/kouko/GitHub/monkey-skills/scripts/check-plugin-description-skill-coherence.py
- **Acceptance**:
  - **RED**: diagnostic `grep -q '"version": "0.3.0"' loom-product-principles/.claude-plugin/plugin.json` exits 1.
  - **GREEN**: version 0.3.0 in both manifests; `python scripts/check-marketplace-description-sync.py` and `python scripts/check-plugin-description-skill-coherence.py` both exit 0; CHANGELOG entry present.
- **Dependencies**: Task 8 completes first
- **Independent**: false
- **Brief item covered**: Decision — "The generator (loom-product-principles) owns all three sections — one file, one owner; its 'product-level' framing prose widens to 'project constitution'"

## Task 11 — Delete the shipped BACKLOG entry and update the v1.1 start condition

- **Description**: In `docs/loom/BACKLOG.md`, delete the "ENGINEERING.md — per-project engineering constitution" entry (completed items are deleted, not archived) and update the v1.1 batch-mode entry's start condition from "(after ENGINEERING.md)" to reflect that the constitution work shipped.
- **Module**: `docs/loom/BACKLOG.md`
- **Files touched**: `docs/loom/BACKLOG.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/BACKLOG.md
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md
- **Acceptance**:
  - **RED**: diagnostic `grep -q 'ENGINEERING.md — per-project engineering constitution' docs/loom/BACKLOG.md` exits 0 (entry still present).
  - **GREEN**: grep exits 1; v1.1 entry no longer names ENGINEERING.md as its start condition; no other entry touched.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: What Becomes Obsolete — "The BACKLOG 'ENGINEERING.md' entry … deleted (not archived) in the shipping PR; the v1.1 batch-mode entry's '(after ENGINEERING.md)' start condition updates"

## Task 12 — Regenerate the living-spec INDEX for the new brief + plan docs

- **Description**: Run the living-spec index check (`loom-code/scripts/check-living-spec-index.py`) against docs/loom/, regenerate `docs/loom/INDEX.md` per the script's own regeneration instructions so the new spec and plan files are registered, and confirm the index test suite passes. Do NOT add `@req:` tags anywhere (dangling-tag CI failure class).
- **Module**: `docs/loom/INDEX.md`
- **Files touched**: `docs/loom/INDEX.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/scripts/check-living-spec-index.py
  - /Users/kouko/GitHub/monkey-skills/loom-code/scripts/test_check_living_spec_index.py
  - /Users/kouko/GitHub/monkey-skills/docs/loom/INDEX.md
- **Acceptance**:
  - **RED**: diagnostic `python loom-code/scripts/check-living-spec-index.py` exits non-zero (new docs unindexed).
  - **GREEN**: the check exits 0 and `pytest loom-code/scripts/test_check_living_spec_index.py` is green.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State item 7 — "docs/loom/INDEX.md regenerated: this brief and its plan are new docs under docs/loom/, and the living-spec index CI gate … requires lockstep registration"

## Notes

- Runtime resolution (2026-07-03): **Task 12 resolved as already-satisfied, no commit.** The implementer verified the living-spec index does NOT register brief/plan markdown under docs/loom/specs|plans — its scope is `@req`-tagged tests + the `docs/loom/spec/` (singular) requirement namespace, which this change never touches. All three GREEN checks pass unchanged (`--verify-index` OK, structural gate OK, 18 index tests green). Brief Smallest End State item 7's premise was over-cautious; the acceptance's GREEN condition holds vacuously.
- Runtime dispatch note (2026-07-03): wave 2 = Tasks 2, 5, 7 dispatched concurrently after their prerequisites (Tasks 1 and 4) completed — pairwise-disjoint write sets verified by the orchestrator (validator+its test / principles-rules.md / SKILL.md+skill test). Task 3 held back until Task 2 lands (shared write set), Task 6 until Task 5, Task 8 until Task 7, Task 10 until Task 8.
- Amendment after PASS (2026-07-03): flipped Tasks 1 and 4 to `Independent: true` per the round-2 reviewer's own Check-15 advisory (chain heads with `Files touched` disjoint from every other `Independent: true` task; Check-14 disjointness re-verified by hand). Additive and schema-safe — DAG, fields, and depth unchanged; re-review skipped.
- Critical path: Task 4 → 7 → 8 → 10 (depth 4). Side chains: 1 → 2 (depth 2), 1 → 3 → 6 (depth 3), 4 → 5 (depth 2). Tasks 9, 11, 12 are depth-1 leaves.
- Tasks 1–3 share two files (validator + its test file): Task 3 depends only on Task 1 semantically but SDD runs it after Task 2 because of the shared write set. Same pattern for Tasks 4–6 (contract file, listed order) and Tasks 7–8 (SKILL + skill test).
- Tasks 9, 11, 12 are `Independent: true` with mutually disjoint `Files touched` — `dispatching-parallel-agents` may run them as one wave alongside the sequential chains.
- No `External surfaces` fields: every task is internal markdown / stdlib-Python / JSON edits — no HTTP API, SDK package, MCP tool, CLI-flag, or sibling-team contract surface is touched.
- No new runnable capability: all tests extend existing pytest files already wired into CI; the command surface is unchanged.
- The loom-pipeline driver and its bundled asset are deliberately NOT in any task (brief Out of Scope: seg1 adopt gate is heading-agnostic — verified in Evidence).
