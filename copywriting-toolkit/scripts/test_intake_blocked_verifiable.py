"""Pin: copywriting-intake's Q8 grill BLOCKED halt must be a verifiable
mechanical condition (named still-empty required fields), not a judgment
call ("user cannot decide").

WHY: docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md —
weak executors preserve vocabulary but drop prose-only enforcement duties.
A halt condition gated on "cannot decide" asks a weak executor to render a
judgment; a halt condition gated on "these named fields are still empty"
is checkable by any reader (human or agent) against the recorded fields.
"""

from pathlib import Path

SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "copywriting-intake"
    / "SKILL.md"
)


def _text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def test_blocked_clause_names_still_empty_required_fields():
    """The BLOCKED clause must direct the agent to emit the concrete list
    of still-empty Level 1 required fields — the observable state a
    reader can check the halt against."""
    text = _text()
    assert "still-empty" in text and "required" in text, (
        "expected the Q8 grill BLOCKED clause to name the still-empty "
        "required field(s) driving the halt"
    )


def test_old_judgment_only_wording_removed():
    """Absence pin: the old judgment-shaped phrasing ('user cannot
    decide') must be gone — it asked the executor to render a judgment
    instead of checking an observable condition."""
    text = _text()
    assert "user cannot decide" not in text, (
        "old judgment-shaped BLOCKED condition ('user cannot decide') "
        "must be replaced by a verifiable named-empty-fields condition"
    )
