#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""Render the two filed renderings of KO FY2017's income statement, so the
committed transcription `ko_fy2017_income_statement_as_filed.json` can be
checked against the documents it claims to transcribe.

WHY THIS EXISTS. Plan Task 10 needs an oracle the code under test did not
produce (docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md;
docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md). Sum
reconciliation cannot supply one — it checks the filing against itself, and it
never reads a label, never reads an order, and never reaches a line outside
every sum. So the oracle has to come from OUTSIDE this repo, and the only thing
outside it that is authoritative is the filing as it was filed.

WHAT IT PRINTS — two renderings of the SAME statement, from the SAME accession
0000021344-18-000008, and the difference between them is the finding:

  PRINTED PAGE — `a2017123110-k.htm`, the primary document of the 10-K: the
      statement a human reads. This is the Task 10 oracle proper. Located by
      its bold heading `CONSOLIDATED STATEMENTS OF INCOME` and confirmed by its
      column header rather than by a byte offset, so a re-run cannot silently
      render some other table.

  SEC-RENDERED EXHIBIT — `R2.htm`, the SEC financial-report rendering of the
      SAME filing's XBRL exhibit, produced by SEC'S OWN renderer. It is a
      SECOND, INDEPENDENT implementation reading the same XBRL this repo reads,
      so it separates "our extraction is wrong" from "the filer's exhibit and
      the filer's printed page differ" — two diagnoses the printed page alone
      cannot tell apart. MEASURED 2026-07-26: it agrees with this repo's
      reconstruction on all 26 labels and their order, byte for byte.

WHAT IT IS NOT. It never imports `kpi_us_statement_shape`,
`kpi_us_statement_lines` or `kpi_us_statement_cells`, and it never reads the
row capture `us_statement_reconstruction_2026-07-26.json`. Nothing this repo
computes can reach the numbers it prints. A generator that consulted the code
under test would make Task 10 prove only that the code agrees with itself.

IT DOES NOT WRITE THE FIXTURE. The committed JSON was transcribed from this
script's output BY HAND, line by line, and the two are kept honest by a reader
re-running this and comparing — not by a pipe. That is deliberate: a fixture
this script emitted would silently absorb any bug in this script's table
parsing, and the parsing is the one part of the chain a reader cannot check by
looking at the filing.

NETWORK. Hits `www.sec.gov` through the repo's shared HTTP boundary
`sec_edgar_client._sec_get`, which carries the module's own `USER_AGENT`; no
new network primitive and no new identity. NOT part of the offline suite — this
is not a `test_*` module and pytest never collects it. Re-run by hand:

    PYTHONDONTWRITEBYTECODE=1 uv run --quiet --with 'requests==2.33.1' \\
      python investing-toolkit/tests/data/fixtures/\\
      capture_ko_fy2017_income_as_filed.py
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[4]
sys.path.insert(
    0, str(_REPO_ROOT / "investing-toolkit" / "skills" / "data-markets" / "scripts")
)
import sec_edgar_client as sec  # noqa: E402

ACCESSION = "0000021344-18-000008"
_BASE = "https://www.sec.gov/Archives/edgar/data/21344/000002134418000008"
PRINTED_PAGE = f"{_BASE}/a2017123110-k.htm"
SEC_RENDERED_EXHIBIT = f"{_BASE}/R2.htm"

_HEADING = "CONSOLIDATED STATEMENTS OF INCOME"
_COLUMN_HEADER = "Year Ended December 31,"


class _FirstTable(HTMLParser):
    """The first HTML table at or after an offset, as rows of cell text.

    Superscript footnote markers are DROPPED: `<sup>1</sup>` beside a label is
    a reference mark, not part of the label, and a reader does not read it as
    one. Everything else in a cell is kept verbatim, including the em dashes
    and the parentheses that carry the sign.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._depth = 0
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._in_sup = 0
        self._done = False
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag, attrs):
        if self._done:
            return
        if tag == "table":
            self._depth += 1
        elif tag == "tr" and self._depth:
            self._row = []
        elif tag in ("td", "th") and self._depth:
            self._cell = []
        elif tag == "sup":
            self._in_sup += 1

    def handle_endtag(self, tag):
        if self._done:
            return
        if tag == "table":
            self._depth -= 1
            self._done = self._depth == 0
        elif tag == "tr" and self._row is not None:
            cells = [cell for cell in self._row if cell]
            if cells:
                self.rows.append(cells)
            self._row = None
        elif tag in ("td", "th") and self._cell is not None:
            if self._row is not None:
                self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "sup":
            self._in_sup = max(0, self._in_sup - 1)

    def handle_data(self, data):
        if self._cell is not None and not self._in_sup:
            self._cell.append(data.replace(" ", " "))


def _table_at(html: str, offset: int) -> list[list[str]]:
    parser = _FirstTable()
    parser.feed(html[html.index("<table", offset):])
    return parser.rows


def _income_statement_of_the_printed_page(html: str) -> list[list[str]]:
    """The statement table, found by its heading and CONFIRMED by its column
    header. The phrase appears ~70 times in KO's 10-K — almost all of them
    body prose ("...in our consolidated statements of income") — so matching
    the phrase alone would pick a table belonging to some other disclosure.
    Fails loudly rather than returning a plausible wrong table."""
    start = 0
    while True:
        found = html.find(_HEADING, start)
        if found == -1:
            raise SystemExit(
                f"no table headed {_HEADING!r} and carrying the column header "
                f"{_COLUMN_HEADER!r} was found in {PRINTED_PAGE} — the document "
                "has changed shape and the transcription must be re-checked by eye"
            )
        start = found + 1
        table = html.find("<table", found)
        if table == -1 or table - found > 2000:
            continue
        rows = _table_at(html, table)
        if rows and rows[0][0].startswith(_COLUMN_HEADER):
            return rows


def _fetch(url: str) -> str:
    html = sec._sec_get(url, as_json=False)
    if not isinstance(html, str):
        raise SystemExit(f"could not fetch {url} (got {type(html).__name__})")
    return html


def _show(title: str, url: str, rows: list[list[str]]) -> None:
    print(f"\n=== {title}\n=== {url}\n")
    for row in rows:
        print(" | ".join(row))


def main() -> None:
    _show(
        "PRINTED PAGE — the statement a human reads; the Task 10 oracle",
        PRINTED_PAGE,
        _income_statement_of_the_printed_page(_fetch(PRINTED_PAGE)),
    )
    _show(
        "SEC-RENDERED EXHIBIT — SEC's own renderer over the same filing's XBRL",
        SEC_RENDERED_EXHIBIT,
        _table_at(_fetch(SEC_RENDERED_EXHIBIT), 0),
    )
    print(
        "\nBoth are the filed accession "
        f"{ACCESSION}. Compare each against "
        "ko_fy2017_income_statement_as_filed.json by eye: `lines` transcribes "
        "the first, `sec_rendered_lines` the second."
    )


if __name__ == "__main__":
    main()
