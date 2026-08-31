#!/usr/bin/env python3
"""Propose review batches for one plan under the module rule.

Usage: ``python3 loom-code/scripts/propose_review_batches.py <plan-path>``

Prints one JSON object on stdout::

    {"batches": [{"members": [1, 2], "lane": "full",
                  "reason": "module:<value>" | "dependency"}, ...],
     "singletons": [3, ...]}

Two non-mechanical tasks are joined when they share a review lane AND
(one lists the other in ``Dependencies`` OR both carry an identical
normalized ``Module`` value). Each connected component is split into
batches of at most ``BATCH_CAP`` tasks in dependency (topological) order,
so a task never precedes one of its dependencies in a later batch.
One-task components are reported as ``singletons``.

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


def _module_values(oracle, text: str) -> dict[int, str]:
    """First `Module` value per Task, read with the oracle's field grammar."""
    review_section = oracle._BATCH_SECTION.search(text)
    modules: dict[int, str] = {}
    for match, block in oracle._blocks(oracle._TASK_HEADING, text):
        if review_section is not None and review_section.start() > match.start():
            block = block[: max(0, review_section.start() - match.end())]
        values = oracle._field_values(block, "Module")
        modules[int(match.group(1))] = _normalize_module(values[0]) if values else ""
    return modules


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
            batches.append({
                "members": members,
                "lane": tasks[members[0]].review_lane,
                "reason": _reason(members, modules),
            })
    return {"batches": batches, "singletons": singletons}, []


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: propose_review_batches.py <plan-path>", file=sys.stderr)
        return 2
    plan_path = Path(args[0])
    try:
        text = plan_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"Error: cannot read plan {plan_path}: {exc}", file=sys.stderr)
        return 1
    proposal, errors = propose(text)
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(proposal, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
