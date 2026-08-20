"""Structural grep-test guarding `handoff-brief-format.md`'s new
`## Queue relation` closed grammar (direction-queue-gate plan, Task 2 /
BI-2).

The reference is prose, not executable code. Its correctness is the
PRESENCE of a `## Queue relation` section naming all three canonical
forms verbatim, plus the unresolved-wording rule, inside that
section's own body (not merely somewhere in the file).

Stdlib only (pathlib + re). Resolve the reference relative to this
test file.
"""

import re
from pathlib import Path

REFERENCE = (
    Path(__file__).parent
    / ".."
    / "skills"
    / "brainstorming"
    / "references"
    / "handoff-brief-format.md"
).resolve()

CANONICAL_FORMS = [
    "in-queue:",
    "unqueued —",
    "displaces:",
]


def _text() -> str:
    assert REFERENCE.is_file(), f"handoff-brief-format.md is absent at {REFERENCE}"
    return REFERENCE.read_text(encoding="utf-8")


def _section(text: str, heading_pattern: str) -> str:
    """Return the body of the first `##`-level section whose heading matches
    heading_pattern, up to (not including) the next `##`-level heading."""
    match = re.search(rf"^##\s+{heading_pattern}\s*$", text, re.MULTILINE)
    assert match is not None, f"heading matching {heading_pattern!r} not found"
    rest = text[match.end():]
    next_heading = re.search(r"^##\s+\S", rest, re.MULTILINE)
    return rest[: next_heading.start()] if next_heading else rest


def test_handoff_format_states_three_canonical_queue_forms():
    text = _text()

    required_sections = _section(text, r"Required sections")

    heading_match = re.search(
        r"^###\s+`## Queue relation`\s*$", required_sections, re.MULTILINE
    )
    assert heading_match is not None, (
        "Required sections must declare a '### `## Queue relation`' subsection"
    )
    rest = required_sections[heading_match.end():]
    next_subsection = re.search(r"^###\s+\S", rest, re.MULTILINE)
    body = rest[: next_subsection.start()] if next_subsection else rest

    for form in CANONICAL_FORMS:
        assert form in body, (
            f"'## Queue relation' section missing canonical form {form!r}"
        )

    assert "unresolved" in body, (
        "'## Queue relation' section must state the unresolved-wording rule"
    )
    assert re.search(r"never treated as a pass", body), (
        "'## Queue relation' section must state that other wording is "
        "never treated as a pass"
    )
    assert re.search(r"pending", body), (
        "'## Queue relation' section must mention `pending` as the "
        "agent's placeholder"
    )
    assert re.search(r"never.*agent'?s own default|never the agent'?s own default", body), (
        "'## Queue relation' section must state that `pending` is never "
        "the agent's own default"
    )


def _overview_paragraph(text: str) -> str:
    """Return the `## Required sections` overview paragraph — the body
    before its first `###` subsection heading."""
    required_sections = _section(text, r"Required sections")
    first_subsection = re.search(r"^###\s+\S", required_sections, re.MULTILINE)
    return (
        required_sections[: first_subsection.start()]
        if first_subsection
        else required_sections
    )


def test_required_sections_overview_names_queue_relation_as_required():
    text = _text()
    overview = _overview_paragraph(text)

    assert "## Queue relation" in overview, (
        "'## Required sections' overview paragraph must name "
        "'## Queue relation' by name, the same way it names "
        "'## Design-side on-ramp'"
    )

    mention_index = overview.index("## Queue relation")
    clause = overview[max(0, mention_index - 20) : mention_index + 80]
    assert "always present" in clause, (
        "'## Queue relation' mention in the overview paragraph must state "
        "it is always present (required), matching the on-ramp line's shape"
    )
    assert "optional" not in clause, (
        "'## Queue relation' mention in the overview paragraph must not be "
        "phrased as optional — the subsection itself says it is required "
        "in every brief"
    )

    for form in CANONICAL_FORMS:
        assert form not in overview, (
            f"overview paragraph must not restate canonical form {form!r} — "
            "the enumeration names sections, the subsection owns the grammar"
        )


def _queue_relation_subsection(text: str) -> str:
    """Body of the `### `## Queue relation`` subsection inside
    `## Required sections` — the same body `_body_after_forms`
    scopes its assertions to."""
    required_sections = _section(text, r"Required sections")
    heading_match = re.search(
        r"^###\s+`## Queue relation`\s*$", required_sections, re.MULTILINE
    )
    assert heading_match is not None, (
        "Required sections must declare a '### `## Queue relation`' subsection"
    )
    rest = required_sections[heading_match.end():]
    next_subsection = re.search(r"^###\s+\S", rest, re.MULTILINE)
    return rest[: next_subsection.start()] if next_subsection else rest


def test_queue_relation_states_name_must_exist_in_now():
    """A well-formed `in-queue:`/`displaces:` line naming an entry
    absent from DIRECTION.md's `## Now` is exactly what
    `check_direction_freshness.py`'s `resolve_queue_relation` rejects
    (loom-code/scripts/check_direction_freshness.py). The SSOT must
    say so in its own voice — not merely contain the word 'exist',
    which a reversed sentence ('need not exist') would also contain.
    Anchor on the specific claim 'must ... exist', not the bare token,
    so a deletion AND a reversal both fail this test."""
    text = _text()
    body = _queue_relation_subsection(text)

    assert re.search(r"must (also )?exist", body), (
        "'## Queue relation' section must state that a name cited by "
        "in-queue:/displaces: must exist as a '## Now' entry — a "
        "well-formed line naming an absent entry is still unresolved"
    )
    assert "need not exist" not in body and "does not need to exist" not in body, (
        "'## Queue relation' section must not state the reversed claim "
        "(a cited name need not exist in '## Now')"
    )


def test_queue_relation_states_empty_now_guidance():
    text = _text()
    body = _queue_relation_subsection(text)

    assert re.search(r"## Now.{0,40}(is )?empty", body) or re.search(
        r"empty.{0,40}## Now", body
    ), (
        "'## Queue relation' section must state what an author does "
        "when '## Now' is empty (in-queue:/displaces: can never "
        "resolve until an entry exists)"
    )
    assert "unqueued" in body, (
        "the empty-'## Now' guidance must point the author at "
        "'unqueued — <reason>' as the usable form"
    )
