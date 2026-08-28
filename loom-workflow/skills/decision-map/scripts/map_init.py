#!/usr/bin/env python3
"""Scaffold a new decision-map store: `docs/loom/maps/<map-id>/`.

Grammar SSOT: `loom-workflow/skills/decision-map/references/
map-format.md` §MAP.md schema, §Command surface. Writes a
schema-conformant, empty MAP.md (the six pinned sections in order,
`state: charting`) plus an empty `tickets/` directory — the sanctioned
replacement for hand-copying an existing map as a template.

CLI: `map_init.py <map-id> --repo-root <path>` — bare positional shape,
no subcommand verb (map-format.md §Command surface: map_init.py is one
of the four scripts with no verb, unlike map_store.py's `validate`).
Exit 0 clean / 1 operational error (refuses — the map dir already
exists, precedent: loom-code/scripts/loom_init.py) / 2 a bad `map-id`
argument.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import map_store

_MAP_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

MAP_MD_TEMPLATE = """---
map-id: {map_id}
schema_version: 1
state: charting
---

## Destination

TODO: what this map is charting toward.

## Notes

## Decisions-so-far

## Not-yet-specified (fog)

## Out-of-scope

## Parts

| Part | Join key | Status |
|---|---|---|
"""


def init_map(map_id: str, repo_root: Path) -> int:
    """Scaffold `<repo_root>/docs/loom/maps/<map_id>/`. Returns the
    §Command surface exit code: 0 clean, 1 the map dir already exists
    (operational refusal), 2 a malformed `map_id`."""
    if not _MAP_ID_RE.fullmatch(map_id):
        print(
            f"map-init: refusing — {map_id!r} is not a valid map-id "
            "(lowercase letters, digits, hyphens; must start with a "
            "letter or digit)",
            file=sys.stderr,
        )
        return 2

    map_dir = Path(repo_root) / "docs" / "loom" / "maps" / map_id
    if map_dir.exists():
        print(
            f"map-init: refusing — {map_dir} already exists; map_init.py "
            "never overwrites a map store"
        )
        return 1

    tickets_dir = map_dir / "tickets"
    tickets_dir.mkdir(parents=True)
    (tickets_dir / ".gitkeep").write_text("", encoding="utf-8")
    (map_dir / "MAP.md").write_text(
        MAP_MD_TEMPLATE.format(map_id=map_id), encoding="utf-8"
    )
    print(f"map-init: scaffolded {map_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new decision-map store (MAP.md + empty tickets/)."
    )
    parser.add_argument("map_id", help="the new map's stable slug")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="repo root (default: git rev-parse --show-toplevel of cwd, "
        "falling back to cwd)",
    )
    args = parser.parse_args(argv)
    repo_root = map_store.resolve_repo_root(args.repo_root, Path.cwd())
    return init_map(args.map_id, repo_root=repo_root)


if __name__ == "__main__":
    sys.exit(main())
