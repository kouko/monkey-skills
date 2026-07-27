"""Structural grep-test guarding the closed-list rewrite of
writing-plans/SKILL.md's §Amending a PASS plan (Task 4,
docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md).

writing-plans/SKILL.md is a prompt artifact, not executable code. Its
correctness here is the REPLACEMENT of the author-self-judged skip
note ("record a one-line skip note ... explaining why the amendment
is additive and schema-safe") with an enumerated CLOSED list of
amendment kinds that may skip re-review, so a weak-tier reader
classifies an amendment mechanically instead of exercising judgment
over an open-ended "additive and schema-safe" standard.

Per the plan's Kickoff decision for T4 (derived from the two
researched precedents already on record -- GitHub/OpenSSF's
mechanical stale-approval dismissal and the JA design-review norm of
fixed-in-advance 判定基準): an amendment may skip re-review only if it
changes no technical content -- stamping the verdict, fixing a typo,
filling a schema field. Anything touching Acceptance RED/GREEN, a
cited fact, a Dependencies edge, or a task's scope re-reviews.

These checks assert on load-bearing PHRASES (intent), tolerant of
wording variation, so the test guards meaning without being brittle.
The self-justification-phrase-removal check is scoped to
writing-plans/SKILL.md ONLY: five pre-existing historical plan
documents under docs/loom/plans/ (verified:
2026-07-18-memo-quarterly-kpi-wiring.md,
2026-07-18-loop-convergence-fixes.md,
2026-07-12-visual-anchor-realignment-tone-and-manner.md,
2026-07-13-us-sec-narrative-memo-wiring.md,
2026-07-17-loom-memory-hardening-o4-o2-o3-o5-o6.md) legitimately still
contain the phrase as a record of a past, already-applied skip
decision -- they are historical record, not the live contract text,
and rewriting them would falsify history. Only the live contract
(SKILL.md) must stop offering the open-ended phrasing going forward.

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "writing-plans" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _amending_a_pass_plan_section(text: str) -> str:
    low = text.lower()
    start = low.index("amending a pass plan")
    # Section runs to the next top-level heading ("## Kickoff briefing").
    end = low.index("## kickoff briefing", start)
    return text[start:end]


def test_skip_note_is_closed_list():
    """§Amending a PASS plan must enumerate the permitted amendment
    kinds as a closed list, state that anything outside the list
    re-reviews, define each enumerated kind inline (so a weak-tier
    reader can classify an amendment without judgment), and the old
    author-supplied self-justification phrasing ("additive and
    schema-safe") must be gone from this file."""
    text = _text()
    section = _amending_a_pass_plan_section(text)
    low = section.lower()

    # The old self-judged escape phrase must be gone from THIS file
    # (historical plan documents are explicitly out of scope -- see
    # module docstring).
    assert "additive and schema-safe" not in low, \
        "the author-self-judged 'additive and schema-safe' phrasing " \
        "must be removed from SKILL.md; a closed list replaces it"

    # Enumerated closed list: at least the three kinds pinned by the
    # plan's Kickoff decision -- stamping the verdict, fixing a typo,
    # filling a schema field.
    assert "stamping the verdict" in low or "stamp the verdict" in low, \
        "must enumerate 'stamping the verdict' as a permitted kind"
    assert "typo" in low, \
        "must enumerate 'fixing a typo' as a permitted kind"
    assert "schema field" in low, \
        "must enumerate 'filling a schema field' as a permitted kind"

    # Closed-list framing: anything not enumerated re-reviews.
    assert "re-review" in low, \
        "must state that amendments outside the list re-review"
    assert (
        "anything else" in low
        or "outside the list" in low
        or "not on the list" in low
        or "does not match" in low
        or "not clearly match" in low
    ), "must state the list is closed -- unmatched amendments re-review"

    # The four specific technical-content categories that always
    # re-review, per the plan's Kickoff decision.
    for must_reroute in (
        "acceptance",
        "cited fact",
        "dependencies",
        "scope",
    ):
        assert must_reroute in low, \
            f"must name {must_reroute!r} as a category that re-reviews"

    # Each enumerated kind carries an inline operational definition,
    # not just a bare label -- a weak-tier reader must be able to
    # classify an amendment without judgment. Heuristic: each kind's
    # label is followed reasonably closely by an explanatory clause
    # (an em/en dash or a parenthetical), not left as a bare list item.
    for label in ("stamping the verdict", "typo", "schema field"):
        idx = low.find(label)
        assert idx != -1, f"expected label {label!r} present (checked above)"
        nearby = low[idx: idx + 400]
        assert "—" in nearby or "--" in nearby or "(" in nearby, \
            f"{label!r} must carry an inline definition (dash or " \
            "parenthetical explanation), not a bare label"


def test_closed_list_is_exhaustive():
    """The enumerated closed list must contain EXACTLY the three
    permitted amendment kinds -- no additional item may sit beside
    them. The presence-only checks above (each label appears
    somewhere) cannot catch an ADDED fourth item; they only catch a
    MISSING one. Regression guard for the mutation that re-opened the
    open-ended self-judged escape this section was written to remove:
    appending "4. Any other minor, cosmetic change -- any edit the
    author judges to be non-substantive and safe." beside the three
    legitimate kinds. That mutant passed every assertion above
    unchanged.

    Structural, not textual: counts top-level Markdown ordered-list
    markers (`N. `) in the section rather than pinning the three
    items' wording byte-for-byte, so reformatting or rewording the
    existing three kinds does not make this brittle. Trade-off: this
    assumes the closed list stays rendered as a Markdown ordered list;
    if a future edit reflows it into prose or bullets without
    numbering, this check would need updating alongside that reflow --
    an acceptable coupling, since the section's own contract text
    calls it an enumerated list.
    """
    text = _text()
    section = _amending_a_pass_plan_section(text)
    items = re.findall(r"^\d+\.\s", section, flags=re.MULTILINE)
    assert len(items) == 3, (
        f"expected exactly 3 enumerated amendment kinds in the closed "
        f"list, found {len(items)} -- any item beyond the three pinned "
        "by the Kickoff decision (stamping the verdict / fixing a typo "
        "/ filling a schema field) re-opens the self-judged escape "
        "this section replaced"
    )
