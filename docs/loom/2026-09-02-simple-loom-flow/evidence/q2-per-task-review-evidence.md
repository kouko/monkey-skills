# Q2 evidence — per-task review layer, what it catches layer 2 would miss

## A. Sample

- Plan corpus scanned: `docs/loom/plans/2026-08-*.md` and `2026-09-*.md` (96 plan files, 2026-08-01 to 2026-09-01).
- `grep -c NEEDS_REVISION` hit 31 of 96 plan files (`grep -c ... | grep -v ':0'`).
- Read in full/near-full: `2026-08-31-goal-create-stop-when.md`, `2026-08-31-decision-map-script-cleanup.md`, `2026-08-31-batch-review-measurement-and-nudge.md`, `2026-08-31-loom-code-script-helper-extraction.md`, `2026-08-10-design-md-spec-conformance.md`, `2026-08-21-dissolve-direction-layer.md`, `2026-08-06-backlog-ready-verb-and-close-loop.md`, `2026-08-24-review-binding-remediation.md`, `2026-08-13-open-question-dispatch-gate.md`, `2026-08-11-review-cost-reduction.md`, `2026-08-05-request-derived-authorization.md`, `2026-08-28-review-loop-convergence.md`, `2026-09-01-prose-edit-self-sweep.md`, `2026-09-01-loom-design-script-hygiene.md`.
- **Finding about the sample itself (important):** most plans that contain the string `NEEDS_REVISION` use it as (a) *plan-document-reviewer* vocabulary (a pre-execution review of the plan text, a third, separate layer, e.g. `2026-08-05-request-derived-authorization.md:7-8`, `2026-08-06-backlog-ready-verb-and-close-loop.md:8`), (b) prose *design content* about a mechanism named `NEEDS_REVISION` (e.g. `2026-08-13-open-question-dispatch-gate.md:186`), or (c) **whole-branch** review rounds recorded in `## Notes`/`## Decision Log`. Plans that log a genuine **per-task** SDD-triad `NEEDS_REVISION` verdict with findings text, inline, are comparatively rare — only 2 of the ~14 read plans carry one with enough detail to classify (`2026-08-21-dissolve-direction-layer.md` DL-8, `2026-08-10-design-md-spec-conformance.md` T5). This is itself evidence: the plan ledger convention foregrounds whole-branch findings far more than per-task ones.
- Per-task PASS/PASS_WITH_NOTES verdicts without NEEDS_REVISION are common (e.g. `2026-08-31-goal-create-stop-when.md:212`, `2026-08-31-loom-code-script-helper-extraction.md:587`).

## B. Per-task NEEDS_REVISION cases found

| Plan:line | Task | Reviewer finding (1 line) | Severity | Classification |
|---|---|---|---|---|
| `2026-08-21-dissolve-direction-layer.md:482-490` (DL-8) | Task 11 | Both per-task review arms (independently) found the charter still asserted two mutually-exclusive closed enums for `status` across two files (SKILL.md-style charter + frontmatter contract + template) — a contradiction that would ship to every scaffolded repo. Round 1 tried to wave it off via a different decision (DL-2); reviewers ruled that inapplicable and re-dispatched. | 🔴 fatal, instruction-class | **YES-likely**: cross-file contradiction in the FINAL diff (fixed within-task, so it never reaches merge unfixed either way) — but the defect class (a claim restated inconsistently across 2+ files) is exactly the class whole-branch review is independently documented to catch (see `whole-branch-review-catches-the-cross-artifact-defect-per-task-review-cannot.md`, `a-changelog-summarizes-layers-no-per-task-review-cross-reads.md`). No mechanism here hides it from a whole-branch reviewer who reads both files. |
| `2026-08-10-design-md-spec-conformance.md:152-172` (T5, rounds 1-4) | Task 5 | A stale claim ("the pick is the generative choice the concept and the depth/shape tokens hang off") recurred across 4 rounds of the SAME task's per-task review; each round's fix left one more pre-existing instance elsewhere in the same file, because the orchestrator's greps were keyed to already-seen phrasings, not the claim itself. | 🔴 (round 3), then 🟢 debt accepted at round 4 | **UNCLEAR→mostly YES-likely**: the defect was fully resolved inside the task before merge (all 4 rounds happened before T5 closed), so it never reaches the final diff either way — this shows per-task review doing its job (iteratively), not a case where whole-branch review is the only backstop. Counts as per-task catching something layer 2 *might* also have caught (same file, same claim), so not a clean "layer 1 exclusive save." |
| `2026-08-10-design-md-spec-conformance.md:112-122` (T3) | Task 3 | Code-quality review found a 🟡: a colon-bearing comment at component-NAME indent parses as a phantom component, silently misfiling the real component's properties under it. | 🟡, PASS_WITH_NOTES | **NO-likely**: explicitly does NOT manifest in the shipped artifact/diff ("does not manifest in the shipped artifact; neither yaml block carries comments today") — it is a latent code-path bug found by a mutation-style probe during per-task review, invisible to any reviewer reading only the diff's rendered behavior, and shipped as documented debt rather than a defect in the final text. A whole-branch reviewer reading the diff would have no textual trigger to find it either. |
| `2026-08-10-design-md-spec-conformance.md:150-165` (T2) | Task 2 | Code-quality review found a 🟡: the shared YAML walker's `_nested_mapping` silently drops a property key indented deeper than its siblings (a self-initiated 4th mutation probe beyond the prescribed 3). | 🟡, PASS_WITH_NOTES | **NO-likely**: found via an active mutation probe run BY the per-task reviewer against the code's behavior, not by reading the diff text — the same "invisible without executing/probing" mechanism as T3 above. Routed into T3's own correctness bar rather than filed as debt. |

Only 4 concrete per-task cases were found with enough detail (finding + fate) to classify in the sampled plans; the rest of the 31 `NEEDS_REVISION`-containing plans use the word for the plan-document-reviewer layer or the whole-branch layer, not per-task SDD triads.

## C. Counter-evidence — whole-branch caught what per-task missed

All of the below are `docs/loom/memory/` entries (type `practice`/`gotcha`), cited verbatim by filename:

1. `a-per-task-triad-cannot-see-cross-plugin-guard-tests.md` — a per-task triad runs only its own test file; a guard test in a *different plugin's* test dir asserting an invariant about an edited file is invisible to it. On plain-relay-contract T10, both per-task reviewers PASSed "no over-stripping" while a cross-plugin guard test (`loom-pipeline/scripts/test_family_relay.py::test_brainstorming_fork_table_default`) was RED. Whole-branch review round 2 caught it.
2. `a-changelog-summarizes-layers-no-per-task-review-cross-reads.md` — a CHANGELOG entry restating semantics owned by other files shipped through **nine green per-task verdicts** with two inversions (a `ratification` field description contradicting the grammar layer; a falsified upgrade-impact claim). Caught only at whole-branch review round 1 (decision-map protocol-hardening branch, 2026-08-29).
3. `per-task-review-misses-duplicated-fallback-fix.md` — a fix at one call-site (a KeyError fallback) PASSed both spec-reviewer and code-quality-reviewer because each was scoped to that one file's diff; three sibling call-sites elsewhere kept the unfixed read and silently lost data one stage later. Only whole-branch review's cross-task-coherence dimension caught it. **Recurred a second time** in pure documentation (a plan-format exemption example vs. a downstream reviewer-prompt Check 16 left stale) — same session, different branch.
4. `whole-branch-review-catches-the-cross-artifact-defect-per-task-review-cannot.md` — prose-edit self-sweep arc, 2026-09-01: **all six per-task reviews PASSed**; whole-branch opus review found 3 stale/false-self-claim defects (a restated finding-count off by 6, a CHANGELOG claim of a nonexistent test, a stale sibling-path date) — none visible to a reviewer scoped to one artifact.
5. `a-review-finding-list-is-a-sample-not-the-population.md` — round-3 whole-branch review named 3 stale-prose sites for a contract change; round 4 whole-branch found 2 more, one a paraphrase with no shared symbol/grep hook. (This is whole-branch-vs-whole-branch iteration, but demonstrates that even the "layer 2" pass under-reaches on first attempt — relevant to cost/rounds, §D.)

Net effect of C: the *known, named* failure mode of per-task review is structurally about scope — it cannot see files outside the task's own diff/test file, and cannot see claims that are true-in-isolation but false-against-a-sibling-copy. Every one of these defects reached whole-branch review because it survived past per-task PASS; none of the corpus's memory entries describe the reverse (a defect whole-branch review missed that per-task review had caught).

## D. Cost side — dispatch counts

From `docs/loom/plans/*.md` close-out "Observed fan-outs" rows (harness-measured, via `task_batch_replay.py observe`):

| Plan | Observed reviewer fan-outs | Rounds | Batch reopens | Note |
|---|---|---|---|---|
| `2026-08-31-batch-review-measurement-and-nudge.md:380` | 7 | 7 | 0 | Planned 7 for 12 tasks: 1 individual (T2) + 3 batch fan-outs + T11/T12 individual + 1 whole-branch context packet; whole-branch ran round 1 + 2 delta cycles (NEEDS_REVISION → PASS) |
| `2026-08-31-decision-map-script-cleanup.md:362` | 6 | 6 | 0 | Per-task individual (T4,T7,T13): 6 dispatches; symlink-guard batch: 2 rounds (1 reopen — T1 wrapper); whole-branch panel: 2 code arms + 2 docs arms, 1 round |
| `2026-08-31-goal-create-stop-when.md:215` | 7 | 7 | 0 | 1 batch fan-out (T1-T3) + 3 individual (T4,T5,T6) + whole-branch context packet + 2 individual packets for T4/T5 = 7; planned 4 fan-outs for 6 tasks |
| `2026-08-31-loom-code-script-helper-extraction.md:577` | 8 | 7 | 2 | Individual tasks 16-19: 8 reviewer dispatches; whole-branch panel: 2 arms × 3 rounds via delta confirmation |
| `2026-09-01-prose-edit-self-sweep.md:218` | 8 | 8 | unmeasured | — |
| `2026-08-31-adversarial-audit-station.md:503` | 34 | 23 | 2 | Largest observed branch in the sample |
| `2026-09-01-loom-design-script-hygiene.md:252` | 4 | 4 | 0 | Dispatch log undercounts — one pair reviewed outside `batch_review_cli` (deletion task, packet couldn't seal), so its fan-outs left no log record |

From `docs/loom/dogfood/2026-08-31-batch-knob-simulation.md` (simulation over 283 historical plans, not this arc's live plans):
- Line 9-11: today's baseline fan-out rule = one reviewer-dispatch per non-mechanical task not already in a declared batch, plus one per declared batch (mechanical tasks self-check, zero fan-out).
- Line 42-45: `fanouts_now` totals **2060** across the 283-plan corpus; only 7 of the 283 are "batch-era" plans, so this total is "almost entirely unbatched" (batching had barely been adopted at simulation time).
- Line 49-50: plans with a clustered batch ≥4 tasks: 36 of 283; ≥6 tasks: 17 of 283.
- Line 191-198, 223-231: with a batch-size cap (K=3..6) and module/lane-based clustering rules, ~32.6% of resulting batches (272 of 835) would share no file among members — i.e., roughly 1 in 3 batches pairs tasks a reviewer could not point to shared-file evidence for, a caveat against over-aggressive batching, not a per-task-vs-whole-branch number.

No plan in the sample states an explicit "reviews per plan before batching vs. after batching" pair I can cite directly — the closest is the per-plan "Observed fan-outs" rows above (post-batching, actual) plus each Notes line's stated "Planned N for M tasks" (the pre-execution estimate under the same batching regime, not a no-batching baseline). I could not find a plan that records the same task set's fan-out count WITHOUT batching for direct comparison — that number exists only in the aggregate simulation corpus above, not per named plan.

## E. Totals table

| Metric | Count |
|---|---|
| Plans examined in depth | 14 (of 96 in the 2026-08/09 corpus) |
| Plans in corpus containing string `NEEDS_REVISION` | 31 of 96 |
| Per-task SDD-triad NEEDS_REVISION cases classified (§B) | 4 |
| — of those, NO-likely (per-task-exclusive catch) | 2 (T2, T3 in `design-md-spec-conformance.md` — both found via active mutation-probing of code behavior, not diff-reading, and both explicitly noted as not manifesting in the shipped artifact) |
| — of those, YES-likely (whole-branch would plausibly also catch) | 1 (DL-8, cross-file contradiction — matches the documented whole-branch catch class in §C) |
| — of those, UNCLEAR | 1 (T5 iterative rounds — resolved within-task before merge either way) |
| Whole-branch NEEDS_REVISION events recorded in the same/sampled plans | ≥6 distinct rounds across the sample: `goal-create-stop-when` round 1 (4 code findings + 3 docs findings), `backlog-ready-verb-and-close-loop` round 1 (code + 2 docs arms), `loom-code-script-helper-extraction` (3 rounds via delta confirmation), `dissolve-direction-layer` DL-26/DL-27 (rounds 3-4, close-out), plus 5 memory-documented whole-branch catches in §C not necessarily tied to a plan read here |
| Memory entries citing whole-branch catching what per-task missed | 5 (§C) |
| Memory entries citing per-task catching something whole-branch would have missed | 0 found |
