"""Tests for mint_critic_verdict.py — the critic-verdict CLI that binds a
loom-spec/loom-interface-design critic's PASS_WITH_NOTES/NEEDS_REVISION
verdict to the exact bytes of the artifact files it reviewed (§4c Fix-4
of docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md).

Fixtures are built INLINE under tmp_path (flat-folder rule: no fixtures/
subdir). Each test constructs its own throwaway change-folder.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from mint_critic_verdict import VERDICT_FILENAME, main


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _change_folder_with_design(tmp_path: Path, text: str = "# Design\n") -> Path:
    folder = tmp_path / "change-folder"
    folder.mkdir()
    _write(folder / "DESIGN.md", text)
    return folder


VALID_PASS = "standards_version: 2026-06\nverdict: PASS_WITH_NOTES\n"
VALID_NEEDS_REVISION = "standards_version: 2026-06\nverdict: NEEDS_REVISION\n"


# --------------------------------------------------------------------- mint


def test_mint_writes_verdict_json_with_pass_with_notes(tmp_path, capsys):
    folder = _change_folder_with_design(tmp_path)
    verdict_file = _write(tmp_path / "verdict.md", VALID_PASS)

    rc = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 0
    marker = folder / VERDICT_FILENAME
    assert marker.is_file()
    data = json.loads(marker.read_text(encoding="utf-8"))
    assert set(data) == {"schema", "verdict", "files", "sha256", "written_at"}
    assert data["schema"] == 1
    assert data["verdict"] == "PASS_WITH_NOTES"
    assert data["files"] == ["DESIGN.md"]
    assert len(data["sha256"]) == 64  # hex sha256
    datetime.fromisoformat(data["written_at"])
    assert str(marker) in capsys.readouterr().out


def test_mint_needs_revision_still_mints(tmp_path):
    folder = _change_folder_with_design(tmp_path)
    verdict_file = _write(tmp_path / "verdict.md", VALID_NEEDS_REVISION)

    rc = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 0
    data = json.loads((folder / VERDICT_FILENAME).read_text(encoding="utf-8"))
    assert data["verdict"] == "NEEDS_REVISION"


def test_mint_change_folder_not_found_exits_2(tmp_path):
    missing_folder = tmp_path / "nope"
    verdict_file = _write(tmp_path / "verdict.md", VALID_PASS)

    rc = main(
        [
            "mint",
            "--change-folder",
            str(missing_folder),
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 2
    assert not missing_folder.exists()


def test_mint_invalid_verdict_text_exits_4(tmp_path):
    folder = _change_folder_with_design(tmp_path)
    # "PASS" alone is not an allowed critic-verdict token (only
    # PASS_WITH_NOTES / NEEDS_REVISION per §4c point 3).
    verdict_file = _write(
        tmp_path / "verdict.md", "standards_version: 2026-06\nverdict: PASS\n"
    )

    rc = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 4
    assert not (folder / VERDICT_FILENAME).exists()


def test_mint_missing_verdict_line_exits_4(tmp_path):
    folder = _change_folder_with_design(tmp_path)
    verdict_file = _write(tmp_path / "verdict.md", "standards_version: 2026-06\n")

    rc = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 4
    assert not (folder / VERDICT_FILENAME).exists()


def test_mint_overwrites_in_place_latest_wins(tmp_path):
    folder = _change_folder_with_design(tmp_path)
    verdict_file = tmp_path / "verdict.md"
    _write(verdict_file, VALID_PASS)

    rc1 = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )
    assert rc1 == 0

    _write(verdict_file, VALID_NEEDS_REVISION)
    rc2 = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )
    assert rc2 == 0

    # Exactly one verdict file remains, reflecting the latest mint.
    assert [p.name for p in folder.glob("*.json")] == [VERDICT_FILENAME]
    data = json.loads((folder / VERDICT_FILENAME).read_text(encoding="utf-8"))
    assert data["verdict"] == "NEEDS_REVISION"


# ----------------------------------------------------------------- validate


def test_validate_fresh_pass_with_notes_exits_0(tmp_path):
    folder = _change_folder_with_design(tmp_path)
    verdict_file = _write(tmp_path / "verdict.md", VALID_PASS)
    assert (
        main(
            [
                "mint",
                "--change-folder",
                str(folder),
                "--verdict-file",
                str(verdict_file),
                "--files",
                "DESIGN.md",
            ]
        )
        == 0
    )

    rc = main(["validate", "--change-folder", str(folder), "--files", "DESIGN.md"])

    assert rc == 0


def test_validate_no_verdict_file_exits_2(tmp_path):
    folder = _change_folder_with_design(tmp_path)

    rc = main(["validate", "--change-folder", str(folder), "--files", "DESIGN.md"])

    assert rc == 2


def test_validate_fresh_needs_revision_exits_3(tmp_path):
    folder = _change_folder_with_design(tmp_path)
    verdict_file = _write(tmp_path / "verdict.md", VALID_NEEDS_REVISION)
    assert (
        main(
            [
                "mint",
                "--change-folder",
                str(folder),
                "--verdict-file",
                str(verdict_file),
                "--files",
                "DESIGN.md",
            ]
        )
        == 0
    )

    rc = main(["validate", "--change-folder", str(folder), "--files", "DESIGN.md"])

    assert rc == 3


def test_validate_stale_hash_after_editing_covered_file_exits_4(tmp_path):
    folder = _change_folder_with_design(tmp_path)
    verdict_file = _write(tmp_path / "verdict.md", VALID_PASS)
    assert (
        main(
            [
                "mint",
                "--change-folder",
                str(folder),
                "--verdict-file",
                str(verdict_file),
                "--files",
                "DESIGN.md",
            ]
        )
        == 0
    )

    # Edit the covered file after minting — the recorded sha256 no
    # longer matches the current bytes.
    _write(folder / "DESIGN.md", "# Design\n\nEdited after mint.\n")

    rc = main(["validate", "--change-folder", str(folder), "--files", "DESIGN.md"])

    assert rc == 4
