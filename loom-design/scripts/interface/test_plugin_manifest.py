"""Regression guard for the loom-interface-design plugin manifest.

plugin.json is pure config (a tdd-iron-law exemption), so these are
cheap presence/validity assertions, not iron-law-mandated logic tests.
Path is resolved relative to this file so the test runs from any cwd.
"""

import json
import re
from pathlib import Path

MANIFEST = Path(__file__).parent.parent / ".claude-plugin" / "plugin.json"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _load():
    assert MANIFEST.exists(), f"plugin.json missing at {MANIFEST}"
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_is_valid_json():
    # Why: a malformed manifest silently breaks plugin discovery.
    _load()


def test_name_is_interface_design_toolkit():
    # Why: name must match the plugin dir + marketplace source for resolution.
    assert _load()["name"] == "loom-interface-design"


def test_version_is_semver():
    # Why: marketplace + version pinning rely on a parseable semver.
    assert SEMVER.match(_load()["version"]), "version must be MAJOR.MINOR.PATCH"


def test_description_is_non_empty():
    # Why: an empty description gives the host nothing to surface to users.
    assert _load()["description"].strip()


def test_description_within_codex_limit():
    # Why: Codex CLI silently drops skills whose description exceeds 1024
    # chars; staying under the cap keeps the plugin loadable on that host.
    assert len(_load()["description"]) <= 1024


def test_license_is_mit():
    # Why: repo convention is MIT across plugins (see research-toolkit).
    assert _load()["license"] == "MIT"


def test_manifest_valid():
    # Why: single gate asserting required fields exist with correct types,
    # the description fits Codex's 1024-char cap, and keywords cover intent.
    manifest = _load()

    assert isinstance(manifest["name"], str)
    assert isinstance(manifest["version"], str)
    assert isinstance(manifest["description"], str)
    assert isinstance(manifest["homepage"], str)
    assert isinstance(manifest["repository"], str)
    assert isinstance(manifest["license"], str)

    author = manifest["author"]
    assert isinstance(author, dict)
    assert isinstance(author["name"], str)
    assert isinstance(author["url"], str)

    keywords = manifest["keywords"]
    assert isinstance(keywords, list)
    assert all(isinstance(k, str) for k in keywords)
    for required in ("interface-design", "ui-ux", "design-system", "portable"):
        assert required in keywords, f"keyword {required!r} missing"

    assert len(manifest["description"]) <= 1024
