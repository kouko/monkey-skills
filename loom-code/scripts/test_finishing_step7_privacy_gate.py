"""Structural grep-test guarding the removal of the SECOND
human-confirmation stop from finishing-a-development-branch's Step 7.

Context: Step 7 used to STOP and ask the user to approve the composed
commit message + trailers before committing — a blanket ask that was
also the only privacy check in the flow. This task replaces that ask
with the automated privacy gate defined by git-memory's compose-commit
protocol Step 3.5 (layer-1 `privacy-scan.py` + layer-2 fresh-context
judge, fail-closed): PASS proceeds silently; BLOCK surfaces findings
and asks the human. The human returns only on failure — exception-based,
not blanket. Step 9's wording (which depended on "user approval at
Step 7") and the ASK-rationale paragraph (which claimed "each
user-visible action has a confirmation") are updated to match.

Neighborhood-scoped (mirrors test_finishing_merge_path_guidance.py and
test_finishing_step3_autoproceed.py): Step 7, Step 9, and the
ASK-rationale paragraph are sliced independently so a whole-file
substring check can't false-green off text living elsewhere in the
file. Guard slices for Step 11 / Step 12 confirm the two remaining
outward-facing asks (PR-open, worktree-removal) survive untouched.

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "finishing-a-development-branch" / "SKILL.md"

OLD_STEP7_ASK = "ASK for approval"
OLD_STEP9_DEP = "user approval at Step 7"
OLD_RATIONALE_CLAIM = "Each user-visible action has a confirmation"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _step_slice(text: str, start_marker: str, end_marker: str) -> str:
    """Window of text from start_marker up to (not including) end_marker.

    Scopes assertions to one region so generic words shared across
    steps don't produce a false-green whole-file match."""
    start = text.find(start_marker)
    assert start != -1, f"start marker not found: {start_marker!r}"
    end = text.find(end_marker, start)
    assert end != -1, f"end marker not found after start: {end_marker!r}"
    assert end > start, "end marker must follow start marker"
    return text[start:end]


def _step7_slice(text: str) -> str:
    return _step_slice(
        text,
        "7. ",
        "8. git hygiene before the close-out commit:",
    )


def _step9_slice(text: str) -> str:
    return _step_slice(
        text,
        "\n9. git commit",
        "9b. Commit-carrier verify gate",
    )


def _rationale_slice(text: str) -> str:
    return _step_slice(
        text,
        "**ASK",
        "## Red Flags",
    )


def _step11_slice(text: str) -> str:
    return _step_slice(
        text,
        '11. ASK user: "Open a PR? (y/N)"',
        '12. ASK user: "Branch was in .worktrees/',
    )


def _step12_slice(text: str) -> str:
    return _step_slice(
        text,
        '12. ASK user: "Branch was in .worktrees/',
        "13. Report final state",
    )


def test_step7_invokes_privacy_gate():
    """Step 7 must invoke the privacy gate (git-memory compose-commit
    Step 3.5's two-layer check), not a blanket commit-message approval."""
    step7 = _step7_slice(_text())
    assert "privacy" in step7.lower(), \
        "Step 7 must invoke the privacy gate"


def test_step7_pass_proceeds_silently():
    """Step 7's PASS branch must proceed silently — no user ask."""
    step7 = _step7_slice(_text())
    assert "PASS" in step7, "Step 7 must define a PASS branch"
    assert "proceed silently" in step7.lower(), \
        "Step 7's PASS branch must proceed silently"


def test_step7_block_asks_user():
    """Step 7's BLOCK branch must surface findings and ask the user —
    this is now the ONLY stop Step 7 has, and only on failure."""
    step7 = _step7_slice(_text())
    assert "BLOCK" in step7, "Step 7 must define a BLOCK branch"
    assert "ask" in step7.lower(), \
        "Step 7's BLOCK branch must ask the user"


def test_step7_old_blanket_ask_absent():
    """The old blanket 'ASK for approval' of the commit message must be
    gone from Step 7 — it described the stop this task removes."""
    step7 = _step7_slice(_text())
    assert OLD_STEP7_ASK not in step7, \
        f"Step 7 must not contain the old blanket ask wording {OLD_STEP7_ASK!r}"


def test_step9_no_longer_requires_blanket_approval():
    """Step 9's dependency wording must no longer require blanket 'user
    approval at Step 7' — the commit now proceeds after the privacy
    gate PASSes (or after the user resolves a BLOCK)."""
    step9 = _step9_slice(_text())
    assert OLD_STEP9_DEP not in step9, \
        f"Step 9 must not contain the old dependency wording {OLD_STEP9_DEP!r}"


def test_rationale_paragraph_drops_blanket_confirmation_claim():
    """The ASK-rationale paragraph must no longer claim 'each
    user-visible action has a confirmation' — a T6 reviewer flagged
    this as over-claiming universality now that Step 7 auto-proceeds
    on PASS."""
    rationale = _rationale_slice(_text())
    assert OLD_RATIONALE_CLAIM not in rationale, \
        f"Rationale paragraph must not contain {OLD_RATIONALE_CLAIM!r}"


def test_rationale_paragraph_reflects_exception_based_model():
    """The rewritten rationale must describe the exception-based model:
    autonomous happy path, human returns only for outward-facing
    actions or a privacy-gate failure."""
    rationale = _rationale_slice(_text())
    assert "autonomous" in rationale.lower(), \
        "Rationale must describe the happy path as autonomous"
    assert "outward-facing" in rationale.lower(), \
        "Rationale must name the outward-facing actions as the remaining stops"
    assert "privacy" in rationale.lower(), \
        "Rationale must name the privacy-gate BLOCK as the remaining exception stop"


def test_guard_step11_pr_open_ask_intact():
    """Guard against over-deletion: Step 11's PR-open ask must survive
    untouched — it is outward-facing and stays."""
    step11 = _step11_slice(_text())
    assert 'ASK user: "Open a PR? (y/N)"' in step11, \
        "Step 11's PR-open ask must remain intact"


def test_guard_step12_worktree_ask_intact():
    """Guard against over-deletion: Step 12's worktree-removal ask must
    survive untouched — it is outward-facing and stays."""
    step12 = _step12_slice(_text())
    assert "remove the worktree? (y/N)" in step12, \
        "Step 12's worktree-removal ask must remain intact"
