---
name: 2026-08-28-one-test-function-bundles-fifteen-independent-claims
description: goal-create's input-floor test bundles ~15 independently-checkable claims behind one name, so a failure anywhere inside it names nothing
status: closed
origin: 2026-08-27 PR #748 whole-branch review, code arm A, which scored naming PASS_WITH_NOTES on loom-workflow/skills/goal-create/scripts/test_input_floor.py's test_defines_slots_refusal_bar_and_provenance — 359 lines, roughly 3x the largest pre-existing test-function outlier in this repo (test_check_scenario_coverage.py's 127 lines, measured at acd5a846), with no in-comment rationale for the length, against naming-and-functions.md's soft target of 20 lines and hard ceiling of 50. Deferred by the user's explicit call on 2026-08-28: the CI-repair branch it surfaced on had no business also restructuring 773 lines of pre-existing test file that earlier review rounds had already passed.
start: the next arc that touches goal-create's input-floor contract for any other reason, because splitting is cheap while the claims are already in context and expensive as a standalone errand.
---

Closed: amnesty-2026-08-30 (bulk cleanup, not per-entry adjudicated)

- Start: the next arc that touches goal-create's input-floor contract for any
  other reason, because splitting is cheap while the claims are already in
  context and expensive as a standalone errand.
- Origin: 2026-08-27 PR #748 whole-branch review, code arm A, which scored
  naming PASS_WITH_NOTES on
  loom-workflow/skills/goal-create/scripts/test_input_floor.py's
  test_defines_slots_refusal_bar_and_provenance — 359 lines, roughly 3x the
  largest pre-existing test-function outlier in this repo
  (test_check_scenario_coverage.py's 127 lines, measured at acd5a846), with no
  in-comment rationale for the length, against naming-and-functions.md's soft
  target of 20 lines and hard ceiling of 50. Deferred by the user's explicit
  call on 2026-08-28: the CI-repair branch it surfaced on had no business also
  restructuring 773 lines of pre-existing test file that earlier review rounds
  had already passed.
- What: `test_defines_slots_refusal_bar_and_provenance` asserts roughly fifteen
  separable prose claims — the two slot names, the refusal rule, the
  vague-goal claim, each clause of the bar, and every provenance tag — behind
  a single test name. The consequence is not that the assertions are wrong;
  it is that a failure anywhere inside gives no localized signal about which
  claim broke, which is the isolation half of F.I.R.S.T.
- Shape of the fix: one test per claim, named for the claim, sharing the
  section-extraction helpers the file already has. The verbatim pins move
  unchanged — this is a regrouping, not a rewrite, and no assertion should be
  weakened or dropped in the split.
- Guard against the obvious wrong version: splitting by *paragraph of the
  source document* rather than by *claim* would reproduce the same problem at
  a smaller size. The unit is the thing a reader would want named when it
  fails.
- Closed for real on branch `goal-cerate-r2` (goal-create Stop-when repair, 2026-08-31): `test_defines_slots_refusal_bar_and_provenance` split into 12 claim-named tests plus a 50-code-line guard (`test_no_test_function_exceeds_fifty_lines`); assert count 62 → 63 (+1 = the guard), no assertion weakened.
