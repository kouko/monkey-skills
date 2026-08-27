---
name: a-verbatim-pin-proves-nobody-edited-the-sentence
description: A verbatim pin is satisfied by its sentence surviving unedited, so a claim the sentence makes about things living elsewhere — how many surfaces do X, which files are covered — goes false while the pin stays green and nothing has to be edited for that to happen; a claim of that shape needs a check that recomputes it from the population it describes, and that recomputation must be unable to pass vacuously
type: gotcha
origin: PR #748 (goal-create — round-1 whole-branch review finding, 2026-08-27)
---

A skill's `## Invocation` section said it is named as an option "at exactly two
points", and a test pinned that sentence verbatim precisely because it was
load-bearing. The same branch then added a third such point in a different
plugin. The sentence was now false, the pin was still green, and nothing had
been edited to make that happen — the drift arrived from outside the pinned
text. A whole-branch reviewer caught it by reading both files; no mechanism
could have.

**Why:** a verbatim pin answers "did anyone reword this?", which is a real
question and not the one a counting claim raises. The failure mode is the
inverse of the usual one: the pin holds *because* the author left the sentence
alone, so the more disciplined everyone is about not touching pinned prose, the
longer the false claim survives. This is distinct from
[[a-doc-pin-makes-a-prose-defect-permanent]], where the prose was already wrong
when pinned and the pin froze it; here the prose was true when pinned and the
world moved underneath it. It is the same shape as
[[enumerate-every-copy-before-editing-a-claim-and-name-the-leaks]] seen from the
other end — that entry is about finding every copy before an edit, this one is
about a claim that decays with no edit at all.

**How to apply:** when a sentence states a count, a list, or a coverage claim
about anything outside its own file, pair the verbatim pin with a check that
rebuilds the claim from the population and compares. Keep both: the pin guards
the wording, the recomputation guards the arithmetic, and a fourth item breaks
the recomputation first while the stale pin then breaks on the edit that fixes
it — coordinated failure rather than silent drift. Scope the scan to the real
population, never to the currently-known answer, or it cannot falsify anything;
assert the scan found something, so an empty sweep fails loudly instead of
passing as agreement; and mutation-check it by planting one more member and
confirming the check names it.
