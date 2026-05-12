#!/usr/bin/env python3
"""Distribute scripts/canonical/* to each routed skill assets/ as byte-identical
functional copies.

SSOT-and-functional-copy pattern (mirror of translation-toolkit/scripts/):
  scripts/canonical/<file>          -> single source of truth (only editable
                                       location)
  skills/<skill>/<subfolder>/<file> -> byte-identical functional copy
                                       (Edit forbidden; CI verifies)

Workflow:
  1. Edit a file under scripts/canonical/.
  2. Run `python3 legal-toolkit/scripts/distribute.py` from the repo root.
  3. Commit canonical edit + functional-copy updates in the same commit.

CI runs verify-drift.py to enforce byte-identical copies.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_DIR = ROOT / "scripts" / "canonical"

# Routing table — reflects CURRENT state. Update in the same commit that
# creates the new consuming skill. No auto-skip.
ROUTE: dict[str, list[str]] = {
    "legal-sources.json": [
        "skills/legal-contract-review/assets/legal-sources.json",
    ],
}

# Filesystem noise to skip — never authored files.
IGNORED_NAMES = {".DS_Store", ".gitkeep"}


def iter_canonical_files(canonical_dir: Path = CANONICAL_DIR) -> list[tuple[str, Path]]:
    """Yield (relative_posix_name, absolute_path) for every file under
    canonical_dir, sorted for deterministic output.

    Filters out macOS Finder droppings, empty-dir markers, AppleDouble files,
    and Python bytecode caches.
    """
    out: list[tuple[str, Path]] = []
    for p in sorted(canonical_dir.rglob("*")):
        if not p.is_file():
            continue
        if p.name in IGNORED_NAMES or p.name.startswith("._"):
            continue
        if "__pycache__" in p.parts:
            continue
        rel = p.relative_to(canonical_dir).as_posix()
        out.append((rel, p))
    return out


def distribute(
    route: dict[str, list[str]] | None = None,
    root: Path | None = None,
) -> int:
    """Copy each canonical file to its routed destinations.

    Args:
      route: routing table; defaults to module-level ROUTE.
      root:  plugin root path; defaults to module-level ROOT.

    Returns:
      Number of byte-identical copies written. Creates parent dirs as needed.
      Raises FileNotFoundError if a canonical file declared in ROUTE is absent.
    """
    if route is None:
        route = ROUTE
    if root is None:
        root = ROOT
    canonical_dir = root / "scripts" / "canonical"

    written = 0
    for canonical_name, destinations in route.items():
        src = canonical_dir / canonical_name
        if not src.is_file():
            raise FileNotFoundError(
                f"canonical source missing: {src.relative_to(root)}"
            )
        for rel_dst in destinations:
            dst = root / rel_dst
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            written += 1
            print(f"[deploy] canonical/{canonical_name} -> {rel_dst}")
    return written
