"""Structural test: both plugin manifests exist, parse, and stay in sync.

# @req: REQ-LOOM-PIPELINE-MANIFEST-1
"""
import json
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parents[1]
CLAUDE_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"


def test_manifests_exist_and_sync():
    # @req: REQ-LOOM-PIPELINE-MANIFEST-1
    assert CLAUDE_MANIFEST.exists(), f"missing {CLAUDE_MANIFEST}"
    assert CODEX_MANIFEST.exists(), f"missing {CODEX_MANIFEST}"

    claude_data = json.loads(CLAUDE_MANIFEST.read_text())
    codex_data = json.loads(CODEX_MANIFEST.read_text())

    assert claude_data["name"] == "loom-pipeline"
    assert codex_data["name"] == "loom-pipeline"

    assert claude_data["version"] == codex_data["version"]

    assert "loom-pipeline" in claude_data["keywords"]
    assert "loom-pipeline" in codex_data["keywords"]
