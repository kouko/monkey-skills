---
name: a-shared-checkout-parallel-wave-dies-to-any-agents-stash-or-reset
description: When several implementers run concurrently in ONE git checkout, any agent — a reviewer as much as an implementer — that runs `git stash`, `git reset --hard`, or `git checkout -- <path>` wipes every sibling's uncommitted work; a spec-reviewer's "harmless" stash/pop mid-wave erased two implementers' in-progress files, so the no-stash/no-reset trap-guard must ride EVERY packet in the wave (reviewers included), or the wave runs in per-task worktrees
type: gotcha
origin: branch loom-doc-container (loom-code 0.85.0, 2026-08-17) — wave 1, T3 spec-reviewer stash vs T2/T6 implementers
---

Five implementers were dispatched into the same checkout. A spec-reviewer
for one finished task ran `git stash -u` / `git stash pop` "to check the
pre-commit state" — its pop resolved cleanly for its own paths, but the
stash had swept two sibling implementers' uncommitted edits and a new test
file into it; one implementer saw its work vanish mid-task and re-applied
it, another was blocked at the time and its edits survived only because
the pop landed before it resumed. Nothing was lost, by luck.

**Why:** the implementer packets carried "never `git stash`"; the reviewer
packets did not — reviewers were assumed read-only. A shared working tree
has no ownership: any process that rewrites it rewrites it for everyone,
and the agents that feel safest (verdict-only reviewers) are exactly the
ones no one guards.

**How to apply:** in any parallel wave sharing one checkout, put the same
trap-guard in every dispatch — implementer, spec-reviewer,
code-quality-reviewer, docs-reviewer: never `git stash`, `git reset`,
`git checkout -- <path>`, or anything else that discards working-tree
state; a reviewer that needs the pre-commit tree reads it from git
(`git show <sha>^:<path>`) or an isolated `git worktree add`, never by
moving this tree. If a wave must let agents move the tree, give each task
its own worktree instead. Related: [[a-correction-issued-in-a-dispatch-packet-evaporates]].
