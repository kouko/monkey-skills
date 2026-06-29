#!/usr/bin/env python3
"""Repo-level Codex manifest sync engine — sync a plugin's Codex manifest from
its Claude SSOT.

For a given plugin directory, the Claude manifest
(``<plugin>/.claude-plugin/plugin.json``) is the single source of truth for the
shared plugin metadata. The Codex manifest
(``<plugin>/.codex-plugin/plugin.json``) derives those same fields but adds a
Codex-only ``interface`` block. This engine copies the shared fields into the
Codex manifest in lock-step while preserving ``interface`` (and any other
Codex-only key) verbatim.

Unlike ``loom-code/scripts/sync_codex_manifest.py`` (self-locating to its own
parent plugin), this engine is REPO-LEVEL: the plugin to sync is passed in as a
directory name or path. The public surface (``sync_plugin`` + a CLI taking a
plugin arg) is shaped so a later task can add ``--scaffold``, an eligible-plugin
list, and ``--all`` without reworking it.

Usage:
    python3 scripts/sync_codex_manifests.py <plugin>
        Rewrite <plugin>'s Codex manifest shared fields from its Claude SSOT.

    python3 scripts/sync_codex_manifests.py --check <plugin>
        Pure read. Exit 0 if the manifests are in sync, non-zero on
        divergence. Used as a CI drift gate.

Stdlib only (json/pathlib/argparse). String equality for the version comparison
— no third-party ``packaging``.
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

CLAUDE_MANIFEST = (".claude-plugin", "plugin.json")
CODEX_MANIFEST = (".codex-plugin", "plugin.json")


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


def claude_manifest_path(plugin_dir: Path) -> Path:
    return plugin_dir.joinpath(*CLAUDE_MANIFEST)


def codex_manifest_path(plugin_dir: Path) -> Path:
    return plugin_dir.joinpath(*CODEX_MANIFEST)


def sync_plugin(plugin_dir, check: bool = False) -> bool:
    """Sync one plugin's Codex manifest shared fields from its Claude SSOT.

    ``plugin_dir`` is a directory name or path containing ``.claude-plugin`` and
    ``.codex-plugin`` subdirs. Returns whether the Codex manifest is in sync:

    - ``check=True``  — pure read; return True iff already synced (no mutation).
    - ``check=False`` — rewrite the Codex manifest when it diverges, then
      return True (in sync after the write).
    """
    plugin_dir = Path(plugin_dir)
    source = _load(claude_manifest_path(plugin_dir))
    target_path = codex_manifest_path(plugin_dir)
    target = _load(target_path)

    if check:
        return manifests_synced(source, target)

    synced = sync_shared_fields(source, target)
    if synced != target:
        _dump(target_path, synced)
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin", type=Path, help="plugin directory (name or path)")
    parser.add_argument(
        "--check",
        action="store_true",
        help="pure read; exit non-zero on divergence (CI drift gate)",
    )
    args = parser.parse_args(argv)

    if args.check:
        if sync_plugin(args.plugin, check=True):
            return 0
        print(
            f"DRIFT: {codex_manifest_path(args.plugin)} shared fields diverge "
            f"from {claude_manifest_path(args.plugin)}. "
            f"Run: python3 {Path(__file__).name} {args.plugin}",
            file=sys.stderr,
        )
        return 1

    sync_plugin(args.plugin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
