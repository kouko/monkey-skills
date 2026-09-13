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
    """W3-01: `loom-memory` is no longer an independent plugin — its sibling
    is now `loom-workflow`, which ships the relocated `loom-memory` skill
    among its own files. The property under test is unchanged (every real
    loom-family plugin root is boundary-clean); only the third plugin's
    identity changed."""
    import check_plugin_boundaries as checker

    repo = Path(__file__).resolve().parents[1]

    assert checker.find_boundary_violations(repo / "loom-code") == []
    assert checker.find_boundary_violations(repo / "loom-design") == []
    assert checker.find_boundary_violations(repo / "loom-workflow") == []


def test_own_skill_folder_named_like_a_sibling_plugin_is_not_flagged(tmp_path):
    """W3-01 regression guard: `loom-workflow` ships a skill literally named
    `loom-memory` (the plugin `loom-memory` retired into it). The generic
    sibling-name regex would otherwise mistake that skill's own internal
    `skills/loom-memory/scripts/...` path for a reference to a sibling
    plugin's private tree. A match is internal, not a sibling reference,
    when it resolves to a real path inside the plugin's own root."""
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-workflow"
    _write(
        plugin / "skills" / "loom-memory" / "scripts" / "loom_memory.py",
        "# real file\n",
    )
    _write(
        plugin / "skills" / "loom-memory" / "SKILL.md",
        "Validation lives at `skills/loom-memory/scripts/loom_memory.py` "
        "and at `/skills/loom-memory/scripts/loom_memory.py` inside this "
        "skill's own directory.\n",
    )

    assert checker.find_boundary_violations(plugin) == []


def test_reports_sibling_internal_path_naming_loom_memory(tmp_path):
    """W4-01: the generic sibling-plugin regex must catch `loom-memory`
    specifically, not just the two plugins every other fixture in this file
    names — a plugin-name-shaped regex proven only against `loom-design`/
    `loom-code` could still miss a real third name."""
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-code"
    source = _write(
        plugin / "skills" / "ship" / "SKILL.md",
        "Read `loom-memory/scripts/loom_memory.py` before recording.\n"
        "[private](../../../loom-memory/skills/loom-memory/SKILL.md)\n",
    )

    assert checker.find_boundary_violations(plugin) == [
        f"{source}:1: sibling internal path: loom-memory/scripts/loom_memory.py",
        f"{source}:2: escaping relative link: ../../../loom-memory/skills/loom-memory/SKILL.md",
    ]


def test_reports_sibling_internal_path_when_loom_memory_is_the_plugin_under_test(tmp_path):
    """The reverse direction: loom-memory itself must not reference a
    sibling's private path either — its own name is excluded from the
    detector, its siblings' names are not."""
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-memory"
    _write(
        plugin / ".claude-plugin" / "plugin.json",
        json.dumps({"name": "loom-memory"}),
    )
    source = _write(
        plugin / "skills" / "loom-memory" / "SKILL.md",
        "Run `loom-code/scripts/loom_checker.py` to cross-check a citation.\n",
    )

    assert checker.find_boundary_violations(plugin) == [
        f"{source}:1: sibling internal path: loom-code/scripts/loom_checker.py",
    ]


def test_decoy_nested_tree_does_not_launder_a_real_sibling_reference(tmp_path):
    """A file planted inside the plugin at a sibling's path shape must not
    make a genuine sibling-private reference read as internal.

    The first version of the internal-path exemption asked only whether the
    target resolved to something that exists under the plugin root. That let
    a decoy defeat the gate: create `<root>/loom-code/scripts/loom_checker.py`
    and a prose reference to the real `loom-code` plugin's private script
    stops being reported. The exemption now requires the target to live under
    this plugin's own `skills/<name>/`, so the decoy is still a violation.
    """
    import check_plugin_boundaries as checker

    plugin = tmp_path / "loom-workflow"
    _write(plugin / ".claude-plugin" / "plugin.json", '{"name": "loom-workflow"}\n')
    _write(plugin / "skills" / "loom-memory" / "scripts" / "loom_memory.py", "# real\n")
    _write(plugin / "loom-code" / "scripts" / "loom_checker.py", "# decoy\n")
    _write(
        plugin / "skills" / "handoff" / "SKILL.md",
        "Run `skills/loom-memory/scripts/loom_memory.py` for the store.\n"
        "See `loom-code/scripts/loom_checker.py` for the rules.\n",
    )

    violations = checker.find_boundary_violations(plugin)

    assert any("loom_checker.py" in v for v in violations), violations
    assert not any("loom_memory.py" in v for v in violations), violations


def test_a_real_sibling_plugin_name_is_never_exempt(tmp_path):
    """Even a same-named skill cannot exempt a name that is a real sibling
    plugin: when `<repo>/loom-design/.claude-plugin/plugin.json` exists, a
    `loom-design/...` reference stays a violation whatever sits inside."""
    import check_plugin_boundaries as checker

    _write(tmp_path / "loom-design" / ".claude-plugin" / "plugin.json", '{"name": "loom-design"}\n')
    plugin = tmp_path / "loom-workflow"
    _write(plugin / ".claude-plugin" / "plugin.json", '{"name": "loom-workflow"}\n')
    _write(plugin / "skills" / "loom-design" / "scripts" / "x.py", "# same-named skill\n")
    _write(
        plugin / "skills" / "handoff" / "SKILL.md",
        "See `skills/loom-design/scripts/x.py` for details.\n",
    )

    assert any("x.py" in v for v in checker.find_boundary_violations(plugin))
