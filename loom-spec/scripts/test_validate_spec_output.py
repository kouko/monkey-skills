"""Tests for validate_spec_output.py — OpenSpec skeleton checks (Task 2).

The validator checks a loom-spec OUTPUT DIRECTORY against the OpenSpec
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


def _well_formed_additive() -> str:
    """The additive sections loom-spec requires in proposal.md (the
    three-flow artifacts USM backbone / OOUX object model / Path × edge matrix
    plus Provenance and a non-empty Blind-spots body, plus the L2/L3
    Cross-object combinations / Journey navigation sections)."""
    return (
        "## USM backbone\n"
        "- Sign up → Log in → Use feature → Log out\n"
        "\n"
        "## OOUX object model\n"
        "- User (objects), Session (objects)\n"
        "\n"
        "## Provenance\n"
        "- User login: seeded\n"
        "- Lockout after N tries: critic-found\n"
        "\n"
        "## Blind spots — needs human/field input\n"
        "- Lockout threshold N is a policy call I cannot judge.\n"
        "\n"
        "## Path × edge matrix\n"
        "| path | edge |\n"
        "| --- | --- |\n"
        "| login | wrong password |\n"
        "\n"
        "## Cross-object combinations\n"
        "- User × Session: one user holds many sessions\n"
        "\n"
        "## Journey navigation\n"
        "- From login screen → dashboard → feature\n"
    )


def _write_skeleton(root: Path, *, delta_body: str | None = None,
                    with_proposal: bool = True,
                    proposal_body: str | None = None) -> Path:
    """Build a skeleton output dir under root; return root.

    `proposal_body`, when given, is the full proposal.md content (lets
    additive tests control which sections are present)."""
    if with_proposal:
        content = ("# Proposal\n\nWhy this change.\n\n" + _well_formed_additive()
                   if proposal_body is None else proposal_body)
        (root / "proposal.md").write_text(content, encoding="utf-8")
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


# --- additive-section tests (Task 3) ---------------------------------------
# loom-spec's differentiating richness lives in proposal.md's additive
# sections; the OpenSpec delta under specs/ stays pure. So additive checks
# operate on proposal.md.

def _proposal_with(*, usm=True, ooux=True, provenance=True, blind_spots=True,
                   blind_spots_empty=False, matrix=True,
                   cross_object=True, journey=True) -> str:
    parts = ["# Proposal\n\nWhy this change.\n"]
    if usm:
        parts.append("## USM backbone\n- Sign up → Log in → Use feature\n")
    if ooux:
        parts.append("## OOUX object model\n- User (objects), Session (objects)\n")
    if provenance:
        parts.append("## Provenance\n- User login: seeded\n")
    if blind_spots:
        if blind_spots_empty:
            parts.append("## Blind spots — needs human/field input\n")
        else:
            parts.append("## Blind spots — needs human/field input\n"
                         "- Lockout threshold is a policy call I cannot judge.\n")
    if matrix:
        parts.append("## Path × edge matrix\n| path | edge |\n| --- | --- |\n"
                     "| login | wrong password |\n")
    if cross_object:
        parts.append("## Cross-object combinations\n"
                     "- User × Session: one user holds many sessions\n")
    if journey:
        parts.append("## Journey navigation\n"
                     "- From login screen → dashboard → feature\n")
    return "\n".join(parts)


def test_additive_rejects_missing_usm_backbone(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with(usm=False))
    ok, problems = validate(root)
    assert not ok
    assert any("USM backbone" in p for p in problems), problems


def test_additive_rejects_missing_ooux_object_model(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with(ooux=False))
    ok, problems = validate(root)
    assert not ok
    assert any("OOUX object model" in p for p in problems), problems


def test_additive_usm_prose_mention_does_not_satisfy(tmp_path):
    # A prose mention of "USM backbone" must NOT count — whole-line header only.
    body = _proposal_with(usm=False)
    body += "\nWe considered a USM backbone here but did not add the section.\n"
    root = _write_skeleton(tmp_path, proposal_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("USM backbone" in p for p in problems), problems


def test_additive_rejects_missing_provenance(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with(provenance=False))
    ok, problems = validate(root)
    assert not ok
    assert any("Provenance" in p for p in problems), problems


def test_additive_rejects_missing_blind_spots(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with(blind_spots=False))
    ok, problems = validate(root)
    assert not ok
    assert any("Blind spots" in p for p in problems), problems


def test_additive_rejects_empty_blind_spots(tmp_path):
    root = _write_skeleton(
        tmp_path, proposal_body=_proposal_with(blind_spots_empty=True))
    ok, problems = validate(root)
    assert not ok
    assert any("Blind spots" in p for p in problems), problems


def test_additive_rejects_missing_path_edge_matrix(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with(matrix=False))
    ok, problems = validate(root)
    assert not ok
    assert any("Path × edge matrix" in p for p in problems), problems


def _proposal_five_original_only() -> str:
    """The five ORIGINAL additive sections, but MISSING the two L2/L3 sections
    (Cross-object combinations / Journey navigation)."""
    return (
        "# Proposal\n\nWhy this change.\n"
        "\n## USM backbone\n- Sign up → Log in → Use feature\n"
        "\n## OOUX object model\n- User (objects), Session (objects)\n"
        "\n## Provenance\n- User login: seeded\n"
        "\n## Blind spots — needs human/field input\n"
        "- Lockout threshold is a policy call I cannot judge.\n"
        "\n## Path × edge matrix\n| path | edge |\n| --- | --- |\n"
        "| login | wrong password |\n"
    )


def test_rejects_missing_cross_object_and_journey(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_five_original_only())
    ok, problems = validate(root)
    assert not ok
    assert any("Cross-object combinations" in p for p in problems), problems
    assert any("Journey navigation" in p for p in problems), problems


def test_additive_accepts_complete_hybrid(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with())
    ok, problems = validate(root)
    assert ok, f"complete hybrid (skeleton + 5 additive) should pass, got: {problems}"
    assert problems == []


def test_additive_accepts_complete_hybrid_cli(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with())
    proc = _run_cli(root)
    assert proc.returncode == 0, proc.stderr + proc.stdout


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
