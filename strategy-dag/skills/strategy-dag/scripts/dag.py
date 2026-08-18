"""strategy-dag core loader — parses the project's frontmatter files into a Project graph.

Subcommands (check / break / claims / render / impact) land in later tasks;
this module currently implements only `load_project` plus an argparse
skeleton so `main()` has a stable place to grow into.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
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
    origin: str | None = None


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
        origin="research",
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


def _relpath(path: Path | None, root: Path) -> str:
    if path is None:
        return "<unknown>"
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _rule_load_bearing(project: Project) -> list[str]:
    violations = []
    for node in project.nodes:
        relpath = _relpath(node.path, project.root)
        for entry in node.inputs:
            if entry.load_bearing is None:
                violations.append(
                    f"{relpath}: load_bearing: input ref={entry.ref!r} missing load_bearing"
                )
    return violations


def _rule_ref(project: Project) -> list[str]:
    known_ids = {n.id for n in project.nodes if n.id} | {
        a.id for a in project.assumptions if a.id
    }
    violations = []
    for node in project.nodes:
        relpath = _relpath(node.path, project.root)
        for entry in node.inputs:
            if entry.ref is not None and entry.ref not in known_ids:
                violations.append(f"{relpath}: ref: input ref={entry.ref!r} resolves to no node/assumption/research id")
    return violations


def _rule_fact_source(project: Project) -> list[str]:
    violations = []
    for node in project.nodes:
        if node.type != "FACT":
            continue
        if node.origin == "research":
            # research-note FACT nodes are exempt: the note file itself is
            # the source and its `claim` line is the citable content (BI-3).
            continue
        relpath = _relpath(node.path, project.root)
        missing = [name for name, value in (("source", node.source), ("quote", node.quote)) if not value]
        for name in missing:
            violations.append(f"{relpath}: fact-source: missing {name}")
    return violations


def _rule_required_field(project: Project) -> list[str]:
    violations = []
    for node in project.nodes:
        relpath = _relpath(node.path, project.root)
        for name in ("type", "id", "seq", "summary"):
            if not getattr(node, name):
                violations.append(f"{relpath}: required-field: missing {name}")
    return violations


def _rule_problems(project: Project) -> list[str]:
    return list(project.problems)


_CHECK_RULES = (
    _rule_load_bearing,
    _rule_ref,
    _rule_fact_source,
    _rule_required_field,
    _rule_problems,
)


def check(project: Project) -> list[str]:
    """Run every structural rule against `project`, returning sorted violation lines.

    Never writes to any file — purely a read/report pass over an already-loaded
    Project. Sort by (relpath, rule) for deterministic output.
    """
    violations: list[str] = []
    for rule in _CHECK_RULES:
        violations.extend(rule(project))

    def sort_key(line: str) -> tuple[str, str]:
        relpath, _, rest = line.partition(": ")
        rule_token, _, _ = rest.partition(": ")
        return (relpath, rule_token)

    return sorted(violations, key=sort_key)


def propagate(project: Project, assumption_id: str) -> tuple[list[str], list[str]]:
    """Walk `inputs` edges outward from `assumption_id`, without writing anything.

    Returns (stale_ids, weakened_ids), each sorted. A node is stale when every
    hop of at least one chain from `assumption_id` to it is `load_bearing:
    True`; a node reachable only through chains containing a non-load-bearing
    (False or None/bare-string) hop is weakened instead.
    """
    dependents: dict[str, list[tuple[str, bool]]] = {}
    for node in project.nodes:
        if node.id is None:
            continue
        for entry in node.inputs:
            if entry.ref is None:
                continue
            dependents.setdefault(entry.ref, []).append((node.id, bool(entry.load_bearing)))

    # state[node_id] is True once a fully-load-bearing chain reached it
    # (stale), False while only a weak chain has (weakened). A node is
    # enqueued again only when its state changes (None->False, None->True,
    # or False->True) so a cycle re-visits each node at most twice and
    # always terminates.
    state: dict[str, bool] = {}

    frontier = [(assumption_id, True)]
    while frontier:
        current_id, chain_load_bearing = frontier.pop()
        for dependent_id, hop_load_bearing in dependents.get(current_id, []):
            new_ok = chain_load_bearing and hop_load_bearing
            prev = state.get(dependent_id)
            if prev is True:
                continue
            if new_ok:
                state[dependent_id] = True
                frontier.append((dependent_id, True))
            elif prev is None:
                state[dependent_id] = False
                frontier.append((dependent_id, False))

    stale = sorted(node_id for node_id, is_stale in state.items() if is_stale)
    weakened = sorted(node_id for node_id, is_stale in state.items() if not is_stale)
    return stale, weakened


def _set_frontmatter_field(path: Path, key: str, value: str) -> None:
    """Rewrite a single top-level frontmatter field in place, byte-preserving.

    Replaces the first `^<key>:\\s*.*$` line if present, else appends
    `<key>: <value>` as the last frontmatter line. Body and every other
    frontmatter line are left untouched -- including the file's original
    line-ending convention (CRLF vs LF), which is detected from the raw
    bytes rather than assumed, since text-mode reads silently translate
    CRLF to LF (universal newlines) before we ever see the content.
    """
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"

    match = re.match(r"^---\r?\n(.*?\r?\n)---\r?\n", text, flags=re.DOTALL)
    if match is None:
        return
    fm_text = match.group(1)
    body = text[match.end():]

    pattern = re.compile(rf"^{re.escape(key)}:[^\r\n]*", flags=re.MULTILINE)
    new_line = f"{key}: {value}"
    if pattern.search(fm_text):
        new_fm_text = pattern.sub(new_line, fm_text, count=1)
    else:
        if fm_text and not fm_text.endswith(eol):
            fm_text += eol
        new_fm_text = fm_text + new_line + eol

    new_text = f"---{eol}{new_fm_text}---{eol}{body}"
    path.write_bytes(new_text.encode("utf-8"))


def claims(project: Project, root: Path, since: str) -> list[str] | None:
    """Report research-note `claim` changes since `since`, with their dependents.

    For every research-note FACT node (origin == "research"), reads the file's
    frontmatter as it stood at `since` via `git show <since>:<relpath>` (never
    shell=True, no interpolated shell string) and compares `claim` values
    after `.strip()`. A file absent at that rev counts as unchanged-new.
    Returns sorted `"<id>: claim changed → dependents: <ids>"` lines, or None
    (having already printed the error) when `root` is not inside a git repo.
    """
    repo_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root, capture_output=True, text=True,
    )
    if repo_root.returncode != 0:
        print(f"not a git repository: {root}", file=sys.stderr)
        return None

    repo_root_path = Path(repo_root.stdout.strip())

    dependents_by_ref: dict[str, list[str]] = {}
    for node in project.nodes:
        if node.id is None:
            continue
        for entry in node.inputs:
            if entry.ref is not None:
                dependents_by_ref.setdefault(entry.ref, []).append(node.id)

    changed: list[str] = []
    for node in project.nodes:
        if node.origin != "research" or node.id is None:
            continue
        relpath = node.path.relative_to(repo_root_path).as_posix()
        result = subprocess.run(
            ["git", "show", f"{since}:{relpath}"],
            cwd=root, capture_output=True, text=True,
        )
        if result.returncode != 0:
            continue  # absent at that rev -- unchanged-new

        fm_text, _ = split_frontmatter(result.stdout)
        try:
            old_fm = yaml.safe_load(fm_text)
        except yaml.YAMLError:
            continue
        if not isinstance(old_fm, dict):
            continue

        old_claim = old_fm.get("claim")
        new_claim = node.summary
        old_claim_norm = old_claim.strip() if isinstance(old_claim, str) else old_claim
        new_claim_norm = new_claim.strip() if isinstance(new_claim, str) else new_claim
        if old_claim_norm == new_claim_norm:
            continue

        ids = sorted(dependents_by_ref.get(node.id, []))
        ids_text = ",".join(ids) if ids else "(none)"
        changed.append(f"{node.id}: claim changed → dependents: {ids_text}")

    return sorted(changed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dag", description="strategy-dag project loader/CLI")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("load", help="load and validate the project graph (diagnostics only)")
    check_parser = subparsers.add_parser("check", help="run the structural gate and report violations")
    check_parser.add_argument("root", help="project root directory")
    break_parser = subparsers.add_parser("break", help="mark an assumption broken and propagate stale/weakened status")
    break_parser.add_argument("root", help="project root directory")
    break_parser.add_argument("assumption_id", help="id of the assumption to break")
    claims_parser = subparsers.add_parser("claims", help="report research claims changed since a git revision, with dependents")
    claims_parser.add_argument("root", help="project root directory")
    claims_parser.add_argument("--since", default="HEAD", help="git revision to diff against (default: HEAD)")
    args = parser.parse_args(argv)

    if args.command == "load":
        project = load_project(Path.cwd())
        print(f"loaded {len(project.nodes)} node(s), {len(project.assumptions)} assumption(s)")
        return 0

    if args.command == "check":
        project = load_project(Path(args.root))
        violations = check(project)
        for line in violations:
            print(line)
        return 1 if violations else 0

    if args.command == "break":
        project = load_project(Path(args.root))
        assumption = next((a for a in project.assumptions if a.id == args.assumption_id), None)
        if assumption is None:
            print(f"assumption {args.assumption_id} not found", file=sys.stderr)
            return 1

        stale_ids, weakened_ids = propagate(project, args.assumption_id)

        _set_frontmatter_field(assumption.path, "status", "broken")
        by_id = {n.id: n for n in project.nodes}
        for node_id in stale_ids:
            _set_frontmatter_field(by_id[node_id].path, "status", "stale")

        print(f"stale: {','.join(stale_ids)}")
        print(f"weakened: {','.join(weakened_ids)}")
        return 0

    if args.command == "claims":
        root = Path(args.root)
        project = load_project(root)
        lines = claims(project, root, args.since)
        if lines is None:
            return 1
        for line in lines:
            print(line)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
