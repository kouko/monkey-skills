# Plan: Reuse-adequacy declaration hardening

Source brief: docs/loom/specs/2026-07-31-reuse-adequacy-declaration-hardening.md
Total tasks: 6
Critical-path depth: 4 (≤5) — T1 → T3 → T5 → T6
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-01, round 2, 14/14)

## Task 1 — rewrite the `Reuse-adequacy` schema into two slots plus a source marker

- **Description**: Replace §`Reuse-adequacy` at `loom-code/skills/writing-plans/references/plan-format.md:141-147` and its field-list entry at `loom-code/skills/writing-plans/references/plan-format.md:57` with the two-slot block. `Observed` reports (present tense, existing code) and ends in a source marker from the pinned vocabulary in ## Notes; `Intended` specifies. There is no author-written adequacy field — the verdict belongs to the reviewer. State the malformed-block consequence verbatim from the pin, and route `unverified assumption` at the §Stated facts convention already at `loom-code/skills/writing-plans/references/plan-format.md:157-159` rather than inventing a parallel rule.
- **Module**: `loom-code/skills/writing-plans/references/plan-format.md`
- **Files touched**: `loom-code/skills/writing-plans/references/plan-format.md`, `loom-code/scripts/test_plan_fact_grounding.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/references/plan-format.md`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/test_plan_fact_grounding.py`
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-31-reuse-adequacy-declaration-hardening.md`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_plan_fact_grounding.py::test_reuse_adequacy_block_pins_two_slots_and_marker_vocabulary` fails against the current single-line schema
  - **GREEN**: the section names both slots, carries all three markers verbatim from the ## Notes pin, pins `<path>` as repo-relative, states the malformed-block consequence, and contains no author-side adequacy/justification field. The existing `test_reuse_adequacy_field_present` at `loom-code/scripts/test_plan_fact_grounding.py:230` still passes.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: "**Observed** (report — words answer to the code) … ending in a **source marker** from a closed vocabulary of exactly three" + "**Intended** (specification — code answers to the words)"

## Task 2 — mirror the new shape into the three READMEs

- **Description**: Update the `Reuse-adequacy` bullet at `loom-code/skills/writing-plans/README.md:39`, `loom-code/skills/writing-plans/README.ja.md:39` and `loom-code/skills/writing-plans/README.zh-TW.md:39` to describe the two-slot block and the obligatory marker. Each locale keeps its own language; the marker tokens themselves are transcribed verbatim from the ## Notes pin, never translated.
- **Module**: `loom-code/skills/writing-plans/README.md`
- **Files touched**: `loom-code/skills/writing-plans/README.md`, `loom-code/skills/writing-plans/README.ja.md`, `loom-code/skills/writing-plans/README.zh-TW.md`, `loom-code/scripts/test_writing_plans_readme_sync.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/README.md`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/README.ja.md`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/README.zh-TW.md`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/test_writing_plans_readme_sync.py`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_writing_plans_readme_sync.py::test_readmes_mirror_the_two_slot_shape` fails
  - **GREEN**: all three READMEs name both slots and carry the three marker tokens verbatim; the pre-existing `test_readmes_list_reuse_adequacy_field` at `loom-code/scripts/test_writing_plans_readme_sync.py:56` still passes
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "the three READMEs mirror the field list … Any field-shape change is a four-file edit"

## Task 3 — add Check 17 to the plan-document-reviewer

- **Description**: Append Check 17 to the checks table in `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`, with the four graded parts (a) presence, (b) marker, (c1) cross-read, (c2) adequacy, each carrying its own failure consequence. (c2)'s consequence states that a reuse whose semantics do not carry over is a `gaps` entry and never a `notes` entry, and that this holds even when the plan is internally consistent and every existing test passes. Check 17 is also the SSOT for the tier floor on (c2) — see ## Notes. Update the output contract's `checks_passed` denominator, the `check_id` range, and the verdict mapping so they stay consistent with the new check.
- **Module**: `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`
- **Files touched**: `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`, `loom-code/scripts/test_plan_document_reviewer_check17.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-31-reuse-adequacy-declaration-hardening.md`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_plan_document_reviewer_check17.py::test_check17_adequacy_failure_is_a_gap_not_a_note` fails (new file)
  - **GREEN**: Check 17 exists with all four parts; the (c2) row contains the gaps-not-notes consequence and the tier floor; `checks_passed`, the `check_id` range and the verdict mapping all name 17
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "one new `plan-document-reviewer` check with four graded parts" + "**(c2) carries a tier floor; (a), (b) and (c1) do not.**"

## Task 4 — add the matching spec-consistency checklist item

- **Description**: Add `CHK-SPEC-009: Reuse-adequacy Block in Plan Tasks [FIXABLE]` to `loom-code/skills/subagent-driven-development/checklists/spec-consistency.md`, following the shape of its sibling `CHK-SPEC-008` at `loom-code/skills/subagent-driven-development/checklists/spec-consistency.md:86`. It requires the block on any task whose Description instructs cross-call-path reuse, and requires the `Observed` slot to carry a marker from the pinned vocabulary. Transcribe the marker tokens verbatim from the ## Notes pin.
- **Module**: `loom-code/skills/subagent-driven-development/checklists/spec-consistency.md`
- **Files touched**: `loom-code/skills/subagent-driven-development/checklists/spec-consistency.md`, `loom-code/scripts/test_spec_consistency_reuse_adequacy.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/subagent-driven-development/checklists/spec-consistency.md`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_spec_consistency_reuse_adequacy.py::test_chk_spec_009_requires_the_source_marker` fails (new file)
  - **GREEN**: `CHK-SPEC-009` exists, is marked `[FIXABLE]`, names the block and the three marker tokens verbatim
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "and a matching `spec-consistency.md` item"

## Task 5 — point SDD's tier section at Check 17's floor

- **Description**: Add one pointer line to `loom-code/skills/subagent-driven-development/SKILL.md` beside the existing most-capable-tier exception at `loom-code/skills/subagent-driven-development/SKILL.md:161`, naming Check 17 (c2) as carrying its own tier floor and pointing at the reviewer prompt as SSOT. Do not restate the floor's value — point at it (repo point-don't-copy convention; a rule written in two places drifts).
- **Module**: `loom-code/skills/subagent-driven-development/SKILL.md`
- **Files touched**: `loom-code/skills/subagent-driven-development/SKILL.md`, `loom-code/scripts/test_plan_document_reviewer_check17.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/subagent-driven-development/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_plan_document_reviewer_check17.py::test_sdd_skill_points_at_check17_without_restating_the_floor` fails
  - **GREEN**: the pointer line sits beside the existing exception and names the reviewer prompt; the tier value itself appears in exactly one file
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Brief item covered**: "Where the tier floor is written … the SSOT choice is not obvious and the existing exception's placement is the precedent to follow"

## Task 6 — version bump, changelog, and the version pin this change trips

- **Description**: Bump `loom-code/.claude-plugin/plugin.json` from 0.42.4 to 0.43.0, add the matching `## [0.43.0]` entry to `loom-code/CHANGELOG.md` describing the schema change and the new check, and update the current-version pin at `loom-code/scripts/test_docs_review_blocking_class.py:200` (the test name embeds the version, so both the name and its two assertions change).
- **Module**: `loom-code/.claude-plugin/plugin.json`
- **Files touched**: `loom-code/.claude-plugin/plugin.json`, `loom-code/CHANGELOG.md`, `loom-code/scripts/test_docs_review_blocking_class.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/.claude-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/CHANGELOG.md`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/test_docs_review_blocking_class.py`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_docs_review_blocking_class.py::test_plugin_version_and_changelog_at_0_43_0` fails
  - **GREEN**: `plugin.json` reads 0.43.0, `CHANGELOG.md` carries `## [0.43.0]`, and the whole `loom-code` suite is green
- **Dependencies**: Tasks 2, 4, 5 complete first
- **Independent**: false
- **Brief item covered**: "**Shipping is part of this change, not a follow-up.** … a skill-content change without a `plugin.json` bump and its matching CHANGELOG entry is a silent no-op for every installed copy. The current-version pin at `loom-code/scripts/test_docs_review_blocking_class.py:200` tracks the shipping version by design, so it moves in the same change."

## Notes

Verdict stamped into the header after the round-2 PASS — stamping the verdict,
no re-review (writing-plans §Amending a PASS plan, kind 1).

### PIN — the marker vocabulary, canonical text

Four files must carry these three tokens (T1 schema, T2 READMEs, T3 Check 17,
T4 CHK-SPEC-009). **Every task transcribes them VERBATIM from this pin — never
from each other, never re-derived, never translated**, so each copy is
character-checkable against one source instead of judged for semantic closeness
(`docs/loom/memory/pin-shared-wording-in-plan-copies-transcribe-from-pin.md`).

```
read <repo-relative-path>:<line>
inferred from docstring
unverified assumption — <what would settle it>
```

Malformed-block consequence, also verbatim:

```
An absent marker, a marker outside this vocabulary, or an absolute path in the
`read` form makes the block malformed: the reviewer returns NEEDS_REVISION on
that ground alone and does not evaluate adequacy.
```

### Kickoff sweep (2026-08-01)

Appetite read: this repo has no `docs/loom/PRINCIPLES.md`, so the default applies
— brief every one-way-door hit. **The sweep found none.** Every design fork
(D over A and B, the tier floor, dropping the author-side adequacy field) was
decided and ratified during the brief; what remains is additive and reversible
by a small edit. A zero-hit sweep is a legitimate outcome, not a skipped step.

Three forks resolved by in-repo lookup (triage arm 1 — recorded, not briefed):

Kickoff decision: version bump level → 0.43.0 (minor). loom-code bumps minor for
schema/contract changes (0.39.0 plan-stage fact grounding, 0.41.0 finding
classes, 0.42.0 standalone skill) and patch for fixes (0.42.1-0.42.4); this is
a schema change plus a new reviewer check, so it sits with the minor group.
Kickoff decision: reviewer check number → 17, the next unused. Note it is
effectively permanent: this repo retires numbered checks in place rather than
renumbering (Check 5 is the standing precedent), so other files may cite 17 by
number from the moment it ships.
Kickoff decision: checklist item id → CHK-SPEC-009, the next unused, same
retire-in-place convention as the check numbers above.

### SSOT decisions

- **Tier floor on (c2)**: Check 17 in `plan-document-reviewer-prompt.md` is SSOT.
  T5 adds a pointer from SDD's tier section, never a second copy. Closes the
  brief's Open Question 5.
- **`unverified assumption`**: reuses `plan-format.md` §Stated facts rather than
  a parallel rule, so there is one convention for unverified assertions.

### Task 2's module boundary

`README.ja.md` and `README.zh-TW.md` are locale mirrors of the same bullet, kept
in lockstep by `loom-code/scripts/test_writing_plans_readme_sync.py:56`. They are
one artifact for splitting purposes; splitting per-locale would produce three
tasks that cannot be verified independently of each other.

### Parallel wave

T2, T3 and T4 sit at the same level below T1 with disjoint `Files touched`. They
have no semantic dependency on each other: each transcribes from the ## Notes pin
and from T1's schema, not from a sibling's output.

### Not in scope

Reviewer-side over-firing on a plausible-but-wrong declaration, and the
`unverified assumption` escape hatch, are both unmeasured (brief §Open Questions
6). They are follow-up arms, not tasks here.
