---
name: editing-a-user-dirty-file-sweeps-their-wip-into-your-commit
description: Path-level git add cannot split hunks — editing a file that already carries the user's uncommitted WIP sweeps the WIP into your commit silently (tests stay green, diff looks intentional); check git status per-file BEFORE editing, and if dirty: reconstruct the edit onto the committed base, commit, then restore the user's delta uncommitted on top
type: gotcha
origin: PR chore-description-diet (2026-07-30) whole-branch review round 1
---

Path-level `git add <file>` cannot split hunks — editing a file that
already carries the user's uncommitted WIP sweeps that WIP into your
commit wholesale. Live case: a description-only edit to
daily-news-digest/SKILL.md swept ~50 WIP body lines into the commit
while the WIP's companion reference file stayed uncommitted, shipping
a dangling cross-file contract that review caught as a 🔴.

**Why:** the sweep is silent — tests stay green (the WIP was
self-consistent) and the diff looks intentional; only whole-artifact
review or the user losing their WIP reveals it.

**How to apply:** before editing ANY file, check
`git status --short <file>`; if it is already modified, either
(a) save the dirty copy, reconstruct your edit onto the committed
base, commit, then restore the user's delta uncommitted on top, or
(b) stop and ask. Never assume a dirty file's extra hunks are yours
to ship.
