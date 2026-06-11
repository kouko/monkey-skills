"""Tests for validate_spec_output.py — OpenSpec skeleton checks (Task 2).

The validator checks a spec-toolkit OUTPUT DIRECTORY against the OpenSpec
change-folder SKELETON. Skeleton-valid iff:
  1. proposal.md present.
  2. specs/ subdir with >=1 *.md delta file.
  3. >=1 delta carries a `## ADDED Requirements` header.
  4. >=1 `### Requirement:` whose body line carries RFC-2119 (MUST/SHALL/SHOULD/MAY).
  5. >=1 `#### Scenario:` with GIVEN/WHEN/THEN lines beneath it.

Validator must be tolerant of EXTRA content (structure-only, mirrors
`openspec validate`). Fixtures built INLINE via tmp_path (flat-folder rule:
no fixtures/ subdir).

Task 3 will ADD additive-section checks (test_additive_*) to this same file.
"""

import subprocess
import sys
from pathlib import Path

from validate_spec_output import validate


SCRIPT = Path(__file__).with_name("validate_spec_output.py")


# --- fixture builders (inline; no fixtures/ subdir) -------------------------

def _well_formed_delta() -> str:
    return (
        "## ADDED Requirements\n"
        "\n"
        "### Requirement: User login\n"
        "The system MUST authenticate a user with valid credentials.\n"
        "\n"
        "#### Scenario: Valid credentials\n"
        "- GIVEN a registered user\n"
        "- WHEN they submit a correct password\n"
        "- THEN they are granted a session\n"
    )


def _write_skeleton(root: Path, *, delta_body: str | None = None,
                    with_proposal: bool = True) -> Path:
    """Build a skeleton output dir under root; return root."""
    if with_proposal:
        (root / "proposal.md").write_text("# Proposal\n\nWhy this change.\n",
                                          encoding="utf-8")
    specs = root / "specs" / "auth"
    specs.mkdir(parents=True, exist_ok=True)
    body = _well_formed_delta() if delta_body is None else delta_body
    (specs / "spec.md").write_text(body, encoding="utf-8")
    return root


# --- skeleton tests --------------------------------------------------------

def test_skeleton_accepts_well_formed(tmp_path):
    root = _write_skeleton(tmp_path)
    ok, problems = validate(root)
    assert ok, f"well-formed skeleton should pass, got: {problems}"
    assert problems == []


def test_skeleton_rejects_missing_proposal(tmp_path):
    root = _write_skeleton(tmp_path, with_proposal=False)
    ok, problems = validate(root)
    assert not ok
    assert any("proposal.md" in p for p in problems), problems


def test_skeleton_rejects_missing_specs_dir(tmp_path):
    (tmp_path / "proposal.md").write_text("# Proposal\n", encoding="utf-8")
    ok, problems = validate(tmp_path)
    assert not ok
    assert any("specs/" in p for p in problems), problems


def test_skeleton_rejects_missing_added_requirements(tmp_path):
    body = (
        "### Requirement: User login\n"
        "The system MUST authenticate a user.\n"
        "\n"
        "#### Scenario: Valid\n"
        "- GIVEN a user\n- WHEN login\n- THEN session\n"
    )
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("ADDED Requirements" in p for p in problems), problems


def test_skeleton_rejects_requirement_without_rfc2119(tmp_path):
    body = (
        "## ADDED Requirements\n"
        "\n"
        "### Requirement: User login\n"
        "The system authenticates a user with valid credentials.\n"
        "\n"
        "#### Scenario: Valid\n"
        "- GIVEN a user\n- WHEN login\n- THEN session\n"
    )
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("RFC-2119" in p or "MUST" in p for p in problems), problems


def test_skeleton_rejects_missing_scenario(tmp_path):
    body = (
        "## ADDED Requirements\n"
        "\n"
        "### Requirement: User login\n"
        "The system MUST authenticate a user.\n"
    )
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("Scenario" in p for p in problems), problems


def test_skeleton_rejects_scenario_missing_given_when_then(tmp_path):
    body = (
        "## ADDED Requirements\n"
        "\n"
        "### Requirement: User login\n"
        "The system MUST authenticate a user.\n"
        "\n"
        "#### Scenario: Valid\n"
        "- GIVEN a user\n"
        "- WHEN they login\n"
    )  # missing THEN
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("THEN" in p for p in problems), problems


def test_skeleton_tolerates_extra_content(tmp_path):
    body = _well_formed_delta() + (
        "\n## Some Unknown Section\n"
        "Extra prose the validator must not reject.\n"
        "\n### MODIFIED Requirements\n"
        "### Requirement: Other\n"
        "Whatever SHOULD happen.\n"
    )
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert ok, f"extra content must be tolerated, got: {problems}"


# --- CLI contract (thin __main__) ------------------------------------------

def _run_cli(target: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True, text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": ""},
    )


def test_cli_exit_zero_on_valid(tmp_path):
    root = _write_skeleton(tmp_path)
    proc = _run_cli(root)
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_cli_nonzero_with_actionable_message_on_invalid(tmp_path):
    root = _write_skeleton(tmp_path, with_proposal=False)
    proc = _run_cli(root)
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert "proposal.md" in combined, combined
