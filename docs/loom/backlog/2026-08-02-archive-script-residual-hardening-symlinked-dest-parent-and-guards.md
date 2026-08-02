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

**Correction (2026-08-02, whole-branch review remediation round 2).**
"Both units are genuinely guarded today and there is no live defect"
was false. `_validate_date` checked shape only (the `YYYY-MM-DD`
pattern), not calendar validity — `--unit file --date 2026-02-30`
passed it, and the file unit then moved the entry, stamped the
malformed date into its frontmatter, and returned success. The live
defect: `--validate` and `--write` both then refused (they DO reject
impossible calendar dates), so the store could no longer be regenerated
from the entry files — the only way back was hand-editing the archived
file, the exact operation this store's charter says never to do. The
guard is fixed in this same remediation round (calendar-validity
checking added to the shared `_validate_date` path), and the
discriminating test landed with it —
`test_file_unit_refuses_calendar_invalid_date_without_touching_filesystem`
pins `--unit file --date <a shape-valid, calendar-impossible date>`
refusing before any move.

**Second correction (same day, third review round).** The paragraph
above originally closed by saying that discriminating test "genuinely
remains deferred". It did not: it was written in the very commit that
fixed the guard, by a parallel agent, and this text was authored before
that landed. Nothing about item 2 remains deferred — **except** the
direction the new test does not cover: it pins that the archiver stays
at least as strict as the validator, not that the validator stays no
stricter than the archiver. The two calendar checks are deliberately
duplicated rather than shared (`loom-code` ships as a standalone
plugin and must not import a host-repo script), so tightening
`backlog_index._is_valid_date_shape` without tightening
`archive_change_folder._validate_date` reopens this bug's exact class
with nothing going red. That asymmetry is what is left.

**3. The store's own charter is archivable.** Nothing stops
`--unit file` with the identifier `README.md`, which would move
`docs/loom/backlog/README.md` — the store's format SSOT — into
`archive/` and stamp `status: archived` into it. The file has no
frontmatter today, so the script would prepend a minimal block and
the charter would then read as an archived entry. A reserved-name
refusal is the obvious fix.
