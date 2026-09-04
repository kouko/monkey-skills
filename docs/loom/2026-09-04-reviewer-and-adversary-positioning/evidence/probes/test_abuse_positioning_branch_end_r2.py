"""Fix-round-2 adversarial probes for 2026-09-04-reviewer-and-adversary-positioning.

Written in the branch-end fix round by the resumed adversary (never an
implementer of any task in this change), against the two fix commits:

  9c47fb58  branch-end-02  reviewer.md positioning restates its output as a
                           claim the fix round confirms (79 words)
  bb7d3670  branch-end-01  adversary.md positioning claims a probe's own
                           artifact path and hands a cross-document count
                           to the reviewer (80 words, AT the cap)

A third file rather than an extension of
`test_abuse_positioning_branch_end.py`: that file's docstring is the closed
record of round 1 (what the wording used to permit, which mutants survived).
This round's scope is exactly the two fix deltas, so it gets its own record.

What each case pins is named in its docstring as `branch-end-01` or
`branch-end-02`. Word counts use `len(str.split())`, never `wc`.

Every mutation runs against a COPY under `tmp_path` with the SHIPPED test
module re-pointed at a mirrored tree (`module.REPO = <tmp root>`); the real
contract files are never edited. An adversary that has to change the artifact
to make an attack land has proved nothing.

## What this round attacked and what held

* branch-end-01, both halves present -- CLOSED, pinned by
  `test_adversary_paragraph_claims_artifact_path_and_hands_cross_document_away`.
* branch-end-01, the split stated as an ASSIGNMENT not a PERMISSION -- HELD.
  "is yours" / "is the reviewer's". Had the clause read "you may settle a
  probe's artifact path", the finding class would be unclaimed again, which
  is the exact cold-read failure bb7d3670 was written to close. Pinned by
  `test_adversary_split_is_an_assignment_not_a_permission`.
* branch-end-01, the paragraph sits AT 80 words -- the cap now binds with
  zero slack. Recorded, not a finding:
  `test_adversary_paragraph_sits_exactly_at_the_cap_so_one_more_word_is_red`.
* branch-end-02, the claim clause is contiguous -- HOLE FOUND, then closed
  here. The shipped guard asserts `"claim" in para` and `"fix round" in para`
  as two independent substring checks, so a paragraph saying "you claim
  nothing" in one sentence and naming "the fix round" in another satisfies
  it while stating the opposite of intent Proposed outcome 2.
  `test_shipped_claim_guard_is_satisfied_by_two_unrelated_mentions`
  reproduces the survival; `test_reviewer_claim_clause_is_contiguous`
  closes it. Severity nit -- the shipped text is correct today, and the
  probe is now the thing that keeps it correct.
* branch-end-02, the `claim` half of the shipped guard is VACUOUS -- second
  surviving mutant, found by running the mutation rather than reasoning
  about it. `assert "claim" in para` was already true before 9c47fb58,
  because the same paragraph has said "overclaim (said, not done)" since
  W1-01. Delete the clause word `claim` and the shipped guard stays green;
  only its `fix round` half does work. Recorded by
  `test_shipped_claim_half_of_the_guard_is_vacuous`, covered by the
  contiguity probe. Severity nit (test quality, not shipped text).
* Portability oracle -- my first hand-rolled `docs/` regex FALSE-POSITIVED on
  `docs/loom/KICKOFF-DEFAULTS.md`, an exempt protocol filename. Rewritten to
  call the shipped `check_contract_citations.find_banned_citations`, plus a
  poisoned-input assertion so a permissive oracle cannot fake the green.
* branch-end-02, the 80-word cap at its boundary -- HELD. 80 exactly passes,
  81 fails, against the shipped assertion itself.
* branch-end-02, the two properties the fix had to preserve while adding
  words (writes no probes; cites `command`/`artifact`, never a `result`) --
  HELD, each with its own mutation.
* portability (CLAUDE.md "Contract Citations") -- HELD. Neither paragraph,
  and neither whole contract body, cites a `docs/` path of this repo.

## Attempts that found nothing (recorded so this is an eval, not an anecdote)

* Non-ASCII / homoglyph smuggling: replacing the ASCII apostrophe in
  "reviewer's" with U+2019 would defeat the shipped substring guard. Not a
  finding -- the shipped file uses the ASCII form and `test_..._dies_when_...`
  proves the guard notices the change, so a homoglyph edit lands as a RED
  test, not a silent bypass.
* Ordering: nothing requires the adversary half to precede the reviewer half.
  Tried asserting order; it is style, not semantics, and asserting it would
  break on a legitimate rewrite. Dropped rather than shipped as a fake pin.
* Deleting the claim clause and checking the r1 suite: no r1 case reads the
  clause (it post-dates that file), so nothing there goes red. Expected, not
  a hole -- the shipped guard plus this file are the coverage.
"""

from __future__ import annotations

import importlib.util
import itertools
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[5]

REVIEWER_REL = "loom-code/agents/reviewer.md"
ADVERSARY_REL = "loom-code/agents/adversary.md"
REVIEWER = REPO_ROOT / REVIEWER_REL
ADVERSARY = REPO_ROOT / ADVERSARY_REL
SHIPPED = REPO_ROOT / "loom-code" / "scripts" / "test_review_station_text.py"

WORD_CAP = 80

_COUNTER = itertools.count()


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _shipped_module():
    """Import the SHIPPED guard module fresh, under a throwaway name.

    Fresh each call so a case can re-point `module.REPO` at a mirrored tree
    without leaking that into the next case. Driving the shipped assertions
    themselves -- rather than re-implementing them here -- is the whole point:
    a mutation test that re-implements its target proves nothing about the
    guard that actually ships.
    """
    name = f"_shipped_review_text_{next(_COUNTER)}"
    spec = importlib.util.spec_from_file_location(name, SHIPPED)
    assert spec and spec.loader, f"cannot import {SHIPPED}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _paragraph(path: Path) -> str:
    """The `You own` positioning paragraph, parsed the shipped way."""
    return _shipped_module()._you_own_paragraph(path.read_text(encoding="utf-8"))


def _mirror(tmp_path: Path, rel: str, text: str) -> Path:
    """Write `text` at `rel` under a fresh tmp root and return that root.

    The shipped module reads `REPO / "<rel>"` at call time, so re-pointing
    `module.REPO` here is enough to run a shipped assertion against a mutant.
    """
    root = tmp_path / f"tree{next(_COUNTER)}"
    out = root / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return root


def _with_mutated_paragraph(path: Path, replacement: str) -> str:
    """The whole file, with its positioning paragraph swapped out."""
    text = path.read_text(encoding="utf-8")
    para = _paragraph(path)
    return text.replace(para, replacement, 1)


def _drop(path: Path, token: str) -> str:
    """The whole file with `token` deleted once from the positioning paragraph.

    Only the paragraph is touched: deleting the token file-wide would hit
    unrelated prose and the mutation would stop being minimal.
    """
    para = _paragraph(path)
    assert re.search(re.escape(token), para, re.IGNORECASE), (
        f"{path.name} positioning paragraph does not contain {token!r}; the "
        "mutation would be a no-op and the case vacuous"
    )
    return _with_mutated_paragraph(
        path, re.sub(re.escape(token), "", para, count=1, flags=re.IGNORECASE)
    )


def _run_shipped(case: str, rel: str, mutated_text: str, tmp_path: Path) -> None:
    module = _shipped_module()
    module.REPO = _mirror(tmp_path, rel, mutated_text)
    getattr(module, case)()


# --------------------------------------------------------------------------
# branch-end-01 -- adversary.md claims the probe-artifact bookkeeping
# --------------------------------------------------------------------------


def test_adversary_paragraph_claims_artifact_path_and_hands_cross_document_away() -> None:
    """branch-end-01. BOTH halves, or the finding class is unowned again.

    The cold read failed because each single-role reader handed "the same
    artifact recorded under two spellings counted twice" to the OTHER role.
    Claiming the adversary half alone would leave the reviewer's reader still
    pointing here; disclaiming the cross-document half alone would leave this
    reader still pointing there. Both clauses are load-bearing, so both are
    asserted, and the disambiguator ("spelling or count") with them.
    """
    para = _paragraph(ADVERSARY)
    low = para.lower()
    assert "artifact path" in low, (
        "adversary positioning paragraph never names a probe's own artifact "
        "path; the class the cold read dropped is unclaimed"
    )
    assert "spelling" in low and "count" in low, (
        "adversary positioning paragraph claims an artifact path without "
        "saying its spelling or its count is what is being settled; the "
        "double-counted-artifact class is not recognisably covered"
    )
    assert "cross-document" in low, (
        "adversary positioning paragraph does not disclaim a cross-document "
        "count, so the reviewer's reader can still hand one here"
    )
    assert "reviewer's" in low, (
        "adversary positioning paragraph disclaims the cross-document count "
        "without naming who owns it; an unowned disclaimer is the original bug"
    )
    assert len(para.split()) <= WORD_CAP, (
        f"adversary positioning paragraph is {len(para.split())} words, over "
        f"the {WORD_CAP}-word cap"
    )


@pytest.mark.parametrize(
    "token",
    ["artifact path", "spelling", "cross-document", "reviewer's"],
    ids=["artifact-path", "spelling", "cross-document", "reviewers"],
)
def test_adversary_shipped_guard_dies_when_one_load_bearing_word_is_deleted(
    tmp_path: Path, token: str
) -> None:
    """branch-end-01, mutation sensitivity. GREEN = bb7d3670's guard bites.

    Delete exactly one load-bearing token from a COPY and require the SHIPPED
    guard to raise. A surviving mutant would mean the shipped assertion passes
    for reasons unrelated to the wording it claims to pin -- i.e. the fix
    could be reverted in that respect and CI would stay green.

    "spelling" is included deliberately: the shipped guard does NOT assert it,
    so this parametrisation would surface that as a survivor if the local
    case above were not the thing carrying it.
    """
    mutated = _drop(ADVERSARY, token)
    module = _shipped_module()
    module.REPO = _mirror(tmp_path, ADVERSARY_REL, mutated)
    case = module.test_adversary_agent_paragraph_owns_probe_artifact_bookkeeping
    if token == "spelling":
        case()  # documented survivor: the shipped guard never reads it
        with pytest.raises(AssertionError):
            _local_adversary_case(mutated)
        return
    with pytest.raises(AssertionError):
        case()


def _local_adversary_case(text: str) -> None:
    """The branch-end-01 assertions above, applied to arbitrary text.

    Kept private and duplicated-by-parameter rather than refactored into the
    public case: the public case must read the real file with no seam an
    argument could redirect.
    """
    para = _shipped_module()._you_own_paragraph(text).lower()
    assert "artifact path" in para
    assert "spelling" in para and "count" in para
    assert "cross-document" in para
    assert "reviewer's" in para


def test_adversary_split_is_an_assignment_not_a_permission() -> None:
    """branch-end-01, self-exempt class. HELD.

    A permission ("you MAY settle a probe's artifact path") leaves the class
    unowned exactly as before -- a reader who declines is still compliant.
    The clause must ASSIGN: `is yours` / `is the reviewer's`. Also refuses a
    hedge inside the new clause specifically (the r1 file checks the whole
    paragraph; this checks the sentence bb7d3670 added).
    """
    para = _paragraph(ADVERSARY)
    clause = para[para.lower().index("artifact path") :]
    assert re.search(r"\bis yours\b|\byours\b", clause, re.IGNORECASE), (
        "the artifact-path clause does not say the path is the adversary's; "
        "an unassigned mention is what the cold read already failed on"
    )
    assert re.search(r"\bis the reviewer's\b|\breviewer's\b", clause), (
        "the clause does not assign the cross-document count to the reviewer"
    )
    for hedge in ("may ", "can ", "might ", "should usually", "where possible"):
        assert hedge not in clause.lower(), (
            f"the artifact-path clause hedges with {hedge!r}; a split an "
            "actor may decline is not a split"
        )


def test_adversary_paragraph_sits_exactly_at_the_cap_so_one_more_word_is_red(
    tmp_path: Path,
) -> None:
    """branch-end-01, boundary. 80 passes; 81 -- one added word -- fails.

    bb7d3670 landed AT the cap, so the next edit to this paragraph has zero
    slack. Recorded as a fact rather than a finding: the cap is a real
    constraint and the guard enforces it at the boundary, both directions.
    """
    para = _paragraph(ADVERSARY)
    assert len(para.split()) == WORD_CAP, (
        f"adversary positioning paragraph is {len(para.split())} words, not "
        f"{WORD_CAP}; this boundary case's premise moved (still fine if <= "
        f"{WORD_CAP}, but re-read the slack claim in the docstring)"
    )
    _run_shipped(
        "test_adversary_agent_paragraph_owns_probe_artifact_bookkeeping",
        ADVERSARY_REL,
        ADVERSARY.read_text(encoding="utf-8"),
        tmp_path,
    )
    over = _with_mutated_paragraph(ADVERSARY, para + " furthermore")
    with pytest.raises(AssertionError):
        _run_shipped(
            "test_adversary_agent_paragraph_owns_probe_artifact_bookkeeping",
            ADVERSARY_REL,
            over,
            tmp_path,
        )


# --------------------------------------------------------------------------
# branch-end-02 -- reviewer.md output lands as a claim the fix round confirms
# --------------------------------------------------------------------------


def test_reviewer_claim_clause_is_contiguous() -> None:
    """branch-end-02. The clause must be ONE statement, not two words nearby.

    Intent Proposed outcome 2 asks the paragraph to say the reviewer's output
    IS a claim THE FIX ROUND CONFIRMS. `claim ... fix round ... confirms` in
    that order inside one clause is the checkable form of that sentence;
    two independent substring hits are not (see the survival case below).
    """
    para = " ".join(_paragraph(REVIEWER).split())
    assert re.search(r"claim[^.]{0,40}fix round[^.]{0,20}confirms?", para), (
        "reviewer positioning paragraph does not state, in one clause, that "
        "its output lands as a claim the fix round confirms"
    )


def test_shipped_claim_guard_is_satisfied_by_two_unrelated_mentions(
    tmp_path: Path,
) -> None:
    """branch-end-02, the SURVIVING mutant -- a documented coverage hole.

    9c47fb58's guard is `"claim" in para` and `"fix round" in para`, two
    independent checks. A paragraph that says "you claim nothing" and
    separately mentions "the fix round" passes it while asserting the exact
    opposite of the requirement. This case asserts the survival, so the hole
    is a fact rather than an opinion; `test_reviewer_claim_clause_is_contiguous`
    is the probe that closes it. Severity nit: the shipped text is correct
    today, and this pair is what keeps it correct.
    """
    decoy = (
        "You own reconciliation in this flow: whether what was delivered "
        "matches what the intent promised. You claim nothing about running "
        "code. The fix round is elsewhere. You write no probes."
    )
    _run_shipped(
        "test_reviewer_agent_paragraph_names_output_as_claim_fix_round_confirms",
        REVIEWER_REL,
        _with_mutated_paragraph(REVIEWER, decoy),
        tmp_path,
    )  # survives -- that is the hole

    flat = " ".join(
        _shipped_module()
        ._you_own_paragraph(_with_mutated_paragraph(REVIEWER, decoy))
        .split()
    )
    assert not re.search(r"claim[^.]{0,40}fix round[^.]{0,20}confirms?", flat), (
        "the contiguity probe accepts the decoy too, so it closes nothing"
    )


def test_reviewer_shipped_guard_dies_when_fix_round_is_cut(tmp_path: Path) -> None:
    """branch-end-02, mutation sensitivity. GREEN = half the guard bites.

    Delete `fix round` from a copy; the shipped guard must raise. Without
    this, the guard could be passing on prose elsewhere in the block.
    """
    with pytest.raises(AssertionError):
        _run_shipped(
            "test_reviewer_agent_paragraph_names_output_as_claim_fix_round_confirms",
            REVIEWER_REL,
            _drop(REVIEWER, "fix round"),
            tmp_path,
        )


def test_shipped_claim_half_of_the_guard_is_vacuous(tmp_path: Path) -> None:
    """branch-end-02, the SECOND surviving mutant. A vacuous half-assertion.

    9c47fb58's `assert "claim" in para` was ALREADY satisfied before the fix:
    the same paragraph has said "overclaim (said, not done)" since W1-01, and
    `"claim" in "overclaim"` is True. So deleting the whole clause word
    `claim` leaves that half of the guard green -- it never tested anything.
    Only the `fix round` half above does real work. This case asserts the
    survival so the vacuity is a recorded fact; the contiguity probe is what
    actually covers the requirement. Severity nit (test quality, not text).
    """
    text = REVIEWER.read_text(encoding="utf-8")
    para = _paragraph(REVIEWER)
    assert "overclaim" in para, (
        "the paragraph no longer says `overclaim`, so this vacuity premise "
        "moved -- re-read whether the shipped `claim` check now bites"
    )
    stripped = re.sub(r"\bclaim\b", "", para, count=1)
    assert "claim" in stripped, "word-boundary deletion did not leave overclaim"
    _run_shipped(
        "test_reviewer_agent_paragraph_names_output_as_claim_fix_round_confirms",
        REVIEWER_REL,
        text.replace(para, stripped, 1),
        tmp_path,
    )  # survives -- the `claim` half asserts nothing

    flat = " ".join(stripped.split())
    assert not re.search(r"claim[^.]{0,40}fix round[^.]{0,20}confirms?", flat), (
        "the contiguity probe accepts the clause-less text too"
    )


@pytest.mark.parametrize("n_words", [WORD_CAP, WORD_CAP + 1], ids=["at-80", "at-81"])
def test_reviewer_word_cap_binds_exactly_at_the_boundary(
    tmp_path: Path, n_words: int
) -> None:
    """branch-end-02, boundary. 80 exactly passes; 81 fails. Same oracle.

    9c47fb58 bought its new clause by compressing the citation sentence, so
    the cap is the constraint the fix had to live inside. A cap asserted only
    at 79 words is a cap nobody has watched refuse anything: this drives the
    SHIPPED assertion with a synthetic paragraph of each length, counted the
    shipped way (`len(str.split())`).
    """
    head = ["You", "own", "a", "claim", "the", "fix", "round", "confirms"]
    synthetic = " ".join(head + ["word"] * (n_words - len(head)))
    assert len(synthetic.split()) == n_words, "synthetic paragraph miscounted"

    def _go() -> None:
        _run_shipped(
            "test_reviewer_agent_paragraph_names_output_as_claim_fix_round_confirms",
            REVIEWER_REL,
            _with_mutated_paragraph(REVIEWER, synthetic),
            tmp_path,
        )

    if n_words <= WORD_CAP:
        _go()
    else:
        with pytest.raises(AssertionError):
            _go()


def test_reviewer_paragraph_still_writes_no_probes() -> None:
    """branch-end-02, regression. The clause was added under a word cap, so
    the risk is that something else was dropped to make room. This is the
    first of the two properties that had to survive the compression.
    """
    para = _paragraph(REVIEWER)
    assert re.search(r"write[s]? no probes", para), (
        "reviewer positioning paragraph no longer says it writes no probes; "
        "the fix bought its claim clause by dropping the boundary"
    )
    assert re.search(r"adversary", para), (
        "reviewer positioning paragraph no longer routes runnable work to "
        "the adversary, so 'writes no probes' names no destination"
    )


def test_reviewer_citation_is_command_and_artifact_never_a_result() -> None:
    """branch-end-02, regression -- the second property the fix had to keep.

    The `tests` dimension paragraph in the same file says a reviewer cites a
    probe record's command, never its `result`. If the compression had
    reintroduced `result` here, the file would contradict itself again --
    the round-1 finding that `test_reviewer_result_citation_...` closed.
    """
    para = _paragraph(REVIEWER)
    assert "`command`" in para and "`artifact`" in para, (
        "reviewer positioning paragraph no longer names both citable fields"
    )
    assert "result" not in para.lower(), (
        "reviewer positioning paragraph mentions a probe `result`, "
        "contradicting the `tests` dimension rule in the same file"
    )
    assert "probes[]" in para, (
        "reviewer positioning paragraph cites no checkable record"
    )


# --------------------------------------------------------------------------
# portability -- CLAUDE.md "Contract Citations", both fix deltas
# --------------------------------------------------------------------------


def _citation_checker():
    name = f"_cite_{next(_COUNTER)}"
    path = REPO_ROOT / "loom-code" / "scripts" / "check_contract_citations.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot import {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "path", [REVIEWER, ADVERSARY], ids=["reviewer", "adversary"]
)
def test_neither_contract_cites_a_docs_path_of_this_repo(path: Path) -> None:
    """Portability, CLAUDE.md "Contract Citations". A dispatched agent reads
    the repo it is standing in, so a citation of one of THIS repo's records
    only resolves here.

    The oracle is the shipped checker's own `find_banned_citations`, not a
    regex written here: a hand-rolled rule would be a second drift surface,
    and my first attempt at one produced a false positive on
    `docs/loom/KICKOFF-DEFAULTS.md`, which is an exempt protocol filename.

    Checked over the whole contract body, not just the edited paragraph: both
    fix commits could have reached for the cold-read evidence by path
    (`evidence/coldread-*.txt` is named in bb7d3670's message) and neither did.
    """
    checker = _citation_checker()
    text = path.read_text(encoding="utf-8")
    bad = checker.find_banned_citations(text)
    assert not bad, (
        f"{path.name} cites this repository's development records {bad}; a "
        "runtime prose contract must stay portable."
    )
    # The oracle bites: a real record path in the same file is caught.
    poisoned = text + "\nSee `docs/loom/2026-09-04-reviewer-and-adversary-positioning/spec.md`.\n"
    assert checker.find_banned_citations(poisoned), (
        "the citation checker accepts a dated record path, so the green "
        "result above proves nothing"
    )
