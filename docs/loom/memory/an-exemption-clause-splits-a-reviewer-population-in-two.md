---
name: an-exemption-clause-splits-a-reviewer-population-in-two
description: A judgment rule with carve-outs does not produce a middling catch rate across reviewers — it produces runs that catch everything or nothing, so the reported average is a number no single run ever produces and more sampling widens the split instead of closing it; and identical zero scores can be reached by different mechanisms, which only the transcripts show, never the tally
type: practice
origin: 2026-08-22 code-as-spec lens dogfood — five samples of the deletion class read 1/2, 2/2, 0/2, 0/2, 2/2 against a baseline of 0/4; the two zeros turned out to have different causes, one invoking the rule's exemptions and one never engaging the rule's deletion half at all
---

A rule written as "delete X, except when Y" gets measured the way a detector
is measured: run it N times, count catches, report a rate. That framing
assumes the misses are noise around a true rate. For a rule whose exception
is a judgment call, they are not.

The code-as-spec lens says a mechanism sentence the code already shows must
be flagged for deletion, except that the reason must survive, and except that
an absence claim is never deletable. Measured across five samples on one fixed
sandbox, the deletion class came back `1/2, 2/2, 0/2, 0/2, 2/2`. Only one run
was ever partial. Runs are all-or-nothing, so the mean over them describes
nothing that happens.

**Two consequences for measurement.**

*The reported average is a number no run produces.* "3/4 on the deletion
class" was the lens's headline after the first measurement. No arm has
produced 3/4 of anything.

*More samples do not converge it.* The deployed run added two samples with the
express purpose of settling the magnitude, and the split widened. Sampling
settles noise; it cannot settle a fork. When the spread is all-or-nothing, the
next move is to find the switch in the rule text — not to keep sampling.

**And the tally hides which switch.** The two zeros looked identical in the
results table and were first written up as one mechanism. They were not. One
arm invoked the carve-outs explicitly and spared every surplus sentence with
them. The other never invoked either carve-out: it treated each surplus
sentence as a claim to verify, executed it, found it true, closed it, and
listed the whole dimension as a no-op for the branch. That is the rule's two
halves competing for one sentence — the run-what-survives duty is the more
salient one and consumes the sentence before the delete-what-is-surplus duty
sees it.

So a rule can have more than one switch, and a score column cannot tell them
apart. Read the transcripts of the zero runs before naming a cause; a
diagnosis taken from the tally will name whichever mechanism you already had
in mind.

The cheap diagnostic for the first question — rate or fork — is whether the
misses scatter across items or cluster by run. Scattered misses are a rate.
Clustered ones mean a switch, and the thing to measure next is what flips it.

Related: [[a-subtractive-rule-relicenses-everything-it-keeps]] — the same
carve-out seen from the other side, where an exemption re-endorses the
sentence it spares.
