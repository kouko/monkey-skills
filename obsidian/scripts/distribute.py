#!/usr/bin/env python3
"""Distribute the canonical language-policy.md from wiki-ingest into sibling
obsidian skills as functional copies.

Layout:

    canonical SSOT
      obsidian/skills/wiki-ingest/references/language-policy.md

    functional copies (sibling skills)
      obsidian/skills/<skill>/references/language-policy.md

Each functional copy is *(SSOT header)+(canonical bytes)*. The header
points back to the SSOT path and forbids in-place editing.
``obsidian/scripts/verify-drift.py`` (T2) regenerates the expected payload
and byte-diffs it against what is on disk; any mismatch fails the CI gate.

Pure stdlib (pathlib, sys, argparse). No network, no third-party deps.

Workflow
========
1. Land all edits in ``obsidian/skills/wiki-ingest/references/language-policy.md``.
2. In the same commit run ``python3 obsidian/scripts/distribute.py``.
3. ``obsidian/scripts/verify-drift.py`` runs in CI and fails on byte diff.

SSOT header line count: 4 lines (2 BEGIN comment lines + 1 blank line +
1 END comment line; canonical content is inserted between blank line and
END). Callers that strip the header before diffing should skip the first
4 lines plus the trailing END line. See HEADER_LINE_COUNT constant.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# obsidian/ — parent of scripts/
OBSIDIAN_ROOT = Path(__file__).resolve().parent.parent

# monkey-skills/ repo root
REPO_ROOT = OBSIDIAN_ROOT.parent

# Canonical SSOT
CANONICAL = (
    OBSIDIAN_ROOT
    / "skills"
    / "wiki-ingest"
    / "references"
    / "language-policy.md"
)

# Relative path of the canonical file (used in header text)
CANONICAL_REL = "obsidian/skills/wiki-ingest/references/language-policy.md"

# Marker identifiers — mirror code-toolkit BEGIN/END style
MARKER_ID = "language-policy-v1"
DISTRIBUTE_SCRIPT = "obsidian/scripts/distribute.py"

# SSOT header: 4 lines total
#   line 1: BEGIN comment
#   line 2: DO NOT EDIT comment
#   line 3: blank
#   line 4: END comment  (written after canonical content)
# HEADER_PREFIX_LINE_COUNT = lines before canonical content = 3 (lines 1-3)
# HEADER_SUFFIX_LINE_COUNT = lines after canonical content = 1 (line 4 END)
# Total header lines to skip when comparing content = 3 prefix + 1 suffix
HEADER_PREFIX_LINE_COUNT = 3
HEADER_SUFFIX_LINE_COUNT = 1

# Routing table: destinations (relative to obsidian/).
# Update in the SAME commit that adds or removes a consuming skill.
TARGETS: list[str] = [
    "skills/wiki-cross-linker/references/language-policy.md",
    "skills/wiki-query/references/language-policy.md",
    "skills/wiki-lint/references/language-policy.md",
    "skills/wiki-auto-research/references/language-policy.md",
]


def header_prefix() -> str:
    """Return the 3-line prefix written BEFORE canonical content."""
    return (
        f"<!-- BEGIN {MARKER_ID} — managed by {DISTRIBUTE_SCRIPT}"
        f" from {CANONICAL_REL} — do not edit in place -->\n"
        f"<!-- This is a functional copy."
        f" Edit the canonical source above and re-run distribute.py. -->\n"
        "\n"
    )


def header_suffix() -> str:
    """Return the 1-line suffix written AFTER canonical content."""
    return f"\n<!-- END {MARKER_ID} -->\n"


def expected_payload() -> bytes:
    """Return the byte content every functional copy MUST equal."""
    canonical_bytes = CANONICAL.read_bytes()
    prefix = header_prefix().encode("utf-8")
    suffix = header_suffix().encode("utf-8")
    return prefix + canonical_bytes + suffix


def distribute() -> int:
    """Write functional copies to all target paths. Returns files written.
    Creates ``references/`` subdirs as needed. Idempotent.
    """
    if not CANONICAL.is_file():
        raise FileNotFoundError(
            f"canonical missing: {CANONICAL.relative_to(REPO_ROOT)}"
        )
    payload = expected_payload()
    written = 0
    for rel_dst in TARGETS:
        dst = OBSIDIAN_ROOT / rel_dst
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(payload)
        written += 1
        print(f"[deploy] {CANONICAL_REL} -> obsidian/{rel_dst}")
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Distribute language-policy.md from wiki-ingest (canonical SSOT) "
            "into sibling obsidian skill references/ directories as functional "
            "copies. Idempotent — running twice produces identical output."
        )
    )
    # No positional args or flags needed for MVP; --help is auto-generated.
    parser.parse_args(argv)

    try:
        n = distribute()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print(f"\nOK: deployed {n} functional copies from {CANONICAL_REL}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
