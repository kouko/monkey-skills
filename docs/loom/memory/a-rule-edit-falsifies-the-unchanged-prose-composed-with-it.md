---
name: a-rule-edit-falsifies-the-unchanged-prose-composed-with-it
description: A pinned edit that changes a rule can falsify the UNCHANGED prose that composes with it — enumerating vocabulary in an untouched clause tail, a file preamble describing what its sections are, a distant heading stating the old policy — and string sweeps cannot see this class because the stale text contains no copy of the edited claim; before committing a rule change, re-read what the changed passage composes with (same paragraph's tail, the file's self-description, sibling headings) as a deliberate pass
type: gotcha
origin: whole-branch docs arms on two consecutive arcs (2026-08-04): 0.51.0 arc round 1 (checks-table heading "first failure determines verdict" vs the new full-sweep sentence; a backlog entry left prescribing shipped work) and 0.52.0 arc round 1 (fail-closed clause tail "in applying either check" after the two-part rule became three-part; dispatch-hygiene preamble claiming every section is a pointer-referenced illustration after a normative section landed)
---

Two consecutive arcs shipped a correct pinned edit and left adjacent,
UNCHANGED prose contradicting it — four instances across the two arcs,
every one caught only by a whole-artifact docs review in round 1, never
by the per-task lane that verified the pinned edit itself:

- the fail-closed enumeration's tail still said "either check" after the
  rule it closes gained a third part (the pinned replacement span ended
  one clause earlier);
- a reference file's preamble still described ALL its sections as
  extracted illustrations after a new section carrying normative rules
  was appended below it;
- a checks-table heading still read "first failure determines verdict"
  in the same file whose verdict-mapping bullet gained a
  report-ALL-failures obligation;
- a backlog entry still prescribed as future work the exact change the
  same branch shipped.

**Why:** the class is structurally invisible to the tools that guard
edits. `claim_copy_sweep` finds copies of the CHANGED claim; the stale
text here contains no copy of it — it states a neighboring proposition
(a count, a self-description, an old policy) that the change silently
falsified. Pin tests guard the inserted text, not what it composes
with. The plan reviewer sees the task's pinned span, not the paragraph
tail outside it. Only whole-artifact reading catches it, which means it
costs a review round every time — or ships, when no docs arm runs.

**How to apply:** when a task edits a rule (a count, a scope, a policy,
a section's nature), spend one deliberate pass on what the changed
passage COMPOSES with, before committing: (1) the rest of the sentence
and paragraph the pin lands in — especially enumerations and tails just
outside the pinned span; (2) the containing file's self-description
(preamble, purpose line, heading) — does it still truthfully describe
the file with the change in it; (3) sibling headings/sections in the
same file stating the old behavior; (4) any tracking artifact (backlog
entry, TODO) that prescribes the work the branch just did. Plan authors:
when pinning a replacement span, read one clause PAST the span's end
and ask whether the remainder still holds. This composes with
[[enumerate-every-copy-before-editing-a-claim-and-name-the-leaks]] —
that entry covers copies of the claim you are editing; this one covers
neighbors that state something ELSE the edit falsified, which no string
sweep can enumerate.
