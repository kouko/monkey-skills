#!/usr/bin/env python3
"""Propose review batches for one plan under the module rule.

Usage::

    python3 loom-code/scripts/propose_review_batches.py <plan-path>
    python3 loom-code/scripts/propose_review_batches.py --check <plan-path>

``propose`` (no flag) prints one JSON object on stdout::

    {"batches": [{"members": [1, 2], "lane": "full",
                  "reason": "module:<value>" | "dependency"}, ...],
     "singletons": [3, ...]}

``--check`` exits non-zero, one stdout line per violation, when the plan's
declared ``## Review Batches`` deviate from the proposal without a reason:
(a) two tasks proposed together are not in the same declared batch and the
later task lacks a non-empty ``- **Not batched because**: <reason>`` line;
(b) a declared batch has more than ``BATCH_CAP`` members and lacks a
non-empty ``- **Oversized because**: <reason>`` line in its block.

Two non-mechanical tasks are joined when they share a review lane AND
(one lists the other in ``Dependencies`` OR both carry an identical
normalized ``Module`` value). Each connected component is split into
batches of at most ``BATCH_CAP`` tasks in dependency (topological) order,
so a task never precedes one of its dependencies in a later batch.
One-task components, and a one-task tail chunk of a split component, are
reported as ``singletons``.

The plan grammar is owned by the sibling ``check_review_batches.py``
oracle, imported by file path; this script never re-implements it.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


# Planning-time constants, not runtime settings. Both were sized from the
# batch-knob simulation record (docs/loom/dogfood/2026-08-31-batch-knob-
# simulation.py, Variant C; per-plan results in the sibling
# ...-simulation-per-plan.csv column `fanouts_c_module_cap4`).
EDGE_RULE = "same lane AND (dependency edge OR identical Module)"
"""Variant C of the simulation: the file-overlap gate is replaced by
``Module`` equality. Changing the rule invalidates the record's numbers."""

BATCH_CAP = 4
"""Maximum members per proposed batch (Variant C ran at cap 4)."""

NOT_BATCHED_FIELD = "Not batched because"
"""Task field excusing a proposed pair the planner kept apart."""

OVERSIZED_FIELD = "Oversized because"
"""Review Batch field excusing a declared batch above ``BATCH_CAP``."""

# Oracle errors a plan written before the Review Batches contract always
# carries. They say nothing about the Task DAG, so the proposer still
# clusters such a plan; every other oracle error is structural and refuses.
_PRE_BATCH_ERA_ERRORS = (
    "plan must declare a Review Batches second-pass section",
    "must declare exactly one review disposition",
)


def _oracle():
    """Load the sibling schema oracle without relying on cwd/sys.path."""
    path = Path(__file__).with_name("check_review_batches.py")
    spec = importlib.util.spec_from_file_location("propose_review_batch_oracle", path)
    if spec is None or spec.loader is None:
        raise ValueError("Review Batch schema oracle cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _normalize_module(value: str) -> str:
    """Mirror the simulation's `_norm_path`: strip space, backticks, `.,;`."""
    return value.strip().strip("`").strip().rstrip(".,;")


def _task_blocks(oracle, text: str) -> dict[int, str]:
    """Each Task's block, cut before the Review Batches section."""
    review_section = oracle._BATCH_SECTION.search(text)
    blocks: dict[int, str] = {}
    for match, block in oracle._blocks(oracle._TASK_HEADING, text):
        if review_section is not None and review_section.start() > match.start():
            block = block[: max(0, review_section.start() - match.end())]
        blocks[int(match.group(1))] = block
    return blocks


def _module_values(oracle, text: str) -> dict[int, str]:
    """First `Module` value per Task, read with the oracle's field grammar."""
    modules: dict[int, str] = {}
    for number, block in _task_blocks(oracle, text).items():
        values = oracle._field_values(block, "Module")
        modules[number] = _normalize_module(values[0]) if values else ""
    return modules


def _has_reason(oracle, block: str, field: str) -> bool:
    return any(value for value in oracle._field_values(block, field))


def _components(tasks: dict, modules: dict[int, str]) -> list[list[int]]:
    """Connected components under EDGE_RULE over non-mechanical tasks."""
    numbers = sorted(n for n, task in tasks.items() if task.review_lane != "mechanical")
    parent = {n: n for n in numbers}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for n in numbers:
        for dep in tasks[n].dependencies:
            if dep in parent and tasks[dep].review_lane == tasks[n].review_lane:
                union(dep, n)
    buckets: dict[tuple[str, str], list[int]] = {}
    for n in numbers:
        if modules[n]:
            buckets.setdefault((tasks[n].review_lane, modules[n]), []).append(n)
    for bucket in buckets.values():
        for n in bucket[1:]:
            union(bucket[0], n)
    groups: dict[int, list[int]] = {}
    for n in numbers:
        groups.setdefault(find(n), []).append(n)
    return sorted(groups.values(), key=lambda group: group[0])


def _topological(members: list[int], tasks: dict) -> list[int]:
    """Kahn's algorithm over in-component edges, ties broken by task number."""
    member_set = set(members)
    indegree = {n: 0 for n in members}
    successors: dict[int, list[int]] = {n: [] for n in members}
    for n in members:
        for dep in tasks[n].dependencies:
            if dep in member_set and dep != n:
                successors[dep].append(n)
                indegree[n] += 1
    ready = sorted(n for n in members if indegree[n] == 0)
    order: list[int] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for nxt in successors[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
        ready.sort()
    return order if len(order) == len(members) else list(members)


def _reason(members: list[int], modules: dict[int, str]) -> str:
    values = {modules[n] for n in members}
    if len(values) == 1 and modules[members[0]]:
        return f"module:{modules[members[0]]}"
    return "dependency"


def propose(text: str) -> tuple[dict[str, object], list[str]]:
    """The proposal for `text`, or the oracle's structural errors."""
    oracle = _oracle()
    errors: list[str] = []
    tasks = oracle._parse_tasks(text, errors)
    structural = [
        error for error in errors
        if not any(marker in error for marker in _PRE_BATCH_ERA_ERRORS)
    ]
    if structural:
        return {}, structural
    modules = _module_values(oracle, text)
    batches: list[dict[str, object]] = []
    singletons: list[int] = []
    for component in _components(tasks, modules):
        if len(component) == 1:
            singletons.append(component[0])
            continue
        order = _topological(component, tasks)
        for start in range(0, len(order), BATCH_CAP):
            members = order[start:start + BATCH_CAP]
            if len(members) == 1:
                # A one-task tail chunk buys nothing for the batch ceremony.
                singletons.append(members[0])
                continue
            batches.append({
                "members": members,
                "lane": tasks[members[0]].review_lane,
                "reason": _reason(members, modules),
            })
    return {"batches": batches, "singletons": sorted(singletons)}, []


def _declared_batches(oracle, text: str) -> tuple[dict[str, object], dict[str, str], list[str]]:
    """Declared batches and their blocks via the oracle; a missing section is
    an empty declaration (the check then asks every proposed pair to explain)."""
    if oracle._BATCH_SECTION.search(text) is None:
        return {}, {}, []
    errors: list[str] = []
    body = oracle._review_batch_body(text, errors)
    batches = oracle._parse_batches(body, errors)
    blocks = {
        match.group(1).strip(): block
        for match, block in oracle._blocks(oracle._BATCH_HEADING, body)
    }
    return batches, blocks, errors


def check(text: str) -> tuple[list[str], list[str]]:
    """Violations of the two reason-line duties, or the oracle's errors."""
    proposal, errors = propose(text)
    if errors:
        return [], errors
    oracle = _oracle()
    batches, blocks, errors = _declared_batches(oracle, text)
    if errors:
        return [], errors
    task_blocks = _task_blocks(oracle, text)
    membership = {
        member: batch_id
        for batch_id, batch in batches.items()
        for member in batch.members
    }
    violations: list[str] = []
    for batch in proposal["batches"]:
        members = sorted(batch["members"])
        for index, later in enumerate(members):
            if _has_reason(oracle, task_blocks.get(later, ""), NOT_BATCHED_FIELD):
                continue
            unbatched = [
                earlier for earlier in members[:index]
                if membership.get(earlier) is None
                or membership.get(earlier) != membership.get(later)
            ]
            if not unbatched:
                continue
            named = ", ".join(f"Task {earlier}" for earlier in unbatched)
            violations.append(
                f"Task {later}: proposed with {named} but not declared in the "
                f"same Review Batch; lacks a non-empty "
                f"'- **{NOT_BATCHED_FIELD}**: <reason>' line"
            )
    for batch_id, batch in batches.items():
        if len(batch.members) <= BATCH_CAP:
            continue
        if _has_reason(oracle, blocks.get(batch_id, ""), OVERSIZED_FIELD):
            continue
        violations.append(
            f"Review Batch {batch_id}: {len(batch.members)} members exceed the "
            f"cap of {BATCH_CAP}; lacks a non-empty "
            f"'- **{OVERSIZED_FIELD}**: <reason>' line"
        )
    return violations, []


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    checking = args[:1] == ["--check"]
    if checking:
        args = args[1:]
    if len(args) != 1:
        print("Usage: propose_review_batches.py [--check] <plan-path>", file=sys.stderr)
        return 2
    plan_path = Path(args[0])
    try:
        text = plan_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"Error: cannot read plan {plan_path}: {exc}", file=sys.stderr)
        return 1
    if checking:
        violations, errors = check(text)
    else:
        proposal, errors = propose(text)
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return 1
    if not checking:
        print(json.dumps(proposal, indent=2))
        return 0
    for violation in violations:
        print(violation)
    if violations:
        return 1
    print(f"Review Batches in {plan_path} conform to the proposal or explain each deviation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
