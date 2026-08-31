---
name: 2026-08-31-sdd-existence-check-refuses-deletion-tasks
description: subagent-driven-development Step 3's `git cat-file -e <reviewed_sha>:<path>` pre-dispatch check fails by construction for a task whose declared Files touched are deleted, so a deletion task cannot enter individual review without an orchestrator-side deviation
status: open
origin: 2026-08-31 — branch loom-script-refactor-phase2, Task 4 (`git rm claim_ticket.py test_claim_ticket.py`); deviation recorded as plan DL-1 and repo memory `deletion-task-review-packet-fails-the-cat-file-existence-check`
start: event — the next plan that carries a deletion-only task, or the next edit to subagent-driven-development/SKILL.md Step 3
---

SDD Step 3 requires, for every path in the task packet's `Files touched`,
`git -C "<target_repo>" cat-file -e "<reviewed_sha>:<path>"` to succeed
before any reviewer is dispatched, and says any failure REFUSES the
fan-out. A task that deletes files declares exactly the paths that are
absent at every SHA after its commit, so the literal rule makes such a
task unreviewable on the individual path.

The intent of the check (reviewers read immutable SHAs, never the working
tree) is preserved by scoping the fan-out to the deletion commit: read the
removed bytes at `<commit>~1:<path>`, prove absence at `<commit>:<path>`,
confirm `git show --stat <commit>` names only the declared paths.

Candidate fix: add one clause to SDD Step 3 — "for a path the task
declares as deleted, the check is inverted: `cat-file -e` at
`reviewed_sha` MUST fail and MUST succeed at `<reviewed_sha>~1`" — and let
the plan grammar mark deleted paths (e.g. `Files touched: … (deleted)`) so
the orchestrator can apply the inverted check mechanically instead of
recording a per-plan Decision Log deviation.
