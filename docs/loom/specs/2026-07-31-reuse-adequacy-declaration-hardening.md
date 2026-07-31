# Brief — hardening the `Reuse-adequacy` declaration

- Date: 2026-07-31
- Origin: `docs/loom/audits/2026-07-31-a-class-interceptability-backtest.md` §候選 1 vs 候選 3 (candidate 3), reached from `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` §8.
- Status: **option D ratified by the user, 2026-07-31; validated across stages
  2a–2c the same day** (8 cells, frozen answer keys). Ready for `writing-plans`.
  One measured constraint rides with it: Check 17 `(c2)` must carry a tier floor
  — see §Smallest End State and §Measured.

## Problem

When a plan instructs an implementer to reuse an existing helper on a new call
path, the plan author needs to establish — before any code exists — whether that
helper's behaviour still holds there. The helper's own tests pass in its old
home, the new caller's tests pass in its slice, and neither crosses the seam;
the loss surfaces only in production or at close-out.

The plan format already asks the author to declare this. The declaration does
not do the job, for two separate reasons:

1. **Nothing enforces its presence.** A plan that omits it passes review.
2. **Nothing constrains its shape.** It is one line of free prose whose
   direction of fit is ambiguous — "whether the helper's behaviour in the new
   lane matches" reads equally as *a report about existing code* and as *a
   specification of intended code*. A live weak-tier author took the second
   reading and wrote a reassuring behaviour that the code does not have.

The job to be done is not "add a field". The field exists. It is: **make the
author's claim about existing behaviour into something a reader can check
without trusting the author.**

## Users

Plan-authoring agents running `writing-plans`, at haiku and sonnet tiers, under
`subagent-driven-development`; and the `plan-document-reviewer` that grades what
they produce. Job story: *when a plan task tells me to reuse a helper somewhere
new, I want to be forced to say what I actually looked at, so that a reviewer can
re-open it instead of taking my word.*

## Smallest End State

The `Reuse-adequacy` field becomes **two** author-written slots with opposite
directions of fit, and the adequacy judgement moves out of the plan entirely,
into the reviewer:

1. **Observed** (report — words answer to the code): what the helper does today,
   written in the present tense about code that already exists, ending in a
   **source marker** from a closed vocabulary of exactly three —
   `read <path>:<line>` / `inferred from docstring` / `unverified assumption`.
   An absent marker is a **malformed block**, not a smaller version of
   `unverified assumption`.
2. **Intended** (specification — code answers to the words): what the new call
   path will do with that behaviour.

The `read` marker's `<path>` is **repo-relative** — an absolute path resolves on
no other machine and `check_doc_citations.py` cannot bounds-check it. (haiku
emitted an absolute path in one 2a cell and a relative one in another, from the
same contract; the form has to be pinned, not left to chance.) The
`unverified assumption` marker reuses the convention `plan-format.md` §Stated
facts already ships — name what would settle it — rather than inventing a
parallel rule.

Plus the enforcement that is missing today — one new `plan-document-reviewer`
check with four graded parts:

- **(a) presence** — a reuse-instructing task without the block fails.
- **(b) marker** — an absent marker, a marker outside the closed vocabulary, or
  an absolute path in the `read` form fails **on that ground alone**; (c) is not
  evaluated.
- **(c1) cross-read** — when the marker is the `read` form, open that path at
  that line and confirm the source says what `Observed` claims.
- **(c2) adequacy** — does that behaviour remain correct on the call path
  `Intended` names? A reuse whose semantics do not carry over is a **`gaps`
  entry, never a `notes` entry**, even when the plan is internally consistent and
  every existing test passes — that combination is precisely how this defect
  class ships.

**(c2) carries a tier floor; (a), (b) and (c1) do not.** Measured: haiku executed
all three mechanical parts correctly in every reviewer cell, and had zero
discriminating power on (c2) — it answered "adequate" on both the defect and the
legitimate material, reaching the defect answer by fabricating a behaviour the
code does not have. The floor has precedent in this plugin:
`loom-code/skills/subagent-driven-development/SKILL.md:161` already carries a
most-capable-tier exception for one reviewer role on architectural tasks.

**A live instance of the defect, found in this brief.** The line above first
cited line 182 — the number `docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md`
cites for the same sentence. It was correct when that note was written and has
since drifted; the text now sits at line 161. `check_doc_citations.py` passed the
brief with an unqualified all-clear both times, because it bounds-checks that the
path resolves and the line exists — never that the line says what the citing text
claims. That gap is exactly what this change's `(c1)` sub-check exists to close,
and it was caught here only because a human-directed recon happened to open the
file. It is also the source audit's own argument for `§N` anchors over line
numbers, arriving unprompted.

Mechanising (c2) instead was considered and ruled out: "does this helper drop
information the new call path needs" is the un-greppable classification named in
`docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md`.

And a matching `spec-consistency.md` item.

**Shipping is part of this change, not a follow-up.** The schema, the three
READMEs, the new check and the checklist item are all skill content, and this
marketplace publishes by version — a skill-content change without a
`plugin.json` bump and its matching CHANGELOG entry is a silent no-op for every
installed copy. The current-version pin at
`loom-code/scripts/test_docs_review_blocking_class.py:200` tracks the shipping
version by design, so it moves in the same change.

**Design correction found while drafting the contract (2026-07-31)**: an earlier
sketch made the adequacy verdict a *third field in the plan*, filled by the
reviewer. That breaks `plan-document-reviewer`'s standing role contract — rule 2
of `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`
forbids it editing the plan. Putting the judgement in the reviewer's **check**
instead is both contract-legal and cheaper, and it buys the separate-context
property for free: the reviewer already is a context that did not write the
draft. No new agent, no new dispatch.

## Current State Evidence

**Every citation in this section describes the state BEFORE this change, pinned
at base commit `293d446c`.** Several no longer resolve to the content described
once the change lands — `loom-code/scripts/test_plan_fact_grounding.py:230` is
the clearest case: the test named there was retired by Task 1, so that line now
holds something else. Read this section with `git show 293d446c:<path>`, not
against the working tree. The section is a dated snapshot by design; leaving its
line numbers unqualified would reproduce, one document over, the drift this
change exists to catch.

- **Forward** — `writing-plans` authors a task; `loom-code/skills/writing-plans/references/plan-format.md:57` lists
  `Reuse-adequacy` in the per-task field list; `loom-code/skills/writing-plans/references/plan-format.md:141-147` defines
  it (v0.39.0+); `plan-document-reviewer-prompt.md` Checks 1–16 grade the plan.
- **Reverse** — `plan-format.md` §`Reuse-adequacy` is SSOT; the three READMEs
  mirror the field list at `loom-code/skills/writing-plans/README.md:39`,
  `loom-code/skills/writing-plans/README.ja.md:39`, `loom-code/skills/writing-plans/README.zh-TW.md:39`, pinned by
  `loom-code/scripts/test_writing_plans_readme_sync.py:56`. Any field-shape
  change is a four-file edit.
- **Error** — the absence path produces nothing. No check in
  `plan-document-reviewer-prompt.md` names the field, so a plan omitting it
  returns `PASS`. The nearest sibling, `loom-code/skills/subagent-driven-development/checklists/spec-consistency.md:86` (`CHK-SPEC-008`),
  covers `External surfaces` only. The only tests touching the field
  (`loom-code/scripts/test_plan_fact_grounding.py:230`,
  `loom-code/scripts/test_writing_plans_readme_sync.py:56`) assert the string appears in the
  document — the failure class named in
  `docs/loom/memory/doc-string-tests-pass-while-weak-readers-misread.md`.
- **Data** — the field carries one line of free prose and **no citation**.
  `spec-reviewer`'s conditional source cross-read (loom-code 0.39.0) fires only
  "when the plan text a task is judged against carries a source citation", so it
  has never fired on a `Reuse-adequacy` line. The mechanism is deployed and idle.
- **Boundary** — no script can decide *when* the field is required: "does this
  task instruct cross-lane reuse" is a classification in the reader's head, which
  `docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md` names as
  un-greppable. The trigger must stay with a reviewer; only the shape of a
  present field is mechanically checkable.

### Measured — stage 1 of the interception experiment (2026-07-31)

Fixture: a two-module sandbox reproducing the PR #619 A-2 shape, verified
mechanically rather than by eye — implementing the reuse exactly as instructed
leaves all 5 pre-existing tests green, and a timestamp whose two probes disagree
is stored as `{}` (both readings lost). Two cold cells, identical neutral
prompts, the shipped contract, `general-purpose` agent type:

| tier | grade | what it produced |
|---|---|---|
| haiku | **MISSED** | asserted the shapes match, then invented a behaviour — "the archive **will** record all results including skipped entries" — and rested the why-acceptable clause on it |
| sonnet | **PARTIAL** | "Behaviour does not fully match"; identified that a disagreeing timestamp needs a defined write outcome and refused a why-acceptable clause, but framed it as under-specification, never as *disagreement being the normal case here* |

The two cells differ in grammatical tense — haiku future (`will record`), sonnet
present (`has no older timestamp`) — which is the direction-of-fit ambiguity
showing up directly in the artifacts.

### Measured — stages 2a–2c, D's own contract (2026-07-31)

Every answer key was written and frozen **before** its cells were dispatched.
Eight cells total, `general-purpose`, neutral prompts identical within each arm.

| Stage | Subject | Material | haiku | sonnet |
|---|---|---|---|---|
| 1 | author, shipped contract | defect | MISSED — fabricated | PARTIAL |
| 2a | author, D | defect | **CAUGHT** | **CAUGHT** |
| 2a | author, D | legitimate | CLEAN | CLEAN |
| 2b | reviewer, Check 17 | defect | MISSED — fabricated | **BLOCKED-RIGHT** |
| 2c | reviewer, Check 17 | legitimate | PASS-RIGHT | **PASS-RIGHT** |

**The finding that outranks "does D work".** Line up the three haiku cells that
asked for a *judgement*: as author under the old contract it invented "the
archive **will** record all results including skipped entries"; as reviewer on
Check 17 (c2) it invented "disagreements **are recorded with reason**". Both are
false — a `{"skipped": …}` result has no `celsius` and nothing is stored
(mechanically probed: `{}`). Between them sits stage 2a, where D took the
judgement out of the author's job and the same tier wrote the truth.

**The fabrication tracks the judgement, not the seat.** Moving the verdict to a
different agent buys independence, not competence.

What that reframes D as: D does not make a weak model judge. It **separates the
mechanical from the judgemental**, so the mechanical steps hold at every tier —
haiku executed presence (a), marker form (b), and the source cross-read (c1)
correctly in every reviewer cell — and the un-delegatable residue is compressed
into one named sub-check, `(c2)`, which can be tier-pinned. Before D, one line of
free prose mixed the two and a single fabrication contaminated all of it.

**Discrimination, measured.** On `(c2)`, haiku answered "adequate" on both
materials — zero discriminating power. sonnet answered "not adequate" on the
defect and "adequate" on the legitimate case, each with correct and specific
reasoning (on the defect it additionally found a *structural* impossibility the
answer key had not: the merged value carries no `sensor` key, and
`archive_reading` keys its series by exactly that).

**Limits — read before citing any of this.**

- **n = 1 per cell.** "2/2" is two observations, not a rate. This clears the
  minimum bar for shipping a prose contract (the 2026-07-27 precedent), nothing
  more.
- One synthetic defect shape (the #619 A-2 analog). No evidence about other
  reuse-defect classes.
- The over-firing arm used an **accurate** declaration. A plausible-but-wrong
  declaration on legitimate material is untested.
- The `unverified assumption` marker was never exercised — all eight cells had
  the source in front of them and read it. Its escape-hatch behaviour is
  unmeasured.
- Stage 2c's fixture carried a residue of the path-normalisation script (Task 5
  named `python -m fixture-legit.page` against Module `fixture/page.py`). sonnet
  caught it and correctly filed it as a note, not a gate failure; it did not
  touch Check 17.

Fixtures, frozen answer keys, and verbatim outputs: session scratchpad
`cand3-exp/`. **Not durable** — re-create from this brief if needed.

## Decision

Build **the split-slot declaration with an obligatory source marker, judged by
the reviewer rather than the author** (option D below), together with the
presence enforcement that options A and D share. **Ratified by the user
2026-07-31**, on the reasoning that D is the only option that converts the
author's word into something a third party can re-open, at a cost of one token
rather than one test.

What we will NOT build: a mechanical trigger for *when* the field applies (the
Boundary evidence rules it out); a requirement that the author write a failing
test at plan time (option B — a plan-stage promise about a not-yet-existing test
is unverifiable, which is the property we are trying to buy); multi-sample voting
on the declaration.

Why D over A and B is argued in §Alternatives.

## Alternatives Considered

Research round: EN + JA, 2026-07-31. Sources listed per claim.

| | A — presence enforcement only | B — name a discriminating input + a RED | D — split slots + source marker + separate context |
|---|---|---|---|
| Field content | unchanged (free prose) | ①divergent input ②`path::test` that goes RED ③why-acceptable | ①Observed + source marker ②Intended ③verdict elsewhere |
| Catches the haiku failure? | no — the invented clause satisfies it | partly | yes — the invention lives in slot 1, where the marker forces a checkable source |
| Author burden | none | a test per reuse task | one closed-vocabulary token |
| Reversibility | two-way | one-way-ish (existing plans all become non-conformant) | two-way for slots; the marker vocabulary is additive |

**Three independent lines converge on the same defect in a self-answered
declaration**, which is what moved the recommendation off the earlier
"two closed questions" proposal (option C, now absorbed into D's third slot):

- **Austin, *How to Do Things with Words* (1962)** distinguishes a **misfire**
  (procedure not properly executed → the act is null and void) from an **abuse**
  (procedure executed but the sincerity condition violated → the act stands but
  is defective). The haiku cell is an abuse: form complete, sincerity condition
  broken. A sincerity condition is internal to the speaker, so no rewording of
  the field can make it externally visible.
- **Chain-of-Verification** (Dhuliawala et al., arXiv 2309.11495; ACL Findings
  2024) drafts, plans verification questions, answers them **independently**, then
  revises. Its **Factored** variant — plan *and* answer in independent contexts —
  exists precisely because otherwise the model repeats its original reasoning.
  A declaration whose author also judges it is the weakest (Joint) variant.
- **Verifier-pattern practice**: the generating role must not be the approving
  role, across distinct agents/sessions/models; same model + same context window
  yields self-confirmation, and the mitigation is to break the shared context
  between maker and checker.

**Direction of fit** (Anscombe, *Intention*, 1957 — the shopping-list/detective
pair; the term is Searle's) is what diagnoses the haiku artifact specifically: the
current wording lets one slot mean both *report* and *specification*, and the two
tiers split on exactly that, visible in their tense.

**Obligatory evidentiality** (Aikhenvald, *Evidentiality*, OUP 2004) supplies the
marker's design property: in languages where evidentiality is grammaticalised —
Turkish, Tibetan, Bulgarian, Quechua, Tariana, Korean — **the absence of an
evidential marker makes the sentence unacceptable**, not merely incomplete.
Japanese is not among them (an earlier claim in this arc, withdrawn). Japanese
industry guidance reaches the same rule from practice — 「根拠・出典の提示を『任意』
でなく『必須』にする」, with an explicit 【未確認・要確認事項】 slot.

**Caveat carried into the design**: forcing inline citations reduces unsupported
claims but models pick a plausibly-related span over the actually-supporting one.
So the marker is only worth its cost because `spec-reviewer`'s cross-read already
exists to open what the marker points at — the marker gives the deployed
mechanism something to bite on.

**Rejected**: multi-sample majority voting over the declaration
(self-consistency, Wang et al. 2022). Real gains on reasoning benchmarks, but
recent work reports diminishing returns and rising costs on modern models, and
it does not address direction-of-fit ambiguity at all.

## What Becomes Obsolete

- The single free-prose `Reuse-adequacy` line at `loom-code/skills/writing-plans/references/plan-format.md:141-147` — it is
  replaced, not extended; leaving both shapes documented would give authors a
  compliant way to keep writing the ambiguous form.
- `test_reuse_adequacy_field_present` in
  `loom-code/scripts/test_plan_fact_grounding.py` — **retired**. It pinned the
  retired field's vocabulary (`behaviour-match claim`, `why-acceptable clause`,
  and an inline definition of `behaviour difference`), none of which survives
  this change. Its one surviving property — that the per-task block names a
  `Reuse-adequacy` field — moves into the new behavioural test rather than being
  dropped.
- `test_readmes_list_reuse_adequacy_field` in
  `loom-code/scripts/test_writing_plans_readme_sync.py` — **stays**. It genuinely
  pins mirror-sync across the three locales, which is still true after the field
  changes shape.
- Nothing else.

**Correction (2026-08-01, reviewer-driven).** This section first read: *"Nothing
else. The two doc-string tests stay (they pin mirror-sync, which is still true);
they gain a behavioural sibling rather than being deleted."* That justification
was **false when it was written** — only the readme-sync test pins mirror-sync;
the other pinned the retired vocabulary, so "still true" never applied to it.
Task 1's code-quality reviewer found the consequence first (the test stayed green
only by keeping the retired vocabulary alive in a historical paragraph, and its
own docstring had become inaccurate); its spec-reviewer sibling then enforced the
sentence's letter and blocked the correct fix. The two verdicts pointing opposite
ways is what localised the defect to this sentence rather than to the artifact.

Recorded here rather than silently overwritten: a brief-level fact that was false
and carried faithfully downstream is the exact defect class this change exists to
intercept. This one was caught by the gate, not at close-out.

## Out of Scope

- Candidate 6 (institutionalising implementer refusal) — disjoint from this
  change; tracked in `docs/loom/BACKLOG.md`.
- Candidates 2 / 4 / 5 from the source audit §8 — never evaluated; any overall
  ordering needs them assessed together.
- The `External surfaces` field, and `CHK-SPEC-008` — sibling shape, not touched.
- Retro-fitting existing plans in `docs/loom/plans/`.

## Open Questions

1. ~~The decision above is a recommendation, not a ratification.~~ **Closed
   2026-07-31 — the user picked D.** `writing-plans` still waits on the stage-2
   result: D's contract wording is the experiment's treatment variable, so
   building it before measuring it would ship an untested wording.
2. ~~Stage 2 tests D, not C.~~ **Closed 2026-07-31 — stages 2a, 2b and 2c ran;
   see §Measured.** C was falsified by the research before it was run, so running
   it would have spent four cells on a superseded treatment.
3. ~~Whether the over-firing arm runs at both tiers.~~ **Closed — both, stage
   2c. No over-firing at either.** The haiku cell is weak evidence on its own:
   that model answered "adequate" on both materials, so its correct answer here
   may be the same bias landing right rather than judgement. The sonnet cell —
   the tier the floor pins — is the load-bearing one.
4. **Still open.** sonnet already reaches the motivating case under the *shipped*
   contract (stage 1, PARTIAL). If plan authoring and plan review both run at
   sonnet or above in practice, this change's value narrows to the weak-tier
   case. Worth weighing before the build, and it is the user's call — it turns on
   how the tiers are actually dispatched, not on anything measured here.
5. Where the tier floor is written: a Check-17 clause, a line in
   `subagent-driven-development/SKILL.md` beside the existing exception, or both.
   Task for `writing-plans`; the SSOT choice is not obvious and the existing
   exception's placement is the precedent to follow.
6. Untested and worth a later arm: the `unverified assumption` escape hatch
   (never exercised in 8 cells), and a plausible-but-wrong declaration on
   legitimate material.

## Evidence paths

- `loom-code/skills/writing-plans/references/plan-format.md`
- `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`
- `loom-code/skills/subagent-driven-development/checklists/spec-consistency.md`
- `loom-code/scripts/test_plan_fact_grounding.py`
- `loom-code/scripts/test_writing_plans_readme_sync.py`
- `loom-code/CHANGELOG.md` (0.39.0 entries)
- `docs/loom/audits/2026-07-31-a-class-interceptability-backtest.md`
- `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` §3.7, §8
- `docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md`
- `docs/loom/memory/a-shared-helper-can-be-right-in-one-lane-and-destructive-in-another.md`
- `docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md`
- `docs/loom/memory/pipeline-enforced-gates-beat-drafter-instructions.md`
- `docs/loom/memory/doc-string-tests-pass-while-weak-readers-misread.md`

## External sources

- Austin, J. L. (1962) *How to Do Things with Words* — felicity conditions;
  misfire vs abuse. <https://plato.stanford.edu/entries/speech-acts/>
- Anscombe, G. E. M. (1957) *Intention* — shopping list / detective; "direction
  of fit" is Searle's term for it.
  <https://www.oxfordreference.com/display/10.1093/oi/authority.20110803095720376>
- Aikhenvald, A. Y. (2004) *Evidentiality*, OUP — obligatory evidentiality; a
  missing marker renders the sentence unacceptable.
- Dhuliawala, S. et al. (2023) *Chain-of-Verification Reduces Hallucination in
  Large Language Models*, arXiv 2309.11495 / ACL Findings 2024 — Factored
  variant. <https://arxiv.org/abs/2309.11495>
- Wang, X. et al. (2022) self-consistency — rejected; see arXiv 2511.00751 on
  diminishing returns.
- Verifier pattern (generator ≠ approver, break the shared context).
  <https://www.mindstudio.ai/blog/verifier-pattern-multi-agent-systems-independent-review>
- Structured inline citation grounding + the plausibly-related-span caveat.
  <https://arxiv.org/html/2606.07130> · <https://zeroentropy.dev/concepts/citation-extraction/>
