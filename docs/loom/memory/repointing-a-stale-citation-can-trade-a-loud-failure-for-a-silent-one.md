---
name: repointing-a-stale-citation-can-trade-a-loud-failure-for-a-silent-one
description: A citation sweep that repoints a dangling anchor at a plausible new target makes things WORSE unless the target is checked for the cited content — an out-of-range line anchor fails loudly (the citation checker flags it), while a repointed path that resolves but does not carry the claim reads as authoritative and no tool can see it; two of eight repoints on one branch attributed a measurement and a premise to entry files that had never held them, one because the original anchor pointed at a section header rather than the figure, one because the premise had been deleted months before the migration the sweep followed
type: gotcha
origin: whole-branch review rounds 2-3 of the docs-backlog-one-entry-per-file arc (2026-08-02), monkey-skills
---

Repointing a citation is not the same operation as fixing it. A dangling
anchor — a line number past end-of-file, a `§heading` a generated file
has no headings for — **fails loudly**: `check_doc_citations.py` reports
it, and a human reading it sees an obviously broken reference. Replacing
it with a path that resolves converts that loud failure into a silent
one, and no mechanical check in this repo can tell the difference between
a correct repoint and a plausible wrong one.

Both live cases came from the same sweep, and neither was carelessness —
each looked correct from the sentence being edited:

- A spec cited *"2 of 7 filers lost their dimensional lane"* to an entry
  file that never carried the measurement. The pre-migration anchor had
  pointed at a **section header**, not at the figure, so the sweep
  repointed a citation that had no source to begin with. Grep for the
  figure across the whole store: zero hits.
- A plan said a disproved premise *"is still present at"* an entry file.
  That premise had been deleted from the source months earlier — by that
  plan's own completed task, whose GREEN criterion was that the grep
  return zero. No entry file could ever have inherited it.

**Why:** the sweep's success criterion is "the path resolves", and both
of these pass it. A sweep is a mass edit whose defects are invisible to
the mechanism that motivated it, so the sweep's own green run is not
evidence. Both were caught only by whole-branch reviewers grepping the
named target for the quoted claim.

**How to apply:** when repointing a citation, verify the **target carries
the claim**, not that the target exists — grep the new path for the
quoted content before writing the link. When it does not carry it, do not
invent an owner: either restore historical framing (what was true, when,
and that the source is gone) or drop the location and keep the claim. And
prefer a carrier that does not decay: cite by symbol name or stable
heading rather than a line anchor into a file the current work is
actively editing — on this branch one such anchor had to be repointed
twice in two days and had drifted again before the third round read it.
See [[a-passage-that-describes-itself-decays-on-every-edit]] for the
sibling failure in the other direction, and
[[verify-the-post-condition-not-that-the-edit-ran]] for the general form.
