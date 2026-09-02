"""Validate a product's PRINCIPLES.md against the loom 1.0 authoring
contract (product-principles/SKILL.md Step 2).

Valid iff:
  1. All five required `##` sections are present, each as a whole-line
     `##` heading: `## Who`, `## Non-negotiables`, `## Won't do`,
     `## Failure we must avoid`, `## Fixed choices`. `## Non-negotiables`
     may carry a trailing parenthetical (e.g. `## Non-negotiables
     (ordered)`) — matched by prefix, not exact string.
  2. `## Non-negotiables` carries **at least 3** list items — a bullet
     (`-`, `*`, `+`) or an ordered entry (`1.` / `1)`), matching
     `loom-code`'s own `loom_checker.py` `unratified_reason()` counting
     rule exactly (`^\\s*(?:[-*+]|\\d+[.)])\\s+\\S`) so this validator and
     the checker that gates `kind: product` changes never disagree on the
     count.
  3. When present, `ratified-by:` matches the grammar
     `ratified-by: <name> <YYYY-MM-DD>` — a non-empty name, a single
     space, then an ISO date. `ratified-by:` itself is OPTIONAL here (an
     in-progress draft, not yet confirmed by the user, is still a valid
     file to iterate on) — but a MALFORMED line (present, wrong shape) is
     always invalid; only a wholly ABSENT line is tolerated. This is
     stricter than `loom_checker.py`'s own regex (which accepts any
     non-empty trailer), which is fine: tightening the authoring-side
     check never weakens the repo-level gate it feeds.

Design: each check is a function (text: str) -> list[str] of problem
messages (empty == ok), mirroring the sibling validators in this plugin.
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

_REQUIRED_SECTIONS = [
    "## Who",
    "## Non-negotiables",
    "## Won't do",
    "## Failure we must avoid",
    "## Fixed choices",
]
_MIN_NON_NEGOTIABLES = 3

# Same lexeme loom_checker.py's unratified_reason() counts against —
# kept byte-identical on purpose (see module docstring point 2).
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S")

# `ratified-by: <name> <YYYY-MM-DD>` — a non-empty name (no bare
# whitespace-only name), a single space, then an ISO date.
_RATIFIED_BY_WELLFORMED = re.compile(
    r"^ratified-by:\s*\S.*\s\d{4}-\d{2}-\d{2}\s*$", re.MULTILINE
)
_RATIFIED_BY_ANY = re.compile(r"^ratified-by:.*$", re.MULTILINE)

_H2 = re.compile(r"^##\s", re.MULTILINE)


def _section_heading_line(text: str, prefix: str) -> str | None:
    """The first whole `## ` heading LINE that starts with `prefix`
    (allowing a trailing parenthetical like `(ordered)`), or None."""
    for line in text.splitlines():
        if line.rstrip() == prefix or line.startswith(prefix + " "):
            return line
    return None


def _section_body(text: str, prefix: str) -> str | None:
    heading = _section_heading_line(text, prefix)
    if heading is None:
        return None
    start = text.index(heading) + len(heading)
    nxt = _H2.search(text, start)
    return text[start:nxt.start()] if nxt else text[start:]


def _check_required_sections(text: str) -> list[str]:
    missing = [s for s in _REQUIRED_SECTIONS if _section_heading_line(text, s) is None]
    if missing:
        return [
            f"missing required section(s): {', '.join(missing)} (the "
            f"PRINCIPLES.md template carries exactly these five `## ` "
            f"sections, in order: {', '.join(_REQUIRED_SECTIONS)})"
        ]
    return []


def _check_non_negotiables_count(text: str) -> list[str]:
    body = _section_body(text, "## Non-negotiables")
    if body is None:
        return []  # already reported by _check_required_sections
    n = sum(1 for line in body.splitlines() if _LIST_ITEM.match(line))
    if n < _MIN_NON_NEGOTIABLES:
        return [
            f"'## Non-negotiables' has {n} list item(s); the contract "
            f"requires at least {_MIN_NON_NEGOTIABLES} (a bullet `-`/`*`/`+` "
            f"or an ordered `1.`/`1)` entry) — this is the exact rule "
            f"loom-code's checker recomputes to gate a `kind: product` "
            f"change, so a file under this count is never ratifiable"
        ]
    return []


def _check_ratified_by_grammar(text: str) -> list[str]:
    if _RATIFIED_BY_ANY.search(text) is None:
        return []  # absent is valid: an in-progress draft
    if _RATIFIED_BY_WELLFORMED.search(text) is None:
        return [
            "'ratified-by:' line is present but malformed; the required "
            "grammar is 'ratified-by: <name> <YYYY-MM-DD>' (a non-empty "
            "name, one space, then an ISO date) — write it only after the "
            "user has said yes to the restatement"
        ]
    return []


_CHECKS = [
    _check_required_sections,
    _check_non_negotiables_count,
    _check_ratified_by_grammar,
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
        description="Validate a product's PRINCIPLES.md against the loom "
                    "1.0 authoring contract (Who / Non-negotiables >=3 / "
                    "Won't do / Failure we must avoid / Fixed choices, "
                    "plus a well-formed 'ratified-by:' line when present).")
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
