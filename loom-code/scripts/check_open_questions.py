#!/usr/bin/env python3
"""Read an intent document, scope the scan to its `## Open questions`
section only, and exit non-zero while the section holds any unresolved
question, or is itself absent or malformed.

Grammar (SSOT: the `intent` artifact schema in
`loom-code/contract/manifest.yaml` and `contract/templates/intent.md`):

- The intent carries exactly one `## Open questions` section (the schema
  marks it required).
- Fill-or-declare: the section body is EITHER a list of entries, each of
  the form `- OQ-<n> [<TOKEN>] — <question text>` (`TOKEN` is exactly
  `OPEN` or `RESOLVED`), OR the single pinned line
  `N/A — no unresolved question: <one-line reason>`.

Exit codes:

    0 — exactly one `## Open questions` section exists, and either every
        well-formed entry is `[RESOLVED]`, or the body is the well-formed
        N/A line (a non-blank reason). Only `- OQ-<n> [TOKEN] — text`
        (a literal `-` bullet, at the line's own start after stripping
        leading whitespace) is a well-formed entry; every other line in
        the section — a soft-wrapped entry's continuation lines, blank
        lines, explanatory prose, or an `OQ-<n>` id merely mentioned in
        prose with no bracketed token attempt following it — is ignored,
        not scanned for the entry grammar. This mirrors the intent
        template's own scope: the `## Open questions` grammar never forbids
        soft-wrap or prose.
    1 — any of: the `## Open questions` heading is absent; more than one
        such heading is present (a malformed plan — the intent schema
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
the entry scan are both fence-aware — a `## Open questions` heading or an
`- OQ-<n>` entry quoted inside a fenced code block (a worked example of
the grammar) is never mistaken for a real declaration. The heading match
IS the exit code here, so a fence-blind scan is not tolerable at this
call site.

A reused `OQ-<n>` identifier (`OQ-<n>` is monotonic, never renumbered,
never reused) is warned about on stderr, first-wins. The warning never
changes the exit code — only an `[OPEN]` entry does.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def iter_lines_outside_fences(text):
    """Yield (offset, content) for every line of `text` that is ordinary
    prose — neither inside a fenced code block nor a fence marker line
    itself. `offset` is the line's start index into `text`.

    A line-scanner state machine, stdlib only: a ``` or ~~~ line (indented
    up to 3 spaces per CommonMark) toggles fence state; a fence only closes
    on the same character with length >= the opening length (also per
    CommonMark — a longer nested fence of the other character does not
    close it). Inlined here when `adjudication_split.py` was deleted; it was
    the only surviving caller.
    """
    fence_char = None
    fence_min_len = 0
    pos = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\n").rstrip("\r")
        fence_match = FENCE_RE.match(content)
        if fence_match:
            marker = fence_match.group(1)
            char, length = marker[0], len(marker)
            if fence_char is None:
                fence_char, fence_min_len = char, length
            elif char == fence_char and length >= fence_min_len:
                fence_char, fence_min_len = None, 0
        elif fence_char is None:
            yield pos, content
        pos += len(line)

# Any level-2 markdown heading line — used both to find `## Open
# Questions` and to find the NEXT one, which closes the section's scan
# window. Matched against a single line's content (via
# iter_lines_outside_fences), not the whole document, so no MULTILINE
# flag is needed here.
_HEADING_2_LINE = re.compile(r"^##\s+(.*)$")
_OPEN_QUESTIONS_HEADING_LINE = re.compile(r"^##\s+Open questions\s*$")

# The pinned N/A line, per the intent template's exact wording.
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
    """Every `## Open questions` H2 heading in `plan_text` that is NOT
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
    it is found, inline in the same scan that builds `problems`. The
    warning is not folded into
    `problems` either way — it must never flip `ok`."""
    sections = _find_open_questions_sections(plan_text)
    if not sections:
        return False, [
            "Error: no '## Open questions' section found. The intent "
            "schema requires this section (fill-or-declare) — see the "
            "`intent` artifact in loom-code/contract/manifest.yaml."
        ]

    if len(sections) > 1:
        linenos = [
            plan_text.count("\n", 0, offset) + 1 for offset, _ in sections
        ]
        return False, [
            f"Error: found {len(sections)} '## Open questions' sections "
            f"at lines {linenos} — the intent schema requires exactly one. "
            "A duplicate is a malformed intent, not a scanning ambiguity: "
            "picking one silently could hide an unresolved question in "
            "the section that gets ignored."
        ]

    _, body_lines = sections[0]
    body = "\n".join(content for _, content in body_lines).strip()

    if not body:
        return False, [
            "Error: '## Open questions' section is present but empty — "
            "fill-or-declare requires either recorded entries or the "
            "pinned N/A line."
        ]

    na_match = _NA_LINE.match(body)
    if na_match is not None:
        reason = na_match.group("reason").strip()
        if not reason:
            return False, [
                "Error: '## Open questions' N/A line is missing its "
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
                    "(the identifiers are declared monotonic). "
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
                "Error: malformed '## Open questions' entry (does not "
                "match `- OQ-<n> [OPEN|RESOLVED] — <question text>`): "
                f"{line}"
            )
            continue
        # Any other line — a soft-wrapped entry's continuation line, a
        # blank separator, explanatory prose, or an `OQ-<n>` id merely
        # mentioned in a sentence — is ignored. Only a line that ATTEMPTS
        # an entry (an `OQ-<n>` id immediately followed by an opening `[`,
        # under any bullet or none — see `_LOOKS_LIKE_ENTRY`) is required
        # to parse; nothing else in the grammar forbids soft-wrap or
        # prose in this section. This is why a
        # `*`/`+`/`>`/no-bullet `OQ-<n> [` prefix still routes to the
        # malformed-entry branch above instead of falling through here —
        # a typo'd token, or a non-`-` bullet, must not go silently
        # invisible as "unrecognized prose". Requiring the trailing `[`
        # is what keeps a bare prose mention (e.g. "OQ-1 was settled last
        # week", no bracket) OUT of that branch — the opposite defect.

    if not found_entry and not problems:
        problems.append(
            "Error: '## Open questions' section contains no recognizable "
            "entry (`- OQ-<n> [OPEN|RESOLVED] — <question text>`) and no "
            "well-formed N/A line — fill-or-declare requires one or the "
            "other."
        )

    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan an intent's '## Open questions' section; exit 1 "
                    "while any entry is unresolved or the section is absent "
                    "or malformed."
    )
    parser.add_argument("plan_path", help="path to the intent file")
    args = parser.parse_args(argv)

    plan_path = Path(args.plan_path)
    if not plan_path.is_file():
        print(f"Error: intent file not found at {plan_path}.", file=sys.stderr)
        return 1
    plan_text = plan_path.read_text(encoding="utf-8")

    ok, problems = check_open_questions(plan_text)
    for problem in problems:
        print(problem, file=sys.stderr)

    if ok:
        print(f"'## Open questions' section in {plan_path} is clean — no "
              f"unresolved entries.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
