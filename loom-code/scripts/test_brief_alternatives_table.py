"""Structural grep test guarding the `## Alternatives Considered`
fill-or-declare rewrite in `brainstorming/references/handoff-brief-format.md`
and the matching `brainstorming/SKILL.md` sentence (Task 2 of
`docs/loom/plans/2026-08-17-artifact-table-routing.md`).

Both files are prompt/contract artifacts, not executable code: nothing
importable observes whether a brief author actually discovers the
fill-or-declare contract for `## Alternatives Considered`. These files ARE
the schema doc / router doc the author reads, so their correctness
condition is the PRESENCE of the pinned phrases (Pin B / Pin B-2,
transcribed verbatim from the plan) and the ABSENCE of the old
numbered-list format sentence.

Stdlib + pytest only (pathlib).
"""
from __future__ import annotations

from pathlib import Path

HANDOFF_BRIEF_FORMAT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "brainstorming"
    / "references"
    / "handoff-brief-format.md"
)

SKILL_MD = (
    Path(__file__).parents[1] / "skills" / "brainstorming" / "SKILL.md"
)

# Pin B's line-prefix (transcribe VERBATIM from the plan's §Pinned wording).
PIN_B_NA_PREFIX = "N/A — no alternatives found:"

# Pin B / Pin B-2's shared column-list phrase: appears once in the spec
# entry's transcribed Pin B block, and once as the template table's header
# row (Pin B-2).
PIN_B_COLUMNS_PHRASE = "Alternative | Who ships it / source | Why rejected"

# The old escape/format sentence this task must remove.
OLD_FORMAT_SENTENCE = (
    "Format: numbered list, each with a one-sentence rejection rationale."
)

# The plan's exact SKILL.md replacement phrase.
SKILL_MD_FILL_OR_DECLARE_PHRASE = (
    "`## Alternatives Considered` (Axis 4) and `## Diagrams` are "
    "fill-or-declare"
)


def _handoff_text() -> str:
    assert HANDOFF_BRIEF_FORMAT_MD.is_file(), (
        f"handoff-brief-format.md is absent at {HANDOFF_BRIEF_FORMAT_MD}"
    )
    return HANDOFF_BRIEF_FORMAT_MD.read_text(encoding="utf-8")


def _skill_text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def test_alternatives_considered_is_fill_or_declare_table() -> None:
    text = _handoff_text()

    # Pin B's N/A line-prefix occurs exactly once: embedded in the spec
    # entry's transcribed Pin B block.
    assert text.count(PIN_B_NA_PREFIX) == 1, (
        f"Pin B's full line-prefix {PIN_B_NA_PREFIX!r} must appear exactly "
        "once in handoff-brief-format.md's `## Alternatives Considered` "
        "fill-or-declare wording"
    )

    # The column-list phrase occurs exactly twice: once in the spec entry's
    # Pin B prose, once as the template table's header row (Pin B-2).
    assert text.count(PIN_B_COLUMNS_PHRASE) == 2, (
        f"the column-list phrase {PIN_B_COLUMNS_PHRASE!r} must appear "
        "exactly twice in handoff-brief-format.md -- once in the spec "
        "entry, once as the template table's header row"
    )

    # The old numbered-list format sentence must be fully gone.
    assert OLD_FORMAT_SENTENCE not in text, (
        f"the old format sentence {OLD_FORMAT_SENTENCE!r} must be removed "
        "from handoff-brief-format.md -- `## Alternatives Considered` is "
        "fill-or-declare, not a numbered list"
    )


def test_skill_md_names_alternatives_fill_or_declare() -> None:
    text = _skill_text()

    assert text.count(SKILL_MD_FILL_OR_DECLARE_PHRASE) == 1, (
        f"the phrase {SKILL_MD_FILL_OR_DECLARE_PHRASE!r} must appear "
        "exactly once in brainstorming/SKILL.md"
    )
