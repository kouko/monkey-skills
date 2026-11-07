# Caller calibration and bounded repair proposal

Status: completed source calibration / proposal only; no implementation or new host test.
Date: 2026-11-07. Repository inspected at c79e18a73daf6004cb99b29da46630680b39d24a.
This is neither a replacement decision file nor a release-readiness verdict.

## Evidence identity and reading boundary

- **T/** means `/private/tmp/toolkit-claude-coverage-20261107/caller/target/`, reconstructed from Git35a6be1446a3636450a6d94886195d37018da9b1 under `skill-dev-toolkit/skills/skill-refactor/`. All T/ line references use that frozen version, not current refactor text.
- **R/** means `/private/tmp/toolkit-claude-coverage-20261107/caller/`; `read-1.json` and `simulate-1.json` are the immutable raw inputs. **O/** means `R/run-ZkVDRO/`, the failed W15 output, not an authority.
- **C/** means current `skill-dev-toolkit/skills/skill-consistency-check/SKILL.md` at c79e18a7. Step6 :159-190 requires the original complete claim, governing qualifications, action and factual/field analysis, and reasons. The script validates structure/coverage, not reason truth (:190).
- Manifest: `skill-dev-toolkit/tests/caller-review-cases/overstated-original-claim/case.json`. All21 frozen target hashes and2 raw hashes match. The wider run's149 prepared preimages also match. Raw read SHA256=`3ee1d9c3703df33312f73e697679e5588c211b53d8a26b6e43a83f75ac946709`; simulate=`5209204ec91b6c9a3a34eb89faaad0b39609add8bb30e0d03f9b0ebaa22e83c3`.
- Scope/precedence search covers T/SKILL.md and all eight Markdown references. Vote-dissent precedence and optional constitution authority do not supply a blanket entry-versus-reference priority for these pairs. A Q1 title is actual scope evidence, not an invented universal priority rule.
- The manifest fixes only read/F1's exclusion. This document changes no expected label, raw claim, confidence or historical result. Each original `why` below is verbatim; the raw steps remain available and are checked against actual sources rather than treated as authority.

## Calibration summary

Recommendations:2 qualified confirmations,3 exclusions,4 indeterminate. These
are source judgments, not a newly executed check, accuracy rate or complete gold
set. A defensible final label can still have an invalid reason. Blanket exclusion
or uncertainty must not replace the source-supported breadth exclusion or the
literal PROCEED/Q2 witness.

| Original | Recommendation | Strength / competing reading |
|---|---|---|
| read/F1 | excluded | Existing fixed breadth exclusion; creative-only concern is narrower. |
| read/F2 | confirmed, qualified | Literal overall-PROCEED witness; local-Q1 shorthand is a rival. |
| simulate/F1 | indeterminate | Creative eligibility versus delegated Q1 reachability. |
| simulate/F2 | indeterminate | Descriptive impossibility versus unreachable warning. |
| simulate/F3 | confirmed, qualified | Same qualified witness as read/F2; not unique gold. |
| simulate/F4 | indeterminate | `Clearer` alone does not establish the judgment-call qualifier. |
| simulate/F5 | excluded | Shared stop and nonexclusive advice; no promised prompt-free evaluation. |
| simulate/F6 | indeterminate | Accept-as-is permission versus anti-pattern classification/rationale. |
| simulate/F7 | excluded | Explicit acceptance resolves the `auto` qualification. |

## Nine original claims and source adjudication

### read-1.json / F1

> Shared condition: the target skill's output is creative, prose, or non-deterministic. SKILL.md and the equivalence protocol require aborting without running the check and routing to skill-tuning, while multi-judge-ensemble.md requires running the full ensemble on that output, so an agent cannot do both.

- **Conditions:** the original covers creative **or prose or** non-deterministic output, claiming opposing obligations across that union, not merely one creative case.
- **Sources:** T/SKILL.md:346,358-360 excludes creative/non-deterministic output; prose is a parenthetical example within that category. T/references/equivalence-check-protocol.md:13-17 admits prose as an artifact type; :119-123 excludes creative/non-deterministic output. T/SKILL.md:95-104,366-369 delegates Q1; ensemble :3-4,150-166 defines its subprocedure scope.
- **Counter-reading:** ensemble :165 literally covers any prose, but does not make the entry exclusion cover every prose output. A source-permitted mechanical prose report need not be creative/non-deterministic. That defeats the asserted prose-wide abort rule even if a narrower creative conflict remains. This is an applicability counterexample, not a new observed model run. The competing interpretation that all prose here means creative prose silently narrows the original union.
- **Calibration:** **excluded as overstated**, the fixture's sole fixed disposition. O/decisions.json:8-11 confirms by matching the three words, failing full-claim coverage. The independent Q1-reachability dispute cannot repair the missing prose-wide abort rule. Do not merge this original with simulate/F1.

### read-1.json / F2

> Shared condition: all three skip conditions hold and Layer 1 passes, but Q2 is marginal or failing, or Q3 is violated. The ensemble file assigns PROCEED from Layer 1 alone, while the SKILL.md verdict rules require RESHAPE or REJECT, and the stated skip exception only covers the ensemble, not Q2 or Q3.

- **Conditions:** structural-only eligibility, Layer1 pass and marginal/failing Q2 or failed Q3. This is an existential conflicting branch, not every structural-only round.
- **Sources:** T/references/multi-judge-ensemble.md:152-163 permits skipping the ensemble and says `Layer 1 pass = PROCEED`. T/SKILL.md:92-93,109-115,128,155-164 requires Q1/Q2/Q3, names distinct Q1 outcomes and rejects <5% reduction. Package protocol :18-22,76-80 separates reducer evidence from adoption; catalog :29-41,211-212 supplies low-risk tightening and Q2/Q3 qualifications.
- **Witness and rival:** an equivalent low-risk tightening can pass exhaustive structural checks on deterministic prompts yet reduce source words by3%. Literal overall PROCEED conflicts with Q2 rejection. Source-word Q2 and output-token Layer1 are different measurements; neither forces the other. The real rival is that PROCEED means continue past Q1 because ensemble :3-4 defines a Q1 subprocedure. Lack of explicit local redefinition favors, but does not prove, the global reading. An all-gates-pass example does not refute this failing-Q2 witness. A separate missing-Q1-vote allegation is unnecessary.
- **Calibration:** **confirmed on the literal defined-verdict reading, qualified**; not unique gold. An indeterminate disposition explicitly weighing the local reading is defensible. Exclusion based only on an unrelated compatible round is invalid.

### simulate-1.json / F1

> When a target skill's output is non-deterministic or creative, one file requires running the full judge ensemble while SKILL.md and the equivalence protocol require aborting and routing to skill-tuning.

- **Conditions:** creative/non-deterministic output. Unlike read/F1, this original does not independently include all prose artifacts.
- **Sources:** T/SKILL.md:84-88,346,358-360 and equivalence protocol :117-123 require stopping/routing. Ensemble :165-166 apparently says run, but :3-4,150-166 concerns Q1 Layer2; entry delegation is T/SKILL.md:95-104,366-369.
- **Competing readings:** literal `any` includes excluded creative output and creates abort/run tension. Subprocedure scope instead means the final line forbids skipping an ensemble **if eligible Q1 is reached**, leaving a creative example unreachable. Inoperative wording can be redundant without requiring entry into an excluded workflow. No explicit clause settles that relation. `Unreliable` and `must run` are not contrary facts: requiring a method does not assert reliability.
- **Calibration:** **indeterminate**, non-unique. A creative witness alone does not settle reachability; read/F1's prose counterexample does not exclude this narrower claim. W15's dismissal of scope merely because text becomes inoperative is insufficient.

### simulate-1.json / F2

> For the output token delta on a candidate, the same file sets a hard ±20% pass limit and also describes a >30% reduction as coexisting with a Layer 1 pass, which the first limit makes impossible.

- **Conditions:** the same output delta, mandatory ±20% pass bound and >30% reduction beneath `Even if both layers pass`. This is a descriptive/value allegation, not necessarily incompatible executable actions.
- **Sources:** T/references/equivalence-check-protocol.md:13-24 measures each prompt/output pair and immediately rejects Layer1 failure; :83-91 introduces the suspicious-pass warning. T/SKILL.md:95-118 delegates it without another output-token limit.
- **Competing readings:** baseline100/candidate65 is a35% reduction and cannot pass ±20%. As a material conditional, `both pass AND reduction>30%` is empty: later text is dead/redundant, not another pass limit. As ordinary procedural prose, `Even if both layers pass` and `didn't catch` describe that impossible state as possible, supporting the original factual allegation. Different token populations or overrides have no source support and cannot be invented.
- **Calibration:** **indeterminate**. A dead-text exclusion or descriptive-inconsistency confirmation needs its explicit reading. Preserve native positive and earlier audit disagreement; neither is unique truth. Absence of incompatible actions alone does not answer the factual allegation.

### simulate-1.json / F3

> On a structural-only round whose Layer 1 passes but whose Q2 or Q3 fails, the ensemble reference assigns PROCEED while SKILL.md requires all three checks to pass and otherwise REJECT.

- **Conditions:** structural-only eligibility, Layer1 pass, failed Q2/Q3. This matches read/F2's `why`; missing judge votes in the raw steps are ancillary.
- **Sources:** T/references/multi-judge-ensemble.md:3-4,152-163; T/SKILL.md:92-93,106-115,128,155-164,244; catalog :29-41,211-212. The skip clause's object is the ensemble, not Q2/Q3.
- **Competing readings:** the same3% source-word reduction witnesses literal overall PROCEED versus rejection; Q1-local continuation remains a rival. Neither a successful round nor missing votes alone resolves the original overall-verdict claim.
- **Calibration:** **confirmed on the literal defined-verdict reading, qualified**, not unique gold; source-grounded indeterminate is defensible. Reuse read/F2's reasoning only with these qualifications.

### simulate-1.json / F4

> For a user-proposed 'clearer' rewording, the catalog requires routing to skill-tuning without doing it in refactor, while SKILL.md's worked example runs that same proposal through the refactor gate.

- **Conditions:** the proposal must belong to the catalog's clarity **with judgment call** class for its routing rule to apply.
- **Sources:** T/SKILL.md:201-219 delegates the catalog and excludes phrasing aimed at different output; :309-331 shows an attempted behavior-preserving change that fails Q1. Catalog :29-41 permits equivalent tightening; :185-194 routes clarity with judgment call to tuning. Entry :255 addresses justification of a weak reduction, not all intake.
- **Competing readings:** `clearer` alone does not establish taste/judgment; an equivalent shortening attempt can later fail Q1. Conversely the example's motive and lost specificity can fit judgment-call rewording. The actual replacement text is absent. Discovering a behavior change afterward does not prove the intake was already in the taste category.
- **Calibration:** **indeterminate**, non-unique. Shared-word confirmation drops a qualifier; categorical reconciliation also lacks the proposed text.

### simulate-1.json / F5

> When test prompts are absent and the user refuses to write them, SKILL.md gives two different exits, skill-tuning or manual edit versus skill-creator-advance, and the skill-tuning exit self-aborts under the same condition.

- **Conditions:** absent prompts and refusal to supply them; alleged incompatible routes plus tuning's inability to run.
- **Sources:** T/SKILL.md:49-52,84-88,246,355-357 all stop refactor. :86-88 conditions suggestions on quality/cosmetic intent; :355-357 offers prompts or infrastructure redesign. Test-prompts schema :18-20,135-137 requires at least3 prompts for both evaluation skills.
- **Competing reading:** `revert to` can sound exclusive, but no clause forbids other suggestions or promises tuning can evaluate without prompts. Stop, report the blocker and applicable alternatives satisfies the governing action. Tuning's own refusal stays true; an unhelpful route is not itself incompatible action or a false promise of completion.
- **Calibration:** **excluded** as unsupported incompatibility. Source-supported negative, not a new fixture expected label. Preserve the real prompt prerequisite.

### simulate-1.json / F6

> When the current output is good and is accepted as-is, the curation process yields exactly the golden the same file names as an anti-pattern; the conflict is uncertain only because the process also offers editing or rewriting options.

- **Conditions:** truly good output **already accepted as-is**. This selects one permitted branch, not a requirement that everyone choose it.
- **Sources:** T/references/golden-anchor-protocol.md:15-29 defines human-curated anchors; :79-83,96-113 requires human judgment/rationale and permits accept-as-is; :179-185 distinguishes unreviewed generated goldens. :187-196 calls identical output an anti-pattern and says `Adds no information; just baseline-locks`. Optional delegation/use: T/SKILL.md:372-373,395-399; golden protocol :129-160.
- **Competing readings:** literally the anti-pattern includes this selected branch and its rationale contradicts curated anchor value. Alternatively it warns against uncritical copying rather than every reviewed identical output; human rationale can add information without changing output bytes. The row never expressly states that exception. Negative classification/guidance is not necessarily an absolute action ban. Both classification and factual rationale need adjudication.
- **Calibration:** **indeterminate** between permission/classification tension and underspecified guidance. **Firm reason failure:** O/decisions.json:49-53 excludes because editing/rewriting is optional. That changes the selected branch and does not answer the original. The raw step's stronger `directs accepting` paraphrase is also inaccurate, but does not erase the actual permission at :109 or the original `why`. Do not automatically confirm this low-confidence claim.

### simulate-1.json / F7

> On an accepted 5-10% package-mode candidate, recording PROCEED brings the verdict definition 'ratchet advances' into conflict with the rule that a marginal reduction does not advance the ratchet automatically.

- **Conditions:** marginal package reduction, explicit user acceptance, recorded PROCEED; preserve `automatically`.
- **Sources:** T/SKILL.md:35-43 permits marginal shipping after explicit acceptance; :155-164 defines verdicts; :131-132 explains threshold rationale. Package protocol :12-22,76-80 converts accepted RESHAPE into PROCEED. Entry :159-161 says not to auto-merge while allowing a user's decision.
- **Competing reading:** interpreting no automatic advance as no marginal advance at all conflicts with the same sentence's explicit acceptance exception. Here advance follows that decision, so is not automatic in the governing sense. Threshold rationale does not override the exception.
- **Calibration:** **excluded**. Do not remove `auto` or treat authorized transition as autonomous action. This does not erase the separately recorded historical10% endpoint wording issue.

## Established failure and causal limits

Observed contract breaches are read/F1's expanded category and simulate/F6's
off-branch alternative. F6's reason failure is firm although its final label is
disputed. Detailed reasons and unchanged top-level `needs-revision` do not cure it.
Earlier independent merger reproduction yielded byte-identical JSON/Markdown,
localizing the bad decisions upstream of rendering. It does not identify the
model's internal cause or prove an architectural limit. The W15 three-line/32-word
change failed semantic acceptance; native labels were unchanged. One replay does
not measure an effect size or prove all future instruction changes futile.
Earlier audits remain historical, not fresh reviews of this document. Recorded
batch estimate remains USD2.8133962; older costs/counters remain preserved.

## Minimum repair plan and alternatives

**Selected now:** source calibration and two fresh independent audits, with zero
runtime changes. There is no evidence that a new field, parser, judge, detector
or whole-package rewrite would solve semantic truth. Do not settle source policy
by majority vote.

**Conditional next candidate:** after implementation is separately authorized,
replace—not append to—C/Step6 items2-3 (:164-181). Reorder the existing reason
obligation: establish the unchanged original antecedent/coverage and governing
scope before testing a reconciliation; use an incompatible-action witness for
action claims and truth-condition analysis for permission/classification/value
claims. Reconciliation must remain inside a selected branch; counterexamples
must address the actually asserted coverage. Reuse the existing `reason` string
and statuses. This is a hypothesis requiring execution evidence, not a proven fix.

The later plan must show exact before/after prose and word counts. Replace the
failed W15 three lines rather than keeping them and adding clauses. Combined
items2-3 must not exceed their pre-W15 count of 153 whitespace words (item3 was 87;
current combined block is 185). Moving words between items
must not hide growth. No new code/functions/files/schema/roles or unrelated
cleanup. This goal makes zero production changes and does not authorize Build.

| Alternative | Decision and evidence |
|---|---|
| Append another qualifier/example | Reject now: failure survived W15 coverage wording; no measured benefit for more clauses. |
| Add runtime judge or condition schema/parser | Reject now: adds mechanism with no evidence it fixes reasoning; existing reason supports audit. |
| Make all nine labels fixed gold | Reject: manifest fixes only read/F1; several source readings remain disputed. |
| Rewrite the target rules | Defer to separate authoring scope; changes the test input, not caller performance. Re-trigger upon source-owner policy clarification. |
| Same-source paid retry, larger model or full case | Outside this goal's authority; residual budget does not reopen the failed window. |
| Remove every confirmation | Reject: discards the literal PROCEED/Q2 witness rather than explaining it. |

The smallest proposed end state retains the two detectors, hash-bound decisions
and merger. The later patch must remove superseded caller prose in that same
patch. No separate service, compatibility path or permanent duplicate is needed.

## Falsifiable validation for a later candidate

1. Freeze the same21 target files,2 raw files and all nine complete claims and confidences. Keep calibration/history/labels away from the executor; grader may read them. Pin revision/request/observed runtime identity and hashes. Leave case.json unchanged; this is a reason rubric, not an expanded answer key.
2. After authorized implementation, use a fresh native recorded-data caller replay for local behavior; it cannot certify Claude. Existing merger/schema tests cover interface regression, not reason truth. Do not write prose-marker tests as semantic proof.
3. read/F1 must exclude the original breadth, not replace it with creative-only. simulate/F6 must not be excluded solely because another curation branch exists. simulate/F1 must weigh Q1 reachability rather than dismissing it because text becomes inoperative. Correct labels with failed reasons still fail.
4. Retain the3% Q2 witness for read/F2 and simulate/F3. If choosing local-Q1/indeterminate, explicitly weigh the defined-PROCEED versus local-continuation reading; an all-gates-pass example is not a rebuttal. Preserve simulate/F2's factual/value reading even if excluding dead text; absence of incompatible actions alone is insufficient. Do not demand a unique label or accept blanket uncertainty as success.
5. F4 must retain `with judgment call`; F6 must weigh classification/rationale and human curation; F5/F7 must retain prompt/acceptance qualifications. Genuine interpretive disagreement remains visible. Do not substitute the grader's preference for source proof.
6. Two fresh source-informed native audits, sequentially, review full original claims and this plan. Resolve factual/citation/rubric errors before accepting this calibration; preserve legitimate interpretive disagreements. No invented precision/recall or named-model receipt from inherited/default profiles.
7. Repeated breadth promotion, off-branch exclusion, erased positive witness without source rebuttal, fabricated scope, dropped candidate or changed input falsifies the candidate. Stop its conditional full test and preserve costs/counters. Any later Claude behavioral validation needs explicit data/model/spend authorization. Release still requires actual intent Acceptance1-11 and fresh owning review; this calibration is no release evidence.

## This goal's verification record

The two new source audits ran sequentially with fresh contexts and no access to
each other's reports. Profiles resolved to host-default/unverified, without
model/effort overrides; actual native model identities were unobserved. These
were source audits, not paid external-host tests or new detector/caller runs.

- Audit A: **QUALIFIED**, `/private/tmp/toolkit-calibration-audit-a.md`. All nine original claims and source hashes matched; one required citation correction changed O/:3-7 to :8-11 (the reason is :11). Root checked the exact output lines and corrected the citation before B read the document. No substantive label reversal was requested.
- Audit B: **PASS for semantic calibration and conditional-plan scope**, `/private/tmp/toolkit-calibration-audit-b.md`. It checked the corrected document against the sources, found no material factual/citation/rubric correction, and retained the legitimate interpretation disputes. It does not certify a future patch or release.
- Both audit reports leave historical receipts/costs and the wider149-preimage check outside their semantic scope. Root separately verified the149 prepared preimages and reviewed the existing verification/batch-status receipts. USD2.8133962 stays a recorded estimate, not an independently measured bill. Do not count the two old W15 FAIL audits as these two new reviews.
- Root check: all nine blockquoted original `why` strings occur verbatim once; all21 target files also hash-match direct `git show` bytes at the pinned35a6be14 commit. Repository raw inputs and replay raw inputs are byte-identical.
- Preservation baseline:156 existing files (149 prepared preimages,6 final W15 outputs,1 unrelated user file) retain their SHA256 values. Result: `git_frozen_target_files=21`, `git_frozen_mismatches=[]`, `preservation_entries=156`, `changed=[]`, `nine_raw_claims=9` in `/private/tmp/toolkit-calibration-final-preservation.json`.
- `git diff --check`: exit0, no output. The new file is untracked, so also checked it directly with `git diff --no-index --check /dev/null docs/loom/2026-11-02-repair-skill-dev-toolkit/evidence/caller-calibration.md`: exit1 (file differs), no whitespace diagnostic. No tracked file differs from HEAD; the only new deliverable is this document. The unrelated pre-existing untracked intent is preserved.
- Root measured pre-W15 items2-3 as153 words and current items2-3 as185 using `git show 658384848^:skill-dev-toolkit/skills/skill-consistency-check/SKILL.md` and the current file, split on whitespace. The proposed ceiling is measured, not inferred from the size of the diff.

| Goal requirement | Evidence and completion limit |
|---|---|
| Nine full claims, conditions, source lines, counter-readings, supported judgments | Nine sections above; both fresh audits verify preservation and source grounding. |
| Ambiguity retained without expanded gold labels | Summary and each contested row; original case.json remains unchanged. |
| Established failures and smallest repair location | read/F1 and simulate/F6 reason breaches; conditional C/:164-181 replacement, measured word ceiling, unchanged interface. |
| Alternatives and falsification | Alternatives table plus seven validation obligations, including correct labels with invalid reasons failing. |
| Preservation and no production change | Direct Git/raw/hash checks above; no tracked diff, no new host test/install/publish/merge. |
| Two independent audits with no unhandled material correction | A's sole citation correction applied and verified; B reports no material correction. Legitimate source-policy disagreements remain explicit. |

This goal completes calibration and planning only. The historical Claude failure
is still failed; actual-usability Acceptance11 remains unmet. No runtime repair,
fresh acceptance attestation, complete gold set or release readiness is claimed.
