"""Guards the Output contract's applicable-check total (`checks_passed`
denominator, `gaps.check_id` range, and the NEEDS_REVISION
verdict-mapping line) against hardcoded drift.

Task 6 (`docs/loom/plans/2026-08-13-open-question-dispatch-gate.md`)
added a Check 18 row without updating any of these three lines --
"a check no reviewer can cite is not shipped." A prior fix that simply
swapped the literal `15` for `16` in a second place would recreate the
exact same defect the next time a row is added or retired: the number
would again live in two places (the table and this line) with nothing
forcing them to agree.

So this file DERIVES the expected total from the checks table's own
rows, read fresh from the file each run, rather than hardcoding 16 (or
any other number) a second time. The derivation: count every
`| <n> | <check> | <gap> |` row, then exclude rows whose check-cell
text carries the RETIRED (row 5) or advisory/non-fatal (row 15)
marker at its FIXED LEADING position -- reusing the SAME bold token
those two rows already carry at the start of their prose, matched by
POSITION rather than by a free substring search anywhere in the cell.
A prior version of this derivation used a free substring test
(`"retired" in cell.lower()`), which silently dropped any genuinely
applicable row that merely MENTIONED either word mid-prose from the
count -- the identical keyword-fragility class that caused Check
18(b)'s original fatal bug, now caught by
test_applicable_ids_uses_marker_position_not_incidental_keyword and
fixed by anchoring on position (see `_is_excluded`). Add a 19th row
later (retired or not) and this test re-derives the new correct total
automatically; it only reddens when the Output contract's three lines
disagree with what the table itself says.

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

from test_plan_document_reviewer_check17 import (
    _check_id_range_text,
    _needs_revision_range_text,
    _range_list_covers,
)

PROMPT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-document-reviewer-prompt.md"
)

_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|(.*)\|(.*)\|\s*$")


def _text() -> str:
    assert PROMPT_MD.is_file(), f"plan-document-reviewer-prompt.md is absent at {PROMPT_MD}"
    return PROMPT_MD.read_text(encoding="utf-8")


def _check_rows(text: str) -> list[tuple[int, str]]:
    """Every `| <n> | <check cell> | <gap cell> |` table row, as
    `(check_id, check-cell text)`. Header (`| # | Check | ... |`) and
    separator (`|---|---|---|`) rows never match `\\d+` in the first
    cell, so they drop out without special-casing."""
    rows = []
    for line in text.splitlines():
        m = _ROW_RE.match(line.strip())
        if m:
            rows.append((int(m.group(1)), m.group(2)))
    assert rows, "no `| <n> |` check rows found in the checks table"
    return rows


# Row 5 and row 15 mark themselves with a bold token at the FIXED
# LEADING position of the check-cell (row 5: "**RETIRED …", row 15:
# "**(advisory …)"). Anchoring on that position -- not a free
# substring search anywhere in the cell -- is what keeps a genuinely
# applicable row that merely MENTIONS either word mid-prose from being
# silently excluded (see test_applicable_ids_uses_marker_position_not_incidental_keyword).
_RETIRED_MARKER_RE = re.compile(r"^\*\*retired\b")
_ADVISORY_MARKER_RE = re.compile(r"^\*\*\(advisory\b")


def _is_excluded(cell: str) -> bool:
    """True only when `cell`, after stripping whitespace, carries the
    RETIRED / advisory marker at its fixed LEADING position -- a
    positional check, never a free substring search over the whole
    cell's prose."""
    stripped = cell.strip().lower()
    return bool(_RETIRED_MARKER_RE.match(stripped) or _ADVISORY_MARKER_RE.match(stripped))


def _applicable_ids(text: str) -> list[int]:
    """Row ids EXCLUDING any row whose check-cell text carries the
    RETIRED / advisory marker at its fixed leading position -- reads
    the table's own self-description via POSITION, not a second
    hardcoded id list and not a free substring search (see
    `_is_excluded`)."""
    return sorted(n for n, cell in _check_rows(text) if not _is_excluded(cell))


def test_checks_passed_denominator_matches_table_row_count():
    """The Output contract's `checks_passed: <N>/<TOTAL>` denominator
    must equal the checks table's own derived applicable-row count.
    Would fail today (RED) because the file still says `/<15>` while
    the table (18 rows minus RETIRED row 5 minus advisory row 15) has
    16 applicable rows now that Check 18 exists."""
    text = _text()
    expected_total = len(_applicable_ids(text))
    denominator_line = next(
        (line for line in text.splitlines() if line.strip().startswith("checks_passed:")),
        None,
    )
    assert denominator_line is not None, "checks_passed line not found"
    assert f"/<{expected_total}>" in denominator_line, (
        f"checks_passed denominator must equal the table-derived "
        f"applicable total {expected_total}, found: {denominator_line!r}"
    )


def test_check_id_range_upper_bound_matches_highest_applicable_check():
    """The `gaps.check_id` range line's upper bound must be the highest
    applicable check id in the table. Uses the same range-list parser
    `test_plan_document_reviewer_check17.py` built and owns
    (`_range_list_covers` + `_check_id_range_text`) rather than a bare
    `str(highest) in check_id_line` substring test -- the substring form
    is satisfied by the digits appearing ANYWHERE on the line, including
    inside the trailing `# Checks 5, 15 and 18 NEVER appear here`
    exclusion comment, which would let a contracted range (`16-17`) that
    excludes 18 from the actual span still pass this assertion. The
    range parser instead checks whether 18 falls inside a `lo-hi` span
    or matches a standalone id in the `<...>` list itself, isolated from
    that trailing comment by `_check_id_range_text`."""
    text = _text()
    highest = _applicable_ids(text)[-1]
    check_id_line = next(
        (line for line in text.splitlines() if "check_id:" in line),
        None,
    )
    assert check_id_line is not None, "gaps.check_id line not found"
    assert _range_list_covers(_check_id_range_text(check_id_line), highest), (
        f"gaps.check_id range must cover the highest applicable check "
        f"id {highest}, found: {check_id_line!r}"
    )


def test_applicable_ids_uses_marker_position_not_incidental_keyword():
    """FIX for keyword-fragility this module's OWN derivation had: the
    prior `_applicable_ids` tested "retired" / "advisory" as a free
    substring ANYWHERE in the check-cell prose. A genuinely-applicable
    Check 19 whose prose merely MENTIONS the word "advisory" (e.g.
    "...this check produces an advisory suggested_fix but still fails
    the plan like any other row") was silently dropped from the
    derived total -- the identical keyword-fragility class that caused
    Check 18(b)'s original fatal bug, now reintroduced INSIDE the
    machinery built to guard against it. Silent undercount is the
    dangerous direction: it fails to fail.

    The fix anchors on row 5's and row 15's EXISTING fixed-position
    bold marker (`**RETIRED` / `**(advisory`) at the START of the
    check-cell (after stripping whitespace), not a free substring
    search -- so a row that merely mentions either word mid-prose no
    longer gets excluded. Would fail under the pre-fix substring
    implementation because both synthetic rows below contain the
    banned words WITHOUT carrying the leading marker."""
    synthetic_table = (
        "| # | Check | Failure -> NEEDS_REVISION |\n"
        "|---|---|---|\n"
        "| 5 | **RETIRED (v0.13.0+)** -- always N/A, never applied. | Never fails. |\n"
        "| 15 | **(advisory / non-fatal -- NEVER triggers NEEDS_REVISION)** For any two tasks... | Never fails. |\n"
        "| 19 | This check produces an advisory suggested_fix but still fails the plan like any other row. | Fails if X |\n"
        "| 20 | This check retired an old ad-hoc workaround and is fully applicable; it must fail like any other row. | Fails if Y |\n"
    )
    ids = _applicable_ids(synthetic_table)
    assert 19 in ids, (
        "Check 19 merely MENTIONING 'advisory' mid-prose (not at the "
        "leading marker position) must still count as applicable"
    )
    assert 20 in ids, (
        "Check 20 merely MENTIONING 'retired' mid-prose (not at the "
        "leading marker position) must still count as applicable"
    )
    assert 5 not in ids, (
        "genuinely RETIRED row 5 (leading **RETIRED marker) must stay excluded"
    )
    assert 15 not in ids, (
        "genuinely advisory row 15 (leading **(advisory marker) must stay excluded"
    )


def test_needs_revision_mapping_upper_bound_matches_highest_applicable_check():
    """The Verdict mapping's NEEDS_REVISION line must independently
    name the same highest applicable check id -- a separate line from
    `gaps.check_id` that has drifted independently before (both said
    `16-17` while the table only had 17 rows was the previously-correct
    state; both now must say up to 18). Uses the same range-list parser
    as `test_check_id_range_upper_bound_matches_highest_applicable_check`
    above -- a bare `str(highest) in needs_revision_line` substring test
    is satisfied by 18 appearing anywhere in the line's prose (e.g. an
    exclusion clause naming Check 18 alongside 5 and 15) even when the
    bold `**lo-hi, lo-hi**` range itself has been contracted to exclude
    18."""
    text = _text()
    highest = _applicable_ids(text)[-1]
    needs_revision_line = next(
        (
            line
            for line in text.splitlines()
            if line.strip().startswith("- **NEEDS_REVISION**")
        ),
        None,
    )
    assert needs_revision_line is not None, "NEEDS_REVISION verdict-mapping line not found"
    assert _range_list_covers(_needs_revision_range_text(needs_revision_line), highest), (
        f"NEEDS_REVISION verdict-mapping range must cover the highest "
        f"applicable check id {highest}, found: {needs_revision_line!r}"
    )
