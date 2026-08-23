"""Composition contract for independently installed loom plugins.

This deliberately complements the standalone-layout probe: it checks only the
public seam between the two packages, not either package's manifest inventory.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import check_plugin_boundaries


REPO_ROOT = Path(__file__).resolve().parents[1]


def _copy_plugin(source_name: str, destination: Path) -> Path:
    source = REPO_ROOT / source_name
    shutil.copytree(source, destination)
    return destination


def _loom_artifacts(markdown: str) -> set[str]:
    """Return the consumer-project artifact names declared in code spans."""

    return {
        span.rstrip("/")
        for span in re.findall(r"`([^`\n]*docs/loom[^`\n]*)`", markdown)
    }


def _resolve_qualified_skill(qualified_name: str, plugin_roots: tuple[Path, ...]) -> Path | None:
    plugin_name, separator, skill_name = qualified_name.partition(":")
    if not separator or not plugin_name or not skill_name:
        return None
    for plugin_root in plugin_roots:
        manifest_path = plugin_root / ".claude-plugin/plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("name") == plugin_name:
            skill_path = plugin_root / "skills" / skill_name / "SKILL.md"
            return skill_path if skill_path.is_file() else None
    return None


def test_plugins_compose_only_through_public_skills_and_artifacts(tmp_path: Path) -> None:
    design_root = _copy_plugin(
        "loom-design", tmp_path / "design-host" / "extensions" / "design-bundle"
    )
    code_root = _copy_plugin(
        "loom-code", tmp_path / "code-host" / "plugins" / "code-bundle"
    )

    # The installs intentionally have neither a shared parent package directory
    # nor their repository names.  A valid composition therefore cannot depend
    # on resolving ../loom-code (or an absolute sibling-plugin internal path).
    assert design_root.parent.parent != code_root.parent.parent
    design_router_path = design_root / "skills/using-loom-design/SKILL.md"
    design_pipeline_path = design_root / "skills/using-loom-pipeline/SKILL.md"
    design_spec_path = design_root / "skills/spec-expansion/SKILL.md"
    code_planner_path = code_root / "skills/writing-plans/SKILL.md"
    design_router = design_router_path.read_text()
    design_pipeline = design_pipeline_path.read_text()
    handoff = "loom-code:using-loom-code"
    assert f"`{handoff}`" in design_router
    assert f"`{handoff}`" in design_pipeline

    code_manifest = json.loads(
        (code_root / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    assert code_manifest["name"] == "loom-code"
    installed_roots = (design_root, code_root)
    resolved_handoff = _resolve_qualified_skill(handoff, installed_roots)
    assert resolved_handoff == code_root / "skills/using-loom-code/SKILL.md"

    # Mutation probe: the public name must stop resolving when its exported
    # skill disappears; mere presence of the handoff string is insufficient.
    hidden_skill = resolved_handoff.with_suffix(".md.hidden")
    resolved_handoff.rename(hidden_skill)
    try:
        assert _resolve_qualified_skill(handoff, installed_roots) is None
    finally:
        hidden_skill.rename(resolved_handoff)

    design_spec = design_spec_path.read_text()
    code_planner = code_planner_path.read_text()
    shared_artifacts = _loom_artifacts(design_spec) & _loom_artifacts(code_planner)

    # The producer and consumer meet in the target project's named change
    # folder.  Plugin source paths are intentionally absent from this seam.
    assert shared_artifacts == {"docs/loom/<change-id>"}
    assert "emitted by `loom-design:spec-expansion`" in code_planner
    assert not any(
        re.search(r"loom-(?:code|design)/(?:hooks|skills|scripts)/", artifact)
        for artifact in shared_artifacts
    )

    violations = {
        plugin_root: check_plugin_boundaries.find_boundary_violations(plugin_root)
        for plugin_root in (design_root, code_root)
    }
    assert not any(violations.values()), violations
