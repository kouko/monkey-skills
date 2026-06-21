#!/usr/bin/env python3
"""Sync the Codex plugin manifest's SHARED fields from the Claude SSOT.

The Claude manifest (`loom-code/.claude-plugin/plugin.json`) is the single
source of truth for the shared plugin metadata. The Codex manifest
(`loom-code/.codex-plugin/plugin.json`) derives those same fields but adds a
Codex-only ``interface`` block. This script copies the shared fields into the
Codex manifest in lock-step while preserving ``interface`` (and any other
Codex-only key) verbatim.

Usage:
    python3 loom-code/scripts/sync_codex_manifest.py
        Rewrite the Codex manifest's shared fields from the Claude SSOT.

    python3 loom-code/scripts/sync_codex_manifest.py --check
        Pure read. Exit 0 if the manifests are in sync, non-zero on
        divergence. Used as a CI drift gate.

Stdlib only (json). String equality for the version comparison — no
third-party ``packaging``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Fields the Codex manifest derives from the Claude SSOT, in lock-step.
SHARED_FIELDS = (
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
)

ROOT = Path(__file__).resolve().parent.parent  # loom-code/
DEFAULT_SOURCE = ROOT / ".claude-plugin" / "plugin.json"
DEFAULT_TARGET = ROOT / ".codex-plugin" / "plugin.json"


def sync_shared_fields(source: dict, target: dict) -> dict:
    """Return a new target dict with SHARED_FIELDS copied from ``source``.

    Codex-only keys on ``target`` (e.g. ``interface``) are preserved verbatim.
    Key ordering of ``target`` is preserved so the diff stays minimal.
    """
    result = dict(target)
    for field in SHARED_FIELDS:
        if field in source:
            result[field] = source[field]
    return result


def manifests_synced(source: dict, target: dict) -> bool:
    """True iff every shared field on ``target`` already matches ``source``."""
    return sync_shared_fields(source, target) == target


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(path: Path, data: dict) -> None:
    # 2-space indent + trailing newline to match the existing manifest style.
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="pure read; exit non-zero on divergence (CI drift gate)",
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args(argv)

    source = _load(args.source)
    target = _load(args.target)

    if args.check:
        if manifests_synced(source, target):
            return 0
        print(
            f"DRIFT: {args.target} shared fields diverge from {args.source}. "
            f"Run: python3 {Path(__file__).name}",
            file=sys.stderr,
        )
        return 1

    synced = sync_shared_fields(source, target)
    if synced != target:
        _dump(args.target, synced)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
