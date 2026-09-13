---
name: a-worktree-cleanup-by-pattern-match-destroys-other-peoples-work
description: A worktree-cleanup command written as a pattern match over `git worktree list` output deletes worktrees that were never yours, because each line carries the branch name as well as the path — and with `--force` plus a suppressed stderr there is no guard and no warning left; remove worktrees one at a time by their known absolute path, never by a filter over a listing
type: gotcha
sources:
  - resource: 2026-09-11 session, loom-memory arc — `git worktree list | grep <word> | awk '{print $1}' | while read w; do git worktree remove --force "$w" 2>/dev/null; done` removed five worktrees belonging to unrelated work; every branch survived, every uncommitted file in them did not
---

The command looked narrow. It was not.

```sh
git worktree list | grep probe | awk '{print $1}' \
  | while read w; do git worktree remove --force "$w" 2>/dev/null; done
```

Five worktrees went, none of them the intended one's siblings. All five
branches survived — `git worktree remove` does not touch refs — so the loss
was invisible in `git branch` and total in the directories: **uncommitted
work in a removed worktree is unrecoverable.** It is not in the object
store, not in a stash, not in the reflog.

**Four independent mistakes, each of which alone would have saved it.**

1. **Filtering instead of naming.** The paths to remove were already known.
   A filter was used anyway, so the command's blast radius was decided by a
   string, not by a list.
2. **`git worktree list` lines contain branch names.** Each line is
   `<path> <sha> [<branch>]`. A pattern intended to match a path segment
   also matches any branch whose name contains it — which is how worktrees
   whose paths shared nothing with the pattern were selected.
3. **`--force` disabled the only guard.** Without it, `git worktree remove`
   refuses a worktree with modified or untracked files. That refusal is
   exactly the signal that the selection was wrong, and it was turned off
   in advance.
4. **`2>/dev/null` suppressed what was left.** Every warning the command
   would have printed went to the same place.

Nothing here is a git defect. Each step is reasonable alone; the failure is
that they compose into an unguarded loop.

**How to apply.**
1. Remove worktrees **one command per worktree, by absolute path**. If that
   feels tedious for five, that tedium is the guard.
2. Never pipe `git worktree list` into a removal. If you must enumerate,
   print the selection and read it before running anything that deletes.
3. `--force` on a removal is a statement that you already know the worktree
   is clean. Verify that separately rather than asserting it through a flag.
4. Never suppress stderr on a destructive command.
5. When it has already happened: say which paths went, say that branches
   survived and uncommitted content did not, and **do not invent an
   explanation for a match you cannot account for.** One of the five could
   not be explained by the pattern, and saying so was the only honest
   report available.

Related: [[a-shared-checkout-parallel-wave-dies-to-any-agents-stash-or-reset]]
and [[a-parallel-wave-shares-one-git-index]] — both are the same family, an
agent's convenience command reaching state that belongs to someone else.
