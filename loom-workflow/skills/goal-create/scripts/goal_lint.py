#!/usr/bin/env python3
"""Mechanical lint floor for a goal condition (loom-workflow:goal-create).

This checker enforces only what is decidable from the goal text alone,
syntactically. That boundary is deliberate: matching prose intent by
regular expression is whitelist maintenance — an unknown test runner and
an unknown phrasing each become a false failure, and a false failure is
the worst outcome for a gate, because it blocks correct work and teaches
its user to ignore the gate. So the hard checks below look only for
syntactic markers (a field label existing with content, a backticked code
span, a character count) and never at whether the prose reads as
convincing. Anything that needs reading intent — is this wording vague,
does finishing depend on a person — is downgraded to an advisory warning
that never fails the run. Anything that needs the repository's current
state rather than the goal text (in particular: is the described
condition actually false right now) cannot be decided by this checker at
all, and is reported as UNCHECKED rather than silently counted as a pass.

The four field labels checked here are the ones this skill's own
goal-shape reference defines, in the same order. A later task adds
Traditional Chinese, English, and Japanese phrasing coverage on top of
this floor; the marker lists below (`STOP_CLAUSE_MARKERS`,
`UNDECIDABLE_WORDING_MARKERS`, `PERSON_DEPENDENT_MARKERS`) are kept as
flat, appendable lists for exactly that reason — extending them to other
languages does not change the shape of the checks.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

FIELD_LABELS = ["Outcome", "Constraints", "Verification", "Stop-when"]

CHARACTER_LIMIT = 4000

# Hard check #2 operates on the Stop-when field's own content (not the
# label line), looking for a literal marker word the way the backtick
# check looks for a literal delimiter — not a whitelist of phrasing.
STOP_CLAUSE_MARKERS = ["stop"]

# Advisory only: illustrative, not exhaustive. False negatives here are
# acceptable because these never fail the run.
UNDECIDABLE_WORDING_MARKERS = [
    "properly",
    "correctly",
    "nicely",
    "appropriately",
    "reasonably",
    "good",
]
PERSON_DEPENDENT_MARKERS = [
    "manual",
    "manually",
    "someone",
    "a person",
    "ask the user",
    "review by",
]

_LABEL_LINE_RE = re.compile(
    r"^\s*\*{0,2}(" + "|".join(re.escape(label) for label in FIELD_LABELS) + r")\*{0,2}\s*:\s*(.*)$"
)
_BACKTICK_SPAN_RE = re.compile(r"`[^`\n]+`")


@dataclass
class Finding:
    code: str
    message: str


@dataclass
class LintResult:
    errors: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)
    unchecked: list[Finding] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        return 1 if self.errors else 0


def parse_fields(text: str) -> dict[str, str]:
    """Split goal text into {label: content} by scanning label lines.

    A field's content runs from just after its label line to the next
    recognized label line (in any order) or end of text. This is purely
    positional/syntactic — no reading of what the content says.
    """
    lines = text.splitlines()
    positions: list[tuple[str, int, str]] = []
    for i, line in enumerate(lines):
        match = _LABEL_LINE_RE.match(line)
        if match:
            positions.append((match.group(1), i, match.group(2)))

    fields: dict[str, str] = {}
    for idx, (label, start, first_content) in enumerate(positions):
        end = positions[idx + 1][1] if idx + 1 < len(positions) else len(lines)
        body = [first_content, *lines[start + 1 : end]]
        fields[label] = "\n".join(body).strip()
    return fields


def lint_text(text: str) -> LintResult:
    result = LintResult()
    fields = parse_fields(text)

    for label in FIELD_LABELS:
        if not fields.get(label, "").strip():
            result.errors.append(
                Finding("missing-field", f"Missing or empty field: {label}")
            )

    stop_content = fields.get("Stop-when", "").strip()
    if stop_content and not any(
        marker in stop_content.lower() for marker in STOP_CLAUSE_MARKERS
    ):
        result.errors.append(
            Finding("no-stop-clause", "Stop-when has content but no recognizable stop clause")
        )

    verification_content = fields.get("Verification", "").strip()
    if verification_content and not _BACKTICK_SPAN_RE.search(verification_content):
        result.errors.append(
            Finding("no-backtick-command", "Verification has no backticked command")
        )

    if len(text) > CHARACTER_LIMIT:
        result.errors.append(
            Finding(
                "length-limit",
                f"Goal text is {len(text)} characters, exceeds the {CHARACTER_LIMIT} limit",
            )
        )

    for label in ("Outcome", "Constraints"):
        content = fields.get(label, "")
        for marker in UNDECIDABLE_WORDING_MARKERS:
            if marker in content.lower():
                result.warnings.append(
                    Finding(
                        "undecidable-wording",
                        f"{label} uses wording that may be undecidable: '{marker}'",
                    )
                )
                break

    for label in ("Verification", "Stop-when"):
        content = fields.get(label, "")
        for marker in PERSON_DEPENDENT_MARKERS:
            if marker in content.lower():
                result.warnings.append(
                    Finding(
                        "person-dependent",
                        f"{label} completion may depend on a person: '{marker}'",
                    )
                )
                break

    result.unchecked.append(
        Finding(
            "condition-currently-false",
            "Whether the described condition is currently false cannot be "
            "checked from goal text alone — it needs the repository's "
            "current state, not just the text.",
        )
    )

    return result


def _format_report(result: LintResult) -> str:
    lines = []
    for finding in result.errors:
        lines.append(f"ERROR [{finding.code}]: {finding.message}")
    for finding in result.warnings:
        lines.append(f"WARNING [{finding.code}]: {finding.message}")
    for finding in result.unchecked:
        lines.append(f"UNCHECKED [{finding.code}]: {finding.message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    text = Path(argv[0]).read_text(encoding="utf-8") if argv else sys.stdin.read()
    result = lint_text(text)
    report = _format_report(result)
    if report:
        print(report)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
