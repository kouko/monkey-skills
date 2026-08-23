"""Tests for the independently-installable plugin boundary checker."""

import json
from pathlib import Path


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_reports_relative_links_and_internal_paths_that_escape_plugin_root(tmp_path):
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-design"
    sibling = tmp_path / "loom-code"
    _write(plugin / "skills" / "router" / "local.md", "local")
    _write(sibling / "hooks" / "family-relay.md", "sibling")
    _write(sibling / "skills" / "using-loom-code" / "SKILL.md", "sibling")
    source = _write(
        plugin / "skills" / "router" / "SKILL.md",
        """
[local](local.md)
[escape](../../../outside.md)
[sibling link](../../../loom-code/skills/using-loom-code/SKILL.md)
Read `loom-code/hooks/family-relay.md` before dispatch.
Run `../loom-code/scripts/private_check.py` to validate it.
[internal path](loom-code/skills/private.md)
""",
    )

    violations = checker.find_boundary_violations(plugin)

    assert violations == [
        f"{source}:3: escaping relative link: ../../../outside.md",
        f"{source}:4: escaping relative link: ../../../loom-code/skills/using-loom-code/SKILL.md",
        f"{source}:5: sibling internal path: loom-code/hooks/family-relay.md",
        f"{source}:6: sibling internal path: ../loom-code/scripts/private_check.py",
        f"{source}:7: sibling internal path: loom-code/skills/private.md",
    ]


def test_accepts_local_links_external_targets_anchors_and_qualified_skills(tmp_path):
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-design"
    _write(plugin / "skills" / "router" / "references" / "guide.md", "guide")
    _write(
        plugin / "skills" / "router" / "SKILL.md",
        """
[local](references/guide.md)
[local anchor](references/guide.md#details)
[web](https://example.com/loom-code/skills/internal.md)
[mail](mailto:maintainer@example.com)
[anchor](#intake)
Invoke `loom-code:using-loom-code` for implementation.
""",
    )

    assert checker.find_boundary_violations(plugin) == []


def test_reports_sibling_internal_reference_when_sibling_is_not_installed(tmp_path):
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-design"
    source = _write(
        plugin / "skills" / "router" / "SKILL.md",
        "Read `loom-code/hooks/family-reception.md` first.\n",
    )

    assert checker.find_boundary_violations(plugin) == [
        f"{source}:1: sibling internal path: loom-code/hooks/family-reception.md"
    ]


def test_reports_reference_style_links_that_escape_plugin_root(tmp_path):
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-design"
    _write(plugin / "local.md", "local")
    source = _write(
        plugin / "SKILL.md",
        """
[escape]: ../outside.md
[angled]: <../../elsewhere.md#section> "title"
[local]: local.md
[web]: https://example.com/guide.md
""",
    )

    assert checker.find_boundary_violations(plugin) == [
        f"{source}:2: escaping relative link: ../outside.md",
        f"{source}:3: escaping relative link: ../../elsewhere.md",
    ]


def test_reports_sibling_internal_paths_with_arbitrary_filesystem_prefixes(tmp_path):
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-design"
    source = _write(
        plugin / "SKILL.md",
        """
Read `./../loom-code/hooks/family-relay.md`.
Read `../../plugins/loom-code/skills/using-loom-code/SKILL.md`.
Run `/cache/loom-code/scripts/check.py`.
""",
    )

    assert checker.find_boundary_violations(plugin) == [
        f"{source}:2: sibling internal path: ./../loom-code/hooks/family-relay.md",
        f"{source}:3: sibling internal path: ../../plugins/loom-code/skills/using-loom-code/SKILL.md",
        f"{source}:4: sibling internal path: /cache/loom-code/scripts/check.py",
    ]


def test_manifest_name_identifies_plugin_inside_versioned_install_root(tmp_path):
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-design" / "0.4.0"
    manifest = plugin / ".claude-plugin" / "plugin.json"
    _write(manifest, json.dumps({"name": "loom-design"}))
    _write(
        plugin / "SKILL.md",
        "Read `loom-design/skills/using-loom-design/SKILL.md`.\n",
    )

    assert checker.find_boundary_violations(plugin) == []


def test_plugin_root_basename_is_identity_fallback_without_manifest(tmp_path):
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-design"
    _write(
        plugin / "SKILL.md",
        "Read `loom-design/skills/using-loom-design/SKILL.md`.\n",
    )

    assert checker.find_boundary_violations(plugin) == []


def test_archival_markdown_is_outside_the_install_runtime_scan(tmp_path):
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-code"
    _write(plugin / "CHANGELOG.md", "`loom-design/hooks/private.md`\n")
    _write(plugin / "CHANGELOG-history.md", "`loom-design/scripts/private.py`\n")
    _write(plugin / "research" / "probe.md", "[old](../../outside.md)\n")
    _write(plugin / "TECH-SPEC.md", "[backlog](../docs/loom/backlog/)\n")
    shipped = _write(
        plugin / "skills" / "router" / "SKILL.md",
        "`loom-design/hooks/private.md`\n",
    )
    nested_research = _write(
        plugin / "skills" / "router" / "research" / "runtime.md",
        "`loom-design/hooks/nested-research.md`\n",
    )
    nested_changelog = _write(
        plugin / "skills" / "router" / "CHANGELOG.md",
        "`loom-design/scripts/nested-changelog.py`\n",
    )
    nested_tech_spec = _write(
        plugin / "skills" / "router" / "TECH-SPEC.md",
        "`loom-design/skills/nested-tech-spec.md`\n",
    )

    assert checker.find_boundary_violations(plugin) == [
        f"{nested_changelog}:1: sibling internal path: loom-design/scripts/nested-changelog.py",
        f"{shipped}:1: sibling internal path: loom-design/hooks/private.md",
        f"{nested_tech_spec}:1: sibling internal path: loom-design/skills/nested-tech-spec.md",
        f"{nested_research}:1: sibling internal path: loom-design/hooks/nested-research.md",
    ]


def test_real_loom_plugins_pass_the_install_boundary_gate():
    import check_plugin_boundaries as checker

    repo = Path(__file__).resolve().parents[1]

    assert checker.find_boundary_violations(repo / "loom-code") == []
    assert checker.find_boundary_violations(repo / "loom-design") == []
