# Plan: spec→code seam wiring

Source brief: docs/loom/specs/2026-06-21-spec-to-code-wiring.md
Total tasks: 6 (uncapped; width fine)
Critical-path depth: 3 (≤5) — wave1{T1..T4} → T5 → T6
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-21, round 2 — 14/14; amendments R2/R5/R6/R7/R3 folded into T1/T2/T3/T6 without breaking any check; T1 stays ≤5-min, no split). Carried advisories: T5 fattest (splits via BLOCKED-fallback), T6 RED is a behavioral ritual.

## Open Questions — resolved at plan time (research-informed, round 2)

1. Traceability field (R5): keep the one field `Brief item covered:`; broaden its accepted
   *referent* to a **stable join key** `<change-id> / Requirement: <name> / Scenario: <name>`
   (à la Kiro `_Requirements:` / Spec-Kit `FR-###`) — checkable, no new field, Check 3 intact.
2. Freeze discrimination (R6, revised from shape-sniffing): **user declares** which artifact;
   freeze confirms by **named-artifact presence** (`specs/<capability>/spec.md` at the
   declared path) **AND** `loom-spec/scripts/validate_spec_output.py` exit 0. No fuzzy
   content-shape classifier (aligns with the declaration-gate learning).
3. Multi-Scenario Requirement: each `#### Scenario:` → one RED/GREEN; group or split per
   the ≤5-min rule; one `### Requirement:` may fan to N tasks.

Decision notes:
- No new validator (R4) — freeze reuses loom-spec's `validate_spec_output.py` (cross-plugin
  call, exit 0). Our validator already checks GIVEN/WHEN/THEN bullets (L101-116), stricter
  than OpenSpec's `####`-count, so the reuse is a sound testability gate. New executable
  surface = guard tests only.
- Point-don't-copy carve-out (R2/R8 — fact vs interpretation): THEN observable / magic
  values / signatures = facts → copied verbatim into RED/GREEN; narrative + rationale =
  interpretation → linked back.
- Consumer read-only (R7): writing-plans MUST NOT modify the producer's change-folder.
- Scenario→test coverage back-check (R3): every `#### Scenario:` must map to ≥1 task
  (verified in the T6 dogfood; OpenSpec `verify`-style).

## Notes

- **Cross-task coherence**: T1 (writing-plans input doc) and T2 (traceability field +
  reviewer) describe the *same* contract surface and must stay mutually consistent. Files
  are disjoint (Independent: true) but the whole-branch review's cross-task-coherence
  dimension is the backstop. If wave1 is dispatched in parallel, **orchestrator commits;
  implementers do not** (per the one-worktree interleaved-commit race) — else dispatch
  wave1 sequentially.
- **Point-don't-copy**: all doc edits *link back* to loom-spec's owned format
  (`spec-expansion/SKILL.md`, `validate_spec_output.py`); none copies the schema. loom-spec
  stays the SSOT.
- T4 deliberately flips an existing test that *encodes* the Tier-2 deferral
  (`test_brainstorming_greenfield_nudge.py:157-170`). The deferral is the design being
  changed, so updating that assertion is intentional, not a violation.

## Task 1 — writing-plans: document the change-folder input contract
- Description: Add a "Consuming a loom-spec change-folder" section to writing-plans
  SKILL.md — second input contract alongside the brief; map each `#### Scenario:`
  GIVEN/WHEN/THEN → one task `Acceptance: RED/GREEN`; link back (point-don't-copy) to the
  source `### Requirement:` / `#### Scenario:` names; multi-Scenario fan-out per ≤5-min.
  **R2/R8 carve-out:** state that the THEN observable / magic values / signatures are
  copied **verbatim** into the assertion (facts), while narrative + rationale are linked,
  not copied. **R7:** state the consumer is **read-only** on the change-folder (loom-spec
  is SSOT; writing-plans must not edit it).
- Module: loom-code/skills/writing-plans (SKILL.md)
- Files touched: loom-code/skills/writing-plans/SKILL.md, loom-code/scripts/test_spec_to_code_wiring.py
- Context paths:
  - loom-code/skills/writing-plans/SKILL.md (existing input contract §14,25,176)
  - loom-spec/skills/spec-expansion/SKILL.md (Scenario schema §305-318, output §287-297)
  - loom-code/scripts/test_brainstorming_greenfield_nudge.py (marker-test pattern to mirror)
- Acceptance:
  - RED: test_spec_to_code_wiring.py::test_writing_plans_documents_changefolder_input — asserts SKILL.md contains the section heading + the strings `#### Scenario:`, `RED`, `GREEN`, "point-don't-copy"/"link back", a verbatim-copy carve-out for THEN/binding values, AND a read-only-on-the-change-folder rule; fails (section absent)
  - GREEN: test passes; section present, links back rather than copies, carve-out + read-only stated
- Dependencies: none
- Independent: true
- Brief item covered: "writing-plans gains a second input contract — a validated loom-spec change-folder … maps each #### Scenario: → one task's Acceptance: RED/GREEN; point-don't-copy carve-out (R2/R8); consumer read-only (R7)" (Decision §1)

## Task 2 — generalize traceability field to a stable join key + Check 3
- Description: In plan-format.md, document that `Brief item covered:` accepts a **stable
  join key** referent for change-folder provenance: `<change-id> / Requirement: <name> /
  Scenario: <name>` (R5 — checkable, à la Kiro `_Requirements:` / Spec-Kit `FR-###`). In
  plan-document-reviewer-prompt.md, generalize Check 3 to accept either a brief item or this
  spec join-key referent (field-presence unchanged; broadened valid content).
- Module: loom-code/skills/writing-plans (references)
- Files touched: loom-code/skills/writing-plans/references/plan-format.md, loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md, loom-code/scripts/test_traceability_generalization.py
- Context paths:
  - loom-code/skills/writing-plans/references/plan-format.md (Brief item covered field)
  - loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md (Check 3)
- Acceptance:
  - RED: test_traceability_generalization.py — asserts plan-format.md + reviewer prompt both name the stable join-key referent (`<change-id> / Requirement / Scenario`) as accepted provenance; fails (only brief referent today)
  - GREEN: test passes; Check 3 accepts the spec join-key provenance
- Dependencies: none
- Independent: true
- Brief item covered: "links back via a stable join key (R5 — <change-id> / Requirement: <name> / Scenario: <name>) … plan-document-reviewer Check 3 intact" (Decision §1)

## Task 3 — using-loom-code: freeze accepts a validated change-folder
- Description: Extend Continuous-mode freeze (entry) in using-loom-code SKILL.md to accept
  a human-approved, validate_spec_output-clean change-folder as an alternative entry
  artifact alongside the brainstorming brief. **R6 discrimination (NOT shape-sniffing):**
  the user **declares** which artifact; freeze confirms by **named-artifact presence**
  (`specs/<capability>/spec.md` at the declared path) **AND** `validate_spec_output.py`
  exit 0. STOP contract + never-auto-merge unchanged.
- Module: loom-code/skills/using-loom-code (SKILL.md)
- Files touched: loom-code/skills/using-loom-code/SKILL.md, loom-code/scripts/test_freeze_changefolder.py
- Context paths:
  - loom-code/skills/using-loom-code/SKILL.md (freeze §69-72, STOP §78-91)
  - loom-spec/scripts/validate_spec_output.py (the exit-0 gate the freeze reuses)
- Acceptance:
  - RED: test_freeze_changefolder.py — asserts freeze section names the change-folder alternative discriminated by **user-declaration + named-artifact presence (`specs/...spec.md`) + `validate_spec_output` exit 0** (NOT content-shape sniffing), AND still asserts "never auto-merge"/STOP unchanged; fails (brief-only today)
  - GREEN: test passes; freeze accepts either artifact via declared+presence+validator, STOP/merge invariants intact
- Dependencies: none
- Independent: true
- Brief item covered: "Continuous-mode freeze accepts the approved change-folder … Discrimination (R6): user declares + named-artifact presence + validate_spec_output exit 0; STOP contract + never-auto-merge unchanged" (Decision §2)

## Task 4 — un-defer the Tier-2 markers (brainstorming + CHANGELOG)
- Description: Flip the Tier-2 "deferred" marker at brainstorming/SKILL.md:193 to "active
  / wired" pointing at the new writing-plans input contract; resolve the deferred CHANGELOG
  entries (§94-96, §114-117). Update the existing greenfield-nudge test assertion that
  encodes the deferral.
- Module: loom-code (cross-doc deferral markers)
- Files touched: loom-code/skills/brainstorming/SKILL.md, loom-code/CHANGELOG.md, loom-code/scripts/test_brainstorming_greenfield_nudge.py
- Context paths:
  - loom-code/skills/brainstorming/SKILL.md (§193 Tier-2 note)
  - loom-code/CHANGELOG.md (§94-96, §114-117 deferred)
  - loom-code/scripts/test_brainstorming_greenfield_nudge.py (§157-170 deferral assertion)
- Acceptance:
  - RED: test_brainstorming_greenfield_nudge.py updated to assert the pointer is "active" (not "deferred") → RED against current SKILL.md
  - GREEN: SKILL.md + CHANGELOG updated; test green; no remaining "Tier 2 — deferred" string for this wiring
- Dependencies: none
- Independent: true
- Brief item covered: "The Tier-2 'deferred' markers … describing this exact wiring as unbuilt — update/remove in the same change" (What Becomes Obsolete)

## Task 5 — manifest coherence: version bump + CHANGELOG entry + frontmatter align
- Description: Bump loom-code plugin.json version, sync root marketplace.json description
  (verbatim), add a keep-a-changelog entry for the spec→code wiring, align touched skills'
  frontmatter `version:` fields (P15-8 convention).
- Module: loom-code (plugin manifest + CHANGELOG)
- Files touched: loom-code/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, loom-code/CHANGELOG.md, loom-code/skills/writing-plans/SKILL.md, loom-code/skills/using-loom-code/SKILL.md, loom-code/skills/brainstorming/SKILL.md
- Context paths:
  - loom-code/.claude-plugin/plugin.json (current version 0.17.0)
  - scripts/check-marketplace-description-sync.py (sync gate)
  - loom-code/scripts/verify-drift.py (SSOT drift gate)
- Acceptance:
  - RED: `python3 scripts/check-marketplace-description-sync.py` + `python3 loom-code/scripts/verify-drift.py` clean AND CHANGELOG has a new dated entry for this change AND plugin.json version bumped above 0.17.0 — initially the new CHANGELOG/version entry is absent
  - GREEN: both gates green; version + CHANGELOG + frontmatter coherent
- Dependencies: Tasks 1, 2, 3, 4 complete first
- Independent: false
- Brief item covered: enabling change — manifest coherence for the Decision's two-part wiring (brownfield: "must not break existing Continuous mode")

## Task 6 — behavioral dogfood (per-Phase ritual)
- Description: Feed a small, real loom-spec change-folder (≥1 Requirement, ≥2 Scenarios)
  through writing-plans; confirm it produces a plan whose tasks trace to the scenarios via
  the generalized traceability field, and that Continuous-mode freeze recognizes the
  change-folder. Capture a dogfood note. Validates the wiring behaviorally (prose is the
  mechanism; this is the behavior check the marker tests cannot give).
- Module: loom-code (research/dogfood note)
- Files touched: loom-code/research/dogfood-2026-06-21-spec-to-code-wiring.md
- Context paths:
  - loom-spec/skills/spec-expansion/SKILL.md (to generate a sample change-folder)
  - docs/loom/plans/2026-06-21-spec-to-code-wiring.md (this plan, as the producer example)
- Acceptance:
  - RED: no dogfood record exists; wiring unproven end-to-end
  - GREEN: dogfood note shows (a) change-folder → writing-plans plan with scenario→RED/GREEN traceability via the stable join key, (b) **R3 coverage back-check — every `#### Scenario:` maps to ≥1 task** (OpenSpec `verify`-style), (c) freeze recognizes the change-folder via declared+presence+validator, (d) STOP/never-auto-merge unaffected
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: brownfield acceptance — "must not break existing Continuous mode"; R3 scenario→test coverage back-check; validates Decision §1+§2 behaviorally
