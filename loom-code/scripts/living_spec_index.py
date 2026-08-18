"""Living-spec index generator.

`load_namespace(specs_dir)` builds the req-to-capability namespace from a
loom-design tree: each `<specs_dir>/<capability>/spec.md` declares its
requirements via `### Requirement: REQ-<n> — <name> [status]` headings
(name and status both optional), and the capability is the immediate
subdirectory name. Returns `{req_id: capability}`. A heading whose text
is not id-form (legacy prose, no `REQ-<n>`) is skipped — it is not a
namespace entry.

Stdlib only (pathlib + re).
"""

import re
from pathlib import Path

# The status vocabulary, declared ONCE — both regexes below are built
# from this single constant (f-string), so a vocabulary change can't
# miss a copy (closes the paired-regex lockstep debt item).
_STATUS_VOCAB = "active|deferred"

# An id-form requirement heading: `### Requirement: REQ-<n>` with an
# optional ` — <name>` and an optional trailing `[<status>]` suffix
# (status vocabulary: `_STATUS_VOCAB`). Named groups: id, name, status. A heading whose text
# is NOT id-form (legacy prose, e.g. `### Requirement: Some prose`)
# does not match this regex at all and is skipped by `load_namespace`
# and `load_req_status`.
_REQUIREMENT_STATUS_RE = re.compile(
    r"^###\s+Requirement:\s*(?P<id>REQ-\d+)(?:\s+—\s+(?P<name>.+?))?"
    rf"\s*(?:\[(?P<status>{_STATUS_VOCAB})\])?\s*$"
)

# A requirement heading (id-form OR legacy prose) that DOES carry a
# trailing `[...]` bracket, capturing the text before the bracket
# (group "id") and the raw bracket content (group "status") regardless
# of whether it is a valid status. This is the fail-loud counterpart to
# `_REQUIREMENT_STATUS_RE`: that regex only matches a valid/absent
# suffix on an id-form heading, so it cannot SEE a typo'd status, nor a
# bracket on a prose heading. This one always matches any heading with
# a bracket — id-form or prose alike — letting the caller flag any
# content that is not in `_STATUS_VOCAB`.
_REQUIREMENT_BRACKET_RE = re.compile(
    r"^###\s+Requirement:\s*(?P<id>.+?)\s*\[(?P<status>[^\]]*)\]\s*$"
)


def load_namespace(specs_dir: Path) -> dict[str, str]:
    """Map each id-form `### Requirement: REQ-<n>` to its capability.

    Walks `<specs_dir>/<capability>/spec.md` files only. A capability dir
    may declare multiple requirements; all map to that capability. A
    prose heading (no `REQ-<n>` id) is legacy and skipped.
    """
    namespace: dict[str, str] = {}
    for spec_path in sorted(Path(specs_dir).glob("*/spec.md")):
        capability = spec_path.parent.name
        for line in spec_path.read_text(encoding="utf-8").splitlines():
            match = _REQUIREMENT_STATUS_RE.match(line)
            if match:
                namespace[match.group("id")] = capability
    return namespace


def load_req_status(specs_dir: Path) -> dict[str, str]:
    """Map each id-form `### Requirement: REQ-<n>` to its status.

    Walks the SAME `<specs_dir>/<capability>/spec.md` files as
    `load_namespace`. A heading may carry an optional trailing
    `[<status>]` suffix (see `_STATUS_VOCAB`); a bare heading defaults
    to "active". A
    prose heading (no `REQ-<n>` id) is legacy and skipped. The status
    suffix is split off so the req id stays identical to
    `load_namespace`'s capture (e.g. "REQ-1", not "REQ-1 [deferred]").
    """
    status: dict[str, str] = {}
    for spec_path in sorted(Path(specs_dir).glob("*/spec.md")):
        for line in spec_path.read_text(encoding="utf-8").splitlines():
            match = _REQUIREMENT_STATUS_RE.match(line)
            if match:
                status[match.group("id")] = match.group("status") or "active"
    return status


def load_req_paths(specs_dir: Path) -> dict[str, list[Path]]:
    """Map each id-form `### Requirement: REQ-<n>` to EVERY declaring path.

    Walks the SAME `<specs_dir>/<capability>/spec.md` files as
    `load_namespace`. Unlike `load_namespace` (a dict merge where the
    last declaration wins), this collects every declaring `spec.md`
    path per id — ONE ENTRY PER DECLARING LINE, repeats included — so a
    duplicate declaration stays visible instead of being silently
    overwritten OR silently deduped within a file. The caller
    (`find_duplicate_req_declarations`) is what turns a repeated same
    path into a same-file-duplicate violation; deduping here would hide
    that case entirely. A prose heading (no `REQ-<n>` id) is legacy and
    skipped.
    """
    paths: dict[str, list[Path]] = {}
    for spec_path in sorted(Path(specs_dir).glob("*/spec.md")):
        for line in spec_path.read_text(encoding="utf-8").splitlines():
            match = _REQUIREMENT_STATUS_RE.match(line)
            if match:
                req_id = match.group("id")
                paths.setdefault(req_id, []).append(spec_path)
    for req_id in paths:
        paths[req_id].sort()
    return paths


def find_malformed_status(specs_dir: Path) -> list[str]:
    """Flag `### Requirement:` headings with an invalid `[...]` status.

    Walks the SAME `<specs_dir>/<capability>/spec.md` files as
    `load_namespace`/`load_req_status`. A heading whose trailing bracket
    content is neither "active" nor "deferred" (e.g. `[activ]`,
    `[todo]`, `[ ]`) is a MALFORMED declaration that `load_req_status`
    would silently default to "active"; this surfaces it instead. The
    suffix grammar applies to BOTH id-form and legacy-prose headings —
    a prose heading with an invalid bracket is flagged too, even though
    it is otherwise skipped (it is not a namespace entry). Returns one
    descriptive string per offender naming the bracket content and the
    id-portion. A heading with no bracket, or a valid `[active]`/
    `[deferred]`, yields nothing. Source order, deterministic.
    """
    valid_statuses = _STATUS_VOCAB.split("|")
    offenders: list[str] = []
    for spec_path in sorted(Path(specs_dir).glob("*/spec.md")):
        for line in spec_path.read_text(encoding="utf-8").splitlines():
            match = _REQUIREMENT_BRACKET_RE.match(line)
            if match and match.group("status") not in valid_statuses:
                offenders.append(
                    f"MALFORMED status '[{match.group('status')}]' on "
                    f"requirement {match.group('id')}"
                )
    return offenders


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
