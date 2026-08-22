---
name: an-exemption-clause-splits-a-reviewer-population-in-two
description: A judgment rule carrying carve-outs does not produce a middling catch rate across reviewers — it produces two populations, one that reaches for the exemption and applies it to everything and one that never reaches for it and catches everything, so averaging samples of such a rule reports a number no single run ever produces and more sampling widens the split instead of closing it
type: practice
origin: 2026-08-22 code-as-spec lens dogfood — five samples of the deletion class read 1/2, 2/2, 0/2, 0/2, 2/2 against a baseline of 0/4; the two deployed arms ran the same contract, model and diff and landed at opposite ends, one scoring the dimension PASS and calling it "a no-op for this branch"
---

A rule written as "delete X, except when Y" is measured the way a detector is
measured: run it N times, count catches, report a rate. That framing assumes
the misses are noise around a true rate. For a rule whose exception is a
judgment call, they are not.

The code-as-spec lens says a mechanism sentence the code already shows must be
flagged for deletion, except that the reason must survive, and except that an
absence claim is never deletable. Measured across five samples on one fixed
sandbox, the deletion class came back `1/2, 2/2, 0/2, 0/2, 2/2`. That is not a
detector running at roughly 50%. It is two behaviours: a reviewer that never
invokes the carve-outs flags every surplus sentence, and a reviewer that
invokes them once applies them to the whole diff and files nothing — the
deployed 0/2 arm scored the dimension PASS outright and wrote that it was "a
no-op for this branch". The exemption is not applied per sentence; it is
adopted as a stance.

Two consequences.

**The reported average is a number no run produces.** "3/4 on the deletion
class" was the lens's headline after the first measurement. No arm has ever
produced a partial catch except once; runs are 0/2 or 2/2. A mean over a
bimodal population describes nothing that happens.

**More samples do not converge it.** The deployed run added two samples with
the express purpose of settling the magnitude, and the split widened. When the
spread is bimodal and the mechanism for the split is visible in the rule text,
the next move is to change the text so the exemption cannot be adopted
wholesale — not to keep sampling. Sampling settles noise; it cannot settle a
fork.

The diagnostic that distinguishes the two cases is cheap: look at whether the
misses are scattered across items or clustered by run. Scattered misses are a
rate. Clustered ones — a run that catches everything or nothing — mean the rule
has a switch in it, and the thing to measure next is what flips the switch.

Related: [[a-subtractive-rule-relicenses-everything-it-keeps]] — the same
carve-out seen from the other side, where an exemption re-endorses the
sentence it spares.
