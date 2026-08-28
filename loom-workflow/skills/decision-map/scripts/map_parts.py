#!/usr/bin/env python3
"""The Parts-row write-back flipper for a decision-map store.

Task 10 of docs/loom/plans/2026-08-28-decision-map-layer.md. Grammar
SSOT: `loom-workflow/skills/decision-map/references/map-format.md`
§Parts and §Command surface. map-format.md §Parts pins the Status cell
vocabulary as `not-started / in-progress / done(<sha>)` — the third
form recording, in parentheses, the commit sha that delivered the
part — and pins that this flipper is the ONLY script permitted to
change a Parts row's Status cell, and that an already-`done(<sha>)`
row is never flipped again (refuse, never overwrite an existing
delivery record). Cell format follows `plan_card.py --set-status`'s
`done(<sha>)` grammar (scripts/plan_card.py) — the single-line-rewrite
precedent this task cites.

Unlike `map_store.py`, this script carries no subcommand verb —
§Command surface pins `map_store.py` alone as the one script with a
leading verb; every other script (map_parts.py included) takes the
bare positional `target` shape with flags.

CLI: `map_parts.py <map-dir> --part <join-key> --sha <commit>
[--repo-root <path>]`. Rewrites ONLY the one Parts row whose join key
matches `--part`; every other byte in MAP.md is unchanged. The write
is atomic: a sibling temp file is written then `os.replace()`d onto
MAP.md, so a crash mid-write never leaves a truncated store. Exit
codes follow §Command surface: 0 clean write, 1 operational error (map
directory or MAP.md missing/unreadable), 2 violation (no Parts row
carries the given join key, or the row is already `done(<sha>)` — the
target exists and was readable, but its content fails the check).

Stdlib only.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import map_store

_PARTS_HEADING = re.compile(r"^## Parts\s*$", re.MULTILINE)
_PART_ROW = re.compile(r"^\|(?P<c1>[^|]*)\|(?P<c2>[^|]*)\|(?P<c3>[^|]*)\|\s*$")


def _row_join_key(cell: str) -> str:
    """The join-key cell's value, normalized the same way map_store's
    `_parse_parts` does: whitespace-stripped, then backtick-stripped,
    then whitespace-stripped again."""
    return cell.strip().strip("`").strip()


def _is_header_or_separator(name_cell: str) -> bool:
    name = name_cell.strip()
    return name in ("Part", "") or set(name) <= {"-"}


def flip_part(text: str, join_key: str, sha: str) -> tuple[str, str, str]:
    """MAP.md's `text` with the Parts row whose join key equals
    `join_key` rewritten to `done(<sha>)` in its Status cell — every
    other byte unchanged. Returns `(new_text, old_line, new_line)`.
    Pure function (the caller writes the file and decides exit codes);
    raises ValueError when MAP.md has no `## Parts` heading or no row
    carries the given join key, listing the known join keys."""
    heading = _PARTS_HEADING.search(text)
    if heading is None:
        raise ValueError("MAP.md has no '## Parts' heading")
    next_heading = text.find("\n## ", heading.end())
    section_end = next_heading if next_heading != -1 else len(text)
    section = text[heading.end():section_end]

    offset = heading.end()
    known_keys: list[str] = []
    match_start: int | None = None
    match_line: str | None = None
    match_cells: tuple[str, str, str] | None = None
    for raw_line in section.splitlines(keepends=True):
        stripped = raw_line.splitlines()[0] if raw_line.splitlines() else ""
        row = _PART_ROW.match(stripped)
        if row is not None and not _is_header_or_separator(row.group("c1")):
            key = _row_join_key(row.group("c2"))
            known_keys.append(key)
            if key == join_key:
                match_start = offset
                match_line = stripped
                match_cells = (row.group("c1"), row.group("c2"), row.group("c3"))
        offset += len(raw_line)

    if match_line is None or match_cells is None or match_start is None:
        raise ValueError(
            f"no Parts row with join key {join_key!r} — known keys: "
            + ", ".join(repr(k) for k in known_keys)
        )

    c1, c2, c3 = match_cells
    existing_status = c3.strip()
    already_done = re.fullmatch(r"done\([^()\s]+\)", existing_status)
    if already_done is not None:
        raise ValueError(
            f"Parts row with join key {join_key!r} is already {existing_status} "
            "— map_parts.py never overwrites an existing delivery record"
        )
    leading = c3[: len(c3) - len(c3.lstrip())]
    trailing = c3[len(c3.rstrip()):]
    new_c3 = f"{leading}done({sha}){trailing}"
    new_line = f"|{c1}|{c2}|{new_c3}|"
    end = match_start + len(match_line)
    return text[:match_start] + new_line + text[end:], match_line, new_line


def _atomic_write(path: Path, text: str) -> None:
    """Write `text` to `path` atomically: a sibling temp file is
    written and flushed, then `os.replace()`d onto `path` — a crash or
    concurrent read mid-write never observes a truncated MAP.md
    (quality-gate 🟡 fix: this flipper used to `write_text` in place)."""
    tmp_path = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    with open(tmp_path, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)


# --- CLI -------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flip one decision-map Parts row's Status cell to done(<sha>)."
    )
    parser.add_argument("map_dir", help="path to the map directory")
    parser.add_argument(
        "--part", required=True, help="the Parts row's join key to flip"
    )
    parser.add_argument("--sha", required=True, help="commit sha to record")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="repo root (default: git rev-parse --show-toplevel of the "
        "map directory, falling back to cwd)",
    )
    args = parser.parse_args(argv)

    map_dir = Path(args.map_dir)
    # repo-root is accepted per the canonical arg shape (map-format.md
    # §Command surface) but this flipper resolves the Parts row relative
    # to the map directory itself, not the repo root.
    map_store.resolve_repo_root(args.repo_root, map_dir)

    map_md = map_dir / "MAP.md"
    if not map_md.is_file():
        print(f"Error: MAP.md not found at {map_md}", file=sys.stderr)
        return 1
    try:
        text = map_md.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error: cannot read {map_md}: {exc}", file=sys.stderr)
        return 1

    try:
        new_text, old_line, new_line = flip_part(text, args.part, args.sha)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    try:
        _atomic_write(map_md, new_text)
    except OSError as exc:
        print(f"Error: cannot write {map_md}: {exc}", file=sys.stderr)
        return 1

    print(f"old: {old_line}")
    print(f"new: {new_line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
