"""Tests for map_init.py — the decision-map store scaffolder.

WHY: map-format.md §Command surface pins map_init.py as the sole way
to create a conformant, empty `docs/loom/maps/<map-id>/` store — a
template a human never hand-copies. These tests pin the round-trip
(scaffold → map_store.validate exits 0) and the refuse-if-exists
guard (map-format.md's other scripts never overwrite a live store).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import map_init  # noqa: E402
import map_store  # noqa: E402

SCRIPT = Path(__file__).parent / "map_init.py"


def _git_init(repo_root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=repo_root, check=True)


# --- RED / GREEN acceptance test ------------------------------------------


def test_scaffolded_map_passes_validate(tmp_path: Path) -> None:
    """A freshly scaffolded map is checker-valid — map_store.validate
    exits 0 against it (map-format.md's Live-map criterion pin)."""
    _git_init(tmp_path)
    code = map_init.init_map("wayfinder", repo_root=tmp_path)
    assert code == 0

    map_dir = tmp_path / "docs" / "loom" / "maps" / "wayfinder"
    validate_code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert validate_code == 0, message


def test_scaffold_creates_empty_tickets_dir_tracked_by_git(tmp_path: Path) -> None:
    _git_init(tmp_path)
    map_init.init_map("wayfinder", repo_root=tmp_path)
    tickets_dir = tmp_path / "docs" / "loom" / "maps" / "wayfinder" / "tickets"
    assert tickets_dir.is_dir()
    assert (tickets_dir / ".gitkeep").is_file()


def test_scaffold_refuses_when_map_dir_already_exists(tmp_path: Path) -> None:
    _git_init(tmp_path)
    map_init.init_map("wayfinder", repo_root=tmp_path)
    code = map_init.init_map("wayfinder", repo_root=tmp_path)
    assert code == 1


# --- CLI smoke test --------------------------------------------------------


def test_cli_bare_positional_shape(tmp_path: Path) -> None:
    """Canonical arg shape: bare positional `map-id`, no subcommand
    verb (map-format.md §Command surface: map_init.py is one of the
    four scripts with no verb, unlike map_store.py's `validate`)."""
    _git_init(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "wayfinder", "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    map_dir = tmp_path / "docs" / "loom" / "maps" / "wayfinder"
    assert (map_dir / "MAP.md").is_file()
