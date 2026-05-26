"""
Tests for dev-workflow plugin.json manifest.

Assertions:
  (a) plugin.json parses as valid JSON
  (b) version is strictly greater than PRE_BUMP snapshot (2.7.1)
  (c) bump is a minor bump: same major, higher minor, patch == 0
  (d) keywords array contains "recap"
"""
import json
import pathlib

from packaging.version import Version

# Historical snapshot — the version in the worktree before T4 landed.
PRE_BUMP = "2.7.1"

PLUGIN_JSON = pathlib.Path(__file__).parent / "plugin.json"


def _load_manifest() -> dict:
    with PLUGIN_JSON.open() as fh:
        return json.load(fh)


def test_version_and_keywords():
    # (a) valid JSON
    manifest = _load_manifest()

    current_str = manifest["version"]
    current = Version(current_str)
    pre = Version(PRE_BUMP)

    # (b) strictly greater than pre-bump snapshot
    assert current > pre, (
        f"version {current_str!r} must be > PRE_BUMP {PRE_BUMP!r}"
    )

    # (c) minor bump: same major, higher minor, patch == 0
    assert current.major == pre.major, (
        f"major must not change: got {current.major}, want {pre.major}"
    )
    assert current.minor > pre.minor, (
        f"minor must increase: got {current.minor}, want > {pre.minor}"
    )
    assert current.micro == 0, (
        f"patch must reset to 0 on a minor bump: got {current.micro}"
    )

    # (d) "recap" in keywords
    keywords = manifest.get("keywords", [])
    assert "recap" in keywords, (
        f'"recap" missing from keywords: {keywords!r}'
    )
