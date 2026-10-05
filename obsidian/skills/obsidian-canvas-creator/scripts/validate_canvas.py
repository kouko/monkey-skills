#!/usr/bin/env python3
"""Validate Obsidian .canvas files (JSON Canvas 1.0). Stdlib only.

Checks:
- JSON parses into an object with optional ``nodes`` / ``edges`` arrays.
- Every ``id`` (nodes and edges) is unique and a 16-character lowercase
  hex string.
- Every edge ``fromNode`` / ``toNode`` references an existing node id.
- Required fields: ``type``, ``x``, ``y``, ``width``, ``height`` on every
  node; ``text`` on ``type: text``, ``file`` on ``type: file``,
  ``url`` on ``type: link``.
- Axis-aligned bounding-box overlap (positive intersection area) between
  two non-group nodes. Group nodes are containers and are excluded from
  overlap checks (children inside a group are expected).

The 320/200 px spacing guidance is advisory and intentionally NOT checked.

Exit status: 0 when every file is clean, 1 when any file has a violation
or cannot be read. Each violation is printed with the file name, the
node/edge id where available, and a short reason.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"[0-9a-f]{16}")

# Extra required field per node type; group nodes require none beyond the
# common fields. Unknown types only get the common-field checks.
NODE_TYPE_FIELD = {"text": "text", "file": "file", "link": "url"}
COMMON_FIELDS = ("type", "x", "y", "width", "height")


def _node_label(node, index: int) -> str:
    if isinstance(node, dict):
        node_id = node.get("id")
        if isinstance(node_id, str):
            return f'node "{node_id}"'
    return f"node #{index}"


def _edge_label(edge, index: int) -> str:
    if isinstance(edge, dict):
        edge_id = edge.get("id")
        if isinstance(edge_id, str):
            return f'edge "{edge_id}"'
    return f"edge #{index}"


def _intersects(x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
    """True when two axis-aligned boxes overlap with positive area."""
    return x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1


def validate_canvas_text(filename: str, text: str) -> list[str]:
    """Return one violation message per problem, empty list when clean."""
    violations: list[str] = []
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"{filename}: invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return [f"{filename}: top level is not an object"]

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if not isinstance(nodes, list):
        violations.append(f"{filename}: nodes is not an array")
        nodes = []
    if not isinstance(edges, list):
        violations.append(f"{filename}: edges is not an array")
        edges = []

    seen_ids: set[str] = set()
    node_ids: set[str] = set()

    for index, node in enumerate(nodes):
        label = _node_label(node, index)
        if not isinstance(node, dict):
            violations.append(f"{filename}: node #{index}: not an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str):
            violations.append(f"{filename}: {label}: id must be a string")
        elif not ID_RE.fullmatch(node_id):
            violations.append(
                f"{filename}: {label}: invalid id (want 16 lowercase hex chars)"
            )
        elif node_id in seen_ids:
            violations.append(f"{filename}: {label}: duplicate id")
        else:
            seen_ids.add(node_id)
            node_ids.add(node_id)
        for field in COMMON_FIELDS:
            if field not in node:
                violations.append(
                    f'{filename}: {label}: missing required field "{field}"'
                )
        node_type = node.get("type")
        if isinstance(node_type, str) and node_type in NODE_TYPE_FIELD:
            field = NODE_TYPE_FIELD[node_type]
            if field not in node:
                violations.append(
                    f'{filename}: {label}: missing required field "{field}" '
                    f'for type "{node_type}"'
                )

    for index, edge in enumerate(edges):
        label = _edge_label(edge, index)
        if not isinstance(edge, dict):
            violations.append(f"{filename}: edge #{index}: not an object")
            continue
        edge_id = edge.get("id")
        if not isinstance(edge_id, str):
            violations.append(f"{filename}: {label}: id must be a string")
        elif not ID_RE.fullmatch(edge_id):
            violations.append(
                f"{filename}: {label}: invalid id (want 16 lowercase hex chars)"
            )
        elif edge_id in seen_ids:
            violations.append(f"{filename}: {label}: duplicate id")
        else:
            seen_ids.add(edge_id)
        for ref_name in ("fromNode", "toNode"):
            ref = edge.get(ref_name)
            if not isinstance(ref, str):
                violations.append(f"{filename}: {label}: missing {ref_name}")
            elif ref not in node_ids:
                violations.append(
                    f'{filename}: {label}: {ref_name} "{ref}" references '
                    "missing node"
                )

    # Overlap: only non-group nodes with numeric geometry participate.
    positioned: list[tuple[str, float, float, float, float]] = []
    for index, node in enumerate(nodes):
        if not isinstance(node, dict) or node.get("type") == "group":
            continue
        x, y, width, height = (
            node.get("x"),
            node.get("y"),
            node.get("width"),
            node.get("height"),
        )
        if all(isinstance(value, (int, float)) for value in (x, y, width, height)):
            positioned.append(
                (_node_label(node, index), x, y, width, height)
            )

    for i in range(len(positioned)):
        label1, x1, y1, w1, h1 = positioned[i]
        for j in range(i + 1, len(positioned)):
            label2, x2, y2, w2, h2 = positioned[j]
            if _intersects(x1, y1, w1, h1, x2, y2, w2, h2):
                violations.append(f"{filename}: {label1} overlaps {label2}")

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Obsidian .canvas files (JSON Canvas 1.0). "
            "Exits 0 when every file is clean, 1 otherwise."
        )
    )
    parser.add_argument(
        "files", nargs="+", metavar="FILE", help=".canvas file(s) to validate"
    )
    args = parser.parse_args(argv)

    failed = False
    for path in args.files:
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"{path}: cannot read: {exc}", file=sys.stderr)
            failed = True
            continue
        violations = validate_canvas_text(path, text)
        for violation in violations:
            print(violation)
        if violations:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
