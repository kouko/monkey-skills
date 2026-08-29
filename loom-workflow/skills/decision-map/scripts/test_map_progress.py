"""Tests for the read-only decision-map delivery-progress query."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).parent / "map_progress.py"
SKILL_DIR = Path(__file__).parent.parent
MAP_FORMAT_MD = SKILL_DIR / "references" / "map-format.md"
SKILL_MD = SKILL_DIR / "SKILL.md"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_map_progress_derives_bound_plan_state_without_writing_map(
    tmp_path: Path,
) -> None:
    map_md = tmp_path / "docs" / "loom" / "maps" / "wayfinder" / "MAP.md"
    _write(map_md, "original map bytes\n")
    before = map_md.read_bytes()
    plan = tmp_path / "docs" / "loom" / "plans" / "delivery.md"
    _write(
        plan,
        """# Plan: delivery

Goal: Ship the delivery.
Stage: sdd:wave-1

## Task 1 — finish it

- Status: done(abc1234)

## Task 2 — review it

- Status: claimed(@worker)

## Notes

Map part: wayfinder / Part: delivery
""",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "wayfinder / delivery" in result.stdout
    assert "state: claimed" in result.stdout
    assert map_md.read_bytes() == before
    assert "map_progress.py" in MAP_FORMAT_MD.read_text(encoding="utf-8")
    assert "map_progress.py <plan-path> --repo-root <path>" in SKILL_MD.read_text(
        encoding="utf-8"
    )
