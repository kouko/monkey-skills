"""Validate a product's PRINCIPLES.md against the authoring contract.

The contract is pinned in
`skills/product-principles/references/principles-rules.md`
("Validator contract (summary)" section). This module checks STRUCTURE +
the load-bearing falsifiable-check marker mechanically; the *quality* of a
check (truly falsifiable vs disguised platitude) is the generator's and
reviewer's responsibility.

Valid iff:
  1. A `## North Star` section exists and is non-empty — at least one
     non-whitespace, non-heading body line appears under the heading before
     the next `##`.
  2. A `## Product Principles` section exists with 3-7 principle ENTRIES,
     where an entry is a TOP-LEVEL ordered-list item (a line matching
     `^\\d+\\.\\s`).
     Unordered bullets, nested (indented) items, and the ✅/❌ example lines
     are NOT counted.
  3. EVERY principle entry carries the literal `— check:` marker — an em dash
     (U+2014 `—`), a single space, the lowercase word `check`, then a colon —
     on the same line as the entry. A hyphen `-`/`--` or different casing does
     NOT satisfy it.
  4. `## Design Principles` and `## Engineering Principles` are OPTIONAL:
     absent is valid; present requires 1-7 entries with the same ordered-list
     + `— check:` rules as `## Product Principles`. A present-but-empty
     section (0 entries) is invalid — it must be omitted, not left empty.
  5. No legacy `## Principles` heading remains — a whole-line legacy heading
     is invalid and yields a targeted migration message naming
     `## Product Principles` as the rename target.
  6. `## Anchors` is OPTIONAL: absent is valid; present requires a
     well-formed table — a header row, a GFM separator row
     (`^\\|[\\s:-]+\\|`) immediately below it, and at least 1 data row
     whose version/edition cell (second pipe-delimited cell) is
     non-empty. A present-but-empty table (header + separator, zero
     data rows) is invalid.
  7. `## Deviation Ledger` is OPTIONAL: absent is valid; present requires
     at least 1 ordered-list entry, and every entry carries both the
     literal `— reason:` and `— principle:` markers on the same
     physical line. A present-but-empty section (0 entries) is invalid.

Design: each check is a function (text: str) -> list[str] of problem messages
(empty == ok), mirroring `loom-spec/scripts/validate_spec_output.py`.
`_CHECKS` is the registry; `validate()` runs them all.

CLI: `python validate_principles_output.py <PRINCIPLES.md>` -> exit 0 if
valid, exit 1 with agent-actionable messages on stderr if invalid.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_NORTH_STAR = "## North Star"
_PRINCIPLES = "## Product Principles"
_LEGACY_PRINCIPLES = "## Principles"

# Optional jurisdiction sections: same ordered-list + `— check:` lexeme as
# `## Product Principles`, but with a lower floor (1, not 3) and OPTIONAL —
# absent is valid. A present-but-empty section is invalid (an empty heading
# invites platitude-filling; a section with no clauses is simply omitted).
_OPTIONAL_SECTIONS = ["## Design Principles", "## Engineering Principles"]
_MIN_OPTIONAL_ENTRIES = 1

# The legacy heading, matched as a WHOLE header line (same style as
# `_section_body`) so `## Product Principles` never false-positives.
_LEGACY_HEADING_RE = re.compile(
    r"^" + re.escape(_LEGACY_PRINCIPLES) + r"\s*$", re.MULTILINE
)

# A top-level ordered-list item: `1. `, `2. `, ... at column 0 (no leading
# whitespace, so nested/indented items do not count).
_ENTRY = re.compile(r"^\d+\.\s")

# The load-bearing marker: em dash (U+2014), single space, lowercase `check`,
# colon. A hyphen or different casing does not match.
_CHECK_MARKER = "— check:"

_H2 = re.compile(r"^##\s", re.MULTILINE)

_MIN_PRINCIPLES = 3
_MAX_PRINCIPLES = 7

# `## Anchors`: optional canon-pin table. GFM separator row: pipes,
# whitespace, colons, and hyphens only.
_ANCHORS = "## Anchors"
_ANCHORS_SEPARATOR_RE = re.compile(r"^\|[\s:-]+\|")

# `## Deviation Ledger`: optional ordered-list ledger of committed breaks
# from the `## Anchors` canon. Entries reuse the `_ENTRY` ordered-list regex
# above; each entry carries both sibling markers on the same physical line.
_DEVIATION_LEDGER = "## Deviation Ledger"
_REASON_MARKER = "— reason:"
_PRINCIPLE_MARKER = "— principle:"


def _section_body(text: str, header: str) -> str | None:
    """Body of the `## <header>` section (lines after the header line up to the
    next `## ` header or end), or None if the header is absent. Match is on a
    whole header line so a substring in prose never counts."""
    pat = re.compile(r"^" + re.escape(header) + r"\s*$", re.MULTILINE)
    m = pat.search(text)
    if m is None:
        return None
    nxt = _H2.search(text, m.end())
    return text[m.end():nxt.start()] if nxt else text[m.end():]


def _principle_entries(body: str) -> list[str]:
    """The top-level ordered-list entry lines within a `## Product Principles`
    body."""
    return [line for line in body.splitlines() if _ENTRY.match(line)]


# --- checks: each returns list[str] of problems (empty == ok) ---------------

def _check_north_star(text: str) -> list[str]:
    body = _section_body(text, _NORTH_STAR)
    if body is None:
        return [f"missing '{_NORTH_STAR}' section "
                f"(state the product Goal + a concrete checkable Success)"]
    has_body = any(
        line.strip() and not line.lstrip().startswith("#")
        for line in body.splitlines()
    )
    if not has_body:
        return [f"'{_NORTH_STAR}' section is empty "
                f"(it MUST carry >=1 body line: Goal + Success)"]
    return []


def _check_principles_count(text: str) -> list[str]:
    body = _section_body(text, _PRINCIPLES)
    if body is None:
        return [f"missing '{_PRINCIPLES}' section "
                f"(list {_MIN_PRINCIPLES}-{_MAX_PRINCIPLES} principles as a "
                f"top-level ordered list)"]
    n = len(_principle_entries(body))
    if not (_MIN_PRINCIPLES <= n <= _MAX_PRINCIPLES):
        return [f"'{_PRINCIPLES}' has {n} ordered-list entries; the contract "
                f"requires {_MIN_PRINCIPLES}-{_MAX_PRINCIPLES} (an entry is a "
                f"top-level `N.` line; bullets, nested items, and ✅/❌ "
                f"examples do not count)"]
    return []


def _check_every_principle_has_check(text: str) -> list[str]:
    body = _section_body(text, _PRINCIPLES)
    if body is None:
        return []  # already reported by _check_principles_count
    problems: list[str] = []
    for entry in _principle_entries(body):
        if _CHECK_MARKER not in entry:
            problems.append(
                f"principle entry lacks the literal '{_CHECK_MARKER}' marker "
                f"(em dash U+2014, single space, lowercase 'check', colon; a "
                f"hyphen or different casing does not count): {entry.strip()!r}"
            )
    return problems


def _check_optional_jurisdiction_sections(text: str) -> list[str]:
    """One rule, applied to both `## Design Principles` and
    `## Engineering Principles`: absent = valid; present = 1-7 top-level
    ordered entries, every entry carrying the `— check:` marker; present
    with 0 entries = invalid."""
    problems: list[str] = []
    for heading in _OPTIONAL_SECTIONS:
        body = _section_body(text, heading)
        if body is None:
            continue  # optional section absent -> valid
        entries = _principle_entries(body)
        n = len(entries)
        if n == 0:
            problems.append(
                f"'{heading}' is present but has no ordered-list entries; a "
                f"section with no committed clauses must be omitted, not left "
                f"empty (an empty heading invites platitude-filling)"
            )
            continue  # no entries to check markers on
        if n > _MAX_PRINCIPLES:
            problems.append(
                f"'{heading}' has {n} ordered-list entries; the contract "
                f"requires {_MIN_OPTIONAL_ENTRIES}-{_MAX_PRINCIPLES} (an entry "
                f"is a top-level `N.` line; bullets, nested items, and ✅/❌ "
                f"examples do not count)"
            )
        for entry in entries:
            if _CHECK_MARKER not in entry:
                problems.append(
                    f"'{heading}' entry lacks the literal '{_CHECK_MARKER}' "
                    f"marker (em dash U+2014, single space, lowercase "
                    f"'check', colon; a hyphen or different casing does not "
                    f"count): {entry.strip()!r}"
                )
    return problems


def _split_pipe_row(line: str) -> list[str]:
    """Split a `|`-delimited table row into cells.

    Convention: a GFM row is written `| cell | cell |`, so a naive
    `line.split("|")` produces an empty string at each end (before the
    leading `|` and after the trailing `|`). Strip exactly those two empty
    boundary elements — not any cell — before returning; a row missing its
    leading/trailing pipe is left as-is.
    """
    parts = line.strip().split("|")
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def _check_anchors(text: str) -> list[str]:
    """`## Anchors` is optional. Present requires a well-formed table:
    header row, a GFM separator row immediately below it, and >=1 data row
    whose version/edition cell (second pipe-delimited cell) is non-empty."""
    body = _section_body(text, _ANCHORS)
    if body is None:
        return []  # optional section absent -> valid
    lines = [line for line in body.splitlines() if line.strip()]
    if (
        len(lines) < 2
        or "|" not in lines[0]
        or not _ANCHORS_SEPARATOR_RE.match(lines[1])
    ):
        return [
            f"'{_ANCHORS}' is present but has no well-formed table (a header "
            f"row, a GFM separator row `| --- | --- |` immediately below it, "
            f"and >=1 data row are required; a present-but-empty section "
            f"must be omitted, not left empty)"
        ]
    # Trailing prose in the same section (after the table) is legal — rule 6
    # constrains the TABLE, not the section's prose. A GFM table row always
    # STARTS with `|`; requiring that (rather than merely containing `|`
    # anywhere) keeps a prose line that happens to mention a pipe character
    # (e.g. a `||` operator reference) from being mistaken for a data row.
    data_rows = [line for line in lines[2:] if line.strip().startswith("|")]
    if not data_rows:
        return [
            f"'{_ANCHORS}' table has no data rows; a present-but-empty "
            f"section must be omitted, not left empty"
        ]
    problems: list[str] = []
    for row in data_rows:
        cells = _split_pipe_row(row)
        version = cells[1] if len(cells) > 1 else ""
        if not version.strip():
            problems.append(
                f"'{_ANCHORS}' row has an empty version/edition cell (the "
                f"second pipe-delimited cell): {row.strip()!r}"
            )
    return problems


def _check_deviation_ledger(text: str) -> list[str]:
    """`## Deviation Ledger` is optional. Present requires >=1 ordered-list
    entry, each carrying both `— reason:` and `— principle:` markers on its
    own physical line."""
    body = _section_body(text, _DEVIATION_LEDGER)
    if body is None:
        return []  # optional section absent -> valid
    entries = _principle_entries(body)
    if not entries:
        return [
            f"'{_DEVIATION_LEDGER}' is present but has no ordered-list "
            f"entries; a present-but-empty section must be omitted, not "
            f"left empty"
        ]
    problems: list[str] = []
    for entry in entries:
        missing = [
            marker
            for marker in (_REASON_MARKER, _PRINCIPLE_MARKER)
            if marker not in entry
        ]
        if missing:
            problems.append(
                f"'{_DEVIATION_LEDGER}' entry is missing marker(s) "
                f"{', '.join(repr(m) for m in missing)} on the same "
                f"physical line: {entry.strip()!r}"
            )
    return problems


def _check_legacy_heading(text: str) -> list[str]:
    if _LEGACY_HEADING_RE.search(text) is None:
        return []
    return [
        f"legacy '{_LEGACY_PRINCIPLES}' heading found; rename it to "
        f"'{_PRINCIPLES}' (same rules apply: 3-7 top-level ordered entries, "
        f"each carrying the '{_CHECK_MARKER}' marker)"
    ]


_CHECKS = [
    _check_north_star,
    _check_principles_count,
    _check_every_principle_has_check,
    _check_optional_jurisdiction_sections,
    _check_anchors,
    _check_deviation_ledger,
    _check_legacy_heading,
]


def validate(path: Path) -> tuple[bool, list[str]]:
    """Run all checks against the PRINCIPLES.md file at `path`.

    Returns (ok, problems). ok is True iff problems is empty.
    """
    path = Path(path)
    if not path.is_file():
        return False, [f"PRINCIPLES.md does not exist: {path}"]
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    for check in _CHECKS:
        problems.extend(check(text))
    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a product's PRINCIPLES.md against the authoring "
                    "contract (North Star + 3-7 principles, each with a "
                    "falsifiable '— check:' marker).")
    parser.add_argument("principles_md", help="path to PRINCIPLES.md")
    args = parser.parse_args(argv)

    ok, problems = validate(Path(args.principles_md))
    if ok:
        print(f"OK: {args.principles_md} conforms to the PRINCIPLES.md contract.")
        return 0
    print(f"INVALID: {args.principles_md} does not conform to the "
          f"PRINCIPLES.md contract.", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
