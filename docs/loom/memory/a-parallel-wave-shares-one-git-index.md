---
name: a-parallel-wave-shares-one-git-index
description: Six implementers dispatched in parallel onto one worktree share a single git index — a sibling's pathspec-less `git commit` swept another task's already-staged files into its own commit, and a sibling's `git reset --soft HEAD~1` un-committed a DIFFERENT sibling's already-landed commit; a worker also ran `git stash push/pop` against an explicit prohibition (the stack happened to come back intact) — every worker packet must mandate a scoped commit command and ban reset/stash outright, because prose alone did not hold
type: gotcha
origin: adversarial-audit-station arc, docs/loom/plans/2026-08-31-adversarial-audit-station.md — ca76d2fe (Task 1's files landed under Task 8's message via a pathspec-less commit), 710ff268 un-committed by a sibling's `git reset --soft HEAD~1` then re-committed as 7d9f3c91
---

The plan dispatched six implementers in parallel against one shared
worktree (one working tree, one index, one `.git`). Two failure shapes
surfaced from that sharing, both caused by a sibling task's git command
having no pathspec or scope of its own: (1) a `git commit` with no
`-- <paths>` picked up whatever was staged at that moment, including
files another task had staged for its own commit — the result (ca76d2fe)
carries Task 1's files under Task 8's commit message; (2) a
`git reset --soft HEAD~1`, run to undo one task's own mistake, actually
uncommitted a SIBLING task's already-landed commit (710ff268), because
`HEAD~1` is a position in the shared branch history, not a reference to
"my last commit" — recovery re-committed it as 7d9f3c91. A separate
worker also ran `git stash push`/`pop` despite an explicit prohibition
in its packet; in that instance the stash stack came back intact, but
only by luck (nothing prevented a fourth party from stashing/popping in
between).

**Why:** `git commit` and `git reset` operate on the shared index and
branch HEAD, not on a task-scoped view of them — in a single-worktree
parallel wave there is no isolation between workers' git state, so any
command that doesn't explicitly scope itself to that task's own paths
or its own commit can silently act on a sibling's work instead.

**How to apply:** every worker packet in a parallel wave on one
worktree must require `git commit -m "…" --only -- <this task's exact
paths>` (never a bare `git commit`), and must prohibit `git reset` and
`git stash` outright — not just discourage them in prose. Prose
prohibition was tried here and one worker still ran `stash`; the
durable guard is a hook that rejects unscoped commit/reset/stash
commands during a parallel wave, not a sentence in the dispatch
(residual filed in the arc's dogfood record,
docs/loom/dogfood/2026-08-31-adversarial-audit-station.md).
