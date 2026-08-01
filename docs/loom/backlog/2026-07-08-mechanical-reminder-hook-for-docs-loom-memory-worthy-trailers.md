---
name: 2026-07-08-mechanical-reminder-hook-for-docs-loom-memory-worthy-trailers
description: Mechanical reminder hook for docs/loom/memory-worthy trailers
status: PARKED
origin: PR #521 review discussion (2026-07-08) — an external critique suggested a `PostToolUse` hook enforcing this "100% declaratively"; evaluated and deliberately deferred, not built, because (a) PR #521's process fix hasn't had a single real-world data point yet, (b) "is this content memory-worthy" is a semantic judgment a hook can't reliably make — at best a heuristic reminder (git-memory returned a non-empty trailer set AND no docs/loom/memory/ file touched in this commit → warn), which risks false-positive noise on the many routine commits that correctly have local-only trailers.
start: the "trailers written but docs/loom/memory not checked" lapse (documented only in this session's private machine-local auto-memory as `feedback_fold_repo_memory_writes_into_same_branch_pr.md` — not yet promoted to a repo-committed `docs/loom/memory/` entry) recurs a THIRD time even after PR #521's fix (the finishing-a-development-branch Step 6/Step 8 re-sequencing). Two occurrences (PR #519, PR #520) already triggered the process fix in #521; a third occurrence AFTER that fix is the signal this needs mechanical backup, not just better sequencing.
---

- Start: the "trailers written but docs/loom/memory not checked" lapse
  (documented only in this session's private machine-local auto-memory
  as `feedback_fold_repo_memory_writes_into_same_branch_pr.md` — not yet
  promoted to a repo-committed `docs/loom/memory/` entry) recurs a THIRD
  time even after PR #521's fix (the
  finishing-a-development-branch Step 6/Step 8 re-sequencing). Two
  occurrences (PR #519, PR #520) already triggered the process fix in
  #521; a third occurrence AFTER that fix is the signal this needs
  mechanical backup, not just better sequencing.
- Origin: PR #521 review discussion (2026-07-08) — an external critique
  suggested a `PostToolUse` hook enforcing this "100% declaratively";
  evaluated and deliberately deferred, not built, because (a) PR #521's
  process fix hasn't had a single real-world data point yet, (b) "is
  this content memory-worthy" is a semantic judgment a hook can't
  reliably make — at best a heuristic reminder (git-memory returned a
  non-empty trailer set AND no docs/loom/memory/ file touched in this
  commit → warn), which risks false-positive noise on the many routine
  commits that correctly have local-only trailers.
- What: if triggered, build a lightweight `PostToolUse` hook on `git
  commit` that fires the heuristic above as a non-blocking reminder
  (never a hard block — the judgment call stays with the agent/user).
  Do not attempt to make the memory-worthiness decision itself
  mechanical.
