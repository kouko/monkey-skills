---
name: deletion-task-review-packet-fails-the-cat-file-existence-check
description: SDD's per-task reviewer fan-out requires `git cat-file -e <reviewed_sha>:<path>` for every declared `Files touched`, so a task whose whole job is deleting files can never satisfy it — the paths are absent at every SHA after the deletion commit; dispatch the reviewers with the deletion commit as scope (cross-read the removed bytes at `<commit>~1:<path>`, prove absence at `<commit>:<path>`), record the deviation in the plan's Decision Log, and keep the immutable-SHA rule intact
type: gotcha
origin: branch loom-script-refactor-phase2 (2026-08-31) — Task 4 (`git rm claim_ticket.py test_claim_ticket.py`) hit it at the first individual review fan-out; recorded as plan DL-1
---

`subagent-driven-development` Step 3 says: for every declared path run
`git -C "<target_repo>" cat-file -e "<reviewed_sha>:<path>"` before
dispatching, and any failure REFUSES the fan-out. Read literally, a
deletion task is unreviewable — its declared paths are gone at the
packet's `reviewed_sha` by construction, and the packet has no other
way to express "these files should not exist".

The check exists to keep reviewers off the mutable working tree, not
to forbid deletions. The reading that preserves that intent: scope the
fan-out to the deletion commit itself — reviewers read the removed
content via `git show <commit>~1:<path>`, prove absence via
`git cat-file -e <commit>:<path>` failing, and confirm the commit's
`--stat` names only the declared paths. Write the deviation into the
plan's `## Decision Log` before dispatching so the reviewer sees why the
existence check was not applied, and do not return `MALFORMED_PACKET`
for that reason alone.

The contract text itself is the fix that outlives this note: an
"absent-at-sha is the expected state for a deletion task" clause in
SDD Step 3 (a backlog entry, not this memory, tracks that edit).
