#!/usr/bin/env python3
"""Deterministic archive step for a loom-spec change-folder OR a single
loom-family store entry file — two units, selected via the ``unit``
parameter (Python API) or the CLI's ``--unit`` flag (see below; defaults to
``folder``).

- ``unit="folder"`` (default, unchanged from the original single-unit
  script): moves ``docs/loom/<change-id>/`` ->
  ``docs/loom/archive/<date>-<change-id>/`` and stamps a ``status:
  archived`` field into the moved ``proposal.md``'s YAML frontmatter — a
  single-command move, not a manual ``mv`` (OpenSpec's own ``archive``
  command exists for the same reason: issue #412 shows path handling is the
  move approach's real risk, so every path is validated before any
  filesystem mutation happens).
- ``unit="file"``: moves ``docs/loom/backlog/<name>.md`` ->
  ``docs/loom/backlog/archive/<name>.md`` **unrenamed** — no date prefix,
  since the entry already carries its creation date in its filename and
  prefixing the archive date produces a double-date defect — and stamps
  BOTH ``status: archived`` and ``archived: <date>`` into the moved file's
  own frontmatter, unconditionally: an unstamped archived entry reads as
  live to any agent that greps the store, so a stamp failure rolls the move
  back and raises loudly rather than tolerating a silent skip (contrast the
  folder unit, which tolerates a missing ``proposal.md`` child).

Frontmatter handling (identical for both units; the object being stamped is
``proposal.md`` for the folder unit and the moved file itself for the file
unit): if it already opens with a ``---\\n...\\n---\\n`` block, each field is
updated in place (or appended to the block if absent); if there is no
frontmatter block at all, a minimal one is prepended ahead of the original
body. The body itself is not rewritten, but note Python's text-mode
read/write applies universal newline translation, so a CRLF-authored file
normalizes to LF along the way — it is not preserved byte-for-byte.

Refusals (raise ``ArchiveError``, never touch the filesystem) — shared by
both units, one copy of each guard:

- the source (a folder for ``unit="folder"``, a file for ``unit="file"``)
  does not exist;
- the source is a symlink (never archive a live symlink — only a real
  folder/file);
- the source's frontmatter already reads ``status: archived`` (idempotency
  guard against double-archiving);
- the destination path already exists (would silently clobber a prior
  archive);
- the identifier (a change-id for the folder unit, an entry filename for
  the file unit) is not a single, safe path segment — empty, ``.``/``..``,
  containing a path separator, or absolute. This is the path-safety guard:
  an identifier is never allowed to escape its base directory via
  traversal (OpenSpec #412 bug class).
- the date stamp does not match ``YYYY-MM-DD`` exactly, OR is shape-valid
  but not a real calendar date (e.g. ``2026-02-30``). For the folder unit
  the date is interpolated straight into the destination path, so it gets
  the same path-safety guard as the identifier; for the file unit the date
  is only ever written into the ``archived:`` frontmatter field, but it is
  validated identically so that field is never malformed — and never
  rejected downstream by ``scripts/backlog_index.py``'s stricter check
  after the move has already happened.

If the post-move stamp write fails, the moved object is moved back to its
original location before ``ArchiveError`` is raised, so a failure never
leaves a stranded moved-but-unstamped object with no recovery path.

CLI: ``archive_change_folder.py <identifier> [root] [--date YYYY-MM-DD]
[--unit folder|file]`` -> exit 0 on success (prints the destination), exit 1
with an actionable stderr message on any refusal (including an unrecognized
``--unit`` value — ``ArchiveError``'s ``invalid unit`` message, not a
separate CLI-level check). ``root`` defaults to ``Path.cwd()``; ``--date``
defaults to today (UTC-naive local date) and exists mainly so callers/tests
get deterministic destinations; ``--unit`` defaults to ``folder``, so every
existing caller (the finishing-a-development-branch archive-on-close step,
AGENTS.md's declared command surface) keeps working unchanged with no flag
added. Pass ``--unit file`` to archive a single
``docs/loom/backlog/<name>.md`` entry instead of a change-folder.

Stdlib only (pathlib, re, shutil, datetime).
"""
from __future__ import annotations

import datetime
import re
import shutil
import sys
from pathlib import Path
from typing import Callable

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
_STATUS_LINE_RE = re.compile(r"^status\s*:\s*(\S+)\s*$", re.MULTILINE)
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_UNIT_FOLDER = "folder"
_UNIT_FILE = "file"
_UNITS = (_UNIT_FOLDER, _UNIT_FILE)


class ArchiveError(Exception):
    """Raised for any refusal to archive — never touches the filesystem."""


def _validate_change_id(change_id: str) -> None:
    """Path-safety guard (OpenSpec #412 bug class), shared by both units: an
    identifier — a change-id for the folder unit, an entry filename for the
    file unit — MUST be a single, non-empty, non-special path segment with
    no separators and no absolute-path form, never allowed to escape its
    base directory. Wording is unit-agnostic on purpose: a file-unit caller
    must never receive an error message about folders."""
    if not change_id or change_id in (".", ".."):
        raise ArchiveError(
            f"invalid identifier {change_id!r}: must be a non-empty name"
        )
    if "/" in change_id or "\\" in change_id:
        raise ArchiveError(
            f"invalid identifier {change_id!r}: must be a single path segment "
            f"(no '/' or '\\\\')"
        )
    if Path(change_id).is_absolute():
        raise ArchiveError(
            f"invalid identifier {change_id!r}: must not be an absolute path"
        )


def _validate_date(date: str) -> None:
    """Path-safety guard: ``date`` is interpolated straight into the
    destination path (``.../archive/<date>-<change-id>/``), so it MUST match
    ``YYYY-MM-DD`` exactly — refuse anything else (including traversal-shaped
    values like ``../../etc``) before any filesystem use. For the file unit
    the date is only ever written into the ``archived:`` frontmatter field
    (never interpolated into a path), but it is validated identically here.

    Calendar-strict, not just shape-strict: a shape-valid but
    calendar-impossible date (``2026-02-30``, February has no 30th) must
    also be refused BEFORE any filesystem mutation. Without this,
    ``scripts/backlog_index.py``'s ``--validate``/``--write`` (which run
    ``strptime``) would reject the ALREADY-MOVED entry after the fact,
    leaving the store unregenerable until a human hand-edited the archived
    file — the exact hand-edit the generated-index design exists to
    eliminate. Duplicates ``scripts/backlog_index.py``'s
    ``_is_valid_date_shape`` (the twin strict-date check) rather than
    importing it: loom-code ships as a standalone marketplace plugin, and
    importing a monkey-skills-repo-root script would couple this
    self-contained plugin script to one specific host repo's layout."""
    if not _DATE_RE.match(date):
        raise ArchiveError(
            f"invalid --date {date!r}: must match YYYY-MM-DD"
        )
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ArchiveError(
            f"invalid --date {date!r}: not a real calendar date"
        )


def _read_status(proposal_text: str) -> str | None:
    """Return the frontmatter ``status:`` value, or None if absent/no
    frontmatter."""
    match = _FRONTMATTER_RE.match(proposal_text)
    if match is None:
        return None
    status_match = _STATUS_LINE_RE.search(match.group(1))
    return status_match.group(1) if status_match else None


def _stamp_field(text: str, key: str, value: str) -> str:
    """Return ``text`` with its frontmatter ``key:`` field set to ``value``,
    adding a minimal frontmatter block first if none exists. Generalizes the
    original single-field ``status:`` stamp to any frontmatter key, so the
    file unit can stamp both ``status`` and ``archived`` by calling this
    twice.

    The line-matching pattern deliberately does NOT reuse ``_STATUS_LINE_RE``
    (whose ``(\\S+)`` value is a single whitespace-free token): the backlog
    store's closed status vocabulary has one multi-word member, ``CLOSED —
    SUPERSEDED`` (em dash), and a single-token pattern misses that line
    entirely, causing this function to APPEND a duplicate ``key:`` line
    instead of replacing the existing one. The pattern below requires the
    value to start with a non-whitespace character (so an empty/whitespace-
    only value still does not count as "present", matching the original
    single-token pattern's behaviour on that edge) and then allows the rest
    of the line verbatim up to end-of-line.

    Two properties keep that widening safe. ``.`` does not match a newline
    (no ``re.DOTALL``), so a match can never run past its own line; and the
    pattern is applied to ``body``, the frontmatter block extracted at the
    top of this function, so a ``status:``-shaped line further down in the
    document body is out of reach either way.

    Ending the pattern at ``.*$`` rather than the original ``(\\S+)\\s*$``
    also fixes a second, previously unnoticed corruption: ``\\s`` matches
    newlines, so the old trailing ``\\s*`` swallowed the line terminator
    whenever ``key:`` was the block's LAST field, and the replacement then
    glued the closing ``---`` fence onto the value. Pinned by
    ``test_stamping_the_last_frontmatter_field_keeps_the_closing_fence``."""
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        return f"---\n{key}: {value}\n---\n\n" + text

    body = match.group(1)
    field_re = re.compile(rf"^{re.escape(key)}\s*:\s*\S.*$", re.MULTILINE)
    if field_re.search(body):
        new_body = field_re.sub(f"{key}: {value}", body)
    else:
        new_body = body + f"{key}: {value}\n"
    return f"---\n{new_body}---\n" + text[match.end():]


def _write_stamp_or_restore(
    status_path: Path,
    dest: Path,
    source: Path,
    noun: str,
    mutate: Callable[[str], str],
) -> None:
    """Read ``status_path``, apply ``mutate`` to its text, and write the
    result back — the same rollback-on-stamp-failure guarantee for both
    units. If either the read or the write fails, move ``dest`` back to
    ``source`` before raising ``ArchiveError``, so a stamp failure never
    leaves a stranded moved-but-unstamped object with no recovery path.
    ``noun`` customizes the stranded-object wording — pass the SAME noun
    used for this unit's other refusal messages ("change-folder" /
    "entry file"), not a shorthand, so all of a unit's messages describe
    the object the same way. ``status_path`` and ``dest`` are two distinct
    parameters (not one) because they genuinely differ for the folder unit
    (``dest_proposal`` vs ``dest`` itself) even though the file unit passes
    the same object for both."""
    try:
        status_path.write_text(mutate(status_path.read_text(encoding="utf-8")), encoding="utf-8")
    except OSError as exc:
        try:
            shutil.move(str(dest), str(source))
        except OSError as restore_exc:
            raise ArchiveError(
                f"status stamp failed for {status_path} ({exc}); restore "
                f"to {source} ALSO failed ({restore_exc}) — the {noun} is "
                f"stranded, unstamped, at {dest}; manually add the required "
                f"frontmatter fields (see this script's module docstring) "
                f"to {status_path}"
            ) from restore_exc
        raise ArchiveError(
            f"status stamp failed for {status_path} ({exc}); restored "
            f"the original {noun} to {source}"
        ) from exc


def archive_change_folder(
    root: Path,
    change_id: str,
    date: str | None = None,
    *,
    unit: str = _UNIT_FOLDER,
) -> Path:
    """Move a change-folder (``unit="folder"``, the default) or a single
    entry file (``unit="file"``) into its unit's archive location, and stamp
    the moved object's frontmatter as archived.

    ``unit="folder"``: ``<root>/docs/loom/<change_id>/`` moves to
    ``<root>/docs/loom/archive/<date>-<change_id>/``; ``status: archived`` is
    stamped into the moved ``proposal.md``.

    ``unit="file"``: ``<root>/docs/loom/backlog/<change_id>`` moves to
    ``<root>/docs/loom/backlog/archive/<change_id>`` unrenamed (no date
    prefix); both ``status: archived`` and ``archived: <date>`` are stamped
    into the moved file itself, unconditionally.

    Returns the destination path on success. Raises ``ArchiveError`` (no
    filesystem mutation) on any refusal: unsafe identifier, missing source,
    already-archived source, or a destination collision.
    """
    if unit not in _UNITS:
        raise ArchiveError(f"invalid unit {unit!r}: must be one of {_UNITS}")

    _validate_change_id(change_id)
    root = Path(root)
    stamp = date if date is not None else datetime.date.today().isoformat()
    _validate_date(stamp)

    is_file_unit = unit == _UNIT_FILE
    noun = "entry file" if is_file_unit else "change-folder"

    if is_file_unit:
        source = root / "docs" / "loom" / "backlog" / change_id
        dest = root / "docs" / "loom" / "backlog" / "archive" / change_id
    else:
        source = root / "docs" / "loom" / change_id
        dest = root / "docs" / "loom" / "archive" / f"{stamp}-{change_id}"

    source_exists = source.is_file() if is_file_unit else source.is_dir()
    if not source_exists:
        raise ArchiveError(f"{noun} does not exist: {source} (nothing to archive)")
    if source.is_symlink():
        kind_word = "files" if is_file_unit else "folders"
        raise ArchiveError(
            f"refusing to archive a symlink: {source} (only real {kind_word} "
            f"may be archived)"
        )

    status_source = source if is_file_unit else source / "proposal.md"
    status_text = (
        status_source.read_text(encoding="utf-8") if status_source.is_file() else ""
    )
    if _read_status(status_text) == "archived":
        raise ArchiveError(
            f"{noun} is already archived: {status_source} carries status: archived"
        )

    if dest.exists():
        raise ArchiveError(f"archive destination already exists: {dest}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(dest))

    if is_file_unit:
        # Unconditional: the moved object IS the file being stamped, so
        # there is no "missing child" case to tolerate (contrast the folder
        # unit's `if dest_proposal.is_file():` below) — a failure here must
        # fail loudly rather than leave an unstamped file at dest.
        _write_stamp_or_restore(
            dest, dest, source, noun,
            lambda text: _stamp_field(_stamp_field(text, "status", "archived"), "archived", stamp),
        )
    else:
        dest_proposal = dest / "proposal.md"
        if dest_proposal.is_file():
            _write_stamp_or_restore(
                dest_proposal, dest, source, noun,
                lambda text: _stamp_field(text, "status", "archived"),
            )

    return dest


def main(argv: list[str] | None = None) -> int:
    # argv shapes:
    #   [identifier]                                        -> archive under
    #       cwd, today's date, folder unit
    #   [identifier, root]                                  -> archive under
    #       root, today's date, folder unit
    #   [identifier, [root], --date YYYY-MM-DD]              -> pin the date
    #       (tests/callers)
    #   [identifier, [root], --unit folder|file]             -> select the
    #       unit; defaults to folder when omitted (every existing caller
    #       keeps working unchanged)
    args = list(sys.argv[1:] if argv is None else argv)

    date_override = None
    if "--date" in args:
        i = args.index("--date")
        if i + 1 >= len(args):
            print(
                "archive_change_folder: --date requires a value (YYYY-MM-DD)",
                file=sys.stderr,
            )
            return 1
        date_override = args[i + 1]
        del args[i : i + 2]

    unit = _UNIT_FOLDER
    if "--unit" in args:
        i = args.index("--unit")
        if i + 1 >= len(args):
            print(
                "archive_change_folder: --unit requires a value (folder|file)",
                file=sys.stderr,
            )
            return 1
        unit = args[i + 1]
        del args[i : i + 2]

    if not args:
        print(
            "usage: archive_change_folder.py <identifier> [root] "
            "[--date YYYY-MM-DD] [--unit folder|file]",
            file=sys.stderr,
        )
        return 1

    change_id = args[0]
    root = Path(args[1]) if len(args) > 1 else Path.cwd()

    try:
        dest = archive_change_folder(root, change_id, date=date_override, unit=unit)
    except ArchiveError as exc:
        print(f"archive_change_folder: {exc}", file=sys.stderr)
        return 1

    source_desc = (
        f"docs/loom/backlog/{change_id}" if unit == _UNIT_FILE else f"docs/loom/{change_id}"
    )
    print(f"OK: archived {source_desc} -> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
