---
name: the-memory-step-belongs-before-the-closing-review-round
description: A commit that lands after the branch-end checkpoint always costs a confirmation round plus a re-created close commit, so probe graduation and docs/loom/memory entries are build's last-wave task (W<n>-memory), done after package tests and before the single closing review call; ship then writes only trailers and questions — three changes (#789, #790, #791) paid the post-review round before the order was fixed, #791 three times
type: practice
origin: 2026-09-05 memory-step-before-branch-end-and-prose-pin-rule (loom-code 1.3.1) — the ship station scheduled graduation and store entries after the branch-end review by design, guaranteeing a post-review commit every change
---

The close-commit shape (`HEAD` review-only, `HEAD^` the one-line close,
`HEAD^^` a checkpoint) is a good invariant: the tree the readers passed is
the tree that ships. What made it expensive was where the memory work was
scheduled. Ship's memory step wrote store entries and graduated probes
*after* the branch-end round had passed, so every change produced at
least one commit the readers had not seen, and the invariant then demanded
a confirmation round and a rebuilt close commit. Three changes in a row
paid it; the third paid it three times because each late fix restarted
the dance.

**What holds now:** build owns the memory step. The plan's last wave ends
with a `W<n>-memory` task whose implementer is the orchestrator itself
(`fresh_context: false`, dispatch entry first). Order for the last wave:
package tests → memory step (graduate probes as byte copies, write store
entries, regenerate the index, `git add` the new files before a
path-limited commit) → one closing call to the review station recorded
`scope: branch-end`. Ship finds nothing left to graduate or store; if it
does, that is a build task and a fresh checkpoint, never a commit made at
ship.

**The general shape of the lesson:** when a gate requires "the reviewed
tree is the shipped tree", every step that produces a commit must be
scheduled before the review, or the gate taxes it. Look for the step that
runs after the review by design — it is the one to move.

Related: [[a-close-commit-sits-directly-under-a-checkpoint-so-any-late-fix-buys-its-own-round]],
[[a-prose-pin-must-require-an-affirmative-un-negated-sentence]].
