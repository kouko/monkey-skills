---
name: two-reviewers-disagreeing-on-a-count-means-it-was-never-countable
description: When two independent reviewers each count the same population carefully and return different totals, the disagreement is not a tie to break — it says the counting rule was never written down, so every total is defensible under one reading and wrong under another; replace the number with the command that derives it, and expect the command to need the same scrutiny the number did
type: practice
origin: pin-granularity arc (2026-08-28) — three review rounds spent refuting three different totals for one population, ending with two `opus` arms reporting 14 and 15 after each counting independently
---

A backlog entry stated how many sites carried a duplicated idiom. Round after
round, a reviewer ran the count and refuted it — five packages became four,
twelve sites became fifteen, then the two final arms counted independently
and returned **14 and 15**. Neither was careless; both showed their work.

The cause was not arithmetic. "The same idiom" spanned a one-line ternary and
a five-line `if/else`, and no draft ever wrote down which to count. One arm
said so directly: under a ternary-only rule the total is 14, under an
idiom-inclusive rule it is 20, and **neither yields 15**. The number was
never a fact about the repository; it was a fact about an unstated predicate.

**Why this is worth its own entry.** The instinct on contradictory reviews is
to adjudicate — get a third opinion, break the tie. That is right when the
reviewers disagree about whether something is *true*. It is wrong here: they
agreed on every observation and differed on what was being asked. Adjudicating
picks a winner and leaves the defect (the missing rule) in place, which is
how three rounds were spent.

**The replacement is not automatically safer.** Swapping the number for a
grep looked like the fix and was refuted the same way twice:

- the command was scoped to the population the work had ALREADY fixed, then
  labelled as the population that REMAINS — returning zero hits in the very
  bullet it was meant to substantiate;
- its caveat warned about false positives only. A reader takes "expect noise"
  as "this is the whole set, some of it spurious". The command also **missed**
  resolvers built on `re.findall(r"^## ...")`, which match no `.find(`/`.index(`
  and never appear. *Expect noise* and *expect gaps* are different warnings and
  only one was given.

**How to apply.**

1. Before writing a count, write the predicate: what counts as one, and what
   near-miss is excluded. If you cannot state it in a sentence, the number is
   not ready to be written.
2. Prefer the command over the number, but scope the command to the
   population the sentence beside it is about — and say which direction it
   errs in. Both directions, when both apply.
3. Treat two careful reviewers disagreeing as a defect report about the
   question, not about either answer. The fix is upstream of both.
4. A count in a durable document goes stale the first time a file is added;
   an enumeration in a docstring is the same defect with a shorter fuse. If
   the population is only knowable by reading, say that instead of listing.

Related: [[contradicting-reviewer-verdicts-localize-the-defect-to-the-spec]]
(disagreement as a pointer at the shared input — the same move, applied to
spec compliance rather than to a countable population);
[[a-number-in-prose-needs-a-test-that-recomputes-it]] (the staleness half of
this: a number true when written and false later); [[a-bounded-check-must-state-its-bound]].
