"""Living-spec index generator.

`load_namespace(specs_dir)` builds the req-to-capability namespace from a
loom-spec tree: each `<specs_dir>/<capability>/spec.md` declares its
requirements via `### Requirement: <id>` headings, and the capability is
the immediate subdirectory name. Returns `{req_id: capability}`.

Stdlib only (pathlib + re).
"""

import re
from pathlib import Path

# A requirement heading: `### Requirement: <id>` with an optional trailing
# `[active|deferred]` status suffix. The id group is non-greedy and the
# suffix is captured separately, so `### Requirement: REQ-1 [deferred]`
# yields id "REQ-1" (NOT "REQ-1 [deferred]") — both `load_namespace` and
# `load_req_status` key on this same id. Only `active`/`deferred` are
# recognized; any other trailing bracket stays part of the id group and
# `load_req_status` defaults it to active.
_REQUIREMENT_STATUS_RE = re.compile(
    r"^###\s+Requirement:\s*(.+?)\s*(?:\[(active|deferred)\])?\s*$"
)


def load_namespace(specs_dir: Path) -> dict[str, str]:
    """Map each `### Requirement: <id>` to its capability (the dir name).

    Walks `<specs_dir>/<capability>/spec.md` files only. A capability dir
    may declare multiple requirements; all map to that capability.
    """
    namespace: dict[str, str] = {}
    for spec_path in sorted(Path(specs_dir).glob("*/spec.md")):
        capability = spec_path.parent.name
        for line in spec_path.read_text(encoding="utf-8").splitlines():
            match = _REQUIREMENT_STATUS_RE.match(line)
            if match:
                namespace[match.group(1)] = capability
    return namespace


def load_req_status(specs_dir: Path) -> dict[str, str]:
    """Map each `### Requirement: <id>` to its status: "active"|"deferred".

    Walks the SAME `<specs_dir>/<capability>/spec.md` files as
    `load_namespace`. A heading may carry an optional trailing
    `[active|deferred]` suffix; a bare heading defaults to "active".
    The status suffix is split off so the req id stays identical to
    `load_namespace`'s capture (e.g. "REQ-1", not "REQ-1 [deferred]").
    """
    status: dict[str, str] = {}
    for spec_path in sorted(Path(specs_dir).glob("*/spec.md")):
        for line in spec_path.read_text(encoding="utf-8").splitlines():
            match = _REQUIREMENT_STATUS_RE.match(line)
            if match:
                status[match.group(1)] = match.group(2) or "active"
    return status


def generate_index(
    tag_records: list[dict], namespace: dict[str, str]
) -> str:
    """Render a 3-level markdown tree: capability > requirement > test.

    For each record's each `@req`, resolve req->capability via
    `namespace` and place `- <test>` under `### <req>` under
    `## <capability>`. Reqs absent from `namespace` are excluded from
    the tree; coverage gaps and dangling tags are then collected into a
    trailing `## Orphans` section (see `_orphan_lines`). Ordering is
    deterministic: capabilities, then requirements, then tests are each
    sorted.
    """
    # tree: capability -> req -> set of test names
    tree: dict[str, dict[str, set[str]]] = {}
    for record in tag_records:
        test = record["test"]
        for req in record["reqs"]:
            capability = namespace.get(req)
            if capability is None:
                continue
            tree.setdefault(capability, {}).setdefault(req, set()).add(test)

    lines = ["# Living-spec index"]
    for capability in sorted(tree):
        lines.append("")
        lines.append(f"## {capability}")
        for req in sorted(tree[capability]):
            lines.append("")
            lines.append(f"### {req}")
            lines.append("")
            for test in sorted(tree[capability][req]):
                lines.append(f"- {test}")

    lines.extend(_orphan_lines(tag_records, namespace))
    return "\n".join(lines) + "\n"


def _orphan_lines(
    tag_records: list[dict], namespace: dict[str, str]
) -> list[str]:
    """Render the `## Orphans` section, or nothing if there are none.

    Two distinct orphan kinds, kept in separate line groups:
    - reqs in `namespace` linked by zero tests (a coverage gap), and
    - a record's `@req` absent from `namespace` (a dangling tag).
    Both groups are sorted for deterministic output.
    """
    linked_reqs = {req for record in tag_records for req in record["reqs"]}
    untested = sorted(req for req in namespace if req not in linked_reqs)
    dangling = sorted(req for req in linked_reqs if req not in namespace)

    if not untested and not dangling:
        return []

    lines = ["", "## Orphans"]
    if untested:
        lines.append("")
        lines.append("### reqs with no tests")
        lines.append("")
        for req in untested:
            lines.append(f"- {req}")
    if dangling:
        lines.append("")
        lines.append("### dangling @req (not in namespace)")
        lines.append("")
        for req in dangling:
            lines.append(f"- {req}")
    return lines
