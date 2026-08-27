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
convincing or bounds the run. Anything that needs reading intent — is
this wording vague, does finishing depend on a person, does a stop
clause actually bound the run — is downgraded to an advisory warning
that never fails the run, or omitted entirely when even an illustrative
marker list would misrepresent itself as a syntactic check. Anything
that needs the repository's current state rather than the goal text (in
particular: is the described condition actually false right now) cannot
be decided by this checker at all, and is reported as UNCHECKED rather
than silently counted as a pass.

There are three hard failures: a missing or empty field label; no
backticked command inside `Verification`; text over the character
limit. `Stop-when` is covered only by the field-presence check — no
word list stands in for reading whether its content actually bounds the
run, because a fixed vocabulary of "stop words" false-fails legitimate
phrasing the list's author didn't anticipate (e.g. "Halt after 20 turns
regardless of outcome"). No check in this module enumerates the words
that make a rule pass or fail; the two marker lists below
(`UNDECIDABLE_WORDING_MARKERS`, `PERSON_DEPENDENT_MARKERS`) are the
exception, and only because they are advisory — illustrative, not
exhaustive, and never able to fail the run.

The four field labels checked here are the ones this skill's own
goal-shape reference defines, in the same order. A later task adds
Traditional Chinese, English, and Japanese phrasing coverage on top of
this floor; the marker lists below are kept as flat, appendable lists
for exactly that reason — extending them to other languages does not
change the shape of the checks.

Field parsing is context-aware: a label line inside a *balanced* fenced
code block (```...```) or a *balanced* inline code span (`...`,
including one whose closing backtick lands on a later line) is content
belonging to whichever field is currently open, never a new field
boundary. Without this, a goal that quotes a bad-example report format
— itself containing lines that look like field labels — would have its
real field wrongly truncated at the quoted line. An *unmatched* opening
fence or a stray odd-backtick-count line masks nothing: only a
delimiter with a matching close is a delimiter at all, so a forgotten
closing fence or a typo'd backtick can never swallow a real field label
that follows it.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

FIELD_LABELS = ["Outcome", "Constraints", "Verification", "Stop-when"]

CHARACTER_LIMIT = 4000

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
_FENCE_MARKER_RE = re.compile(r"^\s*```")


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


def _find_masked_lines(lines: list[str]) -> set[int]:
    """Return line indices that fall inside a *balanced* fence or inline
    code span and must never be read as a field-label boundary.

    Only a delimiter with a matching close counts as a delimiter at all.
    An opening fence marker with no later closing marker, or a stray
    line with an odd backtick count and no later line to pair it with,
    masks nothing — the text after it is ordinary content, exactly as
    it would be read outside any code span.
    """
    masked: set[int] = set()

    fence_indices = [i for i, line in enumerate(lines) if _FENCE_MARKER_RE.match(line)]
    for open_i, close_i in zip(fence_indices[0::2], fence_indices[1::2]):
        masked.update(range(open_i, close_i + 1))

    toggle_indices = [
        i for i, line in enumerate(lines) if i not in masked and line.count("`") % 2
    ]
    for open_i, close_i in zip(toggle_indices[0::2], toggle_indices[1::2]):
        masked.update(range(open_i + 1, close_i + 1))

    return masked


def parse_fields(text: str) -> dict[str, str]:
    """Split goal text into {label: content} by scanning label lines.

    A field's content runs from just after its label line to the next
    recognized label line (in any order) or end of text. This is purely
    positional/syntactic — no reading of what the content says — except
    that a label-shaped line found inside a *balanced* fenced code block
    or a *balanced* inline code span is treated as content, not a
    boundary, since that is what a fence/span means in the source text.
    An unmatched opening delimiter is not a delimiter at all (see
    `_find_masked_lines`), so it never suppresses a real label after it.
    """
    lines = text.splitlines()
    masked = _find_masked_lines(lines)
    positions: list[tuple[str, int, str]] = []
    for i, line in enumerate(lines):
        if i in masked:
            continue
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
