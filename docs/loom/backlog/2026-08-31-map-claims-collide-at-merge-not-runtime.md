---
name: 2026-08-31-map-claims-collide-at-merge-not-runtime
description: A Map is a committed file per worktree, so two worktrees' claims on the same ticket never collide at runtime — they meet as a git merge conflict, or worse, merge cleanly with two claim lines
status: open
origin: 2026-08-31 — surfaced while deciding claim_ticket.py's fate in docs/loom/specs/2026-08-31-decision-map-script-cleanup.md (user runs one Map from several worktrees)
start: event — the first time two worktrees' claims on the same Ticket produce a git merge conflict, or before a second concurrent session is pointed at a live Map
---

A Map under `docs/loom/maps/` is a committed file, not a server or a
database: every worktree/branch that checks it out holds its own
independent copy on disk. `loom-workflow/skills/decision-map/scripts/map_lock.py`
(module docstring: "Descriptor-safe Map-local serialization shared by
all store writers") takes an `fcntl` writer lock, but that lock only
serializes concurrent writers *within one checkout* — it has no reach
across worktrees, because each worktree's copy of the Map file is a
distinct inode with its own lock namespace.

The consequence: if two worktrees both claim the same Ticket (per
`loom-workflow/skills/decision-map/SKILL.md` §Claim), the two claims
never contend at runtime — `map_lock.py` sees no conflict in either
checkout, since each only ever locks its own copy. The collision
surfaces later, at `git merge`, in one of two shapes:

- The two worktrees' edits land on overlapping lines of the ticket
  file and the merge stops with a conflict marker — recoverable, but
  only if a human notices and resolves it correctly.
- The two `claim:` edits land on non-overlapping lines (e.g. two
  different fields, or the tool appends rather than replaces) and the
  merge succeeds cleanly, silently leaving two `claim:` lines on one
  ticket with no error at all.

Candidate directions — deliberately left open, not decided:

- A claim-before-branch convention: claim the ticket on `main` (or
  whatever trunk the worktrees share) before branching, so the claim
  itself is never split across worktrees to begin with.
- A merge-time validator: extend `map_store` (or a new `--validate`
  mode) into a pre-merge/CI check that refuses a merge introducing a
  duplicate or conflicting claim on the same ticket.

Note: the now-deleted `claim_ticket.reclaim` tool was NOT a fix for
this — its git evidence (`git log`/`git blame` on the ticket file) was
scoped to one checkout's history and could not see a sibling
worktree's claim at all.
