"""think-orbit core loader — parses the project's frontmatter files into a Project graph.

Subcommands: check / break / claims / render / impact.
"""
from __future__ import annotations

import argparse
import importlib
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


def _require_yaml(importer=importlib.import_module):
    """Return the PyYAML module, or say so plainly and exit 2.

    PyYAML is this script's only third-party dependency; without it every
    subcommand fails at import time with a traceback that says nothing about
    what to install.
    """
    try:
        return importer("yaml")
    except ImportError:
        print("think-orbit: PyYAML is required — pip install pyyaml", file=sys.stderr)
        raise SystemExit(2)


yaml = _require_yaml()

FRONTMATTER_DELIM = "---"
_LINE_RE = re.compile(r"[^\n]*\n|[^\n]+")


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


def _frontmatter_span(text: str) -> tuple[int, int, int] | None:
    """Locate the frontmatter block as character offsets into `text`.

    Returns `(fm_start, fm_end, body_start)` — `text[fm_start:fm_end]` is the
    raw frontmatter lines with the delimiters excluded, and `text[body_start:]`
    is the body — or None when the text opens no frontmatter block. A delimiter
    is a line that *rstrips* to `---`, LF or CRLF, so the reader and the rewriter
    accept exactly the same files. Only trailing whitespace is tolerated: an
    indented `  ---` is content — typically a markdown rule inside a YAML block
    scalar — and must not be allowed to close the block early, which would push
    every key below it into the body unnoticed.
    """
    lines = list(_LINE_RE.finditer(text))
    if not lines or lines[0].group().rstrip() != FRONTMATTER_DELIM:
        return None
    for match in lines[1:]:
        if match.group().rstrip() == FRONTMATTER_DELIM:
            return lines[0].end(), match.start(), match.end()
    return None


def split_frontmatter(text: str) -> tuple[str, str]:
    """Split raw file text into (frontmatter_text, body_text).

    Returns the frontmatter block's raw text (without the `---` delimiters)
    and the body separately, so `_frontmatter_field_rewrite` can preserve key
    order and body bytes exactly.
    """
    span = _frontmatter_span(text)
    if span is None:
        return "", text
    fm_start, fm_end, body_start = span
    return text[fm_start:fm_end], text[body_start:]


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
    relpath = path.relative_to(root).as_posix()
    try:
        raw_text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, "", f"{relpath}: frontmatter: not utf-8"
    fm_text, body = split_frontmatter(raw_text)
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


def _load_dir(directory: Path, root: Path, loader) -> tuple[list, list[str]]:
    """Load every `*.md` in `directory` through `loader`, in filename order.

    Returns (items, problems): a file whose frontmatter does not parse
    contributes a problem line instead of an item, so a malformed file is
    reported rather than silently fabricated into a Node/Assumption.
    """
    items: list = []
    problems: list[str] = []
    if not directory.is_dir():
        return items, problems
    for path in sorted(directory.glob("*.md")):
        item, problem = loader(path, root)
        if problem:
            problems.append(problem)
        else:
            items.append(item)
    return items, problems


def load_project(root: Path) -> Project:
    """Load every node/assumption/research-note *.md under root into a Project."""
    root = Path(root)
    nodes, problems = _load_dir(root / "nodes", root, _load_node)
    assumptions, assumption_problems = _load_dir(
        root / "assumptions", root, _load_assumption
    )
    research_nodes, research_problems = _load_dir(
        root / "research", root, _load_research_note_as_node
    )
    nodes += research_nodes
    problems += assumption_problems + research_problems

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
        for i, entry in enumerate(node.inputs):
            if not entry.ref:
                if entry.load_bearing is not None:
                    violations.append(f"{relpath}: ref: inputs[{i}] has no ref")
                continue
            if entry.ref not in known_ids:
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


def _id_named_in(ref: str, body: str) -> bool:
    """True when `ref` appears in `body` as a whole id, not as a substring
    of a longer id (`fact1` inside `fact10`) or a longer word (`goal` inside
    `goals` or `goal-v2`).

    Deliberately NOT `\\bref\\b`: Python's `\\b` is defined by `\\w`, and in
    Unicode mode CJK characters count as `\\w` -- so there is no boundary
    between an id and an immediately-following CJK character (`fact1的`),
    and `\\b` silently fails to match exactly the bodies this feature exists
    for (this project's real prose is CJK with no inter-word spaces). The
    lookaround below is ASCII-only on both sides, so it draws a boundary
    against `[A-Za-z0-9_-]` neighbours -- catching `fact10`, `goals`, and
    `goal-v2` (the hyphen is excluded so a short id does not match inside
    a kebab-case sibling id or an ordinary hyphenated compound) -- while
    still matching an id directly against a CJK neighbour.

    `.` is deliberately LEFT OUT of the excluded class, and that is an
    accepted residual risk, not an oversight: excluding it would also
    block the far more common case of an id sitting at the end of an
    ordinary English sentence (`... rests on fact1.`), to guard against
    the much rarer dot-versioned-sibling id (`fact1.1`). A future reader
    "completing" this class by adding `.` would silently reintroduce that
    false negative -- don't.
    """
    pattern = re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(ref) + r"(?![A-Za-z0-9_-])")
    return pattern.search(body) is not None


def _rule_input_narration(project: Project) -> list[str]:
    """A node's body must name the `id` of at least one load-bearing input.

    Violates when the body names NO load-bearing input's `id` -- naming even
    one is enough, whole-id containment only (see `_id_named_in`), verifying
    that the id was NAMED, never whether the surrounding sentence explains
    anything. When a node's inputs carry no load-bearing entry at all, it
    must instead name at least one of its non-load-bearing inputs --
    otherwise a node with only non-load-bearing inputs could never satisfy
    the check no matter what its author writes. A node with empty/absent
    `inputs` is never flagged: it has no upstream to name, mirroring the
    `origin == "research"` carve-out in `_rule_fact_source` rather than
    inventing a second exemption mechanism. An input entry with no `ref` is
    skipped -- that is `_rule_ref`'s violation to report, not this rule's.

    A lexical-overlap arm (matching the *topic* of an input's `summary`
    rather than its id) was tried and measured against the real project and
    dropped: it passed 10/10 nodes including ones that never refer to any of
    their inputs, because nodes on one reasoning chain are always about the
    same topic -- topic overlap cannot distinguish "narrates its upstream"
    from "is about the same subject". An id arm requiring EVERY load-bearing
    input to be named was also measured and rejected: it passed only 1/10,
    stricter than the corpus's own best human-authored nodes -- both
    DECISION nodes the human checkpoint had identified as genuinely
    narrating carry several load-bearing inputs and name only some of them.
    Requiring only that AT LEAST ONE load-bearing input (or, absent any,
    at least one input at all) be named gives 2/10, exactly those two
    nodes -- the only threshold measured to reproduce the human reading,
    and it is deterministic and language-independent besides.
    """
    violations = []
    for node in project.nodes:
        if not node.inputs:
            continue
        refs = [entry.ref for entry in node.inputs if entry.ref]
        if not refs:
            continue
        body = node.body
        load_bearing_refs = [
            entry.ref for entry in node.inputs if entry.ref and entry.load_bearing
        ]
        candidates = load_bearing_refs if load_bearing_refs else refs
        if not any(_id_named_in(ref, body) for ref in candidates):
            relpath = _relpath(node.path, project.root)
            kind = "load-bearing inputs" if load_bearing_refs else "inputs"
            violations.append(
                f"{relpath}: input-narration: body names none of its {kind} {sorted(candidates)}"
            )
    return violations


def _rule_required_field(project: Project) -> list[str]:
    violations = []
    for node in project.nodes:
        relpath = _relpath(node.path, project.root)
        for name in ("type", "id", "seq", "summary"):
            if not getattr(node, name):
                violations.append(f"{relpath}: required-field: missing {name}")
    return violations


_VALID_NODE_STATUSES = {"current", "stale"}


def _rule_node_status(project: Project) -> list[str]:
    """A node's `status` is `current` or `stale`; absent means `current`.

    The field is optional precisely so a hand-written node need not carry it —
    only a *set* value out of the vocabulary is a violation, because that is
    the case where `break` propagation and the renderer would disagree with
    the author about what the node's state is.
    """
    violations = []
    for node in project.nodes:
        if node.status and node.status not in _VALID_NODE_STATUSES:
            violations.append(
                f"{_relpath(node.path, project.root)}: node-status: "
                f"{node.status!r} not in {sorted(_VALID_NODE_STATUSES)}"
            )
    return violations


_VALID_ASSUMPTION_STATUSES = {"open", "broken", "confirmed"}
_ASSUMPTION_MAX_PER_BRANCH = 3


def _rule_assumption_field(project: Project) -> list[str]:
    violations = []
    for assumption in project.assumptions:
        relpath = _relpath(assumption.path, project.root)
        # `branch` is optional: an assumption with no branch is project-wide
        for name in ("id", "status", "statement", "breaks_if"):
            if not getattr(assumption, name):
                violations.append(f"{relpath}: assumption-field: missing {name}")
        if assumption.status and assumption.status not in _VALID_ASSUMPTION_STATUSES:
            violations.append(
                f"{relpath}: assumption-field: status {assumption.status!r} not in "
                f"{sorted(_VALID_ASSUMPTION_STATUSES)}"
            )
    return violations


def _rule_assumption_max(project: Project) -> list[str]:
    # project-wide assumptions (no `branch`) are not counted against any branch
    by_branch: dict[str, int] = {}
    for assumption in project.assumptions:
        if not assumption.branch:
            continue
        by_branch[assumption.branch] = by_branch.get(assumption.branch, 0) + 1

    violations = []
    for branch, count in sorted(by_branch.items()):
        if count > _ASSUMPTION_MAX_PER_BRANCH:
            violations.append(
                f"assumptions: branch {branch} has {count} assumptions (max {_ASSUMPTION_MAX_PER_BRANCH})"
            )
    return violations


def _rule_branch_has_node(project: Project) -> list[str]:
    """A branch id carried by one or more assumptions must also be carried by
    at least one node — a branch box with only floating premises and no
    claim to support argues nothing.

    A project-wide assumption (no `branch` key at all) is out of scope here,
    mirroring the carve-out in `_rule_assumption_max`: it stands outside any
    branch, so it can never trigger this rule.
    """
    node_branches = {node.branch for node in project.nodes if node.branch}
    assumption_branches = {a.branch for a in project.assumptions if a.branch}
    violations = []
    for branch in sorted(assumption_branches - node_branches):
        violations.append(
            f"assumptions: branch-has-node: branch {branch} has assumptions but no node"
        )
    return violations


def _rule_problems(project: Project) -> list[str]:
    return list(project.problems)


def _id_entries(project: Project) -> list[tuple[str, Path | None]]:
    """Every declared (id, path) pair — nodes first, then assumptions."""
    return [(n.id, n.path) for n in project.nodes if n.id] + [
        (a.id, a.path) for a in project.assumptions if a.id
    ]


def _rule_duplicate_id(project: Project) -> list[str]:
    """Flag an id declared by more than one file — the later file (by path)
    is reported and points back at the first one."""
    first_seen: dict[str, str] = {}
    violations = []
    entries = sorted(
        ((raw_id, _relpath(path, project.root)) for raw_id, path in _id_entries(project)),
        key=lambda entry: entry[1],
    )
    for raw_id, relpath in entries:
        if raw_id in first_seen:
            violations.append(
                f"{relpath}: duplicate-id: {raw_id} also declared in {first_seen[raw_id]}"
            )
        else:
            first_seen[raw_id] = relpath
    return violations


def _rule_mermaid_id_collision(project: Project) -> list[str]:
    """Flag *distinct* raw ids that sanitize to the same mermaid id (render
    disambiguates them, but the gate should still surface the underlying
    naming clash). Identical raw ids are `duplicate-id`'s business, not this
    rule's."""
    by_base: dict[str, dict[str, Path | None]] = {}
    for raw_id, path in _id_entries(project):
        by_base.setdefault(_sanitize_mermaid_id(raw_id), {}).setdefault(raw_id, path)

    violations = []
    for base, group in by_base.items():
        if len(group) < 2:
            continue
        group_sorted = sorted(group.items(), key=lambda e: e[0])
        first_id, _ = group_sorted[0]
        for other_id, other_path in group_sorted[1:]:
            relpath = _relpath(other_path, project.root)
            violations.append(
                f"{relpath}: id-collision: {first_id} and {other_id} both render as {base}"
            )
    return violations


_TERMINATOR_CHARS = ".!?。！？"
_CJK_TERMINATORS = "。！？"
_TERMINATOR_RUN_RE = re.compile(r"[.!?。！？]+")
_INLINE_CODE_RE = re.compile(r"`[^`]*`")
_URL_RE = re.compile(r"https?://\S+")
# whitespace or a closing quote/bracket -- what a terminator may be followed by
_CLOSING_RE = re.compile(r"[\s\"'’”)\]」』]")
_FENCE_START_RE = re.compile(r"^(`{3,}|~{3,})")
_ABBREV_WORD_RE = re.compile(r"([A-Za-z]+)$")
_TITLE_ABBREVIATIONS = {
    "Dr.", "Mr.", "Mrs.", "Ms.", "Prof.", "St.", "Jr.", "Sr.", "No.", "Fig.", "vs.", "etc.",
}


def _strip_fenced_blocks(text: str) -> str:
    """Remove fenced code/Mermaid blocks entirely before paragraph splitting.

    Supports both ``` and ~~~ fences (a fence closes only with the same
    marker character); an unclosed fence strips from its opening line to
    the end of the text.
    """
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        match = _FENCE_START_RE.match(lines[i].strip())
        if match is None:
            out.append(lines[i])
            i += 1
            continue
        marker_char = match.group(1)[0]
        i += 1
        while i < len(lines):
            closing = lines[i].strip()
            if closing and set(closing) == {marker_char}:
                i += 1
                break
            i += 1
    return "\n".join(out)


def _strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _is_list_item(line: str) -> bool:
    if line.startswith("- ") or line.startswith("* "):
        return True
    return bool(re.match(r"^\d+\.\s", line))


def _is_secondary_list_line(line: str) -> bool:
    """True for a list/blockquote/table line appearing below a lead-in line
    in the same block (no blank line separating them) -- excluded from the
    lead-in's sentence count."""
    stripped = line.lstrip()
    if stripped.startswith(("- ", "* ", "> ", "| ")):
        return True
    return bool(re.match(r"^\d+\.\s", stripped))


def _skip_paragraph(block: str) -> bool:
    """True when `block` is a heading, list, blockquote, or table -- not counted prose."""
    first_line = block.splitlines()[0].strip()
    if not first_line:
        return True
    if first_line.startswith(("#", ">", "|")):
        return True
    return _is_list_item(first_line)


def _count_sentences(paragraph: str) -> int:
    """Count sentence-ending terminators.

    Before counting: strip inline code spans and URLs (their punctuation
    never ends a sentence). Runs of terminators (`...`, `??`, `。。`)
    collapse into one. A `.` immediately followed by a digit (`3.5`) never
    ends a sentence. An ASCII terminator (`.!?`) ends a sentence only at
    end-of-text, or when followed by whitespace/closing-quote/bracket AND
    the next non-space character is not a lowercase ASCII letter (so
    `e.g. the`, `i.e. this`, `vs. that` don't split) -- otherwise it's
    treated as an abbreviation or mid-word punctuation. A title abbreviation
    (`Dr.`, `Mr.`, `Mrs.`, `Ms.`, `Prof.`, `St.`, `Jr.`, `Sr.`, `No.`, `Fig.`,
    `vs.`, `etc.`) never ends a sentence -- even when followed by a capital
    letter -- except at end-of-text, where the end-of-text rule wins. A CJK
    terminator (`。！？`) always ends a sentence once its run is collapsed.
    """
    text = _INLINE_CODE_RE.sub(" ", paragraph)
    text = _URL_RE.sub(" ", text)

    count = 0
    for match in _TERMINATOR_RUN_RE.finditer(text):
        run = match.group()
        end = match.end()
        if any(ch in _CJK_TERMINATORS for ch in run):
            count += 1
            continue
        if run[-1] == "." and end < len(text) and text[end].isdigit():
            continue
        if end >= len(text):
            count += 1
            continue
        if run == ".":
            word_match = _ABBREV_WORD_RE.search(text[:match.start()])
            if word_match and (word_match.group(1) + ".") in _TITLE_ABBREVIATIONS:
                continue
        if not _CLOSING_RE.match(text[end]):
            continue
        pos = end
        while pos < len(text) and _CLOSING_RE.match(text[pos]):
            pos += 1
        if pos < len(text) and text[pos].isascii() and text[pos].isalpha() and text[pos].islower():
            continue
        count += 1

    return count if count > 0 else 1


def _rule_paragraph_form(project: Project) -> list[str]:
    """Every prose body paragraph of a node (not a research note) must have 2-4 sentences.

    A block whose first line is prose but whose later lines are list/
    blockquote/table lines (a lead-in with no blank line before a list) is
    counted only from its non-list lines.
    """
    violations = []
    for node in project.nodes:
        if node.origin == "research":
            continue
        relpath = _relpath(node.path, project.root)
        body = _strip_html_comments(_strip_fenced_blocks(node.body))
        paragraph_index = 0
        for block in re.split(r"\n\s*\n", body):
            block = block.strip("\n")
            if not block.strip() or _skip_paragraph(block):
                continue
            prose_text = "\n".join(
                line for line in block.splitlines() if not _is_secondary_list_line(line)
            )
            if not prose_text.strip():
                continue
            paragraph_index += 1
            sentence_count = _count_sentences(prose_text)
            if not (2 <= sentence_count <= 4):
                violations.append(
                    f"{relpath}: paragraph-form: paragraph {paragraph_index} has {sentence_count} sentences"
                )
    return violations

_CHECK_RULES = (
    _rule_load_bearing,
    _rule_ref,
    _rule_fact_source,
    _rule_input_narration,
    _rule_required_field,
    _rule_node_status,
    _rule_assumption_field,
    _rule_assumption_max,
    _rule_branch_has_node,
    _rule_problems,
    _rule_duplicate_id,
    _rule_mermaid_id_collision,
    _rule_paragraph_form,
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


def _frontmatter_field_rewrite(path: Path, key: str, value: str) -> bytes | None:
    """Compute `path`'s new bytes with one top-level frontmatter field set.

    Replaces the first `^<key>:...` line if present, else appends
    `<key>: <value>` as the last frontmatter line. Delimiters, body and every
    other frontmatter line are copied verbatim -- including the file's original
    line-ending convention (CRLF vs LF), which is detected from the raw bytes
    rather than assumed, since text-mode reads silently translate CRLF to LF
    (universal newlines) before we ever see the content. Returns None when the
    file carries no frontmatter block to rewrite, so the caller can fail loud
    instead of reporting a write that never happened.
    """
    text = path.read_bytes().decode("utf-8")
    span = _frontmatter_span(text)
    if span is None:
        return None
    fm_start, fm_end, _ = span
    fm_text = text[fm_start:fm_end]
    eol = "\r\n" if "\r\n" in text else "\n"

    pattern = re.compile(rf"^{re.escape(key)}:[^\r\n]*", flags=re.MULTILINE)
    new_line = f"{key}: {value}"
    if pattern.search(fm_text):
        new_fm_text = pattern.sub(new_line, fm_text, count=1)
    else:
        if fm_text and not fm_text.endswith(eol):
            fm_text += eol
        new_fm_text = fm_text + new_line + eol

    return (text[:fm_start] + new_fm_text + text[fm_end:]).encode("utf-8")


# CLI surfaces: git rev-parse --show-toplevel / git show <rev>:<path> —
# grounding: git show --help, git rev-parse --help (captured 2026-08-18).
def claims(project: Project, root: Path, since: str) -> list[str] | None:
    """Report research-note `claim` changes since `since`, with their dependents.

    For every research-note FACT node (origin == "research"), reads the file's
    frontmatter as it stood at `since` via `git show <since>:<relpath>` (never
    shell=True, no interpolated shell string) and compares `claim` values
    after `.strip()`. A file absent at that rev counts as unchanged-new.
    Returns sorted `"<id>: claim changed → dependents: <ids>"` lines, or None
    (having already printed the error) when `root` is not inside a git repo
    or `since` does not resolve to a valid commit.
    """
    repo_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root, capture_output=True, text=True,
    )
    if repo_root.returncode != 0:
        print(f"not a git repository: {root}", file=sys.stderr)
        return None

    verify = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{since}^{{commit}}"],
        cwd=root, capture_output=True, text=True,
    )
    if verify.returncode != 0:
        print(f"invalid revision: {since}", file=sys.stderr)
        return None

    repo_root_path = Path(repo_root.stdout.strip()).resolve()

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
        relpath = _relpath(node.path.resolve(), repo_root_path)
        result = subprocess.run(
            ["git", "show", f"{since}:{relpath}"],
            cwd=root, capture_output=True,
        )
        if result.returncode != 0:
            continue  # absent at that rev -- unchanged-new

        stdout_text = result.stdout.decode("utf-8", errors="replace")
        fm_text, _ = split_frontmatter(stdout_text)
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


_ID_UNSAFE_RE = re.compile(r"[^A-Za-z0-9_]")

_NODE_SHAPES = {
    "GOAL": ('{{"', '"}}'),
    "FACT": ('["', '"]'),
    "CLAIM": ('("', '")'),
    "DECISION": ('[["', '"]]'),
}
_DEFAULT_SHAPE = ('["', '"]')


def _sanitize_mermaid_id(raw_id: str) -> str:
    """Map an author id to a mermaid-safe token (`[A-Za-z0-9_]` only).

    Two distinct raw ids can sanitize to the same token (e.g. `a-1` and
    `a_1` both become `a_1`) -- callers that must keep nodes distinct use
    `_mermaid_ids()` instead, which disambiguates collisions.
    """
    return _ID_UNSAFE_RE.sub("_", raw_id)


def _mermaid_ids(project: Project) -> dict[str, str]:
    """Map every node/assumption raw id to a collision-free mermaid id.

    Built once per render. Ids are sanitized (`_sanitize_mermaid_id`); when
    two or more raw ids sanitize to the same token, the alphabetically-first
    raw id keeps the bare token and every later one gets a deterministic
    `_2`, `_3`, ... suffix -- so colliding nodes never silently merge.
    """
    raw_ids = sorted(
        {n.id for n in project.nodes if n.id} | {a.id for a in project.assumptions if a.id}
    )
    mapping: dict[str, str] = {}
    seen_count: dict[str, int] = {}
    for raw_id in raw_ids:
        base = _sanitize_mermaid_id(raw_id)
        seen_count[base] = seen_count.get(base, 0) + 1
        count = seen_count[base]
        mapping[raw_id] = base if count == 1 else f"{base}_{count}"
    return mapping


def _mermaid_label_text(text: str, limit: int = 60) -> str:
    """Strip newlines, truncate over `limit` chars with '…', escape `" < >`."""
    flat = " ".join((text or "").splitlines())
    if len(flat) > limit:
        flat = flat[:limit] + "…"
    return flat.replace('"', "#quot;").replace("<", "#lt;").replace(">", "#gt;")


def _node_mermaid_line(node: Node, mermaid_id: str) -> str:
    label = f"{_mermaid_label_text(node.id)}<br/>{_mermaid_label_text(node.summary)}"
    open_tok, close_tok = _NODE_SHAPES.get(node.type, _DEFAULT_SHAPE)
    return f'    {mermaid_id}{open_tok}{label}{close_tok}'


def _assumption_mermaid_line(assumption: Assumption, mermaid_id: str) -> str:
    label = f"{_mermaid_label_text(assumption.id)}<br/>{_mermaid_label_text(assumption.statement)}"
    return f'    {mermaid_id}(["{label}"])'


def render_dag(project: Project) -> str:
    """Render `project` as a single `flowchart TD` mermaid block (pure, no I/O).

    Every node with an `id` is drawn (shape by `type`), every assumption as a
    stadium node grouped into its branch's subgraph, one edge per `inputs`
    entry, and a `stale` classDef applied to nodes whose `status == "stale"`.
    A node without an `id` has no drawable identity and is skipped -- `check`
    already reports it as a missing required field. Deterministic: same
    `project` always yields the same string.
    """
    lines = [
        "<!-- generated by dag.py render — regenerate, never hand-edit; agent must not read -->",
        "",
        "```mermaid",
        "flowchart TD",
    ]

    nodes = [node for node in project.nodes if node.id]

    if not nodes:
        lines.append("    %% no nodes yet")
        lines.append("```")
        return "\n".join(lines) + "\n"

    mermaid_ids = _mermaid_ids(project)

    nodes_by_branch: dict[str, list[Node]] = {}
    top_level_nodes: list[Node] = []
    for node in nodes:
        if node.branch:
            nodes_by_branch.setdefault(node.branch, []).append(node)
        else:
            top_level_nodes.append(node)

    assumptions_by_branch: dict[str, list[Assumption]] = {}
    top_level_assumptions: list[Assumption] = []
    for assumption in sorted(project.assumptions, key=lambda a: a.id or ""):
        if assumption.branch:
            assumptions_by_branch.setdefault(assumption.branch, []).append(assumption)
        else:
            top_level_assumptions.append(assumption)

    for node in top_level_nodes:
        lines.append(_node_mermaid_line(node, mermaid_ids[node.id]))
    for assumption in top_level_assumptions:
        lines.append(_assumption_mermaid_line(assumption, mermaid_ids[assumption.id]))

    branches = sorted(set(nodes_by_branch) | set(assumptions_by_branch))
    for branch in branches:
        members = nodes_by_branch.get(branch, [])
        branch_type = next((n.branch_type for n in members if n.branch_type), "?")
        # `br_` prefix keeps a branch id from colliding with a node's mermaid id
        branch_id = f"br_{_sanitize_mermaid_id(branch)}"
        title = f"{_mermaid_label_text(branch)} ({_mermaid_label_text(branch_type)})"
        lines.append(f'    subgraph {branch_id} ["{title}"]')
        for node in members:
            lines.append(f"    {_node_mermaid_line(node, mermaid_ids[node.id]).strip()}")
        for assumption in assumptions_by_branch.get(branch, []):
            lines.append(f"    {_assumption_mermaid_line(assumption, mermaid_ids[assumption.id]).strip()}")
        lines.append("    end")

    for node in nodes:
        node_id = mermaid_ids[node.id]
        for entry in node.inputs:
            if entry.ref is None:
                continue
            ref_id = mermaid_ids.get(entry.ref, _sanitize_mermaid_id(entry.ref))
            arrow = "-->" if entry.load_bearing else "-.->"
            lines.append(f"    {ref_id} {arrow} {node_id}")

    stale_ids = sorted(
        mermaid_ids[n.id] for n in nodes if n.status == "stale"
    )
    if stale_ids:
        lines.append("    classDef stale fill:#f1f3f5,stroke:#adb5bd,color:#868e96")
        lines.append(f"    class {','.join(stale_ids)} stale")

    lines.append("```")
    return "\n".join(lines) + "\n"


_FILENAME_UNSAFE_RE = re.compile(r"[^A-Za-z0-9_-]")


def _sanitize_filename_component(raw_id: str) -> str:
    """Map an author id to a filesystem-safe token (`[A-Za-z0-9_-]` only)."""
    return _FILENAME_UNSAFE_RE.sub("_", raw_id)


def render_impact(project: Project, assumption_id: str) -> str:
    """Render the assumption-impact view for `assumption_id` as a single
    `flowchart LR` mermaid block (pure, no I/O, no mutation of `project`).

    Caller must ensure `assumption_id` names an assumption in `project` —
    this raises `KeyError` otherwise. Computes reachability via
    `propagate()`: every stale (fully load-bearing chain) and weakened
    (chain contains a non-load-bearing hop) dependent is drawn as a box;
    edges among the shown nodes follow the actual `inputs` edges (solid
    when `load_bearing`, dashed otherwise). A `stale` classDef/class is
    applied only to shown nodes whose *current* `status == "stale"`.
    Deterministic: same `project` + `assumption_id` always yields the same
    string.
    """
    assumption = _find_assumption(project, assumption_id)
    if assumption is None:
        raise KeyError(f"no assumption with id {assumption_id!r}")
    stale_ids, weakened_ids = propagate(project, assumption_id)
    shown_ids = set(stale_ids) | set(weakened_ids)

    mermaid_ids = _mermaid_ids(project)
    by_id = {n.id: n for n in project.nodes if n.id}

    lines = [
        "<!-- generated by dag.py impact — regenerate, never hand-edit; agent must not read -->",
        "",
        "```mermaid",
        "flowchart LR",
        _assumption_mermaid_line(assumption, mermaid_ids[assumption_id]),
    ]

    for node_id in sorted(shown_ids):
        lines.append(_node_mermaid_line(by_id[node_id], mermaid_ids[node_id]))

    for node_id in sorted(shown_ids):
        node = by_id[node_id]
        for entry in node.inputs:
            if entry.ref is None:
                continue
            if entry.ref != assumption_id and entry.ref not in shown_ids:
                continue
            ref_mermaid_id = mermaid_ids.get(entry.ref, _sanitize_mermaid_id(entry.ref))
            arrow = "-->" if entry.load_bearing else "-.->"
            lines.append(f"    {ref_mermaid_id} {arrow} {mermaid_ids[node_id]}")

    stale_mermaid_ids = sorted(
        mermaid_ids[node_id] for node_id in shown_ids if by_id[node_id].status == "stale"
    )
    if stale_mermaid_ids:
        lines.append("    classDef stale fill:#f1f3f5,stroke:#adb5bd,color:#868e96")
        lines.append(f"    class {','.join(stale_mermaid_ids)} stale")

    lines.append("```")
    return "\n".join(lines) + "\n"


def _write_view(root: Path, filename: str, content: str) -> Path:
    """Write `content` to `<root>/views/<filename>`, creating the dir. Returns the path."""
    views_dir = root / "views"
    views_dir.mkdir(parents=True, exist_ok=True)
    view_path = views_dir / filename
    view_path.write_text(content, encoding="utf-8")
    return view_path


def _find_assumption(project: Project, assumption_id: str) -> Assumption | None:
    return next((a for a in project.assumptions if a.id == assumption_id), None)


def _impact_view_filename(assumption_id: str) -> str:
    return f"impact-{_sanitize_filename_component(assumption_id)}.md"


def _cmd_check(args) -> int:
    violations = check(load_project(Path(args.root)))
    for line in violations:
        print(line)
    return 1 if violations else 0


def _cmd_break(args) -> int:
    root = Path(args.root)
    project = load_project(root)
    assumption = _find_assumption(project, args.assumption_id)
    if assumption is None:
        print(f"assumption {args.assumption_id} not found", file=sys.stderr)
        return 1

    stale_ids, weakened_ids = propagate(project, args.assumption_id)
    by_id = {n.id: n for n in project.nodes if n.id}
    targets = [(assumption, "broken")] + [(by_id[node_id], "stale") for node_id in stale_ids]

    # compute every rewrite before writing any of it, so an unrewritable file
    # stops the whole command instead of leaving the project half-marked
    rewrites: list[tuple[Path, bytes]] = []
    failed = False
    for entity, status in targets:
        new_bytes = (
            None if entity.path is None
            else _frontmatter_field_rewrite(entity.path, "status", status)
        )
        if new_bytes is None:
            print(
                f"cannot rewrite frontmatter: {_relpath(entity.path, root)}",
                file=sys.stderr,
            )
            failed = True
        else:
            rewrites.append((entity.path, new_bytes))
    if failed:
        return 1

    for path, new_bytes in rewrites:
        path.write_bytes(new_bytes)
    for entity, status in targets:
        entity.status = status

    view_path = _write_view(
        root,
        _impact_view_filename(args.assumption_id),
        render_impact(project, args.assumption_id),
    )

    print(f"stale: {','.join(stale_ids)}")
    print(f"weakened: {','.join(weakened_ids)}")
    print(f"impact view: {_relpath(view_path, root)}")
    return 0


def _cmd_impact(args) -> int:
    root = Path(args.root)
    project = load_project(root)
    if _find_assumption(project, args.assumption_id) is None:
        print(f"assumption {args.assumption_id} not found", file=sys.stderr)
        return 1

    view_path = _write_view(
        root,
        _impact_view_filename(args.assumption_id),
        render_impact(project, args.assumption_id),
    )
    print(f"impact view: {_relpath(view_path, root)}")
    return 0


def _cmd_claims(args) -> int:
    root = Path(args.root)
    lines = claims(load_project(root), root, args.since)
    if lines is None:
        return 1
    for line in lines:
        print(line)
    return 0


def _cmd_render(args) -> int:
    root = Path(args.root)
    view_path = _write_view(root, "dag.md", render_dag(load_project(root)))
    print(f"dag view: {_relpath(view_path, root)}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dag", description="think-orbit project loader/CLI")
    subparsers = parser.add_subparsers(dest="command")
    check_parser = subparsers.add_parser("check", help="run the structural gate and report violations")
    check_parser.add_argument("root", help="project root directory")
    break_parser = subparsers.add_parser("break", help="mark an assumption broken and propagate stale/weakened status")
    break_parser.add_argument("root", help="project root directory")
    break_parser.add_argument("assumption_id", help="id of the assumption to break")
    claims_parser = subparsers.add_parser("claims", help="report research claims changed since a git revision, with dependents")
    claims_parser.add_argument("root", help="project root directory")
    claims_parser.add_argument("--since", default="HEAD", help="git revision to diff against (default: HEAD)")
    render_parser = subparsers.add_parser("render", help="write views/dag.md — the full DAG mermaid view")
    render_parser.add_argument("root", help="project root directory")
    impact_parser = subparsers.add_parser("impact", help="write views/impact-<id>.md — one assumption's impact view")
    impact_parser.add_argument("root", help="project root directory")
    impact_parser.add_argument("assumption_id", help="id of the assumption to render impact for")
    return parser


_COMMANDS = {
    "check": _cmd_check,
    "break": _cmd_break,
    "impact": _cmd_impact,
    "claims": _cmd_claims,
    "render": _cmd_render,
}


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    handler = _COMMANDS.get(args.command)
    if handler is None:
        parser.print_help()
        return 0
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
