"""Prose-pin test for Task 4 (SDD gate ① once-clause + triage SSOT marker).

Pins the N6 once-clause appended to gate ①'s "Irreversible /
outward-facing / costly" row (the confirm is asked ONCE; merge /
deploy / delete / paid runs always confirm regardless) and the N7
cross-skill SSOT marker appended to the three-way triage bullet, in
`subagent-driven-development/SKILL.md` §Asking the user.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SDD_SKILL_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "subagent-driven-development"
    / "SKILL.md"
)

N6_LEAD = "The confirm is asked ONCE"
N6_CLOSING = "always confirm regardless"
N7_LEAD = "the cross-skill SSOT for ask-vs-resolve decisions"


def _normalized_text() -> str:
    """Whitespace-normalized SKILL.md text (collapses hard wraps so a
    contiguous-phrase match doesn't depend on line breaks)."""
    text = SDD_SKILL_MD.read_text(encoding="utf-8")
    return " ".join(text.split())


def test_gate_one_standing_authorization_row_present():
    """Positive-fact control: the pre-existing gate ① phrase is present
    — proves the pins below are not vacuous (the file is actually being
    read/matched, not a stub)."""
    assert "The standing authorization does **not** cover these" in _normalized_text()


def test_once_clause_lead_present():
    """Task 4: N6's lead — the confirm on the always-confirm row is
    asked ONCE (the kickoff request naming the endpoint IS the ask)."""
    assert N6_LEAD in _normalized_text()


def test_once_clause_always_confirm_regardless_present():
    """Task 4: N6's closing — merge, deploy, delete, and paid runs
    always confirm regardless of the once-clause."""
    normalized = _normalized_text()
    assert N6_CLOSING in normalized
    # The closing binds to the enumerated always-confirm actions, not a
    # free-floating fragment.
    assert (
        "`gh pr merge`, deploy, delete, and paid runs always confirm regardless"
        in normalized
    )


def test_triage_ssot_marker_present():
    """Task 4: N7's lead — the three-way triage bullet is marked the
    cross-skill SSOT for ask-vs-resolve decisions."""
    normalized = _normalized_text()
    assert N7_LEAD in normalized
    # Sibling skills point by heading text, never copy.
    assert "sibling skills point here by heading text, never copy it" in normalized
