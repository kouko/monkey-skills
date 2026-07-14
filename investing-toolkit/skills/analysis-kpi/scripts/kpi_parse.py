#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Deterministic cell parser (operational-kpi capability, slice 9).

Layer 2 (Analysis) PURE-COMPUTE — mirrors kpi_validate.py: stdlib only,
text in -> number out. This module is NOT a durable store: it does NOT
import `_store_fs`, does NOT resolve a store dir, does NOT lock or write
files, and touches neither the network nor an LLM.

The CORE property is FAIL-LOUD: an unparseable/missing token RAISES, never
coerces to 0 — a true 0 is a real value, not a missing one. The
deterministic parser emits the number; an LLM (a later slice) only LOCATES
the cell, never types it.

`parse_cell(cell_text)` currently handles the numeric happy path: a leading
currency `$`, thousands `,` separators, a decimal point, a leading `+`/`-`
sign, and the accounting parenthesized-negative convention (`(123)` /
`$(1,234)` / `($1,234)` -> negative). A true `"0"`/`"0.0"` -> `0.0`.

`parse_cell(cell_text)` also RAISES `UnparseableCell` (loud, never a
fabricated `0`) for the not-a-number token taxonomy: `NM`/`nm`, `n/a` /
`N/A` / `na`, a dash used as "not applicable" (em `—`, en `–`, figure `‒`,
or a bare hyphen `-` ALONE — `-45` is still a negative number), and
blank / whitespace-only text. A true `"0"` -> 0.0 is NOT missing.

The `parse` CLI subcommand reads the cell text from `--cell` (or stdin when
omitted), prints the parsed number to stdout on success. An `UnparseableCell`
is a normal fail-loud outcome (not a bug) -- a clean stderr message, exit 1,
never a raw traceback. A malformed invocation (e.g. no subcommand) is an
argparse-level error, exit 2.
"""
from __future__ import annotations

import argparse
import sys

# Dash-as-"not applicable" tokens: em dash, en dash, figure dash, and a
# bare ASCII hyphen used ALONE (a lone dash with no digits attached is
# not-applicable; "-45" is a negative number and never hits this set,
# since `-45` != "-").
_NA_DASHES = {"—", "–", "‒", "-"}
# Case-insensitive not-a-number tokens (checked against the lowercased,
# stripped cell text).
_NA_WORDS = {"nm", "n/a", "na"}


class UnparseableCell(ValueError):
    """Raised when a cell's text is not a genuine number.

    Covers the fail-loud taxonomy: NM, n/a, a dash used as "not
    applicable", and blank/whitespace-only text. A missing cell must
    become the caller's review-item, never a fabricated 0.
    """


def parse_cell(cell_text: str) -> float:
    """Parse a spreadsheet-style cell's numeric text into a float.

    Handles: surrounding whitespace, a leading currency `$` (inside or
    outside accounting parens), thousands `,` separators, a decimal point,
    a leading `+`/`-` sign, and the accounting parenthesized-negative
    convention (`(123)` -> -123.0). A true `"0"` -> 0.0 (a real value).

    Raises `UnparseableCell` for the not-a-number token taxonomy (NM,
    n/a, dash-as-NA, blank/whitespace-only) and for any other non-numeric
    junk — never coerces a missing token to 0.
    """
    text = cell_text.strip()

    if not text or text in _NA_DASHES or text.lower() in _NA_WORDS:
        raise UnparseableCell(f"unparseable cell token: {cell_text!r}")

    text = text.replace("$", "").strip()

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1].strip()

    text = text.replace(",", "")

    try:
        value = float(text)
    except ValueError as exc:
        raise UnparseableCell(f"unparseable cell token: {cell_text!r}") from exc

    return -value if negative else value


def _cli_parse(args: argparse.Namespace) -> int:
    """`parse` subcommand: read the cell text from `--cell` (or stdin when
    omitted), call `parse_cell`, print the parsed number to stdout on
    success and exit 0. An `UnparseableCell` is a normal fail-loud outcome
    (a genuinely-unparseable cell) -- print a clean message to stderr and
    exit 1, never a raw traceback.
    """
    cell_text = args.cell if args.cell is not None else sys.stdin.read()

    try:
        value = parse_cell(cell_text)
    except UnparseableCell as exc:
        print(f"kpi_parse parse: {exc}", file=sys.stderr)
        return 1

    print(value)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic operational-KPI cell parser CLI (parse)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse one spreadsheet-style cell's text into its numeric value.",
    )
    parse_parser.add_argument(
        "--cell", type=str, default=None,
        help="The cell text to parse (default: read stdin).",
    )
    parse_parser.set_defaults(func=_cli_parse)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
