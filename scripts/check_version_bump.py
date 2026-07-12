#!/usr/bin/env python3
"""Fail a PR whose skill content changed without a plugin version bump.

The marketplace publishes plugins BY VERSION. If a PR changes a plugin's skill
content but leaves `<plugin>/.claude-plugin/plugin.json` `version` alone, the
marketplace never republishes it: `plugin update` becomes a silent no-op and
users keep running the stale skill. This repo missed that obligation three times
(PR#539→#540, PR#545→#546, PR#552) — this gate makes the miss mechanical.

Skill content = `<plugin>/{skills,hooks,agents,references}/**`. A plugin's own
CHANGELOG, tests, or docs are NOT skill content and require no bump.

The check compares the `version` FIELD across the two revisions (not merely
whether plugin.json was touched — a description-only edit is not a bump).

The Codex mirror (`.codex-plugin/plugin.json`) stays enforced by the separate
`sync_codex_manifests.py --check --all` gate; this script does not duplicate it.

Plugin discovery is the `CODEX_ELIGIBLE` tuple, so a plugin missing from it would
be invisible to THIS gate — and, because `--check --all` iterates the same tuple,
invisible to the Codex drift gate too (both blind at once, not one backstopping
the other). What actually keeps the tuple honest is
`test_eligible_list_covers_every_repo_plugin` in scripts/test_sync_codex_manifests.py,
which asserts the tuple equals the on-disk plugin census. That test is this gate's
registration backstop; do not remove it.

Usage:
    python3 scripts/check_version_bump.py --base <sha> --head <sha> [--repo DIR]

Exit codes: 0 = clean, 1 = at least one plugin needs a bump.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from sync_codex_manifests import CODEX_ELIGIBLE

# Subdirectories whose contents ship to the marketplace as plugin content.
SKILL_CONTENT_DIRS = ("skills", "hooks", "agents", "references")

MANIFEST = ".claude-plugin/plugin.json"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def changed_paths(repo: Path, base: str, head: str) -> list[str]:
    # --no-renames: with rename detection ON (the default), a file MOVED OUT of a
    # plugin prints only its destination path, so the plugin's shipped content
    # changed but the gate sees no hit (fail-open). Off, both paths are printed.
    out = _git(repo, "diff", "--no-renames", "--name-only", base, head)
    return [line for line in out.splitlines() if line]


def plugins_with_skill_content(paths: list[str]) -> set[str]:
    """Plugins (per CODEX_ELIGIBLE) whose skill content the diff touches."""
    hits = set()
    for path in paths:
        parts = path.split("/")
        if len(parts) < 3:
            continue
        plugin, subdir = parts[0], parts[1]
        if plugin in CODEX_ELIGIBLE and subdir in SKILL_CONTENT_DIRS:
            hits.add(plugin)
    return hits


def version_at(repo: Path, rev: str, plugin: str) -> str | None:
    """The plugin's manifest `version` at ``rev``; None if the manifest is absent."""
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{plugin}/{MANIFEST}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None  # new plugin at head, or deleted plugin at head
    return json.loads(result.stdout).get("version")


def find_violations(repo: Path, base: str, head: str) -> list[str]:
    """Plugins with skill-content changes whose version did not change."""
    violations = []
    for plugin in sorted(plugins_with_skill_content(changed_paths(repo, base, head))):
        before = version_at(repo, base, plugin)
        after = version_at(repo, head, plugin)
        if before is None or after is None:
            continue  # plugin added or removed by this diff — nothing to bump
        if before == after:
            violations.append(plugin)
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="base revision (PR base SHA)")
    parser.add_argument("--head", required=True, help="head revision (PR head SHA)")
    parser.add_argument(
        "--repo", default=".", help="repository root (default: cwd)"
    )
    args = parser.parse_args()

    violations = find_violations(Path(args.repo), args.base, args.head)
    if not violations:
        print("check_version_bump: OK — every plugin with skill-content changes bumped its version.")
        return 0

    print("check_version_bump: FAIL — skill content changed without a version bump.\n")
    print("The marketplace publishes by version: without a bump, `plugin update`")
    print("is a silent no-op and users keep running the stale skill.\n")
    for plugin in violations:
        print(f"  {plugin}: skill content changed, version unchanged")
        print(f"    fix: bump {plugin}/{MANIFEST} version, "
              f"then run python3 scripts/sync_codex_manifests.py {plugin}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
