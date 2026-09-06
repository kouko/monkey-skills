"""Adversarial probe for W2-02 of
2026-09-05-graduated-probes-independent-of-local-history: the 1.6.1
version bump must be stamped everywhere the plugin claims a version, not
just in `plugin.json`.

Checks: `loom-code/.claude-plugin/plugin.json` `version` is the current
release (`1.7.0` after the artifact-charter change landed on 1.6.1); the
Codex mirror `loom-code/.codex-plugin/plugin.json` agrees; `[1.6.1]`
appears as a `## [x.y.z]` entry in `loom-code/CHANGELOG.md`; and
`test_every_place_the_version_is_stamped_agrees` in
`loom-code/scripts/test_probes_positioning_branch_end.py` (which also
checks the root README table row and the two `.codex/hooks` stamps)
passes.

Fails today (1.6.0 everywhere).

Independently re-runnable: `python3 -m pytest
docs/loom/2026-09-05-graduated-probes-independent-of-local-history/evidence/probes/test_changelog_carries_1_6_1.py
-q` from the repo root.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
)

PLUGIN_JSON = REPO / "loom-code" / ".claude-plugin" / "plugin.json"
CODEX_PLUGIN_JSON = REPO / "loom-code" / ".codex-plugin" / "plugin.json"
CHANGELOG = REPO / "loom-code" / "CHANGELOG.md"

def test_plugin_json_is_1_6_1() -> None:
    version = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]
    codex_version = json.loads(CODEX_PLUGIN_JSON.read_text(encoding="utf-8"))["version"]
    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert version == codex_version
    assert re.search(rf"^##\s*\[{re.escape(version)}\]", changelog, re.MULTILINE), (
        f"loom-code/CHANGELOG.md has no entry for the live version {version}"
    )


def test_changelog_carries_1_6_1() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    assert re.search(r"^##\s*\[1\.6\.1\]", text, re.MULTILINE), (
        "loom-code/CHANGELOG.md has no `## [1.6.1]` entry"
    )


def test_every_place_the_version_is_stamped_agrees() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "loom-code/scripts/test_probes_positioning_branch_end.py",
            "-q",
            "-p",
            "no:cacheprovider",
            "-k",
            "test_every_place_the_version_is_stamped_agrees",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "test_every_place_the_version_is_stamped_agrees failed:\n"
        + result.stdout
        + result.stderr
    )
