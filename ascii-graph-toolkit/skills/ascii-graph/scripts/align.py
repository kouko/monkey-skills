"""align.py — alignment oracle CLI for ASCII/Unicode diagrams.

Verification-class scaffolding: the model draws the diagram, this measures
display-width drift and reports it; the model fixes. It does NOT lay out and
does NOT edit the diagram.

Wires the three drift checks (vertical seam, table equal-width, kink +
arrowhead-landing) into one oracle. `analyze` returns a per-line
display-width report plus the aggregated issues in line order; `main` is the
file/stdin CLI wrapper that prints both and exits 0 (clean) / 1 (drift).
"""

import sys

from width import display_width
from checks_seam import find_issues as seam_issues
from checks_table import find_issues as table_issues
from checks_kink import find_issues as kink_issues

_CHECKS = (seam_issues, table_issues, kink_issues)


def analyze(text: str) -> tuple[str, list[tuple[int, int, str]]]:
    """Return (per-line display-width report, aggregated issues in line order).

    The report has one line per input line: a 1-based index, the line's
    display width, and the raw line. Issues from all three checks are merged
    and sorted by (line number, display column) so they read top-to-bottom.
    """
    lines = text.splitlines()
    report = "\n".join(
        f"{i:4d} {display_width(line):5d} | {line}"
        for i, line in enumerate(lines)
    )
    issues: list[tuple[int, int, str]] = []
    for check in _CHECKS:
        issues.extend(check(lines))
    issues.sort(key=lambda issue: (issue[0], issue[1]))
    return report, issues


def main(argv=None) -> int:
    """Read a diagram from a file arg or stdin ('-'), report width + drift.

    Prints the width report, then one line per issue
    (`line {n}: col {c}: {msg}`) or a single "✓ no drift" line when clean.
    Returns 0 when clean, 1 when any issue is found.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    source = argv[0] if argv else "-"
    if source == "-":
        text = sys.stdin.read()
    else:
        with open(source, encoding="utf-8") as fh:
            text = fh.read()

    report, issues = analyze(text)
    print(report)
    if issues:
        for ln, col, msg in issues:
            print(f"line {ln}: col {col}: {msg}")
        return 1
    print("✓ no drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
