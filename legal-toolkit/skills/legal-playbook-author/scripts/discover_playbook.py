#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""discover_playbook — locate the user's legal-playbook/ folder.

Discovery order (deterministic, first match wins):

  1. <cwd>/legal-playbook/
  2. <ancestors>/legal-playbook/   (walk 5 levels up)
  3. BFS depth-5 from <cwd>/        (catch nested project layouts)
  4. None — fall back to bundled baseline (caller decides)

This script is the single source of truth for playbook location.
`legal-contract-review` uses it at session start; `legal-playbook-
author` uses it at mode-detection time.

Output: JSON to stdout with discovered path + index of clause_id
files found. Exits 0 on success even when no playbook is found
(stdout: { "found": false, ... }).

Usage:
    discover_playbook.py [--cwd <dir>] [--max-ancestors N] [--bfs-depth N]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path


DEFAULT_MAX_ANCESTORS = 5
DEFAULT_BFS_DEPTH = 5
TARGET_DIR_NAME = "legal-playbook"


def _index_clauses(playbook_dir: Path) -> list[dict]:
    """Walk the discovered legal-playbook/ folder and produce a clause index.

    Each entry: { clause_id, layout: flat|variant-folder, path, variants?: [...] }.
    Only descends one level past `legal-playbook/` (variant folders are
    expected to be flat themselves; nested-folder pathologies are caught
    by detect_conflicts.py, not here).
    """
    index: list[dict] = []
    if not playbook_dir.is_dir():
        return index
    for entry in sorted(playbook_dir.iterdir()):
        # Hidden files / README seed / status notes — skip
        if entry.name.startswith(".") or entry.name in {"README.md", ".skipped"}:
            continue
        # Flat clause: a single .md file
        if entry.is_file() and entry.suffix == ".md":
            index.append(
                {
                    "clause_id": entry.stem,
                    "layout": "flat",
                    "path": str(entry),
                }
            )
            continue
        # Variant-folder: a directory containing _clause.md + <variant>.md
        if entry.is_dir():
            clause_md = entry / "_clause.md"
            if not clause_md.is_file():
                continue  # not a recognised variant-folder; ignore
            variants = []
            for vf in sorted(entry.iterdir()):
                if vf.is_file() and vf.suffix == ".md" and vf.name != "_clause.md":
                    variants.append({"variant_id": vf.stem, "path": str(vf)})
            index.append(
                {
                    "clause_id": entry.name,
                    "layout": "variant-folder",
                    "path": str(entry),
                    "container": str(clause_md),
                    "variants": variants,
                }
            )
    return index


def _ancestors(start: Path, limit: int) -> list[Path]:
    out = []
    current = start
    for _ in range(limit):
        parent = current.parent
        if parent == current:
            break
        out.append(parent)
        current = parent
    return out


def _bfs_search(start: Path, max_depth: int) -> Path | None:
    """Bounded BFS looking for `legal-playbook/` under start."""
    if not start.is_dir():
        return None
    q: deque[tuple[Path, int]] = deque([(start, 0)])
    visited: set[Path] = set()
    while q:
        d, depth = q.popleft()
        if d in visited or depth > max_depth:
            continue
        visited.add(d)
        # Skip dot-dirs / common cache trees
        if d.name.startswith(".") or d.name in {"node_modules", "__pycache__", "venv", ".venv", "dist", "build"}:
            continue
        for child in d.iterdir():
            if not child.is_dir():
                continue
            if child.name == TARGET_DIR_NAME:
                return child
            q.append((child, depth + 1))
    return None


def discover(
    cwd: Path,
    max_ancestors: int = DEFAULT_MAX_ANCESTORS,
    bfs_depth: int = DEFAULT_BFS_DEPTH,
) -> dict:
    """Return a discovery report: { found, source, path, index, search_log }."""
    log: list[str] = []

    # Step 1 — direct cwd
    direct = cwd / TARGET_DIR_NAME
    log.append(f"checked: {direct} ({'hit' if direct.is_dir() else 'miss'})")
    if direct.is_dir():
        return {
            "found": True,
            "source": "cwd",
            "path": str(direct),
            "index": _index_clauses(direct),
            "search_log": log,
        }

    # Step 2 — ancestors
    for anc in _ancestors(cwd, max_ancestors):
        candidate = anc / TARGET_DIR_NAME
        log.append(f"checked: {candidate} ({'hit' if candidate.is_dir() else 'miss'})")
        if candidate.is_dir():
            return {
                "found": True,
                "source": "ancestor",
                "path": str(candidate),
                "index": _index_clauses(candidate),
                "search_log": log,
            }

    # Step 3 — BFS under cwd
    log.append(f"bfs from: {cwd} (depth {bfs_depth})")
    hit = _bfs_search(cwd, bfs_depth)
    if hit is not None:
        log.append(f"bfs hit: {hit}")
        return {
            "found": True,
            "source": "bfs",
            "path": str(hit),
            "index": _index_clauses(hit),
            "search_log": log,
        }

    log.append("bfs exhausted, no hit")
    return {
        "found": False,
        "source": None,
        "path": None,
        "index": [],
        "search_log": log,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cwd", default=".", help="working directory to search from")
    parser.add_argument(
        "--max-ancestors",
        type=int,
        default=DEFAULT_MAX_ANCESTORS,
        help=f"how many parent dirs to climb (default: {DEFAULT_MAX_ANCESTORS})",
    )
    parser.add_argument(
        "--bfs-depth",
        type=int,
        default=DEFAULT_BFS_DEPTH,
        help=f"BFS depth limit when scanning under cwd (default: {DEFAULT_BFS_DEPTH})",
    )
    args = parser.parse_args()
    report = discover(
        Path(args.cwd).resolve(),
        max_ancestors=args.max_ancestors,
        bfs_depth=args.bfs_depth,
    )
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
