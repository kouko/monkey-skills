---
name: one-record-commit-per-wave-and-per-round-keeps-the-record-honest-and-the-log-short
description: Dispatch records must be committed before the work they record, and "commit it on its own" was read as one commit per record — #792's branch carried 56 commits, 16 of them dispatch records; the honest and short shape is one record commit per wave (every implementer of the wave) and one per verdict round (adversary, blind-runner, readers, and a fix round's fix implementer), so the count of `chore(loom): dispatch` commits stays ≤ waves + verdict rounds at every round boundary
type: practice
origin: 2026-09-05 review-sees-complexity-and-process-cost (loom-code 1.5.0) — build §3 said "Commit it on its own", review §2 already batched the adversary and blind-runner but recorded readers separately; a mid-round fix implementer turned out to be the one record no wave or round commit had a slot for
---

The rule that matters is the ordering one: a record written before the
work is evidence, a record written after it is a reconstruction (an
adversary caught the orchestrator's own self-dispatch committed after
the work). The commit count was never the point, but "commit it on its
own" made each record its own commit, and a branch of five tasks grew
sixteen bookkeeping commits.

**What holds now:** build appends every implementer record of a wave and
commits once (`chore(loom): dispatch <wave>`) before the first dispatch
of that wave; review appends the round's adversary, blind-runner and
reader records and commits once before any of them starts; a fix round
costs one more record commit, its fix implementer. Resumed readers need
no new record — the dispatch that made them is the one that stands.
The blind-run report can then show the arithmetic:
`git log <base>..HEAD --format=%s | grep -c 'chore(loom): dispatch'`
≤ waves + verdict rounds, where rounds are the continuous counter across
checkpoints (review §7), fix rounds included.

**Two things the batching does not change.** A record still names the
real dispatch time — five records written with the wrong calendar day
were caught by the adversary reading `git log` against `started`, and
corrected to their record commit's timestamp. And a probe author who
fixes an unseen bug in its own probe amends the original probe commit;
once a reader has seen the file, the fix is a new commit.

**How to apply:** when a bookkeeping rule says "commit X on its own",
ask whether "own" means "separate from the work" (the guarantee) or "one
per item" (the tax); write the rule as the guarantee.

Related: [[a-gate-that-binds-records-to-commit-ids-taxes-every-bookkeeping-commit]],
[[the-memory-step-belongs-before-the-closing-review-round]],
[[parallel-wave-commit-discipline]].
