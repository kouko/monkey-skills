---
name: contradicting-reviewer-verdicts-localize-the-defect-to-the-spec
description: When one reviewer arm PASSes an artifact and the other blocks it on the same round, the fault is usually in the spec both are reading, not in the work — the contradiction is the signal; re-dispatching the implementer at that moment undoes a correct fix, because one arm is enforcing a spec sentence that is itself wrong
type: practice
origin: branch docs-reuse-adequacy-brief-and-backlog (loom-code 0.43.0, 2026-08-01) — Task 1, round 2
---

On the same artifact and the same round, the code-quality arm returned
NEEDS_REVISION because a test stayed green only by keeping retired vocabulary
alive in the file it guarded, and the spec arm then returned NEEDS_REVISION
because removing that vocabulary violated the brief's explicit commitment that
those tests "stay … rather than being deleted."

Neither verdict was wrong. Neither, alone, located the fault. Following either
one produced the other's failure. The brief's sentence turned out to be false
when written — it justified keeping both tests on the grounds that both "pin
mirror-sync", which was true of one of them and never of the other.

**Why:** each reviewer judges the artifact against the documents. When the
documents contain a false statement, a reviewer enforcing it faithfully will
block correct work, and a reviewer judging the work on its merits will pass the
same artifact. The disagreement is not noise to be resolved by picking a side —
it is the only signal that points at the shared input rather than the output.

**How to apply:** when two arms disagree on one artifact in one round, stop and
read the spec sentence the blocking arm is enforcing, before re-dispatching
anything. Ask whether that sentence is true, not whether the artifact complies
with it. If the sentence is wrong, amend the spec — and record the amendment in
place with the original wording quoted, since a spec-level false claim carried
downstream is exactly the defect class most gates are blind to. Re-dispatching
the implementer on a contradiction is the move that undoes correct work.
Related: [[a-correction-issued-in-a-dispatch-packet-evaporates]] (the same round,
the mirror failure — a correction that never reached the document at all).
