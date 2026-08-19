---
name: a-stamp-recording-an-outcome-without-its-subject-cannot-go-stale
description: A provenance field that records WHAT a check concluded but not WHAT it examined survives every later edit and keeps advertising the old result, so the artifact reports a verdict about text the checker never saw — bind the outcome to a fingerprint of the subject and let the consumer render disagreement as `stale`; the field most likely to be missing this is the one that reports checking, because it reads as already being the safeguard
type: practice
origin: 2026-08-19 cot-explain arc (dev-workflow 2.26.0) — the `verified` gate stamp shipped as a bare outcome while its sibling `fidelity_checked` had carried a body hash from the start
---

A generated artifact carries provenance fields written by tooling: "the
gate passed", "the review approved this", "tests ran". Recording the
OUTCOME alone is the natural first implementation, and it is inert against
the failure it exists to catch.

Nothing invalidates the field. The artifact is edited afterwards — by a
person, by a later pipeline stage, by a fix applied between the check and
the publish — and the field still says `pass`. A reader sees a verdict
rendered next to content that verdict never covered. The field is now worse
than absent: absent reads as "unchecked", and unchecked prompts a check.

The fix is one line of design: **record the outcome together with a
fingerprint of what it judged**, and have the consumer compare that
fingerprint against what it is actually rendering, showing `stale` on
disagreement. Two details from the arc that made it work:

- **Fingerprint the subject, not the container.** Hashing the whole file
  invalidates the verdict when a title or a path format changes, and a
  check that fires on harmless edits is one people learn to wave through.
  Hash the part the verdict is about.
- **The producer and consumer must compute it identically.** Two hash
  functions in two scripts is a divergence waiting to happen; pin it with a
  test that runs both.

**Why:** the blind spot is structural, not careless. Sibling fields on the
same artifact had the binding — the human-judgement verdict file carried a
reviewed-content hash — and the machine-written gate field did not, because
"the gate ran" felt like a fact about an event rather than a claim about a
document. It is a claim about a document. Anything that says "this was
checked" must also say what.

**How to apply:** auditing an artifact's provenance fields, ask of each one
"if someone edits the body now, does this field become false?" Every field
where the answer is yes needs a subject fingerprint. Expect the check-status
field itself to be the one that lacks it. Related:
[[a-self-check-cannot-detect-its-own-staleness]],
[[a-guard-whose-marker-restates-the-artifact-can-never-fire]].
