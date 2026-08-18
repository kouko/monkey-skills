"""strategy-dag core loader — parses the project's frontmatter files into a Project graph.

Subcommands (check / break / claims / render / impact) land in later tasks;
this module currently implements only `load_project` plus an argparse
skeleton so `main()` has a stable place to grow into.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import yaml

FRONTMATTER_DELIM = "---"


@dataclass
class Input:
    ref: str | None = None
    load_bearing: bool | None = None


@dataclass
class Node:
    id: str | None = None
    type: str | None = None
    seq: int | None = None
    inputs: list[Input] = field(default_factory=list)
    summary: str | None = None
    status: str | None = None
    branch: str | None = None
    branch_type: str | None = None
    source: str | None = None
    quote: str | None = None
    path: Path | None = None
    body: str = ""


@dataclass
class Assumption:
    id: str | None = None
    status: str | None = None
    statement: str | None = None
    breaks_if: str | None = None
    source: str | None = None
    branch: str | None = None
    path: Path | None = None
    body: str = ""


@dataclass
class Project:
    root: Path
    nodes: list[Node] = field(default_factory=list)
    assumptions: list[Assumption] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)


def split_frontmatter(text: str) -> tuple[str, str]:
    """Split raw file text into (frontmatter_text, body_text).

    Returns the frontmatter block's raw text (without the `---` delimiters)
    and the body separately, so a later rewrite (Task 5) can preserve key
    order and body bytes exactly.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return "", text
    for idx in range(1, len(lines)):
        if lines[idx].strip() == FRONTMATTER_DELIM:
            fm_text = "\n".join(lines[1:idx]) + "\n"
            body = "\n".join(lines[idx + 1:])
            if body.startswith("\n"):
                body = body[1:]
            return fm_text, body
    return "", text


def _parse_inputs(raw_inputs) -> list[Input]:
    inputs: list[Input] = []
    for entry in raw_inputs or []:
        if isinstance(entry, dict):
            inputs.append(Input(ref=entry.get("ref"), load_bearing=entry.get("load_bearing")))
        else:
            # bare string form — load_bearing left None for a later check to flag
            inputs.append(Input(ref=entry, load_bearing=None))
    return inputs


def _parse_frontmatter_mapping(path: Path, root: Path) -> tuple[dict | None, str, str | None]:
    """Parse a file's frontmatter into a mapping.

    Returns (fm, body, problem). `fm` is None when the frontmatter fails to
    parse to a mapping (non-dict YAML, or invalid YAML); `problem` is then a
    single-line "<relpath>: frontmatter: ..." message for Project.problems,
    and the caller must skip the file rather than fabricate a Node/Assumption.
    """
    fm_text, body = split_frontmatter(path.read_text(encoding="utf-8"))
    relpath = path.relative_to(root).as_posix()
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        reason = str(exc).splitlines()[0]
        return None, body, f"{relpath}: frontmatter: invalid YAML ({reason})"
    fm = fm or {}
    if not isinstance(fm, dict):
        return None, body, f"{relpath}: frontmatter: not a mapping"
    return fm, body, None


def _load_node(path: Path, root: Path) -> tuple[Node | None, str | None]:
    fm, body, problem = _parse_frontmatter_mapping(path, root)
    if fm is None:
        return None, problem
    return Node(
        id=fm.get("id"),
        type=fm.get("type"),
        seq=fm.get("seq"),
        inputs=_parse_inputs(fm.get("inputs")),
        summary=fm.get("summary"),
        status=fm.get("status"),
        branch=fm.get("branch"),
        branch_type=fm.get("branch_type"),
        source=fm.get("source"),
        quote=fm.get("quote"),
        path=path,
        body=body,
    ), None


def _load_assumption(path: Path, root: Path) -> tuple[Assumption | None, str | None]:
    fm, body, problem = _parse_frontmatter_mapping(path, root)
    if fm is None:
        return None, problem
    return Assumption(
        id=fm.get("id"),
        status=fm.get("status"),
        statement=fm.get("statement"),
        breaks_if=fm.get("breaks_if"),
        source=fm.get("source"),
        branch=fm.get("branch"),
        path=path,
        body=body,
    ), None


def _load_research_note_as_node(path: Path, root: Path) -> tuple[Node | None, str | None]:
    fm, body, problem = _parse_frontmatter_mapping(path, root)
    if fm is None:
        return None, problem
    return Node(
        id=fm.get("id"),
        type="FACT",
        seq=fm.get("seq"),
        inputs=_parse_inputs(fm.get("inputs")),
        summary=fm.get("claim"),
        status=fm.get("status"),
        branch=fm.get("branch"),
        branch_type=fm.get("branch_type"),
        source=fm.get("source"),
        quote=fm.get("quote"),
        path=path,
        body=body,
    ), None


def load_project(root: Path) -> Project:
    """Load every node/assumption/research-note *.md under root into a Project."""
    root = Path(root)
    nodes: list[Node] = []
    assumptions: list[Assumption] = []
    problems: list[str] = []

    nodes_dir = root / "nodes"
    if nodes_dir.is_dir():
        for path in sorted(nodes_dir.glob("*.md")):
            node, problem = _load_node(path, root)
            if problem:
                problems.append(problem)
            else:
                nodes.append(node)

    assumptions_dir = root / "assumptions"
    if assumptions_dir.is_dir():
        for path in sorted(assumptions_dir.glob("*.md")):
            assumption, problem = _load_assumption(path, root)
            if problem:
                problems.append(problem)
            else:
                assumptions.append(assumption)

    research_dir = root / "research"
    if research_dir.is_dir():
        for path in sorted(research_dir.glob("*.md")):
            node, problem = _load_research_note_as_node(path, root)
            if problem:
                problems.append(problem)
            else:
                nodes.append(node)

    nodes.sort(key=lambda n: (n.seq is None, n.seq, n.id or ""))

    return Project(root=root, nodes=nodes, assumptions=assumptions, problems=problems)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dag", description="strategy-dag project loader/CLI")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("load", help="load and validate the project graph (diagnostics only)")
    args = parser.parse_args(argv)

    if args.command == "load":
        project = load_project(Path.cwd())
        print(f"loaded {len(project.nodes)} node(s), {len(project.assumptions)} assumption(s)")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
