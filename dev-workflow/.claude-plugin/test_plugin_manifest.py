"""
Tests for dev-workflow plugin.json manifest.

Assertions:
  (a) plugin.json parses as valid JSON
  (b) version is strictly greater than PRE_BUMP snapshot (2.7.1)
  (c) bump is a minor bump: same major, higher minor, patch == 0
  (d) keywords array contains "recap"
  (e) keywords array contains "handoff"
"""
import json
import pathlib

# Historical snapshot — the version in the worktree before T4 landed.
PRE_BUMP = "2.7.1"

PLUGIN_JSON = pathlib.Path(__file__).parent / "plugin.json"


def _parse_semver(v: str) -> tuple[int, int, int]:
    """Parse a 'MAJOR.MINOR.PATCH' string into an integer tuple (stdlib-only)."""
    major, minor, patch = v.split(".")
    return (int(major), int(minor), int(patch))


def _load_manifest() -> dict:
    with PLUGIN_JSON.open() as fh:
        return json.load(fh)


def test_version_and_keywords():
    # (a) valid JSON
    manifest = _load_manifest()

    current_str = manifest["version"]
    current = _parse_semver(current_str)
    pre = _parse_semver(PRE_BUMP)

    # (b) strictly greater than pre-bump snapshot
    assert current > pre, (
        f"version {current_str!r} must be > PRE_BUMP {PRE_BUMP!r}"
    )

    # (c) minor bump: same major, higher minor, patch == 0
    assert current[0] == pre[0], (
        f"major must not change: got {current[0]}, want {pre[0]}"
    )
    assert current[1] > pre[1], (
        f"minor must increase: got {current[1]}, want > {pre[1]}"
    )
    assert current[2] == 0, (
        f"patch must reset to 0 on a minor bump: got {current[2]}"
    )

    # (d) "recap" in keywords
    keywords = manifest.get("keywords", [])
    assert "recap" in keywords, (
        f'"recap" missing from keywords: {keywords!r}'
    )

    # (e) "handoff" in keywords
    assert "handoff" in keywords, (
        f'"handoff" missing from keywords: {keywords!r}'
    )
