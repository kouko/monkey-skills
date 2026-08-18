"""RED test for Task 1 — think-orbit plugin skeleton + marketplace + Codex mirror.

brief-item: BI-8
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "think-orbit"


def test_manifest_marketplace_and_codex_mirror_are_consistent():
    # brief-item: BI-8
    plugin_json_path = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
    assert plugin_json_path.exists(), f"missing {plugin_json_path}"
    plugin_json = json.loads(plugin_json_path.read_text(encoding="utf-8"))
    assert plugin_json["name"] == "think-orbit"
    assert plugin_json["version"] == "0.1.3"

    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    entries = [p for p in marketplace["plugins"] if p.get("name") == "think-orbit"]
    assert entries, "think-orbit entry missing from marketplace.json"
    assert entries[0]["description"] == plugin_json["description"]

    result = subprocess.run(
        [sys.executable, "scripts/sync_codex_manifests.py", "--check", "think-orbit"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"codex manifest not in sync: stdout={result.stdout!r} stderr={result.stderr!r}"
    )

    for rel in (
        "README.md",
        "README.ja.md",
        "README.zh-TW.md",
        "CHANGELOG.md",
        "skills/thinking-session/SKILL.md",
    ):
        assert (PLUGIN_ROOT / rel).exists(), f"missing {PLUGIN_ROOT / rel}"


def test_layout_is_router_plus_verb_skills():
    # brief-item: BI-8
    assert (PLUGIN_ROOT / "scripts" / "dag.py").exists()

    expected_names = {
        "using-think-orbit": "using-think-orbit",
        "thinking-session": "thinking-session",
        "break-assumption": "break-assumption",
    }
    for skill_dir, expected_name in expected_names.items():
        skill_md = PLUGIN_ROOT / "skills" / skill_dir / "SKILL.md"
        assert skill_md.exists(), f"missing {skill_md}"
        text = skill_md.read_text(encoding="utf-8")
        assert f"name: {expected_name}" in text, (
            f"{skill_md} frontmatter name does not match {expected_name!r}"
        )

    assert not (PLUGIN_ROOT / "skills" / "think-orbit").exists(), (
        "skills/think-orbit/ should no longer exist after the router split"
    )

    assert not (PLUGIN_ROOT / "skills" / "decision-session").exists(), (
        "skills/decision-session/ should no longer exist after the 0.1.1 rename"
    )

    schema_path = PLUGIN_ROOT / "skills" / "thinking-session" / "references" / "node-schema.md"
    assert schema_path.exists(), f"missing {schema_path}"


def test_plugin_description_frames_thinking_planning_and_deciding():
    """0.1.1 — the plugin's purpose is thinking and planning; deciding is one ending."""
    plugin_json = json.loads(
        (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    description = plugin_json["description"]

    for token in ("thinking", "planning", "decision"):
        assert token in description.lower(), (
            f"plugin description must frame {token!r}"
        )

    codex = json.loads(
        (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert codex["version"] == plugin_json["version"]
