---
name: a-dispatch-packets-own-wording-becomes-the-artifacts-defect
description: A worker reproduces the dispatch packet's wording faithfully, so any defect in that wording — a completion-tense verb for future work that has not yet run, a mis-attributed citation, an instruction that generalizes over items which are not alike — lands in the durable artifact as the worker's output and is then defended by the review round as if the worker had chosen it; audit the packet's own claims before dispatch, because the packet is the artifact's first draft
type: gotcha
origin: PR #693 (feat/open-question-dispatch-gate, merged 2026-08-14) — five occurrences in one arc; recorded 2026-08-18 in the arc's residue pass
---

Dispatch packets are written fast, in the orchestrator's voice, about
work that has not happened yet. A worker treats that prose as
specification and reproduces it. Every wrong assertion inside the
packet therefore arrives in the artifact wearing the worker's
authorship — and the reviewer, who compares artifact against packet,
finds them consistent.

Five occurrences in a single arc (`feat/open-question-dispatch-gate`):

1. and 2. Two packet sentences written in **completion tense** about
   legs that had not yet run produced two backlog records asserting
   Task 4 and Task 7 had shipped. Neither had. The records are read
   months later as ground truth.
3. The Task 8 RED was drafted as a grep for a **completion-tense**
   phrase — satisfiable by writing the phrase, and nothing else.
   Review caught this one; the shipped plan carries the corrected
   decision-tense RED plus the paragraph explaining why
   (`docs/loom/plans/2026-08-13-open-question-dispatch-gate.md`
   §Task 8 Acceptance — read the rationale paragraph, not the RED
   line, which is now the fixed version).
4. A docstring citation was mis-attributed in the artifact because the
   packet mis-attributed it first.
5. An instruction to "treat all three lines alike" was wrong because
   one of the three was a scalar and the other two were ranges — the
   packet generalized over items that were not alike, and the worker
   applied the generalization.

**Why:** the normal defenses do not see it. The worker is obedient by
contract, so it will not push back on a plausible-sounding claim about
work it cannot observe. The spec-reviewer checks artifact against the
task's stated requirements — and the wrong claim IS the stated
requirement. Only a reviewer who independently checks the packet's
assertions against the repo can catch it, and no gate assigns that
duty. Cost in this arc: two false ground-truth records that shipped,
plus review rounds spent enforcing a wrong criterion against a correct
artifact ([[a-correction-issued-in-a-dispatch-packet-evaporates]] is
the sibling failure — the correction issued in the packet instead of
the plan).

**How to apply:** before dispatching, re-read the packet as a set of
factual claims about the repo and check each one. Three specific
audits, in order of observed frequency: (1) **tense** — every verb
describing another task's work must be decision-tense ("committed to",
"decided") unless that work is already merged; a completion-tense verb
about a pending leg is a false claim the worker will faithfully
transcribe; (2) **acceptance targets** — if the RED greps for a phrase,
ask whether writing the phrase satisfies it, and if so change the
target to something true at authoring time or add a second leg
([[grep-tests-scope-to-measured-neighborhood]]); (3) **any instruction
that generalizes over N items** — enumerate the N and confirm they are
actually alike, because "treat all three the same" is where a scalar
hides among ranges. A correction made after dispatch does not undo
this: the wording has already become the artifact.
