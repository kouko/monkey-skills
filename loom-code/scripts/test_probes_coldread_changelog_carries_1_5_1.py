"""W2-03 probe: loom-code is bumped to 1.5.1 and the changelog carries it.

The patch bump is the plan's W2-03; the Codex mirror manifest must agree
with the Claude manifest (the SSOT), and the changelog must carry a
`[1.5.1]` heading so the marketplace update is not a silent no-op.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

EXPECTED = "1.5.1"


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "docs" / "loom").is_dir():
            return parent
    raise AssertionError("repo root with docs/loom not found above " + str(here))


def _live_claude_version(root: Path) -> str:
    return json.loads((root / "loom-code/.claude-plugin/plugin.json").read_text())["version"]


def test_plugin_manifests_version_1_5_1_and_changelog_carries_it() -> None:
    """Both manifests read 1.5.1 and CHANGELOG.md has a [1.5.1] heading.

    Precondition (the plugin is still AT 1.5.1) graduates away on the next
    version bump — same handling as the two probes #794 left behind: skip
    when the precondition is absent rather than weaken the assertion. The
    changelog-heading check stays unconditional: `[1.5.1]` is a historical
    section header and must never disappear regardless of the live version.
    """
    root = _repo_root()
    changelog = (root / "loom-code/CHANGELOG.md").read_text()
    assert f"## [{EXPECTED}]" in changelog
    live = _live_claude_version(root)
    if live != EXPECTED:
        pytest.skip(f"plugin has moved past {EXPECTED} (now {live}); heading checked above")
    codex = json.loads((root / "loom-code/.codex-plugin/plugin.json").read_text())
    assert live == EXPECTED
    assert codex["version"] == EXPECTED
