"""Structural grep-window test guarding Check 18, added to
`plan-document-reviewer-prompt.md` by Task 6 of
`docs/loom/plans/2026-08-13-open-question-dispatch-gate.md`.

plan-document-reviewer-prompt.md is a prompt/contract artifact, not
executable code: nothing importable observes whether a weak-tier
reviewer actually applies Check 18. This file IS the instruction that
reviewer reads, so its correctness condition is the PRESENCE of the
load-bearing phrases that make the check applicable by that reader --
same convention as `test_plan_document_reviewer_check17.py`.

Check 18 gates two conditions: (a) the `## Open Questions` slot is
absent from the plan; (b) the plan declares the pinned N/A line while
its own prose elsewhere hedges an undecided fork. The (b) half is
deliberately written as a verifiable ACTION (grep for seed vocabulary),
never a judgment call ("decide whether the N/A is honest") --
this repo has recorded evidence (docs/loom/memory/
weak_model_caveats_need_verifiable_action_not_judgment -- see
`~/.claude/rules/judgment-rubrics.md` lineage) that judgment-shaped
prose fails on weak executors while action-shaped prose holds.

Seed vocabulary was NOT copied from the task brief verbatim -- it was
grounded by an independent case-insensitive sweep of
`docs/loom/plans/*.md` (this file's own module-level constant mirrors
that sweep's result). Two candidate phrasings the brief suggested
("not yet decided", "we may want to") had zero hits anywhere in that
corpus and were dropped; "undecided" was added after the sweep found a
real (if generic) hit. See the implementer report for the full sweep
output.

Scope: isolates the Check 18 table row and does not grep the whole
file, so an incidental match elsewhere (e.g. Check 17's row, which
also uses words like "unresolved"-adjacent vocabulary) cannot keep
this test green after the row is deleted
(docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md).

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

PROMPT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-document-reviewer-prompt.md"
)

# Grounded by an independent sweep of docs/loom/plans/*.md (case-insensitive
# grep), not copied from the task brief. "deliberately not resolved",
# "two reviewers disagree", "routed to whole-branch review" and
# "open design question" all occur verbatim in the worked negative case
# (docs/loom/plans/2026-08-13-brief-item-addressability.md:354-373).
# "left open", "TBD", "unresolved" occur elsewhere in the corpus as
# generic hedges. "undecided" occurs once (plan-stage-fact-grounding.md).
SEED_VOCAB = (
    "deliberately not resolved",
    "two reviewers disagree",
    "routed to whole-branch review",
    "open design question",
    "left open",
    "TBD",
    "unresolved",
    "undecided",
)


def _text() -> str:
    assert PROMPT_MD.is_file(), f"plan-document-reviewer-prompt.md is absent at {PROMPT_MD}"
    return PROMPT_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _check18_row(text: str) -> str:
    """Isolate the Check 18 table row -- the line beginning `| 18 |`."""
    for line in text.splitlines():
        if line.strip().startswith("| 18 |"):
            return line
    raise AssertionError("Check 18 table row (`| 18 |`) not found")


def _check18_cells(text: str) -> list[str]:
    """Split the Check 18 row into its three pipe-delimited cells:
    `[<check_id>, <check description>, <gap column>]`. The row states
    "outside the `## Open Questions` section" TWICE -- once in the
    operative check-description cell (where the scan instruction a
    reviewer actually runs lives), once as a prose echo in the gap
    column. A guard that greps the whole row is satisfiable by either
    occurrence alone: a revert of ONLY the operative sentence (leaving
    the gap-column echo untouched) still passes a whole-row grep while
    reinstating the fatal whole-document scan. Callers that must pin a
    SPECIFIC one of the two occurrences slice to this cell, per
    docs/loom/memory/
    substring-assertions-must-pin-the-phrase-their-message-names.md
    ("count() the token in the guarded scope; more than one occurrence
    means the assertion is pinning an unknown one of them")."""
    row = _check18_row(text)
    cells = row.split("|")
    assert len(cells) == 5, f"Check 18 row must have exactly 3 cells, got {row!r}"
    return cells


def _check18_check_cell(text: str) -> str:
    """The operative check-description cell (column 2) -- normalized
    and lowercased, matching `_check18_row`'s callers' convention."""
    return _norm(_check18_cells(text)[2]).lower()


def test_check18_gates_absent_slot_and_false_na():
    """Named RED test (plan Task 6 Acceptance.RED): fails today because
    the prompt holds 17 checks -- no `| 18 |` row exists yet. Once it
    exists, pins both gating conditions: (a) the `## Open Questions`
    heading absent; (b) the pinned N/A line contradicted by hedging
    vocabulary, with the seed vocabulary present verbatim."""
    row = _norm(_check18_row(_text()))
    lower = row.lower()

    # condition (a): absent slot
    assert "## open questions" in lower, (
        "Check 18 must name the `## Open Questions` heading"
    )
    assert "absent" in lower, "Check 18 must gate on the slot being absent"

    # condition (b): false N/A against hedging prose elsewhere in the plan
    assert "n/a — no unresolved question" in lower, (
        "Check 18 must quote the pinned N/A line verbatim from "
        "plan-format.md's §Plan-level open-questions slot"
    )
    for phrase in SEED_VOCAB:
        assert phrase.lower() in lower, (
            f"Check 18 seed vocabulary must include {phrase!r} "
            "(grounded by the docs/loom/plans/*.md sweep)"
        )


def test_check18_never_reassigns_retired_check_5():
    """The permanently-retired Check 5 slot must stay untouched and
    unreassigned -- Check 18 is a NEW row, not a renumbering of 5.
    Mutation check: if Check 18's content were spliced into row 5's
    cells instead of a fresh `| 18 |` row, this test's second assertion
    fails (no `| 18 |` row exists) while the first (row 5 still says
    RETIRED) would misleadingly stay green alone -- both are asserted
    together so neither can mask the other's violation."""
    text = _text()
    row5 = next(
        line for line in text.splitlines() if line.strip().startswith("| 5 |")
    )
    assert "RETIRED" in row5, "Check 5's row must still say RETIRED"
    assert "never applied" in row5.lower(), (
        "Check 5's row must still state it is never applied"
    )
    # Check 18 exists as its OWN row (proves 5 was not silently repurposed
    # to carry Check 18's content instead of a new numbered row).
    assert _check18_row(text).strip().startswith("| 18 |")


def test_check18_false_na_condition_is_action_not_judgment():
    """(b)'s wording must instruct a mechanical grep, not ask the
    reviewer to 'decide' or 'judge' whether the N/A is honest -- the
    load-bearing design constraint from the task brief. Would fail if
    the row instead said something judgment-shaped like 'decide whether
    the N/A declaration is honest given the plan's tone'."""
    row = _norm(_check18_row(_text()))
    lower = row.lower()
    assert "verifiable action" in lower, (
        "Check 18 must name itself a verifiable action"
    )
    assert "not a judgment call" in lower, (
        "Check 18 must explicitly disclaim judgment-call framing"
    )
    assert "grep" in lower, (
        "Check 18 must instruct the reviewer to grep -- a concrete, "
        "mechanical step, not an inference"
    )


def test_check18_vocabulary_is_explicitly_extensible_and_nonexhaustive():
    """The seed list must not read as a closed enum -- an unlisted hedge
    phrase must still be reportable. Would fail if the row instead
    presented the list as the complete/only set of hedges to check."""
    row = _norm(_check18_row(_text()))
    lower = row.lower()
    assert "non-exhaustive" in lower, (
        "Check 18 must state the seed vocabulary is non-exhaustive"
    )
    assert "extensible" in lower, (
        "Check 18 must state the seed vocabulary is extensible"
    )
    assert "unlisted hedge" in lower, (
        "Check 18 must explicitly say an unlisted hedge phrase still "
        "gets reported -- otherwise 'non-exhaustive' is an unenforced "
        "adjective with no behavioral consequence"
    )


def test_check18_states_exclusion_against_own_machinery():
    """Guards the self-vocabulary-collision hazard
    (docs/loom/memory/a-prose-scanner-meets-its-own-vocabulary-first.md):
    a hedge phrase quoted only as an example -- e.g. inside this very
    check's own seed-vocabulary list, if a plan under review happens to
    paste this row's text verbatim (as this arc's own plan literally
    does at Task 6's Acceptance.GREEN) -- must not itself trigger a
    false-N/A gap. Would fail if the row omitted any exclusion and
    instructed a bare whole-document grep instead.

    The third exclusion (quoted example list) must be a MECHANICAL
    pattern, not an undefined phrase a reviewer has to interpret --
    unlike the first two, which are crisp Markdown-syntax categories.
    Would fail if the row still said the unstructured "double-quoted
    example list" (the revision-round finding) instead of a checkable
    pattern (double-quoted, comma-separated, two-or-more items)."""
    row = _norm(_check18_row(_text()))
    lower = row.lower()
    assert "fenced code block" in lower, (
        "Check 18 must exclude fenced-code-block occurrences from the scan"
    )
    assert "backtick-quoted span" in lower, (
        "Check 18 must exclude backtick-quoted-span occurrences from the scan"
    )
    assert "double-quoted" in lower and "comma-separated" in lower, (
        "Check 18 must define the quoted-list exclusion mechanically -- "
        "a double-quoted, comma-separated phrase list -- not the "
        "undefined 'double-quoted example list' a reviewer must interpret"
    )
    assert "two or more" in lower, (
        "Check 18's quoted-list exclusion must state its minimum count "
        "(two or more consecutive double-quoted items) so a reviewer "
        "can check it mechanically, matching the crispness of the other "
        "two Markdown-syntax exclusions"
    )


def test_check18_scopes_false_na_scan_outside_open_questions_section():
    """REGRESSION GUARD for the fatal defect this revision round fixes:
    Check 18(b) inverted on its most common case -- a plan whose
    `## Open Questions` body is exactly the grammar-mandated pinned N/A
    line (plan-format.md:78-79, `N/A -- no unresolved question: <reason>`)
    contains the word "unresolved" verbatim, which is also this check's
    own seed vocabulary. Scanning the WHOLE plan's prose (the pre-fix
    wording) meant the mandated N/A line tripped the false-N/A condition
    on every correctly-formed declaration -- the check fired on the case
    it exists to validate (docs/loom/memory/
    a-prose-scanner-meets-its-own-vocabulary-first.md).

    The fix is STRUCTURAL: the grep is scoped to prose OUTSIDE the
    `## Open Questions` section, so the section's own mandated wording
    (or a recorded entry's own text) can never trigger itself. This
    pins the scoping clause SPECIFICALLY -- not merely that some word
    like "elsewhere" appears (the pre-fix row already said "elsewhere"
    and still inverted), which is why a weaker assertion would not have
    caught the fatal defect this round exists to fix.

    OCCURRENCE-SPECIFIC (revision-round 3 fix): the phrase "outside the
    `## Open Questions` section" occurs TWICE in the row -- once in the
    operative check-description cell (the scan instruction that
    actually runs), once as a prose echo in the gap column. Asserting
    against the whole row is satisfiable by the gap-column echo ALONE:
    a mutation that reverts only the operative sentence back to a
    whole-document scan -- reinstating the fatal -- leaves the gap
    column untouched and the row-wide grep still finds a hit. So this
    test slices to `_check18_check_cell` (column 2 only) and asserts
    there, where reverting the operative sentence has nothing else to
    hide behind."""
    check_cell = _check18_check_cell(_text())
    assert check_cell.count("outside the `## open questions` section") == 1, (
        "Check 18(b)'s OPERATIVE check-description cell (not just the "
        "gap column) must scope its grep to prose OUTSIDE the "
        "`## Open Questions` section -- a structural exclusion, not a "
        "per-phrase exemption -- so the section's own mandated N/A "
        "wording can never trigger the check on itself. A gap-column "
        "echo of this phrase alone does not satisfy this: the SCAN "
        "INSTRUCTION itself must carry the scoping clause."
    )
    assert "own mandated wording" in check_cell, (
        "Check 18(b)'s check-description cell must state explicitly "
        "that the N/A line's own mandated wording, inside the Open "
        "Questions section, is excluded from the scan -- otherwise a "
        "reviewer applying the row literally would still grep it and "
        "re-invert"
    )
    assert "is never a hit" in check_cell, (
        "Check 18(b)'s check-description cell must state the "
        "in-section occurrence is NEVER a hit, not merely 'excluded' "
        "in the abstract"
    )


def test_check18_still_scans_decision_log_and_other_sections_for_hedging():
    """A plan can carry the correctly-formed N/A line in `## Open
    Questions` while genuinely hedging an unresolved fork elsewhere --
    e.g. its `## Decision Log` -- and Check 18 must still fire on THAT.
    Pins that the row names a concrete section other than Open Questions
    as still in scope, so the section-scoping fix cannot be misread as a
    blanket document-wide exemption for the seed vocabulary.

    The POSITIVE assertions below (naming Decision Log, "anywhere else
    in the plan") are phrase co-occurrence: they cannot detect a
    NEUTERING sentence APPENDED elsewhere in the row that leaves both
    phrases untouched but declares the whole check advisory-only /
    non-firing (revision-round 3 finding: mutation F appended exactly
    such a sentence -- "this scan is advisory only and never produces
    a reportable gap by itself ... treat every occurrence ... as
    excluded" -- deleting nothing the positive assertions grep for, and
    all tests stayed green). So this test ALSO asserts the row contains
    NO such neutering language -- an addition that contradicts the
    positive "still scans / still a gap" obligation must redden this
    test even though it deletes nothing. Would fail if the row (a)
    dropped the "outside the section" framing for a document-wide
    exemption, OR (b) kept that framing but added language declaring
    the check advisory-only / no-gap-by-itself.

    KNOWN LIMIT of the neutering guard above (documented here, not
    fixed -- do not widen the blacklist in response): the two banned
    phrases are a literal-string match. They catch (1) outright
    deletion of the "outside the section" / "still scans Decision Log"
    scoping language, and (2) the exact two neutering phrasings seen in
    revision-round 3's mutation F ("advisory only", "never produces a
    reportable gap"). They do NOT catch a REWORDED neutering sentence
    that says the same thing in different words -- e.g. the follow-up
    mutation F' found during this task: "Reviewers should treat hits
    from this scan as informational; they do not on their own justify
    a gaps entry." That sentence leaves both banned phrases absent and
    both positive assertions above satisfied, so this test stays green
    while the check is semantically neutered just the same. Whether a
    sentence neuters the check is a judgment call over MEANING, not a
    mechanical string match -- no blacklist, however long, closes that
    gap; each addition only buys immunity to wording already observed,
    and a guard that claims to catch "neutering" in general while
    actually catching two known phrasings is the same gate-theater
    this Check 18 arc exists to prevent, one level up. A rewording
    like F' can only be caught by a human or LLM review reading the
    row for meaning, not by this test."""
    row = _norm(_check18_row(_text()))
    lower = row.lower()
    assert "decision log" in lower, (
        "Check 18(b) must name Decision Log as a concrete section still "
        "in scope for the hedging scan -- proving the fix excludes only "
        "the Open Questions section, not the whole document"
    )
    assert "anywhere else in the plan" in lower, (
        "Check 18(b) must state the scan covers the rest of the plan "
        "generally (task Acceptance fields, Notes, etc.), not just the "
        "one named example section"
    )
    for neutering_phrase in (
        "advisory only",
        "never produces a reportable gap",
    ):
        assert neutering_phrase not in lower, (
            f"Check 18(b) must not carry neutering language "
            f"({neutering_phrase!r} found) -- an advisory-only / "
            "no-gap-by-itself disclaimer would silently stop the check "
            "from ever firing, contradicting the positive 'still scans "
            "Decision Log and other sections' obligation asserted above"
        )


def test_check18_defines_section_extent_and_is_fence_aware_against_decoy_headings():
    """REGRESSION GUARD (revision-round 3 finding): Check 18(b) scopes
    its grep to "outside the `## Open Questions` section" but never
    said where that section ENDS, and had no defense against a
    `## Open Questions`-looking heading quoted inside a FENCED CODE
    BLOCK that precedes the real section -- a literal grep anchoring on
    the first textual occurrence of the heading text would anchor on
    that decoy and then treat the real section as "outside", reinstating
    the exact fatal this row exists to prevent.

    `loom-code/scripts/check_open_questions.py` (a sibling task, same
    arc) was rebuilt this round to face the identical hazard: it scans
    only fence-external lines via `adjudication_split.
    iter_lines_outside_fences`, defines the section's extent as heading
    through the next level-2 heading or end of file, and fails loudly
    when more than one REAL (non-fenced) `## Open Questions` heading
    exists rather than silently picking the first. This test pins the
    prose gate mirroring that same discipline, so the prose gate and
    the script gate cannot disagree about what "the section" is.

    Would fail if the row stated the outside-the-section scoping
    without ever defining the section's extent, without excluding a
    fenced-code-block heading from counting as a real section boundary,
    or without saying what to do when more than one real heading
    exists."""
    check_cell = _check18_check_cell(_text())
    assert "next level-2" in check_cell and "##" in check_cell, (
        "Check 18(b) must state the section's extent runs from the "
        "`## Open Questions` heading to the next level-2 (`##`) "
        "heading -- mirroring check_open_questions.py's own section-"
        "extent definition -- so a reviewer knows exactly where "
        "'outside the section' begins"
    )
    assert "end of the document" in check_cell or "end of document" in check_cell, (
        "Check 18(b) must state the section runs to end of the "
        "document when no later `##` heading exists"
    )
    assert "fenced code block" in check_cell and (
        "heading" in check_cell
    ), (
        "Check 18(b) must state that a `## Open Questions`-looking "
        "heading found inside a fenced code block is not a real "
        "heading -- otherwise a literal grep anchoring on a decoy "
        "heading (a worked example quoted before the real section) "
        "would treat the real section as 'outside' and reinstate the "
        "fatal"
    )
    assert "more than one" in check_cell, (
        "Check 18(b) must state what happens when more than one real "
        "(non-fenced) `## Open Questions` heading exists -- a malformed "
        "plan -- mirroring check_open_questions.py's fail-loud handling "
        "of the same condition, rather than silently scanning against "
        "the first occurrence"
    )


def test_check18_resolved_entry_text_inside_section_is_excluded_too():
    """A `[RESOLVED]` (or `[OPEN]`) entry's own question/resolution text
    can legitimately contain a hedge word (e.g. "...was left open, now
    resolved: ...") without contradicting anything -- it is the
    section's own recorded history, not evidence contradicting an N/A
    declaration elsewhere. (Note: an entry and the pinned N/A line are
    mutually exclusive per plan-format.md's fill-or-declare rule -- this
    guards the in-section exclusion's WORDING against being scoped to
    only the N/A line's literal characters, which would still misfire if
    ever read alongside entry text, e.g. during a future schema change.)
    Pins that the in-section exclusion explicitly covers ENTRY text too,
    not just the pinned N/A line -- a narrower fix scoped only to the
    N/A line's literal characters would not satisfy this. Would fail if
    the row's in-section exclusion mentioned only the N/A line and never
    named entries."""
    row = _norm(_check18_row(_text()))
    lower = row.lower()
    assert "[open]/[resolved]" in lower or "[resolved]/[open]" in lower, (
        "Check 18(b) must name OPEN/RESOLVED entries, not just the N/A "
        "line, as excluded when they occur inside the Open Questions "
        "section"
    )
    assert "question/resolution text" in lower, (
        "Check 18(b) must state which part of an entry is excluded -- "
        "its own question/resolution text -- so a reviewer knows exactly "
        "what not to grep"
    )
    assert "cannot contradict the section's own declaration" in lower, (
        "Check 18(b) must justify the entry-text exclusion: the "
        "section's own recorded entries cannot contradict the "
        "section's own declaration"
    )


def test_check18_uses_existing_needs_revision_vocabulary_not_new_label():
    """Task 6 acceptance: the failing verdict uses the file's EXISTING
    vocabulary (NEEDS_REVISION + gaps:), never a new severity label.
    Proves the verdict enum line is untouched (still exactly the
    two-valued PASS | NEEDS_REVISION) and that Check 18's own row
    introduces no new severity-label-shaped token. Would fail if Check
    18 had introduced e.g. a bespoke 'CRITICAL' or 'BLOCKER' token."""
    text = _text()
    verdict_line = next(
        line for line in text.splitlines() if line.strip().startswith("verdict:")
    )
    assert verdict_line.strip() == "verdict: PASS | NEEDS_REVISION", (
        "the verdict enum must remain exactly two-valued -- Check 18 "
        "must not introduce a new verdict token"
    )
    row = _check18_row(text)
    for banned in ("CRITICAL", "BLOCKER", "SEV-", "FAIL_HARD"):
        assert banned not in row, (
            f"Check 18 must not introduce the new severity-label-shaped "
            f"token {banned!r}"
        )
