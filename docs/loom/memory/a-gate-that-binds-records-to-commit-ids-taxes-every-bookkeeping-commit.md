---
name: a-gate-that-binds-records-to-commit-ids-taxes-every-bookkeeping-commit
description: When a push gate compares a probe's or verdict's recorded sha to the reviewed commit by commit id, every commit that only moves the record (a dispatch entry, a verdict, a trailer rewrite) invalidates the record and forces a re-run or a confirmation round — #791 re-ran its 1368-test suite about eight times; bind records to the content tree with the change's own review.json removed (commit-id fast path first), and a fix round then needs only the reader whose findings the fix stayed inside
type: practice
origin: 2026-09-06 checker-fix-rounds-and-tree-bound-probes (loom-code 1.4.0) — three rules recomputed against commit ids; two readers re-dispatched for every fix round; the close line needing its own round because the PR number exists only after a push
---

The push gate's job is "the tree the readers passed is the tree that
ships". Comparing commit ids was the cheapest way to write that, and it
is wrong by exactly one file: the review record itself lives in the tree
and changes with every round, so the id of "the reviewed commit" moves
whenever the record does. Everything downstream paid for it — package
tests re-run after each review-only commit, verdicts re-collected after a
message-only rewrite, a one-line close needing its own reviewers.

**What holds now:** identity is the content tree with
`docs/loom/<this change>/review.json` removed (`git ls-tree -r` minus that
one path, hashed), with the commit-id equality as the fast path. Another
change's review.json stays content. A renamed file changes the listing and
therefore the identity — correct, a rename is a change. A sha that does
not resolve still fails closed.

**Two neighbours of the same lesson landed with it.** A fix round needs
only the reader who raised the still-open findings, and only when every
path the fix touched is inside those findings' anchors; the other reader's
PASS stands — but a standing reader must be a dispatched reviewing role,
and a round with one undispatched name stands for nobody (an adversary
laundered a ghost verdict through the standing rule within the hour). And
the close line rides in the final review-only commit as
`closed <date> — branch <name>`: the branch name is known before the push,
the PR number is not, and the squash commit carries `(#N)` afterwards.

**How to apply:** when a gate keeps re-verifying something whose content
did not change, look for the identity it compares — it is probably a
container id that includes the record of the verification itself.

Related: [[the-memory-step-belongs-before-the-closing-review-round]],
[[a-close-commit-sits-directly-under-a-checkpoint-so-any-late-fix-buys-its-own-round]].
