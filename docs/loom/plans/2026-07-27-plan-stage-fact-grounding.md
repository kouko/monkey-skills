# Plan: plan-stage fact grounding

**Source brief**: docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md
**Total tasks**: 10
**Critical-path depth**: 4 (≤5) — longest chain T1 → T2 → T7 → T8; levels are
{T1, T3, T4, T5a, T5b, T9} {T2} {T6, T7} {T8}
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: **PASS** (2026-07-27, round 3, 14/14, zero
gaps; three non-blocking notes, all three applied — see Notes → Post-PASS
amendment). Round history: round 1 NEEDS_REVISION
7/14, round 2 NEEDS_REVISION 11/14; all gaps fixed, see Notes → Review rounds.
Round 3 **exceeds writing-plans' 2-round cap and was explicitly authorised by
the user after escalation**, on the ground that the cap's stated diagnosis —
"likely the brief itself needs revisiting" — did not fit: all three round-2 gaps
were single-line fixes on one task and none traced to the brief.)

## Notes

- **Target repo**: `/Users/kouko/GitHub/monkey-skills`. All plugin edits land in
  `loom-code`. Package test command (from `.github/workflows/loom-code-ci.yml:94`):
  `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -v`.
- **Prose-artifact RED convention.** These are prompt/contract edits, not
  executable code. The repo's established pattern for making them TDD-testable
  is a structural grep-test under `loom-code/scripts/test_*.py` asserting the
  presence of load-bearing *phrases* (intent), tolerant of wording variation —
  see `loom-code/scripts/test_writing_plans_verdict_gate.py` and
  `loom-code/scripts/test_sdd_review_weight_marker.py` for the shape (both exist
  only under `loom-code/scripts/`, not the repo-root `scripts/`), including the
  docstring convention that states why phrase-presence is the correctness
  condition.
- **Why term-definition rides in the same test as the rule (T1/T2/T3).** The
  brief makes every new contract term carry an inline operational definition
  (brief:242, restated brief:72-76) *because* the reader may be a weak tier. An
  undefined term makes the rule non-executable, so "rule stated" and "terms
  defined" are one acceptance boundary, not two — one RED test per task, as the
  splitting framework requires.
- **No new command surface.** New tests live in `loom-code/scripts/`, already
  covered by the CI pytest invocation above. No `make`/`package.json` entry is
  added.
- **Check numbering is append-only.** `plan-document-reviewer-prompt.md:37`
  keeps a RETIRED Check 5 in place rather than renumbering, because other files
  cite check numbers literally (repo memory
  `retire-numbered-checks-dont-renumber.md`). T3 amends Check 8 in place and
  introduces no new number.
- **T5a/T5b duplication is intentional, not an SSOT violation.** The same
  conditional cross-read lands in two peer agent contracts because they run at
  different tiers (brief §Current State Evidence → Boundary). They are peer role
  contracts, not copies of a shared source; `distribute.py` does not sync
  `agents/` (brief §Reverse).
- **Review rounds (plan-document-reviewer, 2026-07-27).** Every reviewer claim
  below was independently re-verified against the repo before being accepted —
  none was taken on the reviewer's word.

  **Round 1 — NEEDS_REVISION, 7/14.** Five gaps, all fixed:
  - *Check 4* — old Task 5 declared a directory as `Module` and edited two
    contracts. Split into **T5a / T5b**, one contract each, separate test
    modules so both stay `Independent: true`.
  - *Check 6* — old T6's RED greped for "pre-change phrasing" of rules T1/T2
    **add**, so it could never be red. Replaced with a named, runnable test
    asserting the three READMEs' per-task field lists contain the new field
    (verified: the lists live at `README.md` / `README.ja.md` /
    `README.zh-TW.md` `:34-39` — the six field bullets; `:32` is the lead-in
    sentence).
  - *Check 7* — old T6's GREEN required a repo-wide grep to return zero, which
    is unsatisfiable: **verified 6 files** under `docs/loom/plans/` legitimately
    contain `additive and schema-safe`. Grep is now scoped to the three README
    paths with a literal pattern, and the self-certifying "or the task report
    names which rules needed no edit" escape clause is deleted.
  - *Check 8* — brief:242 ("Every term entering skill contract text carries an
    inline operational definition") mapped to no task. Now covered by T1/T2/T3
    as a second `Brief item covered` referent and asserted in their REDs. This
    is the dropped-obligation class the change exists to prevent, found in this
    plan.
  - *Check 9* — old T7's `Brief item covered` cited "brief §Users / repo
    convention" for the version bump. **Verified: `version`, `marketplace`,
    `bump`, `changelog` appear 0 times in the brief** — the referent was
    fabricated. Re-pointed at the real source (repo convention + CI gate) and
    explicitly labelled non-brief-derived.
  - *Note (citation off-by-one)* — T3 cited Check 8 at `:41`; **verified Check 8
    is at `:40`** (`:41` is Check 9). Corrected.
  - *Note (Check 15 advisory)* — T7's write set was open-ended, so the
    disjointness oracle could not be evaluated. Pinned (verified
    `sync_codex_manifests.py:50` writes `<plugin>/.codex-plugin/plugin.json`,
    which exists); T6 and T7 are now both `Independent: true`.
  - *Note (formatting)* — header and per-task fields converted to the schema's
    bold `**Field**:` form.

  **Round 2 — NEEDS_REVISION, 11/14.** Three gaps, **all on Task 7**, plus three
  notes. The round-1 "unsatisfiable GREEN" defect class did not recur in place —
  it reappeared at a *different site* (T6 → T7), exactly as repo memory
  `unifying-a-normalization-has-a-scope.md` predicts of fix rounds:
  - *Checks 6 and 7* — T7's RED/GREEN invoked `scripts/check_version_bump.py`
    with no arguments. **Verified**: `--base` and `--head` are required, so the
    bare call exits on `error: the following arguments are required: --base,
    --head` — red for the wrong reason, and red *after* the bump too. Replaced
    with the invocation CI actually uses (`.github/workflows/skill-structure.yml:305`).
  - *Check 9* — T7's referent declared the *absence* of brief traceability
    ("not brief-derived") rather than supplying it. Re-pointed using the repo's
    existing release-carrier form, **verified** at
    `docs/loom/plans/2026-07-07-loom-user-communication-overhaul-tasks.md:322`
    ("repo release conventions for shipped Smallest end state 1-4 (loom-pipeline
    carrier)") and `:337`. No fabrication needed — T7 genuinely is the release
    step for T1–T5b.
  - *Note (citation path prefix)* — the Notes cited the guard-test examples as
    `scripts/…`; **verified** they exist only at `loom-code/scripts/…`.
    Corrected above. This was the third citation error found in this plan, whose
    own subject is citation accuracy.
  - *Note (vacuous clause)* — T6's second Description clause and its
    corresponding GREEN grep targeted the T4 phrasing in the READMEs;
    **verified 0 occurrences** in all three, so the clause was already true
    before the task ran. Removed rather than kept as decoration.
  - *Note (count drift)* — "6 historical plans retain the phrase" counted this
    plan itself; the pre-existing count is **5**. T7's CHANGELOG clause said
    "six changes" against the brief's **five** contract edits (six is the
    file-level count after the T5a/T5b split). Both corrected.
  **Post-PASS amendment (round 3 PASS, three notes applied).** Recorded here per
  writing-plans §Amending a PASS plan. **Read this as a boundary case, not a
  routine skip**: two of the three are cosmetic, but the first changes what an
  implementer must assert, so it is *not* purely additive — and Task 4 of this
  very plan exists to replace this self-judged exemption with a closed list.
  Flagging it rather than burying it, and offering it as a concrete input to
  T4's list design:
  - *Semantic (not merely additive)* — T5a/T5b's RED conjunct "carries no
    unconditional verify-everything mandate" was **unsatisfiable as written**:
    verified `loom-code/agents/code-quality-reviewer.md:365` already carries
    one. Scoped to the added text, using the reviewer's own supplied wording.
    Under T4's proposed closed list this class would plausibly warrant
    re-review; it is applied here because the reviewer PASSED the plan with the
    conjunct present *and* supplied the exact fix.
  - *Cosmetic* — T7's Description said "six contract changes" where its GREEN
    said five; aligned on five brief items / six edited files.
  - *Cosmetic* — the Notes cited the README field list as `:32-39` while T6 said
    `:34-39`; both now `:34-39` (`:32` is the lead-in sentence). Fifth citation
    inconsistency found in this plan, and it was inside the section documenting
    the citation fixes.
  - *Reviewer note adopted beyond the gaps* — brief:242's inline-definition
    obligation is worded universally, and T4/T5a/T5b also add contract text.
    That did not fail Check 8 (the rule is ≥1 task), but leaving it would be the
    same dropped-obligation class one level down, so those three REDs now assert
    it too.

## Kickoff sweep result (2026-07-27, post-PASS, per `references/kickoff-briefing.md`)

Appetite read (§d): **no `docs/loom/PRINCIPLES.md` in this repo** (verified) →
default applies, brief every one-way-door hit.

One-way-door hits (§a Axis B): **zero.** Every task is a prose edit inside a
versioned plugin; reversal is a follow-up version, not a rewrite. No batched
briefing fires (§c).

Fork harvest (§b): two foreseeable implementation forks, both triaged **arm 1
(look-up — answer already on record)**, so both are recorded unbriefed:

```
Kickoff decision: T4's closed list — which amendment kinds may skip re-review → derive from the two researched precedents already on record, not invented fresh: GitHub/OpenSSF "dismiss stale approvals" (mechanical auto-dismissal on any change) and the JA design-review norm (human judgment permitted only when 判定基準 are fixed in advance). Net rule for the list: an amendment may skip re-review only if it changes no technical content — stamping the verdict, fixing a typo, filling a schema field. Anything touching Acceptance RED/GREEN, a cited fact, a Dependencies edge, or a task's scope re-reviews. This plan's own post-PASS amendment (Notes → Post-PASS amendment) is the worked boundary case: two cosmetic edits would skip, the T5a/T5b scoping edit would not.
Kickoff decision: T8's test tiers — which model tiers the cold read and adversarial round run at → both tiers spec-reviewer actually runs at per `subagent-driven-development/SKILL.md:182`: haiku (Integration/Mechanical tasks) and sonnet (Architecture tasks). Not opus — the brief's Decision section already scopes the Opus-5 self-verification guidance out of this slot, so testing at opus would answer a question nobody asked.
```

## Decision Log

- **T5 placement — resolved at kickoff.** Brief Open Question 2 left the
  reviewer undecided. Resolved to **both** `spec-reviewer` and
  `code-quality-reviewer` (now T5a / T5b).
- **Version bump target**: 0.38.0 → **0.39.0** (additive contract rules; no
  breaking change to the plan schema — existing plans without citations remain
  valid, since the rule applies to facts a plan *chooses* to state).

## Kickoff

Kickoff sweep (2026-07-27): **no one-way-door decisions.** Every change is a
reversible prose edit in a versioned plugin. Two forks were resolved before
dispatch, both recorded above:

1. **T5 placement** — resolved to **both** contracts: `spec-reviewer` is the
   agent whose contract is judging the artifact *against the plan text* (natural
   home) but runs at the weakest tier, so it needs the explicit instruction
   most; `code-quality-reviewer` is tier-protected on architecture tasks
   (`subagent-driven-development/SKILL.md:182` exception) and is where the one
   observed spontaneous cross-read happened. Cost of covering both is one
   sentence per file.
2. **Whether to plan the verification task at all (T8)** — the brief names a
   dogfood obligation, and the audit's #618 finding is precisely that a brief
   obligation which never became a task escapes. T8 is in the plan, not
   deferred.

## Task 1 — plan-format.md: pointer-not-copy rule for stated facts

- **Description**: Add a rule to the plan schema stating that any verifiable
  technical assertion in a plan (a number, a formula, a field list, a claim
  about existing behaviour) carries a `file:line` citation, or is explicitly
  marked an unverified assumption; a fact with no citable source means the
  source must be produced first (a probe, a test) and that is a task, not a
  sentence. Every term the rule introduces carries an inline operational
  definition.
- **Module**: `loom-code/skills/writing-plans/references/plan-format.md`
- **Files touched**: `loom-code/skills/writing-plans/references/plan-format.md`,
  `loom-code/scripts/test_plan_fact_grounding.py`
- **Context paths**:
  - `loom-code/skills/writing-plans/references/plan-format.md`
  - `loom-code/scripts/test_writing_plans_verdict_gate.py` (guard-test shape)
  - `docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md`
- **Acceptance**:
  - **RED**: new `loom-code/scripts/test_plan_fact_grounding.py::test_pointer_not_copy_rule_present`
    fails — it asserts `plan-format.md` states (a) the citation requirement,
    (b) the unverified-assumption escape, (c) the produce-the-source-first
    consequence, and (d) that each term the rule introduces ("verifiable
    technical assertion", "unverified assumption") is defined inline where it
    first appears.
  - **GREEN**: that test passes; `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -v`
    is green with no pre-existing test newly failing.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: (1) "**Pointer-not-copy rule** … any verifiable
  technical assertion in a plan … carries a `file:line` citation, or is
  explicitly marked an unverified assumption." (2) brief:242 — "Every term
  entering skill contract text carries an inline operational definition."

## Task 2 — plan-format.md: reuse-adequacy declaration field

- **Description**: Add a per-task field to the plan schema: a task instructed to
  reuse an existing helper states in one line whether that helper's behaviour in
  the new lane matches its behaviour in the old one, and why any difference is
  acceptable. The field name and its terms carry inline operational definitions.
- **Module**: `loom-code/skills/writing-plans/references/plan-format.md`
- **Files touched**: `loom-code/skills/writing-plans/references/plan-format.md`,
  `loom-code/scripts/test_plan_fact_grounding.py`
- **Context paths**:
  - `loom-code/skills/writing-plans/references/plan-format.md` (§Per-task block, `:42+`)
  - `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` (§3.7 A-2)
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_plan_fact_grounding.py::test_reuse_adequacy_field_present`
    fails — it asserts the per-task block documents a reuse-adequacy declaration
    covering the behaviour-match claim, the why-acceptable clause, and an inline
    definition of what counts as a behaviour difference.
  - **GREEN**: that test passes; package suite green.
- **Dependencies**: Task 1 completes first
- **Independent**: false  # same file as Task 1 — file serialization, not a semantic dependency
- **Brief item covered**: (1) "**Reuse-adequacy declaration** … a task instructed
  to reuse an existing helper states in one line whether that helper's behaviour
  in the new lane matches its behaviour in the old one." (2) brief:242 — inline
  operational definition requirement.

## Task 3 — plan-document-reviewer-prompt.md: obligation sweep in Check 8

- **Description**: Amend Check 8 in place (no renumbering) so the reviewer also
  greps the brief for obligation sentences and lists any not covered by a task.
  Define "obligation sentence" inline so a weak-tier reviewer can apply it
  without judgment.
- **Module**: `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`
- **Files touched**:
  `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`,
  `loom-code/scripts/test_plan_obligation_sweep.py`
- **Context paths**:
  - `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`
    (`:40` Check 8; `:37` RETIRED-in-place precedent)
  - `docs/loom/memory/retire-numbered-checks-dont-renumber.md`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_plan_obligation_sweep.py::test_check8_sweeps_brief_obligations`
    fails — it asserts Check 8 carries the obligation-sweep instruction, defines
    "obligation sentence" inline, **and** that the checks table contains no
    number above the current maximum (append-only guard: the amendment must not
    have introduced a renumber).
  - **GREEN**: that test passes; package suite green.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: (1) "**Obligation sweep** … grep the brief for
  obligation sentences and list any not covered by a task." (2) brief:242 —
  inline operational definition requirement.

## Task 4 — writing-plans/SKILL.md: closed list for post-PASS amendments

- **Description**: Replace the author's self-judged "additive and schema-safe"
  skip note at `SKILL.md:115` with an enumerated closed list of amendment kinds
  that may skip re-review; anything not on the list re-reviews.
- **Module**: `loom-code/skills/writing-plans/SKILL.md`
- **Files touched**: `loom-code/skills/writing-plans/SKILL.md`,
  `loom-code/scripts/test_post_pass_amendment_gate.py`
- **Context paths**:
  - `loom-code/skills/writing-plans/SKILL.md` (`:115` §Amending a PASS plan)
  - `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` (§4 P5)
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_post_pass_amendment_gate.py::test_skip_note_is_closed_list`
    fails — it asserts the section enumerates the permitted amendment kinds,
    states that anything outside the list re-reviews, defines each enumerated
    kind inline so a weak-tier reader can classify an amendment without
    judgment, and that the author-supplied self-justification phrasing is gone
    from **this file** (the 5 pre-existing historical plan documents that still
    contain the phrase are out of scope).
  - **GREEN**: that test passes; package suite green.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: (1) "**Closed list for post-PASS amendments** …
  replace the author's self-judged 'additive and schema-safe' skip note … with
  an enumerated list of amendment kinds that may skip re-review." (2) brief:242
  — inline operational definition requirement.

## Task 5a — spec-reviewer: conditional source cross-read

- **Description**: Add one conditional instruction to the spec-reviewer
  contract: when the plan text this task is judged against carries a source
  citation, open the cited source and confirm it says what the plan says.
  Worded as a trigger with an explicit no-op when no citation is present — not a
  blanket verification mandate.
- **Module**: `loom-code/agents/spec-reviewer.md`
- **Files touched**: `loom-code/agents/spec-reviewer.md`,
  `loom-code/scripts/test_spec_reviewer_source_crossread.py`
- **Context paths**:
  - `loom-code/agents/spec-reviewer.md`
  - `loom-code/skills/subagent-driven-development/SKILL.md` (`:182` tier assignment)
  - `docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md` (§Decision → model-generation scope)
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_spec_reviewer_source_crossread.py::test_spec_reviewer_carries_conditional_crossread`
    fails — it asserts the contract carries the if-a-citation-is-present
    condition, the open-and-compare action, the no-citation no-op, an inline
    definition of what counts as a source citation, and that **the added
    instruction** is worded as a trigger rather than an unconditional mandate.
    That last assertion is scoped to the added text only — pre-existing
    unconditional wording elsewhere in a contract is out of scope (verified:
    `loom-code/agents/code-quality-reviewer.md:365` already carries one, so an
    unscoped assertion would be unsatisfiable before and after the task).
  - **GREEN**: that test passes; package suite green.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: (1) "**Conditional cross-read at a reviewer that
  already reads both** — one added instruction, worded as a trigger, not a
  mandate." (2) brief:242 — inline operational definition requirement.

## Task 5b — code-quality-reviewer: conditional source cross-read

- **Description**: Same conditional instruction as Task 5a, in the
  code-quality-reviewer contract — the reviewer that is tier-protected on
  architecture tasks and where the one observed spontaneous cross-read happened.
- **Module**: `loom-code/agents/code-quality-reviewer.md`
- **Files touched**: `loom-code/agents/code-quality-reviewer.md`,
  `loom-code/scripts/test_code_quality_reviewer_source_crossread.py`
- **Context paths**:
  - `loom-code/agents/code-quality-reviewer.md`
  - `loom-code/skills/subagent-driven-development/SKILL.md` (`:182` tier exception)
  - `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` (§3.7 A-1)
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_code_quality_reviewer_source_crossread.py::test_code_quality_reviewer_carries_conditional_crossread`
    fails — same assertions as Task 5a (condition, action, no-op, inline
    definition of "source citation", and the added-instruction-is-a-trigger
    check **scoped to the added text**), against this contract. Scoping matters
    most here: `:365` of this file already carries an unconditional
    external-surface mandate that must be left alone.
  - **GREEN**: that test passes; package suite green.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: (1) "**Conditional cross-read at a reviewer that
  already reads both** … **Which reviewer carries it is open** (see Open
  Questions 2)" — resolved at kickoff to both contracts. (2) brief:242 — inline
  operational definition requirement.

## Task 6 — three-language README sync for the new per-task field

- **Description**: The three shipped writing-plans READMEs enumerate the
  per-task field list (`README.md` / `README.ja.md` / `README.zh-TW.md`,
  `:34-39` — six fields today). Add the reuse-adequacy field introduced by Task
  2 to all three. Scope note: the T4 closed-list phrasing is **not** quoted in
  any of the three READMEs (verified: 0 occurrences), so it needs no sync here.
- **Module**: `loom-code/skills/writing-plans/` (README family)
- **Files touched**: `loom-code/skills/writing-plans/README.md`,
  `loom-code/skills/writing-plans/README.ja.md`,
  `loom-code/skills/writing-plans/README.zh-TW.md`,
  `loom-code/scripts/test_writing_plans_readme_sync.py`
- **Context paths**:
  - `loom-code/skills/writing-plans/README.md`, `README.ja.md`, `README.zh-TW.md`
  - `docs/loom/memory/core-rule-removal-needs-plugin-wide-sweep.md`
- **Acceptance**:
  - **RED**: new
    `loom-code/scripts/test_writing_plans_readme_sync.py::test_readmes_list_reuse_adequacy_field`
    fails — it asserts each of the three READMEs' per-task field list contains
    the reuse-adequacy field. It is red before this task because Task 2 adds the
    field to the schema and the READMEs do not yet list it.
  - **GREEN**: that test passes; `python3 loom-code/scripts/check-skill-crossrefs.py`
    exits 0.
- **Dependencies**: Task 2 completes first
- **Independent**: true  # write set disjoint from T7's at the same level
- **Brief item covered**: brief §Current State Evidence → Boundary — sweep
  surface ("`plan-document-reviewer` is referenced in **17 files** including
  `skills/writing-plans/README.{md,ja.md,zh-TW.md}`").

## Task 7 — version bump 0.39.0 + CHANGELOG + Codex manifest sync

- **Description**: Bump the `loom-code` plugin version to 0.39.0, add the
  CHANGELOG entry describing the five contract changes from the brief's
  Smallest End State (six edited files — T5a/T5b split one brief item into
  two contracts), and run the Codex
  manifest sync so the mirrored manifest matches.
- **Module**: `loom-code/.claude-plugin/plugin.json`
- **Files touched**: `loom-code/.claude-plugin/plugin.json`,
  `loom-code/.codex-plugin/plugin.json`, `loom-code/CHANGELOG.md`
- **Context paths**:
  - `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`
  - `loom-code/CHANGELOG.md`
  - `scripts/sync_codex_manifests.py` (`:50` — writes `<plugin>/.codex-plugin/plugin.json`),
    `scripts/check_version_bump.py`
- **Acceptance**:
  - **RED**: `python3 scripts/check_version_bump.py --base "$(git merge-base origin/main HEAD)" --head HEAD`
    fails while the version is still 0.38.0 (skill content changed without a
    bump). `--base` and `--head` are **required** arguments — the bare
    invocation exits on an argparse error, which would be red for the wrong
    reason; this is the form CI uses
    (`.github/workflows/skill-structure.yml:305`).
  - **GREEN**: that same invocation exits 0; `plugin.json` reads 0.39.0;
    `python3 scripts/sync_codex_manifests.py --check loom-code` exits 0;
    `CHANGELOG.md` has a 0.39.0 entry naming the **five** contract changes from
    the brief's Smallest End State (T5a/T5b are one brief item split across two
    files); `python3 -m pytest scripts/ -v` green.
- **Dependencies**: Tasks 1, 2, 3, 4, 5a, 5b complete first
- **Independent**: true  # write set disjoint from T6's at the same level
- **Brief item covered**: Release carrier for Smallest End State items 1–5 —
  repo release convention requires a plugin version bump on any skill-content
  change, enforced by `scripts/check_version_bump.py`. (Referent form follows
  the repo's existing precedent at
  `docs/loom/plans/2026-07-07-loom-user-communication-overhaul-tasks.md:322,337`
  — "repo release conventions … carrier".)

## Task 8 — weak-tier verification of the new rules (cold read + adversarial)

- **Description**: Run the change's own verification, per repo memory
  `cold-read-and-adversarial-review-catch-different-failures.md`: a
  fresh-context cold read at the tier `spec-reviewer` actually runs at, and a
  separate adversarial round. The cold read tests whether a cooperative weak
  reader executes the conditional cross-read (T5a/T5b) and the pointer-not-copy
  rule (T1) correctly; the adversarial round tests whether a reader trying to
  route around them can satisfy the wording without doing the work.
- **Module**: `docs/loom/dogfood/` (new note; no plugin code changes)
- **Files touched**: `docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md`
- **Context paths**:
  - `docs/loom/memory/cold-read-and-adversarial-review-catch-different-failures.md`
  - `docs/loom/memory/process-mechanism-dogfood-via-coldreader-real-commits.md`
  - `docs/loom/memory/doc-string-tests-pass-while-weak-readers-misread.md`
- **Acceptance**:
  - **RED**: the dogfood note does not exist, so the brief's Open Question 3
    ("does the conditional trigger actually fire at sonnet/haiku?") is
    unanswered.
  - **GREEN**: the note exists and records, for each of the two rounds: the tier
    used, the exact task given, whether the reader performed the cross-read
    unprompted vs only after the instruction, and a verdict on whether the
    instruction is load-bearing at that tier. If the cold read shows the
    instruction is redundant at every tier tested, the note says so and
    recommends the brief's stated reversal (ship T1 alone, drop T5a/T5b).
- **Dependencies**: Tasks 1, 5a, 5b, 7 complete first
- **Independent**: false
- **Brief item covered**: Open Question 3 — "**Does the conditional trigger
  actually fire at sonnet/haiku?** This is the change's own verification task."

## Task 9 — record the PCE success criterion so the change is falsifiable

- **Description**: Add a BACKLOG entry defining the success measure: the share
  of planning-origin defects caught at plan review rather than at close-out
  (Phase Containment Effectiveness), in its cheapest viable form — classify only
  defects found at close-out, not every defect.
- **Module**: `docs/loom/BACKLOG.md`
- **Files touched**: `docs/loom/BACKLOG.md`
- **Context paths**:
  - `docs/loom/BACKLOG.md` (its header defines the entry format)
  - `docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md` (Open Question 1)
- **Acceptance**:
  - **RED**: `grep -c 'Phase Containment' docs/loom/BACKLOG.md` returns 0, so the
    change ships unfalsifiable.
  - **GREEN**: the BACKLOG carries an entry naming the measure, the cheap
    classification rule (close-out defects only), and the arcs it should be
    evaluated over.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Open Question 1 — "**How is success measured?**
  Proposed: Phase Containment Effectiveness … Without this the change ships
  unfalsifiable."
