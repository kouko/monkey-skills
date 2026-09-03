"""Validate a product's DESIGN.md against design-system's authoring contract.

Valid iff:
  1. Every token group `design_md_spec_keys.TOKEN_GROUPS` freezes appears
     as a whole-line `## <group>` heading (case-insensitive, a trailing
     parenthetical allowed) — `colors`, `typography`, `rounded`,
     `spacing`, `components`. The set is closed: the spec defines no
     fallback for an unrecognised member, so a file may ADD a section but
     may not drop one of these.
  2. Each of those sections carries at least one item — a list entry
     (`-`/`*`/`+`/`1.`/`1)`) or a `key: value` line. A heading over an
     empty body declares a group without defining it.
  3. When present, `ratified-by:` matches `ratified-by: <name>
     <YYYY-MM-DD>` with a date `date.fromisoformat` accepts. Absent is a
     valid in-progress draft (the same tolerance the PRINCIPLES.md
     validator gives); malformed is always invalid.

What this deliberately does NOT do: block anything. concept-model §8 says
DESIGN.md is never a rejection gate — this validator is the authoring-side
check design-system runs on its own output, so a mis-shaped file is caught
where it is written rather than accepted everywhere (W2 adversary P08).

CLI: `python validate_design_output.py <DESIGN.md>` -> exit 0 if valid,
exit 1 with agent-actionable messages on stderr if invalid.

Stdlib only apart from the sibling `design_md_spec_keys` data module.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

from design_md_spec_keys import TOKEN_GROUPS

_ITEM = re.compile(r"^\s*(?:(?:[-*+]|\d+[.)])\s+\S|[\w.-]+\s*:\s*\S)")
_H2 = re.compile(r"^##\s", re.MULTILINE)

_RATIFIED_BY_ANY = re.compile(r"^ratified-by:.*$", re.MULTILINE)
_RATIFIED_BY_WELLFORMED = re.compile(
    r"^ratified-by:\s*\S.*\s(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE
)


def _section_body(text: str, group: str) -> str | None:
    """The body under `## <group>`, or None when no such heading exists."""
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        heading = line[3:].strip().lower()
        if heading == group or heading.startswith(group + " "):
            body = []
            for following in lines[index + 1:]:
                if following.startswith("## "):
                    break
                body.append(following)
            return "".join(body)
    return None


def _check_token_groups(text: str) -> list[str]:
    problems = []
    for group in sorted(TOKEN_GROUPS):
        body = _section_body(text, group)
        if body is None:
            problems.append(
                f"missing token group '{group}': design_md_spec_keys.TOKEN_GROUPS "
                f"is a closed set ({', '.join(sorted(TOKEN_GROUPS))}) and every "
                f"member needs its own `## <group>` section"
            )
        elif not any(_ITEM.match(line) for line in body.splitlines()):
            problems.append(
                f"token group '{group}' has no items; a `## {group}` heading "
                f"over an empty body declares the group without defining it "
                f"(one list entry or `key: value` line is the minimum)"
            )
    return problems


def _check_ratified_by_grammar(text: str) -> list[str]:
    if _RATIFIED_BY_ANY.search(text) is None:
        return []  # absent is valid: an in-progress draft
    match = _RATIFIED_BY_WELLFORMED.search(text)
    if match is None:
        return [
            "'ratified-by:' line is present but malformed; the required "
            "grammar is 'ratified-by: <name> <YYYY-MM-DD>' (a non-empty "
            "name, one space, then an ISO date) — write it only after the "
            "user has said yes to the restatement"
        ]
    try:
        date.fromisoformat(match.group(1))
    except ValueError:
        return [
            f"'ratified-by:' names {match.group(1)!r}, which is not a real "
            "date; the grammar is 'ratified-by: <name> <YYYY-MM-DD>' and the "
            "day has to exist"
        ]
    return []


_CHECKS = [_check_token_groups, _check_ratified_by_grammar]


def validate(path: Path) -> tuple[bool, list[str]]:
    """Run all checks against the DESIGN.md at `path`.

    Returns (ok, problems). ok is True iff problems is empty.
    """
    path = Path(path)
    if not path.is_file():
        return False, [f"DESIGN.md does not exist: {path}"]
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    for check in _CHECKS:
        problems.extend(check(text))
    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a product's DESIGN.md against the design-system "
                    "authoring contract (every frozen token group present as a "
                    "`## <group>` section with at least one item, plus a "
                    "well-formed 'ratified-by:' line when present).")
    parser.add_argument("design_md", help="path to DESIGN.md")
    args = parser.parse_args(argv)

    ok, problems = validate(Path(args.design_md))
    if ok:
        print(f"OK: {args.design_md} conforms to the DESIGN.md contract.")
        return 0
    print(f"INVALID: {args.design_md} does not conform to the DESIGN.md "
          f"contract.", file=sys.stderr)
    for problem in problems:
        print(f"  - {problem}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
