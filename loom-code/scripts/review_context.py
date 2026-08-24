"""Emit the immutable, plugin-local context for a review station.

Run as ``python3 review_context.py [--repo <path>]``.  The JSON packet is
read-only: it identifies the target repository and its current commit while
all review resources are derived from this installed script's location.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _git(repo: Path, *args: str) -> str | None:
    """Return stripped git stdout, or None when the command cannot succeed."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _plugin_root() -> Path:
    """Resolve the installed plugin root from this script, never the target."""
    return Path(__file__).resolve().parents[1]


RESOURCE_RELATIVE_PATHS = {
        "review_scope": "scripts/review_scope.py",
        "gate_markers": "scripts/loom_gate_markers.py",
        "live_gate_station_receipt": "scripts/live_gate_station_receipt.py",
        "live_gate_adapter_probe": "scripts/live_gate_adapter_probe.py",
        "doc_citation_checker": "scripts/check_doc_citations.py",
        "reviewer_discipline": "scripts/_reviewer-discipline.md",
        "code_reviewer": "agents/code-reviewer.md",
        "docs_reviewer": "agents/docs-reviewer.md",
        "code_review_skill": "skills/requesting-code-review/SKILL.md",
        "docs_review_skill": "skills/requesting-docs-review/SKILL.md",
        "quality_rubric": "skills/subagent-driven-development/rubrics/quality-gate.md",
        "architecture_rubric": "skills/subagent-driven-development/rubrics/arch-gate.md",
        "security_checklist": "skills/subagent-driven-development/checklists/security-checklist.md",
        "spec_consistency_checklist": "skills/subagent-driven-development/checklists/spec-consistency.md",
        "app_security_standard": "skills/subagent-driven-development/standards/app-security-standard.md",
        "character_encoding_security_standard": "skills/subagent-driven-development/standards/character-encoding-security.md",
        "deliberate_simplification_standard": "skills/subagent-driven-development/standards/deliberate-simplification.md",
        "external_surface_grounding_standard": "skills/subagent-driven-development/standards/external-surface-grounding.md",
        "naming_and_functions_standard": "skills/subagent-driven-development/standards/naming-and-functions.md",
        "pragmatic_principles_standard": "skills/subagent-driven-development/standards/pragmatic-principles.md",
        "refactoring_standard": "skills/subagent-driven-development/standards/refactoring-standard.md",
        "solid_principles_standard": "skills/subagent-driven-development/standards/solid-principles.md",
        "tdd_standard": "skills/subagent-driven-development/standards/tdd-standard.md",
}


def _resources(plugin_root: Path) -> dict[str, str]:
    """Return existing plugin-local files a review station may read."""
    root = plugin_root.resolve()
    resources = {}
    for name, relative_path in RESOURCE_RELATIVE_PATHS.items():
        path = (root / relative_path).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"approved resource escapes plugin root: {name}")
        if not path.is_file():
            raise ValueError(f"approved resource is missing: {name} ({path})")
        resources[name] = str(path)
    return resources


def resolve_context(repo: Path) -> dict[str, object]:
    """Build a review packet for ``repo`` using this installation's files."""
    target_repo = repo.resolve()
    reviewed_sha = _git(target_repo, "rev-parse", "HEAD")
    if reviewed_sha is None:
        raise ValueError(f"could not resolve HEAD for target repository: {target_repo}")

    plugin_root = _plugin_root()
    try:
        manifest = json.loads(
            (plugin_root / ".claude-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        plugin_version = manifest["version"]
    except (OSError, json.JSONDecodeError, KeyError) as error:
        raise ValueError(f"could not read plugin version under {plugin_root}") from error

    return {
        "target_repo": str(target_repo),
        "reviewed_sha": reviewed_sha,
        "plugin_version": plugin_version,
        "resources": _resources(plugin_root),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve immutable review context")
    parser.add_argument("--repo", default=".", help="target repository (default: cwd)")
    args = parser.parse_args(argv)
    try:
        context = resolve_context(Path(args.repo))
    except (OSError, ValueError) as error:
        print(f"review-context: refused — {error}", file=sys.stderr)
        return 1
    print(json.dumps(context, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
