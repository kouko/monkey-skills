"""Structural grep-test guarding brainstorming's Axis 0 — the upstream-artifact
check that fronts the 5-axis framework (loom family connective-tissue plan,
Task E1).

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE + POSITION of a compact new subsection: "Axis 0 — Upstream artifacts
(family §Intake)" placed immediately BEFORE "Axis 1 — Problem". Axis 0 must:

1. Point at the loom family reception's on-ramp criteria table
   (`loom-pipeline/hooks/family-reception.md`) rather than copy it — SSOT
   drift prevention (plan-level note "Reception SSOT rule").
2. On a triggered row, surface the recommendation ONCE (naming the concrete
   design-side sequence), then record the user's choice in the brief under a
   `## Design-side on-ramp` line, and proceed either way — never re-raise
   after a decline.
3. Carry a negative-guard verbatim-equivalent: bug fix / refactor /
   test-covered increment → Axis 0 is skipped silently (no noise on
   incremental work).

These checks assert on load-bearing PHRASES (intent), tolerant of wording
variation, so the test guards meaning without being brittle.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "brainstorming" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


# --- presence + position -----------------------------------------------


def test_axis0_heading_present_before_axis1():
    """'Axis 0' heading must exist and appear strictly before the 'Axis 1'
    heading — Axis 0 fronts the framework, it does not append to it."""
    text = _text()
    axis0_match = re.search(r"^#+\s*Axis 0\b", text, re.MULTILINE)
    axis1_match = re.search(r"^#+\s*Axis 1\b", text, re.MULTILINE)
    assert axis0_match is not None, "Axis 0 heading missing"
    assert axis1_match is not None, "Axis 1 heading missing (sibling regression)"
    assert axis0_match.start() < axis1_match.start(), \
        "Axis 0 must be positioned before Axis 1"


# --- reception reference (point, don't copy) ----------------------------


def test_axis0_references_reception_criteria():
    """Axis 0 must name the loom family reception file / label as the
    criteria SSOT — never copy the on-ramp table body into this SKILL.md."""
    text = _text()
    assert "loom-pipeline/hooks/family-reception.md" in text or \
        "family-reception.md" in text, \
        "Axis 0 must name the reception file (point, don't copy)"
    low = text.lower()
    assert "loom family reception" in low or "family reception" in low, \
        "Axis 0 must reference 'the loom family reception' by name"


# --- recommend-once + record-choice --------------------------------------


def test_axis0_recommend_once_and_record_choice():
    """On a triggered row: surface the recommendation ONCE naming a concrete
    sequence, then record the user's choice in the brief, and never re-raise
    after a decline."""
    text = _text()
    low = text.lower()
    assert "recommend" in low, "Axis 0 must describe surfacing a recommendation"
    assert "once" in low, "Axis 0 must state the recommendation fires ONCE"
    assert "design-side on-ramp" in low, \
        "Axis 0 must name the brief line '## Design-side on-ramp'"
    assert "offered" in low and ("chose" in low or "choice" in low), \
        "Axis 0 must record the user's choice (offered — user chose <X>)"
    assert "never re-raise" in low or "not re-raise" in low \
        or "do not re-raise" in low or "never re-ask" in low, \
        "Axis 0 must forbid re-raising the recommendation after a decline"
    # the concrete sequence must be named, not left abstract
    assert "using-loom-product-principles" in text, \
        "Axis 0 must name a concrete station in the design-side sequence"


# --- negative guard -------------------------------------------------------


def test_axis0_negative_guard_silent_skip():
    """Bug fix / refactor / test-covered increment → Axis 0 is skipped
    silently — no noise on incremental work."""
    text = _text()
    low = text.lower()
    assert "bug fix" in low, "negative guard must name bug fix"
    assert "refactor" in low, "negative guard must name refactor"
    assert "test-covered increment" in low or "test covered increment" in low, \
        "negative guard must name test-covered increment"
    assert "silently" in low, \
        "negative guard must state the skip happens SILENTLY (no noise)"
