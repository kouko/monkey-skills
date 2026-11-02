# Independent re-evaluation and bounded repair proposal

Date: 2026-11-02. Checkout: `/Users/kouko/GitHub/monkey-skills`; HEAD `4cbf85a8841d7d52393a8bb4058284755e108e25`.

Status: **review and repair proposal only**. No implementation, source changes, commits, network calls, installations, publication or merge. This is not a confirmed Loom implementation plan; implementation intake/confirmation remains a separate action if requested.

## Decision

Four implementation defects independently reproduce; eight instruction conflicts or evidence-input gaps remain actionable. The previous fixed-baseline contradiction is withdrawn. The size-warning issue is narrowed to inconsistent reporting semantics, not an empirically proven 25,000-token failure boundary. Test failures and the judge's numerical self-score must not be substituted for runtime evidence.

Three fresh-context reviewers examined implementation, rule scope, and tests/history. They received untrusted hypotheses, not the previous report or its conclusions. They inspected source directly; the implementation reviewer also generated fresh executable probes and negative controls. All exact runtime model IDs were unobservable (`unknown`); this is context-independent review within this host, not cross-vendor/model validation. Independent agreement alone does not establish correctness or exclude a shared blind spot.

## Findings retained, corrected, or excluded

| Prior finding | Re-evaluation | Evidence and actual limit |
|---|---|---|
| Three creator Python commands are Markdown | Confirmed | Every CLI fails at line 3 before arguments/input/model availability matters. Manual quick eval and manual benchmark fallback still exist. |
| Structural equivalence ignores operation order | Confirmed | Reverse-order and duplicate-redistribution traces pass Layer 1; replacing a tool correctly fails. This does not establish that semantic review or the complete release gate passes. |
| Truncated blind comparison exposes identity | Confirmed | Normal baseline/variant directory paths appear when output is truncated; the untruncated negative control does not leak these paths. No prior live user exposure is established. |
| Explicit baseline DROP is lost in preference export | Confirmed, narrower impact | Raw JSONL remains intact. Derived export omits usable baseline wins, whereas ADOPT exports a pair. None is a distinct non-selection. No active trained model exists here. |
| 25k–30k warning is suppressed | Behavior confirmed; original interpretation narrowed | 25,001/28,000/30,000 fixtures suppress warning. However the shipped validated corpus itself estimates 25,135 and tests require no warning. Reconcile report metadata and approximate validation scope; retain 30k grouping policy. |
| Fixed comparison snapshot versus previous iteration | Withdrawn as a conflict | `eval-protocol.md:107` explicitly checks regression against the preceding iteration while `:147` retains the original snapshot for effectiveness comparisons. Both can run. |
| Description policy, metadata path, vote policy, extraction invariant, ablation count, agreement threshold, multi-pick adoption, auditor inputs | Eight actionable conflicts/gaps | See independent rule report and concrete decisions below; not all are demonstrated live host failures. |
| Six hidden description failures | Test/policy drift, not six runtime failures | #851 changed routing/section placement without synchronizing old inline checks; real cross-document policy drift also remains. |
| AGENTS CLI declaration failure | Obsolete test expectation | Generic generated project guidance no longer advertises one plugin CLI; the bundled protocol and behavioral CLI tests remain. |
| Judge 4533 versus 4500 words | Real local structure-gate violation | 33 words over the implemented whole-file count. This is not evidence of incorrect evaluations. |
| Judge 68/120, F | Advisory calibration only | Previous total adds up, but dimensions depend on subjective estimates and the judge's own severe D1 rule. Do not use F as proof of runtime unreliability or as a reason to redesign the rubric. |

The previous raw judge example/parameter conflict remains excluded. Reject-versus-handoff and the context-sensitive “Layer 1 pass = PROCEED” phrasing are not added as independent confirmed bugs. No work is justified merely by a raw detector's confidence label.

## Recovery evidence: restore existing behavior instead of inventing it

Commit `f3b9a9827658b4311675c8111a5b50cbbe23f42b` (#851) replaced real implementations of `aggregate_benchmark.py`, `package_skill.py`, and `run_loop.py` with prose: 856 deleted / 33 inserted lines across those files. Its stated scope was consistency repairs and reference extraction, not removal of automation.

Parent `cb8d7e4aa317af4707373636f494ebd2a45a1f4d` retains working-code candidates (401/136/328 lines). Fresh extraction to a temporary directory established:

- All three old modules parse.
- Historical loop and benchmark `--help` exit successfully.
- Historical packaging produces a valid `.skill` ZIP with fixture content preserved.
- Current helper modules `utils.py`, `run_eval.py`, `improve_description.py`, `quick_validate.py`, `generate_report.py` have no diff from that parent.

This supports selective recovery, not blanket reversion of #851. Syntax/help/archive success is not full optimizer correctness; retained historical behavior still needs the offline tests below. Do not restore the old SKILL.md or undo unrelated reference splitting.

## Alternatives and scope choice

| Approach | What it delivers | What remains |
|---|---|---|
| **Selective recovery plus bounded fixes — recommended** | Restore advertised commands, repair reproduced checks, align existing rules and regression coverage | No new framework, rubric redesign or real trained model |
| Urgent subset only | Restore commands, fix blind path leakage and ordered traces first | Known policy contradictions and export/report issues remain explicitly open |

Doing nothing fails the requested repair outcome. A complete rewrite is unnecessary because recovery code and existing authorities exist. Combining the urgent subset with the remaining bounded repairs is the recommended proposal, not an extra implementation path. No outcome is removed just to make the patch smaller.

## Proposed work packages

These are reviewable repair recommendations, not an implementation authorization. Each begins with a failing regression test against the present source, followed by the smallest change. Exact implementation tasks belong in the confirmed change's plan.

### R1 — Recover the three creator commands (highest priority)

Files: `skill-dev-toolkit/skills/skill-creator-advance/scripts/{aggregate_benchmark,package_skill,run_loop}.py`, focused creator CLI tests.

- Selectively recover the three parent-version implementations; adapt only if a demonstrated current contract mismatch requires it.
- Keep their existing command names, file formats and helper interfaces. Do not rewrite the optimizer, remove advertised capabilities, or revert the entire historical commit.
- Offline positive tests: minimal valid skill creates a readable archive; two configurations/repeated runs produce benchmark JSON and Markdown with recomputed expected statistics; fake evaluator/improver drives a bounded optimization loop and produces the expected result fields.
- Negative/boundary tests: invalid skill/input is rejected; iteration bound is honored; the improvement backend does not receive held-out observations; selected output belongs to an evaluated candidate. Follow the restored protocol's existing selection policy rather than inventing a new evaluation methodology.
- Safe wiring tests: invoke all advertised CLI modules with `--help` from documented cwd. No real model calls/browser launch in CI (mock side effects or disable report launch).

Acceptance: the currently advertised commands perform their existing local responsibilities and no longer fail as Markdown. A green syntax check alone is insufficient.

### R2 — Enforce ordered tool-call comparison

Files: `skill-refactor/scripts/equivalence_check.py`, its new focused regression tests, `references/equivalence-check-protocol.md` if tolerance wording needs precision.

Decision: retain ordered comparison and the existing same-vocabulary / count-difference-at-most-one tolerance. An allowed one-call insertion/deletion must preserve the other calls' relative order. Same-length traces must match exactly. Do not replace sets with multisets, which still lose order. Retain the existing no-trace behavior unless separately justified; malformed-trace hardening is not bundled automatically.

Tests: identical traces pass; reversal and redistributed duplicates fail; an inserted/deleted duplicate call preserves relative order and meets tolerance; new tool vocabulary and difference above one fail. Full Layer 1 fixture must reject the known reversed-order case. Layer 2 remains required by its existing rules.

Acceptance: operation reordering cannot satisfy the structural sequence contract.

### R3 — Keep blind full-output retrieval blind

Files: `skill-tuning/scripts/ab_harness.py`, `references/ab-harness-protocol.md`, focused rendering tests.

Decision: do not print the original source path during truncation. The current CLI has no pre-pick full-text retrieval interface and keeps its label map inside the running process. Copy full outputs as ordinary files into a fresh neutral run directory using blind filenames such as A.md/B.md; display those neutral paths. Keep that same label assignment throughout viewing and choice, and preserve the existing post-lock identity decoding. Do not use symlinks whose targets expose baseline/variant identities. This is a bounded addition to the existing harness, not a generic storage subsystem.

Tests: truncate outputs stored under the documented baseline/variant layout; displayed text contains neither identities nor source paths; full-text retrieval through a blind label remains possible; untruncated rendering remains usable; the locked selection still decodes correctly. Update the instruction that currently asks for the original full-output path.

Acceptance: user can inspect complete output before choosing without learning baseline identity from harness-generated metadata.

### R4 — Align the rule conflicts to existing authorities

| Area | Specific repair and existing authority | Required discriminating case |
|---|---|---|
| Description author/judge consistency | Preserve reference routing. Treat `description-design.md` as the operative authority: positive triggers first, limited 2–3 exclusions only for adjacent-skill disambiguation; optional short multilingual belt only under its stated mixed-language use condition. Align creator/judge and update stale Principle 5 pointers to Principle 4. Historical research claims are not reasserted as newly verified. | A permitted limited exclusion/conditional belt is not rejected by one consumer while authored by another; excessive/redundant use still fails the chosen policy. |
| Eval metadata | Keep one `eval_metadata.json` per eval-case directory, explicitly pass that path to the grader; `grading.json` stays per run. Fix schema line 70. | Two repetitions share the case metadata and write separate run grading results. |
| Refactor votes | Preserve `multi_judge.py` and detailed reference policy; align Q1/Tier prose. 2E+1U = moderate pass; 2E+1N = escalation; specific-change dissent retains override; other distributions follow reducer. | Exhaustive three-vote distributions with/without concrete dissent; do not turn all 2/3 outcomes into an automatic pass. |
| Extraction invariants | Preserve existing dependencies; explicitly allow a new loaded reference created by equivalent content extraction. Changes touching resources obey package mode and whole-package Q2. Update misleading example. | Adding a loaded equivalent reference is permitted; removing/repointing an existing dependency is not; moving words alone does not earn whole-package savings. |
| Ablation judge count | Use Q1's three judges for current ablation instructions. Align cost/mapping; preserve the dated two-judge prototype as historical evidence. Candidate discovery still does not authorize deletion. | Mixed votes are uncertain; actual cuts still require normal Q1/Q2/Q3. |
| Human agreement | Preserve entrypoint's repeated 70% policy; replace two-thirds reference threshold. | 2 of 3 escalates; 3 of 4 meets majority threshold. |
| Multiple choices | Preserve DEFER/no edit; remove adopt-first exception. Apply/commit instructions are conditional on a locked single non-baseline ADOPT. | Both, None and Refine never cause adoption; explicit candidate choice can. |
| Dogfood evidence | Preserve existing blind/informed roles. Give blind auditor explicit output criteria and artifact, without author reasoning/trajectory. Check the transcript/step compliance in the existing informed/orchestrator pass and fix taxonomy role wording. | Artifact with omitted criterion and a transcript with a skipped step are detected by the appropriate distinct checks, without deriving intent from the flawed artifact. |

These choices are agent-decided from existing source ownership and behavior, not requests for the user to judge wording quality. They change conflicting instructions only; they do not add a new reviewer, service, verdict vocabulary or statistics subsystem. The conditional multilingual policy supersedes the old unconditional test expectation; tests must encode the deliberate policy rather than silently changing assertions merely to pass.

### R5 — Preserve explicit baseline wins in derived exports

Files: `skill-tuning/scripts/preference_log.py`, pair extraction/readiness portions of `judge_train_stub.py`, `references/{preference-log-schema,self-trained-judge-pipeline}.md`, applicable entrypoint statements and focused tests.

- Generate preference pairs for a valid explicit single pick, including DROP whose picked identity is `baseline`. Preserve ADOPT behavior.
- Do not infer a winner for None, multiple or refine. Reject/skip invalid chosen identities/missing hashes explicitly; report usable versus skipped evidence.
- Align readiness accounting to usable evidence, not merely 1000 raw ADOPT/DROP records. Keep raw log preservation and training-as-inactive semantics. No migration or rewrite of existing logs.
- Choose **1000 usable explicit single-pick records** as the readiness definition, matching the entrypoint and preference schema. Report generated pair count separately: one human choice counts once even if it yields several pairs. The existing pipeline outline at `references/self-trained-judge-pipeline.md:100-119` and `judge_train_stub.py` instead check 1000 pairs, so update those exact consumers together. This is an explicit reconciliation of an existing conflict, not a claim all current consumers already count records. No real training is enabled.

Tests: baseline DROP produces baseline-over-other pairs; ADOPT remains valid; None does not fabricate a selected output; invalid records cannot count as usable; all explicit-baseline picks remain exportable; empty-pair evidence is not reported as ready.

Acceptance: valid baseline preferences survive derived export and readiness has one documented definition; no real training is enabled.

### R6 — Reconcile the size notice without changing grouping

Files: consistency-check `plan_groups.py`, `merge_report.py`, relevant SKILL/README statements and focused planner/report tests.

Decision: retain split threshold 30,000 and group target 25,000. Retain the currently printed 25,000 as a conservative **nominal reporting bound**, not an empirically proven hard failure threshold. Apply the size notice to all actual groups, including unsplit ones; make wording neutral about why a group is larger. State explicitly that the reference experiment used approximately 25k (current corpus estimate 25,135); crossing the nominal bound is caution, not proof of invalid detection.

Tests: 25,000 / 25,001 / 28,000 / 30,000 / 30,001; unsplit and grouped paths; report/footer agree. Update the existing validated-fixture expectation intentionally: grouping still false, notice true for 25,135 under the chosen nominal policy. Preserve its provenance as the validated experiment fixture rather than claiming it was never validated.

Acceptance: size claims agree with the notice semantics without changing the grouping decision or overstating empirical validation.

### R7 — Repair test routing and guard only demonstrated behavior

Files: hidden description tests, `skill-refactor/scripts/test_package_mode_contract.py`, a minimal `skill-judge/SKILL.md` wording trim, focused regression tests and a path-filtered toolkit job in the existing workflow structure.

- Replace obsolete inline/heading checks with scoped assertions on actual resolved authority and consumer routing. Preserve numeric length semantics, triggers, exceptions and negative cases; do not use whole-file keyword presence as a semantic test.
- Remove/replace only the obsolete root-AGENTS command-advertisement expectation. Assert the bundled protocol and actual CLI at their existing source locations; do not add plugin-specific text to generated root guidance.
- Reduce judge's 4533-word whole-file count below 4500 by trimming repetition only; preserve all eight dimensions, caps, report obligations and loading triggers. Do not redesign it to raise the self-score.
- Ensure local/CI execution explicitly includes existing plugin tests, hidden description tests, toolkit structure checks and the meaningful command fixtures added by R1–R6. A syntax floor is supplementary to actual output assertions. No new generic runner framework.

Acceptance: obsolete placement checks no longer obscure behavior defects; every reproduced behavior has a targeted negative regression case; toolkit checks execute on relevant changes. Remote CI execution remains unverified until a later authorized publication.

## Dependencies and delivery boundaries

R1–R3 can be isolated from policy repairs. Within R4, author/judge/test changes are one coherent unit and must not land in contradictory intermediate states. R7's description tests depend on R4's explicit policy resolution; the ordered-trace fixtures belong with R2. R5's two extractors and documentation must remain aligned in one change. R6's planner/report/tests move together. Build/test/review each coherent change before publication; do not merge solely because another package is green.

Suggested delivery units: creator recovery; structural equivalence; blind display plus tuning/export policy; remaining text/metadata/dogfood consistency and test coverage. Keep unrelated changes separate where acceptance can be verified independently. Exact commit boundaries can be settled in the confirmed implementation plan without changing the outcome above.

## Proposal triage

### KEEP

- Restore known code and fix reproduced order/blind/export defects — GROUNDED and ESSENTIAL to the advertised behavior.
- Resolve eight conflicting instructions with existing authorities — GROUNDED and ESSENTIAL to deterministic execution of the documented procedures.
- Reconcile the size notice and stale tests; add focused execution coverage — GROUNDED and ESSENTIAL to reporting/checking the repaired behavior accurately.
- Minimal judge size trim — GROUNDED and ESSENTIAL to the existing repository structural gate; no claim of improved output quality.

### DEFER

- Real trained preference model — re-trigger only when a usable preference dataset reaches the explicitly adopted readiness condition and model deployment is separately requested.
- New live cross-vendor accuracy comparison — re-trigger when such validation is requested with an identified provider/model scope. This review supplies no cross-vendor accuracy claim.

### DROP

- Changing fixed-baseline comparison logic — the alleged contradiction is refuted.
- Full toolkit or judge-rubric rewrite — no evidence this is necessary for the retained defects; old numerical F is insufficient justification.
- Reverting all of #851 or restoring plugin commands to generated root AGENTS — both exceed the demonstrated repair scope.
- Treating raw detector finding counts, hidden test counts, or 6/6 planted recall as a count of unique real defects or as a global accuracy estimate.

## Verification evidence and completion criteria for a later repair

Current independent runs: plugin suite 71 passed / 2 failed; explicit hidden suite 6 passed / 6 failed (six failures are also surfaced through one plugin wrapper); focused planner/report 34 passed. Toolkit structure: five skills pass, judge fails 4533/4500. These are fresh results from this re-evaluation, not new evidence of full live host success. The prior 710-test repository run was not repeated here because source is unchanged.

A later implementation must produce: the targeted positive/negative/boundary results above, complete plugin plus hidden suites, existing package-gate protections, toolkit structure and repository checks, scoped independent review and updated consistency evidence. Rule changes need fresh realistic executions for vote handling, multiple-choice deferral, extraction package accounting and dogfood evidence separation; keyword tests alone are insufficient. Any paid/provider-dependent or full host replay not executed must be named separately, never counted as passing.

Current output is a repair proposal, not evidence that any fix is implemented or that real activation/optimization has passed.

## Supporting artifacts

- `code/report.md`, `code/probe.py`, `code/outputs.json`: fresh implementation reproduction and controls.
- `rules/report.md`: scope-aware independent rule review, including the withdrawn baseline allegation.
- `tests/report.md`, `tests/historical-smoke.txt`: fresh tests, local Git provenance and temporary-only historical recovery smoke checks.

## Fresh proposal read-back

A separate fresh-context reviewer returned PASS_WITH_NOTES (`proposal-review.md`). Two material notes have been incorporated: R3 now supplies same-session blind full-output files because the current CLI has no retrieval interface; R5 explicitly includes the existing pipeline outline and stub that count pairs, and selects usable single-pick records consistently. The reviewer did not implement fixes or establish live host behavior.
