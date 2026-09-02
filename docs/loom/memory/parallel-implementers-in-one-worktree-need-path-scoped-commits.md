---
name: parallel-implementers-in-one-worktree-need-path-scoped-commits
description: Two agents committing in the same worktree each swept the other's staged deletions into their own commit (twice in one change) because `git add <paths> && git commit` commits the whole index; the fix is `git commit -F <msg> -- <paths>` (path-scoped) plus `git status --short` before every commit — or one worktree per implementer, which is what the build station's worktree action is for
type: gotcha
origin: simple-loom-flow (2026-09-02) — W0 checker commits absorbed the hooks agent's 14 `git rm`; W1 the orchestrator's docs commit 5a05dec2 absorbed the fix agent's 13 deletions; content correct, attribution wrong, reviewers could not map commits to tasks
---

The build station dispatches implementers in parallel. Sharing one
worktree is fast and was chosen here to avoid merge traffic; the cost
was two commits whose diff belonged to someone else. `git add` only
guarantees your files are staged, not that only your files are staged.

Every packet now carries both sentences: commit with an explicit path
list, and look at the index first. The station's own worktree action is
the structural fix; use it when more than one implementer will commit.
