"""test_silent_arithmetic_guards.py — the calculations that fail quietly.

A sampled mutation pass over the US SEC lanes (180 mutants, 2026-07-27) left
45 survivors. This file pins the subset whose failure mode is the worst kind
for a longitudinal dataset: **they do not raise, they return a wrong number**.
A sign flip on an age computation, an inverted restatement test, or a
mis-placed table cell produces a plausible figure that flows all the way to a
rendered tearsheet.

Each test below corresponds to one surviving mutant and states which one.
They pass on first run — the behaviour is already correct — so the
discriminator is the mutant, not a red bar (verified: see the paired
mutation check in the branch's commit message).
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"

if "requests" not in sys.modules:  # module-level `import requests` runs on import
    sys.modules["requests"] = mock.MagicMock(name="requests")
if str(MARKETS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MARKETS_SCRIPTS))

import exhibit_tables  # noqa: E402
import pack_us  # noqa: E402
import sec_edgar_client as sec  # noqa: E402


# ---------------------------------------------------------------------------
# Mutant: sec_edgar_client.py:173  `now - ref` -> `now + ref`
# ---------------------------------------------------------------------------

def test_staleness_is_the_age_of_the_data_not_a_sum_of_two_dates():
    """`staleness_days` feeds cache-cadence decisions. Adding the two
    datetimes instead of subtracting yields a plausible-looking positive
    integer in the tens of thousands, so nothing downstream raises — the
    provenance block simply reports a filing from 2020 as ~740 centuries old.
    """
    prov = sec._make_provenance("2020-01-15")

    staleness = prov["staleness_days"]
    assert isinstance(staleness, int)
    # A 2020 reference read any time this decade is a few thousand days old.
    assert 0 < staleness < 10_000, (
        f"staleness_days={staleness} is not an age; a sign flip on the "
        "subtraction produces a value in this shape"
    )


def test_staleness_is_none_when_no_reference_period_is_given():
    assert sec._make_provenance()["staleness_days"] is None


# ---------------------------------------------------------------------------
# Mutant: sec_edgar_client.py:4046  a `12` in `_WEEK_QUARTER_STRUCTURES`
# ---------------------------------------------------------------------------

def test_week_quarter_offsets_stay_pinned_to_both_observed_filer_families():
    """`_WEEK_QUARTER_STRUCTURES` is declared as the SINGLE SOURCE for the
    week-offset allowlist, and a hand-typed offset table previously drifted
    from it (the Task-2 round-2 finding cited at the constant). Nothing pinned
    the derived result, so a week count could change silently.

    NOTE on what this can and cannot catch, enumerated exhaustively over all
    32 single-element ±1 mutations rather than reasoned from one row:

      - **Element 0 (Q1's own length) is equivalent in all four structures.**
        Q1's length is never read: the offsets are Q3 = Q4, Q2 = Q4 + Q3,
        Q1 = Q4 + Q3 + Q2.
      - **Element 1 (Q2) is equivalent in only TWO of the four** — this test
        kills it in `(13,13,13,13)` and `(12,12,12,17)`. A mutation both ADDS
        a new offset and REMOVES that structure's original contribution, and
        those two structures are the sole contributors of Q1 offsets 39 and 41
        respectively, so the derived set changes. In `(13,13,13,14)` and
        `(12,12,12,16)` the new value collides with an offset another family
        already supplies AND the old value is likewise still supplied, so the
        set is unchanged.
      - Elements 2 and 3 always change the offsets.

    Recorded at this precision because an earlier revision of this docstring
    generalised the single row it had tested to "each tuple" and declared four
    unkillable mutants where there are five. A reader who dismissed a future
    survivor at :4044 or :4047 on that basis would be dismissing a real one.
    """
    offsets = sec._compute_week_quarter_offsets(sec._WEEK_QUARTER_STRUCTURES)

    assert offsets == {
        "Q1": (39, 40, 41),
        "Q2": (26, 27, 28, 29),
        "Q3": (13, 14, 16, 17),
    }, "the derived week-offset allowlist changed"


# ---------------------------------------------------------------------------
# Mutant: exhibit_tables.py:156  `occupied.add((r + dr, c + dc))` -> `c - dc`
#
# ONLY the third test below kills that mutant. The first two are regression
# guards for `_anchor_cells` generally (five other single-line mutants of the
# function kill them) but they CANNOT discriminate the reservation's
# direction — see the third test's docstring for why. Stated here, at the
# header a scanner reads, so neither is mistaken for closing this gap.
# ---------------------------------------------------------------------------

def _cell(text, colspan=1, rowspan=1):
    return {"text": text, "colspan": colspan, "rowspan": rowspan}


def test_a_colspan_reserves_the_cells_to_its_right_not_to_its_left():
    """Grid placement is what keeps a KPI's column coordinate faithful to the
    rendered table. Reserving cells to the LEFT of an anchor leaves the real
    span free, so the next cell lands inside its predecessor and every value
    after it shifts — a table that parses cleanly into wrong columns."""
    rows = [[_cell("A", colspan=2), _cell("B")]]

    anchors = exhibit_tables._anchor_cells(rows)

    assert anchors == [(0, 0, "A"), (0, 2, "B")], (
        f"'B' must start at column 2, after A's two-column span: {anchors}"
    )


def test_a_rowspan_pushes_the_next_row_right_by_the_reserved_width():
    """The rowspan half of the same guard: a cell spanning two rows must
    reserve its column in the row below, so that row's first cell shifts."""
    rows = [
        [_cell("hdr", rowspan=2), _cell("r0c1")],
        [_cell("r1c1")],
    ]

    anchors = exhibit_tables._anchor_cells(rows)

    assert anchors == [(0, 0, "hdr"), (0, 1, "r0c1"), (1, 1, "r1c1")], (
        f"row 1's cell must shift past the rowspan reservation: {anchors}"
    )


def test_a_cell_spanning_both_axes_reserves_its_full_width_in_the_next_row():
    """The ONLY shape that discriminates the reservation's direction, and the
    reason the two tests above do not:

      - colspan alone never consults `occupied` — the column pointer advances
        by `c += cs` regardless, so a wrong reservation changes nothing;
      - rowspan alone reserves at `dc == 0`, where `c + dc` and `c - dc` are
        arithmetically the same cell.

    Only a cell spanning BOTH axes reserves at `dc > 0` in a row that later
    reads `occupied`. Reserving leftward there leaves the real span free, so
    the next row's first cell lands one column early and every value in that
    row is attributed to its neighbour's column — a table that parses cleanly
    into the wrong columns. Found because a mutation run reported this file's
    other two tests as killing the mutant when they provably cannot.
    """
    rows = [
        [_cell("wide-tall", colspan=2, rowspan=2)],
        [_cell("below")],
    ]

    anchors = exhibit_tables._anchor_cells(rows)

    assert anchors == [(0, 0, "wide-tall"), (1, 2, "below")], (
        f"'below' must clear both reserved columns and start at 2: {anchors}"
    )


# ---------------------------------------------------------------------------
# Mutant: pack_us.py:431  `prev != obs` -> `prev == obs` (amendment detection)
# ---------------------------------------------------------------------------

def _obs(end, value, filed, form="10-K"):
    return {"end": end, "val": value, "value": value, "filed": filed,
            "form": form, "start": f"{int(end[:4])}-01-01", "fy": int(end[:4]),
            "fp": "FY"}


def _two_concept_raw(first_value, second_value):
    """One fiscal year supplied by TWO concepts of the revenue chain.

    The cross-concept collision is the only way to reach this comparison:
    `_select_annual_observations` already dedups by end-date WITHIN a
    concept (pack_us.py:352-366), so a single concept filing the same year
    twice never reaches `_normalize_dcf`'s own merge loop. An issuer
    switching concepts mid-history (the ASC 606 transition the function's
    docstring cites) is exactly this shape.
    """
    primary, secondary = pack_us.DCF_CONCEPT_MAPPING["revenue"][:2]
    return {
        primary: {"observations": [_obs("2023-12-31", first_value, "2024-02-01")]},
        secondary: {"observations": [_obs("2023-12-31", second_value, "2025-02-01")]},
    }


def test_a_restated_year_is_reported_as_an_amendment():
    """The same fiscal year carrying DIFFERENT values across two filings is
    the definition of a restatement, and `amendments_seen` is how a reader
    learns the number moved. Inverting the comparison announces an amendment
    when the two filings AGREE and stays silent when they differ — the
    restatement history goes quiet exactly when it matters."""
    out = pack_us._normalize_dcf(_two_concept_raw(100.0, 111.0))

    seen = out["income_statement"]["_meta"]["revenue"]["amendments_seen"]
    assert len(seen) == 1, f"a restated year must be reported: {seen}"
    assert "100.0" in seen[0] and "111.0" in seen[0]


def test_a_year_refiled_with_the_same_value_is_not_an_amendment():
    """The other direction, which is what makes the assertion above
    discriminating rather than merely non-empty: a re-filing that repeats the
    figure is not a restatement and must not be announced as one."""
    out = pack_us._normalize_dcf(_two_concept_raw(100.0, 100.0))

    assert out["income_statement"]["_meta"]["revenue"]["amendments_seen"] == [], (
        "an unchanged re-filing is not an amendment"
    )
