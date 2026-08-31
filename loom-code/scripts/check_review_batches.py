#!/usr/bin/env python3
"""Validate the closed Review Batch metadata contract in one plan.

Usage: ``python3 loom-code/scripts/check_review_batches.py <plan-path>``

Every ``## Task N`` block must declare exactly one review disposition:
``individual`` or ``batch(<id>)``. Review Batches are declared after the
Task DAG under ``## Review Batches`` with this six-field shape (the heading
owns the ID):

    ### Review Batch: <id>
    - **Members**: Task 1, Task 2
    - **Verdict question**: Does the capability satisfy its contract?
    - **Review lane**: full
    - **Aggregate verification**: `<reproducible command>`
    - **Boundary**: capability: <name>; exclusions: none; consumable: yes

The boundary suffix is deliberately closed. Anything other than ``none`` and
``yes`` is rejected; writing-plans must emit an individual disposition instead
of asking this structural oracle to infer eligibility from prose. The script
stores no Batch state.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import sys


_TASK_HEADING = re.compile(r"^## Task (\d+)\b.*$", re.MULTILINE)
_BATCH_SECTION = re.compile(r"^## Review Batches\s*$", re.MULTILINE)
_BATCH_HEADING = re.compile(r"^### Review Batch:\s*(.*?)\s*$", re.MULTILINE)
_H2_HEADING = re.compile(r"^##\s+", re.MULTILINE)
_FIELD = re.compile(
    r"^\s*-\s*(?:\*\*)?(?P<name>[A-Za-z][A-Za-z -]*?)(?:\*\*)?\s*:\s*(?P<value>.*)$",
    re.MULTILINE,
)
_DEPENDENCY_FORMS = (
    re.compile(r"^Task (\d+) completes first$"),
    re.compile(r"^Tasks (\d+(?:,\s*\d+)*) complete first$"),
    re.compile(r"^Tasks (\d+(?:,\s*\d+)*) parallel$"),
)
_DISPOSITION = re.compile(r"^(?:individual|batch\(([a-z0-9][a-z0-9-]*)\))$")
_BATCH_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_MEMBERS = re.compile(r"^Task (\d+)(?:,\s*Task (\d+))*$")
_BOUNDARY = re.compile(
    r"^(?:capability|invariant):\s*(?P<name>[^;]+);\s*"
    r"exclusions:\s*none;\s*consumable:\s*yes$"
)
_PLACEHOLDER = re.compile(r"^(?:tbd|todo|unknown|n/?a|none)\b", re.IGNORECASE)
_ABSOLUTE_PATH_TOKEN = re.compile(
    r"(?:^|[\s`'\"=])(?:/(?!/)|[A-Za-z]:[\\/])"
)
_REQUIRED_BATCH_FIELDS = (
    "Members",
    "Verdict question",
    "Review lane",
    "Aggregate verification",
    "Boundary",
)
_PROJECTION_FIELD = re.compile(
    r"^-\s*(?:\*\*)?(?P<name>[A-Za-z][A-Za-z -]*?)(?:\*\*)?"
    r"\s*:[ \t]*(?P<value>[^\n]*)$"
)
# The `none — <reason>` release-administration referent (plan-format.md
# §Brief item covered) is a legal citation but must NOT count as an owned
# requirement — see `_NONE_VALUE` in check_scenario_coverage.py, whose
# grammar this mirrors. Kept local rather than imported: check_review_batches
# is loaded via importlib.util.spec_from_file_location from more than one
# caller (review_batch.py's oracle, direct CLI, test harnesses) and a plain
# cross-script import would depend on sys.path state none of those callers
# guarantee.
_NONE_REFERENT = re.compile(
    r"^[\"'`]?\s*none(?:\s*[–—]|\s+-(?=\s|$))?.*?[\"'`]?\s*$", re.IGNORECASE
)


@dataclass(frozen=True)
class Task:
    number: int
    dependencies: tuple[int, ...]
    disposition: str
    review_lane: str


@dataclass(frozen=True)
class Batch:
    batch_id: str
    members: tuple[int, ...]
    review_lane: str


def _blocks(pattern: re.Pattern[str], text: str) -> list[tuple[re.Match[str], str]]:
    matches = list(pattern.finditer(text))
    blocks: list[tuple[re.Match[str], str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match, text[match.end():end]))
    return blocks


def _field_values(block: str, name: str) -> list[str]:
    return [
        match.group("value").strip()
        for match in _FIELD.finditer(block)
        if match.group("name").strip() == name
    ]


def _one_field(block: str, name: str, owner: str, errors: list[str]) -> str:
    values = _field_values(block, name)
    if len(values) != 1 or not values[0]:
        errors.append(f"{owner} must declare exactly one non-empty {name} field")
        return ""
    if any(ord(char) < 32 for char in values[0]):
        errors.append(f"{owner} {name} contains a control character")
        return ""
    return values[0]


def _validate_untrusted_value(
    value: str,
    name: str,
    owner: str,
    errors: list[str],
) -> None:
    if (
        "../" in value
        or "..\\" in value
        or "~/" in value
        or "file://" in value.lower()
        or _ABSOLUTE_PATH_TOKEN.search(value)
    ):
        errors.append(f"{owner} {name} contains unsafe path syntax")
    if name != "Aggregate verification" and any(
        token in value for token in ("$(", "${", "&&", "||")
    ):
        errors.append(f"{owner} {name} contains shell-control syntax")


def _parse_dependencies(value: str, task_number: int, errors: list[str]) -> tuple[int, ...]:
    if value == "none":
        return ()
    for form in _DEPENDENCY_FORMS:
        match = form.fullmatch(value)
        if match:
            return tuple(int(part.strip()) for part in match.group(1).split(","))
    errors.append(
        f"Task {task_number} Dependencies is missing or outside the closed DAG grammar"
    )
    return ()


def _parse_tasks(text: str, errors: list[str]) -> dict[int, Task]:
    task_matches = list(_TASK_HEADING.finditer(text))
    if not task_matches:
        errors.append("plan has no Task headings, so its DAG is incomplete")
        return {}
    review_section = _BATCH_SECTION.search(text)
    if review_section is None:
        errors.append("plan must declare a Review Batches second-pass section")
    elif review_section.start() < task_matches[-1].start():
        errors.append("Review Batches must be declared after the completed Task DAG")

    tasks: dict[int, Task] = {}
    for index, match in enumerate(task_matches):
        number = int(match.group(1))
        if number in tasks:
            errors.append(f"duplicate Task {number} heading")
        end = task_matches[index + 1].start() if index + 1 < len(task_matches) else len(text)
        if review_section is not None and review_section.start() > match.start():
            end = min(end, review_section.start())
        block = text[match.end():end]
        owner = f"Task {number}"
        dependency_value = _one_field(block, "Dependencies", owner, errors)
        dependencies = _parse_dependencies(dependency_value, number, errors)
        dispositions = _field_values(block, "Review disposition")
        if len(dispositions) != 1 or _DISPOSITION.fullmatch(dispositions[0]) is None:
            errors.append(
                f"{owner} must declare exactly one review disposition: individual or batch(<id>)"
            )
            disposition = ""
        else:
            disposition = dispositions[0]
        weights = _field_values(block, "Review-weight")
        if len(weights) > 1:
            errors.append(f"{owner} has duplicate Review-weight fields")
        lane = weights[0] if weights else "full"
        if lane not in {"full", "prose", "mechanical"}:
            errors.append(f"{owner} Review-weight is outside full/prose/mechanical")
        tasks[number] = Task(number, dependencies, disposition, lane)
    return tasks


def _member_numbers(value: str, owner: str, errors: list[str]) -> tuple[int, ...]:
    if _MEMBERS.fullmatch(value) is None:
        errors.append(f"{owner} Members must be a non-empty comma-separated Task list")
        return ()
    members = tuple(int(token) for token in re.findall(r"Task (\d+)", value))
    duplicates = sorted({number for number in members if members.count(number) > 1})
    for number in duplicates:
        errors.append(f"{owner} has duplicate member Task {number}")
    return members


def _review_batch_body(text: str, errors: list[str]) -> str:
    sections = list(_BATCH_SECTION.finditer(text))
    if len(sections) != 1:
        errors.append("plan must declare exactly one Review Batches section")
    if not sections:
        return ""
    section = sections[0]
    next_h2 = _H2_HEADING.search(text, section.end())
    end = next_h2.start() if next_h2 is not None else len(text)
    for heading in _BATCH_HEADING.finditer(text):
        if not section.end() <= heading.start() < end:
            errors.append(
                f"Review Batch {heading.group(1).strip() or '(empty ID)'} "
                "is outside the Review Batches section"
            )
    return text[section.end():end]


def _parse_batches(batch_body: str, errors: list[str]) -> dict[str, Batch]:
    batches: dict[str, Batch] = {}
    for match, block in _blocks(_BATCH_HEADING, batch_body):
        batch_id = match.group(1).strip()
        owner = f"Review Batch {batch_id or '(empty ID)'}"
        if _BATCH_ID.fullmatch(batch_id) is None:
            errors.append(f"{owner} ID is outside lowercase letters, digits, and hyphens")
        if batch_id in batches:
            errors.append(f"duplicate Review Batch ID {batch_id}")

        values = {
            name: _one_field(block, name, owner, errors)
            for name in _REQUIRED_BATCH_FIELDS
        }
        field_spans = [field.span() for field in _FIELD.finditer(block)]
        residue = list(block)
        for start, end in field_spans:
            residue[start:end] = " " * (end - start)
        if "".join(residue).strip():
            errors.append(
                f"{owner} contains a newline continuation or undeclared content"
            )
        for name, value in values.items():
            _validate_untrusted_value(
                value,
                name,
                owner,
                errors,
            )
        members = _member_numbers(values["Members"], owner, errors)
        verdict = values["Verdict question"]
        if verdict and (not verdict.endswith("?") or _PLACEHOLDER.match(verdict)):
            errors.append(f"{owner} Verdict question must be one explicit question")
        verification = values["Aggregate verification"]
        if verification and _PLACEHOLDER.match(verification):
            errors.append(f"{owner} Aggregate verification must be reproducible, not a placeholder")
        lane = values["Review lane"]
        if lane not in {"full", "prose"}:
            errors.append(f"{owner} Review lane must be full or prose")
        boundary = values["Boundary"]
        boundary_match = _BOUNDARY.fullmatch(boundary)
        if boundary_match is None:
            if "exclusions: none" not in boundary:
                errors.append(f"{owner} boundary exclusions must be none")
            if "consumable: yes" not in boundary:
                errors.append(f"{owner} boundary consumable proof must be yes")
            if "exclusions: none" in boundary and "consumable: yes" in boundary:
                errors.append(f"{owner} Boundary is outside the closed grammar")
        elif _PLACEHOLDER.match(boundary_match.group("name").strip()):
            errors.append(f"{owner} Boundary must name a capability or invariant")
        batches[batch_id] = Batch(batch_id, members, lane)
    return batches


def _validate_dag(tasks: dict[int, Task], errors: list[str]) -> None:
    for task in tasks.values():
        for dependency in task.dependencies:
            if dependency not in tasks:
                errors.append(f"Task {task.number} depends on unknown Task {dependency}")
    visiting: set[int] = set()
    visited: set[int] = set()

    def visit(number: int, trail: tuple[int, ...]) -> None:
        if number in visiting:
            start = trail.index(number)
            cycle = trail[start:] + (number,)
            errors.append("Task dependency cycle: " + " -> ".join(map(str, cycle)))
            return
        if number in visited or number not in tasks:
            return
        visiting.add(number)
        for dependency in tasks[number].dependencies:
            visit(dependency, trail + (number,))
        visiting.discard(number)
        visited.add(number)

    for number in tasks:
        visit(number, ())


def _validate_membership(
    tasks: dict[int, Task], batches: dict[str, Batch], errors: list[str]
) -> None:
    listed_in: dict[int, list[str]] = {}
    for batch in batches.values():
        for member in batch.members:
            listed_in.setdefault(member, []).append(batch.batch_id)
            task = tasks.get(member)
            if task is None:
                errors.append(f"Review Batch {batch.batch_id} names unknown Task {member}")
                continue
            if task.disposition != f"batch({batch.batch_id})":
                errors.append(
                    f"Task {member} membership contradicts Review Batch {batch.batch_id}"
                )
            if task.review_lane != batch.review_lane:
                errors.append(
                    f"Review Batch {batch.batch_id} Review lane {batch.review_lane} "
                    f"does not match Task {member} lane {task.review_lane}"
                )
        if len(set(batch.members)) != len(batch.members):
            continue

    for number, task in tasks.items():
        memberships = listed_in.get(number, [])
        if len(memberships) > 1:
            errors.append(f"Task {number} belongs to multiple Review Batches")
        match = _DISPOSITION.fullmatch(task.disposition)
        batch_id = match.group(1) if match is not None else None
        if batch_id is not None and batch_id not in batches:
            errors.append(f"Task {number} names unknown Review Batch {batch_id}")
        if batch_id is not None and memberships != [batch_id]:
            errors.append(f"Task {number} batch disposition has no exact membership")
        if task.disposition == "individual" and memberships:
            errors.append(f"individual Task {number} cannot be a Batch member")


def _projection_field_block(
    block: str, name: str, owner: str, errors: list[str]
) -> tuple[str, ...]:
    """Return one field's exact logical lines without crossing Markdown rows."""
    lines = block.splitlines()
    matches = [
        index for index, line in enumerate(lines)
        if (match := _PROJECTION_FIELD.fullmatch(line))
        and match.group("name").strip() == name
    ]
    if len(matches) != 1:
        errors.append(f"{owner} must declare exactly one non-empty {name} field")
        return ()
    index = matches[0]
    match = _PROJECTION_FIELD.fullmatch(lines[index])
    assert match is not None
    values = [match.group("value").strip()]
    for line in lines[index + 1:]:
        if _PROJECTION_FIELD.fullmatch(line) is not None:
            break
        if line.strip():
            # Preserve indentation, list markers, table separators, and all
            # text; only trailing presentation whitespace is non-semantic.
            values.append(line.rstrip())
    if not any(values):
        errors.append(f"{owner} must declare exactly one non-empty {name} field")
        return ()
    return tuple(value for value in values if value)


def _safe_projection_path(path: str) -> bool:
    if not path or "\\" in path or "\x00" in path:
        return False
    if any(part in {"", ".", ".."} for part in path.split("/")):
        return False
    parsed = PurePosixPath(path)
    return not parsed.is_absolute() and parsed.as_posix() == path


def _projection_files(value: str, owner: str, errors: list[str]) -> tuple[str, ...]:
    parts = tuple(part.strip() for part in value.split(","))
    code_spans = all(
        len(part) >= 3 and part.startswith("`") and part.endswith("`")
        and "`" not in part[1:-1]
        for part in parts
    )
    plain = all("`" not in part for part in parts)
    if not parts or not all(parts) or (not code_spans and not plain):
        errors.append(f"{owner} Files touched must be one uniform safe path list")
        return ()
    paths = tuple(part[1:-1] if code_spans else part for part in parts)
    if len(set(paths)) != len(paths) or not all(_safe_projection_path(path) for path in paths):
        errors.append(f"{owner} Files touched contains an unsafe or duplicate path")
        return ()
    return paths


def _projection_references(
    block: str, owner: str, errors: list[str]
) -> tuple[str, ...]:
    references: list[str] = []
    lines = block.splitlines()
    for line in lines:
        match = _PROJECTION_FIELD.fullmatch(line)
        if match is None or match.group("name").strip() != "Brief item covered":
            continue
        values = tuple(part.strip() for part in match.group("value").split(","))
        if not values or not all(values):
            errors.append(f"{owner} has an empty Brief item covered reference")
            return ()
        references.extend(values)
    if not references:
        errors.append(f"{owner} lacks execution-authority plan fields")
        return ()
    if len(set(references)) != len(references):
        errors.append(f"{owner} has duplicate Brief item covered references")
        return ()
    return tuple(references)


def execution_projection_fields(text: str, batch_id: str) -> dict[str, object]:
    """Return the canonical current-plan authority payload for one Batch.

    This is deliberately downstream of the mandatory schema validation: callers
    receive no partial projection for an invalid plan.  The payload contains
    only plan-owned fields; the trusted review boundary later binds it to the
    independently issued plan/spec/ownership receipts.
    """
    if type(text) is not str or type(batch_id) is not str:
        raise ValueError("Review Batch projection input has an invalid type")
    errors = validate_plan(text)
    if errors:
        raise ValueError("Review Batch schema invalid — " + "; ".join(errors))
    body_errors: list[str] = []
    body = _review_batch_body(text, body_errors)
    batches = _parse_batches(body, body_errors)
    batch = batches.get(batch_id)
    if batch is None:
        raise ValueError(f"Review Batch schema has no Batch '{batch_id}'")
    declaration_block = next(
        (
            block for heading, block in _blocks(_BATCH_HEADING, body)
            if heading.group(1).strip() == batch_id
        ),
        None,
    )
    if declaration_block is None:
        raise ValueError(f"Review Batch schema has no Batch '{batch_id}'")
    declaration = {
        "batch_id": batch_id,
        "members": tuple(f"Task {number}" for number in batch.members),
        "verdict_question": _one_field(
            declaration_block, "Verdict question", f"Batch '{batch_id}'", body_errors
        ),
        "review_lane": _one_field(
            declaration_block, "Review lane", f"Batch '{batch_id}'", body_errors
        ),
        "aggregate_verification": _one_field(
            declaration_block,
            "Aggregate verification",
            f"Batch '{batch_id}'",
            body_errors,
        ),
        "boundary": _one_field(
            declaration_block, "Boundary", f"Batch '{batch_id}'", body_errors
        ),
    }
    parsed_tasks = _parse_tasks(text, body_errors)
    task_blocks: dict[int, str] = {}
    for match, block in _blocks(_TASK_HEADING, text):
        task_blocks[int(match.group(1))] = block
    members: list[dict[str, object]] = []
    for number in batch.members:
        task = parsed_tasks[number]
        block = task_blocks[number]
        acceptance = _projection_field_block(
            block, "Acceptance", f"Task {number}", body_errors
        )
        files = _projection_field_block(
            block, "Files touched", f"Task {number}", body_errors
        )
        file_paths = _projection_files(
            files[0] if len(files) == 1 else "", f"Task {number}", body_errors
        )
        briefs = _projection_references(block, f"Task {number}", body_errors)
        # The existing executable plan schema has one authority source:
        # Brief item covered.  R11a widens owned_requirements to every
        # referent kind plan-format.md admits (quote, BI-<n>, REQ-<n>) —
        # non-empty is the only rule — except the `none — <reason>`
        # release-administration value, which cites no brief outcome and so
        # contributes zero owned requirements.  There is no separate
        # future-requirement field to infer or invent, so the canonical
        # future mapping stays the empty tuple until that schema grows a
        # validated source for it.
        owned = tuple(
            reference for reference in briefs
            if _NONE_REFERENT.fullmatch(reference) is None
        )
        members.append({
            "task_id": f"Task {number}",
            "dependencies": tuple(f"Task {dep}" for dep in task.dependencies),
            "review_disposition": task.disposition,
            "review_lane": task.review_lane,
            "acceptance": acceptance,
            "declared_files": file_paths,
            "brief_references": briefs,
            "owned_requirements": owned,
            "future_requirements": (),
        })
    if body_errors:
        raise ValueError("Review Batch schema invalid — " + "; ".join(body_errors))
    return {"declaration": declaration, "members": tuple(members)}


def validate_plan(text: str) -> list[str]:
    errors: list[str] = []
    tasks = _parse_tasks(text, errors)
    batch_body = _review_batch_body(text, errors)
    batches = _parse_batches(batch_body, errors)
    _validate_dag(tasks, errors)
    _validate_membership(tasks, batches, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: check_review_batches.py <plan-path>", file=sys.stderr)
        return 2
    plan_path = Path(args[0])
    try:
        text = plan_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"Error: cannot read plan {plan_path}: {exc}", file=sys.stderr)
        return 1
    errors = validate_plan(text)
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return 1
    task_count = len(_TASK_HEADING.findall(text))
    batch_count = len(_BATCH_HEADING.findall(text))
    print(f"Review Batch schema valid: {task_count} Tasks, {batch_count} Batches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
