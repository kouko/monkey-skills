---
name: parallel-wave-commit-discipline
description: Parallel subagent waves share one git index — commit orchestrator-serially with explicit pathspecs (never git add -A, never plain git commit), verify with git show --stat HEAD
type: process
origin: PR #488 (25-commit wave, zero incidents) + loom-pipeline v1.1 batch mode PRs #483–#487 (race observed live), 2026-07-04
---

When several implementer subagents work in parallel in one checkout
(a "wave"), they share a single git index, so commits can sweep up a
sibling task's files. Two facts, both verified live:

- **Prevention works:** the orchestrator committing serially, one
  task at a time, with explicit pathspecs
  (`git commit -- <task's files>`; never `git add -A`) fully
  prevented index races across a 25-commit wave — zero incidents.
- **The race is real:** on another branch, a plain `git commit`
  (no pathspec) swept a sibling task's staged files into the commit.
  A clean-looking `git status` pre-check is NOT a guarantee — a
  sibling can stage files between your check and your commit.

**Why:** a swept commit silently attributes one task's changes to
another, corrupting review scope and history; the failure is
invisible until someone reads the commit.

**How to apply:** in any parallel-agent wave, only the orchestrator
commits; always scope the commit with pathspecs; after each commit,
verify content with `git show --stat HEAD`. Recovery if a commit
swept extra files: `git reset --soft` then `git restore --staged`
the foreign paths, and recommit scoped.
