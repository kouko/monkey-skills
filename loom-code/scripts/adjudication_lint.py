#!/usr/bin/env python3
"""Zero-token lint over adjudication-view units-JSON (hard checks —
Task 3; language checks are Task 4's addition to CHECKS below), per
loom-code/skills/using-loom-code/protocols/adjudication-view.md
"Lint-failure rule".

Hard checks (this task):
    - every unit has a non-empty `rendition`
    - every anchor in a unit's `anchors` list appears verbatim in
      that unit's `rendition`

Each check is a callable `unit -> list[str]` (violation lines for
that unit, empty if clean) so Task 4 can append language checks to
`CHECKS` without touching `run_checks()`.

CLI:
    python3 adjudication_lint.py <units-json-file>

Exit 0 and no output on a clean run; exit 1 with one violation line
per finding (stdout) otherwise.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def check_nonempty_rendition(unit):
    """Flag a unit whose `rendition` is empty (or whitespace-only)."""
    if not unit["rendition"].strip():
        return [f"{unit['id']}: empty rendition"]
    return []


def _anchor_echoed(anchor, rendition):
    """True if `anchor` appears verbatim in `rendition`. Purely-digit
    anchors require non-digit boundaries (`re.search` with lookaround)
    so e.g. anchor "1" does not false-match inside "10"; anchors with
    any non-digit character (backticked terms, identifiers, dotted
    versions like "0.77") keep plain substring matching — they may
    legitimately sit flush against CJK text or other digits."""
    if anchor.isdigit():
        pattern = r"(?<!\d)" + re.escape(anchor) + r"(?!\d)"
        return re.search(pattern, rendition) is not None
    return anchor in rendition


def check_anchor_echo(unit):
    """Flag each anchor from `unit['anchors']` that does not appear
    verbatim in `unit['rendition']`."""
    rendition = unit["rendition"]
    return [
        f"{unit['id']}: missing anchor {anchor!r}"
        for anchor in unit["anchors"]
        if not _anchor_echoed(anchor, rendition)
    ]


# Extension point: Task 4 appends language checks (negation presence,
# modality-mapping warning) here — run_checks() stays unchanged.
CHECKS = [check_nonempty_rendition, check_anchor_echo]


def run_checks(units, checks=CHECKS):
    """Run `checks` over every unit; return the flattened list of
    violation lines, in unit order then check order."""
    violations = []
    for unit in units:
        for check in checks:
            violations.extend(check(unit))
    return violations


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="path to a units-JSON file")
    args = parser.parse_args(argv)

    units = json.loads(Path(args.path).read_text(encoding="utf-8"))
    violations = run_checks(units)
    for line in violations:
        print(line)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
