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
