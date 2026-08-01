#!/usr/bin/env python3
"""Parse a plan's per-task `Files touched` declarations and `done(<sha>)` join keys.

PURPOSE — measurement prototype for the declared-vs-actual `Files touched`
check (docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md):
join each plan task's declared file set to the commit that resolved it, so a
later layer can compare declaration against `git show` reality.

SCOPE — this module is the PARSE LAYER ONLY: plan markdown in, per-task
`(declared_paths, sha_or_None)` structures out. No git calls, no verdict
logic — those are later tasks and build on `PlanParse` without changing it.

Field lines that match a field name but fail to parse are collected into
`PlanParse.parse_errors`, never silently dropped (the citation-checker
empty-pass lesson, source brief §Decision).

IDIOM PROVENANCE — the two parsing idioms are COPIED (not imported) from
loom-code/scripts/check_scenario_coverage.py:58-68:
  * the bold-optional field-line regex (`- **Field**:` and the plain
    `- Field:` form real plans use), field names swapped to
    `Files touched` / `Status`;
  * the section-boundary idiom, adapted one level up: task blocks open at
    `## Task <N>` so the boundary here is the next `## ` heading only —
    `### ` subheadings stay INSIDE a task block, exactly as upstream keeps
    `#### Scenario:` inside a `### Requirement:` scope. The upstream
    limitation carries over unchanged: a `## `-prefixed line inside a
    fenced code block is still mistaken for a real heading (accepted —
    fixture plans must not embed fenced `## Task` lines).

Token normalization (frozen key cell 10,
docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md): strip
surrounding whitespace, backticks, and a leading `./`; a `NEW: <path>`
token (plan-format.md:79) normalizes to the proposed path itself.

Stdlib only (re / dataclasses / pathlib).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

# `## Task <N>` opens a task block (plan-format.md:45).
_TASK_HDR = re.compile(r"^##\s+Task\s+(\d+)\b.*$", re.MULTILINE)

# A task block ends at the next level-2 heading (`## Task <M>` or a plan
# section like `## Notes`). `###` is deliberately NOT a boundary — see the
# module docstring's idiom-provenance note.
_TASK_BOUNDARY = re.compile(r"^##\s", re.MULTILINE)

# Bold-optional field lines (idiom copied from check_scenario_coverage.py's
# `_BRIEF_ITEM_LINE`, two deliberate deltas): `(.*)` — not `(.+)` — so an
# empty value still MATCHES the field name and can be reported as a parse
# error instead of vanishing; and the post-colon whitespace is `[ \t]*` —
# not `\s*` — because `\s` matches `\n` and would let an empty-valued line
# capture the NEXT line as its value.
_FILES_TOUCHED_LINE = re.compile(
    r"^\s*-\s*(?:\*\*)?Files touched(?:\*\*)?\s*:[ \t]*(.*?)[ \t]*$",
    re.MULTILINE)
_STATUS_LINE = re.compile(
    r"^\s*-\s*(?:\*\*)?Status(?:\*\*)?\s*:[ \t]*(.*?)[ \t]*$", re.MULTILINE)

# Progress-ledger vocabulary (plan-format.md:106): only `done(<sha>)`
# carries a join key; the other three are valid and sha-less.
_STATUS_DONE = re.compile(r"^done\(([0-9a-fA-F]{7,40})\)$")
_STATUS_SHALESS = re.compile(r"^(?:pending|claimed\(@[^)]+\)|blocked)$")

_NEW_TOKEN_PREFIX = re.compile(r"^NEW\s*:\s*")


@dataclass(frozen=True)
class TaskDeclaration:
    """One task's parsed declaration: normalized declared paths + join key."""
    declared_paths: frozenset[str]
    sha: str | None


@dataclass
class PlanParse:
    """Parse result for one plan: task number -> declaration, plus every
    field line that matched a field name but could not be parsed."""
    tasks: dict[int, TaskDeclaration] = field(default_factory=dict)
    parse_errors: list[str] = field(default_factory=list)


def _normalize_token(token: str) -> str:
    """Normalize one comma-separated `Files touched` token to a bare path.

    Frozen-key cell-10 semantics: strip surrounding whitespace, a `NEW:`
    marker, surrounding backticks, and a leading `./`. Returns "" when
    nothing remains (caller reports that as a parse error).
    """
    token = token.strip()
    token = _NEW_TOKEN_PREFIX.sub("", token)
    token = token.strip().strip("`").strip()
    if token.startswith("./"):
        token = token[2:]
    return token.strip()


def _parse_files_touched(task_no: int, value: str,
                         errors: list[str]) -> frozenset[str]:
    if not value:
        errors.append(
            f"Task {task_no}: 'Files touched' line has no parseable value")
        return frozenset()
    paths: set[str] = set()
    for raw in value.split(","):
        normalized = _normalize_token(raw)
        if normalized:
            paths.add(normalized)
        else:
            errors.append(
                f"Task {task_no}: 'Files touched' token {raw!r} "
                f"normalizes to nothing")
    return frozenset(paths)


def _parse_status(task_no: int, value: str, errors: list[str]) -> str | None:
    done = _STATUS_DONE.match(value)
    if done:
        return done.group(1)
    if not _STATUS_SHALESS.match(value):
        errors.append(
            f"Task {task_no}: 'Status' value {value!r} is not in the "
            f"ledger vocabulary (pending | claimed(@agent) | done(<sha>) "
            f"| blocked)")
    return None


def parse_plan_text(text: str) -> PlanParse:
    """Parse plan markdown into per-task declarations.

    Returns a `PlanParse` whose `tasks` maps task number ->
    `TaskDeclaration(declared_paths, sha)`; `sha` is None for any task
    without a `Status: done(<sha>)` line. Unreadable field lines land in
    `parse_errors`. A task block with no `Files touched` line at all yields
    an empty `declared_paths` without a parse error — whether that is
    acceptable is the verdict layer's policy, not the parser's.
    """
    result = PlanParse()
    for hdr in _TASK_HDR.finditer(text):
        task_no = int(hdr.group(1))
        boundary = _TASK_BOUNDARY.search(text, hdr.end())
        block = text[hdr.end():boundary.start() if boundary else len(text)]

        if task_no in result.tasks:
            result.parse_errors.append(
                f"Task {task_no}: duplicate '## Task {task_no}' heading — "
                f"keeping the first block")
            continue

        declared: frozenset[str] = frozenset()
        for match in _FILES_TOUCHED_LINE.finditer(block):
            declared |= _parse_files_touched(
                task_no, match.group(1), result.parse_errors)

        sha: str | None = None
        for match in _STATUS_LINE.finditer(block):
            parsed = _parse_status(task_no, match.group(1), result.parse_errors)
            if parsed is not None:
                sha = parsed

        result.tasks[task_no] = TaskDeclaration(declared_paths=declared, sha=sha)
    return result


def parse_plan(path: Path | str) -> PlanParse:
    """Read a plan file and parse it — thin wrapper over `parse_plan_text`."""
    return parse_plan_text(Path(path).read_text(encoding="utf-8"))
