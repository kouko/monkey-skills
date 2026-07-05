---
name: reviewer-dispatch-isolated-worktree
description: A reviewer subagent comparing commits can overwrite tracked files in the main checkout — dispatch prompts must explicitly order an isolated scratch dir or detached worktree
type: gotcha
origin: loom-pipeline v1.1 batch mode branch (PRs #483–#487, 2026-07-04)
---

A reviewer subagent asked to compare two commits checked historical
file versions out in place and OVERWROTE tracked files in the main
working checkout — clobbering the branch state other work depended
on. Observed once, live, during the loom-pipeline v1.1 review
rounds.

**Why:** "compare commit A with commit B" invites `git checkout
<sha> -- <file>` style moves; nothing in git stops a subagent from
doing that in the shared checkout, and the damage is silent until
someone diffs.

**How to apply:** when dispatching a reviewer (or any agent) that
compares commits or historical states, explicitly order isolation in
the dispatch prompt: work in a scratch directory using
`git show <sha>:<path>` redirects, or in a detached `git worktree` —
never mutate the main checkout. Do not assume the agent will choose
a non-destructive method on its own.
