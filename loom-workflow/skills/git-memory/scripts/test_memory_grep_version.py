"""W2-01: version bump, changelog entry, and minimum git version documented.

Regression contract for the housekeeping task that follows the memory-grep.sh
single-pass rewrite (W1-02/W1-03): the plugin version bumped, the rewrite's
CHANGELOG entry names the measured before/after durations, and the script's
header comment states the minimum git version this rewrite now requires.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_LOOM_WORKFLOW_ROOT = Path(__file__).parents[3]
_PLUGIN_JSON = _LOOM_WORKFLOW_ROOT / ".claude-plugin" / "plugin.json"
_CHANGELOG = _LOOM_WORKFLOW_ROOT / "CHANGELOG.md"
_MEMORY_GREP = Path(__file__).parent / "memory-grep.sh"

_CHANGELOG_HEADING_RE = re.compile(r"^## \[(?P<version>[^\]]+)\]", re.MULTILINE)
_DURATION_RE = re.compile(r"\b\d+(?:\.\d+)?\s*s\b")


def _plugin_version() -> str:
    manifest = json.loads(_PLUGIN_JSON.read_text(encoding="utf-8"))
    return manifest["version"]


def _changelog_top_entry() -> tuple[str, str]:
    """Return (version, body-text-until-next-heading) of the top entry."""
    text = _CHANGELOG.read_text(encoding="utf-8")
    matches = list(_CHANGELOG_HEADING_RE.finditer(text))
    assert matches, "CHANGELOG.md has no version headings"
    first = matches[0]
    end = matches[1].start() if len(matches) > 1 else len(text)
    return first.group("version"), text[first.start() : end]


def _changelog_entry(version: str) -> str:
    """Return one version's body text from the changelog."""
    text = _CHANGELOG.read_text(encoding="utf-8")
    matches = list(_CHANGELOG_HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        if match.group("version") != version:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[match.start() : end]
    raise AssertionError(f"CHANGELOG.md has no {version!r} entry")


def test_changelog_top_entry_version_matches_plugin_json() -> None:
    version, _ = _changelog_top_entry()
    assert version == _plugin_version(), (
        f"CHANGELOG top entry version {version!r} != plugin.json {_plugin_version()!r}"
    )


def test_single_pass_changelog_entry_names_measurement_command_and_both_durations() -> None:
    entry = _changelog_entry("4.1.0")
    durations = _DURATION_RE.findall(entry)
    assert len(durations) >= 2, (
        f"expected at least two measured durations (before/after) in the top "
        f"CHANGELOG entry, found {durations!r}"
    )
    assert "memory-grep.sh" in entry, (
        "top CHANGELOG entry does not name the measurement command"
    )
    assert "time" in entry, (
        "top CHANGELOG entry does not name the measurement command (`time ...`)"
    )


def test_memory_grep_header_states_minimum_git_version() -> None:
    header = "\n".join(_MEMORY_GREP.read_text(encoding="utf-8").splitlines()[:80])
    assert re.search(r"[Mm]inimum git version", header), (
        "memory-grep.sh header does not state a minimum git version"
    )
    assert re.search(r"\bgit\s+\d+\.\d+(\.\d+)?\b", header), (
        "memory-grep.sh header does not name a specific git version number"
    )
