"""Living-spec index generator.

`load_namespace(specs_dir)` builds the req-to-capability namespace from a
loom-spec tree: each `<specs_dir>/<capability>/spec.md` declares its
requirements via `### Requirement: <id>` headings, and the capability is
the immediate subdirectory name. Returns `{req_id: capability}`.

Stdlib only (pathlib + re).
"""

import re
from pathlib import Path

# A requirement heading: `### Requirement: <id>` (id = trailing text, stripped).
_REQUIREMENT_RE = re.compile(r"^###\s+Requirement:\s*(.+?)\s*$")


def load_namespace(specs_dir: Path) -> dict[str, str]:
    """Map each `### Requirement: <id>` to its capability (the dir name).

    Walks `<specs_dir>/<capability>/spec.md` files only. A capability dir
    may declare multiple requirements; all map to that capability.
    """
    namespace: dict[str, str] = {}
    for spec_path in sorted(Path(specs_dir).glob("*/spec.md")):
        capability = spec_path.parent.name
        for line in spec_path.read_text(encoding="utf-8").splitlines():
            match = _REQUIREMENT_RE.match(line)
            if match:
                namespace[match.group(1)] = capability
    return namespace


def generate_index(
    tag_records: list[dict], namespace: dict[str, str]
) -> str:
    """Render a 3-level markdown tree: capability > requirement > test.

    For each record's each `@req`, resolve req->capability via
    `namespace` and place `- <test>` under `### <req>` under
    `## <capability>`. Reqs absent from `namespace` are skipped here
    (orphan handling is a separate concern). Ordering is deterministic:
    capabilities, then requirements, then tests are each sorted.
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
    return "\n".join(lines) + "\n"
