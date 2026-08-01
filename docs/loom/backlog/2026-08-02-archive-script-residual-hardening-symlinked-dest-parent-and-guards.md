---
name: 2026-08-02-archive-script-residual-hardening-symlinked-dest-parent-and-guards
description: three residual guard gaps in loom-code/scripts/archive_change_folder.py that the two-unit generalization left behind
status: OPEN
origin: whole-branch review of the docs-backlog-one-entry-per-file arc, 2026-08-02 — all three were raised as green-level findings and deliberately deferred rather than fixed in that branch
start: the next time anyone edits archive_change_folder.py for any reason
---

`loom-code/scripts/archive_change_folder.py` was generalized from
archiving a change-folder to also archiving a single store entry file.
Its path-safety surface (OpenSpec issue #412 bug class) was reviewed
hard and came out clean on the identifier, the date, and the source
symlink, on both units. Three gaps survive. None is exploitable by
anyone who does not already have write access to the repo tree, which
is why none blocked the merge.

**1. A symlinked destination parent is not refused.** The source is
checked with `is_symlink()` and refused, but `dest.parent.mkdir(
parents=True, exist_ok=True)` followed by `shutil.move` will happily
follow a symlinked `docs/loom/backlog/archive/` (or
`docs/loom/archive/`) and relocate the archived object outside the
store. Fix shape: a `dest.parent.is_symlink()` check alongside the
existing source check. Note this exposure is not new — it is
structurally identical on the folder unit, which predates the
generalization.

**2. The file unit has no bad-date test.** `_validate_date` is called
before the unit branch, so both units are genuinely guarded today and
there is no live defect. What is missing is the pin: move that call
into the folder-unit branch and nothing goes red. This is exactly the
"a guard shared by two units stops being exercised once the code
branches" shape that the same review already caught for the identifier
guard — the identifier guard now has a discriminating file-unit test,
and the date guard does not.

**3. The store's own charter is archivable.** Nothing stops
`--unit file` with the identifier `README.md`, which would move
`docs/loom/backlog/README.md` — the store's format SSOT — into
`archive/` and stamp `status: archived` into it. The file has no
frontmatter today, so the script would prepend a minimal block and
the charter would then read as an archived entry. A reserved-name
refusal is the obvious fix.
