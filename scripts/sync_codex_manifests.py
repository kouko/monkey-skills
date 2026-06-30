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

# Plugins whose Codex manifest is in scope for sync/scaffold: the 21 Batch-A
# plugins plus loom-code (which shipped its Codex manifest first). Deliberately
# EXCLUDES dev-workflow, collab-toolkit, salesforce-toolkit (hook/MCP-only
# plugins with no Codex interface surface to maintain).
CODEX_ELIGIBLE = (
    "ascii-graph-toolkit",
    "briefing-toolkit",
    "copywriting-toolkit",
    "dbt-wiki",
    "deconstruct-toolkit",
    "domain-teams",
    "four-dx-coach",
    "gws-toolkit",
    "investing-toolkit",
    "legal-toolkit",
    "loom-interface-design",
    "loom-product-principles",
    "loom-spec",
    "obsidian",
    "philosophers-toolkit",
    "repo-wiki",
    "research-toolkit",
    "skill-dev-toolkit",
    "systems-thinking-toolkit",
    "translation-toolkit",
    "tsundoku",
    "loom-code",
)


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


def _derive_interface(source: dict) -> dict:
    """Build a fresh Codex ``interface`` block from the Claude SSOT.

    Mechanically-derivable fields are filled from ``source``; judgment fields
    Phase 2 must author by hand are seeded with the literal string ``"TODO"``.
    Key set + order mirror loom-code/.codex-plugin/plugin.json (the schema
    template). ``author`` may be a ``{"name", "url"}`` dict or a bare string.
    """
    name = source.get("name", "")
    author = source.get("author")
    developer = author.get("name", "") if isinstance(author, dict) else (author or "")
    repository = source.get("repository", "")
    homepage = source.get("homepage", "")
    # websiteURL fallback chain: a repository derives the canonical GitHub subdir
    # URL; absent that, the homepage IS already that tree URL; the bare name is a
    # last resort only when neither URL is present.
    if repository and name:
        website = f"{repository}/tree/main/{name}"
    elif homepage:
        website = homepage
    else:
        website = repository or name
    return {
        "displayName": name,
        "shortDescription": "TODO",
        "longDescription": "TODO",
        "developerName": developer,
        "category": "TODO",
        "capabilities": "TODO",
        "defaultPrompt": "TODO",
        "websiteURL": website,
        "brandColor": "TODO",
    }


def scaffold_plugin(plugin_dir, sync: bool = True) -> bool:
    """Create a missing Codex manifest for ``plugin_dir`` from its Claude SSOT.

    Seeds the 8 SHARED_FIELDS plus a TODO-placeholder ``interface`` block (see
    ``_derive_interface``). Returns ``True`` iff a manifest was created.

    Never clobbers an existing Codex manifest: if one is already present this is
    a no-op (or a shared-field sync when ``sync=True``) and returns ``False`` —
    human-authored ``interface`` values are preserved.
    """
    plugin_dir = Path(plugin_dir)
    target_path = codex_manifest_path(plugin_dir)
    if target_path.exists():
        if sync:
            sync_plugin(plugin_dir)
        return False

    source = _load(claude_manifest_path(plugin_dir))
    manifest: dict = {}
    for field in SHARED_FIELDS:
        if field in source:
            manifest[field] = source[field]
    manifest["interface"] = _derive_interface(source)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    _dump(target_path, manifest)
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "plugin",
        type=Path,
        nargs="?",
        help="plugin directory (name or path); omit when using --all",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="pure read; exit non-zero on divergence (CI drift gate)",
    )
    parser.add_argument(
        "--scaffold",
        action="store_true",
        help="create a missing Codex manifest (TODO placeholders) then sync; never clobbers",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="iterate every CODEX_ELIGIBLE plugin under the repo root",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="repo root for --all (defaults to this script's parent repo)",
    )
    args = parser.parse_args(argv)

    if args.all:
        repo_root = (
            args.repo_root
            if args.repo_root is not None
            else Path(__file__).resolve().parent.parent
        )
        # In --check mode this stays read-only and accumulates a non-zero exit
        # if ANY plugin is out of sync; otherwise sync_plugin always returns
        # True (after writing) so the loop never trips the drift branch.
        exit_code = 0
        for name in CODEX_ELIGIBLE:
            plugin_dir = repo_root / name
            if args.scaffold:
                scaffold_plugin(plugin_dir)
            elif args.check and not codex_manifest_path(plugin_dir).exists():
                print(
                    f"MISSING: {codex_manifest_path(plugin_dir)} — run --scaffold",
                    file=sys.stderr,
                )
                exit_code = 1
            elif not sync_plugin(plugin_dir, check=args.check):
                print(
                    f"DRIFT: {codex_manifest_path(plugin_dir)} shared fields "
                    f"diverge from {claude_manifest_path(plugin_dir)}. "
                    f"Run: python3 {Path(__file__).name} {plugin_dir}",
                    file=sys.stderr,
                )
                exit_code = 1
        return exit_code

    if args.plugin is None:
        parser.error("a plugin directory is required unless --all is given")

    if args.scaffold:
        scaffold_plugin(args.plugin)
        return 0

    if args.check:
        if not codex_manifest_path(args.plugin).exists():
            print(
                f"MISSING: {codex_manifest_path(args.plugin)} — run --scaffold",
                file=sys.stderr,
            )
            return 1
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
