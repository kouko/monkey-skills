"""Decision Map validation rules, independent of the store facade."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path

from map_documents import MapDocument, TicketDocument, SchemaViolation
from map_persistence import assert_contained as _assert_contained

MIN_SUPPORTED_SCHEMA_VERSION = 3
SUPPORTED_SCHEMA_VERSION = 3

VALID_MAP_STATES = {"charting", "active", "clear", "archived"}
LIVE_MAP_STATES = {"charting", "active"}
V2_TICKET_TYPES = {"grilling", "research", "task", "prototype"}
V3_TICKET_TYPES = {"grilling", "research", "prototype", "delivery"}
HITL_TICKET_TYPES = {"grilling", "prototype"}
RATIFIED_MAP_STATES = {"active", "clear"}
V2_TICKET_STATUSES = {"open", "claimed", "closed"}
V3_TICKET_STATUSES = {"open", "claimed", "closed", "withdrawn"}
V3_TICKET_FRONTMATTER_FIELDS = {
    "type",
    "status",
    "claim",
    "graduated-from",
    "blocked-by",
    "ratification",
    "withdrawn-from",
    "brief",
}


REQUIRED_SECTIONS = [
    "Destination",
    "Notes",
    "Decisions-so-far",
    "Not-yet-specified (fog)",
    "Out-of-scope",
]


_COMMIT_EVIDENCE = re.compile(r"(?:commit\s+)?[0-9a-fA-F]{7,40}")
_PR_EVIDENCE = re.compile(
    r"(?:PR\s*)?#\d+|(?:PR\s+)?https?://\S+/pull/\d+",
    re.IGNORECASE,
)
_ARTIFACT_PATH_EVIDENCE = re.compile(
    r"(?:\.{1,2}/|/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+"
)


def _has_delivery_evidence(text: str) -> bool:
    """Recognize the three delivery-evidence shapes pinned by the
    ticket contract: commit SHA, PR reference, or artifact path."""
    for line in text.splitlines():
        key, separator, value = line.strip().partition(":")
        if separator != ":" or key != "delivery-evidence":
            continue
        evidence = value.strip()
        if any(
            pattern.fullmatch(evidence)
            for pattern in (
                _COMMIT_EVIDENCE,
                _PR_EVIDENCE,
                _ARTIFACT_PATH_EVIDENCE,
            )
        ):
            return True
    return False


_SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DATED_HUMAN = re.compile(r"^[^,\s][^,]*,\s*\d{4}-\d{2}-\d{2}$")


def _check_schema_version(schema_version: int) -> None:
    if schema_version < MIN_SUPPORTED_SCHEMA_VERSION:
        raise SchemaViolation(
            f"schema_version {schema_version} is retired; migrate MAP.md "
            f"to schema_version {MIN_SUPPORTED_SCHEMA_VERSION} or later"
        )
    if schema_version > SUPPORTED_SCHEMA_VERSION:
        raise SchemaViolation(
            f"schema_version {schema_version} is newer than the "
            f"supported ceiling {SUPPORTED_SCHEMA_VERSION} — refusing "
            "to read further"
        )


def _has_user_ratified_line(text: str) -> bool:
    """Whether a `user-ratified:` line carries a non-empty value.

    A bare `user-ratified:` token is not a ratification (R3b): a
    ratified decision must carry a name/date value.
    """
    return any(
        line.strip().partition(":")[0] == "user-ratified"
        and bool(line.strip().partition(":")[2].strip())
        for line in text.splitlines()
    )


def _has_resolution_field(text: str, field: str) -> bool:
    """Whether a Resolution contains a non-empty `field: value` line."""
    return any(
        line.strip().partition(":")[0] == field
        and bool(line.strip().partition(":")[2].strip())
        for line in text.splitlines()
    )


def _has_named_dated_user_ratification(text: str) -> bool:
    return any(
        re.fullmatch(
            r"user-ratified:\s*[^,\s][^,]*,\s*\d{4}-\d{2}-\d{2}",
            line.strip(),
        )
        for line in text.splitlines()
    )


def _check_v3_ticket_closure_evidence(ticket: TicketDocument) -> None:
    """Require each schema-v3 ticket type's distinct closure record."""
    resolution = ticket.resolution or ""
    ticket_type = ticket.frontmatter.type
    requirements = {
        "grilling": (
            ("decision",),
            "a non-empty 'decision:' line and named/date "
            "'user-ratified: <name>, YYYY-MM-DD'",
        ),
        "research": (
            ("factual-answer", "inspectable-evidence"),
            "non-empty 'factual-answer:' and 'inspectable-evidence:' lines",
        ),
        "prototype": (
            ("candidate-artifact", "evaluation"),
            "non-empty 'candidate-artifact:' and 'evaluation:' lines and "
            "named/date 'user-ratified: <name>, YYYY-MM-DD'",
        ),
    }
    if ticket_type == "delivery":
        if not _has_delivery_evidence(resolution):
            raise SchemaViolation(
                f"{ticket.path}: closed delivery ticket requires "
                "'delivery-evidence: <commit SHA | PR | artifact path>'"
            )
        return
    fields, guidance = requirements[ticket_type]
    needs_ratification = ticket_type in HITL_TICKET_TYPES
    if not all(_has_resolution_field(resolution, field) for field in fields) or (
        needs_ratification and not _has_named_dated_user_ratification(resolution)
    ):
        raise SchemaViolation(
            f"{ticket.path}: closed {ticket_type} ticket requires {guidance}"
        )


def _check_v3_ticket_withdrawal(ticket: TicketDocument) -> None:
    """Require a ratified disposition without treating it as closure."""
    if ticket.frontmatter.withdrawn_from not in {"open", "claimed"}:
        raise SchemaViolation(
            f"{ticket.path}: withdrawn ticket must name 'withdrawn-from: open' "
            "or 'withdrawn-from: claimed'"
        )
    withdrawal = ticket.withdrawal or ""
    if ticket.resolution is not None:
        raise SchemaViolation(
            f"{ticket.path}: withdrawn ticket must not carry a Resolution; "
            "withdrawal does not satisfy subtype closure evidence"
        )
    if not _has_named_dated_user_ratification(withdrawal):
        raise SchemaViolation(
            f"{ticket.path}: withdrawn ticket requires named/date "
            "'user-ratified: <name>, YYYY-MM-DD' in its Withdrawal"
        )
    if not _has_resolution_field(withdrawal, "reason"):
        raise SchemaViolation(
            f"{ticket.path}: withdrawn ticket requires a non-empty "
            "'reason:' line in its Withdrawal"
        )


def _check_v3_ticket_frontmatter(ticket: TicketDocument) -> None:
    """Keep v3 progress derived from artifacts, not ticket fields."""
    unknown = sorted(ticket.frontmatter_keys - V3_TICKET_FRONTMATTER_FIELDS)
    if unknown:
        raise SchemaViolation(
            f"{ticket.path}: v3 ticket has unsupported frontmatter field(s) "
            f"{', '.join(unknown)}; persisted progress is derived from owning "
            "artifacts, not ticket fields"
        )


def _check_map_structure(doc: MapDocument) -> None:
    if doc.frontmatter.state not in VALID_MAP_STATES:
        raise SchemaViolation(
            f"MAP.md frontmatter 'state' {doc.frontmatter.state!r} is not "
            f"one of {sorted(VALID_MAP_STATES)}"
        )
    missing = [s for s in REQUIRED_SECTIONS if s not in doc.sections]
    if missing:
        raise SchemaViolation(
            f"MAP.md is missing required section(s): {', '.join(missing)}"
        )
    present_order = [name for name in doc.sections if name in REQUIRED_SECTIONS]
    if present_order != REQUIRED_SECTIONS:
        raise SchemaViolation(
            "MAP.md sections are out of order: map-format.md pins "
            f"{REQUIRED_SECTIONS}, found {present_order}"
        )
    seen_fog_ids: set[str] = set()
    previous_fog_number = 0
    for fog in doc.fog_entries:
        if not re.fullmatch(r"F-[0-9]+", fog.id):
            raise SchemaViolation(f"malformed fog id: {fog.id!r}")
        if fog.id in seen_fog_ids:
            raise SchemaViolation(f"duplicate fog id reused: {fog.id!r}")
        if fog.number <= previous_fog_number:
            raise SchemaViolation("fog ids must be monotonic in document order")
        seen_fog_ids.add(fog.id)
        previous_fog_number = fog.number
    if doc.frontmatter.state in RATIFIED_MAP_STATES and not _has_user_ratified_line(
        doc.sections.get("Destination", "")
    ):
        raise SchemaViolation(
            f"{doc.path}: state {doc.frontmatter.state!r} requires a "
            "non-empty 'user-ratified:' line like "
            "'user-ratified: <name>, YYYY-MM-DD' in the Destination section "
            "(map-format.md §Sections)"
        )
    if doc.frontmatter.state == "clear" and doc.fog_entries:
        raise SchemaViolation(
            f"{doc.path}: clear map has non-empty fog "
            "(map-format.md §Ticket boundary contract)"
        )


def _da_evidence_is_resolvable(evidence: str, repo_root: Path | None) -> bool:
    """A satisfied objective criterion's evidence must be a pointer a
    reviewer can actually open, per R3c: an existing commit SHA, a
    well-formed PR reference, or an artifact path that exists inside
    the repo. A bare non-pointer string ("looks done") is not
    evidence.

    Grounding (external-surface category 4, CLI flag): the
    `git cat-file -e <sha>^{commit}` form mirrors the in-repo idiom
    at `loom-code/scripts/review_context.py` — the `^{commit}` peel
    asserts commit-ness (gitrevisions(7)) and neutralises
    flag-shaped refs."""
    pr_match = _PR_EVIDENCE.fullmatch(evidence)
    if pr_match is not None:
        return True
    commit_match = _COMMIT_EVIDENCE.fullmatch(evidence)
    if commit_match is not None:
        sha = evidence.split()[-1]
        if repo_root is None:
            return False
        try:
            subprocess.run(
                ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                cwd=repo_root,
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return False
        return True
    if _ARTIFACT_PATH_EVIDENCE.fullmatch(evidence) is not None:
        if repo_root is None:
            return False
        candidate = repo_root / evidence
        try:
            _assert_contained(repo_root, candidate)
        except SchemaViolation:
            return False
        return candidate.resolve().is_file()
    return False


def _check_destination_acceptance(doc: MapDocument, repo_root: Path | None = None) -> None:
    if doc.frontmatter.schema_version != 3:
        return
    if any(
        line.strip().startswith("acceptance:")
        for line in doc.sections.get("Destination", "").splitlines()
    ):
        raise SchemaViolation(
            "schema-v3 Destination acceptance requires stable DA-<n> entries"
        )
    if doc.frontmatter.state == "active" and not doc.destination_acceptance:
        raise SchemaViolation(
            f"{doc.path}: activation requires a Destination acceptance "
            "criterion (map-format.md §Frontmatter and lifecycle); "
            "add at least one DA-<n> entry before state: active"
        )
    seen: set[str] = set()
    previous = 0
    for criterion in doc.destination_acceptance:
        if criterion.id in seen:
            raise SchemaViolation(
                f"duplicate Destination acceptance id reused: {criterion.id}"
            )
        if criterion.number <= previous:
            raise SchemaViolation(
                "Destination acceptance ids must be monotonic in document order"
            )
        seen.add(criterion.id)
        previous = criterion.number
        if criterion.state not in {"open", "satisfied"}:
            raise SchemaViolation(
                f"Destination acceptance {criterion.id} state must be open or satisfied"
            )
        if criterion.kind not in {"objective", "evaluative"}:
            raise SchemaViolation(
                f"Destination acceptance {criterion.id} kind must be objective or evaluative"
            )
        if criterion.state == "satisfied" and criterion.evidence is None:
            raise SchemaViolation(
                f"satisfied Destination acceptance {criterion.id} requires evidence"
            )
        if (
            criterion.kind == "objective"
            and criterion.state == "satisfied"
            and criterion.evidence is not None
            and not _da_evidence_is_resolvable(criterion.evidence, repo_root)
        ):
            raise SchemaViolation(
                f"satisfied objective Destination acceptance {criterion.id} "
                "requires a resolvable evidence pointer (existing commit SHA, "
                "PR reference, or artifact path within the repo), not "
                f"{criterion.evidence!r}"
            )
        if criterion.kind == "evaluative" and criterion.state == "satisfied":
            if criterion.ratification is None or not _DATED_HUMAN.fullmatch(
                criterion.ratification
            ):
                raise SchemaViolation(
                    f"satisfied evaluative Destination acceptance {criterion.id} "
                    "requires named dated user ratification"
                )
    reused = sorted(seen.intersection(doc.retired_da_ids))
    if reused:
        raise SchemaViolation(
            "Destination acceptance id reused from retirement history: "
            + ", ".join(reused)
        )


def _check_v3_clear_acceptance(doc: MapDocument) -> None:
    """Gate clear on stable, satisfied Destination acceptance criteria."""
    if doc.frontmatter.schema_version != 3 or doc.frontmatter.state != "clear":
        return
    if doc.sections["Not-yet-specified (fog)"].strip():
        raise SchemaViolation(
            f"{doc.path}: clear v3 map requires an empty fog section"
        )
    if not doc.destination_acceptance:
        raise SchemaViolation(
            f"{doc.path}: clear v3 map requires a Destination acceptance criterion"
        )
    unsatisfied = [
        criterion.id
        for criterion in doc.destination_acceptance
        if criterion.state != "satisfied" or criterion.evidence is None
    ]
    if unsatisfied:
        raise SchemaViolation(
            f"{doc.path}: clear map requires every Destination acceptance "
            "criterion satisfied with evidence; open/invalid: "
            + ", ".join(unsatisfied)
        )


def _check_tickets(
    map_dir: Path, state: str, schema_version: int, *,
    read_ticket: Callable[[Path], TicketDocument],
) -> None:
    tickets_dir = Path(map_dir) / "tickets"
    if not tickets_dir.is_dir():
        return
    valid_ticket_types = (
        V3_TICKET_TYPES if schema_version == 3 else V2_TICKET_TYPES
    )
    valid_ticket_statuses = (
        V3_TICKET_STATUSES if schema_version == 3 else V2_TICKET_STATUSES
    )
    blocked_by_graph: dict[str, list[str]] = {}
    statuses: dict[str, str] = {}
    non_closed: list[str] = []
    for ticket_path in sorted(tickets_dir.glob("*.md")):
        ticket = read_ticket(ticket_path)
        if ticket.frontmatter.type not in valid_ticket_types:
            guidance = (
                "; classify the ticket by its closure evidence as one of "
                f"{sorted(valid_ticket_types)}"
                if schema_version == 3
                else ""
            )
            raise SchemaViolation(
                f"{ticket_path}: type {ticket.frontmatter.type!r} is not "
                f"one of {sorted(valid_ticket_types)}{guidance}"
            )
        if ticket.frontmatter.status not in valid_ticket_statuses:
            raise SchemaViolation(
                f"{ticket_path}: status {ticket.frontmatter.status!r} is "
                f"not one of {sorted(valid_ticket_statuses)}"
            )
        if schema_version == 3:
            _check_v3_ticket_frontmatter(ticket)
        if schema_version == 3 and ticket.frontmatter.status == "closed":
            _check_v3_ticket_closure_evidence(ticket)
        if schema_version == 3 and ticket.frontmatter.status == "withdrawn":
            _check_v3_ticket_withdrawal(ticket)
        if (
            ticket.frontmatter.status == "closed"
            and ticket.frontmatter.type in HITL_TICKET_TYPES
            and not _has_user_ratified_line(ticket.resolution or "")
        ):
            raise SchemaViolation(
                f"{ticket_path}: closed {ticket.frontmatter.type} ticket "
                "is missing a non-empty 'user-ratified: <name>, YYYY-MM-DD' "
                "line in its Resolution "
                "(map-format.md §Ticket schema HITL rule)"
            )
        if (
            ticket.frontmatter.status == "closed"
            and schema_version == 2
            and ticket.frontmatter.type == "task"
            and not _has_delivery_evidence(ticket.resolution or "")
        ):
            raise SchemaViolation(
                f"{ticket_path}: closed task ticket requires a non-empty "
                "Resolution with 'delivery-evidence: <commit SHA | PR | "
                "artifact path>' (map-format.md §Ticket schema)"
            )
        if ticket.frontmatter.status in {"open", "claimed"}:
            non_closed.append(
                f"{ticket_path.name} ({ticket.frontmatter.status})"
            )
        blocked_by_graph[ticket_path.stem] = ticket.frontmatter.blocked_by
        statuses[ticket_path.stem] = ticket.frontmatter.status
    _check_blocked_by(blocked_by_graph, tickets_dir)
    for slug, blockers in blocked_by_graph.items():
        if statuses[slug] != "claimed":
            continue
        unclosed = [blocker for blocker in blockers if statuses[blocker] != "closed"]
        if unclosed:
            raise SchemaViolation(
                f"{tickets_dir / (slug + '.md')}: claimed ticket requires every "
                "blocker closed; still blocking: " + ", ".join(unclosed)
            )
    for slug, status in statuses.items():
        if status != "withdrawn":
            continue
        stranded = [
            dependent
            for dependent, blockers in blocked_by_graph.items()
            if slug in blockers and statuses[dependent] in {"open", "claimed"}
        ]
        if stranded:
            raise SchemaViolation(
                f"{tickets_dir / (slug + '.md')}: withdrawn ticket would strand "
                "nonterminal dependent(s): "
                + ", ".join(f"{dependent}.md" for dependent in stranded)
            )
    if state == "clear" and non_closed:
        raise SchemaViolation(
            "clear map has non-closed ticket(s): " + ", ".join(non_closed)
        )


def _check_blocked_by(
    graph: dict[str, list[str]], tickets_dir: Path
) -> None:
    """map-format.md §Ticket schema's blocked-by bullet: every slug
    names an existing sibling ticket file, and the blocked-by graph is
    acyclic — dangling slugs and cycles exit 2."""
    for slug, blockers in graph.items():
        invalid = [blocker for blocker in blockers if not _SAFE_SLUG.fullmatch(blocker)]
        if invalid:
            raise SchemaViolation(
                f"{tickets_dir / (slug + '.md')}: blocked-by cross-Map or malformed "
                "target(s): " + ", ".join(invalid)
            )
        if slug in blockers:
            raise SchemaViolation(
                f"{tickets_dir / (slug + '.md')}: blocked-by self edge is forbidden"
            )
        duplicates = sorted(
            blocker for blocker in set(blockers) if blockers.count(blocker) > 1
        )
        if duplicates:
            raise SchemaViolation(
                f"{tickets_dir / (slug + '.md')}: duplicate blocked-by edge(s): "
                + ", ".join(duplicates)
            )
        for blocker in blockers:
            if blocker not in graph:
                raise SchemaViolation(
                    f"{tickets_dir / (slug + '.md')}: blocked-by missing target; names "
                    f"{blocker!r}, but no ticket file "
                    f"'{blocker}.md' exists in {tickets_dir}"
                )
    # cycle detection: iterative DFS with three-color marking
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {slug: WHITE for slug in graph}
    for start in sorted(graph):
        if color[start] != WHITE:
            continue
        stack: list[tuple[str, int]] = [(start, 0)]
        path: list[str] = []
        while stack:
            slug, edge_index = stack.pop()
            if edge_index == 0:
                color[slug] = GRAY
                path.append(slug)
            blockers = graph[slug]
            advanced = False
            for i in range(edge_index, len(blockers)):
                nxt = blockers[i]
                if color[nxt] == GRAY:
                    cycle = path[path.index(nxt):] + [nxt]
                    raise SchemaViolation(
                        "blocked-by graph has a cycle: "
                        + " -> ".join(cycle)
                    )
                if color[nxt] == WHITE:
                    stack.append((slug, i + 1))
                    stack.append((nxt, 0))
                    advanced = True
                    break
            if not advanced:
                color[slug] = BLACK
                path.pop()


def _check_monotonic_relations(
    map_dir: Path, doc: MapDocument, *,
    read_ticket: Callable[[Path], TicketDocument],
) -> None:
    if doc.frontmatter.schema_version != 3:
        return
    out_of_scope_ids = {
        match.group("id")
        for line in doc.out_of_scope
        if (match := re.match(r"^(?P<id>F-[0-9]+)\s*:", line)) is not None
    }
    graduated: dict[str, list[str]] = {}
    closed_tickets: list[str] = []
    for ticket_path in sorted((Path(map_dir) / "tickets").glob("*.md")):
        ticket = read_ticket(ticket_path)
        if ticket.frontmatter.graduated_from:
            graduated.setdefault(ticket.frontmatter.graduated_from, []).append(
                ticket_path.name
            )
        if ticket.frontmatter.status == "closed":
            closed_tickets.append(ticket_path.name)
    current_fog = {entry.id for entry in doc.fog_entries}
    reused_fog = sorted(current_fog.intersection(out_of_scope_ids | set(graduated)))
    if reused_fog:
        raise SchemaViolation(
            "partial fog graduation or fog id reused from graduated or "
            "Out-of-scope history: "
            + ", ".join(reused_fog)
        )
    duplicate_graduations = sorted(
        fog_id for fog_id, tickets in graduated.items() if len(tickets) > 1
    )
    if duplicate_graduations:
        raise SchemaViolation(
            "fog entry graduated more than once: " + ", ".join(duplicate_graduations)
        )
    gist_counts: dict[str, int] = {}
    for decision in doc.decisions:
        gist_counts[decision.ticket_link] = gist_counts.get(decision.ticket_link, 0) + 1
    bad_gists = [
        ticket
        for ticket in closed_tickets
        if gist_counts.get(f"tickets/{ticket}", 0) != 1
    ]
    if bad_gists:
        raise SchemaViolation(
            "every closed ticket requires exactly one Decisions-so-far gist: "
            + ", ".join(bad_gists)
        )


def validate_document(
    map_dir: Path, doc: MapDocument, repo_root: Path | None, *,
    read_ticket: Callable[[Path], TicketDocument],
) -> None:
    """Apply store rules in diagnostic order; the facade owns file errors."""
    _check_schema_version(doc.frontmatter.schema_version)
    _check_map_structure(doc)
    _check_destination_acceptance(doc, repo_root)
    _check_v3_clear_acceptance(doc)
    _check_tickets(
        map_dir, doc.frontmatter.state, doc.frontmatter.schema_version,
        read_ticket=read_ticket,
    )
    _check_monotonic_relations(map_dir, doc, read_ticket=read_ticket)

