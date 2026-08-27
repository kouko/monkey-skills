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

Every polarity-bearing assertion below binds its negation (or its positive
obligation) to the object it governs WITHIN a structurally isolated scope —
one numbered list item, or one sentence — rather than trusting a bare
character-distance bound. A character cap on top of that scoping buys
nothing (the scope already prevents cross-item/cross-sentence bleeding) and
only risks a false failure on a legitimate rewording that happens to be a
few characters longer. Scope to structure, not to distance.
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


def _sentences(text: str) -> list:
    """Split normalized text into sentences on '. ' boundaries.

    Used to bind a polarity check to the ONE sentence that carries the
    claim, inside a paragraph that holds several sentences (e.g. §6's
    citation-boundary paragraph packs the 'never ... authority' claim and
    the separate 'cannot ... substitute' claim into different sentences of
    the same paragraph). Sentence-level scoping is structural — it needs no
    character-distance guess — so it replaces the character caps that used
    to do this job less precisely.
    """
    return [s.strip() for s in re.split(r"(?<=\.)\s+", text) if s.strip()]


def _numbered_list_items(content: str) -> list:
    """Split a top-level markdown numbered list into per-item strings.

    List items with no blank line between them (as in this file's §4)
    collapse into ONE paragraph under blank-line splitting — which lets a
    negation written in item 2 be satisfied by a keyword bleeding in from
    item 1 or item 3. Splitting at each `N. ` line start instead keeps each
    item's polarity bound to its own clause.

    Each chunk is also cut at the next markdown heading (a line starting
    with `#`). Without this, the LAST item in the list (item 3 here) has no
    following `N. ` boundary to stop it, so it silently absorbs every
    section after the list — §5 and §6 — into its own text. That bled-in
    text then lets an item-3 assertion accidentally match on words that
    live in §5/§6, not in item 3 itself, defeating the isolation this
    function exists to provide.

    Known, deliberately-left-open gap: a running-prose line that happens to
    start with `N. ` (e.g. a sentence beginning "3. is the answer...")
    would be misparsed as a list-item boundary by the lookahead regex
    below. No such line exists in the current reference — every `N. ` line
    start in this file is a genuine list item — so this is not fixed here;
    a general prose-vs-list-item detector is more machinery than the
    current, controlled file warrants. If a future edit to input-floor.md
    ever puts a numeral-dot at the start of a running-prose line, this
    function would need to be revisited.
    """
    chunks = re.split(r"\n(?=\d+\.\s)", content)
    items = []
    for chunk in chunks:
        if not re.match(r"^\d+\.\s", chunk.strip()):
            continue
        chunk = re.split(r"\n#", chunk)[0]
        items.append(re.sub(r"\s+", " ", chunk).strip())
    return items


def _bar_intro(content: str) -> str:
    """The prose intro of §4 'The bar', excluding its three list items.

    §4 has no blank line between its intro and item 1 (see
    _numbered_list_items' docstring), so paragraph-level splitting merges
    the intro with all three items into one block. The "not ... mechanical"
    claim belongs to the intro only; isolating it structurally — from the
    heading to the first list item — keeps a mutant that flips the intro's
    polarity from accidentally being rescued by unrelated item text bled
    into the same paragraph.
    """
    match = re.search(r"## 4 — The bar\n\n(.*?)\n1\.\s", content, re.DOTALL)
    assert match, "Expected the §4 'The bar' heading followed by a prose intro."
    return re.sub(r"\s+", " ", match.group(1)).strip()


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
    # This paragraph is a single sentence (verified by inspection of
    # input-floor.md §3), so no separate sentence split is needed — the
    # paragraph boundary already is the sentence boundary. Bind "no" to
    # "goal" within the "emit(s)" clause, unbounded by character count: a
    # mutant that keeps naming the empty slot but swaps the consequence to
    # emitting a degraded goal (instead of none) still fails, while a
    # legitimate rewording that inserts a longer clause between the words
    # (e.g. "emits, given the missing input evidence, no goal") still
    # passes, because the scope is the whole (single) sentence, not a
    # character count.
    assert re.search(r"\bemits?\b.*\bno\b.*\bgoal\b", refusal_para), (
        "The refusal rule must state the consequence as emitting NO goal "
        "(not a degraded/vague one) — expected 'emit(s) ... no ... goal' "
        "within one sentence."
    )
    vague_para = _paragraph_containing("vague", "worse")
    assert vague_para, (
        "Must state that emitting a vague goal is worse than emitting none."
    )
    satisfied_sentence = next(
        (s for s in _sentences(vague_para) if "vague" in s and "satisfied" in s),
        None,
    )
    assert satisfied_sentence, (
        "Must state that a vague condition may be judged satisfied immediately."
    )
    # Positive-obligation check: "may" must bind, in order, to "judged" and
    # "satisfied" within that one sentence. A mutant that inverts this to
    # "a vague condition is never judged satisfied" would still contain
    # both "vague" and "satisfied" and would false-pass the bare
    # containment check above; requiring "may ... judged ... satisfied" in
    # order catches that inversion, since "never" breaks the order-bound
    # "may" requirement.
    assert re.search(r"\bmay\b.*\bjudged\b.*\bsatisfied\b", satisfied_sentence), (
        "The claim that a vague condition may be judged satisfied must use "
        "'may' (permission), not a negated form — expected "
        "'may ... judged ... satisfied' within one sentence."
    )

    # --- the bar: three clauses, each isolated to its own list item ---
    list_items = _numbered_list_items(content)

    decidable_item = next(
        (item for item in list_items if "decidable" in item.lower()), None
    )
    assert decidable_item, "The bar must state the condition must be decidable."
    decidable_item_lower = decidable_item.lower()
    # Positive-obligation check: "must" bound to "checkable", scoped to
    # item 1 only. A mutant reading "the condition need not be checkable
    # true or false against evidence; opinion is fine too" keeps the word
    # "decidable" (in the item's bold heading) but drops the "must ...
    # checkable" obligation entirely — it fails here.
    assert re.search(r"\bmust\s+be\s+checkable\b", decidable_item_lower), (
        "The 'Decidable' item must state the condition MUST be checkable "
        "true or false — expected 'must be checkable' within item 1."
    )
    # Consequence check: an undecidable condition must FAIL this bar, not
    # clear it. A mutant reading "...an undecidable condition still clears
    # this bar" keeps "decidable"/"checkable"-adjacent vocabulary but
    # inverts the consequence — it fails here because "fails" is absent.
    assert re.search(r"\bfails\b.*\bbar\b", decidable_item_lower), (
        "The 'Decidable' item must state that an undecidable condition "
        "FAILS this bar — expected 'fails ... bar' within item 1."
    )

    false_item = next(
        (
            item
            for item in list_items
            if "false" in item.lower() and "written" in item.lower()
        ),
        None,
    )
    assert false_item, "The bar's 'False when written' item must be a list item."
    # Item-scoped negation check: bind "not" to "true" within item 2 only,
    # unbounded by character count now that the item boundary already does
    # the isolation §4's three items carry no blank line between them, so
    # a paragraph-level match would let "not" from item 1 or item 3 satisfy
    # this clause even if item 2 itself were inverted to "may already be
    # true; that is fine."
    assert re.search(r"\bnot\b.*\btrue\b", false_item.lower()), (
        "The 'false when written' clause must state the condition must NOT "
        "already be true at the moment it is written — expected "
        "'not ... true' within its own list item."
    )

    person_item = next(
        (
            item
            for item in list_items
            if "person" in item.lower() and "acting" in item.lower()
        ),
        None,
    )
    assert person_item and "answering" in person_item.lower(), (
        "The bar must state the condition must not depend on a person "
        "acting or answering."
    )
    # Item-scoped negation check: bind "not" to "depend" within item 3
    # only. A mutant reading "the condition may depend on a person acting
    # or answering; that is acceptable" keeps every asserted keyword
    # (person, acting, answering) but drops the "must not depend"
    # obligation — it fails here because no negation binds to "depend".
    assert re.search(r"\bnot\b.*\bdepend\b", person_item.lower()), (
        "The 'Free of dependence on a person' clause must state the "
        "condition must NOT depend on a person — expected "
        "'not ... depend' within its own list item."
    )

    # --- the bar is explicitly NOT claimed to be mechanical ---
    # Structurally isolated to §4's prose intro (heading -> first list
    # item), not the merged intro+items paragraph, so a mutant that
    # flips the intro's polarity cannot be rescued by unrelated item text
    # bled into the same paragraph. Word-boundary + proximity check: "not"
    # must appear before "mechanical" within that intro, unbounded by
    # character count now that the intro is already isolated.
    bar_intro = _bar_intro(content)
    assert "mechanical" in bar_intro.lower(), (
        "The bar section must address whether it is mechanical."
    )
    assert re.search(r"\bnot\b.*\bmechanical\b", bar_intro.lower()), (
        "The bar must be stated as prose judgment, explicitly NOT claimed to "
        "be mechanical — expected 'not ... mechanical' within the intro."
    )

    # --- three provenance tags ---
    user_said_para = _paragraph_containing("user-said")
    assert user_said_para and "quoted" in user_said_para, (
        "Must define `user-said`: the user's own words, quoted."
    )
    # Phrase check (not a bare co-occurrence): "quoted directly" must
    # appear as a contiguous phrase. A mutant reading "...the user's own
    # words, though never literally quoted" keeps "user-said" and "quoted"
    # present but inverts the claim; it fails here because that exact
    # phrase is gone.
    assert "quoted directly" in user_said_para, (
        "The `user-said` tag must state the content is quoted DIRECTLY — "
        "expected the phrase 'quoted directly'."
    )
    derived_para = _paragraph_containing("derived")
    assert derived_para and "anchor" in derived_para, (
        "Must define `derived`: names the anchor it was inferred from."
    )
    # Phrase check: "names the anchor" must appear contiguously. A mutant
    # reading "...the tag does not name the anchor" keeps "anchor" present
    # but inverts the claim; it fails here because that exact phrase is
    # gone.
    assert "names the anchor" in derived_para, (
        "The `derived` tag must state the tag NAMES the anchor — expected "
        "the phrase 'names the anchor'."
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
    never_authority_para = _paragraph_containing("never", "authority")
    assert never_authority_para, (
        "Must state a recorded purpose is never authority to settle a "
        "choice reserved for the user."
    )
    # §6 is one paragraph holding three sentences: the "never ... authority"
    # claim and the "cannot ... substitute" claim are DIFFERENT sentences of
    # that paragraph. Splitting to sentences (structural) rather than
    # bounding by character count keeps each negation bound to its own
    # clause without an arbitrary distance guess.
    citation_sentences = _sentences(never_authority_para)
    authority_sentence = next(
        (s for s in citation_sentences if "never" in s and "authority" in s), None
    )
    assert authority_sentence, (
        "'never' and 'authority' must appear together within one sentence."
    )
    assert re.search(r"\bnever\b.*\bauthority\b", authority_sentence), (
        "'never' must be bound to 'authority' within one sentence — expected "
        "'never ... authority', not the two words merely co-occurring."
    )
    substitute_sentence = next(
        (s for s in citation_sentences if "substitute" in s), None
    )
    assert substitute_sentence, (
        "Must also state a purpose cannot substitute for the user's own "
        "decision, in its own sentence."
    )
    assert re.search(
        r"\b(never|cannot|can't|not)\b.*\bsubstitute\b", substitute_sentence
    ), (
        "Must also state a purpose cannot substitute for the user's own "
        "decision — expected a negation bound to 'substitute' within one "
        "sentence."
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
