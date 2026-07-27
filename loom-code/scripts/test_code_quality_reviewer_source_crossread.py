"""Structural grep-test guarding the Task 5b addition to
code-quality-reviewer.md's role contract: a conditional instruction to
open a plan's cited source and cross-check it against the plan's
stated fact, triggered only when the plan text this task is judged
against actually carries a source citation
(docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md, Task 5b;
mirrors Task 5a's spec-reviewer test -- same five assertions, this
contract).

code-quality-reviewer.md is a prompt artifact, not executable code;
its correctness here is the PRESENCE of load-bearing PHRASES (intent),
tolerant of wording variation -- see
loom-code/scripts/test_writing_plans_verdict_gate.py for the shape.

Scoping note (load-bearing): this file already carries an UNRELATED,
pre-existing, correct unconditional mandate in the dimension table's
external-surface-grounding row ("verify every external-surface call
in this task's diff carries a grounding cite" -- dimension D7). That
mandate is out of scope for Task 5b and must be left alone. (Its line
number has already drifted once, from :365 to :372, because Tasks 5a
and 5b were written concurrently and 5b's own insertion shifted it --
which is exactly why this note anchors on the row's content, not a
line number that the next insertion will invalidate again.) The final
assertion below (the ADDED instruction reads as a trigger, not a
blanket mandate) is therefore scoped to the added section only, via
an anchor unique to the new text -- an unscoped "no unconditional
mandate anywhere in this file" check would be unsatisfiable both
before and after this task, since that row's mandate is legitimate
and untouched.

Stdlib only (pathlib). Resolve the agent file relative to this test.
"""

from pathlib import Path

AGENT = Path(__file__).parents[1] / "agents" / "code-quality-reviewer.md"

ANCHOR = "conditional source cross-read"


def _text() -> str:
    assert AGENT.is_file(), f"code-quality-reviewer.md is absent at {AGENT}"
    return AGENT.read_text(encoding="utf-8")


def _added_section(text: str) -> str:
    """Isolate the added instruction, anchored on a marker phrase that
    exists only in the new text -- never in the pre-existing,
    far-away external-surface-grounding mandate (dimension table),
    which uses entirely different wording. Cuts at the next
    blank-line-preceded boundary, matching Task 5a's sibling test
    (test_spec_reviewer_source_crossread.py::_crossread_section)
    rather than hardcoding the reviewer-discipline managed-block
    marker string: a fixed marker string is tighter only against that
    one specific neighbor and would still swallow a future role-
    contract item 8 inserted, blank-line-separated, between this item
    and the marker -- exactly the failure mode of an item 8 appended
    directly (no blank line) that Task 5a's own boundary shares, since
    this file's numbered-list items are single-newline-separated with
    no blank line until the section actually ends. Aligning to the
    tighter, convention-based cut removes the dependency on knowing
    the neighbor's exact marker text, which is the part actually worth
    tightening."""
    low = text.lower()
    start = low.index(ANCHOR)
    tail = text[start:]
    end_markers = ["\n\n", "\n#"]
    end = len(tail)
    for m in end_markers:
        idx = tail.find(m, len(ANCHOR))
        if idx != -1:
            end = min(end, idx)
    return tail[:end]


def test_code_quality_reviewer_carries_conditional_crossread():
    """The contract must state: (a) the if-a-citation-is-present
    condition, (b) the open-and-compare action, (c) the explicit
    no-citation no-op, (d) an inline definition of what counts as a
    source citation, and (e) that the ADDED instruction (never the
    pre-existing, out-of-scope external-surface-grounding mandate) is
    bounded by a condition whose false branch is a stated no-op --
    not an unconditional verify-everything mandate."""
    text = _text()
    assert ANCHOR in text.lower(), (
        "code-quality-reviewer.md must carry the conditional source "
        "cross-read instruction (Task 5b)"
    )
    section = _added_section(text)
    low = section.lower()

    # (a) if-a-citation-is-present condition
    assert "carries a source citation" in low, (
        "must state the if-a-citation-is-present condition"
    )

    # (b) open-and-compare action
    assert "open" in low and "confirm" in low, (
        "must state the open-and-compare action (open the cited "
        "source and confirm it says what the plan claims)"
    )

    # (c) explicit no-citation no-op
    assert "no-op" in low, "must state the explicit no-op"
    assert "no citation" in low, (
        "the no-op must be conditioned on citation absence"
    )

    # (d) inline definition of what counts as a source citation
    assert "file:line" in low, (
        "must define what counts as a source citation (file:line, "
        "commit SHA, or an explicit pointer)"
    )

    # (e) trigger, not mandate -- scoped to the ADDED section only.
    # The pre-existing external-surface-grounding mandate ("verify
    # every external-surface call ... carries a grounding cite") is
    # untouched, out of scope, and must not satisfy this assertion.
    #
    # This checks the actual property (a condition whose false branch
    # is a stated no-op), not a "when"-present/"every"-absent keyword
    # proxy: that proxy PASSES on the counterexample "When judging any
    # plan, always cross-check its cited facts" -- it contains "when",
    # omits "every", yet is functionally unconditional. Verified by
    # mutation (loom-code/scripts, this task's report has both runs).
    #
    # Structural check: the trigger condition, the open/confirm
    # action, and the no-op must appear in that order (condition ->
    # action -> negated-condition -> no-op) -- if the no-op does not
    # come after the action, it is not actually gating that action.
    trigger_idx = low.find("carries a source citation")
    action_idx = low.find("open")
    noop_idx = low.find("no-op")
    assert trigger_idx != -1 and action_idx != -1 and noop_idx != -1, (
        "trigger, action, and no-op must all be present in the added "
        "section (see assertions a/b/c above)"
    )
    assert trigger_idx < action_idx < noop_idx, (
        "the trigger condition must precede the open/confirm action, "
        "which must precede the stated no-op -- otherwise the no-op "
        "is not actually the condition's false branch"
    )
    # Reject unconditional-strengthening language that would override
    # the stated conditionality even with a valid trigger/action/no-op
    # ordering in place (e.g. "always", "regardless" nearby).
    unconditional_tells = (
        "always", "any plan", "regardless", "unconditionally",
        "no matter", "every",
    )
    found_tells = [w for w in unconditional_tells if w in low]
    assert not found_tells, (
        f"the added instruction must not contain unconditional-"
        f"strengthening language {found_tells} -- that would override "
        "the stated conditionality even if a trigger word and a "
        "no-op are both present"
    )


def _consequence_polarity_violations(section: str) -> list:
    """Return polarity violations in a failed-confirmation consequence
    clause given as arbitrary TEXT -- not necessarily the on-disk
    file -- so a hedged/negated mutation can be checked in-memory
    without touching the shared contract file. Empty list = OK.

    Guards against a rewrite that keeps every keyword the sibling
    assertions above check for ("finding", "severity floor",
    "🔴"/"fatal") while asserting the opposite of the rule, e.g. "this
    is not a 🔴 fatal finding, it is a 🟡 note" -- pins vocabulary but
    inverts polarity, which the plain keyword assertions above cannot
    catch. Mirrors the (e) assertion's pattern above: an ordering
    check plus an explicit negative-mutation list.

    Scoped to the contradiction clause only: cut at the same "drift"
    marker `_drift_scope_violations` below anchors on, but sliced in
    the opposite direction (`scope[:drift_idx]` here vs.
    `stripped[drift_idx:]` there). The drift clause that follows
    legitimately negates "finding" in its OWN exemption ("a drifted
    pointer ... is not a finding") -- an unscoped scan over the whole
    section false-positives on that correct text merely because the
    natural phrasing ("it is not a finding") happens to contain the
    same negation-tell substrings this guard watches for in the
    contradiction clause.
    """
    # Strip markdown bold so "is a **finding**" reads as "is a
    # finding" -- otherwise the "**" splits what is otherwise a
    # contiguous phrase.
    stripped = section.lower().replace("**", "")
    drift_idx = stripped.find("drift")
    scope = stripped if drift_idx == -1 else stripped[:drift_idx]
    violations = []

    # Ordering: the positive assertion ("is a finding") must occur,
    # and it must precede the contrasting negative alternative ("not a
    # note") -- confirming the "not" attaches to the excluded
    # alternative, not to the finding/severity claim itself.
    finding_idx = scope.find("is a finding")
    not_note_idx = scope.find("not a note")
    if finding_idx == -1:
        violations.append("missing positive 'is a finding' assertion")
    if not_note_idx == -1:
        violations.append("missing 'not a note' contrast")
    if finding_idx != -1 and not_note_idx != -1 and not finding_idx < not_note_idx:
        violations.append(
            "'not a note' precedes the positive finding assertion"
        )

    # Explicit negative-mutation list: none of these polarity-
    # inverting substrings may appear anywhere in the contradiction
    # clause's scope (see scoping note above).
    negation_tells = (
        "not a finding", "not a 🔴", "not fatal", "not a fatal",
        "isn't a finding", "is not a finding", "no longer a finding",
    )
    violations.extend(t for t in negation_tells if t in scope)
    return violations


def test_code_quality_reviewer_consequence_clause_rejects_polarity_inversion():
    """RED demonstration: build a hedged/inverted variant of the
    consequence clause IN MEMORY (never touching the shared contract
    file) and show `_consequence_polarity_violations` rejects it, even
    though it still contains every keyword the sibling assertions
    above check for. Also confirms the predicate accepts the real,
    unmutated on-disk text (the GREEN side)."""
    text = _text()
    section = _added_section(text)

    # GREEN: the real on-disk clause has correct polarity.
    assert _consequence_polarity_violations(section) == [], (
        "predicate must accept the real on-disk consequence clause"
    )

    original = (
        "is a **finding**, not a note — severity floor 🔴 fatal."
    )
    mutated_clause = (
        "this is **not** a 🔴 fatal finding, it is a 🟡 note."
    )
    assert original in section, (
        "fixture assumption broken: expected substring not found in "
        "the real contract text -- update this test's anchor"
    )
    mutated = section.replace(original, mutated_clause)
    assert mutated != section, "mutation must actually change the text"

    # The mutated text still contains "finding", "severity floor" is
    # untouched elsewhere in the section, and "🔴"/"fatal" both still
    # appear -- i.e. it would satisfy every sibling keyword assertion
    # above -- yet it asserts the opposite of the rule.
    assert "finding" in mutated.lower()
    assert "🔴" in mutated and "fatal" in mutated.lower()

    violations = _consequence_polarity_violations(mutated)
    assert violations, (
        "the polarity guard must reject a hedged/inverted rewrite "
        f"({mutated_clause!r}) that still contains every required "
        "keyword"
    )


def test_code_quality_reviewer_polarity_guard_scoped_before_drift_clause():
    """RED demonstration of the false positive this fix closes: build
    an in-memory variant of the real added-section text whose
    CONTRADICTION clause is unchanged (still correct) and whose DRIFT
    clause uses the natural phrasing "it is not a finding" in place of
    the shipped "rather than a finding" -- semantically identical,
    equally correct text. Before the fix,
    `_consequence_polarity_violations` scanned the whole section
    (including the drift clause) and false-positived on this correct
    text because "it is not a finding" contains both "not a finding"
    and "is not a finding" from the negation-tells list. After the
    fix, the guard is scoped to stop before the drift clause begins
    (mirroring `_drift_scope_violations`'s forward-scope from the same
    "drift" marker), so it must return []."""
    text = _text()
    section = _added_section(text)
    normalized = " ".join(section.split())

    assert "rather than a finding" in normalized, (
        "fixture assumption broken: expected substring not found in "
        "the real contract text -- update this test's anchor"
    )
    variant = normalized.replace(
        "rather than a finding", "it is not a finding"
    )
    assert variant != normalized, "mutation must actually change the text"

    violations = _consequence_polarity_violations(variant)
    assert violations == [], (
        "the polarity guard must not false-positive on the drift "
        "clause's own, correct negation of 'finding' -- it must be "
        f"scoped to the contradiction clause only; got {violations}"
    )


def _drift_scope_violations(section: str) -> list:
    """Return violations of the drift-vs-contradiction boundary in the
    failed-confirmation consequence clause, given as arbitrary TEXT --
    not necessarily the on-disk file -- so an in-memory mutation can be
    checked without touching the shared contract file. Empty list = OK.
    Mirrors test_spec_reviewer_source_crossread.py's sibling guard --
    same defect shape, this contract's vocabulary (finding / severity
    floor / 🔴 rather than gap / NEEDS_REVISION).

    The clause fixed above defines what a failed confirmation MEANS
    (a 🔴 finding) but not what COUNTS as one -- the same omission
    relocated one sentence up. A cold-read fixture
    (docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md
    Sec. Over-firing) whose citation pointer had drifted two lines off
    while its content stayed verbatim-correct produced no false
    NEEDS_REVISION at either tier, but inconsistent handling of the
    stale pointer itself. Guards against a rewrite that keeps
    'drift'/'citation-hygiene' vocabulary while asserting a drifted
    pointer alone IS a finding (the opposite of the boundary this
    sentence draws), or that drops the boundary sentence entirely.
    """
    # Whitespace-normalized (single spaces): the on-disk clause wraps
    # across lines mid-phrase (e.g. "citation-hygiene note rather\n
    # than a finding"), which would defeat a literal substring check.
    stripped = " ".join(section.lower().replace("**", "").split())
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
    if "rather than a finding" not in clause and "not a finding" not in clause:
        violations.append("missing the drift-is-not-a-finding exemption")
    if "is a finding" in clause:
        violations.append(
            "drifted pointer asserted to be a finding -- polarity inverted"
        )
    return violations


def test_code_quality_reviewer_carries_drift_vs_contradiction_distinction():
    """The clause fixed by
    test_code_quality_reviewer_states_failed_confirmation_consequence_and_floor
    defines what a failed confirmation MEANS but not what COUNTS as
    one. §Over-firing of the cold-read note fed both tiers a citation
    whose LINE NUMBER had drifted two lines off while its CONTENT was
    verbatim correct -- neither tier over-fired (no false
    NEEDS_REVISION), but haiku named the drift and still passed while
    sonnet missed it and asserted the cited source said something at a
    location it does not. The fix: a drifted pointer whose content is
    still present in the cited document is a citation-hygiene note,
    not a finding -- only the document's CONTENT contradicting or
    omitting the claim is a failed confirmation."""
    text = _text()
    section = _added_section(text)
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


def test_code_quality_reviewer_drift_clause_rejects_polarity_inversion():
    """RED demonstration: build an inverted variant of the drift
    clause IN MEMORY (never touching the shared contract file) and
    show `_drift_scope_violations` rejects it, even though it still
    contains the 'drift'/'citation-hygiene' vocabulary the assertion
    above checks for. Also confirms the predicate accepts the real,
    unmutated on-disk text (the GREEN side)."""
    text = _text()
    section = _added_section(text)

    # GREEN: the real on-disk clause draws the boundary correctly.
    assert _drift_scope_violations(section) == [], (
        "predicate must accept the real on-disk drift clause"
    )

    # Whitespace-normalized copy: the on-disk clause wraps mid-phrase
    # (e.g. "citation-hygiene note rather\n   than a finding"), so the
    # literal substring replace below operates on a single-spaced copy
    # rather than the raw multi-line section.
    normalized = " ".join(section.split())
    original = (
        "is a citation-hygiene note rather than a finding, and does "
        "not trigger the 🔴 floor"
    )
    mutated_clause = (
        "is a citation-hygiene concern and is a finding like any "
        "other, and does trigger the 🔴 floor"
    )
    assert original in normalized, (
        "fixture assumption broken: expected substring not found in "
        "the real contract text -- update this test's anchor"
    )
    mutated = normalized.replace(original, mutated_clause)
    assert mutated != normalized, "mutation must actually change the text"

    # The mutated text still names 'drift' and 'citation-hygiene' -- it
    # would satisfy the keyword assertions above -- yet it asserts the
    # opposite of the boundary (drift alone now IS a finding).
    assert "drift" in mutated.lower()
    assert "citation-hygiene" in mutated.lower()

    violations = _drift_scope_violations(mutated)
    assert violations, (
        "the drift-scope guard must reject a rewrite "
        f"({mutated_clause!r}) that keeps the vocabulary but inverts "
        "the polarity"
    )


def test_code_quality_reviewer_states_failed_confirmation_consequence_and_floor():
    """Follow-up fix: a live 2x2 cold-read experiment (haiku/sonnet x
    with/without this item) showed the original wording named the
    ACTION (open + confirm) but left the failed-confirmation
    CONSEQUENCE to inference -- haiku inferred 'note' and passed a
    task built on a plan contradicted by its own cited source; sonnet
    inferred 'gap' and failed it. An instruction whose severity must
    be inferred is a judgment call, which is exactly what breaks at
    weak tiers. The fix: state explicitly that a failed cross-read
    confirmation is a FINDING (not a note), with a named severity
    floor."""
    text = _text()
    section = _added_section(text)
    low = section.lower()

    # consequence: failed confirmation is a *finding*, not a note
    assert "finding" in low, (
        "must state that a failed cross-read confirmation is a finding"
    )

    # severity floor stated explicitly, and it is 🔴 fatal: a plan
    # asserting a fact its own cited source contradicts propagates
    # into downstream stations that judge conformance to that plan,
    # so the floor cannot rest at 🟡 (should-fix).
    assert "severity floor" in low, "must name an explicit severity floor"
    assert "🔴" in section and "fatal" in low, (
        "the severity floor must be 🔴 fatal, not 🟡 -- the artifact "
        "was built to conform to a plan whose own cited source "
        "contradicts it, so the failure cannot settle for should-fix"
    )

    # polarity guard: the above three assertions pin vocabulary, not
    # polarity -- a hedged/inverted rewrite ("this is not a 🔴 fatal
    # finding, it is a 🟡 note") would satisfy all three while
    # asserting the opposite. See
    # test_code_quality_reviewer_consequence_clause_rejects_polarity_inversion
    # for the RED demonstration against an in-memory mutation.
    assert _consequence_polarity_violations(section) == [], (
        "the consequence clause must not read as a negated/hedged "
        f"claim: {_consequence_polarity_violations(section)}"
    )
