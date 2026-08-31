#!/usr/bin/env python3
"""Render the plan-progress card from a plan file's progress headers.

Task 3 of docs/loom/plans/2026-08-06-progress-cards-and-plan-ledger.md.
The card body format is pinned ONCE in that plan's N5 block
(`family-relay.md §(a2) Progress card`) and implemented ONCE here —
same spec, two surfaces; a future format change edits both in one
commit (plan Decision Log, 2026-08-06).

Input: argv = one plan-file path. The plan's header region (everything
before the first `## ` heading) must carry a `Goal:` line and a
`Stage:` line (indented continuation lines are folded into the value,
per N1's wrapped-schema shape); the body must carry at least one
`## Task N — <name>` heading, and every task must carry a
`- Status: <value>` bullet where <value> is one of:

    done(<sha>) | implemented(<sha>) | claimed(@<agent>) | pending |
    blocked[(<why>)]

Output (stdout), field order fixed by N5:

    end-state: <goal>
    tasks: D done / I implemented / C claimed / P pending / B blocked
    [v]|[i]|[~]|[ ]|[!] T<N> <name>
    <mark> T<N> <name>              (one row per task, file order)
    stage: <stage>
    next: T<N> <name>               (first not-done task in roadmap
                                      order — earliest dependency level,
                                      then file order within it; or
                                      `close-out`)

Roadmap view (Task 1 of
docs/loom/plans/2026-08-06-progress-card-roadmap-view.md): per-task
`- Dependencies:` bullets ("none" | "Task <n> completes first" |
"Tasks <n>[, <n>]... complete first" | "Tasks <n>[, <n>]... parallel";
absent = none) derive topological levels; when any real dependency —
or a header `Steps:` title block — is present, each level's rows sit
under an A-layout separator (`-- step <L> --`, titled
`-- step <L>: <title> --`, with ` (needs: T<a> T<b>)` before the
trailing `--` when the level has prerequisites; plain ASCII hyphens,
no trailing fill — CJK-safe; no blank lines anywhere). A plan whose
tasks are all dependency-less renders the flat card unchanged
(backward compat, plan Decision Log 2026-08-06) unless it declares a
`Steps:` block. Optional per-task `- Gloss:` renders as one
six-space-indented line under its task row. `--detail T<N>` prints one
task's description / why (brief item) / acceptance / gloss verbatim
(wrapped lines folded), omitting absent fields.

Ledger writer (Task 1 of
docs/loom/plans/2026-08-06-ledger-writer-and-plan-tooling-hardening.md):
`--set-status "T<N>=<status>"` rewrites the task block's existing
`- Status:` line in place, wherever it sits in the block, and prints
the old line then the new line. The rewrite preserves the matched
line's own markup — a bold `- **Status**:` line stays bold, a plain
`- Status:` line stays plain; the writer never adds or strips bolding.
The writer's status grammar is exactly
the schema's five kinds — `pending` | `claimed(@<agent>)` |
`implemented(<sha>)` | `done(<sha>)` | `blocked` — parenthetical REQUIRED
for claimed/implemented/done,
FORBIDDEN for pending/blocked (stricter than the renderer's
`blocked(<why>)` tolerance: the writer never authors the optional
form). Loud exit 1, file untouched, on: task not found, malformed
status, zero `- Status:` lines in the block, more than one `- Status:`
line in the block (the 0.62.0 duplicate-field incident becomes
detectable instead of survivable — the writer refuses, never repairs).
The file is modified only on that one line. `--set-status` and
`--detail` are mutually exclusive.

Participating Loom writers acquire an advisory lock on the plan's stable
parent directory before reading mutation preconditions and hold it through
atomic replacement plus directory fsync. Batch CAS, `--set-status`, and
`--set-stage` share that protocol; read-only card/detail paths do not lock.
Batch CAS additionally requires the sealed transition authority issued by
`review_batch.resolve_aggregate_review` and compares the current declaration,
disposition, complete member snapshot, action, and owner union before writing.
Direct editors and filesystem tools that bypass the advisory lock are not
participants, so the pre-publish inode check detects their replacement only
best-effort and never claims to exclude an uncooperative concurrent writer.

Stale scan (Task 1 of docs/loom/plans/2026-08-10-terminal-state-gates.md):
`--stale-scan <plans-dir>` walks every `*.md` in the directory
(filename order) and lists each plan whose tasks are ALL `done(...)`
while its header `Stage:` is not `finishing` — the stranded-arc
signature. One line per candidate,
`<filename>: stage=<current> (all N tasks done)`; no candidates prints
the single line `stale-scan: clean`. Files with zero `- Status:` lines
(old-format plans, non-ledger docs) are skipped SILENTLY; a file with
Status lines that still fails to parse degrades LOUDLY per-file on
stderr and the scan continues. The scan ALWAYS exits 0 — advisory by
design: all-done + review:round-N is a legitimate transient state of a
live parallel arc, and a red exit would teach people to ignore the
gate (plan-gate advisory N1). `build_stale_scan()` is a pure function
of (filename, text) pairs, same convention as `build_card()`.

A plan missing `Goal:` or `Stage:`, having zero task headings,
carrying a statusless / unrecognized-status task, a dependency cycle
or phantom-task reference, an inline `Steps: ...` declaration (content
after the colon instead of the bare-line-plus-numbered-titles block),
or a `Steps:` count that mismatches the derived level count exits 1
with a one-line loud message naming the
offending field — a partial card is never rendered. Pure stdlib;
`build_card()` / `build_detail()` are pure functions of the plan text
(raise ValueError; the caller decides exit codes), mirroring
scripts/backlog_index.py's build/main convention.

Usage:
    python3 scripts/plan_card.py <plan-path>
    python3 scripts/plan_card.py <plan-path> --detail T<N>
    python3 scripts/plan_card.py <plan-path> --set-status "T<N>=<status>"
    python3 scripts/plan_card.py --stale-scan <plans-dir>

Exit codes: 0 = card rendered / status rewritten / stale scan completed
(with or without candidates), 1 = unreadable/unrenderable plan, refused
rewrite, or missing plans directory, 2 = usage error.
"""

from __future__ import annotations

import fcntl
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

_TASK_HEADING = re.compile(r"^## Task (\d+) — (.+?)\s*$", re.MULTILINE)
_STATUS_BULLET = re.compile(r"^- \*{0,2}Status\*{0,2}:\s*(\S.*?)\s*$", re.MULTILINE)
_STEPS_TITLE_LINE = re.compile(r"^\s+\d+\.\s+(.+?)\s*$")

# The Dependencies grammar (plan Task 1 (a)): multi-task forms take
# one-or-more comma-separated numbers and are treated IDENTICALLY —
# every listed task is a prerequisite.
_DEP_FORMS = (
    re.compile(r"^Task (\d+) completes first$"),
    re.compile(r"^Tasks (\d+(?:,\s*\d+)*) complete first$"),
    re.compile(r"^Tasks (\d+(?:,\s*\d+)*) parallel$"),
)

# Kind -> mark, in the N5-pinned counts-line order.
_MARKS = {
    "done": "[v]",
    "implemented": "[i]",
    "claimed": "[~]",
    "pending": "[ ]",
    "blocked": "[!]",
}
_DONE_STATUS = re.compile(r"done\([^()\s]+\)")
_IMPLEMENTED_STATUS = re.compile(r"implemented\([^()\s]+\)")
_CLAIMED_STATUS = re.compile(r"claimed\([^()\s]+\)")
_BLOCKED_STATUS = re.compile(r"blocked(?:\([^()\s]+\))?")


def _header_value(header: str, key: str) -> str | None:
    """The value of a `<key>: ...` header line, with indented continuation
    lines folded in (N1 pins the wrapped shape: continuations are
    indented). None when the key line is absent; a present-but-empty
    value comes back as "" (callers treat both as missing)."""
    lines = header.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith(f"{key}:"):
            continue
        parts = [line[len(key) + 1 :].strip()]
        for continuation in lines[i + 1 :]:
            if continuation[:1] in (" ", "\t") and continuation.strip():
                parts.append(continuation.strip())
            else:
                break
        return " ".join(part for part in parts if part)
    return None


def safety_bearing(plan_text: str) -> tuple[str, str] | None:
    """The parsed `Safety-bearing:` header value as (kind, reason), where
    kind is `"yes"` or `"no"` — None when the header is absent (Task 6 of
    docs/loom/plans/2026-08-31-adversarial-audit-station.md; consumed by
    `finishing-a-development-branch`'s trigger). Raises ValueError, naming
    the accepted forms, when the header is present but its value does not
    start with `yes — ` or `no — `."""
    header, _, _ = plan_text.partition("\n## ")
    value = _header_value(header, "Safety-bearing")
    if value is None:
        return None
    for kind in ("yes", "no"):
        prefix = f"{kind} — "
        if value.startswith(prefix):
            return kind, value[len(prefix):]
    raise ValueError(
        f"'Safety-bearing:' value '{value}' outside 'yes — <reason>' / "
        "'no — <reason>'"
    )


def _parse_steps(header: str) -> list[str] | None:
    """The header `Steps:` block's titles, in order — a bare `Steps:`
    line followed by indented numbered lines (`  1. <title>`). None when
    the block is absent; a declared-but-empty block comes back as []
    (the level-count check then fails loud rather than guessing). An
    inline declaration (`Steps: a / b / c` — content after the colon)
    raises ValueError naming the correct format, never a titleless card
    (Task 2 of the 2026-08-06 ledger-writer-hardening plan)."""
    lines = header.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("Steps:"):
            continue
        if line[len("Steps:") :].strip():
            raise ValueError(
                f"inline 'Steps:' declaration ('{line.strip()}') — the "
                "schema is a bare 'Steps:' line followed by indented "
                "numbered titles ('  1. <title>')"
            )
        titles = []
        for candidate in lines[i + 1 :]:
            match = _STEPS_TITLE_LINE.match(candidate)
            if match is None:
                break
            titles.append(match.group(1))
        return titles
    return None


def _bullet_lines(block: str, key: str) -> list[str] | None:
    """The raw lines of a task-block bullet `- <key>: ...` — its
    first-line remainder plus indented continuation lines (sub-bullets
    included), stopping at the first blank or column-0 line. The bullet
    regex mirrors _STATUS_BULLET's `\\*{0,2}` bold tolerance. None when
    the bullet is absent."""
    pattern = re.compile(rf"^- \*{{0,2}}{re.escape(key)}\*{{0,2}}:\s*(.*?)\s*$")
    lines = block.splitlines()
    for i, line in enumerate(lines):
        match = pattern.match(line)
        if match is None:
            continue
        collected = [match.group(1)]
        for continuation in lines[i + 1 :]:
            if continuation[:1] in (" ", "\t") and continuation.strip():
                collected.append(continuation)
            else:
                break
        return collected
    return None


def _bullet_value(block: str, key: str) -> str | None:
    """A bullet's value folded to one line (wrapped continuations joined
    with single spaces). None when the bullet is absent."""
    lines = _bullet_lines(block, key)
    if lines is None:
        return None
    return " ".join(part.strip() for part in lines if part.strip())


def _parse_dependencies(value: str, number: int, name: str) -> list[int]:
    """The prerequisite task numbers a `- Dependencies:` value declares.
    "none" -> []; the three grammar forms are identical for level
    derivation. A value outside the grammar fails loud — never a
    silently-flat card over an unread dependency."""
    if value == "none":
        return []
    for form in _DEP_FORMS:
        match = form.match(value)
        if match is not None:
            return [int(n) for n in re.split(r",\s*", match.group(1))]
    raise ValueError(
        f"task T{number} ({name}) has Dependencies '{value}', outside "
        "none / 'Task <n> completes first' / "
        "'Tasks <n>, <n> complete first' / 'Tasks <n>, <n> parallel'"
    )


def _classify(status: str) -> str | None:
    """One of the five kinds, or None for a value outside the vocabulary.
    Done/claimed carry a mandatory parenthesized payload (`done(<sha>)`,
    `claimed(<who>)` — plan Task 3 pins the `(`-anchored match); blocked
    may carry an optional `(<why>)`."""
    if _DONE_STATUS.fullmatch(status) is not None:
        return "done"
    if _IMPLEMENTED_STATUS.fullmatch(status) is not None:
        return "implemented"
    if _CLAIMED_STATUS.fullmatch(status) is not None:
        return "claimed"
    if status == "pending":
        return "pending"
    if _BLOCKED_STATUS.fullmatch(status) is not None:
        return "blocked"
    return None


def _task_blocks(text: str) -> list[tuple[int, str, str]]:
    """Every `## Task N — <name>` as (number, name, block-text), in file
    order — the block runs to the next `## ` heading or EOF."""
    blocks: list[tuple[int, str, str]] = []
    for match in _TASK_HEADING.finditer(text):
        number, name = int(match.group(1)), match.group(2)
        next_heading = text.find("\n## ", match.end())
        block = text[match.end() : next_heading if next_heading != -1 else len(text)]
        blocks.append((number, name, block))
    return blocks


def _parse_tasks(text: str) -> list[tuple[int, str, str, list[int], str | None]]:
    """Every task as (number, name, kind, deps, gloss), in file order.

    Raises ValueError on a statusless task (old-format plan), a status
    outside the five kinds, or a Dependencies value outside the grammar
    — never silently drops or miscounts a task.
    """
    tasks: list[tuple[int, str, str, list[int], str | None]] = []
    for number, name, block in _task_blocks(text):
        status_match = _STATUS_BULLET.search(block)
        if status_match is None:
            raise ValueError(
                f"task T{number} ({name}) has no '- Status:' line — "
                "either an old-format plan predating the default-on ledger, "
                "or a Status line the parser does not recognize"
            )
        kind = _classify(status_match.group(1))
        if kind is None:
            raise ValueError(
                f"task T{number} ({name}) has status "
                f"'{status_match.group(1)}', outside "
                "done(...)/implemented(...)/claimed(...)/pending/blocked"
            )
        deps_value = _bullet_value(block, "Dependencies")
        deps = (
            _parse_dependencies(deps_value, number, name)
            if deps_value is not None
            else []
        )
        gloss = _bullet_value(block, "Gloss")
        tasks.append((number, name, kind, deps, gloss or None))
    return tasks


def _derive_levels(
    tasks: list[tuple[int, str, str, list[int], str | None]],
) -> dict[int, int]:
    """Topological level per task number: 1 for prerequisite-less tasks,
    else 1 + max(prerequisite levels). Raises ValueError on a reference
    to a nonexistent task or a dependency cycle, naming it."""
    deps_by_number = {number: deps for number, _, _, deps, _ in tasks}
    names = {number: name for number, name, _, _, _ in tasks}
    for number, deps in deps_by_number.items():
        for dep in deps:
            if dep not in deps_by_number:
                raise ValueError(
                    f"task T{number} ({names[number]}) depends on "
                    f"nonexistent task T{dep}"
                )
    levels: dict[int, int] = {}

    def resolve(number: int, stack: list[int]) -> int:
        if number in levels:
            return levels[number]
        if number in stack:
            cycle = stack[stack.index(number) :] + [number]
            raise ValueError(
                "dependency cycle: " + " -> ".join(f"T{n}" for n in cycle)
            )
        stack.append(number)
        level = 1 + max(
            (resolve(dep, stack) for dep in deps_by_number[number]), default=0
        )
        stack.pop()
        levels[number] = level
        return level

    for number in deps_by_number:
        resolve(number, [])
    return levels


def build_card(text: str) -> str:
    """The card body per the N5-pinned field order (module docstring).

    Pure function of the plan text: no filesystem reads, no writes.
    Raises ValueError (never exits the process itself — the caller
    decides exit codes) when the plan cannot render a complete card.
    """
    header, _, _ = text.partition("\n## ")

    goal = _header_value(header, "Goal")
    if not goal:
        raise ValueError("plan has no 'Goal:' header line")
    stage = _header_value(header, "Stage")
    if not stage:
        raise ValueError("plan has no 'Stage:' header line")
    safety = safety_bearing(text)

    tasks = _parse_tasks(text)
    if not tasks:
        raise ValueError("plan has no '## Task N — <name>' headings")

    steps = _parse_steps(header)
    levels = _derive_levels(tasks)
    level_count = max(levels.values())
    if steps is not None and len(steps) != level_count:
        raise ValueError(
            f"'Steps:' block declares {len(steps)} title(s) but the plan "
            f"derives {level_count} dependency level(s)"
        )

    counts = {kind: 0 for kind in _MARKS}
    for _, _, kind, _, _ in tasks:
        counts[kind] += 1

    lines = [
        f"end-state: {goal}",
        "tasks: "
        + " / ".join(
            f"{counts[kind]} {kind}"
            for kind in _MARKS
            if kind != "implemented" or counts[kind]
        ),
    ]

    def rows(subset: list) -> list[str]:
        out = []
        for number, name, kind, _, gloss in subset:
            out.append(f"{_MARKS[kind]} T{number} {name}")
            if gloss is not None:
                out.append(f"      {gloss}")
        return out

    # Stepped A-layout only when a real dependency or a declared Steps
    # title exists — an all-none plan keeps the flat card byte-unchanged
    # (backward compat + Steps-opt-in exception, Decision Log 2026-08-06).
    if steps is None and not any(deps for _, _, _, deps, _ in tasks):
        lines.extend(rows(tasks))
    else:
        for level in range(1, level_count + 1):
            level_tasks = [task for task in tasks if levels[task[0]] == level]
            separator = f"-- step {level}"
            if steps is not None:
                separator += f": {steps[level - 1]}"
            needs = sorted({dep for _, _, _, deps, _ in level_tasks for dep in deps})
            if needs:
                separator += " (needs: " + " ".join(f"T{n}" for n in needs) + ")"
            lines.append(separator + " --")
            lines.extend(rows(level_tasks))

    lines.append(f"stage: {stage}")

    not_done = [
        (levels[number], index, number, name)
        for index, (number, name, kind, _, _) in enumerate(tasks)
        if kind != "done"
    ]
    if not_done:
        _, _, number, name = min(not_done, key=lambda item: item[:2])
        next_task = f"T{number} {name}"
    else:
        next_task = "close-out"
    lines.append(f"next: {next_task}")
    if safety is not None:
        lines.append(f"safety-bearing: {safety[0]} — {safety[1]}")
    else:
        lines.append("safety-bearing: N/A — header absent")

    return "\n".join(lines) + "\n"


def _is_table_row(raw: str) -> bool:
    """Whether a field-body continuation line is a markdown table row
    — its stripped content starts with the pipe delimiter. Shared by
    both `build_detail` continuation loops so a table row is never
    folded into surrounding prose or bullet text in either the
    Description or the Acceptance field, wherever it occurs."""
    return raw.strip().startswith("|")


def _fold_sub_bullets(raw_lines: list[str]) -> list[tuple[str, "list[str] | str"]]:
    """Walk a field's continuation lines (after its own first line)
    into ordered segments, preserving the order they appear in:

    - a `- ` line opens a `("bullet", [text])` segment; a later line
      that is neither a `- ` line nor a table row folds into the
      LAST-opened bullet regardless of what came between (including a
      table row) — the pre-existing behaviour, unchanged;
    - a table row (`_is_table_row`) is never folded into a bullet or
      into prose — always its own `("table", raw)` segment, verbatim,
      wherever it occurs;
    - a line before any bullet has opened, that is not a table row,
      is its own `("pre", raw)` segment — the caller decides whether
      to fold it into prose (Description) or emit it standalone
      (Acceptance).

    Shared by the Description and Acceptance loops in `build_detail`
    — the same table-row and bullet-continuation handling, extracted
    once rather than duplicated a third time (Task 6 revision round 1,
    docs/loom/plans/2026-08-19-field-value-microstructure.md)."""
    items: list[list[str]] = []
    segments: list[tuple[str, "list[str] | str"]] = []
    for raw in raw_lines:
        sub_bullet = re.match(r"^\s*[-*+]\s+(.*?)\s*$", raw)
        if sub_bullet is not None:
            items.append([sub_bullet.group(1)])
            segments.append(("bullet", items[-1]))
        elif _is_table_row(raw):
            segments.append(("table", raw))
        elif items:
            items[-1].append(raw.strip())
        else:
            segments.append(("pre", raw))
    return segments


def build_detail(text: str, task_number: int) -> str:
    """One task's fields for `--detail T<N>`: the task line, then
    description / why (brief item) / acceptance (sub-bullets indented) /
    gloss — transcribed verbatim from the task block with wrapped lines
    folded, absent fields omitted. Pure function; raises ValueError on
    an unknown task number."""
    for number, name, block in _task_blocks(text):
        if number == task_number:
            break
    else:
        raise ValueError(
            f"--detail T{task_number}: no '## Task {task_number}' heading "
            "in the plan"
        )

    lines = [f"T{number} {name}"]
    description_lines = _bullet_lines(block, "Description")
    if description_lines is not None:
        sentence_parts = [description_lines[0]]
        rendered: list[str] = []
        for kind, payload in _fold_sub_bullets(description_lines[1:]):
            if kind == "bullet":
                rendered.append("  " + " ".join(payload))
            elif kind == "table":
                rendered.append(payload)
            else:  # "pre" — folds into the sentence, never a table row
                sentence_parts.append(payload.strip())
        description = " ".join(part.strip() for part in sentence_parts if part.strip())
        if description:
            lines.append(f"description: {description}")
            lines.extend(rendered)
    why = _bullet_value(block, "Brief item covered")
    if why:
        lines.append(f"why (brief item): {why}")
    acceptance = _bullet_lines(block, "Acceptance")
    if acceptance is not None:
        lines.append(f"acceptance: {acceptance[0]}".rstrip())
        for kind, payload in _fold_sub_bullets(acceptance[1:]):
            if kind == "bullet":
                lines.append("  " + " ".join(payload))
            else:  # "table" or "pre" — both emitted verbatim
                lines.append(payload)
    gloss = _bullet_value(block, "Gloss")
    if gloss:
        lines.append(f"gloss: {gloss}")

    return "\n".join(lines) + "\n"


# The writer's status grammar (plan Task 1): exactly the schema's four
# kinds — parenthetical REQUIRED for claimed/done (non-empty, no nested
# parens; claimed's payload is `@<agent>`), FORBIDDEN for pending/blocked.
# Stricter than _classify: the writer never authors `blocked(<why>)`.
_SET_STATUS_GRAMMAR = re.compile(
    rf"pending|blocked|{_DONE_STATUS.pattern}|{_IMPLEMENTED_STATUS.pattern}|"
    r"claimed\(@[^()\s]+\)"
)


def set_status(text: str, task_number: int, status: str) -> tuple[str, str, str]:
    """The plan text with task T<task_number>'s single `- Status:` line
    rewritten to `- Status: <status>`, plus the old and new line —
    every other byte unchanged. Pure function (the caller writes the
    file and decides exit codes); raises ValueError on a malformed
    status, a missing task heading, and zero or duplicate `- Status:`
    lines in the task block (refuse, never repair — plan Decisions)."""
    if _SET_STATUS_GRAMMAR.fullmatch(status) is None:
        raise ValueError(
            f"--set-status: status '{status}' outside pending / "
            "claimed(@<agent>) / implemented(<sha>) / done(<sha>) / "
            "blocked — parenthetical REQUIRED for claimed/implemented/done, "
            "FORBIDDEN for pending/blocked"
        )
    for heading in _TASK_HEADING.finditer(text):
        if int(heading.group(1)) == task_number:
            break
    else:
        raise ValueError(
            f"--set-status T{task_number}: no '## Task {task_number}' "
            "heading in the plan"
        )
    next_heading = text.find("\n## ", heading.end())
    block_end = next_heading if next_heading != -1 else len(text)
    block = text[heading.end() : block_end]
    status_lines = list(_STATUS_BULLET.finditer(block))
    if not status_lines:
        raise ValueError(
            f"task T{task_number} ({heading.group(2)}) has no "
            "'- Status:' line to rewrite — the writer never inserts one"
        )
    if len(status_lines) > 1:
        raise ValueError(
            f"task T{task_number} ({heading.group(2)}) has "
            f"{len(status_lines)} '- Status:' lines — duplicate field; "
            "fix the plan by hand, the writer refuses to pick one"
        )
    # Span the physical line, not the regex match: _STATUS_BULLET's
    # trailing `\s*$` may extend across a following blank line in
    # MULTILINE mode, and the rewrite must never touch that newline.
    start = heading.end() + status_lines[0].start()
    line_break = text.find("\n", start)
    end = line_break if line_break != -1 else len(text)
    old_line = text[start:end]
    label = "- **Status**:" if old_line.startswith("- **Status**:") else "- Status:"
    new_line = f"{label} {status}"
    return text[:start] + new_line + text[end:], old_line, new_line


# SHA-payload expansion (R11b): the writer never lets an operator-typed
# short ref reach the ledger — `done(<ref>)` / `implemented(<ref>)` are
# expanded to the ref's full 40-hex SHA at write time, so every write
# already satisfies batch_review_cli._IMPLEMENTED's 40-hex-only rule.
_STATUS_SHA_REF = re.compile(r"(done|implemented)\(([^()\s]+)\)")
_FULL_SHA = re.compile(r"[0-9a-f]{40}")


def _git_repo_root(start: Path) -> Path | None:
    """The git worktree root containing directory `start`, or None when
    `start` is not inside a git repo (or `git` is not runnable) — SHA
    expansion is then skipped rather than crashing the writer."""
    try:
        result = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def _expand_status_sha_ref(status: str, plan_path: Path) -> str:
    """`status` with a `done(<ref>)` / `implemented(<ref>)` payload
    expanded to the ref's full 40-hex SHA via `git rev-parse`, resolved
    against the git repo containing `plan_path`. Every other status
    (`pending` / `claimed(@<agent>)` / `blocked`) and an already-40-hex
    payload pass through unchanged (no git call needed for the latter).
    Raises ValueError, naming the ref, when the plan sits inside a git
    repo but the ref does not resolve to a commit there. When the plan
    is not inside any git repo (an isolated fixture, e.g.), the ref is
    left exactly as typed — there is no repository to resolve it
    against, and refusing here would reject the CLI's own test
    fixtures, not the operator's real plan files.

    Grounding (external-surface category 4, CLI flag): the
    `git rev-parse --verify <ref>^{commit}` form mirrors the in-repo
    idiom at `loom-code/scripts/review_scope.py` (`_git(repo,
    "rev-parse", "--verify", f"{sha}^{{commit}}")`) — the `^{commit}`
    peel rejects trees/blobs and neutralises flag-shaped refs."""
    match = _STATUS_SHA_REF.fullmatch(status)
    if match is None:
        return status
    kind, ref = match.groups()
    if _FULL_SHA.fullmatch(ref) is not None:
        return status
    repo_root = _git_repo_root(plan_path.resolve().parent)
    if repo_root is None:
        return status
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--verify", f"{ref}^{{commit}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            f"--set-status: ref '{ref}' does not resolve to a commit in "
            f"{repo_root}"
        )
    return f"{kind}({result.stdout.strip()})"


def dependency_is_ready(
    producer_status: str,
    producer_batch: str | None,
    consumer_batch: str | None,
) -> bool:
    """Whether one dependency edge releases its consumer.

    ``done`` releases every edge. ``implemented`` releases only when both
    endpoints have the same explicit Batch identity; absent/uncertain identity
    therefore fails closed to requiring ``done``.
    """
    if _DONE_STATUS.fullmatch(producer_status) is not None:
        return True
    return (
        _IMPLEMENTED_STATUS.fullmatch(producer_status) is not None
        and producer_batch is not None
        and producer_batch == consumer_batch
    )


def _review_batch_oracle():
    """Load the sibling schema oracle without relying on cwd/sys.path.

    Deferred import: a standalone `plan_card.py` copy without its
    `sibling_import.py` sibling (this repo's plan-card shim/standalone
    convention, module docstring) must still import cleanly for every
    batch-free plan — only a plan declaring `## Review Batches` ever
    reaches this function."""
    try:
        import sibling_import

        return sibling_import.load_sibling(
            "check_review_batches.py", name="plan_card_review_batch_oracle"
        )
    except ImportError as exc:
        raise ValueError("Review Batch schema oracle cannot be loaded") from exc


def _validated_batch_snapshot(
    text: str, batch_id: str
) -> tuple[tuple[int, ...], dict[str, object]]:
    """Exact members and declaration after the schema oracle accepts plan."""
    oracle = _review_batch_oracle()
    fields = oracle.execution_projection_fields(text, batch_id)
    return tuple(
        int(member["task_id"].split()[1])
        for member in fields["members"]
    ), fields


def _bullet_count(block: str, key: str) -> int:
    """How many primary `- <key>: ...` bullet lines appear in block (the
    pattern mirrors `_bullet_lines`, but counts every occurrence rather
    than stopping at the first — used to detect a duplicated bullet
    `_bullet_value`'s single-first-match would otherwise hide)."""
    pattern = re.compile(rf"^- \*{{0,2}}{re.escape(key)}\*{{0,2}}:\s*(.*?)\s*$")
    return sum(1 for line in block.splitlines() if pattern.match(line))


def _batch_member_done_refusal(
    text: str, task_number: int, status: str
) -> str | None:
    """None when `--set-status` may write `status` to task T<task_number>
    of the given locked `text`; otherwise the refusal message. Fires
    only for a `done(<sha>)` write to a task whose own `- Review
    disposition:` line is `batch(<id>)` — `batch_review_cli.py
    apply-result` is the only legitimate writer of a declared batch
    member's `done`, so crash recovery can trust a `done` it finds
    (plan Task 5). Fails closed: a missing or duplicated `- Review
    disposition:` line refuses when the plan declares a `## Review
    Batches` section (schema-invalid — a member could be hiding behind
    the missing/duplicated line, and `_bullet_value` only ever returns
    the first match) and passes through when there is no such section
    (an old-format plan predating the disposition field); a disposition
    value that does not fullmatch the oracle's own disposition grammar,
    an unknown/schema-invalid batch id (the oracle's `ValueError`), and
    a disposition naming a batch whose `Members` omit this task all
    refuse too. The disposition and section regexes are the sibling
    schema oracle's `_DISPOSITION` / `_BATCH_SECTION` (mirrored, not
    reimplemented) so a grammar change there cannot silently widen what
    this guard accepts.

    The oracle (`_review_batch_oracle`, a sibling-file import of
    `check_review_batches.py`) is loaded only once the literal string
    `## Review Batches` is seen in `text` — a plan without that heading
    never reaches the oracle call at all (plan Task 5 invariant), so a
    `plan_card.py` copied standalone without its sibling (a documented
    use of this repo's plan-card shim/standalone convention) still
    works for every batch-free plan. That presence check is a plain
    substring test, not the batch-id GRAMMAR — the grammar itself stays
    with the oracle, mirrored nowhere else. When the heading IS present
    but the sibling is missing or unreadable, the oracle load raises
    OSError; this guard turns that into a ValueError so `main()`'s
    existing `except ValueError` prints `plan_card: FAIL —` instead of
    an uncaught traceback — failing closed rather than crashing.

    Callers pass the SAME `text` they are about to mutate, evaluated
    from inside `_publish_cli_mutation`'s lock (the `mutation`
    callable idiom already used by `set_status`/`set_stage`) — the
    guard and the write must see identical bytes, never a read taken
    outside that lock."""
    if _DONE_STATUS.fullmatch(status) is None:
        return None
    for number, _name, block in _task_blocks(text):
        if number == task_number:
            disposition = _bullet_value(block, "Review disposition")
            disposition_count = _bullet_count(block, "Review disposition")
            break
    else:
        return None
    # Literal-string presence test, not the oracle's `_BATCH_SECTION`
    # grammar: a standalone `plan_card.py` copy (documented sibling-free
    # use, this repo's plan-card shim/standalone convention) must never
    # reach the oracle call for a plan with no `## Review Batches`
    # section at all (plan Task 5 invariant) — the batch-id GRAMMAR
    # itself still lives only with the oracle, mirrored nowhere else.
    if "## Review Batches" not in text:
        return None
    try:
        oracle = _review_batch_oracle()
    except OSError as exc:
        raise ValueError(f"Review Batch schema oracle cannot be loaded: {exc}") from exc
    has_batches_section = oracle._BATCH_SECTION.search(text) is not None
    if disposition is None or disposition_count != 1:
        if has_batches_section:
            if disposition is None:
                return (
                    f"task T{task_number} has no '- Review disposition:' line "
                    "while the plan declares a '## Review Batches' section — "
                    "schema-invalid, refusing rather than risk a hidden batch "
                    "member"
                )
            return (
                f"task T{task_number} has {disposition_count} "
                "'- Review disposition:' lines while the plan declares a "
                "'## Review Batches' section — schema-invalid, refusing "
                "rather than trust only the first"
            )
        return None
    match = oracle._DISPOSITION.fullmatch(disposition)
    if match is None:
        return (
            f"task T{task_number} has '- Review disposition: {disposition}' "
            "which does not match the plan schema's disposition grammar — "
            "schema-invalid, refusing rather than risk a hidden batch member"
        )
    batch_id = match.group(1)
    if batch_id is None:
        return None
    try:
        fields = oracle.execution_projection_fields(text, batch_id)
    except ValueError as exc:
        return (
            f"batch '{batch_id}' schema invalid ({exc}) — refusing the "
            "direct write; only `batch_review_cli.py apply-result` may "
            "write a batch member's done"
        )
    members = {int(member["task_id"].split()[1]) for member in fields["members"]}
    if task_number not in members:
        return (
            f"task T{task_number} declares '- Review disposition: "
            f"batch({batch_id})' but batch '{batch_id}'s Members do not "
            "list it — schema-invalid, fix the plan; only "
            "`batch_review_cli.py apply-result` writes a member's done"
        )
    return (
        f"task T{task_number} is a declared member of batch '{batch_id}' — "
        "done(<sha>) may only be written by `batch_review_cli.py "
        "apply-result`, refusing the direct write"
    )


def _transition_authority_validator(authority: object):
    """Resolve only a validator implemented by the sibling authority class."""
    validator = getattr(authority, "_validate_for_plan_card", None)
    function = getattr(validator, "__func__", None)
    code = getattr(function, "__code__", None)
    if code is None:
        return None
    try:
        exact_path = Path(code.co_filename).resolve()
    except OSError:
        return None
    if exact_path != Path(__file__).with_name("review_batch.py").resolve():
        return None
    return validator


def _task_statuses(text: str) -> dict[int, str]:
    statuses: dict[int, str] = {}
    for number, name, block in _task_blocks(text):
        matches = list(_STATUS_BULLET.finditer(block))
        if len(matches) != 1:
            raise ValueError(
                f"task T{number} ({name}) must have exactly one '- Status:' line"
            )
        statuses[number] = matches[0].group(1)
    return statuses


def _same_member_sha(implemented: str, done: str) -> bool:
    return (
        _IMPLEMENTED_STATUS.fullmatch(implemented) is not None
        and _DONE_STATUS.fullmatch(done) is not None
        and implemented[len("implemented(") : -1] == done[len("done(") : -1]
    )


def _atomic_replace_text(
    path: Path,
    text: str,
    before_replace: Callable[[], None] | None,
    mode: int,
    expected_identity: tuple[int, int],
) -> bool:
    """Durably stage bytes beside ``path``, then expose them in one replace."""
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if before_replace is not None:
            before_replace()
        try:
            current = path.stat()
        except OSError:
            return False
        if (current.st_dev, current.st_ino) != expected_identity:
            return False
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return True
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _open_locked_current(path: Path) -> tuple[int, str, os.stat_result]:
    """Lock and read the inode currently named by ``path``.

    A waiter may have opened the old inode just before another caller's
    ``os.replace``. Rechecking device/inode after the lock is acquired makes
    that waiter retry against the replacement instead of applying stale bytes.
    """
    while True:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            opened = os.fstat(descriptor)
            current = path.stat()
            if (opened.st_dev, opened.st_ino) == (
                current.st_dev,
                current.st_ino,
            ):
                chunks: list[bytes] = []
                while chunk := os.read(descriptor, 1024 * 1024):
                    chunks.append(chunk)
                text = b"".join(chunks).decode("utf-8")
                return descriptor, text, opened
        except BaseException:
            os.close(descriptor)
            raise
        os.close(descriptor)


@contextmanager
def _plan_directory_lock(path: Path):
    """Serialize participating Loom plan writers on the stable parent dir."""
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _batch_replacements_finalize(replacements: dict[int, str]) -> bool:
    """True iff every replacement value is a done(<sha>) status.

    ``set(replacements) == member_set`` looks like "every member changes"
    but says nothing about the direction of that change — a reopen whose
    owner union happens to be the whole membership (every replacement is
    ``pending``) matches it too. Only the replacement VALUES tell finalize
    and reopen apart.
    """
    return bool(replacements) and all(
        _DONE_STATUS.fullmatch(status) is not None
        for status in replacements.values()
    )


def _validate_batch_transition(
    members: tuple[int, ...],
    execution_projection_fields: tuple[object, ...],
    expected_statuses: dict[int, str],
    replacements: dict[int, str],
    transition_authority: object,
) -> bool:
    """Validate one authorized finalization or owner-union reopen."""
    member_set = set(members)
    finalizing = _batch_replacements_finalize(replacements)
    action = "finalize" if finalizing else "reopen"
    owners = (
        tuple(f"Task {number}" for number in members if number in replacements)
        if action == "reopen"
        else ()
    )
    authority_statuses = tuple(
        (f"Task {number}", expected_statuses.get(number, ""))
        for number in members
    )
    authority_validator = _transition_authority_validator(transition_authority)
    if authority_validator is None:
        return False
    if not authority_validator(
        execution_projection_fields=execution_projection_fields,
        member_statuses=authority_statuses,
        action=action,
        reopen_owners=owners,
    ):
        return False
    if set(expected_statuses) != member_set:
        raise ValueError("expected member set does not equal the validated Batch")
    if not replacements or not set(replacements).issubset(member_set):
        raise ValueError("replacement owner set is empty or outside the member set")
    if any(
        _IMPLEMENTED_STATUS.fullmatch(status) is None
        for status in expected_statuses.values()
    ):
        raise ValueError(
            "expected member snapshot must contain exact implemented(<sha>)"
        )
    if finalizing:
        if any(
            not _same_member_sha(expected_statuses[number], replacements[number])
            for number in members
        ):
            raise ValueError("finalization must preserve every member SHA")
    elif any(status != "pending" for status in replacements.values()):
        raise ValueError("an owner-union reopen may replace statuses only with pending")
    return True


def _atomic_batch_status_update_locked(
    plan_path: Path,
    batch_id: str,
    expected_statuses: dict[int, str],
    replacements: dict[int, str],
    *,
    transition_authority: object,
    before_replace: Callable[[], None] | None = None,
) -> bool:
    """Compare and atomically replace one validated Batch status snapshot.

    ``expected_statuses`` must be the Batch's complete implemented member set.
    ``replacements`` is either every member's member-SHA-preserving ``done``
    status (PASS finalization), or a non-empty owner subset changed to
    ``pending`` (attributable finding union). A stale snapshot returns False
    with zero mutation; malformed sets or transitions raise ValueError.
    """
    path = Path(plan_path)
    descriptor, text, opened = _open_locked_current(path)
    try:
        try:
            members, execution_projection_fields = _validated_batch_snapshot(text, batch_id)
        except ValueError:
            return False
        if not _validate_batch_transition(
            members,
            execution_projection_fields,
            expected_statuses,
            replacements,
            transition_authority,
        ):
            return False
        finalizing = _batch_replacements_finalize(replacements)

        current = _task_statuses(text)
        current_snapshot = {number: current[number] for number in members}
        target_snapshot = {
            number: replacements.get(number, expected_statuses[number])
            for number in members
        }
        if current_snapshot == target_snapshot:
            return True
        if current_snapshot != expected_statuses:
            if finalizing and all(
                current_snapshot[number]
                in {expected_statuses[number], replacements[number]}
                for number in members
            ) and any(
                current_snapshot[number] == replacements[number]
                for number in members
            ):
                raise ValueError(
                    "torn Batch state mixes implemented and done members"
                )
            return False

        new_text = text
        for number in members:
            if number in replacements:
                new_text, _, _ = set_status(
                    new_text, number, replacements[number]
                )
        return _atomic_replace_text(
            path,
            new_text,
            before_replace,
            opened.st_mode & 0o7777,
            (opened.st_dev, opened.st_ino),
        )
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def atomic_batch_status_update(
    plan_path: Path,
    batch_id: str,
    expected_statuses: dict[int, str],
    replacements: dict[int, str],
    *,
    transition_authority: object,
    before_replace: Callable[[], None] | None = None,
) -> bool:
    """Run Batch CAS while holding the shared Loom plan-directory lock."""
    path = Path(plan_path)
    with _plan_directory_lock(path):
        return _atomic_batch_status_update_locked(
            path,
            batch_id,
            expected_statuses,
            replacements,
            transition_authority=transition_authority,
            before_replace=before_replace,
        )


def _publish_cli_mutation(
    path: Path,
    mutation: Callable[[str], tuple[str, str, str]],
) -> tuple[str, str, str]:
    """Read and atomically publish one CLI mutation under the shared lock."""
    with _plan_directory_lock(path):
        descriptor, text, opened = _open_locked_current(path)
        try:
            new_text, old_line, new_line = mutation(text)
            published = _atomic_replace_text(
                path,
                new_text,
                None,
                opened.st_mode & 0o7777,
                (opened.st_dev, opened.st_ino),
            )
            if not published:
                raise ValueError("plan changed before CLI mutation publish")
            return new_text, old_line, new_line
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)


def set_stage(text: str, new_value: str) -> tuple[str, str, str]:
    """The plan text with the header `Stage:` line's value replaced by
    `new_value`, plus the old and new line — every other byte unchanged.
    Pure function (the caller writes the file and decides exit codes);
    raises ValueError when the plan has no `Stage:` header line, or
    `new_value` is empty/whitespace-only. Free-text value — stage
    vocabulary evolves, no enum validation (plan Task 1 Decisions).

    A wrapped value (indented continuation lines, `_header_value`'s
    folded shape) has its ENTIRE span replaced — the `Stage:` line plus
    every continuation line — never just the first line, which would
    leave a stale orphan continuation that `_header_value` folds back in
    on the next read (Finding 2, fix round)."""
    header, sep, rest = text.partition("\n## ")
    match = re.search(r"^Stage:.*$(?:\n[ \t]+\S.*$)*", header, re.MULTILINE)
    if match is None:
        raise ValueError("plan has no 'Stage:' header line")
    if not new_value.strip():
        raise ValueError("--set-stage: value is empty or whitespace-only")
    if len(new_value.splitlines()) > 1:
        raise ValueError("--set-stage: value must be a single line")
    old_line = match.group(0)
    new_line = f"Stage: {new_value}"
    new_header = header[: match.start()] + new_line + header[match.end() :]
    return new_header + sep + rest, old_line, new_line


def build_stale_scan(
    plans: list[tuple[str, str]],
) -> tuple[list[str], list[str]]:
    """(stdout lines, stderr degrade lines) for `--stale-scan` over
    (filename, text) pairs, in input order.

    A file with zero `- Status:` lines OR without a `Stage:` header is
    skipped SILENTLY — both are pre-ledger-era shapes this repo really
    ships (six Status-ledger/no-Stage plans predate the Stage field),
    and a plan without a Stage header cannot be stage-stale by
    definition; emitting stderr for them on every sweep is the
    dismissed-gate noise the advisory design exists to avoid (T1 spec
    review 🟡, 2026-08-10). A file WITH Status lines AND a Stage header
    that still fails to parse (no task headings, a status outside the
    vocabulary) contributes one loud stderr line and the scan
    continues — a single corrupt plan must never hide the rest of the
    sweep. Candidates are plans whose tasks
    are ALL done while `Stage:` is not `finishing`; none found yields
    the single `stale-scan: clean` line. Pure function — the caller
    reads the directory, prints, and always exits 0 (advisory)."""
    candidates: list[str] = []
    degrades: list[str] = []
    for filename, text in plans:
        if _STATUS_BULLET.search(text) is None:
            continue
        header, _, _ = text.partition("\n## ")
        stage = _header_value(header, "Stage")
        if not stage:
            continue  # pre-Stage-era plan — cannot be stage-stale
        try:
            tasks = _parse_tasks(text)
            if not tasks:
                raise ValueError("plan has no '## Task N — <name>' headings")
        except ValueError as exc:
            degrades.append(f"stale-scan: skipping {filename} — {exc}")
            continue
        if stage != "finishing" and all(
            kind == "done" for _, _, kind, _, _ in tasks
        ):
            candidates.append(
                f"{filename}: stage={stage} (all {len(tasks)} tasks done)"
            )
    return candidates or ["stale-scan: clean"], degrades


def _print_card_or_degrade(text: str) -> None:
    """Print a blank line then the full rendered card; when `build_card`
    raises on the (already successfully written) plan, degrade to one
    line instead — a valid flip is never reported as a failure."""
    print()
    try:
        sys.stdout.write(build_card(text))
    except ValueError as exc:
        print(f"plan_card: card unavailable — {exc}")


_USAGE = (
    "usage: python3 scripts/plan_card.py <plan-path> "
    '[--detail T<N> | --set-status "T<N>=<status>" | --set-stage "<text>"]'
    "\n       python3 scripts/plan_card.py --stale-scan <plans-dir>"
)


def _run_stale_scan(plans_dir: Path) -> int:
    """Read every `*.md` under `plans_dir` (filename order), print
    `build_stale_scan`'s degrade lines to stderr and its result lines
    to stdout. Always 0 once the directory exists — advisory by
    design, module docstring."""
    if not plans_dir.is_dir():
        print(f"plan_card: FAIL — no plans directory at {plans_dir}")
        return 1
    plans: list[tuple[str, str]] = []
    read_degrades: list[str] = []
    for path in sorted(plans_dir.glob("*.md")):
        try:
            plans.append((path.name, path.read_text(encoding="utf-8")))
        except (UnicodeDecodeError, OSError) as exc:
            # Whole-branch review 🟡 (2026-08-10): one unreadable file
            # crashed the entire sweep, hiding every other candidate —
            # the exact outcome the per-file degrade posture forbids.
            read_degrades.append(f"stale-scan: skipping {path.name} — {exc}")
    out_lines, degrades = build_stale_scan(plans)
    degrades = read_degrades + degrades
    for line in degrades:
        print(line, file=sys.stderr)
    for line in out_lines:
        print(line)
    return 0


def main() -> int:
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "--stale-scan":
        return _run_stale_scan(Path(args[1]))
    detail_number: int | None = None
    set_status_ref: tuple[int, str] | None = None
    set_stage_ref: str | None = None
    if len(args) == 3 and args[1] == "--detail":
        task_ref = re.fullmatch(r"T(\d+)", args[2])
        if task_ref is None:
            print(_USAGE, file=sys.stderr)
            return 2
        detail_number = int(task_ref.group(1))
    elif len(args) == 3 and args[1] == "--set-status":
        task_ref = re.fullmatch(r"T(\d+)=(.+)", args[2])
        if task_ref is None:
            print(_USAGE, file=sys.stderr)
            return 2
        set_status_ref = (int(task_ref.group(1)), task_ref.group(2))
    elif len(args) == 3 and args[1] == "--set-stage":
        set_stage_ref = args[2]
    elif len(args) != 1:
        print(_USAGE, file=sys.stderr)
        return 2

    plan_path = Path(args[0])
    if not plan_path.is_file():
        print(f"plan_card: FAIL — no plan file at {plan_path}")
        return 1

    try:
        if set_status_ref is not None:
            task_number, status = set_status_ref
            set_status_ref = (
                task_number,
                _expand_status_sha_ref(status, plan_path),
            )

            def _guarded_set_status(current: str) -> tuple[str, str, str]:
                refusal = _batch_member_done_refusal(current, *set_status_ref)
                if refusal is not None:
                    raise ValueError(refusal)
                return set_status(current, *set_status_ref)

            new_text, old_line, new_line = _publish_cli_mutation(
                plan_path, _guarded_set_status
            )
            print(f"old: {old_line}")
            print(f"new: {new_line}")
            _print_card_or_degrade(new_text)
            return 0
        if set_stage_ref is not None:
            new_text, old_line, new_line = _publish_cli_mutation(
                plan_path,
                lambda current: set_stage(current, set_stage_ref),
            )
            print(f"old: {old_line}")
            print(f"new: {new_line}")
            _print_card_or_degrade(new_text)
            return 0
        text = plan_path.read_text(encoding="utf-8")
        card = (
            build_card(text)
            if detail_number is None
            else build_detail(text, detail_number)
        )
    except ValueError as exc:
        print(f"plan_card: FAIL — {exc}")
        return 1

    sys.stdout.write(card)
    return 0


if __name__ == "__main__":
    sys.exit(main())
