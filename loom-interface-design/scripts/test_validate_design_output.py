"""Tests for validate_design_output.py — design change-folder structure (Task 8).

The validator checks a design CHANGE-FOLDER (a directory) against the
loom-interface-design output contract. Task 8 covers the first check only:
the change-folder contains the design-system doc (`DESIGN.md` for the GUI
modality) AND `ui-flows.md`.

Later tasks append further checks to the same registry:
  - Task 9: DESIGN.md carries the 8 canonical sections.
  - Task 10: ui-flows.md carries its required sections.

Each check = a function (root: Path) -> list[str] of problems (empty == ok),
mirroring loom-spec/scripts/validate_spec_output.py. CLI:
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

# The 8 canonical `##` section headings DESIGN.md MUST carry, in order, per
# design-system/references/design-md-schema.md. Used to build a complete
# DESIGN.md body so the presence + section checks both pass.
_DESIGN_SECTIONS = [
    "Overview / Brand",
    "Colors",
    "Typography",
    "Layout",
    "Elevation & Depth",
    "Shapes",
    "Components",
    "Do's & Don'ts",
]


def _design_body(sections=_DESIGN_SECTIONS) -> str:
    """Build a minimal DESIGN.md body carrying the given `##` sections."""
    lines = ["# DESIGN", "", "GUI visual design system (placeholder body)."]
    for name in sections:
        lines += ["", f"## {name}", "", "Token block placeholder."]
    return "\n".join(lines) + "\n"


# The required `##` section headings ui-flows.md MUST carry, per
# interaction-flows/references/ux-flow-checklist.md (lenient/minimal subset:
# inventory + user flows + UI structure). Used to build a complete ui-flows.md
# body so the presence + section checks both pass.
_UI_FLOWS_SECTIONS = [
    "Inventory",
    "User Flows",
    "UI Structure",
]


def _ui_flows_body(sections=_UI_FLOWS_SECTIONS) -> str:
    """Build a minimal ui-flows.md body carrying the given `##` sections."""
    lines = ["# ui-flows", "", "Interaction flows (placeholder body)."]
    for name in sections:
        lines += ["", f"## {name}", "", "Surface block placeholder."]
    return "\n".join(lines) + "\n"


def _write_gui_change_folder(root: Path, *, design: bool = True,
                             ui_flows: bool = True,
                             design_sections=_DESIGN_SECTIONS,
                             ui_flows_sections=_UI_FLOWS_SECTIONS) -> None:
    """Materialize a GUI design change-folder under `root`.

    `design` / `ui_flows` toggle whether each file is written, so a test can
    omit one and assert the absence is flagged. `design_sections` controls
    which `##` sections DESIGN.md carries (default = all 8 canonical), so a
    test can drop one and assert the omission is flagged. `ui_flows_sections`
    likewise controls which `##` sections ui-flows.md carries (default = all
    required), so a test can drop one and assert the omission is flagged.
    """
    root.mkdir(parents=True, exist_ok=True)
    if design:
        (root / "DESIGN.md").write_text(
            _design_body(design_sections),
            encoding="utf-8",
        )
    if ui_flows:
        (root / "ui-flows.md").write_text(
            _ui_flows_body(ui_flows_sections),
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


def test_design_missing_section_flagged(tmp_path):
    # DESIGN.md present but missing the Typography section -> flagged.
    incomplete = [s for s in _DESIGN_SECTIONS if s != "Typography"]
    _write_gui_change_folder(tmp_path, design_sections=incomplete)
    ok, problems = validate(tmp_path)
    assert not ok
    assert any("Typography" in m for m in problems), problems


def test_design_section_name_in_prose_does_not_count(tmp_path):
    # A section name appearing only in prose (not as a `## ` heading) must
    # NOT satisfy the check — whole-line heading matching, not substring.
    body = (
        "# DESIGN\n\n"
        "This system covers Typography in great detail within the body.\n"
    )
    # carry every heading EXCEPT Typography, which appears only in prose above
    for name in _DESIGN_SECTIONS:
        if name != "Typography":
            body += f"\n## {name}\n\nToken block placeholder.\n"
    (tmp_path / "DESIGN.md").write_text(body, encoding="utf-8")
    (tmp_path / "ui-flows.md").write_text(
        "# ui-flows\n\nInteraction flows.\n", encoding="utf-8")
    ok, problems = validate(tmp_path)
    assert not ok
    assert any("Typography" in m for m in problems), problems


def test_uiflows_missing_section_flagged(tmp_path):
    # ui-flows.md present but missing the User Flows section -> flagged.
    incomplete = [s for s in _UI_FLOWS_SECTIONS if s != "User Flows"]
    _write_gui_change_folder(tmp_path, ui_flows_sections=incomplete)
    ok, problems = validate(tmp_path)
    assert not ok
    assert any("User Flows" in m for m in problems), problems


def test_uiflows_section_name_in_prose_does_not_count(tmp_path):
    # A section name appearing only in prose (not as a `## ` heading) must
    # NOT satisfy the check — whole-line heading matching, not substring.
    body = (
        "# ui-flows\n\n"
        "This doc covers User Flows in great detail within the body.\n"
    )
    # carry every heading EXCEPT User Flows, which appears only in prose above
    for name in _UI_FLOWS_SECTIONS:
        if name != "User Flows":
            body += f"\n## {name}\n\nSurface block placeholder.\n"
    (tmp_path / "ui-flows.md").write_text(body, encoding="utf-8")
    (tmp_path / "DESIGN.md").write_text(_design_body(), encoding="utf-8")
    ok, problems = validate(tmp_path)
    assert not ok
    assert any("User Flows" in m for m in problems), problems


def test_uiflows_absent_not_double_reported_by_section_check(tmp_path):
    # When ui-flows.md is absent, the presence check (T8) flags it; the
    # section check must return [] (no double-reporting of the same problem).
    _write_gui_change_folder(tmp_path, design=True, ui_flows=False)
    ok, problems = validate(tmp_path)
    assert not ok
    # exactly one problem mentioning ui-flows.md (presence), not two.
    uiflows_msgs = [m for m in problems if "ui-flows.md" in m]
    assert len(uiflows_msgs) == 1, uiflows_msgs


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


# --- per-change layout: ui-flows.md in docs/loom/<change-id>/ ----------------
# DESIGN.md is product-level (one per product, at docs/loom/); ui-flows.md is
# per-change (docs/loom/<change-id>/). The validator, given the CHANGE folder,
# must accept DESIGN.md at the folder itself (legacy side-by-side layout) OR
# at its parent (per-change layout).

def test_change_folder_with_design_at_parent_passes(tmp_path):
    (tmp_path / "DESIGN.md").write_text(_design_body(), encoding="utf-8")
    change = tmp_path / "my-feature"
    change.mkdir()
    (change / "ui-flows.md").write_text(_ui_flows_body(), encoding="utf-8")
    ok, problems = validate(change)
    assert ok, problems


def test_design_sections_checked_at_parent(tmp_path):
    """A parent-level DESIGN.md is not just presence-checked — its 8-section
    contract is enforced the same as a side-by-side one."""
    (tmp_path / "DESIGN.md").write_text(
        _design_body(sections=_DESIGN_SECTIONS[:4]), encoding="utf-8")
    change = tmp_path / "my-feature"
    change.mkdir()
    (change / "ui-flows.md").write_text(_ui_flows_body(), encoding="utf-8")
    ok, problems = validate(change)
    assert not ok
    assert any("DESIGN.md" in p for p in problems)


def test_missing_design_at_both_levels_flagged(tmp_path):
    change = tmp_path / "my-feature"
    change.mkdir()
    (change / "ui-flows.md").write_text(_ui_flows_body(), encoding="utf-8")
    ok, problems = validate(change)
    assert not ok
    assert any("DESIGN.md" in p for p in problems)


def test_side_by_side_design_md_takes_precedence(tmp_path):
    """Legacy layout stays valid; a change-folder-local DESIGN.md wins over
    the parent one (most-specific-first resolution)."""
    (tmp_path / "DESIGN.md").write_text(
        _design_body(sections=_DESIGN_SECTIONS[:4]), encoding="utf-8")
    change = tmp_path / "chg"
    change.mkdir()
    (change / "DESIGN.md").write_text(_design_body(), encoding="utf-8")
    (change / "ui-flows.md").write_text(_ui_flows_body(), encoding="utf-8")
    ok, problems = validate(change)
    assert ok, problems


def test_relative_dot_invocation_from_inside_change_folder(tmp_path, monkeypatch):
    """Invoking the validator with root="." from INSIDE the change folder must
    still find the parent-level DESIGN.md — Path(".").parent is Path("."), so
    the resolver must normalize the root to an absolute path first."""
    (tmp_path / "DESIGN.md").write_text(_design_body(), encoding="utf-8")
    change = tmp_path / "my-feature"
    change.mkdir()
    (change / "ui-flows.md").write_text(_ui_flows_body(), encoding="utf-8")
    monkeypatch.chdir(change)
    ok, problems = validate(Path("."))
    assert ok, problems
