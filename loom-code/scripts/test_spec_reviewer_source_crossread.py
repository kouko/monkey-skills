"""Structural grep-test guarding the conditional source cross-read
instruction added to spec-reviewer.md (Task 5a,
docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md).

spec-reviewer.md is a prompt artifact, not executable code. Its
correctness here is the PRESENCE of one added instruction: when the
plan/spec text under review carries a source citation, the reviewer
must open the cited source and confirm it says what the text claims.
This must be worded as a CONDITIONAL TRIGGER, not a blanket
verification mandate -- Anthropic's current model guidance is that an
unconditional "verify everything" instruction causes over-verification
with no capability gain, and this repo's own guidance
(judgment-rubrics.md quality-floor row) is that prose requiring a
judgment call fails at weak tiers while prose naming a checkable
action survives. spec-reviewer runs at sonnet or haiku
(subagent-driven-development/SKILL.md:182 -- one tier below the
implementer), which is exactly why the trigger must be explicit rather
than left to initiative.

The "worded as a trigger, not a mandate" assertion is scoped to the
ADDED text only, isolated via `_crossread_section` anchored on a
distinctive marker phrase unique to this addition. An unscoped
assertion over the whole file would be the wrong test: this file's
pre-existing `rule-sheet-v1` block already contains unconditional
"MUST" citation-discipline language for an unrelated concern (citing
standards), and code-quality-reviewer.md's dimension-table row for
`external-surface-grounding` (D7, "verify every external-surface call
in this task's diff carries a grounding cite" -- :372 as of this
writing; the peer file, Task 5b) independently carries an
unconditional external-surface mandate --
neither is what this task is about, and an unscoped grep would
conflate them with the new instruction or become unsatisfiable for
the wrong reason.

These checks assert on load-bearing PHRASES (intent), tolerant of
wording variation, so the test guards meaning without being brittle.

Stdlib only (pathlib). Resolve spec-reviewer.md relative to this test
file.
"""

from pathlib import Path

AGENT = Path(__file__).parents[1] / "agents" / "spec-reviewer.md"

# Anchors the added instruction. Must be unique to the new text so the
# isolated section cannot accidentally swallow unrelated pre-existing
# unconditional wording (see module docstring).
MARKER = "conditional source cross-read"


def _text() -> str:
    assert AGENT.is_file(), f"spec-reviewer.md is absent at {AGENT}"
    return AGENT.read_text(encoding="utf-8")


def _crossread_section(text: str) -> str:
    low = text.lower()
    start = low.index(MARKER)
    # The addition is a single list item / short paragraph; stop at
    # the next blank-line-preceded heading or numbered-list boundary
    # so the isolated snippet cannot bleed into an unrelated
    # pre-existing rule that happens to follow it.
    tail = text[start:]
    end_markers = ["\n\n", "\n#"]
    end = len(tail)
    for m in end_markers:
        idx = tail.find(m, len(MARKER))
        if idx != -1:
            end = min(end, idx)
    return tail[:end]


def _consequence_polarity_violations(section: str) -> list:
    """Return polarity violations in a failed-confirmation consequence
    clause given as arbitrary TEXT -- not necessarily the on-disk
    file -- so a hedged/negated mutation can be checked in-memory
    without touching the shared contract file. Empty list = OK.

    Guards against a rewrite that keeps every keyword the sibling
    assertions below check for ("gap", "NEEDS_REVISION") while
    asserting the opposite of the rule, e.g. "this is not a gap
    requiring NEEDS_REVISION" -- pins vocabulary but inverts polarity,
    which the plain keyword assertions cannot catch. Mirrors the
    sibling (e) assertion's pattern in
    test_code_quality_reviewer_source_crossread.py:143-156: an
    ordering check plus an explicit negative-mutation list.

    Scoped to the contradiction clause only: cut at the same "drift"
    marker `_drift_scope_violations` below anchors on, but sliced in
    the opposite direction (`stripped[:drift_idx]` here vs.
    `stripped[drift_idx:]` there). The drift clause that follows
    legitimately negates "gap" in its OWN exemption ("a drifted
    pointer ... is not a gap") -- an unscoped scan over the whole
    section false-positives on that correct text merely because the
    natural phrasing ("it is not a gap") happens to contain the same
    negation-tell substrings this guard watches for in the
    contradiction clause.
    """
    stripped = section.lower().replace("`", "")
    drift_idx = stripped.find("drift")
    scope = stripped if drift_idx == -1 else stripped[:drift_idx]
    violations = []

    # Ordering: the positive assertion ("is a gap") must occur, and it
    # must precede the contrasting negative alternative ("not a
    # note") -- confirming the "not" attaches to the excluded
    # alternative, not to the gap/verdict claim itself.
    gap_idx = scope.find("is a gap")
    not_note_idx = scope.find("not a note")
    if gap_idx == -1:
        violations.append("missing positive 'is a gap' assertion")
    if not_note_idx == -1:
        violations.append("missing 'not a note' contrast")
    if gap_idx != -1 and not_note_idx != -1 and not gap_idx < not_note_idx:
        violations.append("'not a note' precedes the positive gap assertion")

    # Explicit negative-mutation list: none of these polarity-
    # inverting substrings may appear anywhere in the contradiction
    # clause's scope (see scoping note above).
    negation_tells = (
        "not a gap", "isn't a gap", "is not a gap", "no longer a gap",
        "not needs_revision", "isn't needs_revision",
        "is not needs_revision",
    )
    violations.extend(t for t in negation_tells if t in scope)
    return violations


def test_spec_reviewer_consequence_clause_rejects_polarity_inversion():
    """RED demonstration: build a hedged/inverted variant of the
    consequence clause IN MEMORY (never touching the shared contract
    file) and show `_consequence_polarity_violations` rejects it, even
    though it still contains every keyword the sibling assertions in
    test_spec_reviewer_carries_conditional_crossread's (f) block check
    for. Also confirms the predicate accepts the real, unmutated
    on-disk text (the GREEN side)."""
    text = _text()
    section = _crossread_section(text)

    # GREEN: the real on-disk clause has correct polarity.
    assert _consequence_polarity_violations(section) == [], (
        "predicate must accept the real on-disk consequence clause"
    )

    original = (
        "that is a gap: the\n   verdict is `NEEDS_REVISION`, not a "
        "note, not an observation, and\n   not something to excuse on "
        "the plan author's behalf."
    )
    mutated_clause = (
        "this is not a gap requiring NEEDS_REVISION -- it is a note, "
        "an observation the reviewer may excuse on the plan author's "
        "behalf."
    )
    assert original in section, (
        "fixture assumption broken: expected substring not found in "
        "the real contract text -- update this test's anchor"
    )
    mutated = section.replace(original, mutated_clause)
    assert mutated != section, "mutation must actually change the text"

    # The mutated text still contains "gap" and "NEEDS_REVISION" -- it
    # would satisfy every sibling keyword assertion in (f) above --
    # yet it asserts the opposite of the rule.
    assert "gap" in mutated.lower()
    assert "needs_revision" in mutated.lower()

    violations = _consequence_polarity_violations(mutated)
    assert violations, (
        "the polarity guard must reject a hedged/inverted rewrite "
        f"({mutated_clause!r}) that still contains every required "
        "keyword"
    )


def test_spec_reviewer_polarity_guard_scoped_before_drift_clause():
    """RED demonstration of the false positive this fix closes: build
    an in-memory variant of the real item-7 text whose CONTRADICTION
    clause is unchanged (still correct) and whose DRIFT clause uses
    the natural phrasing "it is not a gap" in place of the shipped
    "rather than a gap" -- semantically identical, equally correct
    text. Before the fix, `_consequence_polarity_violations` scanned
    the whole section (including the drift clause) and false-positived
    on this correct text because "it is not a gap" contains both
    "not a gap" and "is not a gap" from the negation-tells list. After
    the fix, the guard is scoped to stop before the drift clause
    begins (mirroring `_drift_scope_violations`'s forward-scope from
    the same "drift" marker), so it must return []."""
    text = _text()
    section = _crossread_section(text)
    normalized = " ".join(section.split())

    assert "rather than a gap" in normalized, (
        "fixture assumption broken: expected substring not found in "
        "the real contract text -- update this test's anchor"
    )
    variant = normalized.replace(
        "rather than a gap", "it is not a gap"
    )
    assert variant != normalized, "mutation must actually change the text"

    violations = _consequence_polarity_violations(variant)
    assert violations == [], (
        "the polarity guard must not false-positive on the drift "
        "clause's own, correct negation of 'gap' -- it must be scoped "
        f"to the contradiction clause only; got {violations}"
    )


def _drift_scope_violations(section: str) -> list:
    """Return violations of the drift-vs-contradiction boundary in the
    failed-confirmation consequence clause, given as arbitrary TEXT --
    not necessarily the on-disk file -- so an in-memory mutation can be
    checked without touching the shared contract file. Empty list = OK.

    The (f) consequence clause above defines what a failed confirmation
    MEANS (a gap) but not what COUNTS as one -- the same omission
    relocated one sentence up. A cold-read fixture
    (docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md
    Sec. Over-firing) whose citation pointer had drifted two lines off
    while its content stayed verbatim-correct produced inconsistent
    handling (haiku named the drift and still passed; sonnet missed it
    and asserted something false about the source) but no false
    NEEDS_REVISION at either tier. Guards against a rewrite that keeps
    'drift'/'citation-hygiene' vocabulary while asserting a drifted
    pointer alone IS a gap (the opposite of the boundary this sentence
    draws), or that drops the boundary sentence entirely.
    """
    # Whitespace-normalized (single spaces): the on-disk clause wraps
    # across lines mid-phrase (e.g. "citation-hygiene\n   note"), which
    # would defeat a literal substring check.
    stripped = " ".join(section.lower().replace("`", "").split())
    drift_idx = stripped.find("drift")
    violations = []
    if drift_idx == -1:
        violations.append("missing any mention of a drifted/stale locator")
        return violations

    clause = stripped[drift_idx:]
    if "citation-hygiene" not in clause:
        violations.append(
            "missing 'citation-hygiene note' classification for a drifted pointer"
        )
    if "rather than a gap" not in clause and "not a gap" not in clause:
        violations.append("missing the drift-is-not-a-gap exemption")
    if "is a gap" in clause:
        violations.append(
            "drifted pointer asserted to be a gap -- polarity inverted"
        )
    return violations


def test_spec_reviewer_carries_drift_vs_contradiction_distinction():
    """The (f) consequence clause defines what a failed confirmation
    MEANS but not what COUNTS as one. §Over-firing of the cold-read
    note fed both tiers a citation whose LINE NUMBER had drifted two
    lines off while its CONTENT was verbatim correct -- neither tier
    over-fired (no false NEEDS_REVISION), but haiku named the drift and
    still returned PASS while sonnet missed it and asserted the cited
    source said something at a location it does not. The fix: a
    drifted pointer whose content is still present in the cited
    document is a citation-hygiene note, not a gap -- only the
    document's CONTENT contradicting or omitting the claim is a failed
    confirmation."""
    text = _text()
    section = _crossread_section(text)
    low = section.lower()

    assert "drift" in low, (
        "must name a drifted/stale locator (line number, range, or "
        "path segment) as distinct from the source's content"
    )
    assert "citation-hygiene" in low, (
        "a drifted pointer whose content is still present must be "
        "classified as a citation-hygiene note"
    )

    violations = _drift_scope_violations(section)
    assert violations == [], (
        f"drift-vs-contradiction boundary violated: {violations}"
    )


def test_spec_reviewer_drift_clause_rejects_polarity_inversion():
    """RED demonstration: build an inverted variant of the drift
    clause IN MEMORY (never touching the shared contract file) and
    show `_drift_scope_violations` rejects it, even though it still
    contains the 'drift'/'citation-hygiene' vocabulary the assertion
    above checks for. Also confirms the predicate accepts the real,
    unmutated on-disk text (the GREEN side)."""
    text = _text()
    section = _crossread_section(text)

    # GREEN: the real on-disk clause draws the boundary correctly.
    assert _drift_scope_violations(section) == [], (
        "predicate must accept the real on-disk drift clause"
    )

    # Whitespace-normalized copy: the on-disk clause wraps mid-phrase
    # (e.g. "citation-hygiene\n   note"), so the literal substring
    # replace below operates on a single-spaced copy rather than the
    # raw multi-line section.
    normalized = " ".join(section.split())
    original = (
        "is a citation-hygiene note rather than a gap, and does not "
        "trigger `NEEDS_REVISION`"
    )
    mutated_clause = (
        "is a citation-hygiene concern and is a gap like any other, "
        "and does trigger `NEEDS_REVISION`"
    )
    assert original in normalized, (
        "fixture assumption broken: expected substring not found in "
        "the real contract text -- update this test's anchor"
    )
    mutated = normalized.replace(original, mutated_clause)
    assert mutated != normalized, "mutation must actually change the text"

    # The mutated text still names 'drift' and 'citation-hygiene' -- it
    # would satisfy the keyword assertions above -- yet it asserts the
    # opposite of the boundary (drift alone now IS a gap).
    assert "drift" in mutated.lower()
    assert "citation-hygiene" in mutated.lower()

    violations = _drift_scope_violations(mutated)
    assert violations, (
        "the drift-scope guard must reject a rewrite "
        f"({mutated_clause!r}) that keeps the vocabulary but inverts "
        "the polarity"
    )


def test_spec_reviewer_carries_conditional_crossread():
    """The contract must state: (a) the if-a-citation-is-present
    condition, (b) the open-and-compare action, (c) an explicit
    no-citation no-op, (d) an inline definition of what counts as a
    source citation, and (e) that the added instruction is worded as a
    trigger, not an unconditional verify-everything mandate -- scoped
    to the added text only."""
    text = _text()
    assert MARKER in text.lower(), (
        "spec-reviewer.md must add a distinctly-named conditional "
        "source cross-read instruction"
    )
    section = _crossread_section(text)
    low = section.lower()

    # (a) condition: triggered only when a citation is present
    assert "citation" in low, "must name the citation condition"
    assert "if " in low or "when " in low, (
        "the citation check must be phrased conditionally (if/when), "
        "not as a standing requirement"
    )

    # (b) action: open the cited source and confirm/compare
    assert "open" in low, "must instruct opening the cited source"
    assert "confirm" in low or "compare" in low or "matches" in low, (
        "must instruct confirming the source says what the text claims"
    )

    # (c) explicit no-citation no-op
    assert "no citation" in low or "no such citation" in low or "carries no" in low, (
        "must state the no-citation case explicitly"
    )
    assert "no-op" in low, (
        "the no-citation case must be named a no-op, not left implicit"
    )

    # (d) inline definition of "source citation"
    assert "file:line" in low or "url" in low, (
        "must define inline what counts as a source citation "
        "(e.g. file:line pointer, URL, named doc+section, quoted excerpt)"
    )

    # (e) trigger, not an unconditional mandate -- scoped to this
    # section only (see module docstring on why unscoped is wrong)
    assert "trigger" in low, (
        "must self-label the instruction as a trigger"
    )
    assert "not a blanket" in low or "not an unconditional" in low or (
        "not a" in low and "mandate" in low
    ), (
        "must explicitly disclaim being a blanket/unconditional "
        "verification mandate"
    )

    # (f) failed-confirmation consequence: the contract must not leave
    # the outcome of a failed cross-read to be inferred. A 2x2 cold-read
    # experiment (haiku x sonnet, with/without item 7) showed the
    # trigger alone fires the cross-read at both tiers, but without a
    # named consequence haiku treats a found contradiction as a `notes`
    # observation and still returns PASS, while sonnet infers NEEDS_
    # REVISION -- same instruction, two verdicts. The consequence must
    # be explicit: failed confirmation is a gap, and the verdict is
    # NEEDS_REVISION.
    assert "does not say" in low or "does not match" in low or "contradict" in low, (
        "must name the failed-confirmation condition (source doesn't "
        "say what the plan/spec text claims)"
    )
    assert "gap" in low, (
        "failed confirmation must be named a gap, not a note or "
        "observation"
    )
    assert "needs_revision" in low, (
        "failed confirmation must name the resulting verdict as "
        "NEEDS_REVISION, not left to be inferred"
    )

    # polarity guard: the two assertions above pin vocabulary, not
    # polarity -- a hedged/inverted rewrite ("this is not a gap
    # requiring NEEDS_REVISION") would satisfy both while asserting
    # the opposite. See
    # test_spec_reviewer_consequence_clause_rejects_polarity_inversion
    # for the RED demonstration against an in-memory mutation.
    assert _consequence_polarity_violations(section) == [], (
        "the consequence clause must not read as a negated/hedged "
        f"claim: {_consequence_polarity_violations(section)}"
    )
