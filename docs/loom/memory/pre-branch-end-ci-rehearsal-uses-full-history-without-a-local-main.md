---
name: pre-branch-end-ci-rehearsal-uses-full-history-without-a-local-main
description: Rehearse CI before the branch-end checkpoint in a clone that matches CI — full history (fetch-depth 0) with origin/main but no local `main` — because a depth-1 single-branch clone is harsher than CI (a mechanism measure that reads an old sha and any probe comparing against a base sha go red there for no CI-relevant reason) while the local worktree is laxer (its stale `main` hides missing refs); a red after branch-end costs a fix round plus a close-commit rebuild
type: practice
origin: 2026-09-04/05 — #789 and #790 each went red on CI after branch-end (doc-citation check, a graduated probe calling `git show main:`); artifact-language-policy rehearsed in a depth-1 clone and chased two failures CI could never produce
---

CI checks out the pull-request head with the full history and every
remote ref, so `origin/main` resolves and old shas resolve; what it does
not have is a local branch named `main`. Two ways to rehearse it wrong:

- **The working tree.** Its local `main` is whatever it was last fast-
  forwarded to — a probe written as `git show main:<path>` passes here
  and fails on CI. Also the branch base computed from local `main` can
  pull two other changes' docs into a "scope" diff.
- **A depth-1, single-branch clone.** Stricter than CI: a checker that
  recomputes a baseline from a pinned old sha reports RED because the sha
  is absent, and a template-anchor probe that compares against a base
  sha skips or fails. Neither is a CI failure; chasing them costs time.

**What matches CI:** `git clone --no-local file://<repo> <tmp>` (full
history), then `git checkout <branch>` — no local `main` exists in the
fresh clone unless you create it — and run the CI commands from the
workflow file, including the doc-citation selection line verbatim, the
package tests, and every probe that will graduate. Probes that need a
base ref use `origin/main` first and skip, never fail, when nothing
resolves.

Related: [[a-close-commit-sits-directly-under-a-checkpoint-so-any-late-fix-buys-its-own-round]],
[[a-backticked-token-with-a-slash-is-a-repo-path-to-the-citation-check]].
