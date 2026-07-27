"""Structural grep-test guarding the pointer-not-copy rule added to
`writing-plans/references/plan-format.md` (Task 1 of
`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md`, brief
`docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md:93-98`).

plan-format.md is a prompt/contract artifact, not executable code.
Nothing importable can observe whether a plan author cited their
sources, because this file IS the instruction the plan author (and the
plan-document-reviewer) reads. Its correctness condition is therefore
the PRESENCE of the load-bearing phrases that make the rule executable
by that reader -- the same convention as
`test_writing_plans_verdict_gate.py` and
`test_sdd_review_weight_marker.py`. Assertions target intent-bearing
phrases, tolerant of surrounding wording, so the guard survives an
edit that rephrases and fails an edit that removes a conjunct.

The rule has four conjuncts, all four load-bearing:

(a) **Citation requirement** -- a verifiable technical assertion
    carries a `file:line` citation. Without it the plan restates a
    fact it could have pointed at, and the copy drifts from the source
    while every test stays green (brief's #619 evidence: a three-term
    identity copied from four-term evidence).
(b) **Unverified-assumption escape** -- a fact may instead be
    explicitly marked an unverified assumption. Without the escape the
    rule is unsatisfiable for genuinely-unknown facts and readers
    route around it by inventing citations.
(c) **Produce-the-source-first consequence** -- a fact with no citable
    source means the source has to be produced (a probe, a test), and
    that is a task, not a sentence. Without it (a) and (b) collapse
    into "mark everything an assumption".
(d) **Inline operational definitions** -- brief:242 requires every
    term entering skill contract text to carry an inline operational
    definition, because the reader may be running at a weak model
    tier; a term the reader has to guess at is a defect. This is
    checked at each term's FIRST occurrence in the file and only
    within that occurrence's own paragraph -- a definition three
    paragraphs later is not inline. It rides in the same test as the
    rule because an undefined term makes the rule non-executable:
    "rule stated" and "terms defined" are one acceptance boundary
    (plan Notes, "Why term-definition rides in the same test").

Stdlib only (pathlib). plan-format.md is resolved relative to this
test file.
"""

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


def _rule_section(text: str) -> str:
    """Isolate the pointer-not-copy rule's own section.

    Scoping to the section (rather than grepping the whole file) means
    the conjunct assertions can only be satisfied by the rule itself --
    an incidental mention of "citation" elsewhere in the schema cannot
    keep this test green after the rule is deleted. The section runs
    from its heading to the next heading of the same or shallower
    depth.
    """
    lines = text.splitlines(keepends=True)
    start = None
    depth = 0
    for i, line in enumerate(lines):
        if line.startswith("#") and "pointer-not-copy" in line.lower():
            start = i
            depth = len(line) - len(line.lstrip("#"))
            break
    assert start is not None, (
        "plan-format.md carries no heading naming the pointer-not-copy "
        "rule -- the rule must be a findable section a plan author and "
        "the plan-document-reviewer can be pointed at, not a sentence "
        "buried in unrelated prose"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if line.startswith("#") and len(line) - len(line.lstrip("#")) <= depth:
            end = j
            break
    return "".join(lines[start:end])


def _first_paragraph_at(text: str, term: str) -> str:
    """The paragraph containing the FIRST occurrence of `term`.

    "Defined inline where it first appears" is operationalized as:
    the definitional cues sit in the same paragraph as the term's first
    use. A gloss further down the file fails a reader who stops at the
    sentence that used the term.
    """
    low = text.lower()
    assert term in low, f"the rule never uses the term {term!r}"
    start = low.index(term)
    para_start = text.rfind("\n\n", 0, start)
    para_start = 0 if para_start == -1 else para_start + 2
    para_end = text.find("\n\n", start)
    para_end = len(text) if para_end == -1 else para_end
    return text[para_start:para_end]


def test_pointer_not_copy_rule_present():
    """plan-format.md states the pointer-not-copy rule with all four
    conjuncts, and defines inline every term the rule introduces."""
    text = _text()
    section = _rule_section(text)
    low = section.lower()

    # (a) citation requirement
    assert "verifiable technical assertion" in low, (
        "must name the class of statement the rule binds -- "
        "'verifiable technical assertion'"
    )
    assert "file:line" in low, (
        "must require a `file:line` citation specifically; 'cite your "
        "sources' is not checkable by a reviewer"
    )

    # (b) unverified-assumption escape
    assert "unverified assumption" in low, (
        "must offer the explicit escape -- a fact may instead be marked "
        "an unverified assumption; without it the rule is unsatisfiable "
        "for genuinely-unknown facts"
    )
    assert "marked" in low or "mark it" in low, (
        "the escape must be an explicit MARKING in the plan text, not a "
        "silent omission -- an unmarked guess reads identically to a "
        "verified fact"
    )

    # (c) produce-the-source-first consequence
    assert "probe" in low, (
        "must name producing the source (a probe, a test) as the "
        "consequence when no citable source exists"
    )
    assert "produce" in low, (
        "must state that the missing source has to be PRODUCED first, "
        "not that the assertion may stand uncited"
    )
    assert "not a sentence" in low, (
        "must state that producing the source is a TASK, not a sentence "
        "-- otherwise (a) and (b) collapse into 'mark everything an "
        "assumption'"
    )

    # (d) brief:242 -- every introduced term defined inline at first use
    assertion_para = _first_paragraph_at(section, "verifiable technical assertion").lower()
    for cue in ("number", "formula", "field list"):
        assert cue in assertion_para, (
            f"'verifiable technical assertion' must be defined inline at "
            f"its first use by enumerating what counts ({cue!r} missing) "
            f"-- a weak-tier reader cannot classify a sentence from the "
            f"bare term"
        )
    assert "behaviour" in assertion_para or "behavior" in assertion_para, (
        "'verifiable technical assertion' must include a claim about "
        "existing behaviour among the enumerated kinds -- that is the "
        "defect class the rule exists for (brief:93-98)"
    )

    assumption_para = _first_paragraph_at(section, "unverified assumption").lower()
    assert (
        "not been checked" in assumption_para
        or "not checked" in assumption_para
        or "not verified" in assumption_para
        or "no source" in assumption_para
    ), (
        "'unverified assumption' must be defined inline at its first use "
        "-- state that the author has not checked it against a source, so "
        "the reader knows what the label asserts"
    )


def _per_task_block_section(text: str) -> str:
    """Isolate the '### Per-task block' section (Task 2 of
    `docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md`).

    Scoping to this section -- rather than grepping the whole file --
    means the reuse-adequacy assertions below can only be satisfied by
    the field actually living inside the per-task schema, not by an
    incidental use of "reuse" or "behaviour" elsewhere in the document
    (plan-format.md already uses both words outside this section). The
    section runs from the '### Per-task block' heading to the next
    heading of the same or shallower depth (`### Stated facts ...`),
    which also covers the `####`-depth subsections describing
    individual fields (Files touched, Review-weight, External
    surfaces, ...) -- the same place a Reuse-adequacy subsection
    belongs.
    """
    lines = text.splitlines(keepends=True)
    start = None
    depth = 0
    for i, line in enumerate(lines):
        if line.startswith("#") and "per-task block" in line.lower():
            start = i
            depth = len(line) - len(line.lstrip("#"))
            break
    assert start is not None, (
        "plan-format.md carries no '### Per-task block' heading -- the "
        "per-task schema must be a findable section"
    )
    end = len(lines)
    in_fence = False
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        # A fenced code block's own contents (e.g. the schema's worked
        # examples embed a literal "## Task <N> -- ..." heading) must
        # not be mistaken for a real heading that ends this section.
        if not in_fence and line.startswith("#") and len(line) - len(line.lstrip("#")) <= depth:
            end = j
            break
    return "".join(lines[start:end])


def test_reuse_adequacy_field_present():
    """plan-format.md's per-task block documents a reuse-adequacy
    declaration: the behaviour-match claim, the why-acceptable clause,
    and an inline definition of what counts as a behaviour difference
    (Task 2, brief item 'Reuse-adequacy declaration'; motivating
    evidence: #619 reused the top-line lane's selector in the
    statement lane without re-checking its semantics --
    `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`
    §3.7 A-2)."""
    text = _text()
    section = _per_task_block_section(text)
    low = section.lower()

    # field name
    assert "reuse-adequacy" in low, (
        "the per-task block must name a Reuse-adequacy field -- a task "
        "instructed to reuse an existing helper must declare whether its "
        "behaviour still holds in the new lane"
    )

    # behaviour-match claim
    assert "behaviour-match claim" in low, (
        "must name the behaviour-match claim -- the one-line statement of "
        "whether the helper's behaviour in the new lane matches its "
        "behaviour in the old one"
    )
    match_para = _first_paragraph_at(section, "behaviour-match claim").lower()
    assert "new lane" in match_para and "old" in match_para, (
        "the behaviour-match claim must be defined against the concrete "
        "old-lane vs new-lane comparison, not left abstract"
    )

    # why-acceptable clause
    assert "why-acceptable clause" in low, (
        "must name the why-acceptable clause -- the stated reason a "
        "behaviour difference, if any, is acceptable for this task"
    )
    accept_para = _first_paragraph_at(section, "why-acceptable clause").lower()
    assert "acceptable" in accept_para, (
        "the why-acceptable clause must require a stated reason the "
        "difference is acceptable, not just record that one exists"
    )

    # inline definition of "behaviour difference"
    diff_para = _first_paragraph_at(section, "behaviour difference").lower()
    for cue in ("different value", "different branch", "different default"):
        assert cue in diff_para, (
            f"'behaviour difference' must be defined inline at its first "
            f"use by enumerating what counts ({cue!r} missing) -- a "
            f"weak-tier reader cannot classify a helper's divergence from "
            f"the bare term"
        )
