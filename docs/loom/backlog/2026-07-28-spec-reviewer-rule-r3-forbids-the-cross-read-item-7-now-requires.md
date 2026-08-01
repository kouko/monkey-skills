---
name: 2026-07-28-spec-reviewer-rule-r3-forbids-the-cross-read-item-7-now-requires
description: spec-reviewer Rule R3 forbids the cross-read item 7 now requires
status: OPEN
origin: whole-branch review of `feat-plan-fact-grounding`, finding 3. The contradiction was latent before 0.39.0; item 7 makes it adjacent — the two rules now sit ~30 lines apart in the same document.
start: next edit to either reviewer contract's discipline rules, or the next time a reviewer's R3 compliance lets a false reported figure through.
---

- Start: next edit to either reviewer contract's discipline rules, or the next time a
  reviewer's R3 compliance lets a false reported figure through.
- Origin: whole-branch review of `feat-plan-fact-grounding`, finding 3. The contradiction was
  latent before 0.39.0; item 7 makes it adjacent — the two rules now sit ~30 lines apart in
  the same document.
- What: `agents/spec-reviewer.md` (same shape in `agents/code-quality-reviewer.md`) newly
  **requires** a reviewer to independently open a cited source and confirm it says what the
  claim says (item 7), while Rule R3 in the same contract **forbids** independently confirming
  a reported test result. Both are the same epistemic act. A weak-tier reader has to reconcile
  them; on this branch 5 of 7 spec-reviewer dispatches resolved it by violating R3.
  - **Ruling from that review: the rule is wrong, not the reviewers.** R3 conflates "do not
    substitute for the verification station" (sound) with "do not independently confirm
    reported evidence" (unsound, and contradicted by this branch's own thesis).
  - **Evidence**: an implementer-reported test count of `437` that no reproducible scope
    yields survived every R3-compliant reviewer on this branch and was caught only by a
    reviewer that violated R3.
  - Not fixed here because R3 is outside this branch's diff — changing a discipline rule that
    governs every reviewer dispatch is its own change with its own review.
