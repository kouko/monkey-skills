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
    map_text = (map_dir / "MAP.md").read_text(encoding="utf-8")
    assert "schema_version: 3" in map_text
    assert "## Parts" not in map_text
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


# --- destination ratification slot (map-format.md §Sections) ---------------


def test_scaffold_destination_ratification_slot_is_not_a_valid_line(
    tmp_path: Path,
) -> None:
    """map-format.md §Sections: map_init scaffolds the destination
    ratification SLOT — a visible placeholder the charting close
    replaces — which must NOT read as a real `user-ratified:` line:
    the scaffold validates 0 in `charting`, but hand-flipping state to
    `active` without a real ratification line is exit 2."""
    _git_init(tmp_path)
    assert map_init.init_map("wayfinder", repo_root=tmp_path) == 0
    map_dir = tmp_path / "docs" / "loom" / "maps" / "wayfinder"
    map_md = map_dir / "MAP.md"
    text = map_md.read_text(encoding="utf-8")
    # the slot is visible in the Destination section...
    assert "user-ratified" in text
    # ...but no line is a real ratification line
    assert not any(
        line.strip().startswith("user-ratified:")
        for line in text.splitlines()
    )
    # charting scaffold validates clean
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message
    # hand-flipped to active with only the placeholder: exit 2
    map_md.write_text(
        text.replace("state: charting", "state: active"), encoding="utf-8"
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "user-ratified:" in message
