"""Tests for validate_design_output.py — design change-folder structure (Task 8).

The validator checks a design CHANGE-FOLDER (a directory) against the
interface-design-toolkit output contract. Task 8 covers the first check only:
the change-folder contains the design-system doc (`DESIGN.md` for the GUI
modality) AND `ui-flows.md`.

Later tasks append further checks to the same registry:
  - Task 9: DESIGN.md carries the 8 canonical sections.
  - Task 10: ui-flows.md carries its required sections.

Each check = a function (root: Path) -> list[str] of problems (empty == ok),
mirroring spec-toolkit/scripts/validate_spec_output.py. CLI:
`python validate_design_output.py <dir>` -> exit 0 valid / 1 invalid.

Synthetic content only; no real brand / company / customer / product names.
Fixtures built INLINE via tmp_path (flat-folder rule: no fixtures/ subdir).
"""

import subprocess
import sys
from pathlib import Path

from validate_design_output import validate


SCRIPT = Path(__file__).with_name("validate_design_output.py")


# --- fixture builders (inline; no fixtures/ subdir) -------------------------

def _write_gui_change_folder(root: Path, *, design: bool = True,
                             ui_flows: bool = True) -> None:
    """Materialize a GUI design change-folder under `root`.

    `design` / `ui_flows` toggle whether each file is written, so a test can
    omit one and assert the absence is flagged. File *bodies* are minimal —
    Task 8 checks presence only; section-content checks arrive in T9/T10.
    """
    root.mkdir(parents=True, exist_ok=True)
    if design:
        (root / "DESIGN.md").write_text(
            "# DESIGN\n\nGUI visual design system (placeholder body).\n",
            encoding="utf-8",
        )
    if ui_flows:
        (root / "ui-flows.md").write_text(
            "# ui-flows\n\nInteraction flows (placeholder body).\n",
            encoding="utf-8",
        )


# --- presence check (Task 8 — THE first check) -----------------------------

def test_complete_gui_folder_passes(tmp_path):
    _write_gui_change_folder(tmp_path)
    ok, problems = validate(tmp_path)
    assert ok, f"complete GUI change-folder should pass, got: {problems}"
    assert problems == []


def test_missing_file_flagged(tmp_path):
    # ui-flows.md absent -> the change-folder is incomplete.
    _write_gui_change_folder(tmp_path, design=True, ui_flows=False)
    ok, problems = validate(tmp_path)
    assert not ok
    assert any("ui-flows.md" in m for m in problems), problems


def test_missing_design_doc_flagged(tmp_path):
    # DESIGN.md absent -> the design-system doc is missing for GUI.
    _write_gui_change_folder(tmp_path, design=False, ui_flows=True)
    ok, problems = validate(tmp_path)
    assert not ok
    assert any("DESIGN.md" in m for m in problems), problems


def test_missing_directory_flagged(tmp_path):
    missing = tmp_path / "does-not-exist"
    ok, problems = validate(missing)
    assert not ok
    assert problems, "a non-existent directory must be flagged"


# --- CLI contract (thin __main__) ------------------------------------------

def _run_cli(target: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True, text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": ""},
    )


def test_cli_exit_zero_on_valid(tmp_path):
    _write_gui_change_folder(tmp_path)
    proc = _run_cli(tmp_path)
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_cli_nonzero_with_actionable_message_on_invalid(tmp_path):
    _write_gui_change_folder(tmp_path, design=True, ui_flows=False)
    proc = _run_cli(tmp_path)
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert "ui-flows.md" in combined, combined
