"""
Structural tests for input-floor.md reference.

Tests verify:
- The two input slot names appear: current state, wanted difference
- The slot-to-field mapping uses the actual field names goal-shape.md
  defines (Outcome, Verification), read from that file rather than
  hardcoded twice
- The refusal rule: empty slot named, no goal emitted
- The three bar clauses: decidable, false when written, free of
  dependence on a person acting or answering — and the bar is
  explicitly NOT claimed to be mechanical
- The three provenance tags: user-said (quoted), derived (anchor),
  proposed (agent-supplied, unconfirmed)
- The citation boundary: a recorded purpose is a source to quote,
  never authority to settle a choice reserved for the user

WHY: This reference is the SSOT for what must hold before a goal may be
written and what must hold of the condition itself. Any drift in the slot
names, the refusal rule, the bar clauses, or the provenance tags silently
breaks every downstream skill section that assumes this contract. The
slot-to-field mapping is also a live seam onto goal-shape.md (Task 1): if
that file renames a field, this file's mapping text must be checked against
the renamed field, not a frozen copy of the old name.
"""

import re
from pathlib import Path

REFERENCES_DIR = Path(__file__).parent.parent / "references"
REFERENCE_PATH = REFERENCES_DIR / "input-floor.md"
SHAPE_REFERENCE_PATH = REFERENCES_DIR / "goal-shape.md"


def _read_reference() -> str:
    """Read the reference file; fail with a descriptive message if missing."""
    assert REFERENCE_PATH.exists(), (
        f"Reference file not found: {REFERENCE_PATH}\n"
        "This is expected at RED stage. Create the reference to make this test pass."
    )
    return REFERENCE_PATH.read_text(encoding="utf-8")


def _paragraphs_normalized(content: str) -> list:
    """Split into paragraphs and collapse internal whitespace/newlines.

    Markdown line-wrap can split a phrase across lines; matching against
    raw content makes a multi-word phrase assertion fragile to reflow.
    Normalizing whitespace per paragraph before matching avoids that trap.
    """
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", content)]


def _field_names_from_shape_reference() -> list:
    """Extract the field names goal-shape.md actually defines, in order.

    Headers look like: '## 1 — `Outcome`'. Pulling the names out of the
    file (instead of hardcoding "Outcome" / "Verification" as literals in
    this test) means a rename upstream fails this probe rather than
    drifting silently, per the cross-seam requirement.
    """
    assert SHAPE_REFERENCE_PATH.exists(), (
        f"Upstream reference not found: {SHAPE_REFERENCE_PATH}"
    )
    shape_content = SHAPE_REFERENCE_PATH.read_text(encoding="utf-8")
    names = re.findall(r"^## \d+ — `([\w-]+)`", shape_content, re.MULTILINE)
    assert len(names) >= 3, (
        f"Expected at least 3 field headers in {SHAPE_REFERENCE_PATH}, found {names}"
    )
    return names


def test_defines_slots_refusal_bar_and_provenance() -> None:
    content = _read_reference()
    paragraphs = _paragraphs_normalized(content)
    paragraphs_lower = [p.lower() for p in paragraphs]

    def _paragraph_containing(*keywords: str):
        for p in paragraphs_lower:
            if all(kw in p for kw in keywords):
                return p
        return None

    # --- two input slot names ---
    assert "current state" in content.lower(), "Must name the 'current state' slot."
    assert "wanted difference" in content.lower(), (
        "Must name the 'wanted difference' slot."
    )

    # --- refusal rule ---
    refusal_para = _paragraph_containing("empty", "names the empty slot") or (
        _paragraph_containing("empty slot", "emits no goal")
    )
    assert refusal_para, (
        "Must state the refusal rule: when either slot is empty, name the "
        "empty slot and emit no goal."
    )
    vague_para = _paragraph_containing("vague", "worse")
    assert vague_para, (
        "Must state that emitting a vague goal is worse than emitting none."
    )
    assert _paragraph_containing("vague", "satisfied"), (
        "Must state that a vague condition may be judged satisfied immediately."
    )

    # --- the bar: three clauses ---
    decidable_para = _paragraph_containing("decidable")
    assert decidable_para, "The bar must state the condition must be decidable."
    false_para = _paragraph_containing("false", "written")
    assert false_para, "The bar must state the condition must be false when written."
    person_para = _paragraph_containing("person", "acting")
    assert person_para and "answering" in person_para, (
        "The bar must state the condition must not depend on a person acting "
        "or answering."
    )

    # --- the bar is explicitly NOT claimed to be mechanical ---
    # Word-boundary + proximity check: "not" must appear close to
    # "mechanical" within the same paragraph, so a paragraph that merely
    # contains "mechanical" unqualified does not pass by accident.
    mechanical_para = _paragraph_containing("mechanical")
    assert mechanical_para, "The bar section must address whether it is mechanical."
    assert re.search(r"\bnot\b[^.]{0,60}\bmechanical\b", mechanical_para), (
        "The bar must be stated as prose judgment, explicitly NOT claimed to "
        "be mechanical — expected 'not ... mechanical' within one sentence."
    )

    # --- three provenance tags ---
    user_said_para = _paragraph_containing("user-said")
    assert user_said_para and "quoted" in user_said_para, (
        "Must define `user-said`: the user's own words, quoted."
    )
    derived_para = _paragraph_containing("derived")
    assert derived_para and "anchor" in derived_para, (
        "Must define `derived`: names the anchor it was inferred from."
    )
    proposed_para = _paragraph_containing("proposed")
    assert proposed_para and (
        "not" in proposed_para and "confirm" in proposed_para
    ), "Must define `proposed`: agent-supplied, user has not confirmed it."

    # --- citation boundary ---
    citation_para = _paragraph_containing("source", "quote")
    assert citation_para, (
        "Must state a recorded purpose is a source an agent quotes to "
        "justify an inference."
    )
    assert _paragraph_containing("never", "authority"), (
        "Must state a recorded purpose is never authority to settle a "
        "choice reserved for the user."
    )
    assert _paragraph_containing("irreversible") or _paragraph_containing(
        "outward-facing"
    ), (
        "The citation boundary must name at least one example of a choice "
        "reserved for the user, e.g. an irreversible or outward-facing action."
    )

    # --- negative guard: "required"/"require" collision with word 'bar' ---
    # (regression guard per known trap: a bare substring match on 'require'
    # would false-positive inside 'required'.) Nothing in this reference
    # should claim the bar is REQUIRED to be mechanical — that would
    # contradict the "not ... mechanical" assertion above.
    for p in paragraphs_lower:
        if "mechanical" in p and re.search(r"\brequires?\b", p):
            raise AssertionError(
                f"Must not claim the bar 'requires' mechanical checking: {p!r}"
            )


def test_slot_mapping_uses_the_shape_reference_field_names() -> None:
    """Cross-seam probe: the mapping must cite goal-shape.md's real names.

    This does not hardcode "Outcome" / "Verification" as the expectation —
    it pulls the field names goal-shape.md actually defines and asserts
    this file's slot-to-field mapping paragraph uses those exact names. If
    goal-shape.md is renamed upstream, this probe fails here instead of the
    mapping silently pointing at a field that no longer exists.
    """
    field_names = _field_names_from_shape_reference()

    outcome_name = next((n for n in field_names if n.lower() == "outcome"), None)
    verification_name = next(
        (n for n in field_names if n.lower() == "verification"), None
    )
    assert outcome_name and verification_name, (
        f"goal-shape.md must define both an 'Outcome' and a 'Verification' "
        f"field; found {field_names}"
    )

    content = _read_reference()
    paragraphs = _paragraphs_normalized(content)

    mapping_para = None
    for p in paragraphs:
        p_lower = p.lower()
        if "current state" in p_lower and verification_name.lower() in p_lower:
            mapping_para = p
            break
    assert mapping_para, (
        f"Expected a paragraph mapping 'current state' to the "
        f"'{verification_name}' field (as named in goal-shape.md)."
    )

    outcome_mapping_para = None
    for p in paragraphs:
        p_lower = p.lower()
        if "wanted difference" in p_lower and outcome_name.lower() in p_lower:
            outcome_mapping_para = p
            break
    assert outcome_mapping_para, (
        f"Expected a paragraph mapping 'wanted difference' to the "
        f"'{outcome_name}' field (as named in goal-shape.md)."
    )
