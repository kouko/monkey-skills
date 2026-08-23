"""Structural test: both plugin manifests exist, parse, and stay in sync.

"""
import json
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parents[2]
CLAUDE_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
REPO_ROOT = PLUGIN_ROOT.parent
MANDATORY_DEPENDENCY_KEYS = {
    "dependencies",
    "pluginDependencies",
    "requiredPlugins",
    "requires",
}


def test_manifests_exist_and_sync():
    assert CLAUDE_MANIFEST.exists(), f"missing {CLAUDE_MANIFEST}"
    assert CODEX_MANIFEST.exists(), f"missing {CODEX_MANIFEST}"

    claude_data = json.loads(CLAUDE_MANIFEST.read_text())
    codex_data = json.loads(CODEX_MANIFEST.read_text())

    assert claude_data["name"] == "loom-design"
    assert codex_data["name"] == "loom-design"

    assert claude_data["version"] == codex_data["version"]

    assert "loom-design" in claude_data["keywords"]
    assert "loom-design" in codex_data["keywords"]


def test_loom_plugins_do_not_mandate_each_other():
    """Each package remains useful when its loom sibling is absent."""

    for plugin_name, sibling_name in (
        ("loom-design", "loom-code"),
        ("loom-code", "loom-design"),
    ):
        for host_manifest in (".claude-plugin", ".codex-plugin"):
            manifest_path = REPO_ROOT / plugin_name / host_manifest / "plugin.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            mandatory = {
                key: manifest[key]
                for key in MANDATORY_DEPENDENCY_KEYS
                if key in manifest
            }
            assert sibling_name not in json.dumps(mandatory, sort_keys=True)

    design_readme = (REPO_ROOT / "loom-design" / "README.md").read_text()
    code_readme = (REPO_ROOT / "loom-code" / "README.md").read_text()
    required_contract = (
        "independently installable",
        "plugin-qualified skill names",
        "docs/loom/",
    )
    for phrase in required_contract:
        assert phrase in design_readme
        assert phrase in code_readme
    assert "`loom-design: N/A` with the reason" in design_readme
    assert "N/A with the reason" in code_readme
