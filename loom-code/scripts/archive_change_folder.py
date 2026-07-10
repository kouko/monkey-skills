#!/usr/bin/env python3
"""Deterministic archive step for a loom-spec change-folder.

Moves ``docs/loom/<change-id>/`` -> ``docs/loom/archive/<date>-<change-id>/``
and stamps a ``status: archived`` field into the moved ``proposal.md``'s YAML
frontmatter — a single-command move, not a manual ``mv`` (OpenSpec's own
``archive`` command exists for the same reason: issue #412 shows path
handling is the move approach's real risk, so every path is validated before
any filesystem mutation happens).

Frontmatter handling (proposal.md may or may not have one — both are
handled): if ``proposal.md`` already opens with a ``---\\n...\\n---\\n``
block, ``status:`` is updated in place (or appended to the block if absent);
if there is no frontmatter block at all, a minimal one (``---\\nstatus:
archived\\n---\\n\\n``) is prepended ahead of the original body. The body
itself is not rewritten, but note Python's text-mode read/write applies
universal newline translation, so a CRLF-authored file normalizes to LF
along the way — it is not preserved byte-for-byte.

Refusals (raise ``ArchiveError``, never touch the filesystem):

- the source change-folder does not exist;
- the source change-folder is a symlink (never archive a live symlink —
  only a real folder);
- the source ``proposal.md`` frontmatter already reads ``status: archived``
  (idempotency guard against double-archiving);
- the destination path already exists (would silently clobber a prior
  archive of the same change-id + date);
- the change-id is not a single, safe path segment — empty, ``.``/``..``,
  containing a path separator, or absolute. This is the path-safety guard:
  a change-id is never allowed to escape ``docs/loom/`` via traversal.
- the date stamp does not match ``YYYY-MM-DD`` exactly. The date is
  interpolated straight into the destination path, so it gets the same
  path-safety guard as the change-id (both API arg and CLI ``--date``).

If the post-move status stamp write fails, the moved folder is moved back
to its original location before ``ArchiveError`` is raised, so a failure
never leaves a stranded moved-but-unstamped folder with no recovery path.

CLI: ``archive_change_folder.py <change-id> [root] [--date YYYY-MM-DD]`` ->
exit 0 on success (prints the destination), exit 1 with an actionable
stderr message on any refusal. ``root`` defaults to ``Path.cwd()``; ``--date``
defaults to today (UTC-naive local date) and exists mainly so callers/tests
get deterministic destinations.

Stdlib only (pathlib, re, shutil, datetime).
"""
from __future__ import annotations

import datetime
import re
import shutil
import sys
from pathlib import Path

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
_STATUS_LINE_RE = re.compile(r"^status\s*:\s*(\S+)\s*$", re.MULTILINE)
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ArchiveError(Exception):
    """Raised for any refusal to archive — never touches the filesystem."""


def _validate_change_id(change_id: str) -> None:
    """Path-safety guard (OpenSpec #412 bug class): a change-id MUST be a
    single, non-empty, non-special path segment with no separators and no
    absolute-path form — never allowed to escape ``docs/loom/``."""
    if not change_id or change_id in (".", ".."):
        raise ArchiveError(
            f"invalid change-id {change_id!r}: must be a non-empty folder name"
        )
    if "/" in change_id or "\\" in change_id:
        raise ArchiveError(
            f"invalid change-id {change_id!r}: must be a single path segment "
            f"(no '/' or '\\\\')"
        )
    if Path(change_id).is_absolute():
        raise ArchiveError(
            f"invalid change-id {change_id!r}: must not be an absolute path"
        )


def _validate_date(date: str) -> None:
    """Path-safety guard: ``date`` is interpolated straight into the
    destination path (``.../archive/<date>-<change-id>/``), so it MUST match
    ``YYYY-MM-DD`` exactly — refuse anything else (including traversal-shaped
    values like ``../../etc``) before any filesystem use."""
    if not _DATE_RE.match(date):
        raise ArchiveError(
            f"invalid --date {date!r}: must match YYYY-MM-DD"
        )


def _read_status(proposal_text: str) -> str | None:
    """Return the frontmatter ``status:`` value, or None if absent/no
    frontmatter."""
    match = _FRONTMATTER_RE.match(proposal_text)
    if match is None:
        return None
    status_match = _STATUS_LINE_RE.search(match.group(1))
    return status_match.group(1) if status_match else None


def _stamp_status(proposal_text: str, status: str) -> str:
    """Return ``proposal_text`` with its frontmatter ``status:`` field set to
    ``status``, adding a minimal frontmatter block first if none exists."""
    match = _FRONTMATTER_RE.match(proposal_text)
    if match is None:
        return f"---\nstatus: {status}\n---\n\n" + proposal_text

    body = match.group(1)
    if _STATUS_LINE_RE.search(body):
        new_body = _STATUS_LINE_RE.sub(f"status: {status}", body)
    else:
        new_body = body + f"status: {status}\n"
    return f"---\n{new_body}---\n" + proposal_text[match.end():]


def archive_change_folder(root: Path, change_id: str, date: str | None = None) -> Path:
    """Move ``<root>/docs/loom/<change_id>/`` to
    ``<root>/docs/loom/archive/<date>-<change_id>/`` and stamp
    ``status: archived`` into the moved ``proposal.md``.

    Returns the destination path on success. Raises ``ArchiveError`` (no
    filesystem mutation) on any refusal: unsafe change-id, missing source,
    already-archived source, or a destination collision.
    """
    _validate_change_id(change_id)
    root = Path(root)
    stamp = date if date is not None else datetime.date.today().isoformat()
    _validate_date(stamp)

    source = root / "docs" / "loom" / change_id
    if not source.is_dir():
        raise ArchiveError(
            f"change-folder does not exist: {source} (nothing to archive)"
        )
    if source.is_symlink():
        raise ArchiveError(
            f"refusing to archive a symlink: {source} (only real folders "
            f"may be archived)"
        )

    proposal_path = source / "proposal.md"
    proposal_text = (
        proposal_path.read_text(encoding="utf-8") if proposal_path.is_file() else ""
    )
    if _read_status(proposal_text) == "archived":
        raise ArchiveError(
            f"change-folder is already archived: {proposal_path} carries "
            f"status: archived"
        )

    dest = root / "docs" / "loom" / "archive" / f"{stamp}-{change_id}"
    if dest.exists():
        raise ArchiveError(f"archive destination already exists: {dest}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(dest))

    dest_proposal = dest / "proposal.md"
    if dest_proposal.is_file():
        try:
            dest_proposal.write_text(
                _stamp_status(dest_proposal.read_text(encoding="utf-8"), "archived"),
                encoding="utf-8",
            )
        except OSError as exc:
            try:
                shutil.move(str(dest), str(source))
            except OSError as restore_exc:
                raise ArchiveError(
                    f"status stamp failed for {dest_proposal} ({exc}); restore "
                    f"to {source} ALSO failed ({restore_exc}) — the folder is "
                    f"stranded, unstamped, at {dest}; manually add "
                    f"'status: archived' to {dest_proposal}"
                ) from restore_exc
            raise ArchiveError(
                f"status stamp failed for {dest_proposal} ({exc}); restored "
                f"the original folder to {source}"
            ) from exc

    return dest


def main(argv: list[str] | None = None) -> int:
    # argv shapes:
    #   [change-id]                            -> archive under cwd, today's date
    #   [change-id, root]                      -> archive under root, today's date
    #   [change-id, [root], --date YYYY-MM-DD] -> pin the date (tests/callers)
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

    if not args:
        print(
            "usage: archive_change_folder.py <change-id> [root] [--date YYYY-MM-DD]",
            file=sys.stderr,
        )
        return 1

    change_id = args[0]
    root = Path(args[1]) if len(args) > 1 else Path.cwd()

    try:
        dest = archive_change_folder(root, change_id, date=date_override)
    except ArchiveError as exc:
        print(f"archive_change_folder: {exc}", file=sys.stderr)
        return 1

    print(f"OK: archived docs/loom/{change_id} -> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
