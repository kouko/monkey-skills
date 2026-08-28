#!/usr/bin/env python3
"""The Decisions-so-far link gate for a decision-map store.

Grammar SSOT: `loom-workflow/skills/decision-map/references/
map-format.md` §MAP.md schema (Decisions-so-far bullet) and §Command
surface. This script never re-parses MAP.md/ticket bytes itself — it
imports `map_store` (the sole sanctioned parser) for every read.

Every Decisions-so-far line must link an existing ticket file, under
the map's `tickets/`, whose frontmatter `status` is `closed`. A
dangling link or a link to a non-closed ticket is a violation.

CLI: `check_map_links.py <map-dir> --repo-root <path>` — bare
positional shape, no verb (map-format.md §Command surface: only
`map_store.py` carries a subcommand). Exit 0 clean / 1 operational
error / 2 violation, per §Command surface's shared exit-code split.

Stdlib only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import map_store


def check_links(map_dir: Path) -> tuple[int, str]:
    """Check every Decisions-so-far line in `<map_dir>/MAP.md` links an
    existing, closed ticket. Returns `(exit_code, message)`: 0 clean,
    1 operational error, 2 a violation naming the offending line."""
    map_dir = Path(map_dir)
    if not map_dir.is_dir():
        return 1, f"map directory not found: {map_dir}"

    try:
        doc = map_store.read_map(map_dir)
    except map_store.MapStoreError as exc:
        return 1, str(exc)
    except map_store.SchemaViolation as exc:
        return 2, str(exc)

    if doc.frontmatter.schema_version > map_store.SUPPORTED_SCHEMA_VERSION:
        return 2, (
            f"{map_dir / 'MAP.md'}: schema_version "
            f"{doc.frontmatter.schema_version} is newer than the "
            f"supported ceiling {map_store.SUPPORTED_SCHEMA_VERSION} — "
            "refusing to read further"
        )

    for decision in doc.decisions:
        ticket_path = map_dir / decision.ticket_link
        if not ticket_path.is_file():
            return 2, (
                f"Decisions-so-far line {decision.gist!r} links a "
                f"non-existent ticket: {decision.ticket_link}"
            )
        try:
            ticket = map_store.read_ticket(ticket_path)
        except map_store.MapStoreError as exc:
            return 1, str(exc)
        except map_store.SchemaViolation as exc:
            return 2, str(exc)
        if ticket.frontmatter.status != "closed":
            return 2, (
                f"Decisions-so-far line {decision.gist!r} links ticket "
                f"{decision.ticket_link} whose status is "
                f"{ticket.frontmatter.status!r}, not 'closed'"
            )

    return 0, f"{map_dir} — all Decisions-so-far links resolve to closed tickets"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify every Decisions-so-far line links an "
        "existing, closed ticket."
    )
    parser.add_argument("target", help="path to the map directory")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="repo root (default: git rev-parse --show-toplevel of the "
        "target's directory, falling back to cwd)",
    )
    args = parser.parse_args(argv)

    target = Path(args.target)
    # repo-root is accepted per the canonical arg shape (map-format.md
    # §Command surface) but this checker resolves ticket links relative
    # to the map directory itself, not the repo root.
    map_store.resolve_repo_root(
        args.repo_root, target if target.is_dir() else target.parent
    )

    code, message = check_links(target)
    if code == 0:
        print(message)
    else:
        print(f"Error: {message}", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
