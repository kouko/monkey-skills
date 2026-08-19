---
name: a-guard-whose-marker-restates-the-artifact-can-never-fire
description: A guard that looks for a literal marker RESTATED from the artifact it protects — a template's comment, a header line, a sentinel — silently stops matching the moment the artifact's wording drifts, and reads as coverage forever after because a never-firing check is indistinguishable from a check that keeps finding nothing; derive the marker FROM the artifact at check time instead of restating it, and pin that with a test that reads the artifact too
type: practice
origin: 2026-08-19 cot-explain arc (dev-workflow 2.26.0) — a checker looked for "cot-explain report template" while the shipped template said "cot-explain markdown template"; it had passed every page ever rendered
---

A checker often guards against a marker it expects to find in the material:
a template's "DELETE THIS BLOCK" comment, a scaffold header, a `TODO`
sentinel, a placeholder token. The obvious implementation restates that
marker as a literal in the checker.

Restating is the defect. The artifact and the checker then hold two copies
of one string with nothing binding them, and the artifact is the one that
gets reworded — templates get retitled, headers get rephrased, sentinels get
renamed. From that moment the guard matches nothing.

**The failure has no symptom.** A guard that never fires and a guard that
fires correctly on a clean corpus produce identical output: silence, and a
passing run. Nobody investigates a green check. The one shipped here had
been green on every page ever generated, and the wording drift that killed
it was in the very commit that introduced both halves.

Two things fix it, and the second is what makes the first stick:

1. **Derive the marker from the artifact at check time.** Read the template,
   extract its comment, search for that. The strings cannot drift apart
   because there is only one.
2. **Have the test read the artifact too.** A test that restates the marker
   reproduces the original bug one level up: it goes green against a checker
   that is looking for a string nothing produces any more.

**Why:** the intuition "a check that finds nothing is a check that found
nothing wrong" is exactly backwards for this class. Every other guard in a
suite is exercised by the cases it rejects; a marker guard is exercised only
by material nobody generates deliberately, so its own liveness is never
observed. It has to be constructed so that drift is impossible, because
drift will not be detected.

**How to apply:** when writing a check that searches for a literal drawn
from another file in the repo, do not type the literal. Read the file and
extract it. If that is genuinely impractical, add a test asserting the
literal still occurs in the source file — the assertion the guard's own
silence can never make. Related:
[[a-self-check-cannot-detect-its-own-staleness]],
[[assertion-must-encode-the-property-it-claims]],
[[a-test-can-pin-behaviour-with-a-false-rationale]].
