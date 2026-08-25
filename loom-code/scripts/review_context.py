"""Emit the immutable, plugin-local context for a review station.

Run as ``python3 review_context.py [--repo <path>]``.  The JSON packet is
read-only: it identifies the target repository and its current commit while
all review resources are derived from this installed script's location.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


PACKET_KEYS = ("target_repo", "reviewed_sha", "plugin_version", "resources")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


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


def validate_packet(packet_path: Path) -> list[str]:
    """Return one message per failing packet field; empty means well-formed."""
    try:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"packet: unreadable or not JSON ({error})"]
    if not isinstance(packet, dict):
        return ["packet: top level must be a JSON object"]

    errors = []
    for key in PACKET_KEYS:
        if not packet.get(key):
            errors.append(f"{key}: missing or empty")

    reviewed_sha = packet.get("reviewed_sha")
    target_repo = packet.get("target_repo")
    if isinstance(reviewed_sha, str) and reviewed_sha:
        if SHA_PATTERN.fullmatch(reviewed_sha) is None:
            errors.append("reviewed_sha: must match ^[0-9a-f]{40}$")
        elif isinstance(target_repo, str) and target_repo:
            exists = _git(
                Path(target_repo), "cat-file", "-e", f"{reviewed_sha}^{{commit}}"
            )
            if exists is None:
                errors.append("reviewed_sha: commit does not exist in target_repo")

    resources = packet.get("resources")
    if resources and not isinstance(resources, dict):
        errors.append("resources: must be an object of name -> absolute path")
    elif isinstance(resources, dict):
        for name, value in resources.items():
            if not isinstance(value, str) or not Path(value).is_absolute():
                errors.append(f"resources: {name} is not an absolute path")
            elif not Path(value).exists():
                errors.append(f"resources: {name} does not exist ({value})")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve immutable review context")
    parser.add_argument("--repo", default=".", help="target repository (default: cwd)")
    parser.add_argument(
        "--validate",
        metavar="PACKET_JSON",
        help="validate an existing packet file instead of emitting one",
    )
    args = parser.parse_args(argv)
    if args.validate is not None:
        try:
            errors = validate_packet(Path(args.validate))
        except OSError as error:
            print(f"PACKET-INVALID: packet: {error}", file=sys.stderr)
            return 1
        for error in errors:
            print(f"PACKET-INVALID: {error}", file=sys.stderr)
        return 1 if errors else 0
    try:
        context = resolve_context(Path(args.repo))
    except (OSError, ValueError) as error:
        print(f"review-context: refused — {error}", file=sys.stderr)
        return 1
    print(json.dumps(context, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
