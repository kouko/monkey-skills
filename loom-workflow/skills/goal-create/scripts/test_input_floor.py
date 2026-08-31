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

import ast
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


def _bullet_list_items(content: str) -> list:
    """Split a top-level markdown `- ` bullet list into per-item strings.

    §5's three provenance-tag bullets carry no blank line between them, so
    paragraph-level splitting merges all three into ONE block — the same
    shape that motivated `_numbered_list_items()` for §4. That merge let a
    mutant that inverted ONE bullet (e.g. `proposed`) keep passing, because
    the OTHER two bullets' unmutated text ("quoted directly", "not ...
    confirmed", "names the anchor") were still present somewhere in the
    same merged paragraph and satisfied a bare containment/co-occurrence
    check meant for the mutated bullet. Splitting at each `- ` line start,
    the way `_numbered_list_items` splits at each `N. ` line start, binds
    each bullet's polarity to its own clause only.

    Each chunk is also cut at the next markdown heading, for the same
    reason `_numbered_list_items` does: without it, the LAST bullet in the
    list has no following `- ` boundary to stop it and silently absorbs
    every section after the list.
    """
    chunks = re.split(r"\n(?=-\s)", content)
    items = []
    for chunk in chunks:
        if not re.match(r"^-\s", chunk.strip()):
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


def _negation_binds(text: str, negation: str, target: str, max_gap_words: int = 4) -> bool:
    """The sanctioned bound form of a negation-to-target polarity check.

    True iff a `negation` token (a regex alternation fragment, e.g.
    ``"not"`` or ``"never|cannot|can't|not"``) sits within
    `max_gap_words` words directly BEFORE `target`, word-boundary safe
    on both ends. This replaces a bare ``<negation>.*<target>`` regex,
    which a bare, unbounded ``.*`` lets pass on mere co-occurrence
    anywhere in `text` — including an inversion where the negation's
    real clause has nothing to do with `target`, and an unrelated
    occurrence of `target` merely appears somewhere later (or the
    negation appears somewhere earlier, unrelated to the actual
    obligation). Capping the gap keeps the match local to the clause
    the negation actually governs, which a bare ``.*`` does not.
    """
    pattern = (
        r"\b(?:" + negation + r")\b"
        r"\W*"  # trailing markdown/punctuation glued to the negation word
        r"(?:\s+\S+){0," + str(max_gap_words) + r"}"
        r"\s+\b" + target + r"\b"
    )
    return re.search(pattern, text) is not None


def test_no_unbound_negation_regex_in_this_file() -> None:
    """Guard against the negation-inversion trap this file has hit
    repeatedly: a bare ``<negation-token>.*<target-word>`` regex passed
    directly to `re.search`/`re.match`, which a bare unbounded ``.*``
    satisfies on mere co-occurrence rather than true binding — even a
    fresh assertion written by the previous round's own fix for this
    exact defect class had this shape. `_negation_binds()` above is the
    sanctioned bound replacement. This guard reads THIS FILE'S OWN
    SOURCE and fails the moment the unbound shape is written again, in
    any assertion, including one nobody has written yet.

    What this guard catches: a regex string literal passed directly as
    the first argument to `re.search(...)` or `re.match(...)`,
    anywhere in this file's source, that contains a whole-word negation
    token ('not' / 'never' / 'no' / 'cannot' / "can't") followed later
    in that SAME literal by a bare, unbounded `.*` — the exact shape
    every prior instance of this defect had, whether the negation sits
    directly against a `\\b...\\b` or inside an alternation group like
    `(never|cannot|can't|not)`.

    What this guard CANNOT catch: (a) an unbound negation-to-target
    check built by string concatenation, an f-string, or `.format()`
    instead of a single literal passed straight to `re.search` — a
    determined rewrite could assemble the same unbound pattern
    dynamically and dodge this scan; (b) a negation word outside this
    guard's fixed vocabulary (e.g. 'nor', 'without', 'lacks', 'fails to');
    (c) the same unbound shape reached through a helper function other
    than `_negation_binds` that this guard has never heard of — it only
    inspects `re.search`/`re.match` call sites, not arbitrary helper
    internals; (d) a bounded-looking gap (e.g. `{0,50}`) that is bound
    in form but effectively unbound in practice — this guard checks for
    literal `.*`, not for a suspiciously large finite cap. It is a
    source-pattern check on THIS file only; it proves nothing about any
    other file.
    """
    source = Path(__file__).read_text(encoding="utf-8")

    call_pattern = re.compile(
        r"""re\.(?:search|match)\(\s*r(['"])(?P<pat>.*?)\1""", re.DOTALL
    )
    negation_word = re.compile(r"\b(?:not|never|no|cannot|can't)\b")
    dotstar = re.compile(r"\.\*")

    def _is_unbound_negation(pat: str) -> bool:
        # A pattern literal's own `\b` word-boundary escapes are TWO
        # characters at the source level — backslash then the letter
        # 'b' — and that trailing 'b' sits glued directly against the
        # word it delimits (e.g. `\bnot\b` is the literal characters
        # `\`, `b`, `n`, `o`, `t`, `\`, `b`). Read as plain text, 'b'
        # and 'n' are both word characters with no boundary between
        # them, so a plain `\bnot\b` search against the UNMODIFIED
        # literal never matches "not" at all. Replacing each literal
        # `\b` with a space turns it into a real, plain-text word
        # boundary before running the word/`.*` checks below.
        cleaned = pat.replace("\\b", " ")
        dotstar_positions = [m.start() for m in dotstar.finditer(cleaned)]
        if not dotstar_positions:
            return False
        return any(
            m.start() < pos
            for m in negation_word.finditer(cleaned)
            for pos in dotstar_positions
        )

    offenders = [
        match.group("pat")
        for match in call_pattern.finditer(source)
        if _is_unbound_negation(match.group("pat"))
    ]
    assert not offenders, (
        "Found a bare '<negation>.*<target>' regex passed directly to "
        "re.search/re.match — route it through _negation_binds() "
        f"instead: {offenders!r}"
    )


def _code_line_count(node: ast.FunctionDef, lines: list) -> int:
    """Count a function's body lines, excluding its docstring, comments,
    and blank lines.

    This is the measure that matches naming-and-functions.md's 50-line
    hard ceiling, which is about CODE complexity, not the prose that
    documents a regex trap or a structural rationale — a function like
    `test_no_unbound_negation_regex_in_this_file` carries a long,
    load-bearing docstring but little actual code, and should not be
    flagged on docstring length alone.
    """
    body = node.body
    has_docstring = (
        bool(body)
        and isinstance(body[0], ast.Expr)
        and isinstance(getattr(body[0], "value", None), ast.Constant)
        and isinstance(body[0].value.value, str)
    )
    if has_docstring:
        start = body[1].lineno if len(body) > 1 else body[0].end_lineno + 1
    else:
        start = body[0].lineno if body else node.lineno + 1
    segment = lines[start - 1 : node.end_lineno]
    return sum(1 for line in segment if line.strip() and not line.strip().startswith("#"))


def test_no_test_function_exceeds_fifty_lines() -> None:
    """Guard against reproducing the bundled-claims defect this file hit
    once already (`test_defines_slots_refusal_bar_and_provenance` grew to
    359 lines bundling ~15 independent claims behind one name, so a
    failure inside named nothing). This guard reads THIS FILE'S OWN
    SOURCE and fails the moment any `def test_...` function's code body
    (docstring/comments/blank lines excluded — see `_code_line_count`)
    exceeds the 50-line hard ceiling (naming-and-functions.md).
    """
    source = Path(__file__).read_text(encoding="utf-8")
    lines = source.splitlines()
    tree = ast.parse(source)
    offenders = [
        (node.name, code_len)
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        for code_len in [_code_line_count(node, lines)]
        if code_len > 50
    ]
    assert not offenders, (
        f"Test function(s) exceed the 50-line hard ceiling: {offenders!r}"
    )


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


def _paragraph_containing(paragraphs_lower: list, *keywords: str):
    """Return the first paragraph containing every keyword, or None.

    Shared across the split-out claim tests below so each keeps the
    file's single search semantics instead of redefining its own closure.
    """
    for p in paragraphs_lower:
        if all(kw in p for kw in keywords):
            return p
    return None


def _paragraphs_lower_of_reference() -> list:
    """Read input-floor.md and return its paragraphs, lowercased/normalized."""
    return [p.lower() for p in _paragraphs_normalized(_read_reference())]


def _list_items_of_reference() -> list:
    """Read input-floor.md and return its top-level numbered list items."""
    return _numbered_list_items(_read_reference())


def _tag_items_of_reference() -> list:
    """Read input-floor.md and return its top-level bullet list items."""
    return _bullet_list_items(_read_reference())


def test_input_floor_names_two_slots() -> None:
    content = _read_reference()
    assert "current state" in content.lower(), "Must name the 'current state' slot."
    assert "wanted difference" in content.lower(), (
        "Must name the 'wanted difference' slot."
    )


def test_refusal_rule_states_empty_slot_and_no_goal() -> None:
    paragraphs_lower = _paragraphs_lower_of_reference()
    refusal_para = _paragraph_containing(
        paragraphs_lower, "empty", "names the empty slot"
    ) or (_paragraph_containing(paragraphs_lower, "empty slot", "emits no goal"))
    assert refusal_para, (
        "Must state the refusal rule: when either slot is empty, name the "
        "empty slot and emit no goal."
    )
    # This paragraph is a single sentence (verified by inspection of
    # input-floor.md §3), so no separate sentence split is needed — the
    # paragraph boundary already is the sentence boundary. "emit(s)" is a
    # plain presence check (no polarity to invert); "no" must BIND to
    # "goal" via `_negation_binds` — a mutant like "will emit, no matter
    # which slot is missing, a goal anyway" keeps "no" and "goal" as bare
    # co-occurring words but puts several unrelated words between them,
    # which the bound gap rejects.
    assert re.search(r"\bemits?\b", refusal_para), (
        "The refusal rule must state the consequence as an emission."
    )
    assert _negation_binds(refusal_para, "no", "goal"), (
        "The refusal rule must state the consequence as emitting NO goal "
        "(not a degraded/vague one) — expected 'no' bound directly to "
        "'goal', not merely co-occurring somewhere in the same sentence."
    )


def test_vague_goal_is_worse_than_none() -> None:
    paragraphs_lower = _paragraphs_lower_of_reference()
    vague_para = _paragraph_containing(paragraphs_lower, "vague", "worse")
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


def test_bar_clause_decidable() -> None:
    list_items = _list_items_of_reference()
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


def test_bar_clause_false_when_written() -> None:
    list_items = _list_items_of_reference()
    false_item = next(
        (
            item
            for item in list_items
            if "false" in item.lower() and "written" in item.lower()
        ),
        None,
    )
    assert false_item, "The bar's 'False when written' item must be a list item."
    false_item_lower = false_item.lower()
    # Bound negation guard: a bare "not ... true" co-occurrence check
    # survives even in an INVERTED sentence — "the condition need not be
    # false when written; it is fine if it is already true" contains "not"
    # (bound to "false", not "true") followed later by "true" and would
    # false-pass a bare co-occurrence check. Require "not" to sit directly
    # against "already"/"be" ahead of "true" — the actual obligation
    # clause — and separately forbid "need not be false" and "already
    # true" appearing as their own (inverted) phrases in this item.
    assert re.search(r"\bmust\s+not\s+already\s+be\s+true\b", false_item_lower) or (
        re.search(r"\bnot\b\s+(?:already\s+)?be\s+true\b", false_item_lower)
    ), (
        "The 'false when written' clause must bind 'not' directly to the "
        "obligation — expected 'must not (already) be true' as a "
        "contiguous clause, not 'not' and 'true' merely co-occurring."
    )
    assert "need not be false" not in false_item_lower, (
        "The 'false when written' clause must not read as 'need not be "
        "false when written' — that inverts the obligation."
    )
    assert not re.search(r"\bfine\s+if\s+it\s+is\s+already\s+true\b", false_item_lower), (
        "The 'false when written' clause must not state it is fine for "
        "the condition to already be true — that inverts the obligation."
    )


def test_bar_clause_free_of_person_dependence() -> None:
    list_items = _list_items_of_reference()
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
    person_item_lower = person_item.lower()
    # Bound negation guard: a bare "not ... depend" co-occurrence check
    # survives even in an INVERTED sentence — "the condition may depend on
    # a person acting or answering, which is fine" contains "not" only
    # inside an earlier, unrelated clause (e.g. "is not decidable by the
    # run itself" from item 3's own second sentence) and "depend" later in
    # the inverted clause — a bare co-occurrence regex would be satisfied
    # even though the actual "may depend ... fine" clause carries no
    # negation of its own. Require "not" to sit directly against "depend"
    # (optionally via "must"), and separately forbid the inverted phrasing
    # itself.
    assert re.search(r"\bmust\s+not\s+depend\b", person_item_lower) or re.search(
        r"\bnot\s+depend\b", person_item_lower
    ), (
        "The 'Free of dependence on a person' clause must bind 'not' "
        "directly to 'depend' — expected 'must not depend' as a "
        "contiguous clause, not 'not' and 'depend' merely co-occurring."
    )
    assert not re.search(r"\bmay\s+depend\s+on\s+a\s+person\b", person_item_lower), (
        "The 'Free of dependence on a person' clause must not state the "
        "condition MAY depend on a person — that inverts the obligation."
    )
    assert "which is fine" not in person_item_lower, (
        "The 'Free of dependence on a person' clause must not read as "
        "acceptable ('which is fine') for the condition to depend on a "
        "person — that inverts the obligation."
    )


def test_bar_is_not_claimed_mechanical() -> None:
    # Structurally isolated to §4's prose intro (heading -> first list
    # item), not the merged intro+items paragraph, so a mutant that
    # flips the intro's polarity cannot be rescued by unrelated item text
    # bled into the same paragraph. "not" must BIND to "mechanical" (via
    # `_negation_binds`), not merely co-occur — a mutant claiming the bar
    # IS mechanical, with an unrelated earlier "not" elsewhere in the
    # intro, must still fail.
    bar_intro = _bar_intro(_read_reference())
    assert "mechanical" in bar_intro.lower(), (
        "The bar section must address whether it is mechanical."
    )
    assert _negation_binds(bar_intro.lower(), "not", "mechanical"), (
        "The bar must be stated as prose judgment, explicitly NOT claimed to "
        "be mechanical — expected 'not' bound directly to 'mechanical' "
        "within the intro, not merely co-occurring."
    )


def test_provenance_tag_user_said() -> None:
    tag_items = _tag_items_of_reference()
    user_said_item = next(
        (item for item in tag_items if "`user-said`" in item.lower()), None
    )
    assert user_said_item and "quoted" in user_said_item.lower(), (
        "Must define `user-said`: the user's own words, quoted."
    )
    # Phrase check: "quoted directly" must appear as a contiguous phrase.
    # Bare containment alone is not enough — "...but is never quoted
    # directly, only paraphrased" still CONTAINS "quoted directly" as a
    # substring while inverting the claim, so it is paired with a
    # whole-item negation guard below.
    assert "quoted directly" in user_said_item.lower(), (
        "The `user-said` tag must state the content is quoted DIRECTLY — "
        "expected the phrase 'quoted directly'."
    )
    # Bound negation guard: "quoted directly" survives as a substring even
    # when negated ("but is never quoted directly, only paraphrased" still
    # contains "quoted directly"), so the phrase check alone lets that
    # mutant through. A blanket "no not/never anywhere in this bullet" ban
    # over-corrects: it also fails legitimate prose that uses "not" in an
    # ordinary contrastive clause elsewhere in the same bullet (e.g.
    # "...quoted directly, not the agent's paraphrase" — a normal way to
    # write a definition, not a negation of the claim). Bind the negation
    # check to "quoted" itself: fail only when "not"/"never" sits within a
    # few words directly BEFORE "quoted" (negating the act of quoting),
    # not when it appears anywhere else in the bullet.
    assert not re.search(
        r"\b(?:not|never)\b(?:\s+\S+){0,3}\s+quoted\b", user_said_item.lower()
    ), (
        "The `user-said` tag must not negate 'quoted' — expected no "
        "'not'/'never' bound directly to 'quoted' within its own bullet "
        "item (a 'not' elsewhere in the bullet, e.g. a contrastive clause, "
        "is fine)."
    )


def test_provenance_tag_derived() -> None:
    tag_items = _tag_items_of_reference()
    derived_item = next(
        (item for item in tag_items if "`derived`" in item.lower()), None
    )
    assert derived_item and "anchor" in derived_item.lower(), (
        "Must define `derived`: names the anchor it was inferred from."
    )
    # Positive-obligation check: "was inferred" must appear as a
    # contiguous phrase. Without this, "the field's content was NOT
    # inferred, though the tag still names the anchor" keeps "names the
    # anchor" intact (see next assert) and false-passes on the
    # `derived`/`anchor` checks alone — the "inferred" half of the
    # definition was never checked for its own polarity.
    assert "was inferred" in derived_item.lower(), (
        "The `derived` tag must state the content WAS INFERRED — expected "
        "the phrase 'was inferred'."
    )
    # Phrase check: "names the anchor" must appear contiguously. A mutant
    # reading "...the tag does not name the anchor" keeps "anchor" present
    # but inverts the claim; it fails here because that exact phrase is
    # gone (the plural "names" does not survive "does not name").
    assert "names the anchor" in derived_item.lower(), (
        "The `derived` tag must state the tag NAMES the anchor — expected "
        "the phrase 'names the anchor'."
    )
    # Bound negation guard, same rationale as `user-said` above: bind the
    # negation to the specific claims it could invert — "inferred" (e.g.
    # "was not inferred") and "anchor" (e.g. "does not name the anchor") —
    # rather than banning "not"/"never" anywhere in the bullet, which would
    # false-fail a legitimate contrastive rewording elsewhere in the item.
    assert not re.search(
        r"\b(?:not|never)\b(?:\s+\S+){0,3}\s+inferred\b", derived_item.lower()
    ), (
        "The `derived` tag must not negate 'inferred' — expected no "
        "'not'/'never' bound directly to 'inferred' within its own bullet "
        "item."
    )
    assert not re.search(
        r"\b(?:not|never)\b(?:\s+\S+){0,3}\s+anchor\b", derived_item.lower()
    ), (
        "The `derived` tag must not negate 'the anchor' — expected no "
        "'not'/'never' bound directly to 'anchor' within its own bullet "
        "item."
    )


def test_provenance_tag_proposed() -> None:
    tag_items = _tag_items_of_reference()
    proposed_item = next(
        (item for item in tag_items if "`proposed`" in item.lower()), None
    )
    assert proposed_item and (
        "confirm" in proposed_item.lower()
    ), "Must define `proposed`: agent-supplied, user has not confirmed it."
    # Positive-obligation check: "agent supplied the content itself" must
    # appear as a contiguous phrase. A mutant reading "the agent did NOT
    # supply the content itself" drops this exact phrase (the "not"
    # replaces "supplied" with "supply"), so it fails here even though the
    # phrase-hunting-only version of this test did not check this clause
    # at all.
    assert "agent supplied the content itself" in proposed_item.lower(), (
        "The `proposed` tag must state the AGENT supplied the content "
        "itself — expected the phrase 'agent supplied the content itself'."
    )
    # Negation-binding check: "not" must sit directly against "confirmed"
    # (optionally via "yet"), not merely co-occur anywhere in the item. The
    # reviewer's round-4 inversion — "the agent did not supply the content
    # itself; the user has already confirmed it" — keeps a bare "not" (now
    # bound to "supply") and the word "confirm" (inside "confirmed"), which
    # is exactly what the old unscoped `"not" in ... and "confirm" in ...`
    # check accepted. Binding "not" immediately to "confirmed" closes that:
    # the mutant's "not" is nowhere near "confirmed", and its "confirmed"
    # clause carries no negation at all ("has already confirmed").
    assert re.search(r"\bnot\b\s+(?:yet\s+)?confirmed\b", proposed_item.lower()), (
        "The `proposed` tag must state the user has NOT (yet) confirmed "
        "it — expected 'not [yet] confirmed' bound together within its "
        "own bullet item, not 'not' and 'confirm' merely co-occurring."
    )


def test_citation_boundary() -> None:
    paragraphs_lower = _paragraphs_lower_of_reference()
    citation_para = _paragraph_containing(paragraphs_lower, "source", "quote")
    assert citation_para, (
        "Must state a recorded purpose is a source an agent quotes to "
        "justify an inference."
    )
    never_authority_para = _paragraph_containing(paragraphs_lower, "never", "authority")
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
    assert _negation_binds(authority_sentence, "never", "authority"), (
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
    assert _negation_binds(
        substitute_sentence, "never|cannot|can't|not", "substitute"
    ), (
        "Must also state a purpose cannot substitute for the user's own "
        "decision — expected a negation bound to 'substitute' within one "
        "sentence."
    )
    assert _paragraph_containing(
        paragraphs_lower, "irreversible"
    ) or _paragraph_containing(paragraphs_lower, "outward-facing"), (
        "The citation boundary must name at least one example of a choice "
        "reserved for the user, e.g. an irreversible or outward-facing action."
    )


def test_bar_negative_guard_required_vs_mechanical() -> None:
    # (regression guard per known trap: a bare substring match on 'require'
    # would false-positive inside 'required'.) Nothing in this reference
    # should claim the bar is REQUIRED to be mechanical — that would
    # contradict the "not ... mechanical" assertion above.
    paragraphs_lower = _paragraphs_lower_of_reference()
    for p in paragraphs_lower:
        if "mechanical" in p and re.search(r"\brequires?\b", p):
            raise AssertionError(
                f"Must not claim the bar 'requires' mechanical checking: {p!r}"
            )


def test_constraints_and_stop_when_source_is_stated() -> None:
    """§1 must not claim the two input slots source every field; §2 must
    say, honestly, where `Constraints` and `Stop-when` actually come from,
    and that the refusal rule does not gate on them.

    Structural scoping: the "other two fields" claim is its own paragraph
    (blank-line-delimited) under §2, isolated from the two mapping bullets
    above it — so a mutant that inverts this paragraph cannot be rescued
    by the unrelated bullet text sharing a merged block.
    """
    content = _read_reference()
    paragraphs = _paragraphs_normalized(content)
    paragraphs_lower = [p.lower() for p in paragraphs]

    def _paragraph_containing(*keywords: str):
        for p in paragraphs_lower:
            if all(kw in p for kw in keywords):
                return p
        return None

    # --- §1 no longer totalizes: it must call the two slots a floor, not
    # the source of every field. ---
    floor_para = _paragraph_containing("floor")
    assert floor_para, "§1 must name the two input slots as 'the floor'."

    # --- §2 states where `constraints` and `stop-when` come from. ---
    source_para = _paragraph_containing(
        "constraints", "stop-when", "not sourced from either input slot"
    )
    assert source_para, (
        "§2 must state that `Constraints` and `Stop-when` are not sourced "
        "from either input slot."
    )
    # Positive-obligation check: the real source (agent, drafted from the
    # same evidence/context) must be stated in that same paragraph, not
    # merely the negative half.
    assert "drafted by the agent" in source_para, (
        "§2 must state Constraints/Stop-when are drafted by the agent — "
        "expected the phrase 'drafted by the agent'."
    )

    # --- The refusal rule must be scoped to the two input slots, not the
    # other two fields — bind the negation to 'trigger' within the same
    # paragraph that raises the point. ---
    gate_sentence = next(
        (s for s in _sentences(source_para) if "refusal rule" in s), None
    )
    assert gate_sentence, (
        "§2 must state the refusal rule's relationship to Constraints/"
        "Stop-when in its own sentence."
    )
    assert _negation_binds(gate_sentence, "not", "trigger"), (
        "Expected 'not' bound directly to 'trigger' within one sentence: "
        "an empty Constraints/Stop-when must not by itself trigger "
        "refusal — not merely co-occur with an unrelated 'not' elsewhere "
        "in the same sentence."
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

    # §2 packs its two mapping bullets back-to-back with no blank line
    # between them, so `_paragraphs_normalized()` (blank-line splitting)
    # merges both into ONE block. Scanning that merged block for "current
    # state ... verification_name" and, separately, "wanted difference ...
    # outcome_name" only proves the four tokens co-occur somewhere in the
    # merged text — it does not prove which slot maps to which field. A
    # mutant that swaps the mapping (current state -> Outcome, wanted
    # difference -> Verification) leaves all four tokens present in the
    # same merged block and still passes. Isolating each bullet first, the
    # way `_bullet_list_items()` isolates §5's tags, binds each slot name
    # to the field name inside ITS OWN bullet only.
    section2_match = re.search(
        r"## 2 — Slot-to-field mapping\n\n(.*?)(?=\n## )", content, re.DOTALL
    )
    assert section2_match, "Expected the §2 'Slot-to-field mapping' section."
    section2_items = _bullet_list_items(section2_match.group(1))

    # Match on the bullet's OWN bolded slot name (its subject), not on
    # whether the phrase merely appears anywhere in the bullet's prose —
    # the "current state" bullet's own explanatory clause happens to
    # mention "the wanted difference" too, which would otherwise pick the
    # wrong bullet for the "wanted difference" match below.
    current_state_item = next(
        (
            item
            for item in section2_items
            if re.match(r"-\s*\*\*current state\*\*", item.lower())
        ),
        None,
    )
    assert current_state_item, (
        "Expected a §2 bullet mapping the 'current state' slot to a field."
    )
    assert verification_name.lower() in current_state_item.lower(), (
        f"Expected the 'current state' bullet itself to name the "
        f"'{verification_name}' field (as named in goal-shape.md), not "
        f"merely have that name appear elsewhere in §2."
    )

    wanted_difference_item = next(
        (
            item
            for item in section2_items
            if re.match(r"-\s*\*\*wanted difference\*\*", item.lower())
        ),
        None,
    )
    assert wanted_difference_item, (
        "Expected a §2 bullet mapping the 'wanted difference' slot to a field."
    )
    assert outcome_name.lower() in wanted_difference_item.lower(), (
        f"Expected the 'wanted difference' bullet itself to name the "
        f"'{outcome_name}' field (as named in goal-shape.md), not merely "
        f"have that name appear elsewhere in §2."
    )


def _section_content(content: str, heading_number: int) -> str:
    """Extract one '## N — ...' section's body, up to the next '## ' heading.

    Used to scope the search for the standing decision rule's name to §2
    only, rather than scanning the whole file for a bold lead.
    """
    pattern = rf"^## {heading_number} — .*?\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    assert match, f"Section {heading_number} not found in goal-shape.md"
    return match.group(1)


def _standing_rule_name_from_shape_reference() -> str:
    """Read the standing decision rule's bold-lead name from goal-shape.md §2.

    §2 has two bold leads — "**Definition**" and the rule's own name. The
    rule's name is whichever bold lead is not "Definition", found
    structurally rather than hardcoded, so a rename by Task 2 (or any
    later edit) flows through instead of drifting silently between the
    two files.
    """
    assert SHAPE_REFERENCE_PATH.exists(), (
        f"Upstream reference not found: {SHAPE_REFERENCE_PATH}"
    )
    shape_content = SHAPE_REFERENCE_PATH.read_text(encoding="utf-8")
    section2 = _section_content(shape_content, 2)
    bold_leads = re.findall(r"\*\*([^*]+)\*\*:", section2)
    rule_names = [name.strip() for name in bold_leads if name.strip().lower() != "definition"]
    assert rule_names, (
        f"Expected a bold-lead rule name (other than 'Definition') in "
        f"goal-shape.md §2, found bold leads: {bold_leads}"
    )
    return rule_names[0]


def test_person_dependence_names_its_two_destinations() -> None:
    """Item 3's remedy must name both destinations for a person-dependent
    fork and forbid it from ever becoming a Stop-when branch.

    A person-dependent condition left with nowhere to go is exactly what
    let drafting agents park such conditions in Stop-when as an exit
    branch — item 3 must close that gap by naming where it goes instead.
    """
    content = _read_reference()
    list_items = _numbered_list_items(content)
    person_item = next(
        (
            item
            for item in list_items
            if "person" in item.lower() and "acting" in item.lower()
        ),
        None,
    )
    assert person_item, "The bar must state the condition must not depend on a person."
    person_item_lower = person_item.lower()

    # "never" must bind directly to "Stop-when" (bound negation, not mere
    # co-occurrence) — a mutant reading "such a condition may still become
    # a Stop-when branch" would keep both words present but drop the
    # binding this assertion requires.
    assert _negation_binds(person_item_lower, "never", "stop-when"), (
        "Item 3 must state such a condition is NEVER a Stop-when branch — "
        "expected 'never' bound directly to 'Stop-when' within item 3."
    )
    assert "constraints" in person_item_lower, (
        "Item 3 must name 'Constraints' as one destination for a "
        "person-dependent condition (the goal pre-decides it there)."
    )
    rule_name = _standing_rule_name_from_shape_reference()
    assert rule_name in person_item, (
        f"Item 3 must name the standing decision rule from goal-shape.md "
        f"§2 verbatim ({rule_name!r}) as the run's delegated destination, "
        f"rather than restating the rule."
    )
