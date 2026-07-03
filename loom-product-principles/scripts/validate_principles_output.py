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

# A top-level ordered-list item: `1. `, `2. `, ... at column 0 (no leading
# whitespace, so nested/indented items do not count).
_ENTRY = re.compile(r"^\d+\.\s")

# The load-bearing marker: em dash (U+2014), single space, lowercase `check`,
# colon. A hyphen or different casing does not match.
_CHECK_MARKER = "— check:"

_H2 = re.compile(r"^##\s", re.MULTILINE)

_MIN_PRINCIPLES = 3
_MAX_PRINCIPLES = 7


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


_CHECKS = [
    _check_north_star,
    _check_principles_count,
    _check_every_principle_has_check,
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
