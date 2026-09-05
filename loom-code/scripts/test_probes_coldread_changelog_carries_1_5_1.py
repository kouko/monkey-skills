"""W2-03 probe: loom-code is bumped to 1.5.1 and the changelog carries it.

The patch bump is the plan's W2-03; the Codex mirror manifest must agree
with the Claude manifest (the SSOT), and the changelog must carry a
`[1.5.1]` heading so the marketplace update is not a silent no-op.
"""

from __future__ import annotations

import json
from pathlib import Path

EXPECTED = "1.5.1"


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "docs" / "loom").is_dir():
            return parent
    raise AssertionError("repo root with docs/loom not found above " + str(here))


def test_plugin_manifests_version_1_5_1_and_changelog_carries_it() -> None:
    """Both manifests read 1.5.1 and CHANGELOG.md has a [1.5.1] heading."""
    root = _repo_root()
    claude = json.loads((root / "loom-code/.claude-plugin/plugin.json").read_text())
    codex = json.loads((root / "loom-code/.codex-plugin/plugin.json").read_text())
    assert claude["version"] == EXPECTED
    assert codex["version"] == EXPECTED
    changelog = (root / "loom-code/CHANGELOG.md").read_text()
    assert f"## [{EXPECTED}]" in changelog
