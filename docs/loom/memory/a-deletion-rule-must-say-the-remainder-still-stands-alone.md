---
name: a-deletion-rule-must-say-the-remainder-still-stands-alone
description: A writing rule that says WHAT to delete and never says the remainder must still read on its own licenses a stranded qualifier — a clause whose antecedent was just deleted — as a clean removal; a rule can be perfectly decidable sentence-by-sentence and still damage the artifact, because decidability is a property of each sentence in isolation and readability is a property of what is left after the cut
type: gotcha
origin: code-as-spec-writing-rule (2026-08-21) — two implementers, no contact, same defect on different files
---

The code-as-spec writing rule told implementers to delete any sentence
restating what the code already shows. Two implementers applied it,
independently, to different files, and produced the same new defect:
deleting the summary sentence left the sentence after it — a qualifier
that depended on the deleted sentence for its subject — standing alone
with nothing to attach to.

- `backlog_index.py`'s `live_entries` docstring opened "Archived entries
  are never returned:" after its summary sentence was deleted. Never
  returned from WHAT? The deleted sentence was the antecedent.
- `archive_change_folder.py`'s `_validate_change_id` docstring opened
  "Wording is unit-agnostic on purpose:" the same way. Which wording?
  Same shape, same cause, a different file, no contact between the two
  implementers who hit it.

Both sites are fixed. The rule that caused them is what this entry is
about.

**Why:** four plan-review rounds on this same branch tested the rule
before it shipped, and all four asked the same question — is this rule
DECIDABLE? Can an implementer tell, sentence by sentence, whether a
given sentence restates the code? They converged on yes, and passed
the rule. None of the four asked whether APPLYING the rule left
READABLE prose behind. Those are different properties: decidability is
checked one sentence at a time, in isolation; readability is a
property of the sequence of sentences that survive the cut, and a rule
that is perfectly decidable per-sentence can still leave the artifact
worse, because deleting a correctly-identified sentence can orphan the
sentence next to it. A rule review that only exercises the delete
condition will not find this — it has to exercise the state after the
deletion.

**How to apply:** a deletion rule is incomplete until it also says what
the survivor must do. When a rule instructs deleting sentence A, add
the companion check: read sentence B — the one that follows, or the
one A was propping up — as it will read once A is gone, and confirm B
still has everything it needs (an antecedent, a subject, a referent)
without A. A qualifier, a pronoun, or a "this" left pointing at nothing
is not a clean removal; it is a second defect the deletion introduced,
and the rule must name it as such rather than leave it to be caught
by chance on the next read. When testing a rule like this before it
ships, run a check pass that asks not just "is each sentence's fate
decidable" but "does the survivor read on its own" — the two questions
find different bugs.
