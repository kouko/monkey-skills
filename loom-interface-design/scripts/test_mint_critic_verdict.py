"""Tests for mint_critic_verdict.py — the critic-verdict CLI that binds a
loom-spec/loom-interface-design critic's PASS_WITH_NOTES/NEEDS_REVISION
verdict to the exact bytes of the artifact files it reviewed (§4c Fix-4
of docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md).

Ported from loom-spec/scripts/test_mint_critic_verdict.py (Task 14's
proven test matrix) — byte-identical logic; fixture default filename
switched from DESIGN.md to this plugin's typical artifact, per Task 15.

Fixtures are built INLINE under tmp_path (flat-folder rule: no fixtures/
subdir). Each test constructs its own throwaway change-folder.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from mint_critic_verdict import verdict_filename, main


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
            "--critic",
            "design-critic",
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 0
    marker = folder / verdict_filename("design-critic")
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
            "--critic",
            "design-critic",
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 0
    data = json.loads(
        (folder / verdict_filename("design-critic")).read_text(encoding="utf-8")
    )
    assert data["verdict"] == "NEEDS_REVISION"


def test_mint_change_folder_not_found_exits_2(tmp_path):
    missing_folder = tmp_path / "nope"
    verdict_file = _write(tmp_path / "verdict.md", VALID_PASS)

    rc = main(
        [
            "mint",
            "--change-folder",
            str(missing_folder),
            "--critic",
            "design-critic",
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
            "--critic",
            "design-critic",
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 4
    assert not (folder / verdict_filename("design-critic")).exists()


def test_mint_missing_verdict_line_exits_4(tmp_path):
    folder = _change_folder_with_design(tmp_path)
    verdict_file = _write(tmp_path / "verdict.md", "standards_version: 2026-06\n")

    rc = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 4
    assert not (folder / verdict_filename("design-critic")).exists()


def test_mint_overwrites_in_place_latest_wins(tmp_path):
    folder = _change_folder_with_design(tmp_path)
    verdict_file = tmp_path / "verdict.md"
    _write(verdict_file, VALID_PASS)

    rc1 = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
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
            "--critic",
            "design-critic",
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )
    assert rc2 == 0

    # Exactly one verdict file remains, reflecting the latest mint.
    assert [p.name for p in folder.glob("*.json")] == [
        verdict_filename("design-critic")
    ]
    data = json.loads(
        (folder / verdict_filename("design-critic")).read_text(encoding="utf-8")
    )
    assert data["verdict"] == "NEEDS_REVISION"


def test_mint_invalid_utf8_verdict_file_exits_4(tmp_path):
    # Finding 2: invalid UTF-8 bytes must be reported as the documented
    # exit 4 (schema-invalid), not crash with a raw UnicodeDecodeError
    # traceback.
    folder = _change_folder_with_design(tmp_path)
    verdict_file = tmp_path / "verdict.md"
    verdict_file.write_bytes(b"verdict: PASS_WITH_NOTES\n\xff\xfe garbage")

    rc = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 4
    assert not (folder / verdict_filename("design-critic")).exists()


def test_mint_two_critics_same_change_folder_coexist(tmp_path):
    # Finding 1: per-critic filenames — design-critic and
    # completeness-critic verdicts in the same change-folder must not
    # clobber each other.
    folder = _change_folder_with_design(tmp_path)
    pass_file = _write(tmp_path / "pass.md", VALID_PASS)
    needs_revision_file = _write(tmp_path / "needs-revision.md", VALID_NEEDS_REVISION)

    rc_design = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
            "--verdict-file",
            str(pass_file),
            "--files",
            "DESIGN.md",
        ]
    )
    rc_completeness = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--critic",
            "completeness-critic",
            "--verdict-file",
            str(needs_revision_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc_design == 0
    assert rc_completeness == 0
    design_marker = folder / verdict_filename("design-critic")
    completeness_marker = folder / verdict_filename("completeness-critic")
    assert design_marker.is_file()
    assert completeness_marker.is_file()
    assert design_marker != completeness_marker

    design_data = json.loads(design_marker.read_text(encoding="utf-8"))
    completeness_data = json.loads(completeness_marker.read_text(encoding="utf-8"))
    assert design_data["verdict"] == "PASS_WITH_NOTES"
    assert completeness_data["verdict"] == "NEEDS_REVISION"

    # Both validate independently against the SAME change-folder/files.
    rc_validate_design = main(
        [
            "validate",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
            "--files",
            "DESIGN.md",
        ]
    )
    rc_validate_completeness = main(
        [
            "validate",
            "--change-folder",
            str(folder),
            "--critic",
            "completeness-critic",
            "--files",
            "DESIGN.md",
        ]
    )
    assert rc_validate_design == 0
    assert rc_validate_completeness == 3


# ------------------------------------------------------------ critic-name


def test_mint_rejects_path_traversal_critic_name_exits_4(tmp_path, capsys):
    # Round-3 fix: --critic flows into verdict_filename() = an
    # f-string filename; an unsanitized "../../evil" escapes the
    # change-folder entirely (CHK-SEC-004).
    folder = _change_folder_with_design(tmp_path)
    verdict_file = _write(tmp_path / "verdict.md", VALID_PASS)
    traversal_target = tmp_path.parent.parent / "evil-verdict.json"

    rc = main(
        [
            "mint",
            "--change-folder",
            str(folder),
            "--critic",
            "../../evil",
            "--verdict-file",
            str(verdict_file),
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 4
    assert "../../evil" in capsys.readouterr().err
    assert not traversal_target.exists()
    assert list(folder.glob("*.json")) == []


def test_validate_rejects_path_traversal_critic_name_exits_4(tmp_path, capsys):
    folder = _change_folder_with_design(tmp_path)

    rc = main(
        [
            "validate",
            "--change-folder",
            str(folder),
            "--critic",
            "../../evil",
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 4
    assert "../../evil" in capsys.readouterr().err


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
                "--critic",
                "design-critic",
                "--verdict-file",
                str(verdict_file),
                "--files",
                "DESIGN.md",
            ]
        )
        == 0
    )

    rc = main(
        [
            "validate",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 0


def test_validate_no_verdict_file_exits_2(tmp_path):
    folder = _change_folder_with_design(tmp_path)

    rc = main(
        [
            "validate",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
            "--files",
            "DESIGN.md",
        ]
    )

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
                "--critic",
                "design-critic",
                "--verdict-file",
                str(verdict_file),
                "--files",
                "DESIGN.md",
            ]
        )
        == 0
    )

    rc = main(
        [
            "validate",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
            "--files",
            "DESIGN.md",
        ]
    )

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
                "--critic",
                "design-critic",
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

    rc = main(
        [
            "validate",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 4


def test_validate_invalid_utf8_verdict_json_exits_4(tmp_path):
    # Finding 2, validate side: a corrupted verdict JSON with invalid
    # UTF-8 bytes must exit 4, not crash with a raw traceback.
    folder = _change_folder_with_design(tmp_path)
    marker = folder / verdict_filename("design-critic")
    marker.write_bytes(b'{"schema": 1, \xff\xfe garbage')

    rc = main(
        [
            "validate",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
            "--files",
            "DESIGN.md",
        ]
    )

    assert rc == 4


def test_validate_files_list_mismatch_exits_4_with_distinct_message(tmp_path, capsys):
    # Finding 3: caller-supplied --files must be compared against the
    # files list recorded at mint time; a divergence is a distinct
    # exit-4 diagnostic, not the generic stale-hash message.
    folder = _change_folder_with_design(tmp_path)
    _write(folder / "OTHER.md", "# Other\n")
    verdict_file = _write(tmp_path / "verdict.md", VALID_PASS)
    assert (
        main(
            [
                "mint",
                "--change-folder",
                str(folder),
                "--critic",
                "design-critic",
                "--verdict-file",
                str(verdict_file),
                "--files",
                "DESIGN.md",
            ]
        )
        == 0
    )

    rc = main(
        [
            "validate",
            "--change-folder",
            str(folder),
            "--critic",
            "design-critic",
            "--files",
            "DESIGN.md,OTHER.md",
        ]
    )

    assert rc == 4
    stderr = capsys.readouterr().err
    assert "files list" in stderr.lower()
    assert "DESIGN.md" in stderr
    assert "OTHER.md" in stderr
    # Must be distinguishable from the generic stale-hash message.
    assert "STALE" not in stderr
