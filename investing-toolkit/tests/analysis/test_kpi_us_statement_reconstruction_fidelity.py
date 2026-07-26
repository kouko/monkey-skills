"""Plan Task 10 — the arc's real acceptance: does the reconstruction match the
FILED DOCUMENT, line for line?
(docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md)

WHAT EVERY GREEN TEST BEFORE THIS ONE LEAVES UNPROVEN. Task 4 verifies every
declared sum in `Decimal`; Task 3 counts KO FY2017's income statement to 26
lines. Both check the filing against ITSELF. Neither can see:

  * lines OUTSIDE every sum — KO's six per-share rows and three share-count
    rows carry `weight=None` and no calculation parent, so no sum check
    reaches them; a pipeline that dropped all nine would still reconcile 100%;
  * ORDER — Sigma(child x weight) is commutative, so a shuffled statement sums
    identically to a correct one;
  * LABELS — the sums never read a label, and the brief's own §Series identity
    proves labels move independently of the concepts the arithmetic uses.

Those three are exactly what a human reads. The oracle is therefore the filing
itself: `../data/fixtures/ko_fy2017_income_statement_as_filed.json`, a hand
transcription of accession 0000021344-18-000008. Its `_transcription` block
records how it was obtained and how a reader re-verifies it by eye.

WHAT THE ORACLE MEASURED, stated here because it is the finding and not a
footnote: THE FILER FILED THE STATEMENT TWICE AND THE TWO DO NOT AGREE. The
printed 10-K page and the XBRL exhibit of the same accession differ on 15 of
the 26 labels and transpose three lines. This repo reconstructs the EXHIBIT
faithfully — SEC's own renderer of that exhibit agrees with it byte for byte on
all 26 labels and their order — so the divergence is the filer's, not ours.
That distinction is what Task 10 buys, and neither sum reconciliation nor the
printed page alone could have produced it. The brief's phrase "each line
carrying the filer's own label" therefore needs its exception named in the same
breath: the filer's own XBRL label, which for 15 of these 26 lines is NOT the
label the filer printed.

WHY THIS IS NOT A CONSTRUCTION-GUARANTEED INVARIANT
(docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md): the
transcription was read off the FILED DOCUMENTS, never generated from
`statements_for`, `is_statement_line`, `statement_kind` or the committed row
capture. The two sides share only the filing. An oracle produced by the code
under test would prove only that the code agrees with itself, and a FABRICATED
oracle would be worse than none at all.

THE SUITE IS OFFLINE. The reconstruction side reads the committed capture
`us_statement_reconstruction_2026-07-26.json`; the oracle side reads the
committed transcription. Fetching the filed documents was a one-time act,
reproducible through `capture_ko_fy2017_income_as_filed.py`, never a test-time
call.

THE ACCEPTANCE'S OWN SENSITIVITY IS TESTED, not asserted: the three mutations
the plan names — a leaked dimensional row, a dropped line, a reordering — are
each applied to the reconstruction and each must fail. A guard nobody mutated
is a guard nobody verified, and mutation is the only technique in this arc that
has caught a defect all 1278 tests passed over.
"""
from __future__ import annotations

import json
from decimal import Decimal

import pytest
from conftest import SKILLS

# The offline doubles and the capture accessor live in Task 3's suite and are
# imported rather than copied: they stand in for the LIVE edgartools surface,
# and a second copy could drift away from that surface while staying green —
# invisibly, because both copies would be ours. A rename there breaks this
# import loudly, which is the intended failure.
from test_kpi_us_statement_shape import (  # noqa: F401  (fixtures used by name)
    _CapturedFiling,
    _captured_filing,
    reconstruction_capture,
    shape,
)

KO_FY2017 = "0000021344-18-000008"

# Both documents head three comparative columns, in this order.
YEARS = ("2017", "2016", "2015")

_SCALE = {
    # Each document's own scale header: "(In millions except per share data)"
    # on the printed page, "shares in Millions, $ in Millions" on SEC's.
    "millions_usd": Decimal(10) ** 6,
    "millions_shares": Decimal(10) ** 6,
    "usd_per_share": Decimal(1),
}


@pytest.fixture(scope="module")
def as_filed():
    fixture = (
        SKILLS.parent / "tests" / "data" / "fixtures"
        / "ko_fy2017_income_statement_as_filed.json"
    )
    return json.loads(fixture.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def reconstructed(shape, reconstruction_capture):
    """KO FY2017's income statement as THIS repo reconstructs it."""
    filing = _CapturedFiling(_captured_filing(reconstruction_capture, KO_FY2017))
    return shape.statements_for(filing).by_kind["income"]


# LABELS ARE COMPARED VERBATIM — no case folding, no dash folding, no
# whitespace normalisation. An earlier draft of this module normalised
# whitespace, on the reasoning that a difference a reader cannot see is not a
# fidelity defect. The reasoning is sound; the concession was unmeasured, and
# measuring it retired it. Of the 80 rows in KO's captured income role exactly
# ONE label carries doubled whitespace (`CCBA  [Domain]`), and it is a
# dimensional row that never reaches a statement line — so the normalisation
# protected nothing while silently widening what could pass. If a filer's label
# ever does differ from the printed page only in whitespace, this test fails
# and a human decides that case with the evidence in front of them, which
# beats granting the concession in advance to a case nobody has seen.
#
# Case and dashes are load-bearing, not incidental: KO prints its subtotals in
# capitals and its components in sentence case, and the printed page's em dash
# against the exhibit's ASCII hyphen is one of the measured divergences below.
# Folding either would erase evidence this test exists to surface.


def _figure(raw) -> Decimal | None:
    """One cell as a `Decimal`, or `None` when it holds no number. Via `str`,
    never `Decimal(float)` — this module family has already manufactured a
    false restatement that way
    (docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md)."""
    if raw is None or isinstance(raw, bool) or not isinstance(raw, (int, float)):
        return None
    return Decimal(str(raw))


def _transcribed_rows(lines) -> list[tuple]:
    """A transcription as (label, 2017, 2016, 2015), scaled by the unit the
    document's own header declares. A cell transcribed `null` — an em dash on
    the page — stays `None`; the transcription records the blank and claims
    nothing about why it is blank."""
    rows = []
    for line in lines:
        factor = _SCALE[line["unit"]]
        rows.append((
            line["label"],
            tuple(
                None if line["values"][year] is None
                else Decimal(str(line["values"][year])) * factor
                for year in YEARS
            ),
        ))
    return rows


def _reconstructed_rows(lines, period_keys) -> list[tuple]:
    return [
        (
            line.label or "",
            tuple(_figure(line.values.get(period_keys[year])) for year in YEARS),
        )
        for line in lines
    ]


def _at(rows: list[tuple], index: int):
    return rows[index] if index < len(rows) else None


def _unaccounted_differences(as_filed, built: list[tuple]) -> list[str]:
    """Every position where the reconstruction matches NEITHER the printed page
    NOR the filer's own XBRL exhibit — i.e. every difference this repo, rather
    than the filer, is responsible for.

    Positional, not set-based, and that is the point: a reordering leaves both
    sides holding the same lines, so any comparison that sorted or matched by
    label would call a shuffled statement identical.

    Accepting a difference the EXHIBIT explains is the one concession here, and
    it is bounded by `test_the_reconstruction_is_byte_identical_to_sec_s_own_
    rendering_of_the_exhibit`: the exhibit side is not this repo's word for
    what the filer declared, it is SEC's independent rendering of it. Without
    that test this concession would be a blindfold.
    """
    printed = _transcribed_rows(as_filed["lines"])
    exhibit = _transcribed_rows(as_filed["sec_rendered_lines"])
    differences = []
    for index in range(max(len(printed), len(exhibit), len(built))):
        actual = _at(built, index)
        if actual == _at(printed, index) or actual == _at(exhibit, index):
            continue
        differences.append(
            f"line {index + 1}:\n"
            f"    printed page   {_at(printed, index)!r}\n"
            f"    filer exhibit  {_at(exhibit, index)!r}\n"
            f"    reconstructed  {actual!r}"
        )
    return differences


def test_reconstructed_statement_matches_the_filed_document_line_for_line(
    as_filed, reconstructed,
):
    """The plan's RED for Task 10. Every line of KO's FY2017 income statement,
    at its own position, under a label the filer filed for it, with the numbers
    the filer filed beside it in each of the three comparative columns.

    The per-share and share-count rows are the load-bearing half: they sit
    outside every declared sum, so this is the only test in the arc that can
    notice if they go missing or arrive scrambled.

    "A label the filer filed" and not "the label the filer printed", because
    the two are not the same string for 15 of these 26 lines and no code can
    reconcile them — the exception is pinned line by line in
    `test_the_divergence_between_the_two_filed_renderings_is_pinned`, and the
    exhibit side is corroborated by SEC's own renderer in the test below.
    """
    period_keys = as_filed["_transcription"]["period_keys"]
    built = _reconstructed_rows(reconstructed, period_keys)

    assert len(as_filed["lines"]) == as_filed["_transcription"]["line_count"] == 26

    # The per-line report comes FIRST and the count second, deliberately: a
    # dropped or leaked line trips both, and "line 26 reconstructed as None" is
    # the message that says WHICH line, where "25 != 26" only says how many.
    differences = _unaccounted_differences(as_filed, built)
    assert not differences, (
        f"{len(differences)} line(s) match neither of the filer's own two "
        f"renderings of this statement "
        f"({as_filed['_transcription']['printed_page_url']}):\n"
        + "\n".join(differences)
    )
    assert len(built) == 26, (
        f"the printed statement has 26 lines; the reconstruction has {len(built)}"
    )


def test_the_reconstruction_is_byte_identical_to_sec_s_own_rendering_of_the_exhibit(
    as_filed, reconstructed,
):
    """The independent corroboration, and the reason the test above may accept
    a difference from the printed page at all.

    SEC's financial-report renderer is a SECOND implementation, written by
    someone else, reading the same XBRL exhibit this repo reads. Agreement on
    all 26 labels, their order and their figures says this repo's extraction
    adds no error of its own — which is precisely what the printed page CANNOT
    say, since a difference against it could equally be our defect or the
    filer's own divergence.

    It corroborates the extraction; it does NOT stand in for the printed page.
    Two renderers of one exhibit can only agree about the exhibit.
    """
    period_keys = as_filed["_transcription"]["period_keys"]
    assert (
        _reconstructed_rows(reconstructed, period_keys)
        == _transcribed_rows(as_filed["sec_rendered_lines"])
    )


def test_the_divergence_between_the_two_filed_renderings_is_pinned(as_filed):
    """The finding itself, pinned so it cannot quietly change size.

    MEASURED 2026-07-26 on accession 0000021344-18-000008: the filer's printed
    page and the filer's XBRL exhibit disagree on 15 of 26 labels, transpose 3
    lines, and print a blank against a tagged 0 in 6 cells. Every other figure
    is identical — no number the filer printed is missing from, or altered in,
    the exhibit this repo reconstructs, which is the reassurance a reader
    actually needs.

    WHAT THIS TEST GUARDS, narrowed to what it earns: it reads the two
    TRANSCRIPTIONS and nothing else — it never takes `reconstructed`. So it
    guards the fixture, not the pipeline: it fails if either transcription is
    hand-edited, if a fourth divergence CLASS appears, or if a known one grows,
    shrinks or moves. A change on the PIPELINE side is caught one test up, by
    `test_the_reconstruction_is_byte_identical_to_sec_s_own_rendering_of_the_
    exhibit`, and the two together are what make a fix loud: the pipeline can
    only stop matching the exhibit there, and the exhibit can only stop
    diverging from the page here.

    An earlier version of this docstring claimed the test fails "if the
    divergence is ever FIXED", which would require watching the reconstruction
    it never receives. Corrected rather than quietly deleted: a claim written
    wider than the code earns is the defect this arc has now met nine times,
    and it landed here, in the test whose whole subject is two claims that
    disagree.
    """
    printed = {line["order"]: line for line in as_filed["lines"]}
    exhibit = as_filed["sec_rendered_lines"]

    transposed = [
        line["order"] for line in exhibit if line["printed_order"] != line["order"]
    ]
    relabelled = [
        line["printed_order"] for line in exhibit
        if line["label"] != printed[line["printed_order"]]["label"]
    ]
    blank_against_zero = [
        (line["printed_order"], year)
        for line in exhibit for year in YEARS
        if printed[line["printed_order"]]["values"][year] is None
        and line["values"][year] == 0
    ]
    altered = [
        (line["printed_order"], year)
        for line in exhibit for year in YEARS
        if printed[line["printed_order"]]["values"][year] is not None
        and printed[line["printed_order"]]["values"][year] != line["values"][year]
    ]
    # THE FOURTH BUCKET, and the reason the other three are not a partition:
    # `blank_against_zero` requires the tagged figure to be exactly 0 and
    # `altered` requires the printed figure to be present, so a cell the page
    # leaves BLANK against a NON-ZERO tagged figure falls through both and
    # could grow unseen. It is the worst of the four — a number that exists in
    # the exhibit a reader never saw on the page — so it gets its own list
    # rather than an assumption that it cannot happen.
    blank_against_a_figure = [
        (line["printed_order"], year)
        for line in exhibit for year in YEARS
        if printed[line["printed_order"]]["values"][year] is None
        and line["values"][year] not in (None, 0)
    ]

    # The subtotal CONSOLIDATED NET INCOME (printed 15) sits BEFORE the two
    # components the printed page puts above it (13, 14).
    assert transposed == [13, 14, 15]
    assert relabelled == [9, 10, 11, 12, 14, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    assert blank_against_zero == [
        (14, "2016"), (14, "2015"),
        (19, "2016"), (19, "2015"),
        (22, "2016"), (22, "2015"),
    ]
    assert altered == [], (
        "a figure the filer PRINTED differs from the one it TAGGED — that is a "
        "restatement between two documents of one filing, not a label quirk"
    )
    assert blank_against_a_figure == [], (
        "the printed page leaves a cell BLANK where the exhibit tags a non-zero "
        "figure — a number that reaches the reconstruction but that no reader of "
        "the 10-K ever saw"
    )


# --- the acceptance's own sensitivity, verified by mutation -----------------
# The plan's RED names three ways the reconstruction could be wrong while every
# declared sum still reconciles. Each is applied to the reconstruction below
# and each must be caught. They prove the ACCEPTANCE CHECK is sensitive, which
# is the only claim they make; that the pipeline is correct is what the tests
# above prove.


def _leaked_dimensional_row(shape, capture):
    """A REAL segment slice from KO's captured income role, projected onto a
    `Line` exactly as assembly would if `is_statement_line` ever let it
    through. Not a hand-made stand-in: a leak renders as a plausible line with
    a plausible label, and only a real row has that property."""
    rows = next(
        entry["rows"] for entry in _captured_filing(capture, KO_FY2017)["roles_captured"]
        if shape.statement_kind(entry["role"]) == "income"
    )
    return shape._line(next(row for row in rows if row.get("full_dimension_label")))


def test_a_leaked_dimensional_row_fails_the_acceptance(
    shape, as_filed, reconstructed, reconstruction_capture,
):
    period_keys = as_filed["_transcription"]["period_keys"]
    leaked = list(reconstructed)
    leaked.insert(1, _leaked_dimensional_row(shape, reconstruction_capture))

    assert _unaccounted_differences(
        as_filed, _reconstructed_rows(leaked, period_keys)
    ), "a leaked segment slice must not pass as a statement line"


def test_a_dropped_line_fails_the_acceptance(as_filed, reconstructed):
    period_keys = as_filed["_transcription"]["period_keys"]
    # The LAST line — what a truncation loses first, and one no sum check
    # reaches (the diluted share count has no calculation parent), so nothing
    # else in this arc would notice it go.
    dropped = list(reconstructed)[:-1]

    assert _unaccounted_differences(
        as_filed, _reconstructed_rows(dropped, period_keys)
    ), "a dropped statement line must fail the acceptance"


def test_a_reordering_fails_the_acceptance(as_filed, reconstructed):
    period_keys = as_filed["_transcription"]["period_keys"]
    # ADJACENT lines swapped: the hardest reordering to see, and the one a set-
    # or label-keyed comparison would miss entirely.
    reordered = list(reconstructed)
    reordered[1], reordered[2] = reordered[2], reordered[1]

    assert _unaccounted_differences(
        as_filed, _reconstructed_rows(reordered, period_keys)
    ), "a reordered statement must fail the acceptance"
