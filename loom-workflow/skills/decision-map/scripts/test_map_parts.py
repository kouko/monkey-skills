"""Tests for map_parts.py — the Parts-row write-back flipper.

Grammar SSOT: references/map-format.md §Parts (the pinned
`not-started / in-progress / done` Status vocabulary — this flipper
follows it exactly; the plan Task 10 text's `shipped` token is
superseded by the SSOT per the plan's own Decision Log entry 1) and
§Command surface (map_parts.py takes the bare positional `target`
shape — no subcommand verb, unlike map_store.py).

Cell-format precedent: `done(<sha>)` — plan_card.py --set-status's
`done(<sha>)` grammar (loom-code/scripts/plan_card.py), reused here
since it is the existing single-line-rewrite precedent this task cites.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import map_parts  # noqa: E402

SCRIPT = Path(__file__).parent / "map_parts.py"

MAP_MD = """---
map-id: wayfinder
schema_version: 1
state: active
---

## Destination

Chart the decision-map layer.

## Notes

Nothing special.

## Decisions-so-far

- We chose stdlib-only parsing (tickets/decision-a.md)

## Not-yet-specified (fog)

- F-1: how does the fog id survive a rename?

## Out-of-scope

- F-2: retrofitting the four legacy scripts

## Parts

| Part | Join key | Status |
|---|---|---|
| Engine | `wayfinder / Part: Engine` | in-progress |
| SKILL.md | `wayfinder / Part: SKILL.md` | not-started |
"""


def _write_map(tmp_path: Path) -> Path:
    map_dir = tmp_path / "docs" / "loom" / "maps" / "wayfinder"
    map_dir.mkdir(parents=True)
    (map_dir / "MAP.md").write_text(MAP_MD, encoding="utf-8")
    return map_dir


# --- RED / GREEN acceptance test ------------------------------------------


def test_flip_marks_single_part_shipped() -> None:
    """flip_part rewrites exactly the targeted row's Status cell to
    `done(<sha>)` and leaves every other line byte-identical."""
    new_text, old_line, new_line = map_parts.flip_part(
        MAP_MD, "wayfinder / Part: Engine", "096c3167"
    )

    assert old_line == "| Engine | `wayfinder / Part: Engine` | in-progress |"
    assert new_line == "| Engine | `wayfinder / Part: Engine` | done(096c3167) |"

    old_lines = MAP_MD.splitlines()
    new_lines = new_text.splitlines()
    assert len(old_lines) == len(new_lines)
    changed = [
        (o, n) for o, n in zip(old_lines, new_lines) if o != n
    ]
    assert changed == [(old_line, new_line)]

    # The other Parts row is completely untouched.
    assert "| SKILL.md | `wayfinder / Part: SKILL.md` | not-started |" in new_text


def test_flip_unknown_join_key_raises() -> None:
    try:
        map_parts.flip_part(MAP_MD, "wayfinder / Part: Nonexistent", "abc123")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "wayfinder / Part: Engine" in str(exc)
        assert "wayfinder / Part: SKILL.md" in str(exc)


# --- CLI exit-code contract ------------------------------------------------


def test_cli_flip_exits_0_and_writes_file(tmp_path: Path) -> None:
    map_dir = _write_map(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(map_dir),
            "--part",
            "wayfinder / Part: Engine",
            "--sha",
            "096c3167",
            "--repo-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    written = (map_dir / "MAP.md").read_text(encoding="utf-8")
    assert "| Engine | `wayfinder / Part: Engine` | done(096c3167) |" in written
    assert "| SKILL.md | `wayfinder / Part: SKILL.md` | not-started |" in written


def test_cli_unknown_join_key_exits_2(tmp_path: Path) -> None:
    map_dir = _write_map(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(map_dir),
            "--part",
            "wayfinder / Part: Nonexistent",
            "--sha",
            "abc123",
            "--repo-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "wayfinder / Part: Engine" in result.stderr


def test_cli_missing_map_md_exits_1(tmp_path: Path) -> None:
    map_dir = tmp_path / "docs" / "loom" / "maps" / "ghost"
    map_dir.mkdir(parents=True)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(map_dir),
            "--part",
            "ghost / Part: Anything",
            "--sha",
            "abc123",
            "--repo-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
