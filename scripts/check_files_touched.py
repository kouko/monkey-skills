#!/usr/bin/env python3
"""Parse a plan's per-task `Files touched` declarations and `done(<sha>)` join keys.

PURPOSE — measurement prototype for the declared-vs-actual `Files touched`
check (docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md):
join each plan task's declared file set to the commit that resolved it, so a
later layer can compare declaration against `git show` reality.

SCOPE — two pure layers, no git calls (the git layer + CLI are Task 4):
  * PARSE: plan markdown in, per-task `(declared_paths, sha_or_None)`
    structures out (`parse_plan` / `parse_plan_text` -> `PlanParse`);
  * VERDICT: pure set arithmetic over (declared, actual, plan_path) per
    rule variant R1/R2/R3 (`verdict_r1/r2/r3`, `evaluate_task`) — variant
    semantics frozen in
    docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md.

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
                if sha is not None:
                    result.parse_errors.append(
                        f"Task {task_no}: multiple 'Status: done(<sha>)' "
                        f"lines — ambiguous join key, keeping the last")
                sha = parsed

        result.tasks[task_no] = TaskDeclaration(declared_paths=declared, sha=sha)
    return result


def parse_plan(path: Path | str) -> PlanParse:
    """Read a plan file and parse it — thin wrapper over `parse_plan_text`."""
    return parse_plan_text(Path(path).read_text(encoding="utf-8"))


# --- Verdict layer (Task 3) — pure set arithmetic, no git calls -------------
#
# Variant semantics are the frozen key's §Rule variants table
# (docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md):
#   R1 strict     — flags any set difference, both directions;
#   R2 under-only — flags only `actual − declared ≠ ∅` (the dangerous
#                   direction; OVER may be legitimate drift);
#   R3            — R2 computed after removing the standing excludes from
#                   the ACTUAL set (the plan file under check, and any path
#                   containing `__pycache__/`).
# A task whose sha is None yields NO_JOIN under every variant, never OK.

OK = "OK"
UNDER = "UNDER"
OVER = "OVER"
NO_JOIN = "NO_JOIN"

VARIANTS = ("R1", "R2", "R3")


@dataclass(frozen=True)
class Verdict:
    """One variant's verdict on one task.

    `under` / `over` carry only the paths THIS variant flags (sorted):
    R2/R3 never populate `over` — their verdict ignores that direction.
    When R1 flags both directions at once, `verdict` carries the dominant
    token UNDER (the dangerous direction — matches the frozen key's cell
    rows, which record one dominant token per cell) while both lists stay
    populated for reporting.
    """
    variant: str
    verdict: str  # OK | UNDER | OVER | NO_JOIN
    under: tuple[str, ...] = ()
    over: tuple[str, ...] = ()


def verdict_r1(declared: frozenset[str], actual: frozenset[str]) -> Verdict:
    """R1 strict: any symmetric difference flags."""
    under = tuple(sorted(actual - declared))
    over = tuple(sorted(declared - actual))
    verdict = UNDER if under else (OVER if over else OK)
    return Verdict(variant="R1", verdict=verdict, under=under, over=over)


def verdict_r2(declared: frozenset[str], actual: frozenset[str]) -> Verdict:
    """R2 under-only: flags only `actual − declared ≠ ∅`."""
    under = tuple(sorted(actual - declared))
    return Verdict(variant="R2", verdict=UNDER if under else OK, under=under)


def _normalize_plan_path(plan_path: Path | str) -> str:
    """Normalize the plan path for the R3 exclude comparison — POSIX
    separators, no leading `./` (Path() collapses it) — the same family of
    rules `_normalize_token` applies to declared tokens."""
    return Path(str(plan_path).strip()).as_posix()


def verdict_r3(declared: frozenset[str], actual: frozenset[str],
               plan_path: Path | str) -> Verdict:
    """R3: R2 after removing the standing excludes from the ACTUAL set.

    Exactly two exclude classes (frozen key §Rule variants): the plan file
    under check (normalized-path comparison), and any path containing
    `__pycache__/`. Nothing else — regenerated functional copies and
    manifest mirrors are under-declaration TARGETS, never excludes.
    """
    plan_norm = _normalize_plan_path(plan_path)
    kept = frozenset(
        p for p in actual
        if _normalize_plan_path(p) != plan_norm and "__pycache__/" not in p)
    under = tuple(sorted(kept - declared))
    return Verdict(variant="R3", verdict=UNDER if under else OK, under=under)


def evaluate_task(declaration: TaskDeclaration,
                  actual_paths: frozenset[str] | None,
                  plan_path: Path | str) -> dict[str, Verdict]:
    """Run all three variants on one task; the seam Task 4's CLI calls.

    A declaration with no join key (`sha is None`) yields NO_JOIN under
    every variant — never OK (frozen key cell 7); `actual_paths` is
    ignored in that case because nothing joins the task to a commit.
    """
    if declaration.sha is None:
        return {v: Verdict(variant=v, verdict=NO_JOIN) for v in VARIANTS}
    actual = frozenset(actual_paths or ())
    declared = declaration.declared_paths
    return {
        "R1": verdict_r1(declared, actual),
        "R2": verdict_r2(declared, actual),
        "R3": verdict_r3(declared, actual, plan_path),
    }
