---
name: a-line-cite-fixed-before-its-file-is-edited-goes-stale-again
description: A `path:line` citation written or corrected inside the same change that edits the cited file is captured against pre-edit coordinates and nothing re-checks it, so it ships stale by exactly the number of lines that change inserted above it — grep confirming the line today proves nothing about the line at commit time, and the failure repeats even for an author who just recorded the lesson, because the cite is corrected at the moment it is noticed rather than after the edits settle
type: gotcha
origin: 2026-08-07 whole-branch review of feat/u1-nightly-phase2-loop — round 2 raised five drifted cites, round 3 found two of the five drifted AGAIN by the same mechanism in the commit that "fixed" them
---

A backlog entry filed during a review round cited five `path:line`
coordinates. Review found all five stale: they had been captured while
reading the files, before the same change edited those files. Correcting them
looked trivial — open each file, `grep`, write the number down. That is
exactly what was done, and two of the five were stale again at the next
round, off by `+5` and `+2` — precisely the line counts that same commit
inserted above them, in edits made *after* the cites were corrected.

**The mechanism is ordering, not carelessness.** Within one change, a cite
and the edits that move it are both in flight. Fixing the cite the moment it
is noticed pins it to an intermediate state of the file. Nothing downstream
re-reads it: the citation pre-pass this repo runs
(`loom-code/scripts/check_doc_citations.py`) resolves paths and bounds, not
whether line N still holds the claimed content, so a cite pointing at a blank
line or an argument list passes clean.

The recurrence is the load-bearing part. The author had, in the very commit
that reintroduced the defect, written a commit trailer stating the lesson
("line cites written into a document in the same change that edits the cited
files drift silently"). Knowing the rule did not prevent it, because the rule
as stated does not say *when* to act.

**The rule that works is an ordering constraint:** make every content edit
first, then resolve every `path:line` in the change as the last step before
staging — and resolve them by opening the file and confirming the cited line
holds what the prose claims, not by trusting a `grep` run earlier in the
session. A cite is the address a future reader navigates to; in a store whose
entries are triggered by "next substantive touch of X", it is the only
navigation the reader gets.

Cheap tell that you are about to do this wrong: you are editing a
citation-bearing document and a code file in the same change, and you fix the
citation before you are finished with the code.

Sibling failure, same family, already recorded:
[[a-passage-that-describes-itself-decays-on-every-edit]] — there the claim has
no external source to open at all; here it has one, and the coordinate to it
is what rots. Its remedy (anchor by verbatim quote or stable heading, never by
position) is the stronger fix where the cited text is quotable, and is worth
preferring over a line number whenever it fits. Also related:
[[a-composed-cli-hands-back-only-the-fields-it-dispatches]].
