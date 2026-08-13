#!/usr/bin/env python3
"""Read a writing-plans plan document, scope the scan to its `## Open
Questions` section only, and exit non-zero while the section holds any
unresolved question, or is itself absent or malformed.

Grammar (SSOT: `loom-code/skills/writing-plans/references/plan-format.md`
§Plan-level open-questions slot):

- The plan carries exactly one `## Open Questions` section, placed after
  the plan-level diagram slot and before Task 1.
- Fill-or-declare: the section body is EITHER a list of entries, each of
  the form `- OQ-<n> [<TOKEN>] — <question text>` (`TOKEN` is exactly
  `OPEN` or `RESOLVED`), OR the single pinned line
  `N/A — no unresolved question: <one-line reason>`.

Exit codes:

    0 — exactly one `## Open Questions` section exists, and either every
        well-formed entry is `[RESOLVED]`, or the body is the well-formed
        N/A line (a non-blank reason). Only `- OQ-<n> [TOKEN] — text`
        (a literal `-` bullet, at the line's own start after stripping
        leading whitespace) is a well-formed entry; every other line in
        the section — a soft-wrapped entry's continuation lines, blank
        lines, explanatory prose, or an `OQ-<n>` id merely mentioned in
        prose with no bracketed token attempt following it — is ignored,
        not scanned for the entry grammar. This mirrors plan-format.md's
        own scope: the `## Open Questions` grammar never forbids
        soft-wrap or prose, unlike `## Decision Log`, which pins entries
        to a single physical line explicitly.
    1 — any of: the `## Open Questions` heading is absent; more than one
        such heading is present (a malformed plan — plan-format.md
        requires exactly one); any well-formed entry is `[OPEN]` (its
        `OQ-<n>` named on stderr); the N/A line is present but its reason
        is missing/blank; a line that ATTEMPTS an entry — an `OQ-<n>` id
        followed by an opening `[`, under any bullet (`-`, `*`, `+`, `>`,
        blockquoted, or none at all) — but does not match the strict
        well-formed grammar in full (malformed, named on stderr); the
        section body is present but contains neither a recognizable
        entry nor the N/A line (e.g. prose only).

The scan is scoped to the section BODY — text between the `## Open
Questions` heading and the next level-2 (`##`) heading, or end of file.
A `[OPEN]` / `[RESOLVED]` token appearing anywhere else in the document
(ordinary prose, a Decision Log sentence, a quoted example, a fenced
code block) is out of scope and never inspected. Heading detection and
the entry scan are both fence-aware — a `## Open Questions` heading or
an `- OQ-<n>` entry quoted inside a fenced code block (a worked example
of the grammar, which plan-format.md's own `## Worked example` and
`### Wide-but-shallow example` sections do, each fencing a `## Open
Questions` heading inside a ```markdown block) is never mistaken for a
real declaration — via
`adjudication_split.iter_lines_outside_fences`, the same primitive
`check_scenario_coverage.collect_brief_item_ids` already adopted for
the identical problem. Fence-blindness is tolerable in some heading
matches and not in others, and the difference is what the match feeds:
`check_scenario_coverage._HEADING` is fence-blind by design, and its own
comment says so is "tolerable at this call site" because that value is
"only a label in a diagnostic message, never a key" — a wrong label
misdirects a reader but changes no exit code. Here the heading match IS
the exit code, so that tolerance does not transfer. (Note the sibling's
other heading regex, `_SECTION_BOUNDARY`, is NOT the tolerable case: it
slices each requirement's scope and does reach that script's exit code;
its comment claims only a "known limitation", never tolerance.)

A reused `OQ-<n>` identifier (plan-format.md's slot subsection: `OQ-<n>`
is monotonic, never renumbered, never reused) is warned about on
stderr, first-wins, mirroring `collect_brief_item_ids`' duplicate-id
handling (`check_scenario_coverage.py:270`). The warning never changes
the exit code — only an `[OPEN]` entry does.

Stdlib only, plus the sibling `adjudication_split` for its CommonMark
fence scan (`iter_lines_outside_fences`) — this file runs as a script,
so the sibling resolves off `sys.path[0]`, its own directory (same
convention as `check_scenario_coverage.py`).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from adjudication_split import iter_lines_outside_fences

# Any level-2 markdown heading line — used both to find `## Open
# Questions` and to find the NEXT one, which closes the section's scan
# window. Matched against a single line's content (via
# iter_lines_outside_fences), not the whole document, so no MULTILINE
# flag is needed here.
_HEADING_2_LINE = re.compile(r"^##\s+(.*)$")
_OPEN_QUESTIONS_HEADING_LINE = re.compile(r"^##\s+Open Questions\s*$")

# The pinned N/A line, per plan-format.md's exact wording (mirrors the
# `## Diagrams` slot's own N/A form, same file).
_NA_LINE = re.compile(r"^N/A\s*—\s*no unresolved question:\s*(?P<reason>.*)$")

# A well-formed entry: `- OQ-<n> [OPEN|RESOLVED] — <question text>`.
_ENTRY_LINE = re.compile(
    r"^-\s*OQ-(?P<n>\d+)\s*\[(?P<token>OPEN|RESOLVED)\]\s*—\s*(?P<text>.+)$"
)

# A line that starts to look like an ENTRY ATTEMPT — some combination of
# bullet-ish characters (`-`, `*`, `+`, `>`, blockquoted dash, or no
# bullet at all), an `OQ-<n>` id, and an opening `[` immediately after it
# (the start of a bracketed-token attempt) — but does not match
# `_ENTRY_LINE` in full. The net is deliberately wider than the
# well-formed grammar (`- OQ-<n> [TOKEN] — text`, still the ONLY shape
# `_ENTRY_LINE` accepts): a `*`/`+`/`>` bullet, or no bullet, must still
# fail loudly as malformed rather than silently fall through to the
# ignored-prose branch below — that silent fallthrough was the fatal
# false-negative whole-branch review found (three `[OPEN]` entries with
# non-`-` bullets exited 0 as "clean").
#
# The trailing `\s*\[` is the boundary against the opposite defect: a
# line that merely MENTIONS an `OQ-<n>` id in prose (no bracketed token
# immediately following, e.g. "OQ-1 was settled last week") must stay
# ignored as prose, not become a new false positive. Requiring an
# attempted `[` right after the id is what tells "trying to declare an
# entry" apart from "referencing an id in a sentence".
_LOOKS_LIKE_ENTRY = re.compile(r"^[-*+>\s]*OQ-\d+\s*\[")


def _find_open_questions_sections(
    plan_text: str,
) -> list[tuple[int, list[tuple[int, str]]]]:
    """Every `## Open Questions` H2 heading in `plan_text` that is NOT
    inside a fenced code block, paired with its section's BODY lines —
    each `(offset, content)`, also fence-filtered — up to the next H2
    heading (fence-filtered) or end of file. `offset` is the line's
    start index into `plan_text`, for line-number diagnostics.

    Returns one entry per real heading, in document order, so the
    caller can fail loudly on more than one (a malformed plan) instead
    of silently picking the first — the bug this scan replaced."""
    lines = list(iter_lines_outside_fences(plan_text))
    heading_idxs = [
        i for i, (_, content) in enumerate(lines)
        if _OPEN_QUESTIONS_HEADING_LINE.match(content)
    ]
    h2_idxs = [
        i for i, (_, content) in enumerate(lines)
        if _HEADING_2_LINE.match(content)
    ]
    sections = []
    for idx in heading_idxs:
        start_offset = lines[idx][0]
        next_h2 = next((j for j in h2_idxs if j > idx), None)
        end_idx = next_h2 if next_h2 is not None else len(lines)
        sections.append((start_offset, lines[idx + 1:end_idx]))
    return sections


def check_open_questions(plan_text: str) -> tuple[bool, list[str]]:
    """Returns (ok, problems) — `problems` is one diagnostic string per
    issue found, printed to stderr by the caller. `ok` is False whenever
    `problems` is non-empty.

    A reused `OQ-<n>` identifier is warned about directly to stderr as
    it is found, inline in the same scan that builds `problems` — unlike
    the sibling collectors in `check_scenario_coverage.py`
    (`collect_brief_item_ids`, `collect_folder_scenario_keys`), which
    each finish their own full scan first and print duplicate warnings
    in a separate pass afterward. The warning is not folded into
    `problems` either way — it must never flip `ok`."""
    sections = _find_open_questions_sections(plan_text)
    if not sections:
        return False, [
            "Error: no '## Open Questions' section found. The plan schema "
            "requires this section (fill-or-declare) — see "
            "loom-code/skills/writing-plans/references/plan-format.md "
            "§Plan-level open-questions slot."
        ]

    if len(sections) > 1:
        linenos = [
            plan_text.count("\n", 0, offset) + 1 for offset, _ in sections
        ]
        return False, [
            f"Error: found {len(sections)} '## Open Questions' sections "
            f"at lines {linenos} — plan-format.md requires exactly one. "
            "A duplicate is a malformed plan, not a scanning ambiguity: "
            "picking one silently could hide an unresolved question in "
            "the section that gets ignored."
        ]

    _, body_lines = sections[0]
    body = "\n".join(content for _, content in body_lines).strip()

    if not body:
        return False, [
            "Error: '## Open Questions' section is present but empty — "
            "fill-or-declare requires either recorded entries or the "
            "pinned N/A line."
        ]

    na_match = _NA_LINE.match(body)
    if na_match is not None:
        reason = na_match.group("reason").strip()
        if not reason:
            return False, [
                "Error: '## Open Questions' N/A line is missing its "
                "one-line reason — write `N/A — no unresolved question: "
                "<reason>`."
            ]
        return True, []

    problems: list[str] = []
    found_entry = False
    seen_ids: dict[str, int] = {}
    for offset, raw_line in body_lines:
        line = raw_line.strip()
        if not line:
            continue
        entry = _ENTRY_LINE.match(line)
        if entry is not None:
            found_entry = True
            oq_id = entry.group("n")
            lineno = plan_text.count("\n", 0, offset) + 1
            if oq_id in seen_ids:
                print(
                    f"Warning: OQ-{oq_id} is declared twice — line "
                    f"{seen_ids[oq_id]} and line {lineno}; OQ-<n> "
                    "identifiers are monotonic and never reused "
                    "(plan-format.md §Plan-level open-questions slot). "
                    f"Line {seen_ids[oq_id]} is recorded as the "
                    "first-seen declaration for bookkeeping only — this "
                    "does not suppress evaluation of the other entry; "
                    "every entry sharing this id, including this one, is "
                    "still checked for its own [OPEN]/[RESOLVED] status "
                    "and can still fail the check on its own.",
                    file=sys.stderr,
                )
            else:
                seen_ids[oq_id] = lineno
            if entry.group("token") == "OPEN":
                problems.append(
                    f"Error: unresolved open question OQ-{entry.group('n')} "
                    f"— {entry.group('text').strip()}"
                )
            continue
        if _LOOKS_LIKE_ENTRY.match(line):
            found_entry = True
            problems.append(
                "Error: malformed '## Open Questions' entry (does not "
                "match `- OQ-<n> [OPEN|RESOLVED] — <question text>`): "
                f"{line}"
            )
            continue
        # Any other line — a soft-wrapped entry's continuation line, a
        # blank separator, explanatory prose, or an `OQ-<n>` id merely
        # mentioned in a sentence — is ignored. Only a line that ATTEMPTS
        # an entry (an `OQ-<n>` id immediately followed by an opening `[`,
        # under any bullet or none — see `_LOOKS_LIKE_ENTRY`) is required
        # to parse; nothing else in the grammar (plan-format.md
        # §Plan-level open-questions slot) forbids soft-wrap or prose in
        # this section (contrast '## Decision Log', which pins its
        # entries to a single physical line explicitly). This is why a
        # `*`/`+`/`>`/no-bullet `OQ-<n> [` prefix still routes to the
        # malformed-entry branch above instead of falling through here —
        # a typo'd token, or a non-`-` bullet, must not go silently
        # invisible as "unrecognized prose". Requiring the trailing `[`
        # is what keeps a bare prose mention (e.g. "OQ-1 was settled last
        # week", no bracket) OUT of that branch — the opposite defect.

    if not found_entry and not problems:
        problems.append(
            "Error: '## Open Questions' section contains no recognizable "
            "entry (`- OQ-<n> [OPEN|RESOLVED] — <question text>`) and no "
            "well-formed N/A line — fill-or-declare requires one or the "
            "other."
        )

    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan a writing-plans plan's '## Open Questions' "
                    "section; exit 1 while any entry is unresolved or the "
                    "slot is absent or malformed."
    )
    parser.add_argument("plan_path", help="path to the writing-plans plan file")
    args = parser.parse_args(argv)

    plan_path = Path(args.plan_path)
    if not plan_path.is_file():
        print(f"Error: plan file not found at {plan_path}.", file=sys.stderr)
        return 1
    plan_text = plan_path.read_text(encoding="utf-8")

    ok, problems = check_open_questions(plan_text)
    for problem in problems:
        print(problem, file=sys.stderr)

    if ok:
        print(f"'## Open Questions' section in {plan_path} is clean — no "
              f"unresolved entries.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
