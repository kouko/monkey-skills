"""Pin: copywriting-intake's Q8 grill BLOCKED halt must be a verifiable
mechanical condition (named still-empty required fields), not a judgment
call ("user cannot decide").

WHY: docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md —
weak executors preserve vocabulary but drop prose-only enforcement duties.
A halt condition gated on "cannot decide" asks a weak executor to render a
judgment; a halt condition gated on "these named fields are still empty"
is checkable by any reader (human or agent) against the recorded fields.

Window-scoped per docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md:
whole-file substring checks on generic terms ("required", "still-empty")
would false-green if those words happen to appear in an unrelated bullet
elsewhere in this SKILL.md. Anchored to the Q8 grill step-4 clause via the
unique phrase "one probe round" (present in both the old judgment-shaped
wording and the new verifiable wording), windowed to the paragraph that
follows it (bounded by the next blank line).
"""

import re
from pathlib import Path

SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "copywriting-intake"
    / "SKILL.md"
)

ANCHOR = "one probe round"


def _text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _step4_window(text: str) -> str:
    """Return the Q8 grill step-4 clause: from ANCHOR to the next blank
    line (paragraph boundary). Asserts ANCHOR is unique first — a
    non-unique anchor would make the window ambiguous."""
    occurrences = [m.start() for m in re.finditer(re.escape(ANCHOR), text)]
    assert len(occurrences) == 1, (
        f"anchor {ANCHOR!r} must be unique in SKILL.md, found "
        f"{len(occurrences)} occurrences"
    )
    start = occurrences[0]
    end = text.index("\n\n", start)
    return text[start:end]


def test_step4_anchor_is_unique():
    text = _text()
    occurrences = [m.start() for m in re.finditer(re.escape(ANCHOR), text)]
    assert len(occurrences) == 1


def test_blocked_clause_names_still_empty_required_fields():
    """The BLOCKED clause must direct the agent to emit the concrete list
    of still-empty Level 1 required fields — the observable state a
    reader can check the halt against. Scoped to the step-4 window so
    this cannot pass via an unrelated 'required' elsewhere in the file."""
    window = _step4_window(_text())
    assert "still-empty" in window, (
        "expected the Q8 grill BLOCKED clause (step-4 window) to name "
        "the still-empty field(s) driving the halt"
    )
    assert "required" in window, (
        "expected the Q8 grill BLOCKED clause (step-4 window) to name "
        "the required field(s) driving the halt"
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
