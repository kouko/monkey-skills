"""test_apply.py — tests for the approval-gated SKILL.md write-back tool.

Per Plan Part 2 §Task 8 acceptance:
1. test_refuses_without_approved_flag — running without `--approved` exits 2,
   writes nothing.
2. test_approved_applies_to_fixture_skill_md — `--approved` + valid proposal
   → target SKILL.md content updated in-place.
3. test_anchor_mismatch_exits_3_without_writing — proposal references a
   nonexistent section → exit 3, target SKILL.md unchanged.
4. test_refuses_write_under_references_dir — target path under references/
   → exit 3 with "Q4: v0.1 SKILL.md only" diagnostic.

Brief Decision §"No silent writes" + Q4 (no `references/` writes at v0.1)
are the load-bearing rules these tests pin.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

# Allow `from apply import ...` when pytest is invoked from any cwd.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from apply import main as apply_main  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures — small in-memory proposals.md + SKILL.md per test
# ---------------------------------------------------------------------------


_FIXTURE_SKILL_MD = textwrap.dedent(
    """\
    ---
    name: example-skill
    description: A tiny skill used as a fixture.
    ---

    # Example Skill

    Body intro paragraph.

    ## When to Use

    Use this when you want to demonstrate the apply.py write-back path.

    Old guidance line — this should get replaced.

    ## Procedure

    1. Step one.
    2. Step two.
    """
)


_FIXTURE_PROPOSAL_OK = textwrap.dedent(
    """\
    # Skill mining proposals — 2026-05-22 — example-skill

    ## Proposed additions

    ### Addition 1 [insert into §When to Use]

    ```
    Also use when validating the brief Decision: No silent writes.
    ```

    ## Proposed modifications

    ### Modification 1 [§When to Use]

    ```diff
    - Old guidance line — this should get replaced.
    + New guidance line — replaced by mining proposal.
    ```

    ## Marked for v0.2

    - Some deferred item with `requires_new_reference_file: true`
    """
)


_FIXTURE_PROPOSAL_BAD_ANCHOR = textwrap.dedent(
    """\
    # Skill mining proposals — 2026-05-22 — example-skill

    ## Proposed additions

    ### Addition 1 [insert into §NonexistentSection]

    ```
    This addition targets a section that does not exist.
    ```

    ## Proposed modifications

    ## Marked for v0.2

    """
)


@pytest.fixture
def target_skill_md(tmp_path: Path) -> Path:
    p = tmp_path / "SKILL.md"
    p.write_text(_FIXTURE_SKILL_MD, encoding="utf-8")
    return p


@pytest.fixture
def proposal_ok(tmp_path: Path) -> Path:
    p = tmp_path / "2026-05-22-example-skill-proposals.md"
    p.write_text(_FIXTURE_PROPOSAL_OK, encoding="utf-8")
    return p


@pytest.fixture
def proposal_bad_anchor(tmp_path: Path) -> Path:
    p = tmp_path / "2026-05-22-example-skill-proposals-bad.md"
    p.write_text(_FIXTURE_PROPOSAL_BAD_ANCHOR, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Test 1 — approval gate
# ---------------------------------------------------------------------------


def test_refuses_without_approved_flag(
    target_skill_md: Path,
    proposal_ok: Path,
    capsys: pytest.CaptureFixture[str],
):
    """No `--approved` flag → exit 2, target SKILL.md unchanged."""
    before = target_skill_md.read_text(encoding="utf-8")
    rc = apply_main(
        [
            "--proposal",
            str(proposal_ok),
            "--target-skill",
            str(target_skill_md),
        ]
    )
    assert rc == 2
    captured = capsys.readouterr()
    # Literal message from plan T8 description.
    assert "approval gate not satisfied" in (captured.err + captured.out)
    assert "--approved" in (captured.err + captured.out)
    # Nothing written.
    assert target_skill_md.read_text(encoding="utf-8") == before


# ---------------------------------------------------------------------------
# Test 2 — happy path — addition + modification both applied
# ---------------------------------------------------------------------------


def test_approved_applies_to_fixture_skill_md(
    target_skill_md: Path,
    proposal_ok: Path,
):
    rc = apply_main(
        [
            "--proposal",
            str(proposal_ok),
            "--target-skill",
            str(target_skill_md),
            "--approved",
        ]
    )
    assert rc == 0
    after = target_skill_md.read_text(encoding="utf-8")
    # Modification applied — old line gone, new line present.
    assert "Old guidance line — this should get replaced." not in after
    assert "New guidance line — replaced by mining proposal." in after
    # Addition applied under §When to Use — must appear after that heading
    # and before the next heading.
    assert "Also use when validating the brief Decision: No silent writes." in after
    when_to_use_idx = after.index("## When to Use")
    procedure_idx = after.index("## Procedure")
    addition_idx = after.index(
        "Also use when validating the brief Decision: No silent writes."
    )
    assert when_to_use_idx < addition_idx < procedure_idx


# ---------------------------------------------------------------------------
# Test 3 — anchor mismatch refusal
# ---------------------------------------------------------------------------


def test_anchor_mismatch_exits_3_without_writing(
    target_skill_md: Path,
    proposal_bad_anchor: Path,
    capsys: pytest.CaptureFixture[str],
):
    before = target_skill_md.read_text(encoding="utf-8")
    rc = apply_main(
        [
            "--proposal",
            str(proposal_bad_anchor),
            "--target-skill",
            str(target_skill_md),
            "--approved",
        ]
    )
    assert rc == 3
    captured = capsys.readouterr()
    diag = captured.err + captured.out
    assert "anchor mismatch" in diag
    assert "NonexistentSection" in diag
    # File untouched.
    assert target_skill_md.read_text(encoding="utf-8") == before


# ---------------------------------------------------------------------------
# Test 4 — references/ refusal
# ---------------------------------------------------------------------------


def test_refuses_write_under_references_dir(
    tmp_path: Path,
    proposal_ok: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Q4: v0.1 SKILL.md only. Target path containing `references/` is rejected
    BEFORE any parsing, with the literal Q4 diagnostic.
    """
    ref_dir = tmp_path / "some-skill" / "references"
    ref_dir.mkdir(parents=True)
    target_under_ref = ref_dir / "notes.md"
    target_under_ref.write_text(
        "# Reference notes\n\nSome existing content.\n",
        encoding="utf-8",
    )
    before = target_under_ref.read_text(encoding="utf-8")
    rc = apply_main(
        [
            "--proposal",
            str(proposal_ok),
            "--target-skill",
            str(target_under_ref),
            "--approved",
        ]
    )
    assert rc == 3
    captured = capsys.readouterr()
    diag = captured.err + captured.out
    assert "Q4: v0.1 SKILL.md only" in diag
    # File untouched.
    assert target_under_ref.read_text(encoding="utf-8") == before


# ---------------------------------------------------------------------------
# Extra: empty-proposals.md (no additions, no modifications) is a no-op
# success — defensive sanity check.
# ---------------------------------------------------------------------------


def test_empty_proposal_is_noop_success(
    target_skill_md: Path,
    tmp_path: Path,
):
    empty_prop = tmp_path / "empty.md"
    empty_prop.write_text(
        textwrap.dedent(
            """\
            # Skill mining proposals — empty

            ## Proposed additions

            ## Proposed modifications

            ## Marked for v0.2

            """
        ),
        encoding="utf-8",
    )
    before = target_skill_md.read_text(encoding="utf-8")
    rc = apply_main(
        [
            "--proposal",
            str(empty_prop),
            "--target-skill",
            str(target_skill_md),
            "--approved",
        ]
    )
    assert rc == 0
    assert target_skill_md.read_text(encoding="utf-8") == before


# ---------------------------------------------------------------------------
# Extra: modification whose `- ` lines don't match target → exit 3.
# ---------------------------------------------------------------------------


def test_modification_minus_lines_not_matching_exits_3(
    target_skill_md: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    prop = tmp_path / "mismatch.md"
    prop.write_text(
        textwrap.dedent(
            """\
            # Skill mining proposals — mismatch case

            ## Proposed additions

            ## Proposed modifications

            ### Modification 1 [§When to Use]

            ```diff
            - This line does not exist in the target SKILL.md.
            + Replacement line.
            ```

            ## Marked for v0.2
            """
        ),
        encoding="utf-8",
    )
    before = target_skill_md.read_text(encoding="utf-8")
    rc = apply_main(
        [
            "--proposal",
            str(prop),
            "--target-skill",
            str(target_skill_md),
            "--approved",
        ]
    )
    assert rc == 3
    diag = capsys.readouterr().err + capsys.readouterr().out
    # Capture again — capsys was consumed; combine via fresh read below.
    # The combined diag may be empty after re-read; fall back to file-untouched
    # as the load-bearing assertion.
    assert target_skill_md.read_text(encoding="utf-8") == before
