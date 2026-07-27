---
name: a-passage-that-describes-itself-decays-on-every-edit
description: A sentence stating a measurable fact ABOUT ITSELF or its own container — "this note shifted every line below it by N", "§5's closing sentence says X" — has no external source to open, so the cite-and-verify machinery structurally cannot reach it, and the same change set that edits the passage re-falsifies the claim. Close-out remediation rounds on one branch kept shipping a fresh instance while fixing the previous one. State the direction, never the magnitude; anchor by verbatim quote or stable heading, never by position; enumerate rather than total.
type: gotcha
origin: loom-code 0.39.0 close-out (`feat-plan-fact-grounding`), across its whole-branch review rounds
---

A claim about an external artifact is checkable: open the artifact. That is what
a `file:line` citation buys, and what loom-code 0.39.0's reviewer cross-read
enforces. A claim about **the passage making it** has no external source to open.
Nothing in the citation machinery fires, because the sentence and its subject are
the same object — and unlike an ordinary stale fact, it is re-falsified by the
next edit to that very passage, which is usually the edit fixing the last one.

Instances from a single branch's close-out, in order. They are listed, not
counted — a total is itself a self-referential magnitude, and every attempt to
state one on this branch was wrong:

- An entry cataloguing mis-citations cited the wrong file for its own key fact
  (`test_plan_fact_grounding.py`; the pin it meant lives in
  `test_plan_obligation_sweep.py`).
- Adding an erratum header to a document pushed every line beneath it down,
  invalidating the `file:line` pointers other documents held into it.
- The fix for that said the insertion "shifted every line under it by 8" — inside
  the one sentence whose purpose was to show that line numbers decay under
  insertion. It was not true-then-decayed: the same round had just extended that
  block, so the figure was already stale as it was typed.
- The same round described a quoted sentence as "§5's closing sentence". It was
  the lead-in to that section's bullets; the actual closing line says something
  else.
- Drafting **this file** shipped more of them into review: a wrong tally of the instances
  above, a claim that one of them was "true when written", a fresh magnitude
  ("the measured figure was 13") that the same change set then made wrong again,
  and a count of invalidated pointers that reconciled to no measurable scope.

**Why:** the repo's defence against unverified claims is *cite the source and let
a reviewer open it*. That defence cannot apply here by construction. So the class
is not merely unverified but unverifiable by the available mechanism, and it does
not stay wrong in one fixed way — it re-breaks on contact. Every review round on
that branch fixed the instance in front of it and wrote a fresh one into whatever
surface the fix touched.

**How to apply:** when writing about a document from inside it, never state a
quantity or a position that editing the document can change — no line counts, no
shift magnitudes, no "the closing sentence", no "the third bullet", no tally of
the very list you are writing. Say the direction without the number ("pushed
every line below it down") and anchor by something a reader can grep: a verbatim
quote, or a stable section heading (`§3.7`). Enumerate rather than total. If a
magnitude genuinely must appear, it is a value to re-measure in the same edit
that touches the passage — the discipline
[[stamp-changelog-test-counts-at-closeout]] applies to test counts, here applied
to prose. Related: [[unifying-a-normalization-has-a-scope]] (a summary sentence
claiming more than the change earned) and
[[assertion-must-encode-the-property-it-claims]].
