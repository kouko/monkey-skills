"""Structural grep-test guarding the removal of the PASS_WITH_NOTES
human-confirmation stop from finishing-a-development-branch's Step 3.

Context: Step 3 dispatches requesting-code-review and routes on the
returned verdict. Previously, PASS_WITH_NOTES (exactly one 🟡 minor
finding, no 🔴) STOPPED and asked the user whether to proceed or
remediate — a second confirmation stop alongside NEEDS_REVISION's hard
STOP. The user removed that ask: PASS_WITH_NOTES now auto-proceeds and
carries the 🟡 finding forward into the PR body and the final close-out
report as noted debt. NEEDS_REVISION's hard STOP is unchanged, and PASS
(all 🟢) still proceeds silently.

Neighborhood-scoped (mirrors test_finishing_merge_path_guidance.py): the
phase-diagram line and the Step 3 body are sliced independently so a
whole-file substring check can't false-green off text elsewhere in the
file, and so the old ask wording's absence is checked exactly where it
used to live (not merely "somewhere in the file").

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "finishing-a-development-branch" / "SKILL.md"

OLD_PHASE_DIAGRAM_ASK = "surfaces + asks"
OLD_STEP3_ASK = "ASK user to proceed or remediate"


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


def _phase_diagram_slice(text: str) -> str:
    return _step_slice(
        text,
        "├─→ Phase 1: requesting-code-review",
        "├─→ Phase 2: verification-before-completion",
    )


def _step3_slice(text: str) -> str:
    return _step_slice(
        text,
        "3. Dispatch requesting-code-review",
        "4. Before applying any review findings from Step 3",
    )


def test_step3_pass_with_notes_auto_proceeds():
    """The PASS_WITH_NOTES branch must state it auto-proceeds, not that
    it asks the user to proceed or remediate."""
    step3 = _step3_slice(_text())
    assert "auto-proceed" in step3.lower() or "auto proceed" in step3.lower(), \
        "Step 3's PASS_WITH_NOTES branch must state it auto-proceeds"


def test_step3_pass_with_notes_carries_finding_forward():
    """The PASS_WITH_NOTES branch must carry the 🟡 finding forward into
    both the PR body and the final close-out report."""
    step3 = _step3_slice(_text())
    assert "PR body" in step3, \
        "Step 3's PASS_WITH_NOTES branch must mention carrying the finding into the PR body"
    assert "report" in step3.lower(), \
        "Step 3's PASS_WITH_NOTES branch must mention carrying the finding into the close-out report"


def test_step3_old_ask_wording_absent():
    """The old 'ASK user to proceed or remediate' wording must be gone
    from Step 3 — it described the stop this task removes."""
    step3 = _step3_slice(_text())
    assert OLD_STEP3_ASK not in step3, \
        f"Step 3 must not contain the old ask wording {OLD_STEP3_ASK!r}"


def test_step3_no_stale_reference_to_pass_with_notes_asking():
    """No leftover sentence in Step 3 may still claim PASS_WITH_NOTES
    'asks' — the explicit-contract bullet used to say the user-ask gate
    'is UNCHANGED ... it still asks', which is now false."""
    step3 = _step3_slice(_text())
    assert "still asks" not in step3.lower(), \
        "Step 3 must not claim PASS_WITH_NOTES 'still asks' anywhere"


def test_phase_diagram_old_asks_wording_absent():
    """The phase-diagram line summarizing Phase 1's routing must drop
    'surfaces + asks' for PASS_WITH_NOTES."""
    phase_diagram = _phase_diagram_slice(_text())
    assert OLD_PHASE_DIAGRAM_ASK not in phase_diagram, \
        f"Phase diagram must not contain the old wording {OLD_PHASE_DIAGRAM_ASK!r}"


def test_phase_diagram_states_auto_proceed():
    """The phase-diagram line must state PASS_WITH_NOTES auto-proceeds,
    matching Step 3's body."""
    phase_diagram = _phase_diagram_slice(_text())
    assert "auto-proceed" in phase_diagram.lower() or "auto proceed" in phase_diagram.lower(), \
        "Phase diagram must state PASS_WITH_NOTES auto-proceeds"


def test_step3_needs_revision_stop_unchanged():
    """Guard against over-deletion: NEEDS_REVISION's hard STOP wording
    must survive this edit untouched."""
    step3 = _step3_slice(_text())
    assert "NEEDS_REVISION" in step3, "Step 3 must still mention NEEDS_REVISION"
    assert "STOP" in step3, "Step 3 must still contain the NEEDS_REVISION STOP wording"
    assert "do NOT push" in step3, \
        "Step 3 must still state NEEDS_REVISION means do NOT push"


def test_step3_pass_all_green_still_silent():
    """Guard against over-deletion: PASS (all green) must remain a
    silent proceed, unaffected by this change."""
    step3 = _step3_slice(_text())
    assert "proceed silently" in step3, \
        "Step 3 must still state PASS (all green) proceeds silently"
