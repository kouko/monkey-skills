#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Format lineage data as ASCII tree + Mermaid diagram for query output.

Two modes:

1. Column lineage (consumes recursive_column_lineage.py JSONL output):

       python3 format_lineage_diagram.py column \\
           --recursive-jsonl /tmp/dbt-wiki-recursive-lineage.jsonl \\
           --model model.example_project.fct_orders --column customer_id \\
           --direction both

2. Model lineage (consumes manifest.json directly, walks depends_on / feeds_into):

       python3 format_lineage_diagram.py model \\
           --manifest dbt/target/manifest.json \\
           --model model.example_project.fct_orders \\
           --direction both --max-depth 3

Output (stdout, JSON):
    {
        "ascii": "<ascii tree string>",
        "mermaid": "<mermaid graph LR string>",
        "node_count": <int>,
        "truncated": <bool>            # true if we hit max_node cap
    }

Pure stdlib — no third-party deps.

Why both formats:
- ASCII renders in any terminal / Claude Code chat output (immediate scan)
- Mermaid renders in IDE preview (Dataspell / VS Code / Cursor) and on
  GitHub / Obsidian when synthesis files are committed and viewed there

Truncation policy (avoid 1000-node Mermaid diagrams):
- max 30 nodes per diagram by default (configurable via --max-nodes)
- if exceeded, return a tier-aggregated graph (group leaves by tier path)
- ASCII tree always shows what was rendered; Mermaid is the visual extra
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ----- column lineage formatters -----


def load_recursive_record(jsonl_path: str, model_uid: str, column: str) -> dict | None:
    """Find the JSONL record matching (model_uid, column)."""
    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("model_uid") == model_uid and rec.get("column") == column:
                return rec
    return None


def short_uid(uid: str) -> str:
    """model.proj.fct_orders → fct_orders; source.proj.raw_data.orders → orders"""
    return uid.split(".")[-1] if "." in uid else uid


def parse_node_key(key: str) -> tuple[str, str]:
    """Split '<uid>::<col>' or '_unresolved::<table>::<col>' into (uid, col)."""
    parts = key.split("::")
    if len(parts) == 2:
        return parts[0], parts[1]
    elif len(parts) == 3 and parts[0] == "_unresolved":
        return f"_unresolved::{parts[1]}", parts[2]
    return key, ""


def render_column_ascii(
    rec: dict,
    direction: str = "both",
    indent: str = "",
) -> str:
    """ASCII tree for a single column lineage record."""
    out_lines: list[str] = []
    target = f"{short_uid(rec['model_uid'])}.{rec['column']}"
    out_lines.append(f"{target}")

    def walk(tree: dict, prefix: str = "  "):
        items = list(tree.items())
        for i, (key, sub) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└─ " if is_last else "├─ "
            uid, col = parse_node_key(key)
            label = f"{short_uid(uid)}.{col}"
            if uid.startswith("_cycle") or uid.startswith("_max"):
                label = f"... ({uid})"
            elif uid.startswith("source."):
                label = f"{label} *(source)*"
            elif uid.startswith("_unresolved"):
                label = f"{label} *(unresolved)*"
            out_lines.append(f"{prefix}{connector}{label}")
            if isinstance(sub, dict) and sub:
                next_prefix = prefix + ("   " if is_last else "│  ")
                walk(sub, next_prefix)

    if direction in ("ancestors", "both") and rec.get("ancestors"):
        out_lines.append("")
        out_lines.append("⬆ Ancestors (where this column comes from):")
        walk(rec["ancestors"])

    if direction in ("descendants", "both") and rec.get("descendants"):
        out_lines.append("")
        out_lines.append("⬇ Descendants (where this column flows to):")
        walk(rec["descendants"])

    return "\n".join(out_lines)


def render_column_mermaid(
    rec: dict,
    direction: str = "both",
    max_nodes: int = 30,
) -> tuple[str, int, bool]:
    """Mermaid graph LR for a column lineage record.

    Returns (mermaid_str, node_count, truncated_flag).
    """
    target_uid = rec["model_uid"]
    target_col = rec["column"]
    target_node_id = _node_id(target_uid, target_col)
    target_label = f"{short_uid(target_uid)}.{target_col}"

    nodes: dict[str, str] = {target_node_id: target_label}
    edges: list[tuple[str, str]] = []

    def walk(tree: dict, child_node_id: str, depth: int = 0):
        if depth > 8:  # safety
            return
        for key, sub in tree.items():
            uid, col = parse_node_key(key)
            if uid.startswith("_cycle") or uid.startswith("_max"):
                continue
            parent_node_id = _node_id(uid, col)
            label = f"{short_uid(uid)}.{col}"
            if uid.startswith("source."):
                label = f"{label} (src)"
            elif uid.startswith("_unresolved"):
                label = f"{label} (?)"
            nodes[parent_node_id] = label
            edges.append((parent_node_id, child_node_id))
            if len(nodes) >= max_nodes:
                return
            if isinstance(sub, dict) and sub:
                walk(sub, parent_node_id, depth + 1)

    def walk_descendants(tree: dict, parent_node_id: str, depth: int = 0):
        if depth > 8:
            return
        for key, sub in tree.items():
            uid, col = parse_node_key(key)
            if uid.startswith("_cycle") or uid.startswith("_max"):
                continue
            child_node_id = _node_id(uid, col)
            label = f"{short_uid(uid)}.{col}"
            if uid.startswith("_unresolved"):
                label = f"{label} (?)"
            nodes[child_node_id] = label
            edges.append((parent_node_id, child_node_id))
            if len(nodes) >= max_nodes:
                return
            if isinstance(sub, dict) and sub:
                walk_descendants(sub, child_node_id, depth + 1)

    if direction in ("ancestors", "both") and rec.get("ancestors"):
        walk(rec["ancestors"], target_node_id)

    if direction in ("descendants", "both") and rec.get("descendants"):
        walk_descendants(rec["descendants"], target_node_id)

    truncated = len(nodes) >= max_nodes
    lines = ["graph LR"]
    for nid, label in nodes.items():
        # Quote labels to handle special chars
        lines.append(f'  {nid}["{label}"]')
    # Dedupe edges + drop self-loops (rare but possible after node id collision)
    seen: set[tuple[str, str]] = set()
    for src, dst in edges:
        if src == dst or (src, dst) in seen:
            continue
        seen.add((src, dst))
        lines.append(f"  {src} --> {dst}")
    if truncated:
        lines.append(f'  truncated["⚠ truncated at {max_nodes} nodes; see ASCII tree for full"]')

    return "\n".join(lines), len(nodes), truncated


def _node_id(uid: str, col: str) -> str:
    """Convert uid+col to a Mermaid-safe node id.

    Long uid names get truncated, which used to cause distinct nodes to
    collide (and Mermaid drew nonsensical self-edges). We append a short
    hash suffix derived from the FULL uid+col so collisions are
    eliminated even after truncation.
    """
    import hashlib

    raw = f"{uid}__{col}"
    safe = "".join(c if c.isalnum() else "_" for c in raw)
    h = hashlib.md5(raw.encode()).hexdigest()[:6]
    # Truncate the human-readable part to 50, append _<hash> for uniqueness
    return "n_" + safe[:50] + "_" + h


# ----- model lineage formatters (no column granularity) -----


def render_model_lineage(
    manifest_path: str,
    model_uid: str,
    direction: str = "both",
    max_depth: int = 3,
    max_nodes: int = 30,
) -> tuple[str, str, int, bool]:
    """Model-level lineage from manifest. Returns (ascii, mermaid, count, truncated)."""
    manifest = json.loads(Path(manifest_path).read_text())
    nodes_dict = manifest.get("nodes", {})
    sources_dict = manifest.get("sources", {})

    # Build feeds_into from depends_on
    feeds_into: dict[str, list[str]] = {}
    for uid, node in nodes_dict.items():
        if node.get("resource_type") not in ("model", "snapshot"):
            continue
        for dep in node.get("depends_on", {}).get("nodes", []):
            feeds_into.setdefault(dep, []).append(uid)

    visited: set[str] = set()
    nodes: dict[str, str] = {}  # node_id → label
    edges: list[tuple[str, str]] = []

    def walk_up(uid: str, depth: int) -> None:
        if depth > max_depth or uid in visited or len(nodes) >= max_nodes:
            return
        visited.add(uid)
        nid = _node_id(uid, "")
        label = short_uid(uid)
        if uid.startswith("source."):
            label = f"{label} (src)"
        nodes[nid] = label
        node = nodes_dict.get(uid) or sources_dict.get(uid)
        if not node:
            return
        for dep in node.get("depends_on", {}).get("nodes", []):
            dep_nid = _node_id(dep, "")
            edges.append((dep_nid, nid))
            walk_up(dep, depth + 1)

    def walk_down(uid: str, depth: int) -> None:
        if depth > max_depth or len(nodes) >= max_nodes:
            return
        nid = _node_id(uid, "")
        node = nodes_dict.get(uid) or sources_dict.get(uid)
        if not node:
            return
        nodes.setdefault(nid, short_uid(uid))
        for child_uid in feeds_into.get(uid, []):
            child_nid = _node_id(child_uid, "")
            nodes.setdefault(child_nid, short_uid(child_uid))
            edges.append((nid, child_nid))
            walk_down(child_uid, depth + 1)

    if direction in ("ancestors", "both"):
        walk_up(model_uid, 0)
    if direction in ("descendants", "both"):
        # don't reset nodes — keep target node in
        walk_down(model_uid, 0)

    # ASCII tree (simple adjacency style for model-level)
    ascii_lines = [f"{short_uid(model_uid)}"]
    target_node = nodes_dict.get(model_uid) or sources_dict.get(model_uid)
    if direction in ("ancestors", "both") and target_node:
        deps = target_node.get("depends_on", {}).get("nodes", [])[:max_nodes]
        if deps:
            ascii_lines.append("⬆ depends on:")
            for d in deps:
                ascii_lines.append(f"  - {short_uid(d)}{' (src)' if d.startswith('source.') else ''}")
    if direction in ("descendants", "both"):
        children = feeds_into.get(model_uid, [])[:max_nodes]
        if children:
            ascii_lines.append("⬇ feeds into:")
            for c in children:
                ascii_lines.append(f"  - {short_uid(c)}")

    truncated = len(nodes) >= max_nodes

    mermaid_lines = ["graph LR"]
    for nid, label in nodes.items():
        mermaid_lines.append(f'  {nid}["{label}"]')
    # Dedupe edges
    seen_edges = set()
    for src, dst in edges:
        if (src, dst) in seen_edges:
            continue
        seen_edges.add((src, dst))
        mermaid_lines.append(f"  {src} --> {dst}")
    if truncated:
        mermaid_lines.append(f'  truncated["⚠ truncated at {max_nodes} nodes"]')

    return "\n".join(ascii_lines), "\n".join(mermaid_lines), len(nodes), truncated


# ----- CLI -----


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="mode", required=True)

    pc = sub.add_parser("column", help="Column-level lineage diagram")
    pc.add_argument("--recursive-jsonl", required=True)
    pc.add_argument("--model", required=True, help="model unique_id")
    pc.add_argument("--column", required=True)
    pc.add_argument("--direction", default="both", choices=["ancestors", "descendants", "both"])
    pc.add_argument("--max-nodes", type=int, default=30)

    pm = sub.add_parser("model", help="Model-level lineage diagram")
    pm.add_argument("--manifest", required=True)
    pm.add_argument("--model", required=True, help="model unique_id")
    pm.add_argument("--direction", default="both", choices=["ancestors", "descendants", "both"])
    pm.add_argument("--max-depth", type=int, default=3)
    pm.add_argument("--max-nodes", type=int, default=30)

    args = p.parse_args()

    if args.mode == "column":
        rec = load_recursive_record(args.recursive_jsonl, args.model, args.column)
        if rec is None:
            print(json.dumps({"_error": f"no record for {args.model} / {args.column}"}))
            return 1
        ascii_str = render_column_ascii(rec, args.direction)
        mermaid_str, count, truncated = render_column_mermaid(
            rec, args.direction, args.max_nodes
        )
        print(json.dumps({
            "ascii": ascii_str,
            "mermaid": mermaid_str,
            "node_count": count,
            "truncated": truncated,
        }, ensure_ascii=False, indent=2))
        return 0

    if args.mode == "model":
        ascii_str, mermaid_str, count, truncated = render_model_lineage(
            args.manifest, args.model, args.direction, args.max_depth, args.max_nodes
        )
        print(json.dumps({
            "ascii": ascii_str,
            "mermaid": mermaid_str,
            "node_count": count,
            "truncated": truncated,
        }, ensure_ascii=False, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
