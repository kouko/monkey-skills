"""Structural grep-test guarding the anchor-primary inversion of the
`### Stated facts` section in
`loom-code/skills/writing-plans/references/plan-format.md`.

The section's cited authority --
`subagent-driven-development/references/dispatch-hygiene-notes.md`
§Dispatch-packet context rule (a): "Anchor by string, never by line
number alone" -- already states the rule the section should align with.
Before this inversion the section prescribed the OPPOSITE ordering: it
made `file:line` the citation and the verbatim string / stable heading
an added "pairing duty". This test pins the inverted ordering so a
later edit that reverts to line-first is caught.

plan-format.md is a prompt/contract artifact, not executable code; its
correctness condition is the PRESENCE of the load-bearing phrases that
make the rule executable by the reader (same convention as
`test_plan_fact_grounding.py`). Assertions target intent-bearing
phrases, tolerant of surrounding wording, so the guard survives a
rephrase and fails a removal.

Stdlib only (pathlib). plan-format.md is resolved relative to this
test file.
"""

import re
from pathlib import Path

PLAN_FORMAT = (
    Path(__file__).parents[1]
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-format.md"
)


def _text() -> str:
    assert PLAN_FORMAT.is_file(), f"plan-format.md is absent at {PLAN_FORMAT}"
    return PLAN_FORMAT.read_text(encoding="utf-8")


def _stated_facts_section(text: str) -> str:
    """Isolate the `### Stated facts` section.

    Scoping to the section means the conjunct assertions below can only
    be satisfied by the Stated-facts rule itself -- an incidental mention
    of "anchor" or "line number" elsewhere in the schema cannot keep
    this test green. The section runs from its heading to the next
    heading of the same or shallower depth.
    """
    lines = text.splitlines(keepends=True)
    start = None
    depth = 0
    for i, line in enumerate(lines):
        if line.startswith("#") and "stated facts" in line.lower():
            start = i
            depth = len(line) - len(line.lstrip("#"))
            break
    assert start is not None, (
        "plan-format.md carries no '### Stated facts' heading -- the "
        "pointer-not-copy rule must be a findable section a plan author "
        "and the plan-document-reviewer can be pointed at"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if line.startswith("#") and len(line) - len(line.lstrip("#")) <= depth:
            end = j
            break
    return "".join(lines[start:end])


def test_stated_facts_is_anchor_primary():
    """The Stated-facts section cites the ANCHOR as the citation, with a
    line number as optional precision -- not the line-first `file:line`
    prescription the section carried before the inversion."""
    section = _stated_facts_section(_text())
    low = section.lower()

    # PRESENCE: anchor-primary wording
    assert "verbatim string" in low and "stable heading" in low, (
        "must name the anchor forms -- 'verbatim string' and 'stable "
        "heading' -- as the citation a verifiable technical assertion "
        "carries"
    )
    assert "anchor" in low, (
        "must use the term 'anchor' for the verbatim-string / "
        "stable-heading citation form"
    )
    assert "line number is optional" in low or (
        "optional precision" in low and "line number" in low
    ), (
        "must state that a line number is OPTIONAL precision, not the "
        "citation itself -- the pairing duty inverts: the anchor IS the "
        "citation, the line is the add-on"
    )
    assert "ambiguous" in low, (
        "must state WHEN the optional line number becomes required -- "
        "when the anchor alone is ambiguous (the string occurs more "
        "than once in the file); without this the optionality is "
        "unbounded and the anchor can be silently dropped"
    )

    # ABSENCE: the retired line-first prescription
    assert "narrowest form" not in low, (
        "the line-first prescription 'Cite the narrowest form that "
        "resolves' is retired -- it made `file:line` the citation and "
        "the anchor an added pairing duty, the opposite of the "
        "anchor-primary rule this section now states"
    )


def test_stated_facts_selects_anchors_by_artifact_type():
    """The Stated-facts rule gives plan authors concrete anchors for
    prose, code, and config/data artifacts rather than treating every
    source as an interchangeable string search."""
    section = _stated_facts_section(_text()).lower()
    category_clauses = {
        "prose": (
            r"\bprose\s+uses\s+a\s+stable\s+heading\s+or\s+"
            r"distinctive\s+phrase\b"
        ),
        "code": (
            r"\bcode\s+uses\s+a\s+function,\s+class,\s+or\s+method\s+"
            r"signature,\s+a\s+constant,\s+or\s+a\s+distinctive\s+message\b"
        ),
        "config/data": (
            r"\bconfig/data\s+uses\s+a\s+key\s+path\s+plus\s+a\s+"
            r"distinctive\s+value\s+fragment\b"
        ),
    }

    for artifact_type, clause in category_clauses.items():
        assert re.search(clause, section), (
            f"must keep the complete {artifact_type}-to-anchor clause; "
            "independent tokens can conceal a wrong category pairing"
        )
