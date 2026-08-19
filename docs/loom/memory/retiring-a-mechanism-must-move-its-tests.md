---
name: retiring-a-mechanism-must-move-its-tests
description: When a redesign RETIRES a guard and MOVES its property to a new home, the guard's adversarial tests must move with it — deleting them alongside the old machinery leaves the property implemented-but-unverified, a coverage regression a "tests still green" check cannot see.
type: practice
origin: branch feat-kpi-obs-history (2026-07-22) — T9 retired the read-time unit-scale inference (and T8) and moved whole-word magnitude matching to the 8-K producer; the old word-boundary tests were deleted with the read-side scaler and not replaced
---

Task 9 replaced a read-time scale INFERENCE (parse a magnitude word out of
a free-text unit in `history`) with an explicit per-point `scale` set at the
producer. The whole-word discipline "millionaire ≠ million" moved from the
retired `kpi_store._scale_multiplier` to the new `kpi_8k_candidates.
_scale_from_unit`. The two tests that pinned that discipline
(`test_scale_multiplier_matches_scale_word_as_whole_word`,
`test_history_word_boundary_unit_is_not_scaled`) were deleted *with* the
read-side scaler — correct, they tested dead code — but **no replacement
pinned the same property at its new home**. The implementation was correct;
the property was simply unverified. The full suite stayed green because the
happy path (`unit="millions"→1e6`) was tested; the adversarial
`"millionaire"→1` case had silently lost its only guard.

**Why:** a redesign's diff shows tests being *removed*, and "removed a test
of retired machinery" reads as legitimate cleanup — indistinguishable, at
diff-review speed, from "removed a test of a property that still exists,
just elsewhere." The green suite confirms nothing, because a moved-but-
untested property fails only on the adversarial input no remaining test
exercises. Only reading each deleted test and asking "does the PROPERTY it
pinned still exist somewhere?" catches it — which is a whole-branch /
spec-review lens, not a per-task one (the per-task triad passed T9).

**How to apply:** when a task retires a mechanism, for each test it deletes,
classify the test: (a) tests behavior that no longer exists anywhere → delete
freely; (b) tests a PROPERTY that moved to a new home → the test must be
rewritten against the new home in the SAME task, not dropped. Grep the
adversarial inputs (the boundary/negative cases, not the happy path) and
confirm each still has a live assertion. "Net test count went down and the
suite is green" is not evidence — a lost adversarial case is invisible to it.

Related: [[construction-guaranteed-invariant-proves-nothing]] (the moved
property here was itself a whole-word guard against a clean-looking wrong
scale); [[count-only-regression-pins-false-confidence]] (a green count
hides a lost exemplar).

**Increment (2026-08-19, branch `plan-field-microstructure`) — classification
(a) misfires when the deleted test was the only thing exercising a still-live
shared path.** That arc removed a length ceiling on one plan field. The test
asserting the ceiling tested behaviour that genuinely no longer existed
anywhere, so rule (a) above says delete it freely — and that reading was
correct about the *property*. It was wrong about the *path*: that test was the
only case in the suite that drove the checker's parsing branch for that field
at all. The branch stayed live, serving a second rule that survived the
removal, and after the delete nothing exercised it. Nothing went red, because
nothing was supposed to.

**Why:** rule (a) asks where the *property* went, which is the right question
for coverage of a behaviour and the wrong question for coverage of a
mechanism. A test usually pins one property while incidentally being the sole
caller of the machinery underneath it. Removing the property does not remove
the machinery, and a suite cannot report a path it no longer reaches.

**How to apply:** before deleting a test under rule (a), ask the second
question too — *which production code does this test uniquely reach?* Run the
suite with the test removed under coverage and diff the reached lines, or grep
the callers of each function the deleted test touched. Any line that goes from
covered to uncovered while still being live code needs a replacement test at
that line, even though the property being retired is genuinely gone.
