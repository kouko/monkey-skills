---
name: parallel-wave-commit-discipline
description: Parallel subagent waves share one git index — commit orchestrator-serially with explicit pathspecs (never git add -A, never plain git commit), verify with git show --stat HEAD; and NEVER recover a swept commit with reset --soft while siblings are still committing — if a sibling committed after you, the reset orphans THEIR commit too (verify HEAD is still yours first)
type: process
origin: PR #488 (25-commit wave, zero incidents) + loom-pipeline v1.1 batch mode PRs #483–#487 (race observed live), 2026-07-04; reset-orphaning variant + pathspec-insufficiency observed live on loop-convergence-fixes (2026-07-18, incident log in docs/loom/plans/2026-07-18-loop-convergence-fixes.md)
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

**2026-07-18 hardening (loop-convergence-fixes incident, two new facts):**

- **The reset recovery recipe above is UNSAFE while siblings are still
  committing.** An implementer recovered its own swept commit with
  `git reset --soft HEAD~1` — but by then HEAD had advanced past two
  sibling commits, so the reset orphaned a sibling task's reviewed
  commit and another task's content silently rode into a later
  unrelated commit. Before ANY reset-based recovery in a shared tree:
  `git log --oneline -3` and confirm HEAD is still YOUR commit; if it
  is not, do NOT reset — surface to the orchestrator, which re-commits
  the affected files verbatim instead (content survives on disk; only
  attribution needs repair, and the repo squash-merges anyway).
- **Pathspec scoping was observed insufficient under live concurrency**
  (`git commit -- <paths>` and `--only` both reportedly swept
  concurrently-staged foreign files in one session). Treat pathspec as
  necessary, not sufficient: the post-commit `git show --stat HEAD`
  verify is the load-bearing check, and implementer-committed waves
  should be kept small or downgraded to orchestrator-serial commits
  when many agents share one index.

**2026-07-24 addition (kpi-tearsheet T3/T4 interleave):** commit a
finished task BEFORE dispatching its same-file successor. The
orchestrator dispatched T4 (same files as T3) while T3's verdict-
approved state was still uncommitted; by the time T3's commit point
arrived, T4's edits had interleaved into the same files and the two
tasks had to ship as ONE combined commit (disclosed, but
bisectability lost). The wave rule above covers parallel SIBLINGS;
this covers sequential same-file SUCCESSORS: the successor's dispatch
gate is the predecessor's commit, not its verdict.
