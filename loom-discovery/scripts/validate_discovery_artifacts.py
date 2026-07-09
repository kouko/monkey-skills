"""Validate a `docs/loom/discovery/<slug>/` folder produced by the
loom-discovery station.

    <folder>/
      user-insights.md   # REQUIRED
      evidence.md        # REQUIRED
      business-value.md  # OPTIONAL
      research/          # OPTIONAL

Checks:
  - user-insights.md: present, and carries every required section heading.
    SSOT for the heading list is the shipped template —
    loom-discovery/skills/user-insights/assets/user-insights-template.md —
    hardcoded in _REQUIRED_USER_INSIGHTS_SECTIONS below (read the template
    at authoring time; do not re-derive at runtime).
  - evidence.md: present, and contains a markdown table header row (SSOT:
    loom-discovery/skills/user-insights/assets/evidence-template.md).
  - business-value.md: optional; when present, its verdict line must
    contain exactly one of GO / NO-GO / NEEDS-MORE-RESEARCH (SSOT:
    loom-discovery/skills/business-value/assets/business-value-template.md).
  - research/: optional directory; no structural check either way.

Design mirrors loom-spec/scripts/validate_spec_output.py: each check is a
function (root: Path) -> list[str] of problem messages (empty == ok).

CLI: `python validate_discovery_artifacts.py <folder>` -> exit 0 if valid,
exit 1 with agent-actionable messages on stderr if invalid.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# SSOT: loom-discovery/skills/user-insights/assets/user-insights-template.md
# — the four required "## " headings, hardcoded here (whole-line match only;
# a prose mention must never satisfy a check).
_REQUIRED_USER_INSIGHTS_SECTIONS = [
    "## Problem framing",
    "## Opportunity space",
    "## Value commitment",
    "## Risks & open questions",
]

# SSOT: loom-discovery/skills/business-value/assets/business-value-template.md
_VALID_VERDICTS = ("GO", "NO-GO", "NEEDS-MORE-RESEARCH")

# Longest-first alternation so "NO-GO" / "NEEDS-MORE-RESEARCH" match whole,
# rather than "GO" matching as a substring of "NO-GO" too (naive `in`
# containment double-counts that case).
_VERDICT_PATTERN = re.compile(
    "|".join(re.escape(v) for v in sorted(_VALID_VERDICTS, key=len, reverse=True)))

# A markdown table header row: `| ... |` immediately followed by a separator
# row `|---|---|...`.
_TABLE_HEADER = re.compile(
    r"^\|.+\|[ \t]*\n\|[ \t]*:?-+:?[ \t]*(\|[ \t]*:?-+:?[ \t]*)+\|?[ \t]*$",
    re.MULTILINE,
)


def _section_present(text: str, header: str) -> bool:
    """Whole-header-line match — a substring in prose never counts."""
    pat = re.compile(r"^" + re.escape(header) + r"\s*$", re.MULTILINE)
    return pat.search(text) is not None


# --- checks: each returns list[str] of problems (empty == ok) --------------

def _check_user_insights_present(root: Path) -> list[str]:
    if not (root / "user-insights.md").is_file():
        return [f"missing user-insights.md at {root / 'user-insights.md'} "
                f"(every discovery folder needs a user-insights.md)"]
    return []


def _check_user_insights_sections(root: Path) -> list[str]:
    path = root / "user-insights.md"
    if not path.is_file():
        return []  # already reported by _check_user_insights_present
    text = path.read_text(encoding="utf-8")
    problems = []
    for header in _REQUIRED_USER_INSIGHTS_SECTIONS:
        if not _section_present(text, header):
            problems.append(f"missing '{header}' section in {path} "
                            f"(required by the user-insights template)")
    return problems


def _check_evidence_present(root: Path) -> list[str]:
    if not (root / "evidence.md").is_file():
        return [f"missing evidence.md at {root / 'evidence.md'} "
                f"(every discovery folder needs an evidence.md claims registry)"]
    return []


def _check_evidence_table_header(root: Path) -> list[str]:
    path = root / "evidence.md"
    if not path.is_file():
        return []  # already reported by _check_evidence_present
    text = path.read_text(encoding="utf-8")
    if _TABLE_HEADER.search(text) is None:
        return [f"evidence.md at {path} has no markdown table header row "
                f"(expected a '| Claim id | ... |' header + '|---|...' "
                f"separator, per the evidence template)"]
    return []


def _check_business_value_verdict(root: Path) -> list[str]:
    path = root / "business-value.md"
    if not path.is_file():
        return []  # optional — absence is fine
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^Verdict:\s*(.+)$", text, re.MULTILINE)
    if m is None:
        return [f"business-value.md at {path} has no 'Verdict: ...' line "
                f"(expected one of {', '.join(_VALID_VERDICTS)})"]
    line = m.group(1)
    hits = _VERDICT_PATTERN.findall(line)
    if len(hits) != 1:
        return [f"business-value.md at {path} verdict line {line!r} must "
                f"contain exactly one of {', '.join(_VALID_VERDICTS)}, "
                f"found {len(hits)}"]
    return []


_CHECKS = [
    _check_user_insights_present,
    _check_user_insights_sections,
    _check_evidence_present,
    _check_evidence_table_header,
    _check_business_value_verdict,
]


def validate(root: Path) -> tuple[bool, list[str]]:
    """Run all checks against the discovery folder `root`.

    Returns (ok, problems). ok is True iff problems is empty.
    """
    root = Path(root)
    problems: list[str] = []
    if not root.is_dir():
        return False, [f"discovery folder does not exist: {root}"]
    for check in _CHECKS:
        problems.extend(check(root))
    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a docs/loom/discovery/<slug>/ folder produced "
                    "by the loom-discovery station.")
    parser.add_argument("folder", help="path to the discovery folder")
    args = parser.parse_args(argv)

    ok, problems = validate(Path(args.folder))
    if ok:
        print(f"OK: {args.folder} conforms to the discovery artifact contract.")
        return 0
    print(f"INVALID: {args.folder} does not conform to the discovery "
          f"artifact contract.", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
