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

**2026-07-24 variant (kpi-tearsheet branch, concurrent-review false
🔴s):** MUTATION TESTING is the same hazard even when the reviewer
restores perfectly. A spec-reviewer mutation-tested the shared
checkout (mutate → run → stash-restore, net-zero when done), but two
OTHER reviewers running CONCURRENTLY `git diff`-ed the tree during
the mutation window and each filed a fatal "uncommitted regression"
finding (`pass  # mutated: marker suppressed`) — two contaminated
verdicts, resolved only by the orchestrator re-verifying reality
(diff vs HEAD empty + full re-run green). Rule: reviewer dispatch
prompts must order mutations to run ONLY in an isolated copy (e.g.
`/private/tmp` scratch clone), never mutate-and-restore in the shared
tree; and an orchestrator receiving a "working-tree regression"
finding while sibling reviewers are in flight must re-verify the tree
itself before dispatching a fix.
