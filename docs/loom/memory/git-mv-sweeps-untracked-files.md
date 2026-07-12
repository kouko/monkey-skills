---
name: git-mv-sweeps-untracked-files
description: git mv of a directory physically relocates UNTRACKED files too — a later git add of the new dir sweeps WIP into the commit; unstage by status A via git diff --cached --name-status
type: gotcha
origin: PR #440 external-repo migration (2026-06-21)
---

`git mv <dir> <newdir>` physically relocates EVERYTHING inside the
directory — including untracked files git is not managing. A later
`git add <newdir>` then stages that untracked work-in-progress as
new additions, sweeping it into the commit. Real case: a docs
directory rename carried 64 untracked WIP plan files along, and the
follow-up `git add` staged them all.

**Why:** `git mv` looks like a metadata operation on tracked files,
but it is a filesystem move; the untracked passengers are invisible
in the rename diff and only surface as unexpected `A` (added)
entries — easy to commit unnoticed.

**How to apply:** after `git mv` + `git add` of a renamed directory,
inspect `git diff --cached --name-status`: keep `R` (rename) and `M`
(modify) entries, and unstage the `A` (added) entries — e.g.
`git diff --cached --name-status | awk '$1=="A"'` to list them.
Leave the WIP untracked (updating paths inside those files for
consistency is fine).

This is the **over-inclusion** twin of
[[untracked-replacement-while-deletion-staged]] (that one is
*under*-inclusion — a staged deletion whose replacement is left
untracked, so the deletion ships alone). Both stem from the same blind
spot: **untracked files are invisible in `git diff` during a
relocation** — trust `git status`, not the diff.
