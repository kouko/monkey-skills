# `write-spec` complexity-control dogfood — rounds 1–12

- **Date:** 2026-09-10 to 2026-09-11
- **Status:** completed research through round 12; no production skill, template, checker, or
  workflow change authorized by this record
- **Question:** can a small stage-local rule prevent `write-spec` completeness
  checks from expanding a confirmed intent into unnecessary Requirements,
  flows, decisions, tasks, or implementation detail?
- **Decision:** stop prompt tuning after round 8. Keep the structural findings;
  do not ship any complete candidate from these rounds.

## Executive conclusion

The experiments falsified the idea that a better necessity sentence or role
description is enough.
Generic minimality advice, owner-first justification, source/consequence tests,
and an explicit neutral failure fallback all remained vulnerable to
self-justification or semantic merging. Each new sentence reduced one observed
failure mode but moved discretion into the next free-prose carrier.

Template structure produced the first large, repeatable improvement:

- CRUD Requirement counts changed from `3, 9` to `3, 3`;
- Web-accessibility Requirement counts changed from `2, 4` to `2, 2`;
- explicit Constraint mapping prevented the password-reset preservation
  omission observed in round 4;
- a compact Constraint list was materially smaller than a three-column table;
- constraining `Design decision` removed ARIA/DOM mechanism leakage in both Web
  repetitions;
- one-operation-per-flow reduced CRUD flow carriers from `6, 9` to `3, 4`.

The complete template still did not pass. In round 8, one of two runs grouped a
request failure with validation errors and incorrectly inherited the
Acceptance-owned “beside the edited field” presentation. Both independent
reviewers found the same defect under reversed labels. This met the predeclared
stop condition: do not add another prose exception.

Rounds 9 and 10 tested two later hypotheses. PM/engineer role boundaries kept
plan task counts and architecture small but did not stop a plan from resolving
a product gap it had just named. A distinct post-draft self-check did remove
the earlier unsupported failure-placement inheritance, but overcorrected: it
expanded the Requirement set from the baseline's `3, 4` to `5, 6` and weakened
the source-supported neutral obligation to report request failure while leaving
state unchanged. The failure moved from unsupported specificity to fragmented
or incomplete carriers.

Round 11 tested the proposed hybrid directly: a closed scope envelope, an
explicit coverage contract, one Requirement group per Acceptance, sourced
Scenarios, and a silent post-draft reducer. It did not pass. Both reversed-
label reviewers failed both arms on the routine case; the candidate still
invented a reload-failure report in one run and narrowed the keyboard
Constraint in the other. On the adversarial CRUD case, both reviewers passed
the baseline arm and failed the candidate arm: one candidate run lost the
explicit rule that deletion occurs only after request success, and both wrote
success Scenarios whose trigger also matched failed requests. Rendering the
scope and coverage model also increased artifact size by 23–52% in these
samples and duplicated obligations across four carriers.

The supported direction remains a small hybrid, not a new Loom station:

1. use the existing `spec.md` template to own deterministic output shape;
2. extend an existing checker rule only for facts it can recompute exactly,
   such as Acceptance-to-Requirement cardinality and pointer coverage;
3. keep semantic source-altitude judgments in the single closing review;
4. if a post-draft reducer is pursued, constrain it inside the existing one-
   Requirement-per-Acceptance skeleton; replace unsupported specificity with
   source-supported neutral wording instead of creating another Requirement;
5. do not persist a per-probe audit ledger or import Ponytail's full decision
   ladder into `write-spec`.

Round 11 narrows item 1 further: do not add a rendered scope-envelope plus
coverage-contract pair to the production spec as drafted. If a coverage model
is tested again, keep it internal or collapse it into the existing Requirement
and Constraint carriers; it must not become two more copies of the contract.

This direction remains a proposal. None of rounds 1–11 is a production
authorization, and cross-model portability was not tested.

## Why this research started

The original `write-spec` completeness pass asked ten broad questions. Several
questions mixed discovery with authorization: once a check suggested an empty,
loading, failure, accessibility, quality, or actor/object concern, an executor
could turn the suggestion into a new Requirement even when confirmed
Acceptance did not require it.

The preceding source audit concluded that the number ten had no authoritative
basis and separated the checklist into:

- four universal requirement-set checks;
- interaction probes enabled only for an actual interaction surface;
- risk probes enabled only by an observed trigger;
- an admission rule intended to prevent a probe from authoring scope.

This dogfood tested whether the admission and minimality boundary changed
actual executor behavior.

## Research questions

1. Does the candidate reduce unnecessary Requirement, UI-flow, alternative,
   task, file, dependency, or owner expansion relative to the current wording?
2. Is the reduction repeatable across two executions of the same input?
3. Does simplification preserve confirmed Acceptance, explicit Constraints,
   and concrete security, accessibility, retention, and data-loss invariants?
4. Does complexity disappear, or merely move into another section?
5. Can the result remain inside `write-spec` without adding a workflow node or
   artifact type?

## Fixed method

### Arms and isolation

Each candidate was stored outside the production skill tree. Formal Loom files
were kept clean during execution. A candidate changed only the wording or
template surface named for that round. Later rounds reused earlier outputs only
when the changed text could not affect the preserved case dimension.

### Executors and reviewers

- Fresh Claude Sonnet sessions generated proposed specs from the complete raw
  skill package and a fixed fixture.
- Claude Opus sessions independently reviewed blinded, case-local packages.
- Reviewer A saw one LEFT/RIGHT order; Reviewer B saw the reverse.
- Neutral prompts explicitly named which arm to grade without disclosing which
  was candidate or comparison.
- Codex launched every Claude executor and reviewer through a sandbox-external
  runner, per the experiment's trust boundary.
- A skipped, truncated, conditional, or disagreeing reviewer could not be
  converted into PASS.

### Cases

| Case | Purpose | Must preserve |
|---|---|---|
| CRUD labels | ordinary UI with validation, request failure, and destructive deletion | three Acceptance lines; existing panel/modal; typed-value preservation; confirmation; unchanged data on request failure; no invented surfaces |
| ZIP import | legitimate high security complexity | path containment; absolute and `..` rejection; all symlink entries; duplicate/conflicting paths; 1,000 members; 100 MiB expanded data; nested archives; no overwrite; cleanup |
| Web sign-in errors | declared accessibility scope plus unchanged behavior | announcement; visible association; focus movement; WCAG 2.2 AA on changed behavior only; authentication, password-reset link, layout, and successful sign-in preserved |

### Pass rule

The compared arm passed a case only when all conditions held:

1. every Acceptance, Constraint, and named invariant remained explicit and
   testable in the proposed spec itself;
2. no scored expansion category increased in either paired repetition;
3. the improvement was repeatable within the arm;
4. both independent reviewers returned unconditional PASS.

A shorter artifact did not pass by size alone. Required security and
accessibility complexity was allowed when it remained source-bound and
testable.

## Round-by-round results

| Round | Candidate boundary | Result | What was learned |
|---|---|---|---|
| 1 | short stage-local minimality advice in `write-spec` and `write-plan` | FAIL | Current behavior already rejected obvious expansion in the primary case; no repeatable benefit. One run weakened a permanent-retention invariant, and the plan ladder did not reduce task expansion. |
| 2 | before adding an item, name the existing Requirement or owner that cannot carry it | FAIL | A self-authored gap is not evidence. Executors invented a policy, resume hook, owner, task, or module and then used the requested sentence to justify it. |
| 3 | bind every gap to Source, counterfactual Consequence, and Minimal carrier | FAIL, materially better | The completed reviewer preferred the candidate in all six cases and all twelve paired runs, but one Web run still split focus visibility into an extra Requirement and another leaked an ARIA mechanism. A monolithic review bundle also exceeded a reviewer's turn budget. |
| 4 | add a set-level merge pass after admission | FAIL | Web's two round-3 defects were fixed and ZIP passed, but identical CRUD runs produced 3 and 9 Requirements. “Independently verifiable” was too permissive. One Web run discussed but failed to preserve the password-reset Constraint inside the spec. |
| 5 | template: exactly one Requirement per Acceptance plus a three-column Constraint coverage table | FAIL, structural improvement | CRUD stabilized at 3/3 and Web at 2/2; all explicit Constraints survived. Complexity moved into `Design decision`, including ARIA/DOM mechanisms, and the coverage table added recurring ceremony. |
| 6 | compact Constraint list and mechanism-free `Design decision` | FAIL, narrower | Web passed both reviewers; ZIP preservation passed; spec size fell. CRUD reviewers disagreed because UI flows still varied from 6 to 9 lines. |
| 7 | one UI-flow line per Acceptance-owned operation; separate line only for a distinct user action | FAIL | Flow carriers stabilized at 3/4, where the fourth was cancel. Both reviewers found an unsupported presentation choice: request failures were assigned to fields or modal-dismissal behavior. |
| 8 | repository-evidence-only failure must use neutral “reports failure and leaves state unchanged” wording | FAIL; stop condition reached | Run 2 complied. Run 1 merged request failure with validation errors and inherited their field placement. Both reversed-label reviewers found the same bypass. More prose is not justified. |
| 9 | opening PM boundary for `write-spec` and engineer boundary for `write-plan`, tested with isolated and same-session handoffs | FAIL, partial architecture benefit | Candidate plans stayed at three tasks and invented no architectural owner, but product gaps were still silently resolved, Constraints or cancellation coverage drifted, and same-session flow structure varied. Role text is orientation, not enforcement. |
| 10 | same writer drafts, then audits every clause as KEEP / OPEN / MOVE / DROP before final output | FAIL, useful semantic signal | Both runs stopped inheriting rename-only placement for create and preserved the complete Constraint, but Requirements expanded to 5/6 and the neutral sourced request-failure obligation was weakened. Post-draft reduction can find the defect, but its carrier rule was wrong. |
| 11 | closed scope envelope + coverage contract + Acceptance-owned Requirement groups + sourced Scenarios + silent reducer | FAIL, structural signal only | The candidate stabilized top-level groups and exposed ownership, but still invented routine failure behavior, narrowed a Constraint, lost an explicit delete ordering invariant in one CRUD run, and produced overlapping success/failure triggers. Both reversed-label reviewers preferred the CRUD baseline. |
| 12 | PM boundary + one existing `REQ-n` owner group per Acceptance + unnumbered clauses + deletion-only post-draft pass; no new IDs, checker, or review station | FAIL, positive low-cost signal | Both reviewers passed the candidate on the routine case and preferred it on the CRUD case, but both candidate CRUD runs retained overlapping create/rename success and request-failure triggers; one run also invented modal closure on cancel. Phase B plan handoff was not run because the spec-only gate failed. |

## Quantitative progression

The comparable measurements below count the proposed spec artifact, excluding
trajectory commentary.

| Stage | CRUD REQs | Web REQs | CRUD UI-flow lines | CRUD words | Web words |
|---|---:|---:|---:|---:|---:|
| Round 4 prose candidate | 3, 9 | 2, 4 | not normalized | 697, 1011 | 639, 746 |
| Round 5 first template | 3, 3 | 2, 2 | 3, 3 | 799, 817 | 598, 609 |
| Round 6 compact template | 3, 3 | 2, 2 | 6, 9 | 613, 630 | 385, 358 |
| Round 7 flow-bound template | 3, 3 | reused | 3, 4 | 493, 573 | reused with focused PASS |
| Round 8 neutral fallback | 3, 3 | reused | structurally stable | not used as pass evidence | reused |
| Round 9 role boundary, isolated | 4, 3 | not rerun | varied | not used as pass evidence | not rerun |
| Round 9 role boundary, same session | 3, 3 | not rerun | 12, 8 | not used as pass evidence | not rerun |
| Round 10 post-draft self-check | 5, 6 | not rerun | 10, 10 | not used as pass evidence | not rerun |

Round 11 used a new routine fixture plus the adversarial CRUD fixture, so its
size measurements are reported separately rather than mixed into the earlier
progression:

| Round 11 arm | Routine groups / clauses | Routine words | CRUD groups / clauses | CRUD words | Blind verdict |
|---|---:|---:|---:|---:|---|
| baseline run 1 | 10 / 10 | 583 | 3 / 13 | 592 | routine FAIL; CRUD PASS |
| baseline run 2 | 7 / 7 | 517 | 3 / 13 | 576 | routine FAIL; CRUD PASS |
| candidate run 1 | 2 / 9 | 760 | 3 / 10 | 873 | routine FAIL; CRUD FAIL |
| candidate run 2 | 2 / 7 | 634 | 3 / 11 | 837 | routine FAIL; CRUD FAIL |

The candidate's top-level group cardinality was stable, but the rendered scope
envelope, coverage contract, Requirement Scenarios, Constraint index, and UI
flows repeated the same obligations. Candidate word count rose 30% and 23% on
the two routine pairings, and 47% and 45% on the two CRUD pairings.

Round 12 removed the rendered scope envelope, coverage contract, Scenario IDs,
and source tags. It retained only the existing `REQ-n` IDs and used unnumbered
clauses inside one Acceptance-owned group:

| Round 12 arm | Routine groups | Routine words | CRUD groups | CRUD words | Blind verdict |
|---|---:|---:|---:|---:|---|
| baseline run 1 | 2 | 300 | 10 | 493 | routine FAIL; CRUD FAIL |
| baseline run 2 | 3 | 323 | 10 | 548 | routine FAIL; CRUD FAIL |
| candidate run 1 | 2 | 199 | 3 | 467 | routine PASS; CRUD FAIL |
| candidate run 2 | 2 | 225 | 3 | 419 | routine PASS; CRUD FAIL |

Relative to its paired baseline, the candidate was 30–34% shorter on the
routine case and 5–24% shorter on CRUD. Both reversed-label reviewers agreed
that the candidate was safer in both cases. Size and stable owner cardinality
therefore improved without adding identifiers, but neither property was
sufficient for semantic correctness.

The round-5 CRUD word increase is important: a stable carrier count can still
cost more prose when a coverage table and free-form decisions duplicate the
same content. Round 6 removed that cost without losing Constraints.

## Findings that survived adversarial testing

### Supported

#### Structure is stronger than advice for cardinality

The same-model variance that produced 3/9 and 2/4 Requirements disappeared
when the output skeleton allocated exactly one Requirement slot per confirmed
Acceptance. This effect survived subsequent rounds.

#### Constraints need an explicit carrier

Merely discussing an excluded item in trajectory does not preserve an
unchanged invariant in the artifact. A compact one-line-per-Constraint index
preserved the Web authentication, password-reset, layout, success-path, and
WCAG boundaries in repeated outputs.

#### Compact lists dominate coverage tables here

The three-column table made preservation visible but repeated full Constraint
text and created permanent ceremony. The compact list retained the mapping and
reduced Web specs by roughly two hundred words in these samples.

#### Free prose is where complexity migrates

Across rounds, expansion moved from Requirements to Design decisions, then to
UI-flow carrier count, then to unsourced presentation inside a flow. Any design
that measures only Requirement count will miss this displacement.

#### Safety complexity must be preserved, not minimized away

The ZIP case repeatedly showed that multiple security controls can share one
Acceptance-owned Requirement without being omitted. The criterion is explicit
and testable hazard coverage, not a globally small number of clauses.

#### Requirement groups improve cardinality but do not guarantee semantics

Round 11 kept the candidate at two routine groups and three CRUD groups across
both repetitions. That makes the Acceptance ownership shape predictable, but
one Scenario still dropped the temporal force of “only after successful
request,” and other Scenarios used a broad “valid submission” trigger that also
matched their request-failure branches. Stable grouping is therefore a useful
mechanical property, not evidence that the clauses are mutually exclusive or
source-complete.

### Falsified

- “Keep it simple” changes behavior reliably.
- Naming an existing owner prevents a fabricated gap.
- Source and consequence alone determine a minimal carrier.
- “Independently verifiable” is a useful exception boundary; almost any branch
  can be described that way.
- A final merge instruction stabilizes Requirement decomposition.
- Acceptance traceability alone preserves explicit Constraints.
- An exact prose fallback guarantees that two semantic failure classes remain
  separate after the executor compresses them into one sentence.
- A PM/engineer role declaration prevents a plan from resolving a product gap
  it correctly identified.
- A free-standing KEEP / OPEN / MOVE / DROP pass automatically preserves the
  right carrier cardinality and the strongest source-supported neutral wording.
- A closed scope-envelope declaration prevents the writer from adding behavior
  for an in-scope object or operation that the source never required.
- A rendered coverage contract is a low-cost source of truth. In round 11 it
  duplicated the normative clauses, grew both fixtures, and once claimed that
  a Scenario owned an invariant its text had actually dropped.
- Source tags alone prevent semantic contradiction. Direct-tagged success
  Scenarios still used triggers broad enough to overlap direct-tagged failure
  Scenarios.

### Newly supported direction

A post-draft pass can detect unsupported specificity that survived generation-
time rules: both round-10 candidate repetitions removed the field-adjacent
placement incorrectly inherited from rename. That is directional evidence,
not a passing candidate. The reducer must operate on clauses within a fixed
Acceptance-owned carrier rather than deciding carrier count itself, and its
replacement operation must preserve the strongest neutral statement directly
supported by evidence.

Round 11 adds a second supported direction: if Scenarios are retained, their
value is atomic test behavior, not another discovery surface. Success and
failure Scenarios need disjoint observable preconditions, and preservation of
source qualifiers such as “only,” “before,” “until,” and “unchanged” must be a
mechanical or reviewer check. The scope/coverage model should be an internal
authoring aid unless a compact, non-duplicative carrier can be demonstrated.

Round 12 supports a smaller candidate surface. An Acceptance-owned group with
unnumbered clauses eliminated the baseline's 10-way CRUD Requirement split,
kept every explicit Constraint, and reduced artifact size. It did not require
clause IDs, cross-file traceability, a new checker rule, or another review
station. The routine arm passed both blind reviews.

Round 12 also exposes the remaining semantic limit precisely. The fixture says
that a valid submission creates or renames a label and separately says what
happens when its request fails. Both candidate Requirement sections preserved
those sentences without conditioning the success outcome on request success,
so the success and failure triggers overlap even though their UI flows were
disjoint. The no-derivation rule prevents the writer from repairing that
ambiguity safely on its own. One candidate run additionally stated that the
confirmation modal closes on cancel without source authority. The next design
decision is therefore not another identifier or generic completeness check; it
is whether contradictory or overlapping source behavior must stop for user
clarification, or whether a narrowly defined logical-normalization operation
can be proven safe. No further prompt round is justified until that authority
boundary is chosen.

### Not tested

- A different executor model or provider.
- Model-version upgrades.
- A full real-repository `write-spec` run including intent commit identity,
  checker execution, decision point ②, commit, and closing review.
- Triggering behavior; candidate frontmatter was unchanged by construction.
- Long-term authoring cost across a broad population of real specs.
- A mechanical validator implementation.
- A representative corpus of ordinary real-repository intents; round 11 added
  one synthetic routine fixture but did not sample production intents.

The results therefore establish behavior for the pinned Claude executor and
reviewer setup on four synthetic fixtures. They do not establish model-independent
correctness.

## Mechanism-complexity assessment

### Smallest supported end state

Keep the change inside the current `write-spec` station and current `spec.md`
artifact:

- one existing Requirement owner group per confirmed Acceptance in newly
  authored specs, with unnumbered clauses when the source contains distinct
  observable conditions;
- derived branches remain conditions or UI-flow outcomes;
- one compact Constraint-preservation line per explicit Constraint;
- implementation methods do not enter a product spec;
- no rendered scope-envelope or coverage-contract section unless a later test
  proves it replaces rather than duplicates existing carriers;
- no per-check admission record is persisted.

This shape adds no station, artifact type, or identifier type. Round 12 does
not justify enforcing it against historical artifacts.

### What should be mechanical

Keep the current deterministic checks unchanged for the first implementation
candidate. They may continue to verify the existing Requirement identifier and
Acceptance-pointer grammar, but Round 12 does not justify a new owner-
cardinality, clause, Constraint, or semantic-overlap rule. Any later checker
proposal needs separate evidence that it catches a repeated defect without
rejecting historical specs or creating another review loop.

### What should remain semantic

A deterministic checker should not guess whether:

- two clauses describe the same behavior;
- a hazard is concrete enough to authorize derived behavior;
- an error placement was actually specified;
- a Design decision is a user-visible fork or an implementation choice;
- a Constraint mapping truthfully preserves the invariant.

These judgments belong in the single closing review. Attempting to encode them
as keywords would create a gameable second specification language.

### What not to build

- no new complexity-review station;
- no new `critique` auto-trigger inside `write-spec`;
- no complete Ponytail ladder at spec time;
- no permanent Source/Consequence/Minimal-carrier table for every probe;
- no permanent rendered scope-envelope plus coverage-contract pair from round
  11;
- no automatic Requirement for every completeness finding;
- no checker that interprets semantic similarity or inferred necessity.

## Recommendation

Do not apply the round-8, round-11, or round-12 candidate verbatim. Round 12
supports keeping the next candidate deliberately prompt-only:

1. retain only the existing `REQ-n` identifiers; do not add clause, Scenario,
   source, coverage, or cross-file IDs;
2. treat each existing `REQ-n` as an Acceptance-owned group that may contain
   unnumbered clauses, without adding an exact-cardinality checker;
3. retain the compact Constraint-preservation list as the sole carrier for
   cross-cutting Constraints;
4. allow the post-draft pass to delete unsourced behavior, implementation
   detail, and duplicate wording only; it must not rewrite sourced obligations;
5. when sourced success and failure conditions overlap, stop for clarification
   rather than infer a missing product condition under the current authority
   model;
6. do not add a new station, reviewer loop, or checker rule from this evidence;
7. test the spec-only candidate on representative repository intents before
   testing the existing `write-plan` handoff or claiming portability.

The acceptance decision for a future implementation should be based on the
whole end state: fewer discretionary prose rules, stable structural output,
unchanged security/accessibility invariants, and no net increase in Loom
mechanism count without an explicit budget exception.

## Independent planning audit

A user-authorized Claude Code audit subsequently reviewed the smallest proposed
owner-group change. It did not clear the proposal for implementation planning;
its result was `RESHAPE`. Controller checks substantiated the most important
objections:

- the current plan owns one positive plus one negative/boundary test pair per
  Acceptance, not per proposed atomic clause;
- a dry-run of exact owner cardinality over the 13 active specs found 3 that
  would newly fail, so compatibility is parser-level rather than artifact-
  level;
- the proposed dogfood gate would miss narrowed or weakened sourced behavior
  and overlapping success/failure triggers;
- “surface a product gap” has no defined `write-plan` handback behavior.

The audit therefore recommends resolving clause-level test ownership, legacy-
spec treatment, deletion-pass authority, cross-cutting Constraint ownership,
and product-gap handback before implementation planning. The full consultation
record is [the independent planning audit](2026-09-11-write-spec-owner-group-independent-audit.md).

## Capture-intent frontier probe

A separate minimal A/B probe tested whether replacing `capture-intent`'s fixed
interview scheduling with a temporary grilling-style decision tree and frontier
would improve the first-turn decision. It did not modify the formal skill.

Two cases were each generated twice per arm. A complete CSV-export request
should have returned `READY`; an ambiguous project-mute request should have
asked which notification channels were affected. Two Claude Opus reviewers
received reversed arm labels.

| Case | Current interview | Frontier candidate | Result |
|---|---|---|---|
| complete CSV request | both runs asked unnecessary CSV-format questions | both runs asked unnecessary CSV-format questions | both FAIL |
| ambiguous project mute | both runs reached the missing notification-channel scope | one run returned `READY` and invented Unmute behavior; one asked an already-answered member-scope question | current PASS; candidate FAIL |

Both reversed-label reviewers agreed. The candidate's abstract frontier rule
did not keep the model from promoting plausible spec details into intent
questions. Worse, one run treated its own inferred member scope and Unmute
behavior as settled while missing the explicitly planted channel ambiguity.
This falsifies the claim that adding grilling vocabulary alone improves
`capture-intent`. A full multi-round grilling replacement is not justified by
this probe. Any next candidate needs a closed question-admission rule grounded
in the five intent fields, not merely a decision-tree traversal instruction.

This was a first-turn behavioral probe, not a full interactive interview. It
does not establish multi-round convergence, user experience, or cross-model
behavior.

## Standards and prior-art boundary

The completeness redesign used these sources as scoped inputs, not as automatic
scope generators:

- [ISO/IEC/IEEE 29148:2018](https://www.iso.org/obp/ui/#iso:std:iso-iec-ieee:29148:ed-2:v1:en) — requirement quality and traceability.
- [NASA Systems Engineering Handbook Appendix C](https://www.nasa.gov/reference/system-engineering-handbook-appendix/) — necessity, correctness, feasibility, and traceability checks.
- [ISO 9241-110](https://www.iso.org/obp/ui/#iso:std:iso:9241:-110:dis:ed-2:v1:en) — interaction principles, only when a human-system interaction is in scope.
- [Nielsen's usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) — lightweight discovery prompts, not a normative completeness standard.
- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) — product-quality risk vocabulary, not automatic Requirements.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) — normative only for applicable Web content and the declared conformance scope.

The experiments borrowed Ponytail's deletion-first intuition but did not import
its full decision ladder. At `write-spec`, the tested failure is scope
authorization and artifact shape; dependency/platform escalation is closer to
implementation planning and would add unrelated decisions here.

## Evidence inventory

Raw executor and reviewer transcripts were intentionally kept outside the repo
to avoid committing bulky model output and local path metadata. The reports
were retained in the experiment workspace. Their SHA-256 digests are recorded
below so a locally available bundle can be checked for identity.

| Report | SHA-256 |
|---|---|
| `dogfood-stage-minimality/report.md` | `660e5e39b71f594dfe205d35452d33d1da9b4cc1ca1fb884aa8b26a15335866c` |
| `dogfood-owner-first-r2/report.md` | `62ad61c7d0975f0b18ddfe52ad7000f52bd79961a6452d4e678d85d4e59f574e` |
| `dogfood-acceptance-bound-r3/report.md` | `c5275c9ba57f67fa92e5710450deae73f9c38574b046d5c5a50db5fdd8cc22f4` |
| `dogfood-acceptance-bound-r4/report.md` | `2c979da951a18c4f5b892146b0993aca0811e70854e4b86c8570c0057dc04f89` |
| `dogfood-template-bound-r5/report.md` | `9e0c7f6470551bc418b469687731bb38d0e89b362be9c241e6732f2c62752e1f` |
| `dogfood-template-bound-r6/report.md` | `74f1132c3f6f4a09e28f79ad0933e631c3249ffce411a32ce5474395fe3ed3d3` |
| `dogfood-template-bound-r7/report.md` | `47c1539c24f0ee81a2c3d144faf479346b895612128fb420b3452a8caca1cfd8` |
| `dogfood-template-bound-r8/report.md` | `1287fe1f3f2e969fda3969b56f2f39e923d41b4461c366e41636b4c69893e66f` |
| `dogfood-template-bound-r8/candidate-template.md` | `a4455e481af397318402af4d8c7acabdc17d615f2a8af26701ff4b6b15c86fe5` |

Round 9 and 10 raw outputs and blind reports are retained in the same external
experiment workspace. Their digests should be recorded after the files are
frozen; until then, the repository conclusion relies on the named report and
raw-output inventory rather than claiming immutable identity.

Round 11 used a fresh external bundle named `loom-r11`. Its inputs, outputs,
and reversed-label reviews were frozen with these identities:

| Round 11 file | SHA-256 |
|---|---|
| `common-baseline.md` | `bc5bc27af31f9eb2a5d83cf34041a8edb93560902fee5f3fe9be23f977f20510` |
| `candidate-addon.md` | `db07472c9262fb5b6e033d2cd87c0be3403e55f3bccd7c9e1ebb3cc137e24c47` |
| `case-routine.md` | `c9743f6f5167d01e994dda60241cde69c4a6b5749afbf01411c986c284ae2468` |
| `case-stress.md` | `d46ce4a9ed02322301dcd660d1277f9337654590040fda432763dcc3d69343b0` |
| `outputs/routine-baseline-1.md` | `434305cc7cd8eafb36af95547c59974fee7c2448626c0191440f7aec357da3a8` |
| `outputs/routine-baseline-2.md` | `638c94f8f1b6320ab5b7a745d7613ad9bc5c26e7643c5fcde35b00600f825700` |
| `outputs/routine-candidate-1.md` | `e7e4cc7d815901c215c9658a9b9d2b73334405c53de148b30d505c27ef5a1b12` |
| `outputs/routine-candidate-2.md` | `44810085b06b843a54f268a1a9718169449d299282a700c8cdbb676d638a04a6` |
| `outputs/stress-baseline-1.md` | `70d1a5470ec160f4ce0fc65b2d1460bdbdbac011eac0ad07be9fc02c1b677f1d` |
| `outputs/stress-baseline-2.md` | `22fc87bcfedb94ceea9ae13a2f8ad7d291cd5e5b9f93c7cd58f219215bd75a70` |
| `outputs/stress-candidate-1.md` | `10d345ac5491bc184d75ab5e6a210046d82a944826f40365adebb82be47456d9` |
| `outputs/stress-candidate-2.md` | `0ad51b27f0a54214d03370793d693f6e742274ef50f7a7b5e6480e8806c6904f` |
| `reviews/routine-review-a.md` | `f3b39f323e2bba5672e19df1b9f2ff97e30bbf0bb38558975615e7cb5e8578d7` |
| `reviews/routine-review-b.md` | `76180e617389b1631bf6bf9750a59f2703e9df32bae5351ed57fb527363a7e81` |
| `reviews/stress-review-a.md` | `931f399cb1252df37e795e4609c877545d0bdd8278721376efbaea61edd105d0` |
| `reviews/stress-review-b.md` | `a1de6fdde00a204ee4f05aa4f7309757750319b2d83235cefa2b6cb1f1f935ac` |

Round 12 used a separate external bundle named `loom-r12`. It deliberately
tested no new ID and no new checker. Its frozen identities are:

| Round 12 file | SHA-256 |
|---|---|
| `common.md` | `e82bdb78dec78ed25571eb9a455a07fb43b154ec7457f8a4fddaa1eb97236185` |
| `candidate-addon.md` | `785fed54b00d9c7dc1f5501cb44d9815fecfa37d8c41043670ff7d2a1940f9c8` |
| `case-routine.md` | `ff5f6ecfdd5c29eb17d1605f7ed131a48bdbf5213f1db7c641284b2162ffb55b` |
| `case-stress.md` | `665a439b264fff896b456b9ea430d1bed0765e2a1ab642385c0f76468d1a2641` |
| `reviewer.md` | `e769c5e0c6e213fee03c86a9bcfa5d17824ad5ac64c0874162a0de7ea36a2f37` |
| `outputs/routine-baseline-1.md` | `16664b479f4276a119541376d4a8d1a0533ee23b7e94112470f8c170088482b6` |
| `outputs/routine-baseline-2.md` | `5b55d8c8b1240ce9eb6e568bea028ab817cf44c3f74fb09ec31a039d6ca9c855` |
| `outputs/routine-candidate-1.md` | `bce455552be1a2285646ccbb521969b4d7b7bda4868c32c2bf817f64f952608c` |
| `outputs/routine-candidate-2.md` | `43fb4220c24a83a44c17993ea21ac9210664ea4aae52d59a6470fc7926045f5f` |
| `outputs/stress-baseline-1.md` | `d375f544311be441343503af8a3c93232e72d7bcbaef4fa6d3032427deabcf7d` |
| `outputs/stress-baseline-2.md` | `42e9eb0063f6aa1581e30607ac8366f46cde69a6d4646325bfdd5b5855a5eb74` |
| `outputs/stress-candidate-1.md` | `8cfd0301f0e8ec200a09516e01097265ba5fcada8662d100726c2ca6763af6c5` |
| `outputs/stress-candidate-2.md` | `6d16b91dec52bb747ed937442e502bb8e76302c0b26019f01a6db37ecb0ce435` |
| `reviews/routine-review-a.md` | `06137cb1a61ace5176072e41f380b862a98fff7eb2cf57c02fdf50bae0ef240d` |
| `reviews/routine-review-b.md` | `f37cac65ebb7e616493ceb6b5fe2740dca8fa23d6fc136ffdcaadde6d6c82b62` |
| `reviews/stress-review-a.md` | `e2319fcb663a9e7815b5da45887b7b7fdc22a84e46d70ec00bf627c4c050dbca` |
| `reviews/stress-review-b.md` | `89344851574966d061b1789ae361bf24592a10b94f2f98741c809c160e547788` |

The separate `loom-capture-frontier` probe was frozen with these identities:

| Capture-intent probe file | SHA-256 |
|---|---|
| `baseline.md` | `a2dd89a748e52c195647d68ddd4b99e5114dd1163ee82cca4b68e4127f90a1a9` |
| `candidate.md` | `0b91ba409562a93fa0815cecdcd8d7a42fa268eb3ea6dd99db16777c0969a362` |
| `case-ambiguous.md` | `a3b57d99475adb9fc50a20460f30b0d36fae5098ddadc833044528bca35fd0aa` |
| `case-complete.md` | `3f20c735cb6e200c4ece105c4365f55bab87752e0403cd5ad4fd8f1949b06a54` |
| `common.md` | `26c80a015197d42dd5e553a1de3174141762fdd77b57dc63dff8b56955bb8f91` |
| `reviewer.md` | `f68e6335da691bbe0ba96b1298990800be916964f03e11b7750031c539038811` |
| `outputs/ambiguous-baseline-1.md` | `18d3870b9d239d6293be311b134bbcd50365c4abd851cdddbbc563c227cb3fa5` |
| `outputs/ambiguous-baseline-2.md` | `f219242bcc2fa08a27645131dc2963a0b6d0b9e544c521508fddc1c5c8c0e429` |
| `outputs/ambiguous-candidate-1.md` | `385cf24c7917723f29e73cb412b84b123c929e6a8967c2544c4cb1f9d2ee39ef` |
| `outputs/ambiguous-candidate-2.md` | `098eadb257e6911bc757e3500e242eb350032dc45bfa9bfd4b52144558343c7e` |
| `outputs/complete-baseline-1.md` | `e17464338024dacc614e0c17bb37ea78baa600d076a79e9788a5fa62c1745e34` |
| `outputs/complete-baseline-2.md` | `d3211ae4ebf7b52f50478fc230c8ce5d6e4747696897b70a762ff583949e62bf` |
| `outputs/complete-candidate-1.md` | `d3211ae4ebf7b52f50478fc230c8ce5d6e4747696897b70a762ff583949e62bf` |
| `outputs/complete-candidate-2.md` | `0f9dd8d38fde081022b3874e20523c4c35473363c3b637c024efa706eda2b162` |
| `reviews/ambiguous-a.md` | `d7722b7f1831c1cdba63bab531ebb51180409fb770e35b36b2b0280c252d21ee` |
| `reviews/ambiguous-b.md` | `ddec86562a423ee2d7f83eea78d28b53239b19f76dcc1640b1177042dfabf330` |
| `reviews/complete-a.md` | `dd30773140e3786dc0aa3f688b32a2a2f0a6c2562bd0e25ecc9f40c947dadea1` |
| `reviews/complete-b.md` | `d547575f2934cfdaf878585c669e19973988c1d94514fc728d2f78988dfd6b94` |

Repository snapshot inspected for the final synthesis:
`3f8ed28080d3a41be95a42d17f0106a57b64bbe2`.

## Reproduction outline

1. Pin the baseline/candidate package bytes and the selected fixtures.
2. Run each executor twice in a fresh Claude Sonnet session with read-only
   access to its package and fixture.
3. Strip arm identity, scan for leakage, and create case-local bundles.
4. Reverse LEFT/RIGHT order between two Claude Opus reviewers.
5. Explicitly name the neutral arm each reviewer grades.
6. Treat disagreement, truncation, skipped preservation, or any invariant loss
   as FAIL.
7. Compare carrier counts, artifact word counts, within-arm variation, and
   source-sensitive semantic defects.
8. Keep production files unchanged until one complete candidate passes and a
   separate implementation change is authorized.
