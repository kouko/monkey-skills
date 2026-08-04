---
name: 2026-08-04-directive-1-does-not-say-what-follows-a-failed-authorized-round
description: the convergence contract defines the STOP after round 2 but not the state after a user-authorized round also ends NEEDS_REVISION
status: OPEN
origin: PR #645 — its own verification round (an authorized round 3) ended NEEDS_REVISION, landing in a state the contract does not describe
start: next edit to `requesting-docs-review` Directive 1, or the next time an authorized round fails
---

## The gap

Directive 1 covers two states precisely:

- round 2 ends passing → the review ends;
- round 2 ends `NEEDS_REVISION` → STOP, present the three options, and a
  third round runs only on explicit user authorization.

It does not say what happens when that authorized round **also** ends
`NEEDS_REVISION`. PR #645 reached exactly there.

**Half of it is already written, and the gap is the other half.** The
authorization rule generalizes on its own: `SKILL.md:63` states "A round
past the cap needs explicit user authorization (Directive 1)", which covers
a fourth round as much as a third. What no passage states is whether the
**three-option STOP handoff** (Directive 1's fix-plus-verification / fix-and-
ship / ship-with-residuals menu) recurs after a failed authorized round, or
whether something else governs there. Do not add a clause about
authorization; it exists.

## What the answer probably is, and why it is not written yet

The likely shape is that the same three-option STOP repeats, with the round
counter irrelevant: Directive 1 already says the criterion is **how large the
remaining fixes are, not how many rounds are left**, and that criterion does
not change on the fourth round. Writing it as "every round past the cap ends
in the same STOP" would close the gap in one sentence.

Two reasons it was not written on the branch that found it:

- The branch was already three rounds deep and its own contract says a fix
  round is where defects get written; adding a directive edit at that point
  is the move Directive 1 tells the reader to weigh against.
- The right wording may want a bound. "Repeat forever" is honest but invites
  the loop this whole contract exists to end; "stop after N" reintroduces the
  round-count criterion the contract just replaced with fix size. That is a
  design question, not a transcription one.

## Adjacent, do not conflate

Directive 4's two sentences use different tests for the same thing — "prose
the branch left unchanged" versus "settled narrative" — and neither defines
"settled". Raised as an out-of-scope observation by a #645 verification arm,
carried as a 🟢 residual there. Same file, different defect; fix them in one
pass if convenient, but they are not the same item.
