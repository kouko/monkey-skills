"""W2-01 — version bumps and changelog lines for the loom-script-performance wave.

Three checks, each recomputed from the committed files (no claims trusted):

1. Each plugin's CHANGELOG.md top entry version equals its
   ``.claude-plugin/plugin.json`` version, and the entry names a before and
   an after number (Keep a Changelog style, matching the existing
   ``[4.1.0]`` memory-grep entry's tone).
2. The Codex mirror's version-stamp header line
   (``# loom-checker <version>``, ``.codex/hooks/loom_checker.py``) carries
   the loom-code plugin.json version — the mirror drifts silently on a bump
   if this is not regenerated (docs/loom/2026-09-07-loom-script-performance
   plan W2-01 risk).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

STAMP_PREFIX = "# loom-checker "
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:ms|s|x|×|calls?|spawns?)\b", re.IGNORECASE)


def _plugin_version(plugin: str) -> str:
    manifest = REPO / plugin / ".claude-plugin" / "plugin.json"
    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


def _changelog_top_entry(plugin: str) -> tuple[str, str]:
    """Return (version, entry_text) for the first ``## [x.y.z]`` block."""
    changelog = (REPO / plugin / "CHANGELOG.md").read_text(encoding="utf-8")
    entries = list(re.finditer(r"^## \[(\d+\.\d+\.\d+)\][^\n]*\n", changelog, re.MULTILINE))
    assert entries, f"{plugin}/CHANGELOG.md has no `## [x.y.z]` entry"
    top = entries[0]
    version = top.group(1)
    start = top.end()
    end = entries[1].start() if len(entries) > 1 else len(changelog)
    return version, changelog[start:end]


def _has_at_least_two_numbers(text: str) -> bool:
    return len(NUMBER_RE.findall(text)) >= 2


def test_loom_code_changelog_top_entry_matches_plugin_version():
    version = _plugin_version("loom-code")
    entry_version, entry_text = _changelog_top_entry("loom-code")
    assert entry_version == version, (
        f"loom-code CHANGELOG top entry is {entry_version!r} but "
        f"plugin.json version is {version!r}"
    )
    assert _has_at_least_two_numbers(entry_text), (
        "loom-code CHANGELOG top entry must name a before AND an after "
        "measurement number"
    )


def test_loom_workflow_changelog_top_entry_matches_plugin_version():
    version = _plugin_version("loom-workflow")
    entry_version, entry_text = _changelog_top_entry("loom-workflow")
    assert entry_version == version, (
        f"loom-workflow CHANGELOG top entry is {entry_version!r} but "
        f"plugin.json version is {version!r}"
    )
    assert _has_at_least_two_numbers(entry_text), (
        "loom-workflow CHANGELOG top entry must name a before AND an after "
        "measurement number"
    )


def test_codex_mirror_stamp_carries_loom_code_version():
    version = _plugin_version("loom-code")
    mirror = REPO / ".codex" / "hooks" / "loom_checker.py"
    lines = mirror.read_text(encoding="utf-8").splitlines()
    stamped = [line for line in lines if line.startswith(STAMP_PREFIX)]
    assert stamped, f"no {STAMP_PREFIX!r} line found in {mirror}"
    assert stamped[0] == f"{STAMP_PREFIX}{version}", (
        f"mirror stamp is {stamped[0]!r}, expected {STAMP_PREFIX}{version!r} "
        "— regenerate with `python3 loom-code/scripts/codex_scaffold.py --repo .`"
    )
